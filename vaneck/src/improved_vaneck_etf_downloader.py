#!/usr/bin/env python3
"""
Improved VanEck ETF Data Downloader
Downloads ETF data from VanEck website with proper URL patterns and error handling.
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vaneck_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ImprovedVanEckETFDownloader:
    """Improved VanEck ETF downloader with proper URL construction and error handling."""
    
    def __init__(self, download_dir: str = "download", max_concurrent: int = 3):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self.base_url = "https://www.vaneck.com"
        
        # Browser-like headers for better success rate
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # PDF-specific headers
        self.pdf_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/pdf,application/octet-stream,*/*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Cache-Control": "no-cache",
        }
        
    async def fetch_etf_list(self) -> List[Dict]:
        """Fetch the list of ETFs from VanEck."""
        logger.info("Fetching ETF list from VanEck...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Try the main ETFs listing page
                response = await client.get(
                    f"{self.base_url}/us/en/investments/etfs/",
                    headers=self.headers,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    etfs = await self._parse_etf_list(response.content)
                    logger.info(f"Found {len(etfs)} ETFs")
                    return etfs
                else:
                    logger.error(f"Failed to fetch ETF list: HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error fetching ETF list: {e}")
        
        # Fallback to sample data
        logger.warning("Using sample ETF data as fallback")
        return self._get_sample_etfs()
    
    async def _parse_etf_list(self, html_content: bytes) -> List[Dict]:
        """Parse the ETF list from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        etfs = []
        
        # Look for ETF links in various possible structures
        etf_selectors = [
            'a[href*="/investments/"][href*="-etf-"]',
            'a[href*="/etf/"]',
            '.etf-item a',
            '.fund-item a',
            'tr td a[href*="-etf-"]'
        ]
        
        for selector in etf_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if not href or href in [etf.get('url') for etf in etfs]:
                    continue
                
                # Extract ticker from URL or text
                ticker = self._extract_ticker_from_url(href) or self._extract_ticker_from_text(link.get_text())
                if not ticker:
                    continue
                
                # Get name from link text or nearby elements
                name = self._clean_etf_name(link.get_text()) or f"{ticker} ETF"
                
                # Make URL absolute
                if href.startswith('/'):
                    href = self.base_url + href
                
                etfs.append({
                    'ticker': ticker.upper(),
                    'name': name,
                    'url': href,
                    'type': 'ETF'
                })
        
        # Remove duplicates
        seen_tickers = set()
        unique_etfs = []
        for etf in etfs:
            if etf['ticker'] not in seen_tickers:
                unique_etfs.append(etf)
                seen_tickers.add(etf['ticker'])
        
        return unique_etfs[:50]  # Limit to first 50 for practical purposes
    
    def _extract_ticker_from_url(self, url: str) -> Optional[str]:
        """Extract ticker symbol from URL."""
        patterns = [
            r'etf-([a-zA-Z]+)/?$',
            r'/([a-zA-Z]+)-etf-',
            r'/etf/([a-zA-Z]+)/?',
            r'investments/([a-zA-Z]+)-',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                ticker = match.group(1)
                if 2 <= len(ticker) <= 5:  # Reasonable ticker length
                    return ticker
        return None
    
    def _extract_ticker_from_text(self, text: str) -> Optional[str]:
        """Extract ticker symbol from text."""
        # Look for patterns like "GDX" or "(GDX)"
        text = text.strip()
        match = re.search(r'\b([A-Z]{2,5})\b', text)
        if match:
            return match.group(1)
        return None
    
    def _clean_etf_name(self, text: str) -> str:
        """Clean and format ETF name."""
        if not text:
            return ""
        
        # Remove common suffixes and clean up
        text = re.sub(r'\s*\([A-Z]+\)\s*', '', text)  # Remove (TICKER)
        text = re.sub(r'\s*ETF\s*$', '', text, re.IGNORECASE)  # Remove trailing ETF
        text = text.strip()
        
        # Capitalise properly
        if text.isupper() or text.islower():
            text = text.title()
        
        return text
    
    def _get_sample_etfs(self) -> List[Dict]:
        """Get sample ETF data for testing."""
        return [
            {
                "ticker": "GDX",
                "name": "VanEck Gold Miners ETF",
                "url": f"{self.base_url}/us/en/investments/gold-miners-etf-gdx/",
                "type": "ETF"
            },
            {
                "ticker": "GDXJ", 
                "name": "VanEck Junior Gold Miners ETF",
                "url": f"{self.base_url}/us/en/investments/junior-gold-miners-etf-gdxj/",
                "type": "ETF"
            },
            {
                "ticker": "ARKK",
                "name": "ARK Innovation ETF",
                "url": f"{self.base_url}/us/en/investments/ark-innovation-etf-arkk/",
                "type": "ETF"
            }
        ]
    
    async def download_etf_documents(self, etf: Dict, client: httpx.AsyncClient) -> Dict:
        """Download documents for a single ETF with improved URL patterns and retry logic."""
        ticker = etf.get('ticker', 'UNKNOWN')
        etf_dir = self.download_dir / ticker
        etf_dir.mkdir(exist_ok=True)
        
        results = {
            'ticker': ticker,
            'success': False,
            'downloaded_files': [],
            'failed_downloads': [],
            'metadata_saved': False
        }
        
        logger.info(f"Processing ETF: {ticker}")
        
        # Save ETF metadata
        try:
            metadata_file = etf_dir / f"{ticker}_metadata.json"
            metadata = {
                **etf,
                'download_timestamp': datetime.now().isoformat(),
                'downloader_version': '2.0'
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            results['metadata_saved'] = True
            results['downloaded_files'].append(str(metadata_file))
            logger.info(f"✓ Saved metadata for {ticker}")
        except Exception as e:
            logger.error(f"✗ Failed to save metadata for {ticker}: {e}")
        
        # Download fact sheet PDF
        fact_sheet_success = await self._download_fact_sheet(etf, client, etf_dir, results)
        
        # Download holdings data
        holdings_success = await self._download_holdings_data(etf, client, etf_dir, results)
        
        # Download other documents (prospectus, etc.)
        other_docs_success = await self._download_other_documents(etf, client, etf_dir, results)
        
        results['success'] = fact_sheet_success or holdings_success or other_docs_success
        
        if results['success']:
            logger.info(f"✓ Successfully downloaded documents for {ticker}")
        else:
            logger.warning(f"⚠ No documents downloaded for {ticker}")
        
        return results
    
    async def _download_fact_sheet(self, etf: Dict, client: httpx.AsyncClient, etf_dir: Path, results: Dict) -> bool:
        """Download fact sheet PDF with multiple URL patterns."""
        ticker = etf['ticker']
        product_url = etf.get('url', '')
        
        # Generate fact sheet URL patterns
        fact_sheet_patterns = self._generate_fact_sheet_urls(ticker, product_url)
        
        for i, (pattern_name, url) in enumerate(fact_sheet_patterns):
            try:
                logger.info(f"Trying fact sheet pattern {i+1}/{len(fact_sheet_patterns)}: {pattern_name}")
                
                # Set referer based on product page
                headers = self.pdf_headers.copy()
                if product_url:
                    headers['Referer'] = product_url
                
                response = await client.get(
                    url,
                    headers=headers,
                    follow_redirects=True,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Check if it's actually a PDF
                    if ('pdf' in content_type or response.content.startswith(b'%PDF')):
                        pdf_file = etf_dir / f"{ticker}_fact_sheet.pdf"
                        with open(pdf_file, 'wb') as f:
                            f.write(response.content)
                        
                        results['downloaded_files'].append(str(pdf_file))
                        logger.info(f"✓ Downloaded fact sheet for {ticker} ({len(response.content)} bytes)")
                        return True
                    else:
                        logger.warning(f"⚠ URL returned non-PDF content for {ticker}: {content_type}")
                        results['failed_downloads'].append({
                            'url': url,
                            'pattern': pattern_name,
                            'reason': f'Non-PDF content: {content_type}'
                        })
                else:
                    logger.warning(f"⚠ HTTP {response.status_code} for {ticker} fact sheet: {url}")
                    results['failed_downloads'].append({
                        'url': url,
                        'pattern': pattern_name,
                        'reason': f'HTTP {response.status_code}'
                    })
                    
            except Exception as e:
                logger.error(f"✗ Error downloading fact sheet for {ticker} from {url}: {e}")
                results['failed_downloads'].append({
                    'url': url,
                    'pattern': pattern_name,
                    'reason': str(e)
                })
        
        return False
    
    def _generate_fact_sheet_urls(self, ticker: str, product_url: str) -> List[Tuple[str, str]]:
        """Generate fact sheet URL patterns based on discovered patterns."""
        ticker_lower = ticker.lower()
        
        patterns = []
        
        # Pattern 1: Direct fact sheet URL (discovered working pattern)
        if product_url and 'investments/' in product_url:
            # Extract the ETF name part from product URL
            # e.g., "/investments/gold-miners-etf-gdx/" -> "gold-miners-etf-gdx"
            match = re.search(r'/investments/([^/]+)', product_url)
            if match:
                etf_path = match.group(1)
                if not etf_path.endswith('/'):
                    fact_sheet_url = f"{self.base_url}/us/en/investments/{etf_path}-fact-sheet.pdf"
                else:
                    fact_sheet_url = f"{self.base_url}/us/en/investments/{etf_path}fact-sheet.pdf"
                patterns.append(("direct_product_path", fact_sheet_url))
        
        # Pattern 2: Common naming patterns
        common_patterns = [
            ("simple_ticker", f"{self.base_url}/us/en/investments/{ticker_lower}-etf-fact-sheet.pdf"),
            ("ticker_with_etf", f"{self.base_url}/us/en/investments/{ticker_lower}-fact-sheet.pdf"),
            ("assets_resources", f"{self.base_url}/us/en/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"),
            ("direct_assets", f"{self.base_url}/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"),
        ]
        
        patterns.extend(common_patterns)
        
        return patterns
    
    async def _download_holdings_data(self, etf: Dict, client: httpx.AsyncClient, etf_dir: Path, results: Dict) -> bool:
        """Download holdings CSV data."""
        ticker = etf['ticker']
        
        holdings_patterns = [
            f"{self.base_url}/us/en/assets/resources/holdings/{ticker.lower()}-holdings.csv",
            f"{self.base_url}/assets/resources/holdings/{ticker.lower()}-holdings.csv",
            f"{self.base_url}/holdings/{ticker.lower()}.csv",
            f"{self.base_url}/us/en/investments/{ticker.lower()}-holdings.csv",
        ]
        
        for pattern in holdings_patterns:
            try:
                response = await client.get(
                    pattern,
                    headers=self.headers,
                    follow_redirects=True,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Check if it's CSV data
                    if ('csv' in content_type or 'text/' in content_type):
                        holdings_file = etf_dir / f"{ticker}_holdings.csv"
                        with open(holdings_file, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        results['downloaded_files'].append(str(holdings_file))
                        logger.info(f"✓ Downloaded holdings for {ticker}")
                        return True
                        
            except Exception as e:
                logger.debug(f"Holdings pattern failed for {ticker}: {e}")
                continue
        
        logger.info(f"ⓘ No holdings data found for {ticker}")
        return False
    
    async def _download_other_documents(self, etf: Dict, client: httpx.AsyncClient, etf_dir: Path, results: Dict) -> bool:
        """Download other documents by scraping the product page."""
        ticker = etf['ticker']
        product_url = etf.get('url')
        
        if not product_url:
            return False
        
        try:
            # Get the product page to find document links
            response = await client.get(
                product_url,
                headers=self.headers,
                follow_redirects=True,
                timeout=30.0
            )
            
            if response.status_code != 200:
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True).lower()
                
                if '.pdf' in href.lower():
                    if href.startswith('/'):
                        href = self.base_url + href
                    
                    # Skip if it's the fact sheet (already handled)
                    if 'fact-sheet' in href or 'fact_sheet' in href:
                        continue
                    
                    pdf_links.append({
                        'url': href,
                        'text': link_text,
                        'type': self._classify_document_type(link_text, href)
                    })
            
            # Download found PDFs
            success = False
            for pdf_info in pdf_links:
                try:
                    pdf_response = await client.get(
                        pdf_info['url'],
                        headers=self.pdf_headers,
                        follow_redirects=True,
                        timeout=30.0
                    )
                    
                    if (pdf_response.status_code == 200 and 
                        ('pdf' in pdf_response.headers.get('content-type', '') or 
                         pdf_response.content.startswith(b'%PDF'))):
                        
                        doc_type = pdf_info['type']
                        pdf_file = etf_dir / f"{ticker}_{doc_type}.pdf"
                        
                        with open(pdf_file, 'wb') as f:
                            f.write(pdf_response.content)
                        
                        results['downloaded_files'].append(str(pdf_file))
                        logger.info(f"✓ Downloaded {doc_type} for {ticker}")
                        success = True
                        
                except Exception as e:
                    logger.debug(f"Failed to download {pdf_info['url']}: {e}")
                    continue
            
            return success
            
        except Exception as e:
            logger.debug(f"Error scraping product page for {ticker}: {e}")
            return False
    
    def _classify_document_type(self, link_text: str, href: str) -> str:
        """Classify document type based on text and URL."""
        text_lower = link_text.lower()
        href_lower = href.lower()
        
        if 'prospectus' in text_lower or 'prospectus' in href_lower:
            return 'prospectus'
        elif 'annual report' in text_lower or 'annual-report' in href_lower:
            return 'annual_report'
        elif 'semi annual' in text_lower or 'semi-annual' in href_lower:
            return 'semi_annual_report'
        elif 'summary' in text_lower:
            return 'summary'
        else:
            return 'other_document'
    
    async def download_all(self, max_etfs: int = 10, dry_run: bool = False):
        """Download data for multiple ETFs with improved error handling."""
        etfs = await self.fetch_etf_list()
        
        if not etfs:
            logger.error("No ETFs found to download")
            return
        
        # Limit number of ETFs
        etfs_to_download = etfs[:max_etfs]
        
        print(f"\n🔍 ETFs to Download (max {max_etfs})")
        print("=" * 80)
        for i, etf in enumerate(etfs_to_download, 1):
            status = "🔄 Pending" if not dry_run else "⏭️ Dry Run"
            print(f"{i:2d}. {etf.get('ticker', 'N/A'):5s} - {etf.get('name', 'Unknown')[:50]:50s} {status}")
        
        if dry_run:
            print(f"\n⚠️ DRY RUN MODE - No files will be downloaded")
            return
        
        print(f"\n🚀 Starting downloads...")
        print(f"📁 Download directory: {self.download_dir.absolute()}")
        print(f"📊 Concurrency limit: {self.max_concurrent}")
        
        # Track overall results
        overall_results = {
            'total_etfs': len(etfs_to_download),
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_files': 0,
            'etf_results': []
        }
        
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            # Use semaphore to limit concurrent downloads
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def download_with_limit(etf):
                async with semaphore:
                    return await self.download_etf_documents(etf, client)
            
            # Create tasks for all ETFs
            tasks = [download_with_limit(etf) for etf in etfs_to_download]
            
            # Execute downloads with progress tracking
            print(f"\n📥 Downloading documents...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error downloading {etfs_to_download[i]['ticker']}: {result}")
                    overall_results['failed_downloads'] += 1
                else:
                    overall_results['etf_results'].append(result)
                    if result['success']:
                        overall_results['successful_downloads'] += 1
                        overall_results['total_files'] += len(result['downloaded_files'])
                    else:
                        overall_results['failed_downloads'] += 1
        
        # Save overall results
        results_file = self.download_dir / 'download_results.json'
        overall_results['download_timestamp'] = datetime.now().isoformat()
        with open(results_file, 'w') as f:
            json.dump(overall_results, f, indent=2)
        
        # Display summary
        self._display_summary(overall_results)
    
    def _display_summary(self, results: Dict):
        """Display download summary."""
        print(f"\n✅ Download Complete!")
        print("=" * 80)
        print(f"📊 Total ETFs processed: {results['total_etfs']}")
        print(f"✅ Successful downloads: {results['successful_downloads']}")
        print(f"❌ Failed downloads: {results['failed_downloads']}")
        print(f"📄 Total files downloaded: {results['total_files']}")
        print(f"📁 Files saved to: {self.download_dir.absolute()}")
        
        success_rate = (results['successful_downloads'] / results['total_etfs'] * 100) if results['total_etfs'] > 0 else 0
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        # Show successful downloads
        successful_etfs = [r for r in results['etf_results'] if r['success']]
        if successful_etfs:
            print(f"\n✅ Successfully downloaded:")
            for etf_result in successful_etfs:
                ticker = etf_result['ticker']
                file_count = len(etf_result['downloaded_files'])
                print(f"   {ticker}: {file_count} files")
        
        # Show failed downloads
        failed_etfs = [r for r in results['etf_results'] if not r['success']]
        if failed_etfs:
            print(f"\n❌ Failed downloads:")
            for etf_result in failed_etfs:
                ticker = etf_result['ticker']
                print(f"   {ticker}: No documents downloaded")


async def main(download_dir: str = "download", max_etfs: int = 5, dry_run: bool = False):
    """Main entry point."""
    print("🚀 Improved VanEck ETF Downloader v2.0")
    print("=" * 50)
    
    downloader = ImprovedVanEckETFDownloader(download_dir=download_dir)
    await downloader.download_all(max_etfs=max_etfs, dry_run=dry_run)


if __name__ == "__main__":
    import sys
    
    # Parse simple command line args
    max_etfs = 5
    dry_run = False
    download_dir = "download"
    
    for arg in sys.argv[1:]:
        if arg.startswith("--max-etfs="):
            max_etfs = int(arg.split("=")[1])
        elif arg == "--dry-run":
            dry_run = True
        elif arg.startswith("--download-dir="):
            download_dir = arg.split("=")[1]
    
    asyncio.run(main(download_dir=download_dir, max_etfs=max_etfs, dry_run=dry_run))