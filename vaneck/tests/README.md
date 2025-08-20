# VanEck ETF Downloader Test Suite

This directory contains a comprehensive test suite for the VanEck ETF Downloader application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialisation
├── conftest.py                 # Shared pytest fixtures
├── test_config.py              # Configuration management tests
├── test_downloader.py          # Core downloader functionality tests  
├── test_integration.py         # Integration tests
├── fixtures/                   # Test data and fixtures
│   ├── __init__.py
│   └── sample_data.py          # Sample HTML, CSV, JSON data
└── README.md                   # This file
```

## Test Categories

Tests are organised into categories using pytest markers:

- **`@pytest.mark.unit`**: Fast, isolated unit tests
- **`@pytest.mark.integration`**: Integration tests with external dependencies
- **`@pytest.mark.e2e`**: End-to-end system tests
- **`@pytest.mark.slow`**: Tests that take longer than 5 seconds
- **`@pytest.mark.network`**: Tests requiring internet connectivity
- **`@pytest.mark.selenium`**: Tests using Selenium WebDriver
- **`@pytest.mark.docker`**: Tests requiring Docker
- **`@pytest.mark.performance`**: Performance and load tests

## Running Tests

### Quick Start

```bash
# Install dependencies
pip install -e .[dev]

# Run all tests
pytest

# Or use the test script
./shell/test.sh
```

### Test Script Options

The `shell/test.sh` script provides comprehensive testing with additional features:

```bash
# Run all tests with coverage
./shell/test.sh

# Run only unit tests (fast)
./shell/test.sh --unit

# Run integration tests (requires network)
./shell/test.sh --integration

# Run tests matching a pattern
./shell/test.sh -k "test_download"

# Skip slow tests
./shell/test.sh -m "not slow"

# Run tests in parallel
./shell/test.sh --parallel

# Generate HTML coverage report
./shell/test.sh --html

# Clean artifacts and run tests
./shell/test.sh --clean

# Verbose output
./shell/test.sh --verbose
```

### Pytest Direct Usage

```bash
# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit

# Skip network tests
pytest -m "not network"

# Run tests matching pattern
pytest -k "test_config"

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

## Test Configuration

### pytest.ini

The `pytest.ini` file in the project root contains default configuration:

- Test discovery patterns
- Coverage settings
- Logging configuration
- Marker definitions
- Timeout settings

### Environment Variables

Tests respect these environment variables:

```bash
export VANECK_LOG_LEVEL=DEBUG                    # Set log level for tests
export VANECK_DOWNLOAD_DIR=/tmp/test_downloads    # Test download directory
export VANECK_REQUEST_TIMEOUT=10                 # Shorter timeout for tests
export SELENIUM_GRID_URL=http://localhost:4444   # Selenium Grid URL
```

## Test Data and Fixtures

### Shared Fixtures (conftest.py)

- **`temp_dir`**: Temporary directory for test files
- **`test_config`**: Test configuration with safe defaults
- **`mock_session`**: Mocked HTTP session
- **`mock_aiohttp_session`**: Mocked async HTTP session
- **`sample_etf_list`**: Sample ETF data
- **`sample_html_response`**: Sample HTML response
- **`mock_selenium_driver`**: Mocked Selenium WebDriver

### Test Data (fixtures/sample_data.py)

- Sample HTML responses from VanEck website
- Sample CSV, JSON, and PDF content
- Mock HTTP response configurations
- URL patterns and test data

## Coverage Requirements

- Minimum coverage threshold: **90%**
- Branch coverage enabled
- Coverage reports generated in `htmlcov/`
- XML reports for CI in `coverage.xml`

## Mock Strategy

Tests use comprehensive mocking to avoid external dependencies:

1. **HTTP Requests**: Mock `requests` and `aiohttp` calls
2. **File System**: Use temporary directories for file operations  
3. **Selenium**: Mock WebDriver for browser automation tests
4. **Network**: Mock network responses and errors
5. **Time**: Use `freezegun` for time-dependent tests

## Integration Test Guidelines

Integration tests in `test_integration.py` include:

### Network Tests
- Mark with `@pytest.mark.network`
- Skip automatically if network is unavailable
- Use real VanEck URLs with proper timeouts
- Test SSL certificate validation

### Docker Volume Tests
- Simulate volume mounting behaviour
- Test file permissions and concurrent access
- Verify cleanup on container exit

### Resume Functionality Tests
- Test partial download resumption
- Verify HTTP Range request support
- Test integrity checking during resume
- Test atomic operations to prevent corruption

### Performance Tests
- Mark with `@pytest.mark.performance` or `@pytest.mark.slow`
- Test concurrent download limits
- Memory usage patterns
- Error handling under load

## Selenium Tests

Browser automation tests require Chrome/Chromium:

```bash
# Install Chrome/Chromium for Selenium tests
sudo apt-get update
sudo apt-get install -y chromium-browser

# Or install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

Selenium tests automatically skip if browser is not available.

## CI/CD Integration

### GitHub Actions / GitLab CI

```yaml
- name: Run Tests
  run: |
    pip install -e .[dev]
    ./shell/test.sh --xml --cov-fail
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Jenkins

```groovy
stage('Test') {
    steps {
        sh 'pip install -e .[dev]'
        sh './shell/test.sh --xml --html'
    }
    post {
        always {
            junit 'test-reports/junit.xml'
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
    }
}
```

## Debugging Tests

### Failed Test Debugging

```bash
# Run with maximum verbosity and show local variables
pytest -vvv -l --tb=long

# Stop on first failure and open debugger
pytest -x --pdb

# Run specific failing test
pytest tests/test_downloader.py::TestURLParsing::test_valid_vaneck_url_parsing -v

# Show print statements
pytest -s
```

### Coverage Debugging

```bash
# See which lines are missing coverage
pytest --cov=src --cov-report=term-missing

# Generate detailed HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Performance Debugging

```bash
# Profile test execution time
pytest --durations=10

# Memory profiling (if installed)
pytest --memprof
```

## Best Practices

### Writing Tests

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use appropriate markers** to categorise tests
4. **Mock external dependencies** to ensure tests are isolated
5. **Test both success and failure cases**
6. **Use parametrized tests** for testing multiple scenarios
7. **Keep tests focused** - one concept per test
8. **Use fixtures** for common setup and teardown

### Test Data

1. **Use realistic test data** that mirrors production
2. **Keep test data small** but representative
3. **Use factories** for generating test data
4. **Store reusable data** in fixtures/sample_data.py
5. **Clean up test data** after tests complete

### Performance

1. **Mark slow tests** with `@pytest.mark.slow`
2. **Use mocks** to avoid actual HTTP requests
3. **Run unit tests frequently** during development
4. **Run integration tests** before commits
5. **Use parallel execution** for large test suites

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `pip install -e .[dev]` was run
2. **Permission errors**: Check file permissions in test directories
3. **Network timeouts**: Skip network tests or increase timeouts
4. **Selenium errors**: Ensure Chrome/Chromium is installed
5. **Coverage too low**: Add tests for uncovered code paths

### Getting Help

1. Check test output for specific error messages
2. Run tests with `-vvv` for maximum verbosity  
3. Use `--tb=long` for detailed tracebacks
4. Check fixture definitions in `conftest.py`
5. Review sample data in `fixtures/sample_data.py`

## Contributing

When adding new tests:

1. Follow existing naming conventions
2. Add appropriate markers
3. Update this README if adding new test categories
4. Ensure tests are deterministic and don't depend on external state
5. Add fixtures for reusable test data
6. Maintain or improve coverage percentage