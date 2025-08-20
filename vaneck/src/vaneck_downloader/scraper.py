"""Web scraper for VanEck ETF data."""

import asyncio
import logging
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from pydantic import BaseModel

from .config import Config

logger = logging.getLogger(__name__)


class ETFData(BaseModel):
    """ETF data model."""
    
    ticker: str
    name: str
    fund_url: str
    fact_sheet_url: Optional[str] = None
    holdings_url: Optional[str] = None
    prospectus_url: Optional[str] = None
    annual_report_url: Optional[str] = None
    data_files: List[Dict[str, str]] = []


class VanEckScraper:
    """Scraper for VanEck ETF data."""
    
    def __init__(self, config: Config):
        """Initialise scraper with configuration."""
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.driver: Optional[webdriver.Chrome] = None
        
    async def __aenter__(self) -> "VanEckScraper":
        """Async context manager entry."""
        await self._init_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self._cleanup()
        
    async def _init_session(self) -> None:
        """Initialise HTTP session."""
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        )
        
    async def _cleanup(self) -> None:
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
            
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None
                
    def _init_selenium_driver(self) -> webdriver.Chrome:
        """Initialise Selenium Chrome driver."""
        if self.driver:
            return self.driver
            
        chrome_options = Options()
        if self.config.browser_headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-agent={self.config.user_agent}")
        
        try:
            if self.config.selenium_grid_url:
                self.driver = webdriver.Remote(
                    command_executor=self.config.selenium_grid_url,
                    options=chrome_options
                )
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
                
            self.driver.implicitly_wait(10)
            return self.driver
        except Exception as e:
            logger.error(f"Failed to initialise Chrome driver: {e}")
            raise
            
    async def get_etf_list(self) -> List[ETFData]:
        """Get list of ETFs from VanEck website."""
        logger.info("Starting ETF list scraping...")
        
        try:
            # Try async HTTP first
            etfs = await self._scrape_etf_list_async()
            if etfs:
                logger.info(f"Successfully scraped {len(etfs)} ETFs using HTTP")
                return etfs
        except Exception as e:
            logger.warning(f"HTTP scraping failed: {e}")
            
        try:
            # Fallback to Selenium for JavaScript-rendered content
            logger.info("Falling back to Selenium for JavaScript rendering...")
            etfs = await self._scrape_etf_list_selenium()
            logger.info(f"Successfully scraped {len(etfs)} ETFs using Selenium")
            return etfs
        except Exception as e:
            logger.error(f"Selenium scraping failed: {e}")
            raise
            
    async def _scrape_etf_list_async(self) -> List[ETFData]:
        """Scrape ETF list using async HTTP."""
        if not self.session:
            raise RuntimeError("Session not initialised")
            
        async with self.session.get(self.config.etf_finder_url) as response:
            response.raise_for_status()
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        etfs = []
        
        # Look for ETF listings in various possible container patterns
        etf_containers = (
            soup.find_all('div', class_=re.compile(r'fund|etf|listing', re.I)) +
            soup.find_all('tr', class_=re.compile(r'fund|etf|row', re.I)) +
            soup.find_all('a', href=re.compile(r'/etf/'))
        )
        
        for container in etf_containers:
            etf_data = await self._extract_etf_data_from_element(container)
            if etf_data:
                etfs.append(etf_data)
                
        # Remove duplicates based on ticker
        seen_tickers = set()
        unique_etfs = []
        for etf in etfs:
            if etf.ticker not in seen_tickers:
                seen_tickers.add(etf.ticker)
                unique_etfs.append(etf)
                
        return unique_etfs
        
    async def _scrape_etf_list_selenium(self) -> List[ETFData]:
        """Scrape ETF list using Selenium."""
        driver = self._init_selenium_driver()
        
        try:
            driver.get(self.config.etf_finder_url)
            
            # Wait for content to load
            wait = WebDriverWait(driver, self.config.browser_timeout)
            
            # Try different possible selectors for ETF listings
            selectors_to_try = [
                '[data-testid*="etf"]',
                '.fund-row',
                '.etf-listing',
                'a[href*="/etf/"]',
                'tr[data-fund-ticker]',
                '.fund-table tbody tr'
            ]
            
            elements = []
            for selector in selectors_to_try:
                try:
                    elements = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    if elements:
                        logger.info(f"Found elements using selector: {selector}")
                        break
                except TimeoutException:
                    continue
                    
            if not elements:
                # If no specific ETF elements found, try to find all links to ETF pages
                elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/etf/"]')
                
            etfs = []
            for element in elements:
                try:
                    # Extract basic info from element
                    ticker_match = re.search(r'/etf/([A-Z]+)/', element.get_attribute('href') or '')
                    if ticker_match:
                        ticker = ticker_match.group(1)
                        name = element.text.strip() or ticker
                        fund_url = urljoin(self.config.base_url, element.get_attribute('href'))
                        
                        etf_data = ETFData(
                            ticker=ticker,
                            name=name,
                            fund_url=fund_url
                        )
                        etfs.append(etf_data)
                        
                except Exception as e:
                    logger.warning(f"Error extracting ETF data from element: {e}")
                    continue
                    
            return etfs
            
        finally:
            # Don't close driver here as it might be reused
            pass
            
    async def _extract_etf_data_from_element(self, element) -> Optional[ETFData]:
        """Extract ETF data from HTML element."""
        try:
            # Try to find ticker and fund URL
            ticker = None
            fund_url = None
            name = None
            
            # Look for links to ETF pages
            links = element.find_all('a', href=re.compile(r'/etf/'))
            if not links and element.name == 'a' and element.get('href'):
                links = [element]
                
            for link in links:
                href = link.get('href')
                if href:
                    ticker_match = re.search(r'/etf/([A-Z]+)/', href)
                    if ticker_match:
                        ticker = ticker_match.group(1)
                        fund_url = urljoin(self.config.base_url, href)
                        name = link.get_text(strip=True) or ticker
                        break
                        
            if ticker and fund_url:
                return ETFData(
                    ticker=ticker,
                    name=name,
                    fund_url=fund_url
                )
                
        except Exception as e:
            logger.warning(f"Error extracting ETF data: {e}")
            
        return None
        
    async def get_etf_documents(self, etf: ETFData) -> ETFData:
        """Get document URLs for a specific ETF."""
        logger.info(f"Getting documents for {etf.ticker}")
        
        try:
            if self.session:
                async with self.session.get(etf.fund_url) as response:
                    response.raise_for_status()
                    html = await response.text()
            else:
                # Fallback to Selenium
                driver = self._init_selenium_driver()
                driver.get(etf.fund_url)
                html = driver.page_source
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract document URLs
            etf.fact_sheet_url = self._find_document_url(soup, ['fact sheet', 'factsheet'])
            etf.holdings_url = self._find_document_url(soup, ['holdings', 'portfolio'])
            etf.prospectus_url = self._find_document_url(soup, ['prospectus'])
            etf.annual_report_url = self._find_document_url(soup, ['annual report', 'report'])
            
            # Find additional data files
            data_files = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in self.config.download_extensions):
                    file_url = urljoin(self.config.base_url, href)
                    file_type = self._classify_file_type(link.get_text(strip=True), href)
                    data_files.append({
                        'url': file_url,
                        'type': file_type,
                        'filename': urlparse(href).path.split('/')[-1]
                    })
                    
            etf.data_files = data_files
            
        except Exception as e:
            logger.error(f"Error getting documents for {etf.ticker}: {e}")
            
        return etf
        
    def _find_document_url(self, soup: BeautifulSoup, keywords: List[str]) -> Optional[str]:
        """Find document URL by keywords."""
        for keyword in keywords:
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True).lower()
                if keyword.lower() in link_text:
                    return urljoin(self.config.base_url, link['href'])
        return None
        
    def _classify_file_type(self, link_text: str, url: str) -> str:
        """Classify file type based on link text and URL."""
        link_text = link_text.lower()
        url = url.lower()
        
        if any(term in link_text for term in ['fact sheet', 'factsheet']):
            return 'fact_sheet'
        elif any(term in link_text for term in ['holdings', 'portfolio']):
            return 'holdings'
        elif 'prospectus' in link_text:
            return 'prospectus'
        elif any(term in link_text for term in ['annual report', 'report']):
            return 'annual_report'
        elif '.pdf' in url:
            return 'pdf'
        elif '.csv' in url:
            return 'csv'
        elif '.xlsx' in url:
            return 'excel'
        elif '.json' in url:
            return 'json'
        else:
            return 'other'