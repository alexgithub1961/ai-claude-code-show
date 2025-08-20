"""Storage management for ETF data files."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import hashlib
from datetime import datetime, timezone

from .config import Config
from .scraper import ETFData

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages file storage and organisation for ETF data."""
    
    def __init__(self, config: Config):
        """Initialise storage manager with configuration."""
        self.config = config
        self.base_path = config.download_dir
        self._ensure_base_directory()
        
    def _ensure_base_directory(self) -> None:
        """Ensure base download directory exists."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using download directory: {self.base_path}")
        
    def get_etf_directory(self, ticker: str) -> Path:
        """Get directory path for an ETF."""
        etf_dir = self.base_path / ticker.upper()
        etf_dir.mkdir(parents=True, exist_ok=True)
        return etf_dir
        
    def get_file_path(self, ticker: str, file_type: str, url: str) -> Path:
        """Get local file path for a download."""
        etf_dir = self.get_etf_directory(ticker)
        
        # Create subdirectory by file type
        type_dir = etf_dir / file_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        
        # If no filename in URL, generate one
        if not filename or '.' not in filename:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            extension = self._guess_extension_from_url(url)
            filename = f"{file_type}_{url_hash}{extension}"
            
        # Sanitise filename
        filename = self._sanitise_filename(filename)
        
        return type_dir / filename
        
    def _guess_extension_from_url(self, url: str) -> str:
        """Guess file extension from URL."""
        url_lower = url.lower()
        for ext in self.config.download_extensions:
            if ext in url_lower:
                return ext
        return '.pdf'  # Default to PDF
        
    def _sanitise_filename(self, filename: str) -> str:
        """Sanitise filename for filesystem compatibility."""
        # Replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Limit length
        if len(filename) > 200:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:200-len(ext)-1] + (f'.{ext}' if ext else '')
            
        return filename
        
    def save_etf_metadata(self, etf: ETFData) -> Path:
        """Save ETF metadata to JSON file."""
        etf_dir = self.get_etf_directory(etf.ticker)
        metadata_file = etf_dir / 'metadata.json'
        
        metadata = {
            'ticker': etf.ticker,
            'name': etf.name,
            'fund_url': etf.fund_url,
            'fact_sheet_url': etf.fact_sheet_url,
            'holdings_url': etf.holdings_url,
            'prospectus_url': etf.prospectus_url,
            'annual_report_url': etf.annual_report_url,
            'data_files': etf.data_files,
            'last_updated': datetime.now(timezone.utc).isoformat(),
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        logger.debug(f"Saved metadata for {etf.ticker} to {metadata_file}")
        return metadata_file
        
    def load_etf_metadata(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Load ETF metadata from JSON file."""
        etf_dir = self.get_etf_directory(ticker)
        metadata_file = etf_dir / 'metadata.json'
        
        if not metadata_file.exists():
            return None
            
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading metadata for {ticker}: {e}")
            return None
            
    def get_downloaded_files(self, ticker: str) -> List[Path]:
        """Get list of downloaded files for an ETF."""
        etf_dir = self.get_etf_directory(ticker)
        
        if not etf_dir.exists():
            return []
            
        files = []
        for file_path in etf_dir.rglob('*'):
            if file_path.is_file() and file_path.name != 'metadata.json':
                files.append(file_path)
                
        return files
        
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            'total_etfs': 0,
            'total_files': 0,
            'total_size_bytes': 0,
            'etf_stats': {},
        }
        
        if not self.base_path.exists():
            return stats
            
        for etf_dir in self.base_path.iterdir():
            if etf_dir.is_dir():
                ticker = etf_dir.name
                stats['total_etfs'] += 1
                
                files = self.get_downloaded_files(ticker)
                file_count = len(files)
                total_size = sum(f.stat().st_size for f in files if f.exists())
                
                stats['total_files'] += file_count
                stats['total_size_bytes'] += total_size
                
                stats['etf_stats'][ticker] = {
                    'file_count': file_count,
                    'size_bytes': total_size,
                    'has_metadata': (etf_dir / 'metadata.json').exists(),
                }
                
        return stats
        
    def cleanup_empty_directories(self) -> int:
        """Remove empty directories and return count removed."""
        removed_count = 0
        
        if not self.base_path.exists():
            return removed_count
            
        # Remove empty subdirectories first
        for etf_dir in self.base_path.iterdir():
            if etf_dir.is_dir():
                for sub_dir in etf_dir.iterdir():
                    if sub_dir.is_dir() and not any(sub_dir.iterdir()):
                        try:
                            sub_dir.rmdir()
                            removed_count += 1
                            logger.debug(f"Removed empty directory: {sub_dir}")
                        except OSError as e:
                            logger.warning(f"Could not remove directory {sub_dir}: {e}")
                            
                # Remove empty ETF directories
                if not any(etf_dir.iterdir()):
                    try:
                        etf_dir.rmdir()
                        removed_count += 1
                        logger.debug(f"Removed empty ETF directory: {etf_dir}")
                    except OSError as e:
                        logger.warning(f"Could not remove ETF directory {etf_dir}: {e}")
                        
        return removed_count
        
    def create_download_summary(self, download_results: List) -> Path:
        """Create a summary file of download results."""
        summary_file = self.base_path / 'download_summary.json'
        
        summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_downloads': len(download_results),
            'successful_downloads': sum(1 for r in download_results if r.success),
            'failed_downloads': sum(1 for r in download_results if not r.success),
            'total_bytes': sum(r.size_bytes or 0 for r in download_results if r.success),
            'details': []
        }
        
        for result in download_results:
            detail = {
                'url': result.url,
                'local_path': str(result.local_path),
                'success': result.success,
                'size_bytes': result.size_bytes,
                'duration_seconds': result.duration_seconds,
                'resumed': getattr(result, 'resumed', False),
                'error': result.error if not result.success else None,
            }
            summary['details'].append(detail)
            
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Created download summary: {summary_file}")
        return summary_file
        
    def verify_file_integrity(self, file_path: Path) -> bool:
        """Verify file integrity (basic check for now)."""
        if not file_path.exists():
            return False
            
        try:
            # Basic check - file exists and has content
            stat = file_path.stat()
            return stat.st_size > 0
        except Exception as e:
            logger.warning(f"Error verifying file {file_path}: {e}")
            return False