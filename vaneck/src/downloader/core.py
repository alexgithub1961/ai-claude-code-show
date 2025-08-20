"""
ETF Downloader Core Module

This module contains the main ETFDownloader class and supporting components
for downloading ETF data from multiple sources with rate limiting, caching,
and error handling.

Classes:
    ETFDownloader: Main downloader class
    DownloadSession: Manages individual download sessions
    RateLimiter: Enforces API rate limits

Example:
    Basic usage:
        >>> config = Config.load('config.yaml')
        >>> downloader = ETFDownloader(config)
        >>> data = await downloader.download_etfs(['VTI', 'VOO'])

Author: VanEck Data Team
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from decimal import Decimal

import httpx
from httpx import AsyncClient

from .adapters import AdapterFactory, BaseAdapter
from .cache import ResponseCache
from ..processors.validator import DataValidator
from ..processors.normaliser import DataNormaliser
from ..processors.enricher import DataEnricher
from ..storage.backends import StorageFactory
from ..utils.config import Config
from ..utils.exceptions import (
    ETFDownloaderError,
    DataSourceError,
    ValidationError,
    RateLimitError
)


@dataclass
class ETFData:
    """
    Represents ETF data for a specific symbol and date.
    
    This class encapsulates all relevant ETF information including
    price data, volume, and optional dividend/split information.
    
    Attributes:
        symbol: ETF ticker symbol (e.g., 'VTI')
        date: Trading date
        open_price: Opening price for the day
        high_price: Highest price during the day
        low_price: Lowest price during the day
        close_price: Closing price for the day
        volume: Number of shares traded
        adjusted_close: Split and dividend adjusted closing price
        dividend_amount: Dividend paid per share (if any)
        split_coefficient: Stock split ratio (if any)
    
    Example:
        >>> etf_data = ETFData(
        ...     symbol='VTI',
        ...     date=datetime(2024, 1, 15),
        ...     open_price=Decimal('245.50'),
        ...     high_price=Decimal('247.20'),
        ...     low_price=Decimal('244.80'),
        ...     close_price=Decimal('246.75'),
        ...     volume=1500000
        ... )
        >>> print(f"VTI closed at ${etf_data.close_price}")
        VTI closed at $246.75
    """
    symbol: str
    date: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    adjusted_close: Optional[Decimal] = None
    dividend_amount: Optional[Decimal] = None
    split_coefficient: Optional[Decimal] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ETFData to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all ETF data fields
        """
        return {
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'open_price': str(self.open_price),
            'high_price': str(self.high_price),
            'low_price': str(self.low_price),
            'close_price': str(self.close_price),
            'volume': self.volume,
            'adjusted_close': str(self.adjusted_close) if self.adjusted_close else None,
            'dividend_amount': str(self.dividend_amount) if self.dividend_amount else None,
            'split_coefficient': str(self.split_coefficient) if self.split_coefficient else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ETFData':
        """
        Create ETFData instance from dictionary.
        
        Args:
            data: Dictionary containing ETF data fields
            
        Returns:
            ETFData: New instance created from dictionary data
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            return cls(
                symbol=data['symbol'],
                date=datetime.fromisoformat(data['date']),
                open_price=Decimal(data['open_price']),
                high_price=Decimal(data['high_price']),
                low_price=Decimal(data['low_price']),
                close_price=Decimal(data['close_price']),
                volume=int(data['volume']),
                adjusted_close=Decimal(data['adjusted_close']) if data.get('adjusted_close') else None,
                dividend_amount=Decimal(data['dividend_amount']) if data.get('dividend_amount') else None,
                split_coefficient=Decimal(data['split_coefficient']) if data.get('split_coefficient') else None,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid ETF data format: {e}") from e


class RateLimiter:
    """
    Implements rate limiting for API requests.
    
    This class ensures that API calls don't exceed the configured rate limits
    for each data source, preventing API quotas from being exceeded.
    
    Attributes:
        calls_per_minute: Maximum number of API calls allowed per minute
        calls_made: Number of calls made in the current time window
        window_start: Start time of the current rate limiting window
    
    Example:
        >>> limiter = RateLimiter(calls_per_minute=60)
        >>> await limiter.acquire()  # Waits if rate limit would be exceeded
        >>> # Make API call here
    """
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum number of calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.calls_made = 0
        self.window_start = datetime.now()
        self._lock = asyncio.Lock()
        
    async def acquire(self) -> None:
        """
        Acquire permission to make an API call.
        
        This method will block if making a call would exceed the rate limit,
        waiting until it's safe to proceed.
        
        Example:
            >>> limiter = RateLimiter(calls_per_minute=60)
            >>> await limiter.acquire()
            >>> # Safe to make API call now
        """
        async with self._lock:
            now = datetime.now()
            
            # Reset counter if we've moved to a new minute
            if now - self.window_start >= timedelta(minutes=1):
                self.calls_made = 0
                self.window_start = now
            
            # Check if we need to wait
            if self.calls_made >= self.calls_per_minute:
                # Calculate wait time until next window
                next_window = self.window_start + timedelta(minutes=1)
                wait_seconds = (next_window - now).total_seconds()
                
                if wait_seconds > 0:
                    logging.info(f"Rate limit reached, waiting {wait_seconds:.1f} seconds")
                    await asyncio.sleep(wait_seconds)
                    
                    # Reset for new window
                    self.calls_made = 0
                    self.window_start = datetime.now()
            
            self.calls_made += 1


class DownloadSession:
    """
    Manages a download session for multiple ETF symbols.
    
    This class coordinates the download of multiple ETF symbols,
    handling failures, retries, and progress tracking.
    
    Attributes:
        symbols: List of ETF symbols to download
        adapter: Data source adapter to use
        results: Dictionary storing download results
        errors: Dictionary storing any errors encountered
    """
    
    def __init__(self, symbols: List[str], adapter: BaseAdapter):
        """
        Initialize download session.
        
        Args:
            symbols: List of ETF symbols to download
            adapter: Data source adapter to use for downloads
        """
        self.symbols = symbols
        self.adapter = adapter
        self.results: Dict[str, Optional[ETFData]] = {}
        self.errors: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)
    
    async def download_all(self, max_concurrent: int = 5) -> Dict[str, Optional[ETFData]]:
        """
        Download data for all symbols in the session.
        
        Args:
            max_concurrent: Maximum number of concurrent downloads
            
        Returns:
            Dict[str, Optional[ETFData]]: Results for each symbol, None if failed
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_single(symbol: str) -> None:
            async with semaphore:
                try:
                    self.logger.info(f"Downloading data for {symbol}")
                    data = await self.adapter.fetch_etf_data(symbol)
                    self.results[symbol] = data
                    self.logger.debug(f"Successfully downloaded {symbol}")
                except Exception as e:
                    self.logger.error(f"Failed to download {symbol}: {e}")
                    self.results[symbol] = None
                    self.errors[symbol] = str(e)
        
        # Create tasks for all symbols
        tasks = [download_single(symbol) for symbol in self.symbols]
        
        # Execute all downloads concurrently
        await asyncio.gather(*tasks)
        
        return self.results


class ETFDownloader:
    """
    Main ETF downloader class.
    
    This class orchestrates the entire ETF download process, including:
    - Configuration management
    - Data source coordination
    - Rate limiting
    - Data processing
    - Storage operations
    
    Attributes:
        config: Application configuration
        client: HTTP client for API requests
        cache: Response cache for reducing API calls
        rate_limiter: Rate limiter for API requests
        validator: Data validator
        normaliser: Data normaliser
        enricher: Data enricher
        storage: Storage backend
    
    Example:
        >>> config = Config.load('config.yaml')
        >>> downloader = ETFDownloader(config)
        >>> results = await downloader.download_etfs(['VTI', 'VOO', 'SPY'])
        >>> print(f"Downloaded {len(results)} ETFs")
    """
    
    def __init__(self, config: Config):
        """
        Initialize ETF downloader.
        
        Args:
            config: Application configuration object
            
        Raises:
            ETFDownloaderError: If configuration is invalid
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize HTTP client
        self.client = AsyncClient(
            timeout=httpx.Timeout(config.network.timeout),
            limits=httpx.Limits(max_connections=config.network.max_connections)
        )
        
        # Initialize components
        self.cache = ResponseCache(ttl_seconds=config.cache.ttl)
        self.rate_limiter = RateLimiter(calls_per_minute=config.rate_limiting.calls_per_minute)
        
        # Initialize processing pipeline
        self.validator = DataValidator(config.validation)
        self.normaliser = DataNormaliser(config.normalisation)
        self.enricher = DataEnricher(config.enrichment)
        
        # Initialize storage backend
        self.storage = StorageFactory.create_backend(
            backend_type=config.output.format,
            output_dir=config.output.directory,
            compression=config.output.compression
        )
        
        self.logger.info("ETF Downloader initialized successfully")
    
    async def download_etf(self, symbol: str, adapter_name: Optional[str] = None) -> Optional[ETFData]:
        """
        Download data for a single ETF symbol.
        
        Args:
            symbol: ETF ticker symbol to download
            adapter_name: Specific adapter to use (optional)
            
        Returns:
            Optional[ETFData]: ETF data if successful, None if failed
            
        Raises:
            DataSourceError: If all data sources fail
            ValidationError: If downloaded data is invalid
        """
        # Create adapter
        if adapter_name:
            adapter = AdapterFactory.create_adapter(adapter_name, self.config, self.client)
        else:
            # Use primary adapter from config
            adapter = AdapterFactory.create_adapter(
                self.config.data_sources[0].type,
                self.config,
                self.client
            )
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Check cache first
            cached_data = await self.cache.get(f"etf_{symbol}")
            if cached_data:
                self.logger.debug(f"Using cached data for {symbol}")
                return ETFData.from_dict(cached_data)
            
            # Download fresh data
            raw_data = await adapter.fetch_etf_data(symbol)
            
            if raw_data is None:
                self.logger.warning(f"No data returned for {symbol}")
                return None
            
            # Process data through pipeline
            processed_data = await self._process_data(raw_data)
            
            # Cache the processed data
            await self.cache.set(f"etf_{symbol}", processed_data.to_dict())
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Failed to download {symbol}: {e}")
            raise DataSourceError(f"Failed to download {symbol}: {e}") from e
    
    async def download_etfs(self, symbols: List[str]) -> Dict[str, Optional[ETFData]]:
        """
        Download data for multiple ETF symbols.
        
        Args:
            symbols: List of ETF ticker symbols to download
            
        Returns:
            Dict[str, Optional[ETFData]]: Results for each symbol
            
        Example:
            >>> results = await downloader.download_etfs(['VTI', 'VOO', 'SPY'])
            >>> successful = [k for k, v in results.items() if v is not None]
            >>> print(f"Successfully downloaded: {successful}")
        """
        self.logger.info(f"Starting download for {len(symbols)} symbols")
        
        # Create adapter for the session
        primary_source = self.config.data_sources[0]
        adapter = AdapterFactory.create_adapter(
            primary_source.type,
            self.config,
            self.client
        )
        
        # Create download session
        session = DownloadSession(symbols, adapter)
        
        # Download all symbols
        results = await session.download_all(
            max_concurrent=self.config.concurrency.max_concurrent_downloads
        )
        
        # Process successful downloads
        processed_results = {}
        for symbol, raw_data in results.items():
            if raw_data is not None:
                try:
                    processed_data = await self._process_data(raw_data)
                    processed_results[symbol] = processed_data
                except Exception as e:
                    self.logger.error(f"Failed to process {symbol}: {e}")
                    processed_results[symbol] = None
            else:
                processed_results[symbol] = None
        
        # Save results if configured
        if self.config.output.auto_save:
            await self.save_data(processed_results)
        
        return processed_results
    
    async def _process_data(self, data: ETFData) -> ETFData:
        """
        Process raw ETF data through the validation and enrichment pipeline.
        
        Args:
            data: Raw ETF data from data source
            
        Returns:
            ETFData: Processed and validated data
            
        Raises:
            ValidationError: If data fails validation
        """
        # Validate data
        is_valid, validation_errors = self.validator.validate(data)
        if not is_valid:
            raise ValidationError(f"Data validation failed: {validation_errors}")
        
        # Normalise data format
        normalised_data = self.normaliser.normalise(data)
        
        # Enrich with additional fields
        enriched_data = self.enricher.enrich(normalised_data)
        
        return enriched_data
    
    async def save_data(self, data: Dict[str, Optional[ETFData]], filename: Optional[str] = None) -> str:
        """
        Save ETF data using the configured storage backend.
        
        Args:
            data: Dictionary of ETF data to save
            filename: Optional custom filename
            
        Returns:
            str: Path to saved file
            
        Raises:
            StorageError: If saving fails
        """
        # Filter out None values
        valid_data = {k: v for k, v in data.items() if v is not None}
        
        if not valid_data:
            raise ValueError("No valid data to save")
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            symbols_str = "_".join(sorted(valid_data.keys())[:5])  # Limit length
            if len(valid_data) > 5:
                symbols_str += "_and_more"
            filename = f"etf_data_{symbols_str}_{timestamp}"
        
        # Save using storage backend
        saved_path = await self.storage.save(valid_data, filename)
        
        self.logger.info(f"Saved {len(valid_data)} ETF records to {saved_path}")
        
        return saved_path
    
    async def close(self) -> None:
        """
        Clean up resources and close connections.
        
        This method should be called when the downloader is no longer needed
        to ensure proper cleanup of HTTP connections and other resources.
        
        Example:
            >>> downloader = ETFDownloader(config)
            >>> try:
            ...     # Use downloader
            ...     pass
            ... finally:
            ...     await downloader.close()
        """
        await self.client.aclose()
        await self.cache.close()
        self.logger.info("ETF Downloader closed successfully")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()