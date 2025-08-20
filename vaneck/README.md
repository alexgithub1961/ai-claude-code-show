# VanEck ETF Data Downloader

A robust Python application for downloading ETF data files from VanEck's website with concurrent downloads, retry logic, and resumable transfers.

## Features

- 🌐 **Web Scraping**: Fetches ETF list from VanEck (handles JavaScript-rendered content with Selenium fallback)
- 📁 **Organised Storage**: Downloads files to structured directories (`download/{ticker}/{file_type}/`)
- 🔄 **Retry Logic**: Implements exponential backoff for failed downloads
- ⏸️ **Resumable Downloads**: Supports partial downloads and skips already downloaded files
- ⚡ **Concurrent Downloads**: Uses async/await for efficient parallel downloads
- 📊 **Progress Tracking**: Rich terminal output with progress bars and statistics
- 🛠️ **Configurable**: Environment-based configuration with sensible defaults
- 🧪 **Well Tested**: Comprehensive test suite with 90%+ coverage

## Quick Start

### Option 1: Using the standalone script

```bash
# Clone and setup
git clone <repository>
cd vaneck

# Quick run (creates venv and installs dependencies)
./shell/run.sh

# Download specific ETF
./shell/run.sh --ticker VTI

# Dry run to see what would be downloaded
./shell/run.sh --dry-run --max-etfs 5
```

### Option 2: Manual setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the downloader
python src/etf_downloader.py
```

### Option 3: Development setup

```bash
# Setup development environment with linting, testing, etc.
./shell/dev.sh
```

## Usage

### Command Line Options

```bash
python src/etf_downloader.py [OPTIONS]

Options:
  --max-etfs N         Maximum number of ETFs to process
  --ticker TICKER      Download data for specific ETF ticker only
  --dry-run           Show what would be downloaded without downloading
  --download-dir DIR   Download directory override
  --log-level LEVEL    Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

### Using the CLI Interface

```bash
# Install as package
pip install -e .

# Use the CLI
vaneck-downloader download --max-etfs 10
vaneck-downloader status
vaneck-downloader clean --ticker VTI
```

## Configuration

Create a `.env` file to customise settings:

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VANECK_DOWNLOAD_DIR` | `./download` | Download directory path |
| `VANECK_MAX_CONCURRENT` | `5` | Maximum concurrent downloads |
| `VANECK_REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `VANECK_MAX_RETRIES` | `3` | Maximum number of retries |
| `VANECK_RATE_LIMIT` | `1.0` | Delay between requests in seconds |
| `VANECK_LOG_LEVEL` | `INFO` | Logging level |
| `VANECK_ENABLE_RESUME` | `true` | Enable resumable downloads |
| `VANECK_HEADLESS` | `true` | Run browser in headless mode |
| `SELENIUM_GRID_URL` | - | Optional Selenium Grid URL |

## File Structure

Downloaded files are organised as follows:

```
download/
├── VTI/
│   ├── metadata.json
│   ├── fact_sheet/
│   │   └── vti_fact_sheet.pdf
│   ├── holdings/
│   │   └── vti_holdings.csv
│   ├── prospectus/
│   │   └── vti_prospectus.pdf
│   └── annual_report/
│       └── vti_annual_report.pdf
├── VEA/
│   └── ...
└── download_summary.json
```

## Development

### Setup Development Environment

```bash
./shell/dev.sh
```

This will:
- Create virtual environment
- Install all dependencies (including dev tools)
- Format code with Black
- Sort imports with isort
- Lint with Ruff
- Type check with mypy
- Run tests with coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/vaneck_downloader

# Run specific test
pytest tests/test_config.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/vaneck_downloader/
```

## Architecture

The application follows a clean architecture pattern:

- **`config.py`**: Configuration management with environment variable support
- **`scraper.py`**: Web scraping logic with HTTP + Selenium fallback
- **`downloader.py`**: Async file downloader with retry and resume capabilities
- **`storage.py`**: File organisation and metadata management
- **`main.py`**: CLI interface with Rich output
- **`etf_downloader.py`**: Standalone script entry point

## Error Handling

The downloader includes comprehensive error handling:

- **Network Errors**: Automatic retries with exponential backoff
- **Rate Limiting**: Configurable delays between requests
- **Partial Downloads**: Resume capability for interrupted transfers
- **Invalid URLs**: Graceful handling of broken links
- **File System Errors**: Proper cleanup of partial files

## Browser Automation

For JavaScript-heavy pages, the scraper falls back to Selenium:

- **Chrome WebDriver**: Automated browser for JavaScript rendering
- **Headless Mode**: Runs without GUI by default
- **Grid Support**: Can connect to remote Selenium Grid
- **Resource Management**: Proper cleanup of browser instances

## Performance

- **Concurrent Downloads**: Configurable number of simultaneous downloads
- **Rate Limiting**: Respectful scraping with delays
- **Resume Capability**: Avoid re-downloading existing files
- **Memory Efficient**: Streaming downloads for large files
- **Connection Pooling**: Reuse HTTP connections where possible

## Docker Support

```bash
# Build image
docker build -t vaneck-downloader .

# Run with volume mount
docker run -v $(pwd)/download:/app/download vaneck-downloader

# Run with environment variables
docker run -e VANECK_MAX_CONCURRENT=10 vaneck-downloader
```

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # Install Chrome and ChromeDriver
   sudo apt-get install google-chrome-stable
   pip install webdriver-manager
   ```

2. **Permission Errors**
   ```bash
   # Ensure download directory is writable
   chmod 755 download/
   ```

3. **Rate Limiting**
   ```bash
   # Increase delays if getting rate limited
   export VANECK_RATE_LIMIT=2.0
   ```

### Logging

Increase log level for debugging:

```bash
export VANECK_LOG_LEVEL=DEBUG
python src/etf_downloader.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run the development setup: `./shell/dev.sh`
4. Make your changes
5. Ensure tests pass and coverage is maintained
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Please respect VanEck's robots.txt and terms of service. Use responsibly and don't overload their servers.