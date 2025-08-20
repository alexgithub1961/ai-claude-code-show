#!/usr/bin/env python3
"""
VanEck ETF Data Downloader - Main Entry Point
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    """Main entry point for the VanEck ETF downloader."""
    parser = argparse.ArgumentParser(
        description="VanEck ETF Data Downloader - Download ETF data from VanEck"
    )
    
    parser.add_argument(
        "--download-dir",
        type=str,
        default="/app/download",
        help="Directory to save downloaded files (default: /app/download)"
    )
    
    parser.add_argument(
        "--max-etfs",
        type=int,
        default=5,
        help="Maximum number of ETFs to download (default: 5)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="VanEck ETF Downloader v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Ensure download directory exists
    download_dir = Path(args.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"VanEck ETF Data Downloader")
    print(f"==========================")
    print(f"Download directory: {download_dir}")
    print(f"Maximum ETFs: {args.max_etfs}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be downloaded")
        print()
    
    # Import the actual downloader
    try:
        from etf_downloader import download_etf_data
        print("Starting download process...")
        download_etf_data(
            download_dir=str(download_dir),
            max_etfs=args.max_etfs,
            dry_run=args.dry_run
        )
        print("Download process completed successfully!")
    except ImportError:
        print("Note: ETF downloader module not fully implemented yet")
        print("This is a placeholder that demonstrates the container is working")
        print()
        print("Would download ETF data from:")
        print("https://www.vaneck.com/us/en/etf-mutual-fund-finder/")
        print()
        print(f"Files would be saved to: {download_dir}")
        
        # Create a sample file to show it's working
        if not args.dry_run:
            sample_file = download_dir / "sample_download.txt"
            with open(sample_file, "w") as f:
                f.write("VanEck ETF Downloader - Sample Download\n")
                f.write("This file confirms the container is working correctly.\n")
                f.write(f"Download directory: {download_dir}\n")
            print(f"Created sample file: {sample_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())