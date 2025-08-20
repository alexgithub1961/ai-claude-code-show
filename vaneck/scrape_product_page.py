#!/usr/bin/env python3
"""
Scrape VanEck product page to find actual PDF links.
"""

import asyncio
import re
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup


class VanEckProductScraper:
    """Scrape VanEck product pages to find PDF download links."""
    
    def __init__(self):
        self.base_url = "https://www.vaneck.com"
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
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
    
    async def scrape_product_page(self, ticker: str) -> Dict:
        """Scrape the product page for a given ticker to find PDF links."""
        # Try different product page URL patterns
        url_patterns = [
            f"{self.base_url}/us/en/investments/gold-miners-etf-{ticker.lower()}/",
            f"{self.base_url}/us/en/investments/{ticker.lower()}-etf/",
            f"{self.base_url}/us/en/etf/{ticker.lower()}/",
            f"{self.base_url}/etf/{ticker.lower()}/",
        ]
        
        results = {
            'ticker': ticker,
            'product_url': None,
            'pdf_links': [],
            'csv_links': [],
            'other_links': [],
            'page_title': None,
            'error': None
        }
        
        async with httpx.AsyncClient() as client:
            for url_pattern in url_patterns:
                try:
                    print(f"Trying product page: {url_pattern}")
                    response = await client.get(
                        url_pattern,
                        headers=self.headers,
                        follow_redirects=True,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        results['product_url'] = str(response.url)
                        print(f"✓ Found product page: {response.url}")
                        
                        # Parse the HTML
                        soup = BeautifulSoup(response.content, 'html.parser')
                        results['page_title'] = soup.title.string.strip() if soup.title else None
                        
                        # Find all links that might be PDFs or CSVs
                        all_links = soup.find_all('a', href=True)
                        
                        for link in all_links:
                            href = link['href']
                            link_text = link.get_text(strip=True).lower()
                            
                            # Make href absolute if it's relative
                            if href.startswith('/'):
                                href = self.base_url + href
                            elif not href.startswith('http'):
                                continue
                            
                            # Categorise links
                            if '.pdf' in href.lower():
                                results['pdf_links'].append({
                                    'url': href,
                                    'text': link_text,
                                    'type': self._classify_pdf_type(link_text, href)
                                })
                            elif '.csv' in href.lower():
                                results['csv_links'].append({
                                    'url': href,
                                    'text': link_text,
                                    'type': 'holdings'
                                })
                            elif any(term in link_text for term in ['download', 'document', 'report', 'prospectus', 'fact sheet']):
                                results['other_links'].append({
                                    'url': href,
                                    'text': link_text
                                })
                        
                        # Also check for JavaScript-generated links or data attributes
                        scripts = soup.find_all('script')
                        for script in scripts:
                            if script.string:
                                # Look for PDF URLs in JavaScript
                                pdf_matches = re.findall(r'https?://[^"\s]+\.pdf', script.string)
                                for match in pdf_matches:
                                    if match not in [link['url'] for link in results['pdf_links']]:
                                        results['pdf_links'].append({
                                            'url': match,
                                            'text': 'Found in JavaScript',
                                            'type': 'script'
                                        })
                        
                        break  # Found a working product page
                        
                except Exception as e:
                    print(f"✗ Error trying {url_pattern}: {e}")
                    continue
        
        if not results['product_url']:
            results['error'] = f"Could not find product page for ticker {ticker}"
        
        return results
    
    def _classify_pdf_type(self, link_text: str, href: str) -> str:
        """Classify the type of PDF based on link text and URL."""
        link_text_lower = link_text.lower()
        href_lower = href.lower()
        
        if 'fact sheet' in link_text_lower or 'factsheet' in link_text_lower or 'fact-sheet' in href_lower:
            return 'fact_sheet'
        elif 'prospectus' in link_text_lower or 'prospectus' in href_lower:
            return 'prospectus'
        elif 'annual report' in link_text_lower or 'annual-report' in href_lower:
            return 'annual_report'
        elif 'semi annual' in link_text_lower or 'semi-annual' in href_lower:
            return 'semi_annual_report'
        elif 'summary' in link_text_lower or 'summary' in href_lower:
            return 'summary'
        else:
            return 'other'
    
    def display_results(self, results: Dict):
        """Display the scraping results."""
        ticker = results['ticker']
        print(f"\n=== Results for {ticker} ===")
        
        if results.get('error'):
            print(f"❌ Error: {results['error']}")
            return
        
        print(f"Product URL: {results['product_url']}")
        print(f"Page Title: {results['page_title']}")
        
        if results['pdf_links']:
            print(f"\n📄 PDF Links ({len(results['pdf_links'])}):")
            for pdf in results['pdf_links']:
                print(f"  - {pdf['type']}: {pdf['text']}")
                print(f"    URL: {pdf['url']}")
        
        if results['csv_links']:
            print(f"\n📊 CSV Links ({len(results['csv_links'])}):")
            for csv in results['csv_links']:
                print(f"  - {csv['text']}")
                print(f"    URL: {csv['url']}")
        
        if results['other_links']:
            print(f"\n🔗 Other Relevant Links ({len(results['other_links'])}):")
            for link in results['other_links'][:5]:  # Limit to first 5
                print(f"  - {link['text']}")
                print(f"    URL: {link['url']}")
    
    async def run_analysis(self, tickers: List[str] = None):
        """Run analysis for given tickers."""
        if tickers is None:
            tickers = ['GDX', 'GDXJ', 'VTI']
        
        print("🔍 VanEck Product Page Scraper")
        print(f"Analysing {len(tickers)} tickers")
        
        all_results = []
        
        for ticker in tickers:
            results = await self.scrape_product_page(ticker)
            all_results.append(results)
            self.display_results(results)
            
            # Small delay to be respectful
            await asyncio.sleep(1)
        
        # Save results
        import json
        results_file = Path('debug_downloads') / 'product_scrape_results.json'
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n📁 Results saved to: {results_file}")
        
        return all_results


async def main():
    """Main entry point."""
    scraper = VanEckProductScraper()
    await scraper.run_analysis(['GDX', 'GDXJ'])


if __name__ == "__main__":
    asyncio.run(main())