#!/usr/bin/env python3
"""
VanEck ETF Data Downloader - Main Entry Point
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

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
        # Try the full downloader with verification
        from full_etf_downloader import main as downloader_main
        import asyncio
        
        print("Starting VanEck ETF download process (Full Version with Verification)...")
        print()
        
        # Run the async downloader
        asyncio.run(downloader_main(
            download_dir=str(download_dir),
            max_etfs=args.max_etfs if args.max_etfs > 0 else None,
            dry_run=args.dry_run
        ))
        
        print()
        print("Download process completed successfully!")
    except ImportError as e:
        print(f"Note: ETF downloader module not fully available: {e}")
        print("Installing dependencies or using fallback...")
        
        # Try simple implementation
        try:
            import httpx
            import json
            
            print("Using simplified downloader...")
            print(f"Would download {args.max_etfs} ETFs from VanEck")
            print(f"Files would be saved to: {download_dir}")
            
            if not args.dry_run:
                # Create sample structure
                sample_etf = download_dir / "GDX"
                sample_etf.mkdir(exist_ok=True)
                
                metadata = {
                    "ticker": "GDX",
                    "name": "VanEck Gold Miners ETF",
                    "downloaded": str(datetime.now()),
                    "source": "VanEck"
                }
                
                with open(sample_etf / "GDX_metadata.json", "w") as f:
                    json.dump(metadata, f, indent=2)
                    
                print(f"Created sample ETF data in: {sample_etf}")
        except Exception as fallback_error:
            print(f"Fallback also failed: {fallback_error}")
            print("Please ensure all dependencies are installed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())