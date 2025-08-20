"""File download functionality with resumable downloads and error handling."""

import asyncio
import hashlib
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles
import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import Config
from .scraper import ETFFund
from .storage import DownloadRecord, StorageManager

logger = logging.getLogger(__name__)


class DownloadStats:
    """Track download statistics."""
    
    def __init__(self):
        self.total_files = 0
        self.downloaded_files = 0
        self.skipped_files = 0
        self.failed_files = 0
        self.total_bytes = 0
        self.start_time = time.time()
        self.errors: List[str] = []
        
    def add_success(self, file_size: int) -> None:
        """Record a successful download."""
        self.downloaded_files += 1
        self.total_bytes += file_size
        
    def add_skip(self) -> None:
        """Record a skipped download."""
        self.skipped_files += 1
        
    def add_failure(self, error: str) -> None:
        """Record a failed download."""
        self.failed_files += 1
        self.errors.append(error)
        
    def get_summary(self) -> Dict:
        """Get download summary."""
        elapsed_time = time.time() - self.start_time
        
        return {
            "total_files": self.total_files,
            "downloaded": self.downloaded_files,
            "skipped": self.skipped_files,
            "failed": self.failed_files,
            "total_bytes": self.total_bytes,
            "total_mb": round(self.total_bytes / (1024 * 1024), 2),
            "elapsed_seconds": round(elapsed_time, 2),
            "download_rate_mbps": round(
                (self.total_bytes / (1024 * 1024)) / max(elapsed_time, 1), 2
            ),
            "success_rate": round(
                self.downloaded_files / max(self.total_files, 1) * 100, 1
            ),
            "errors": self.errors[-10],  # Last 10 errors
        }


