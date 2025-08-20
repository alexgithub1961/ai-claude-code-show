#!/usr/bin/env python3
"""
Fixed VanEck ETF Data Downloader with Correct URL Patterns
Based on investigation findings
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


class FixedVanEckETFDownloader:
    """Fixed downloader with correct URL patterns and session management."""
    
    # Known ETF name mappings for URL construction
    ETF_NAME_MAPPINGS = {
        'GDX': 'gold-miners-etf',
        'GDXJ': 'junior-gold-miners-etf',
        'SLV': 'silver-etf',
        'VTI': 'total-stock-market-etf',
        'BND': 'total-bond-market-etf',
        'VEA': 'ftse-developed-markets-etf',
        'VWO': 'ftse-emerging-markets-etf',
        'MOAT': 'morningstar-wide-moat-etf',
        'NLR': 'uranium-nuclear-energy-etf',
        'REMX': 'rare-earth-strategic-metals-etf',
    }
    
    def __init__(self, download_dir: str = "download", max_concurrent: int = 3):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self.base_url = "https://www.vaneck.com"
        
        # Enhanced headers that mimic a real browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
    async def fetch_etf_list(self) -> List[Dict]:
        """Fetch the list of ETFs from VanEck website."""
        console.print("[bold blue]Fetching ETF list from VanEck...[/bold blue]")
        
        # Try to fetch the main investments page
        url = "https://www.vaneck.com/us/en/investments/etfs/"
        
        async with aiohttp.ClientSession() as session:
            # First establish session by visiting main page
            async with session.get(self.base_url, headers=self.headers) as response:
                await response.text()  # Consume response to set cookies
            
            # Now fetch the ETF list page
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    console.print(f"[yellow]Could not fetch ETF list, using sample data[/yellow]")
                    return self._get_sample_etfs()
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                etfs = []
                # Look for ETF links
                etf_links = soup.find_all('a', href=re.compile(r'/investments/[^/]+-etf-[^/]+/?$'))
                
                for link in etf_links[:20]:  # Limit to first 20
                    try:
                        href = link['href']
                        # Extract ticker from URL
                        ticker_match = re.search(r'-([A-Z]+)/?$', href, re.I)
                        if ticker_match:
                            ticker = ticker_match.group(1).upper()
                            name = link.get_text(strip=True) or ticker
                            
                            etfs.append({
                                'ticker': ticker,
                                'name': name,
                                'url': href if href.startswith('http') else self.base_url + href,
                                'etf_slug': self._extract_etf_slug(href)
                            })
                    except Exception:
                        continue
                
                if etfs:
                    console.print(f"[green]Found {len(etfs)} ETFs[/green]")
                    return etfs
                else:
                    return self._get_sample_etfs()
    
    def _extract_etf_slug(self, url: str) -> str:
        """Extract the ETF slug from URL for constructing document URLs."""
        # Extract from patterns like /investments/gold-miners-etf-gdx/
        match = re.search(r'/investments/([^/]+)', url)
        if match:
            slug = match.group(1).rstrip('/')
            # Remove trailing ticker if present
            slug = re.sub(r'-[A-Z]+$', '', slug, flags=re.I)
            return slug
        return ""
    
    def _get_sample_etfs(self) -> List[Dict]:
        """Return sample ETF data with correct slugs."""
        return [
            {
                "ticker": "GDX", 
                "name": "VanEck Gold Miners ETF",
                "url": "/us/en/investments/gold-miners-etf-gdx/",
                "etf_slug": "gold-miners-etf"
            },
            {
                "ticker": "GDXJ",
                "name": "VanEck Junior Gold Miners ETF", 
                "url": "/us/en/investments/junior-gold-miners-etf-gdxj/",
                "etf_slug": "junior-gold-miners-etf"
            },
            {
                "ticker": "MOAT",
                "name": "VanEck Morningstar Wide Moat ETF",
                "url": "/us/en/investments/morningstar-wide-moat-etf-moat/",
                "etf_slug": "morningstar-wide-moat-etf"
            },
            {
                "ticker": "NLR",
                "name": "VanEck Uranium+Nuclear Energy ETF",
                "url": "/us/en/investments/uranium-nuclear-energy-etf-nlr/",
                "etf_slug": "uranium-nuclear-energy-etf"
            },
            {
                "ticker": "REMX",
                "name": "VanEck Rare Earth/Strategic Metals ETF",
                "url": "/us/en/investments/rare-earth-strategic-metals-etf-remx/",
                "etf_slug": "rare-earth-strategic-metals-etf"
            },
        ]
    
    async def download_etf_data(self, etf: Dict, session: aiohttp.ClientSession) -> bool:
        """Download data for a single ETF with correct URL patterns."""
        ticker = etf.get('ticker', 'UNKNOWN')
        etf_dir = self.download_dir / ticker
        etf_dir.mkdir(exist_ok=True)
        
        # Save ETF metadata
        metadata_file = etf_dir / f"{ticker}_metadata.json"
        etf['download_time'] = datetime.now().isoformat()
        with open(metadata_file, 'w') as f:
            json.dump(etf, f, indent=2)
        
        success_count = 0
        
        # Get ETF slug for URL construction
        etf_slug = etf.get('etf_slug') or self.ETF_NAME_MAPPINGS.get(ticker, f"{ticker.lower()}-etf")
        ticker_lower = ticker.lower()
        
        # Correct fact sheet URL patterns based on investigation
        fact_sheet_urls = [
            # Primary pattern: /us/en/investments/{etf-name}-{ticker}-fact-sheet.pdf
            f"{self.base_url}/us/en/investments/{etf_slug}-{ticker_lower}-fact-sheet.pdf",
            # Alternative without ticker
            f"{self.base_url}/us/en/investments/{etf_slug}-fact-sheet.pdf",
            # Content files pattern
            f"{self.base_url}/content/files/etf/{ticker_lower}/fact-sheet.pdf",
        ]
        
        # Try downloading fact sheet
        pdf_file = etf_dir / f"{ticker}_fact_sheet.pdf"
        for url in fact_sheet_urls:
            try:
                headers = self.headers.copy()
                headers['Accept'] = 'application/pdf,*/*'
                
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        content = await response.read()
                        # Verify it's a PDF
                        if content.startswith(b'%PDF'):
                            with open(pdf_file, 'wb') as f:
                                f.write(content)
                            console.print(f"[green]✓[/green] Downloaded fact sheet for {ticker} ({len(content):,} bytes)")
                            success_count += 1
                            break
                        else:
                            console.print(f"[dim]Non-PDF content from {url}[/dim]")
            except Exception as e:
                console.print(f"[dim]Failed {url}: {str(e)[:50]}[/dim]")
                continue
        
        # Try downloading holdings CSV
        holdings_urls = [
            f"{self.base_url}/us/en/investments/{etf_slug}-{ticker_lower}-holdings.csv",
            f"{self.base_url}/content/holdings/{ticker_lower}.csv",
            f"{self.base_url}/api/holdings/{ticker_lower}",
        ]
        
        holdings_file = etf_dir / f"{ticker}_holdings.csv"
        for url in holdings_urls:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Check if it's CSV-like data
                        if ',' in content[:1000] and not content.startswith('<!'):
                            with open(holdings_file, 'w') as f:
                                f.write(content)
                            console.print(f"[green]✓[/green] Downloaded holdings for {ticker}")
                            success_count += 1
                            break
            except Exception:
                continue
        
        return success_count > 0
    
    async def download_all(self, max_etfs: int = 5, dry_run: bool = False):
        """Download data for multiple ETFs."""
        etfs = await self.fetch_etf_list()
        
        if not etfs:
            etfs = self._get_sample_etfs()
            console.print("[yellow]Using sample ETF data[/yellow]")
        
        # Limit number of ETFs
        etfs_to_download = etfs[:max_etfs]
        
        # Display ETF table
        table = Table(title=f"ETFs to Download (max {max_etfs})")
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("ETF Slug", style="yellow")
        table.add_column("Status", justify="right")
        
        for etf in etfs_to_download:
            status = "🔄 Pending" if not dry_run else "⏭️ Dry Run"
            table.add_row(
                etf.get('ticker', 'N/A'),
                etf.get('name', 'Unknown')[:40],
                etf.get('etf_slug', 'N/A')[:25],
                status
            )
        
        console.print(table)
        
        if dry_run:
            console.print("\n[yellow]DRY RUN MODE - No files will be downloaded[/yellow]")
            return
        
        # Download ETF data with session reuse
        console.print(f"\n[bold]Downloading data for {len(etfs_to_download)} ETFs...[/bold]")
        
        async with aiohttp.ClientSession() as session:
            # Establish session
            await session.get(self.base_url, headers=self.headers)
            
            # Download with concurrency limit
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def download_with_limit(etf):
                async with semaphore:
                    await asyncio.sleep(1)  # Rate limiting
                    return await self.download_etf_data(etf, session)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task = progress.add_task("Downloading ETFs...", total=len(etfs_to_download))
                
                tasks = [download_with_limit(etf) for etf in etfs_to_download]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    progress.update(task, advance=1)
        
        # Summary
        console.print(f"\n[bold green]✅ Download complete![/bold green]")
        console.print(f"Files saved to: {self.download_dir.absolute()}")
        
        # Count files
        total_files = sum(1 for _ in self.download_dir.glob("*/*"))
        console.print(f"Total files downloaded: {total_files}")


async def main(download_dir: str = "download", max_etfs: int = 5, dry_run: bool = False):
    """Main entry point."""
    downloader = FixedVanEckETFDownloader(download_dir=download_dir)
    await downloader.download_all(max_etfs=max_etfs, dry_run=dry_run)


if __name__ == "__main__":
    import sys
    
    # Parse command line args
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