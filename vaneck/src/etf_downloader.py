#!/usr/bin/env python3
"""
VanEck ETF Data Downloader

A standalone script to download ETF data from VanEck with these features:
- Fetches ETF list from VanEck (handles JavaScript-rendered content if needed)
- Downloads data files (PDFs, CSVs, fact sheets) for each ETF
- Saves to download/ directory with proper folder structure
- Implements retry logic with exponential backoff
- Supports resumable downloads and skips already downloaded files
- Uses async/await for concurrent downloads
- Proper logging with timestamps

Usage:
    python src/etf_downloader.py [--max-etfs N] [--ticker TICKER] [--dry-run]
    
Environment Variables:
    VANECK_DOWNLOAD_DIR - Download directory (default: ./download)
    VANECK_MAX_CONCURRENT - Max concurrent downloads (default: 5)
    VANECK_LOG_LEVEL - Log level (default: INFO)
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the package to Python path so we can import from vaneck_downloader
sys.path.insert(0, str(Path(__file__).parent))

from vaneck_downloader.config import Config
from vaneck_downloader.scraper import VanEckScraper
from vaneck_downloader.downloader import ETFDownloader
from vaneck_downloader.storage import StorageManager


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def main():
    """Main function to download ETF data."""
    
    # Parse simple command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Download VanEck ETF data')
    parser.add_argument('--max-etfs', type=int, help='Maximum number of ETFs to process')
    parser.add_argument('--ticker', help='Download data for specific ETF ticker only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without downloading')
    parser.add_argument('--download-dir', help='Download directory override')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Load configuration from environment
    config = Config.from_env()
    
    # Override with command line arguments
    if args.download_dir:
        config.download_dir = Path(args.download_dir)
    if args.log_level:
        config.log_level = args.log_level
        
    logger.info("VanEck ETF Data Downloader Starting")
    logger.info(f"Download directory: {config.download_dir}")
    logger.info(f"Max concurrent downloads: {config.max_concurrent_downloads}")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be downloaded")
    
    try:
        # Initialize storage manager
        storage = StorageManager(config)
        
        # Scrape ETF list
        logger.info("Scraping ETF list from VanEck...")
        async with VanEckScraper(config) as scraper:
            etfs = await scraper.get_etf_list()
            
            if not etfs:
                logger.error("No ETFs found. Exiting.")
                return 1
                
            logger.info(f"Found {len(etfs)} ETFs")
            
            # Filter by ticker if specified
            if args.ticker:
                original_count = len(etfs)
                etfs = [etf for etf in etfs if etf.ticker.upper() == args.ticker.upper()]
                if not etfs:
                    logger.error(f"ETF with ticker '{args.ticker}' not found.")
                    return 1
                logger.info(f"Filtered from {original_count} to {len(etfs)} ETFs for ticker: {args.ticker}")
                
            # Limit ETFs if specified
            if args.max_etfs:
                original_count = len(etfs)
                etfs = etfs[:args.max_etfs]
                logger.info(f"Limited from {original_count} to {len(etfs)} ETFs")
                
            # Get document URLs for each ETF
            logger.info("Getting document URLs for each ETF...")
            enriched_etfs = []
            for i, etf in enumerate(etfs, 1):
                logger.info(f"Processing ETF {i}/{len(etfs)}: {etf.ticker}")
                enriched_etf = await scraper.get_etf_documents(etf)
                enriched_etfs.append(enriched_etf)
                
                # Save metadata
                storage.save_etf_metadata(enriched_etf)
                
            etfs = enriched_etfs
            
        # Show download plan
        total_files = 0
        for etf in etfs:
            doc_count = sum(1 for url in [
                etf.fact_sheet_url, etf.holdings_url,
                etf.prospectus_url, etf.annual_report_url
            ] if url)
            data_file_count = len(etf.data_files)
            total_files += doc_count + data_file_count
            
            logger.info(f"ETF {etf.ticker}: {doc_count} documents, {data_file_count} data files")
            
        logger.info(f"Total files to download: {total_files}")
        
        if args.dry_run:
            logger.info("Dry run complete. No files were downloaded.")
            return 0
            
        if total_files == 0:
            logger.warning("No files to download.")
            return 0
            
        # Download files
        logger.info("Starting downloads...")
        async with ETFDownloader(config, storage) as downloader:
            download_results = await downloader.download_etf_data(etfs)
            
        # Create summary
        storage.create_download_summary(download_results)
        removed_dirs = storage.cleanup_empty_directories()
        if removed_dirs > 0:
            logger.info(f"Cleaned up {removed_dirs} empty directories")
            
        # Show results
        successful = sum(1 for r in download_results if r.success)
        failed = sum(1 for r in download_results if not r.success)
        total_size = sum(r.size_bytes or 0 for r in download_results if r.success)
        
        logger.info("Download Complete!")
        logger.info(f"Successful downloads: {successful}")
        logger.info(f"Failed downloads: {failed}")
        logger.info(f"Total size: {_format_bytes(total_size)}")
        
        if failed > 0:
            logger.warning("Failed downloads:")
            for result in download_results:
                if not result.success:
                    logger.warning(f"  {result.url}: {result.error}")
                    
        return 0 if failed == 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Error during download: {e}")
        return 1


def _format_bytes(bytes_size: int) -> str:
    """Format bytes in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)