class ETFDownloader:
    """Downloads ETF documents with resumable capability."""
    
    def __init__(self, config: Config, storage_manager: StorageManager):
        self.config = config
        self.storage = storage_manager
        self.stats = DownloadStats()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent,
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _get_file_info(self, url: str) -> Tuple[Optional[int], bool]:
        """Get file size and check if server supports range requests."""
        try:
            response = self.session.head(
                url, 
                timeout=self.config.request_timeout,
                allow_redirects=True
            )
            
            if response.status_code == 405:  # Method not allowed, try GET
                response = self.session.get(
                    url,
                    timeout=self.config.request_timeout,
                    stream=True,
                    allow_redirects=True
                )
                # Close immediately to avoid downloading
                response.close()
            
            response.raise_for_status()
            
            # Get content length
            content_length = response.headers.get('Content-Length')
            file_size = int(content_length) if content_length else None
            
            # Check if server supports range requests
            supports_range = response.headers.get('Accept-Ranges') == 'bytes'
            
            return file_size, supports_range
            
        except Exception as e:
            logger.warning(f"Failed to get file info for {url}: {e}")
            return None, False

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
            return ""

    def download_file_sync(
        self, 
        url: str, 
        local_path: Path, 
        fund_symbol: str,
        document_type: Optional[str] = None
    ) -> bool:
        """Download a single file with resume capability (synchronous)."""
        logger.debug(f"Downloading {url} -> {local_path}")
        
        try:
            # Check if file already exists and is complete
            if (self.storage.is_file_downloaded(url, fund_symbol, document_type) and 
                local_path.exists() and local_path.stat().st_size > 0):
                logger.debug(f"File already exists: {local_path}")
                self.stats.add_skip()
                return True
            
            # Get file information
            expected_size, supports_range = self._get_file_info(url)
            
            # Check for partial download
            existing_size = 0
            headers = {}
            
            if (self.config.enable_resume and 
                local_path.exists() and 
                supports_range and 
                expected_size):
                
                existing_size = local_path.stat().st_size
                
                if existing_size < expected_size:
                    headers['Range'] = f'bytes={existing_size}-'
                    logger.debug(f"Resuming download from byte {existing_size}")
                elif existing_size >= expected_size:
                    logger.debug(f"File appears complete: {local_path}")
                    self.stats.add_skip()
                    return True
            
            # Make the download request
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.config.request_timeout,
                stream=True,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            mode = 'ab' if existing_size > 0 else 'wb'
            downloaded_bytes = existing_size
            
            with open(local_path, mode) as f:
                for chunk in response.iter_content(chunk_size=self.config.chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
            
            # Verify download
            if expected_size and downloaded_bytes != expected_size:
                logger.warning(
                    f"Size mismatch for {url}: expected {expected_size}, "
                    f"got {downloaded_bytes}"
                )
            
            # Calculate checksum
            checksum = self._calculate_checksum(local_path)
            
            # Record the download
            record = DownloadRecord(
                url=url,
                local_path=str(local_path),
                file_size=downloaded_bytes,
                download_date=datetime.now().isoformat(),
                checksum=checksum,
                fund_symbol=fund_symbol,
                document_type=document_type,
            )
            
            self.storage.save_download_record(record)
            self.stats.add_success(downloaded_bytes - existing_size)
            
            logger.debug(f"Downloaded {url} ({downloaded_bytes} bytes)")
            return True
            
        except Exception as e:
            error_msg = f"Failed to download {url}: {e}"
            logger.error(error_msg)
            self.stats.add_failure(error_msg)
            
            # Clean up partial download if it's corrupted
            if local_path.exists() and local_path.stat().st_size == 0:
                try:
                    local_path.unlink()
                except Exception:
                    pass
                    
            return False

    async def download_file_async(
        self, 
        session: aiohttp.ClientSession,
        url: str, 
        local_path: Path, 
        fund_symbol: str,
        document_type: Optional[str] = None
    ) -> bool:
        """Download a single file asynchronously with resume capability."""
        logger.debug(f"Downloading async {url} -> {local_path}")
        
        try:
            # Check if file already exists
            if (self.storage.is_file_downloaded(url, fund_symbol, document_type) and 
                local_path.exists() and local_path.stat().st_size > 0):
                logger.debug(f"File already exists: {local_path}")
                self.stats.add_skip()
                return True
            
            # Check for partial download
            existing_size = 0
            headers = {}
            
            if self.config.enable_resume and local_path.exists():
                existing_size = local_path.stat().st_size
                headers['Range'] = f'bytes={existing_size}-'
                logger.debug(f"Resuming download from byte {existing_size}")
            
            # Make the request
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                
                # Ensure parent directory exists
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download the file
                mode = 'ab' if existing_size > 0 else 'wb'
                downloaded_bytes = existing_size
                
                async with aiofiles.open(local_path, mode) as f:
                    async for chunk in response.content.iter_chunked(self.config.chunk_size):
                        await f.write(chunk)
                        downloaded_bytes += len(chunk)
                
                # Calculate checksum
                checksum = self._calculate_checksum(local_path)
                
                # Record the download
                record = DownloadRecord(
                    url=url,
                    local_path=str(local_path),
                    file_size=downloaded_bytes,
                    download_date=datetime.now().isoformat(),
                    checksum=checksum,
                    fund_symbol=fund_symbol,
                    document_type=document_type,
                )
                
                self.storage.save_download_record(record)
                self.stats.add_success(downloaded_bytes - existing_size)
                
                logger.debug(f"Downloaded {url} ({downloaded_bytes} bytes)")
                return True
                
        except Exception as e:
            error_msg = f"Failed to download {url}: {e}"
            logger.error(error_msg)
            self.stats.add_failure(error_msg)
            
            # Clean up partial download if it's corrupted
            if local_path.exists() and local_path.stat().st_size == 0:
                try:
                    local_path.unlink()
                except Exception:
                    pass
                    
            return False

    def download_fund_documents(self, fund: ETFFund) -> bool:
        """Download all documents for a specific fund."""
        logger.info(f"Downloading documents for {fund.symbol}")
        
        success_count = 0
        total_count = len(fund.document_urls)
        
        if total_count == 0:
            logger.warning(f"No documents found for {fund.symbol}")
            return True
        
        # Download each document
        for url in fund.document_urls:
            # Determine document type
            document_type = None
            if url == fund.fact_sheet_url:
                document_type = "fact_sheet"
            elif url == fund.holdings_url:
                document_type = "holdings"
            elif url == fund.performance_url:
                document_type = "performance"
            
            local_path = self.storage.get_local_path(url, fund.symbol, document_type)
            
            if self.download_file_sync(url, local_path, fund.symbol, document_type):
                success_count += 1
                
            # Rate limiting
            time.sleep(self.config.rate_limit_delay)
        
        success_rate = success_count / total_count if total_count > 0 else 0
        logger.info(
            f"Downloaded {success_count}/{total_count} documents for {fund.symbol} "
            f"({success_rate:.1%})"
        )
        
        return success_rate > 0.5  # Consider successful if > 50% downloaded

    async def download_funds_async(self, funds: List[ETFFund]) -> None:
        """Download documents for multiple funds asynchronously."""
        logger.info(f"Starting async downloads for {len(funds)} funds")
        
        # Calculate total files
        self.stats.total_files = sum(len(fund.document_urls) for fund in funds)
        
        # Create aiohttp session
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_downloads)
        
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'User-Agent': self.config.user_agent}
        ) as session:
            
            # Create download tasks
            tasks = []
            
            for fund in funds:
                for url in fund.document_urls:
                    # Determine document type
                    document_type = None
                    if url == fund.fact_sheet_url:
                        document_type = "fact_sheet"
                    elif url == fund.holdings_url:
                        document_type = "holdings"
                    elif url == fund.performance_url:
                        document_type = "performance"
                    
                    local_path = self.storage.get_local_path(url, fund.symbol, document_type)
                    
                    task = self.download_file_async(
                        session, url, local_path, fund.symbol, document_type
                    )
                    tasks.append(task)
            
            # Execute downloads with concurrency limit
            semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
            
            async def download_with_semaphore(task):
                async with semaphore:
                    return await task
            
            # Run all downloads
            results = await asyncio.gather(
                *[download_with_semaphore(task) for task in tasks],
                return_exceptions=True
            )
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.stats.add_failure(str(result))
        
        logger.info("Completed async downloads")

    def download_all_funds(self, funds: List[ETFFund], use_async: bool = True) -> DownloadStats:
        """Download documents for all funds."""
        logger.info(f"Starting downloads for {len(funds)} funds (async={use_async})")
        
        self.stats.total_files = sum(len(fund.document_urls) for fund in funds)
        
        if use_async and self.stats.total_files > 10:
            # Use async for large downloads
            asyncio.run(self.download_funds_async(funds))
        else:
            # Use sync for small downloads or when async is disabled
            for fund in funds:
                self.download_fund_documents(fund)
        
        return self.stats