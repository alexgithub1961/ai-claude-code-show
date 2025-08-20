# Source Code Documentation

This directory contains the core source code for the VanEck ETF Data Downloader application.

## Module Overview

The application is organised into several key modules, each with specific responsibilities:

```
src/
├── main.py                 # Application entry point and CLI interface
├── downloader/            # Core downloading functionality
│   ├── __init__.py
│   ├── core.py           # Main ETFDownloader class
│   ├── adapters/         # Data source adapters
│   │   ├── __init__.py
│   │   ├── alpha_vantage.py
│   │   ├── iex_cloud.py
│   │   └── yahoo_finance.py
│   ├── auth.py           # Authentication handling
│   └── cache.py          # Request caching
├── processors/            # Data processing pipeline
│   ├── __init__.py
│   ├── validator.py      # Data validation
│   ├── normaliser.py     # Data normalisation
│   ├── enricher.py       # Data enrichment
│   └── cleaner.py        # Data cleaning
├── storage/              # Data storage backends
│   ├── __init__.py
│   ├── backends/         # Storage implementations
│   │   ├── __init__.py
│   │   ├── csv_storage.py
│   │   ├── json_storage.py
│   │   └── parquet_storage.py
│   ├── schemas.py        # Data schemas
│   └── compression.py    # Compression utilities
└── utils/                # Utility functions
    ├── __init__.py
    ├── config.py         # Configuration management
    ├── logging.py        # Logging setup
    ├── exceptions.py     # Custom exceptions
    └── decorators.py     # Common decorators
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Flow Diagram                            │
└─────────────────────────────────────────────────────────────────────────┘

    [CLI Interface]
           │
           ▼
    [Configuration]
           │
           ▼                     ┌─────────────────┐
    [ETF Downloader] ────────────│ Rate Limiter    │
           │                     └─────────────────┘
           ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ Alpha       │    │ IEX Cloud   │    │ Yahoo       │
    │ Vantage     │    │ Adapter     │    │ Finance     │
    │ Adapter     │    │             │    │ Adapter     │
    └─────────────┘    └─────────────┘    └─────────────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │
                                 ▼
                        [Raw Data Cache]
                                 │
                                 ▼
                      ┌─────────────────┐
                      │ Data Processing │
                      │ Pipeline        │
                      └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            [Validation]  [Normalisation] [Enrichment]
                    │            │            │
                    └────────────┼────────────┘
                                 │
                                 ▼
                        [Cleaned Dataset]
                                 │
                                 ▼
                      ┌─────────────────┐
                      │ Storage Backend │
                      │ Selection       │
                      └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
              [CSV Files]  [JSON Files] [Parquet Files]
                    │            │            │
                    └────────────┼────────────┘
                                 │
                                 ▼
                         [File System]
```

## Key Components

### 1. Main Entry Point (`main.py`)

The application entry point provides a command-line interface for the ETF downloader.

**Key Features:**
- Argument parsing and validation
- Configuration loading
- Logging setup
- Error handling and graceful shutdown
- Progress reporting

**Usage Patterns:**
```python
# Direct execution
python main.py --etfs VTI,VOO --output-format csv

# Programmatic usage
from src.main import main
main(['--config', 'custom_config.yaml'])
```

### 2. Downloader Module (`downloader/`)

#### Core Downloader (`core.py`)
The heart of the application that orchestrates data collection from multiple sources.

**Key Classes:**
- `ETFDownloader`: Main downloader class with rate limiting and error handling
- `DownloadSession`: Manages individual download sessions
- `RateLimiter`: Enforces API rate limits

**Key Methods:**
```python
async def download_etfs(etfs: List[str]) -> Dict[str, ETFData]
async def download_etf(symbol: str) -> ETFData
def save_data(data: Dict[str, ETFData], output_path: str) -> None
```

#### Data Source Adapters (`adapters/`)
Standardised interfaces for different financial data providers.

**Base Adapter Pattern:**
```python
class BaseAdapter:
    async def fetch_etf_data(self, symbol: str) -> ETFData
    async def fetch_historical_data(self, symbol: str, period: str) -> List[ETFData]
    def validate_response(self, response: dict) -> bool
```

**Supported Adapters:**
- **Alpha Vantage**: Professional-grade financial data
- **IEX Cloud**: Real-time market data
- **Yahoo Finance**: Fallback data source

### 3. Processing Pipeline (`processors/`)

#### Data Validator (`validator.py`)
Ensures data quality and consistency across all sources.

**Validation Rules:**
- Required field presence (symbol, date, price, volume)
- Data type validation
- Range checks (positive prices, valid dates)
- Consistency checks (chronological order)

#### Data Normaliser (`normaliser.py`)
Standardises data formats across different providers.

**Normalisation Tasks:**
- Date format standardisation (ISO 8601)
- Decimal precision alignment
- Currency code standardisation
- Field name mapping

#### Data Enricher (`enricher.py`)
Adds calculated fields and derived metrics.

