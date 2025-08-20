# VanEck ETF Data Downloader - Claude Instructions

This document provides project-specific guidance for Claude when working with the VanEck ETF data downloader project.

## Project Context

This is a Python-based ETF data collection system that downloads, processes, and stores financial data from multiple sources. The system prioritises reliability, data quality, and extensibility.

## Architecture Decisions

### Core Design Principles
- **Fault tolerance**: All external API calls must handle failures gracefully
- **Rate limiting**: Respect provider rate limits to maintain API access
- **Data integrity**: Validate all incoming data before processing
- **Modularity**: Each component should be independently testable
- **Configuration-driven**: Minimise hard-coded values

### Technology Stack
- **Language**: Python 3.12+ with type hints
- **Data processing**: pandas, numpy for data manipulation
- **HTTP client**: httpx for async requests with retry logic
- **Storage**: Support for CSV, JSON, Parquet formats
- **Containerisation**: Docker for deployment
- **Testing**: pytest with fixtures for external dependencies

### Key Architectural Patterns
- **Strategy Pattern**: For different data source adapters
- **Observer Pattern**: For progress monitoring and logging
- **Factory Pattern**: For creating appropriate storage backends
- **Command Pattern**: For CLI operations

## Component Responsibilities

### `src/downloader/`
- **`core.py`**: Main ETFDownloader class with rate limiting
- **`adapters/`**: Data source-specific implementations
- **`auth.py`**: Authentication handling for APIs
- **`cache.py`**: Request caching to reduce API calls

### `src/processors/`
- **`validator.py`**: Data validation rules and schemas
- **`normaliser.py`**: Data standardisation across sources
- **`enricher.py`**: Additional data enhancement (ratios, metrics)
- **`cleaner.py`**: Data cleaning and outlier detection

### `src/storage/`
- **`backends/`**: Storage implementation (CSV, JSON, Parquet, DB)
- **`schemas.py`**: Data schemas and validation
- **`compression.py`**: Data compression utilities

### `src/utils/`
- **`config.py`**: Configuration loading and validation
- **`logging.py`**: Structured logging setup
- **`exceptions.py`**: Custom exception classes
- **`decorators.py`**: Common decorators (retry, rate_limit, etc.)

## Testing Strategy

### Unit Tests
- Mock all external API calls using `httpx_mock` or `responses`
- Test data validation with both valid and invalid datasets
- Verify error handling for network failures and malformed data
- Use parametrised tests for different data source formats

### Integration Tests
- Test complete data pipeline with sample data
- Verify storage backend functionality
- Test configuration loading from files and environment

### Performance Tests
- Benchmark data processing speed with large datasets
- Test memory usage with streaming data processing
- Verify rate limiting effectiveness

### Test Data
- Store sample responses in `tests/fixtures/`
- Use realistic but anonymised ETF data
- Include edge cases (missing fields, unusual values)

## Configuration Management

### Environment Variables (Production)
```bash
ETF_API_KEY=your_api_key_here
ETF_DATA_DIR=/data/etf
ETF_LOG_LEVEL=INFO
ETF_CACHE_TTL=3600
```

### Local Development
- Use `.env` file for local configuration
- Never commit API keys or sensitive data
- Provide `.env.example` with dummy values

### Docker Configuration
- Use multi-stage builds for smaller images
- Non-root user for security
- Health check endpoint for container orchestration

## Data Sources

### Primary Sources
- **Alpha Vantage**: Real-time and historical data
- **IEX Cloud**: Market data API
- **Yahoo Finance**: Backup data source
- **Direct ETF providers**: VanEck, Vanguard APIs where available

### Data Quality Requirements
- Validate required fields: symbol, date, price, volume
- Check for reasonable price ranges (no negative prices)
- Ensure chronological consistency in time series
- Flag and handle missing data appropriately

## Error Handling Patterns

### API Errors
```python
@retry(max_attempts=3, backoff_factor=2)
async def fetch_etf_data(symbol: str) -> ETFData:
    try:
        response = await client.get(f"/etf/{symbol}")
        response.raise_for_status()
        return ETFData.parse(response.json())
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            await asyncio.sleep(self.rate_limiter.wait_time)
            raise
        logger.error(f"API error for {symbol}: {e}")
        raise
```

### Data Validation Errors
- Log validation failures with specific field information
- Continue processing other symbols when one fails
- Provide summary statistics of validation results

## Deployment Considerations

### Production Environment
- Use environment-specific configuration files
- Implement health check endpoints
- Set up monitoring and alerting for failed downloads
- Use volume mounts for data persistence

### Scaling Considerations
- Implement async downloads for better throughput
- Consider task queues (Celery/RQ) for distributed processing
- Database storage for high-volume scenarios
- Caching layer for frequently accessed data

### Security Requirements
- Never log API keys or sensitive data
- Validate all input parameters
- Use HTTPS for all external requests
- Implement request signing where required

## Known Issues and Limitations

### Current Limitations
- Single-threaded processing (planned: async implementation)
- Limited to CSV/JSON output (planned: database support)
- No real-time streaming (planned: WebSocket support)
- Basic error recovery (planned: exponential backoff)

### Known Issues
- Rate limiting may be too conservative for some APIs
- Large datasets may cause memory issues without streaming
- Time zone handling needs improvement for global markets
- Limited support for complex ETF structures

### Technical Debt
- Refactor configuration system to use Pydantic
- Improve test coverage for edge cases
- Add proper OpenAPI documentation
- Implement comprehensive logging strategy

## Development Workflow

### Before Starting Work
1. Check existing issues and PRs
2. Run full test suite to ensure clean starting state
3. Update dependencies if needed
4. Review recent commits for context

### Code Quality Gates
- All functions must have type hints and docstrings
- Test coverage must remain above 80%
- Code must pass flake8 and mypy checks
- No hardcoded API keys or sensitive data

### When Adding New Features
- Start with failing tests (TDD approach)
- Update configuration schema if needed
- Add example usage to documentation
- Consider backwards compatibility

### Performance Considerations
- Profile memory usage for large datasets
- Benchmark API response times
- Consider caching strategies for repeated requests
- Monitor rate limit adherence

## Integration Points

### External Dependencies
- Financial data APIs (rate-limited, authentication required)
- Storage systems (file system, databases)
- Monitoring systems (logging, metrics)
- Container orchestration platforms

### Internal Dependencies
- Configuration system drives all component behaviour
- Logging system provides observability across components
- Error handling provides consistent failure modes
- Data validation ensures system reliability