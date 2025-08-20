#!/usr/bin/env python3
"""
Full VanEck ETF Downloader - Downloads all available ETFs with PDF verification
"""

import asyncio
import json
import re
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

import aiohttp
import httpx
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

console = Console()


class FullVanEckETFDownloader:
    """Downloads all VanEck ETFs with comprehensive validation."""
    
    # Complete ETF list from VanEck
    VANECK_ETFS = [
        {'ticker': 'GDX', 'name': 'Gold Miners ETF', 'slug': 'gold-miners-etf'},
        {'ticker': 'GDXJ', 'name': 'Junior Gold Miners ETF', 'slug': 'junior-gold-miners-etf'},
        {'ticker': 'MOAT', 'name': 'Morningstar Wide Moat ETF', 'slug': 'morningstar-wide-moat-etf'},
        {'ticker': 'NLR', 'name': 'Uranium+Nuclear Energy ETF', 'slug': 'uranium-nuclear-energy-etf'},
        {'ticker': 'REMX', 'name': 'Rare Earth/Strategic Metals ETF', 'slug': 'rare-earth-strategic-metals-etf'},
        {'ticker': 'SLV', 'name': 'Silver ETF', 'slug': 'silver-etf'},
        {'ticker': 'ESPO', 'name': 'Video Gaming and eSports ETF', 'slug': 'video-gaming-esports-etf'},
        {'ticker': 'SMH', 'name': 'Semiconductor ETF', 'slug': 'semiconductor-etf'},
        {'ticker': 'BUZF', 'name': 'BuzzFeed ETF', 'slug': 'buzzfeed-etf'},
        {'ticker': 'JETS', 'name': 'U.S. Global Jets ETF', 'slug': 'us-global-jets-etf'},
        {'ticker': 'OIH', 'name': 'Oil Services ETF', 'slug': 'oil-services-etf'},
        {'ticker': 'HAP', 'name': 'Natural Resources ETF', 'slug': 'natural-resources-etf'},
        {'ticker': 'RTM', 'name': 'Retail ETF', 'slug': 'retail-etf'},
        {'ticker': 'BDJ', 'name': 'Emerging Markets High Yield Bond ETF', 'slug': 'emerging-markets-high-yield-bond-etf'},
        {'ticker': 'ANGL', 'name': 'Fallen Angel High Yield Bond ETF', 'slug': 'fallen-angel-high-yield-bond-etf'},
        {'ticker': 'MOO', 'name': 'Agribusiness ETF', 'slug': 'agribusiness-etf'},
        {'ticker': 'CNXT', 'name': 'ChiNext ETF', 'slug': 'chinext-etf'},
        {'ticker': 'ASHR', 'name': 'China A-Shares ETF', 'slug': 'china-a-shares-etf'},
        {'ticker': 'KWEB', 'name': 'China Internet ETF', 'slug': 'china-internet-etf'},
        {'ticker': 'PEK', 'name': 'China Bond ETF', 'slug': 'china-bond-etf'},
        {'ticker': 'XMMO', 'name': 'MidCap Momentum ETF', 'slug': 'midcap-momentum-etf'},
        {'ticker': 'IFLY', 'name': 'Drone Economy ETF', 'slug': 'drone-economy-etf'},
        {'ticker': 'MES', 'name': 'Gulf States Index ETF', 'slug': 'gulf-states-index-etf'},
        {'ticker': 'RSXJ', 'name': 'Russia Small-Cap ETF', 'slug': 'russia-small-cap-etf'},
        {'ticker': 'KOL', 'name': 'Coal ETF', 'slug': 'coal-etf'},
        {'ticker': 'EVX', 'name': 'Environmental Services ETF', 'slug': 'environmental-services-etf'},
        {'ticker': 'FILL', 'name': 'Global Water ETF', 'slug': 'global-water-etf'},
        {'ticker': 'PHO', 'name': 'Water Resources ETF', 'slug': 'water-resources-etf'},
        {'ticker': 'RYN', 'name': 'Timber ETF', 'slug': 'timber-etf'},
        {'ticker': 'EDV', 'name': 'Energy Income ETF', 'slug': 'energy-income-etf'},
    ]
    
    def __init__(self, download_dir: str = "download", max_concurrent: int = 3):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self.base_url = "https://www.vaneck.com"
        self.download_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'pdf_verified': 0,
            'csv_downloaded': 0,
            'bytes_downloaded': 0
        }
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
    
    def verify_pdf_content(self, file_path: Path) -> Tuple[bool, str]:
        """Verify that a file is actually a PDF and get its hash."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    return False, ""
                
                # Calculate hash for deduplication
                f.seek(0)
                file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
                return True, file_hash
        except Exception:
            return False, ""
    
    async def fetch_all_etfs(self) -> List[Dict]:
        """Fetch complete list of VanEck ETFs."""
        console.print(Panel.fit("[bold blue]Fetching VanEck ETF List[/bold blue]"))
        
        # Try to fetch live data first
        async with aiohttp.ClientSession() as session:
            try:
                # Establish session
                await session.get(self.base_url, headers=self.headers)
                
                # Try to fetch ETF list page
                url = "https://www.vaneck.com/us/en/investments/etfs/"
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        # Extract ETFs from page
                        etfs = []
                        etf_links = soup.find_all('a', href=re.compile(r'/investments/[^/]+-etf-[^/]+/?$'))
                        
                        for link in etf_links:
                            href = link['href']
                            ticker_match = re.search(r'-([A-Z]+)/?$', href, re.I)
                            if ticker_match:
                                ticker = ticker_match.group(1).upper()
                                slug = re.search(r'/investments/([^/]+)', href)
                                if slug:
                                    slug_text = slug.group(1).rstrip('/')
                                    slug_text = re.sub(r'-[A-Z]+$', '', slug_text, flags=re.I)
                                    
                                    etfs.append({
                                        'ticker': ticker,
                                        'name': link.get_text(strip=True) or ticker,
                                        'slug': slug_text,
                                        'url': href
                                    })
                        
                        if etfs:
                            console.print(f"[green]Found {len(etfs)} ETFs from website[/green]")
                            return etfs
            except Exception as e:
                console.print(f"[yellow]Could not fetch live data: {str(e)[:50]}[/yellow]")
        
        # Use comprehensive fallback list
        console.print(f"[cyan]Using comprehensive ETF list ({len(self.VANECK_ETFS)} ETFs)[/cyan]")
        return self.VANECK_ETFS
    
    async def download_etf_data(self, etf: Dict, session: aiohttp.ClientSession, progress_task) -> Dict:
        """Download data for a single ETF with verification."""
        ticker = etf.get('ticker', 'UNKNOWN')
        etf_dir = self.download_dir / ticker
        etf_dir.mkdir(exist_ok=True)
        
        result = {
            'ticker': ticker,
            'name': etf.get('name', ''),
            'pdf_downloaded': False,
            'pdf_verified': False,
            'pdf_size': 0,
            'csv_downloaded': False,
            'csv_size': 0,
            'errors': []
        }
        
        # Save metadata
        metadata_file = etf_dir / f"{ticker}_metadata.json"
        etf['download_time'] = datetime.now().isoformat()
        with open(metadata_file, 'w') as f:
            json.dump(etf, f, indent=2)
        
        # Get ETF slug
        etf_slug = etf.get('slug', f"{ticker.lower()}-etf")
        ticker_lower = ticker.lower()
        
        # PDF download with verification
        pdf_file = etf_dir / f"{ticker}_fact_sheet.pdf"
        fact_sheet_urls = [
            f"{self.base_url}/us/en/investments/{etf_slug}-{ticker_lower}-fact-sheet.pdf",
            f"{self.base_url}/us/en/investments/{etf_slug}-fact-sheet.pdf",
            f"{self.base_url}/content/files/etf/{ticker_lower}/fact-sheet.pdf",
            f"{self.base_url}/us/en/vaneck-etfs/{ticker_lower}/{ticker_lower}-fact-sheet.pdf",
        ]
        
        for url in fact_sheet_urls:
            try:
                headers = self.headers.copy()
                headers['Accept'] = 'application/pdf,*/*'
                
                async with session.get(url, headers=headers, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Write file first
                        with open(pdf_file, 'wb') as f:
                            f.write(content)
                        
                        # Verify it's actually a PDF
                        is_pdf, file_hash = self.verify_pdf_content(pdf_file)
                        
                        if is_pdf:
                            result['pdf_downloaded'] = True
                            result['pdf_verified'] = True
                            result['pdf_size'] = len(content)
                            result['pdf_hash'] = file_hash
                            self.download_stats['pdf_verified'] += 1
                            self.download_stats['bytes_downloaded'] += len(content)
                            console.print(f"[green]✓[/green] {ticker}: PDF verified ({len(content):,} bytes, hash: {file_hash})")
                            break
                        else:
                            # Delete non-PDF file
                            pdf_file.unlink()
                            result['errors'].append(f"Not a PDF from {url}")
                            console.print(f"[yellow]⚠[/yellow] {ticker}: Not a PDF from {url}")
            except Exception as e:
                result['errors'].append(str(e)[:50])
                continue
        
        # Holdings download - first try to get the page and extract API URL
        holdings_csv_file = etf_dir / f"{ticker}_holdings.csv"
        holdings_json_file = etf_dir / f"{ticker}_holdings.json"
        
        # First, fetch the ETF page to get the API URL
        etf_page_url = f"{self.base_url}/us/en/investments/{etf_slug}-{ticker_lower}"
        
        try:
            async with session.get(etf_page_url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Extract API URL from JSON-LD metadata
                    api_url_match = re.search(r'"contentUrl"\s*:\s*"([^"]+GetDataset[^"]+)"', html)
                    
                    if api_url_match:
                        api_url = api_url_match.group(1)
                        
                        # Download actual holdings data from API
                        api_headers = self.headers.copy()
                        api_headers['Accept'] = 'application/json, text/plain, */*'
                        
                        async with session.get(api_url, headers=api_headers, timeout=aiohttp.ClientTimeout(total=30)) as api_response:
                            if api_response.status == 200:
                                holdings_data = await api_response.json()
                                
                                # Save as JSON
                                with open(holdings_json_file, 'w') as f:
                                    json.dump(holdings_data, f, indent=2)
                                
                                # Convert to CSV if holdings exist
                                if 'holdings' in holdings_data and holdings_data['holdings']:
                                    holdings = holdings_data['holdings']
                                    # Get all unique keys
                                    all_keys = set()
                                    for holding in holdings:
                                        all_keys.update(holding.keys())
                                    
                                    # Write CSV
                                    with open(holdings_csv_file, 'w', newline='', encoding='utf-8') as f:
                                        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                                        writer.writeheader()
                                        writer.writerows(holdings)
                                    
                                    result['csv_downloaded'] = True
                                    result['csv_size'] = holdings_json_file.stat().st_size
                                    self.download_stats['csv_downloaded'] += 1
                                    self.download_stats['bytes_downloaded'] += result['csv_size']
                                    console.print(f"[green]✓[/green] {ticker}: Holdings downloaded ({len(holdings)} positions)")
                                else:
                                    result['errors'].append("No holdings data in API response")
                    else:
                        result['errors'].append("Could not find API URL in page")
        except Exception as e:
            result['errors'].append(f"Holdings download error: {str(e)[:50]}")
        
        # Update stats
        if result['pdf_verified'] or result['csv_downloaded']:
            self.download_stats['success'] += 1
        else:
            self.download_stats['failed'] += 1
        
        return result
    
    async def download_all(self, max_etfs: Optional[int] = None, dry_run: bool = False):
        """Download all VanEck ETFs with comprehensive reporting."""
        etfs = await self.fetch_all_etfs()
        
        if max_etfs:
            etfs = etfs[:max_etfs]
            console.print(f"[yellow]Limiting to first {max_etfs} ETFs[/yellow]")
        
        self.download_stats['total'] = len(etfs)
        
        # Display ETF table
        table = Table(title=f"VanEck ETFs to Process ({len(etfs)} total)")
        table.add_column("#", style="dim", width=4)
        table.add_column("Ticker", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Slug", style="yellow")
        
        for i, etf in enumerate(etfs[:20], 1):  # Show first 20
            table.add_row(
                str(i),
                etf.get('ticker', 'N/A'),
                etf.get('name', 'Unknown')[:35],
                etf.get('slug', 'N/A')[:25]
            )
        
        if len(etfs) > 20:
            table.add_row("...", "...", f"... and {len(etfs)-20} more ...", "...")
        
        console.print(table)
        
        if dry_run:
            console.print("\n[yellow]DRY RUN MODE - No files will be downloaded[/yellow]")
            return
        
        # Download with progress tracking
        console.print(f"\n[bold]Starting download of {len(etfs)} ETFs...[/bold]")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Establish session
            await session.get(self.base_url, headers=self.headers)
            
            # Create semaphore for concurrency
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def download_with_limit(etf, progress_task):
                async with semaphore:
                    await asyncio.sleep(0.5)  # Rate limiting
                    return await self.download_etf_data(etf, session, progress_task)
            
            # Progress tracking
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                main_task = progress.add_task(
                    f"[cyan]Downloading {len(etfs)} ETFs...", 
                    total=len(etfs)
                )
                
                # Process all ETFs
                tasks = []
                for etf in etfs:
                    task = download_with_limit(etf, main_task)
                    tasks.append(task)
                
                # Gather results
                for future in asyncio.as_completed(tasks):
                    result = await future
                    results.append(result)
                    progress.update(main_task, advance=1)
        
        # Save results
        results_file = self.download_dir / "download_report.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'stats': self.download_stats,
                'results': results
            }, f, indent=2)
        
        # Display summary
        self._display_summary(results)
    
    def _display_summary(self, results: List[Dict]):
        """Display comprehensive download summary."""
        console.print("\n")
        console.print(Panel.fit("[bold green]Download Complete![/bold green]"))
        
        # Statistics table
        stats_table = Table(title="Download Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow", justify="right")
        
        stats_table.add_row("Total ETFs", str(self.download_stats['total']))
        stats_table.add_row("Successful", str(self.download_stats['success']))
        stats_table.add_row("Failed", str(self.download_stats['failed']))
        stats_table.add_row("PDFs Verified", str(self.download_stats['pdf_verified']))
        stats_table.add_row("CSVs Downloaded", str(self.download_stats['csv_downloaded']))
        stats_table.add_row("Total Downloaded", f"{self.download_stats['bytes_downloaded']:,} bytes")
        stats_table.add_row("Average Size", f"{self.download_stats['bytes_downloaded']//max(1, self.download_stats['success']):,} bytes")
        
        console.print(stats_table)
        
        # Failed downloads
        failed = [r for r in results if not r['pdf_verified'] and not r['csv_downloaded']]
        if failed:
            console.print(f"\n[red]Failed downloads ({len(failed)}):[/red]")
            for f in failed[:10]:
                console.print(f"  - {f['ticker']}: {', '.join(f['errors'][:2])}")
        
        # Success summary
        console.print(f"\n[green]✅ Successfully downloaded and verified {self.download_stats['pdf_verified']} PDFs[/green]")
        console.print(f"[green]📊 Downloaded {self.download_stats['csv_downloaded']} holdings files[/green]")
        console.print(f"[cyan]📁 Files saved to: {self.download_dir.absolute()}[/cyan]")


async def main(download_dir: str = "download", max_etfs: Optional[int] = None, dry_run: bool = False):
    """Main entry point."""
    downloader = FullVanEckETFDownloader(download_dir=download_dir)
    await downloader.download_all(max_etfs=max_etfs, dry_run=dry_run)


if __name__ == "__main__":
    import sys
    
    # Parse command line args
    max_etfs = None
    dry_run = False
    download_dir = "download"
    
    for arg in sys.argv[1:]:
        if arg.startswith("--max-etfs="):
            max_etfs = int(arg.split("=")[1])
        elif arg == "--dry-run":
            dry_run = True
        elif arg.startswith("--download-dir="):
            download_dir = arg.split("=")[1]
        elif arg == "--all":
            max_etfs = None
    
    # Run
    asyncio.run(main(download_dir=download_dir, max_etfs=max_etfs, dry_run=dry_run))