**Enrichment Features:**
- Moving averages (SMA, EMA)
- Technical indicators (RSI, MACD)
- Volatility calculations
- Performance ratios

### 4. Storage Backends (`storage/`)

#### Storage Factory Pattern
Dynamic backend selection based on configuration.

```python
storage_backend = StorageFactory.create_backend(
    backend_type='csv',
    compression='gzip',
    output_dir='./data'
)
```

#### Supported Formats:
- **CSV**: Human-readable, Excel-compatible
- **JSON**: Structured data with metadata
- **Parquet**: Columnar format for analytics

### 5. Utilities (`utils/`)

#### Configuration Management (`config.py`)
Hierarchical configuration with environment variable support.

```python
config = Config.load(
    config_file='config.yaml',
    env_prefix='ETF_'
)
```

#### Logging System (`logging.py`)
Structured logging with multiple outputs and log rotation.

```python
logger = setup_logging(
    level='INFO',
    file_path='logs/etf_downloader.log',
    enable_console=True
)
```

## API Endpoints and Data Sources

### Primary Data Sources

#### Alpha Vantage API
- **Base URL**: `https://www.alphavantage.co/query`
- **Authentication**: API key required
- **Rate Limit**: 5 calls per minute (free tier)
- **Data Types**: Real-time quotes, historical data, fundamentals

**Example Request:**
```
GET /query?function=TIME_SERIES_DAILY&symbol=VTI&apikey=demo&outputsize=compact
```

#### IEX Cloud API
- **Base URL**: `https://cloud.iexapis.com/stable`
- **Authentication**: Token-based
- **Rate Limit**: 100 calls per second (paid tier)
- **Data Types**: Real-time data, historical prices, company info

**Example Request:**
```
GET /stock/VTI/quote?token=pk_test
```

#### Yahoo Finance (Unofficial)
- **Base URL**: `https://query1.finance.yahoo.com`
- **Authentication**: None required
- **Rate Limit**: Best effort (no official limits)
- **Data Types**: Historical data, real-time quotes

**Example Request:**
```
GET /v7/finance/download/VTI?period1=0&period2=9999999999&interval=1d
```

## Data Models and Schemas

### Core Data Structures

#### ETF Data Model
```python
@dataclass
class ETFData:
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
    
    def to_dict(self) -> Dict[str, Any]: ...
    def from_dict(cls, data: Dict[str, Any]) -> 'ETFData': ...
```

#### Configuration Schema
```yaml
data_sources:
  - name: string
    type: string  # alpha_vantage, iex_cloud, yahoo_finance
    api_key: string
    base_url: string
    rate_limit: integer
    timeout: integer
    retry_count: integer

processing:
  validation:
    strict_mode: boolean
    allow_missing_fields: list
  normalisation:
    date_format: string
    decimal_places: integer
  enrichment:
    calculate_indicators: boolean
    indicators: list

output:
  format: string  # csv, json, parquet
  compression: string  # none, gzip, bz2
  file_naming: string
  directory_structure: string
```

## Error Handling Strategy

### Exception Hierarchy
```python
class ETFDownloaderError(Exception):
    """Base exception for ETF downloader"""

class ConfigurationError(ETFDownloaderError):
    """Configuration-related errors"""

class DataSourceError(ETFDownloaderError):
    """Data source connection/response errors"""

class ValidationError(ETFDownloaderError):
    """Data validation failures"""

class StorageError(ETFDownloaderError):
    """Data storage operation failures"""
```

### Retry Logic
```python
@retry(
    max_attempts=3,
    backoff_factor=2,
    exceptions=(httpx.HTTPStatusError, httpx.ConnectTimeout)
)
async def fetch_with_retry(url: str) -> httpx.Response:
    # Implementation with exponential backoff
```

## Performance Considerations

### Async Operations
The application uses `asyncio` for concurrent data fetching:
- Multiple ETF symbols downloaded simultaneously
- Rate limiting applied per data source
- Connection pooling for HTTP requests

### Memory Management
- Streaming processing for large datasets
- Lazy loading of historical data
- Configurable batch sizes

### Caching Strategy
- HTTP response caching with TTL
- Computed indicator caching
- Configuration caching

## Testing Structure

### Unit Tests
- Mock external API responses
- Test data validation rules
- Verify configuration loading
- Check error handling paths

### Integration Tests
- End-to-end data pipeline testing
- Storage backend verification
- Configuration file validation

### Performance Tests
- Benchmark download speeds
- Memory usage profiling
- Rate limiting effectiveness

## Development Guidelines

### Code Style
- Type hints for all functions
- Docstrings in Google format
- Maximum line length: 88 characters
- Use `black` for formatting

### Adding New Data Sources
1. Create adapter class inheriting from `BaseAdapter`
2. Implement required methods
3. Add configuration schema
4. Write comprehensive tests
5. Update documentation

### Adding New Storage Formats
1. Create backend class inheriting from `BaseStorage`
2. Implement serialisation/deserialisation
3. Add compression support if needed
4. Write format validation tests
5. Update factory registration