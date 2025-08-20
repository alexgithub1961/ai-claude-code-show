"""Pytest configuration and shared fixtures."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock
from typing import AsyncGenerator, Generator
import pytest
from pytest_mock import MockerFixture

from vaneck_downloader.config import Config


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_config(temp_dir: Path) -> Config:
    """Provide a test configuration."""
    return Config(
        download_dir=temp_dir / "downloads",
        max_concurrent_downloads=2,
        request_timeout=10,
        max_retries=2,
        retry_delay=0.1,
        rate_limit_delay=0.1,
        log_level="DEBUG",
        enable_resume=True,
        browser_headless=True,
    )


@pytest.fixture
def mock_session(mocker: MockerFixture) -> Mock:
    """Provide a mock HTTP session."""
    session = mocker.patch("requests.Session")
    session.return_value.get.return_value.status_code = 200
    session.return_value.get.return_value.text = "<html><body>Mock response</body></html>"
    session.return_value.get.return_value.content = b"Mock binary content"
    session.return_value.get.return_value.headers = {
        "Content-Type": "text/html",
        "Content-Length": "100",
    }
    return session


@pytest.fixture
def mock_aiohttp_session(mocker: MockerFixture) -> Mock:
    """Provide a mock aiohttp session."""
    session = mocker.patch("aiohttp.ClientSession")
    response_mock = Mock()
    response_mock.status = 200
    response_mock.text = asyncio.coroutine(lambda: "<html><body>Mock response</body></html>")()
    response_mock.read = asyncio.coroutine(lambda: b"Mock binary content")()
    response_mock.headers = {
        "Content-Type": "text/html", 
        "Content-Length": "100",
    }
    
    session.return_value.__aenter__ = asyncio.coroutine(lambda x: session.return_value)
    session.return_value.__aexit__ = asyncio.coroutine(lambda *args: None)
    session.return_value.get.return_value.__aenter__ = asyncio.coroutine(lambda x: response_mock)
    session.return_value.get.return_value.__aexit__ = asyncio.coroutine(lambda *args: None)
    
    return session


@pytest.fixture
def sample_etf_list() -> list[dict]:
    """Provide sample ETF data for testing."""
    return [
        {
            "name": "VanEck Vectors Gold Miners ETF",
            "ticker": "GDX",
            "url": "https://www.vaneck.com/us/en/investments/gold-miners-etf-gdx/",
            "nav": 25.43,
            "expense_ratio": 0.52,
        },
        {
            "name": "VanEck Vectors Semiconductor ETF", 
            "ticker": "SMH",
            "url": "https://www.vaneck.com/us/en/investments/semiconductor-etf-smh/",
            "nav": 145.67,
            "expense_ratio": 0.35,
        },
        {
            "name": "VanEck Vectors Oil Services ETF",
            "ticker": "OIH", 
            "url": "https://www.vaneck.com/us/en/investments/oil-services-etf-oih/",
            "nav": 198.32,
            "expense_ratio": 0.35,
        },
    ]


@pytest.fixture
def sample_html_response() -> str:
    """Provide sample HTML response for scraping tests."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>VanEck ETF Finder</title></head>
    <body>
        <div class="etf-list">
            <div class="etf-item" data-ticker="GDX">
                <h3>VanEck Vectors Gold Miners ETF</h3>
                <span class="ticker">GDX</span>
                <span class="nav">$25.43</span>
                <a href="/us/en/investments/gold-miners-etf-gdx/" class="detail-link">Details</a>
            </div>
            <div class="etf-item" data-ticker="SMH">
                <h3>VanEck Vectors Semiconductor ETF</h3>
                <span class="ticker">SMH</span>
                <span class="nav">$145.67</span>
                <a href="/us/en/investments/semiconductor-etf-smh/" class="detail-link">Details</a>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_selenium_driver(mocker: MockerFixture) -> Mock:
    """Provide a mock Selenium WebDriver."""
    driver = mocker.patch("selenium.webdriver.Chrome")
    driver.return_value.page_source = "<html><body>Selenium response</body></html>"
    driver.return_value.get = Mock()
    driver.return_value.quit = Mock()
    driver.return_value.find_elements.return_value = []
    return driver


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Provide event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_temp_files(temp_dir: Path) -> AsyncGenerator[list[Path], None]:
    """Create temporary files for async tests."""
    files = []
    for i in range(3):
        file_path = temp_dir / f"test_file_{i}.txt"
        file_path.write_text(f"Test content {i}")
        files.append(file_path)
    
    yield files
    
    # Cleanup (though temp_dir fixture handles this)
    for file_path in files:
        if file_path.exists():
            file_path.unlink()


@pytest.fixture
def mock_file_operations(mocker: MockerFixture) -> dict:
    """Mock file system operations."""
    return {
        "open": mocker.patch("builtins.open", mocker.mock_open(read_data="test data")),
        "makedirs": mocker.patch("os.makedirs"),
        "exists": mocker.patch("os.path.exists", return_value=True),
        "remove": mocker.patch("os.remove"),
        "rename": mocker.patch("os.rename"),
    }


@pytest.fixture
def mock_env_vars(mocker: MockerFixture) -> dict:
    """Mock environment variables."""
    env_vars = {
        "VANECK_DOWNLOAD_DIR": "/tmp/vaneck_test",
        "VANECK_MAX_CONCURRENT": "3",
        "VANECK_LOG_LEVEL": "DEBUG",
        "VANECK_REQUEST_TIMEOUT": "15",
        "SELENIUM_GRID_URL": "http://localhost:4444/wd/hub",
    }
    
    mocker.patch.dict("os.environ", env_vars)
    return env_vars


# Markers for test categorisation
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests") 
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "network: Tests requiring network access")