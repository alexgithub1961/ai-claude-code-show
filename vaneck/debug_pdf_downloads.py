#!/usr/bin/env python3
"""
Debug script to test different URL patterns and headers for VanEck PDF downloads.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

import httpx
from rich.console import Console
from rich.table import Table

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_downloads.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

console = Console()


class VanEckPDFDebugger:
    """Debug PDF downloads from VanEck website."""
    
    def __init__(self):
        self.base_url = "https://www.vaneck.com"
        self.download_dir = Path("debug_downloads")
        self.download_dir.mkdir(exist_ok=True)
        
        # Test different headers configurations
        self.headers_variants = {
            'basic': {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/pdf,application/octet-stream,*/*",
                "Accept-Language": "en-GB,en;q=0.9",
            },
            'browser_like': {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
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
            },
            'with_referer': {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/pdf,application/octet-stream,*/*",
                "Accept-Language": "en-GB,en;q=0.9",
                "Referer": "https://www.vaneck.com/us/en/etf/gdx/",
            }
        }
    
    def generate_url_patterns(self, ticker: str) -> List[Dict[str, str]]:
        """Generate different URL patterns to test."""
        ticker_lower = ticker.lower()
        ticker_upper = ticker.upper()
        
        patterns = [
            # Current pattern from the code
            {
                'name': 'current_code_pattern',
                'url': f"{self.base_url}/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"
            },
            # Common document patterns
            {
                'name': 'us_en_assets',
                'url': f"{self.base_url}/us/en/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"
            },
            {
                'name': 'direct_assets',
                'url': f"{self.base_url}/assets/fact-sheets/{ticker_lower}-fact-sheet.pdf"
            },
            {
                'name': 'documents_folder',
                'url': f"{self.base_url}/documents/{ticker_lower}-fact-sheet.pdf"
            },
            {
                'name': 'pdfs_folder',
                'url': f"{self.base_url}/pdfs/{ticker_lower}-fact-sheet.pdf"
            },
            # Upper case variants
            {
                'name': 'upper_case_ticker',
                'url': f"{self.base_url}/assets/resources/fact-sheets/{ticker_upper}-fact-sheet.pdf"
            },
            {
                'name': 'us_en_upper',
                'url': f"{self.base_url}/us/en/assets/resources/fact-sheets/{ticker_upper}-fact-sheet.pdf"
            },
            # Different file naming patterns
            {
                'name': 'factsheet_single_word',
                'url': f"{self.base_url}/assets/resources/fact-sheets/{ticker_lower}-factsheet.pdf"
            },
            {
                'name': 'fact_sheet_underscore',
                'url': f"{self.base_url}/assets/resources/fact-sheets/{ticker_lower}_fact_sheet.pdf"
            },
            {
                'name': 'prospectus_pattern',
                'url': f"{self.base_url}/assets/resources/prospectuses/{ticker_lower}-prospectus.pdf"
            },
            # Holdings patterns
            {
                'name': 'holdings_csv',
                'url': f"{self.base_url}/us/en/assets/resources/holdings/{ticker_lower}-holdings.csv"
            },
            {
                'name': 'holdings_direct',
                'url': f"{self.base_url}/assets/resources/holdings/{ticker_lower}-holdings.csv"
            }
        ]
        
        return patterns
    
    async def test_url(self, client: httpx.AsyncClient, url: str, headers: Dict[str, str], pattern_name: str) -> Dict:
        """Test a single URL with given headers."""
        logger.info(f"Testing {pattern_name}: {url}")
        
        try:
            response = await client.get(
                url, 
                headers=headers,
                follow_redirects=True,
                timeout=30.0
            )
            
            result = {
                'pattern': pattern_name,
                'url': url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', 'unknown'),
                'content_length': response.headers.get('content-length', 'unknown'),
                'final_url': str(response.url),
                'redirected': str(response.url) != url,
                'success': False,
                'error': None
            }
            
            # Check if it's a PDF or other document
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type or 'octet-stream' in content_type:
                    result['success'] = True
                    # Save a small sample to verify it's actually a PDF
                    content_sample = response.content[:1024]  # First 1KB
                    if content_sample.startswith(b'%PDF'):
                        result['is_valid_pdf'] = True
                        logger.info(f"✓ Found valid PDF: {url}")
                    else:
                        result['is_valid_pdf'] = False
                        logger.warning(f"⚠ Response claims to be PDF but doesn't start with PDF header: {url}")
                elif 'text/csv' in content_type:
                    result['success'] = True
                    result['is_valid_csv'] = True
                    logger.info(f"✓ Found CSV: {url}")
                else:
                    # Check content anyway in case headers are wrong
                    content_sample = response.content[:1024]
                    if content_sample.startswith(b'%PDF'):
                        result['success'] = True
                        result['is_valid_pdf'] = True
                        result['content_type'] = 'application/pdf (detected)'
                        logger.info(f"✓ Found PDF (mismatched headers): {url}")
            
            return result
                
        except httpx.TimeoutException:
            logger.error(f"✗ Timeout: {url}")
            return {
                'pattern': pattern_name,
                'url': url,
                'status_code': None,
                'error': 'timeout',
                'success': False
            }
        except Exception as e:
            logger.error(f"✗ Error testing {url}: {e}")
            return {
                'pattern': pattern_name,
                'url': url,
                'status_code': None,
                'error': str(e),
                'success': False
            }
    
    async def debug_ticker(self, ticker: str) -> List[Dict]:
        """Debug downloads for a specific ticker."""
        console.print(f"\n[bold]Debugging downloads for ticker: {ticker}[/bold]")
        
        url_patterns = self.generate_url_patterns(ticker)
        all_results = []
        
        async with httpx.AsyncClient() as client:
            # Test each URL pattern with each header variant
            for pattern in url_patterns:
                for headers_name, headers in self.headers_variants.items():
                    test_name = f"{pattern['name']}_{headers_name}"
                    result = await self.test_url(
                        client, 
                        pattern['url'], 
                        headers, 
                        test_name
                    )
                    result['headers_variant'] = headers_name
                    all_results.append(result)
                    
                    # Small delay to be respectful
                    await asyncio.sleep(0.1)
        
        return all_results
    
    def display_results(self, results: List[Dict]):
        """Display test results in a table."""
        # Successful results
        successful = [r for r in results if r.get('success')]
        if successful:
            console.print("\n[bold green]✅ Successful Downloads:[/bold green]")
            success_table = Table()
            success_table.add_column("Pattern", style="green")
            success_table.add_column("Headers", style="cyan")
            success_table.add_column("Status", style="yellow")
            success_table.add_column("Content Type", style="magenta")
            success_table.add_column("URL", style="blue", max_width=50)
            
            for result in successful:
                success_table.add_row(
                    result['pattern'].replace('_' + result.get('headers_variant', ''), ''),
                    result.get('headers_variant', 'unknown'),
                    str(result.get('status_code', 'N/A')),
                    result.get('content_type', 'unknown'),
                    result['url']
                )
            
            console.print(success_table)
        
        # Failed results summary
        failed = [r for r in results if not r.get('success')]
        if failed:
            console.print(f"\n[bold red]❌ Failed Downloads: {len(failed)}[/bold red]")
            
            # Group by status code
            status_counts = {}
            for result in failed:
                status = result.get('status_code', 'error')
                if status not in status_counts:
                    status_counts[status] = []
                status_counts[status].append(result)
            
            fail_table = Table()
            fail_table.add_column("Status Code", style="red")
            fail_table.add_column("Count", style="yellow")
            fail_table.add_column("Example URL", style="blue", max_width=50)
            
            for status, examples in status_counts.items():
                fail_table.add_row(
                    str(status),
                    str(len(examples)),
                    examples[0]['url']
                )
            
            console.print(fail_table)
    
    async def run_debug(self, tickers: List[str] = None):
        """Run debug tests for given tickers."""
        if tickers is None:
            tickers = ['GDX', 'VTI', 'SPY', 'QQQ']  # Some common tickers to test
        
        console.print("[bold]🔍 VanEck PDF Download Debugger[/bold]")
        console.print(f"Testing {len(tickers)} tickers with {len(self.headers_variants)} header variants")
        console.print(f"Results will be logged to: debug_downloads.log")
        
        all_results = {}
        
        for ticker in tickers:
            results = await self.debug_ticker(ticker)
            all_results[ticker] = results
            self.display_results(results)
        
        # Save results to JSON for analysis
        results_file = self.download_dir / 'debug_results.json'
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        console.print(f"\n[bold]Debug results saved to: {results_file}[/bold]")
        
        # Summary
        total_tests = sum(len(results) for results in all_results.values())
        total_successful = sum(len([r for r in results if r.get('success')]) for results in all_results.values())
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"Total tests: {total_tests}")
        console.print(f"Successful: {total_successful}")
        console.print(f"Success rate: {(total_successful/total_tests*100):.1f}%")


async def main():
    """Main entry point."""
    debugger = VanEckPDFDebugger()
    
    # Test with some common VanEck ETF tickers
    test_tickers = ['GDX', 'GDXJ', 'VTI', 'SPY', 'ARKK']
    
    await debugger.run_debug(test_tickers)


if __name__ == "__main__":
    asyncio.run(main())