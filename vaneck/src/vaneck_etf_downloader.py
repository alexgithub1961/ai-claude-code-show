#!/usr/bin/env python3
"""
VanEck ETF Data Downloader - Real Implementation
Downloads ETF data from VanEck website
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import aiohttp
import httpx
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

console = Console()


class VanEckETFDownloader:
    """Downloads ETF data from VanEck website."""
    
    def __init__(self, download_dir: str = "download", max_concurrent: int = 3):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self.base_url = "https://www.vaneck.com"
        self.api_url = "https://www.vaneck.com/api/fundfinder"
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
        """Fetch the list of ETFs from VanEck API."""
        console.print("[bold blue]Fetching ETF list from VanEck...[/bold blue]")
        
        # VanEck uses an API endpoint for fund data
        params = {
            "InvType": "etf",
            "AssetClass": "c,nr,t,cb,ei,ib,mb,fr,c-ra,c-da,c-g",
            "Funds": "emf,grf,iigf,mwmf,embf,ccif",
            "ShareClass": "a,c,i,y,z",
            "Sort": "name",
            "SortDesc": "true"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                # Try the API endpoint first
                async with session.get(
                    f"{self.api_url}/etf",
                    headers=self.headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        console.print(f"[green]Found {len(data)} ETFs via API[/green]")
                        return data
            except Exception as e:
                console.print(f"[yellow]API request failed: {e}. Falling back to HTML scraping...[/yellow]")
                
            # Fallback to HTML scraping
            return await self._scrape_etf_list(session)
    
    async def _scrape_etf_list(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Scrape ETF list from HTML page as fallback."""
        url = "https://www.vaneck.com/us/en/investments/etfs/"
        
        async with session.get(url, headers=self.headers) as response:
            if response.status != 200:
                console.print(f"[red]Failed to fetch ETF page: {response.status}[/red]")
                return []
                
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            
            etfs = []
            # Look for ETF table or grid
            etf_elements = soup.find_all('div', class_=re.compile(r'fund-item|etf-row|product-row'))
            
            if not etf_elements:
                # Try alternative selectors
                etf_elements = soup.find_all('tr', class_=re.compile(r'fund|etf'))
            
            for element in etf_elements:
                try:
                    # Extract ticker
                    ticker_elem = element.find(class_=re.compile(r'ticker|symbol'))
                    ticker = ticker_elem.text.strip() if ticker_elem else None
                    
                    # Extract name
                    name_elem = element.find(class_=re.compile(r'fund-name|product-name'))
                    name = name_elem.text.strip() if name_elem else None
                    
                    # Extract URL
                    link_elem = element.find('a', href=re.compile(r'/etf/'))
                    url = self.base_url + link_elem['href'] if link_elem else None
                    
                    if ticker:
                        etfs.append({
                            'ticker': ticker,
                            'name': name or ticker,
                            'url': url,
                            'assetClass': 'ETF'
                        })
                except Exception as e:
                    continue
            
            console.print(f"[green]Found {len(etfs)} ETFs via HTML scraping[/green]")
            return etfs
    
    async def download_etf_data(self, etf: Dict, session: aiohttp.ClientSession) -> bool:
        """Download data for a single ETF."""
        ticker = etf.get('ticker', 'UNKNOWN')
        etf_dir = self.download_dir / ticker
        etf_dir.mkdir(exist_ok=True)
        
        success = False
        
        # Save ETF metadata
        metadata_file = etf_dir / f"{ticker}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(etf, f, indent=2)
            
        # Download fact sheet with improved URL patterns and retry logic
        fact_sheet_success = False
        if etf.get('url'):
            fact_sheet_success = await self._download_fact_sheet_with_retry(etf, session, etf_dir, ticker)
        
        # Download holdings data with multiple URL patterns
        holdings_patterns = [
            f"{self.base_url}/us/en/assets/resources/holdings/{ticker.lower()}-holdings.csv",
            f"{self.base_url}/assets/resources/holdings/{ticker.lower()}-holdings.csv",
            f"{self.base_url}/holdings/{ticker.lower()}.csv",
            f"{self.base_url}/us/en/investments/{ticker.lower()}-holdings.csv",
        ]
        
        holdings_file = etf_dir / f"{ticker}_holdings.csv"
        holdings_success = False
        
        for holdings_url in holdings_patterns:
            try:
                async with session.get(holdings_url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        
                        # Check if it's CSV data
                        if ('csv' in content_type or 'text/' in content_type):
                            content = await response.text()
                            with open(holdings_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            holdings_success = True
                            console.print(f"[green]✓[/green] Downloaded holdings for {ticker}")
                            break
            except Exception as e:
                continue
        
        if not holdings_success:
            console.print(f"[yellow]ⓘ[/yellow] No holdings data found for {ticker}")
        
        success = fact_sheet_success or holdings_success
            
        return success
    
    async def _download_fact_sheet_with_retry(self, etf: Dict, session: aiohttp.ClientSession, etf_dir: Path, ticker: str) -> bool:
        """Download fact sheet PDF with multiple URL patterns and retry logic."""
        import re
        
        product_url = etf.get('url', '')
        
        # Generate fact sheet URL patterns based on discovered working patterns
        fact_sheet_patterns = []
        
        # Pattern 1: Direct fact sheet URL (discovered working pattern)
        if product_url and 'investments/' in product_url:
            # Extract the ETF name part from product URL
            # e.g., "/investments/gold-miners-etf-gdx/" -> "gold-miners-etf-gdx"
            match = re.search(r'/investments/([^/]+)', product_url)
            if match:
                etf_path = match.group(1)
                if etf_path.endswith('/'):
                    etf_path = etf_path[:-1]
                fact_sheet_url = f"{self.base_url}/us/en/investments/{etf_path}-fact-sheet.pdf"
                fact_sheet_patterns.append(("direct_product_path", fact_sheet_url))
        
        # Pattern 2: Common naming patterns
        ticker_lower = ticker.lower()
        common_patterns = [
            ("simple_ticker", f"{self.base_url}/us/en/investments/{ticker_lower}-etf-fact-sheet.pdf"),
            ("ticker_with_etf", f"{self.base_url}/us/en/investments/{ticker_lower}-fact-sheet.pdf"),
            ("assets_resources", f"{self.base_url}/us/en/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"),
            ("direct_assets", f"{self.base_url}/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"),
        ]
        
        fact_sheet_patterns.extend(common_patterns)
        
        # Try each URL pattern
        for pattern_name, url in fact_sheet_patterns:
            try:
                # Set proper headers and referer
                headers = self.pdf_headers.copy()
                if product_url:
                    headers['Referer'] = product_url
                
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        content = await response.read()
                        
                        # Check if it's actually a PDF
                        if ('pdf' in content_type or content.startswith(b'%PDF')):
                            pdf_file = etf_dir / f"{ticker}_fact_sheet.pdf"
                            with open(pdf_file, 'wb') as f:
                                f.write(content)
                            console.print(f"[green]✓[/green] Downloaded fact sheet for {ticker} ({len(content)} bytes)")
                            return True
                        else:
                            console.print(f"[yellow]⚠[/yellow] URL returned non-PDF content for {ticker}: {content_type}")
                    else:
                        console.print(f"[yellow]⚠[/yellow] HTTP {response.status} for {ticker} fact sheet: {url}")
                        
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Error downloading fact sheet for {ticker} from {url}: {e}")
                continue
        
        console.print(f"[red]✗[/red] Could not download fact sheet for {ticker} after trying {len(fact_sheet_patterns)} URL patterns")
        return False
    
    async def download_all(self, max_etfs: int = 5, dry_run: bool = False):
        """Download data for multiple ETFs."""
        etfs = await self.fetch_etf_list()
        
        if not etfs:
            # Use sample data for demonstration
            console.print("[yellow]Using sample ETF data for demonstration...[/yellow]")
            etfs = [
                {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "url": "/etf/vti"},
                {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "url": "/etf/bnd"},
                {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "url": "/etf/vea"},
                {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "url": "/etf/vwo"},
                {"ticker": "GDX", "name": "VanEck Gold Miners ETF", "url": "/etf/gdx"},
            ]
        
        # Limit number of ETFs
        etfs_to_download = etfs[:max_etfs]
        
        # Display ETF table
        table = Table(title=f"ETFs to Download (max {max_etfs})")
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Status", justify="right")
        
        for etf in etfs_to_download:
            status = "🔄 Pending" if not dry_run else "⏭️ Dry Run"
            table.add_row(etf.get('ticker', 'N/A'), etf.get('name', 'Unknown'), status)
        
        console.print(table)
        
        if dry_run:
            console.print("\n[yellow]DRY RUN MODE - No files will be downloaded[/yellow]")
            return
        
        # Download ETF data
        console.print(f"\n[bold]Downloading data for {len(etfs_to_download)} ETFs...[/bold]")
        
        async with aiohttp.ClientSession() as session:
            # Use semaphore to limit concurrent downloads
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def download_with_limit(etf):
                async with semaphore:
                    return await self.download_etf_data(etf, session)
            
            # Create progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("Downloading ETFs...", total=len(etfs_to_download))
                
                tasks = []
                for etf in etfs_to_download:
                    tasks.append(download_with_limit(etf))
                    
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    progress.update(task, advance=1)
                    if isinstance(result, Exception):
                        console.print(f"[red]Error downloading {etfs_to_download[i]['ticker']}: {result}[/red]")
        
        # Summary
        console.print(f"\n[bold green]✅ Download complete![/bold green]")
        console.print(f"Files saved to: {self.download_dir.absolute()}")
        
        # List downloaded files
        total_files = sum(1 for _ in self.download_dir.glob("*/*"))
        console.print(f"Total files downloaded: {total_files}")


async def main(download_dir: str = "download", max_etfs: int = 5, dry_run: bool = False):
    """Main entry point."""
    downloader = VanEckETFDownloader(download_dir=download_dir)
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