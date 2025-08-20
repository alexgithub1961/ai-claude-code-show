#!/usr/bin/env python3
"""
Fix VanEck ETF Holdings Downloader
Extracts actual API URLs from HTML files and downloads real holdings data
"""

import json
import re
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich import print as rprint
import csv

console = Console()

class HoldingsFixDownloader:
    def __init__(self, download_dir: str = "download_all"):
        self.download_dir = Path(download_dir)
        self.session: Optional[aiohttp.ClientSession] = None
        self.stats = {
            "total": 0,
            "processed": 0,
            "fixed": 0,
            "failed": 0,
            "errors": []
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.vaneck.com/'
            }
        )
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            
    def extract_api_url(self, html_file: Path) -> Optional[str]:
        """Extract the API URL from the HTML file containing JSON-LD metadata"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for the contentUrl in the JSON-LD Dataset schema
            pattern = r'"contentUrl"\s*:\s*"([^"]+GetDataset[^"]+)"'
            match = re.search(pattern, content)
            
            if match:
                return match.group(1)
                
            console.print(f"[yellow]No API URL found in {html_file.name}[/yellow]")
            return None
            
        except Exception as e:
            console.print(f"[red]Error extracting URL from {html_file}: {e}[/red]")
            return None
            
    async def download_holdings_json(self, ticker: str, api_url: str) -> Optional[Dict]:
        """Download the actual holdings data from the API"""
        try:
            async with self.session.get(api_url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    console.print(f"[red]Failed to download {ticker}: HTTP {response.status}[/red]")
                    return None
                    
        except Exception as e:
            console.print(f"[red]Error downloading {ticker}: {e}[/red]")
            self.stats["errors"].append(f"{ticker}: {str(e)}")
            return None
            
    def save_holdings_json(self, ticker: str, data: Dict, etf_dir: Path) -> bool:
        """Save holdings data as JSON"""
        try:
            json_file = etf_dir / f"{ticker}_holdings.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            console.print(f"[red]Error saving JSON for {ticker}: {e}[/red]")
            return False
            
    def save_holdings_csv(self, ticker: str, data: Dict, etf_dir: Path) -> bool:
        """Convert holdings JSON to CSV format"""
        try:
            csv_file = etf_dir / f"{ticker}_holdings_real.csv"
            
            if 'holdings' not in data or not data['holdings']:
                console.print(f"[yellow]No holdings data for {ticker}[/yellow]")
                return False
                
            holdings = data['holdings']
            
            # Get all unique keys from holdings
            all_keys = set()
            for holding in holdings:
                all_keys.update(holding.keys())
            
            # Write CSV
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(holdings)
                
            # Remove the old HTML file that was saved as .csv
            old_csv = etf_dir / f"{ticker}_holdings.csv"
            if old_csv.exists():
                old_csv.rename(etf_dir / f"{ticker}_holdings_old.html")
                
            return True
            
        except Exception as e:
            console.print(f"[red]Error saving CSV for {ticker}: {e}[/red]")
            return False
            
    async def process_etf(self, etf_dir: Path, progress: Progress, task: TaskID) -> bool:
        """Process a single ETF directory"""
        ticker = etf_dir.name
        holdings_file = etf_dir / f"{ticker}_holdings.csv"
        
        # Check if the CSV file exists and is actually HTML
        if not holdings_file.exists():
            return False
            
        # Check if it's already been fixed
        if (etf_dir / f"{ticker}_holdings.json").exists():
            console.print(f"[green]✓ {ticker} already fixed[/green]")
            return True
            
        # Extract API URL
        api_url = self.extract_api_url(holdings_file)
        if not api_url:
            self.stats["failed"] += 1
            return False
            
        # Download real data
        progress.update(task, description=f"Downloading {ticker} holdings...")
        data = await self.download_holdings_json(ticker, api_url)
        
        if data:
            # Save as JSON
            json_saved = self.save_holdings_json(ticker, data, etf_dir)
            
            # Save as CSV
            csv_saved = self.save_holdings_csv(ticker, data, etf_dir)
            
            if json_saved and csv_saved:
                self.stats["fixed"] += 1
                console.print(f"[green]✓ Fixed {ticker} holdings[/green]")
                return True
                
        self.stats["failed"] += 1
        return False
        
    async def fix_all_holdings(self):
        """Process all ETF directories and fix holdings files"""
        etf_dirs = sorted([d for d in self.download_dir.iterdir() if d.is_dir()])
        self.stats["total"] = len(etf_dirs)
        
        console.print(f"\n[bold cyan]Found {len(etf_dirs)} ETFs to process[/bold cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task(
                "[cyan]Fixing holdings files...", 
                total=len(etf_dirs)
            )
            
            # Process ETFs in batches
            batch_size = 5
            for i in range(0, len(etf_dirs), batch_size):
                batch = etf_dirs[i:i+batch_size]
                tasks = [self.process_etf(etf_dir, progress, main_task) for etf_dir in batch]
                await asyncio.gather(*tasks)
                
                self.stats["processed"] += len(batch)
                progress.update(main_task, completed=self.stats["processed"])
                
        # Display results
        self.display_results()
        
    def display_results(self):
        """Display summary of the fix operation"""
        table = Table(title="Holdings Fix Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total ETFs", str(self.stats["total"]))
        table.add_row("Successfully Fixed", str(self.stats["fixed"]))
        table.add_row("Failed", str(self.stats["failed"]))
        
        console.print("\n")
        console.print(table)
        
        if self.stats["errors"]:
            console.print("\n[red]Errors encountered:[/red]")
            for error in self.stats["errors"][:10]:  # Show first 10 errors
                console.print(f"  • {error}")
                
        # Save report
        report_file = self.download_dir / "holdings_fix_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "stats": self.stats,
                "errors": self.stats["errors"]
            }, f, indent=2)
            
        console.print(f"\n[green]Report saved to: {report_file}[/green]")

async def main():
    """Main entry point"""
    console.print("[bold cyan]VanEck ETF Holdings Fix Tool[/bold cyan]")
    console.print("This tool will extract API URLs from HTML files and download real holdings data\n")
    
    async with HoldingsFixDownloader() as downloader:
        await downloader.fix_all_holdings()

if __name__ == "__main__":
    asyncio.run(main())