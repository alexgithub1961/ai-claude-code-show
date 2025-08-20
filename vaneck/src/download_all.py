#!/usr/bin/env python3
"""
Download all VanEck ETFs with smart search to timestamped folder
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from full_etf_downloader import FullVanEckETFDownloader

async def download_all_etfs():
    """Download all VanEck ETFs to timestamped folder."""
    
    # Create timestamped folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_dir = f"downloads/download_{timestamp}"
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"Downloading ALL VanEck ETFs to: {download_dir}")
    print(f"{'='*70}\n")
    
    # Create downloader with smart search enabled
    downloader = FullVanEckETFDownloader(download_dir=download_dir, max_concurrent=3)
    
    # Run the download
    await downloader.download_all(max_etfs=None, dry_run=False)
    
    print(f"\n✅ Download complete! Files saved to: {download_dir}")
    
    return download_dir

if __name__ == "__main__":
    download_folder = asyncio.run(download_all_etfs())
    print(f"\nAll ETFs downloaded to: {download_folder}")
    
    # Show summary
    from pathlib import Path
    download_path = Path(download_folder)
    etf_folders = list(download_path.iterdir())
    
    print(f"\nSummary:")
    print(f"- Total ETF folders: {len(etf_folders)}")
    
    pdf_count = sum(1 for etf in etf_folders for f in etf.glob("*.pdf"))
    json_count = sum(1 for etf in etf_folders for f in etf.glob("*holdings.json"))
    csv_count = sum(1 for etf in etf_folders for f in etf.glob("*holdings.csv"))
    
    print(f"- PDF fact sheets: {pdf_count}")
    print(f"- Holdings JSON files: {json_count}")
    print(f"- Holdings CSV files: {csv_count}")
    
    # Calculate total size
    total_size = sum(f.stat().st_size for etf in etf_folders for f in etf.iterdir() if f.is_file())
    print(f"- Total size: {total_size / (1024*1024):.2f} MB")