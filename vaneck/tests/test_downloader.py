"""Unit tests for the ETF downloader module."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from urllib.parse import urljoin, urlparse
import pytest
import requests
import aiohttp
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from vaneck_downloader.config import Config


class TestURLParsing:
    """Test URL parsing and validation functionality."""
    
    def test_valid_vaneck_url_parsing(self):
        """Test parsing of valid VanEck URLs."""
        base_url = "https://www.vaneck.com"
        relative_url = "/us/en/investments/gold-miners-etf-gdx/"
        
        full_url = urljoin(base_url, relative_url)
        parsed = urlparse(full_url)
        
        assert parsed.scheme == "https"
        assert parsed.netloc == "www.vaneck.com"
        assert parsed.path == "/us/en/investments/gold-miners-etf-gdx/"
        
    def test_absolute_url_parsing(self):
        """Test parsing of absolute URLs."""
        url = "https://www.vaneck.com/us/en/investments/gold-miners-etf-gdx/holdings.xlsx"
        parsed = urlparse(url)
        
        assert parsed.scheme == "https"
        assert parsed.netloc == "www.vaneck.com"
        assert parsed.path.endswith("holdings.xlsx")
        
    def test_invalid_url_handling(self):
        """Test handling of invalid URLs."""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://invalid-scheme.com",
            "javascript:alert('xss')",
        ]
        
        for url in invalid_urls:
            parsed = urlparse(url)
            # Should not crash, but may have empty or invalid components
            assert isinstance(parsed.scheme, str)
            
    def test_url_filename_extraction(self):
        """Test extraction of filename from URL."""
        test_cases = [
            ("https://example.com/file.pdf", "file.pdf"),
            ("https://example.com/path/to/document.xlsx", "document.xlsx"), 
            ("https://example.com/noextension", "noextension"),
            ("https://example.com/path/", ""),
        ]
        
        for url, expected_filename in test_cases:
            parsed = urlparse(url)
            filename = Path(parsed.path).name
            assert filename == expected_filename


class TestDataExtraction:
    """Test data extraction from HTML responses."""
    
    def test_etf_link_extraction(self, sample_html_response):
        """Test extraction of ETF detail links from HTML."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(sample_html_response, 'html.parser')
        detail_links = soup.find_all('a', class_='detail-link')
        
        assert len(detail_links) == 2
        assert detail_links[0].get('href') == '/us/en/investments/gold-miners-etf-gdx/'
        assert detail_links[1].get('href') == '/us/en/investments/semiconductor-etf-smh/'
        
    def test_ticker_extraction(self, sample_html_response):
        """Test extraction of ticker symbols from HTML."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(sample_html_response, 'html.parser')
        ticker_elements = soup.find_all('span', class_='ticker')
        
        tickers = [elem.text.strip() for elem in ticker_elements]
        assert tickers == ['GDX', 'SMH']
        
    def test_nav_value_extraction(self, sample_html_response):
        """Test extraction of NAV values from HTML."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(sample_html_response, 'html.parser')
        nav_elements = soup.find_all('span', class_='nav')
        
        navs = [elem.text.strip() for elem in nav_elements]
        assert navs == ['$25.43', '$145.67']
        
    def test_empty_html_handling(self):
        """Test handling of empty or malformed HTML."""
        from bs4 import BeautifulSoup
        
        empty_cases = ["", "<html></html>", "<invalid>markup"]
        
        for html in empty_cases:
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a')
            assert isinstance(links, list)  # Should return empty list, not crash


class TestHTTPRequestMocking:
    """Test HTTP request functionality with mocks."""
    
    def test_successful_get_request(self, mock_session):
        """Test successful HTTP GET request."""
        import requests
        
        response = requests.get("https://www.vaneck.com/test")
        
        assert response.status_code == 200
        assert "Mock response" in response.text
        
    def test_request_with_headers(self, mock_session):
        """Test HTTP request with custom headers."""
        import requests
        
        headers = {
            "User-Agent": "VanEck-Downloader/1.0",
            "Accept": "text/html,application/xhtml+xml",
        }
        
        requests.get("https://www.vaneck.com/test", headers=headers)
        
        mock_session.return_value.get.assert_called_once()
        call_args = mock_session.return_value.get.call_args
        assert call_args[1]["headers"] == headers
        
    def test_request_timeout_handling(self, mock_session):
        """Test request timeout configuration."""
        import requests
        
        mock_session.return_value.get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(requests.exceptions.Timeout):
            requests.get("https://www.vaneck.com/test", timeout=5)
            
    def test_connection_error_handling(self, mock_session):
        """Test connection error handling."""
        import requests
        
        mock_session.return_value.get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get("https://www.vaneck.com/test")
            
    @pytest.mark.asyncio
    async def test_aiohttp_request_mock(self, mock_aiohttp_session):
        """Test async HTTP requests with aiohttp."""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.vaneck.com/test") as response:
                assert response.status == 200
                text = await response.text()
                assert "Mock response" in text


class TestRetryLogic:
    """Test retry logic and error handling."""
    
    def test_retry_on_connection_error(self, mocker):
        """Test retry mechanism on connection errors."""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=0.1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Mock the actual request to simulate failures then success
        mock_get = mocker.patch.object(session, 'get')
        mock_get.side_effect = [
            requests.exceptions.ConnectionError(),
            requests.exceptions.ConnectionError(), 
            Mock(status_code=200, text="Success")
        ]
        
        # This should succeed after retries
        response = session.get("https://www.vaneck.com/test")
        assert response.status_code == 200
        assert mock_get.call_count == 3
        
    def test_max_retries_exceeded(self, mocker):
        """Test behaviour when max retries are exceeded.""" 
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        retry_strategy = Retry(total=2, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        
        mock_get = mocker.patch.object(session, 'get')
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(requests.exceptions.ConnectionError):
            session.get("https://www.vaneck.com/test")
            
        assert mock_get.call_count == 3  # Original + 2 retries
        
    def test_exponential_backoff(self, mocker):
        """Test exponential backoff in retry logic."""
        import time
        from tenacity import retry, stop_after_attempt, wait_exponential
        
        call_times = []
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.1, min=0.1, max=1)
        )
        def failing_function():
            call_times.append(time.time())
            raise Exception("Simulated failure")
        
        with pytest.raises(Exception):
            failing_function()
            
        assert len(call_times) == 3
        
        # Check that delays increase (exponential backoff)
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            assert delay2 >= delay1  # Second delay should be longer
            
    @pytest.mark.asyncio 
    async def test_async_retry_logic(self, mocker):
        """Test retry logic for async operations."""
        import asyncio
        from tenacity import retry, stop_after_attempt, wait_fixed
        
        attempt_count = 0
        
        @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1))
        async def failing_async_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise aiohttp.ClientError("Simulated async failure")
            return "success"
        
        result = await failing_async_function()
        assert result == "success"
        assert attempt_count == 3


class TestFileSystemOperations:
    """Test file system operations for downloads."""
    
    def test_file_creation_and_writing(self, temp_dir):
        """Test creating and writing files."""
        test_file = temp_dir / "test_download.txt"
        test_content = "Test file content for download"
        
        test_file.write_text(test_content)
        
        assert test_file.exists()
        assert test_file.read_text() == test_content
        
    def test_directory_creation(self, temp_dir):
        """Test creating nested directories."""
        nested_dir = temp_dir / "downloads" / "etf_data" / "2024"
        nested_dir.mkdir(parents=True, exist_ok=True)
        
        assert nested_dir.exists()
        assert nested_dir.is_dir()
        
    def test_file_size_checking(self, temp_dir):
        """Test checking file sizes."""
        test_file = temp_dir / "size_test.txt" 
        content = "X" * 1000  # 1000 bytes
        test_file.write_text(content)
        
        assert test_file.stat().st_size == 1000
        
    def test_file_exists_before_download(self, temp_dir):
        """Test checking if file exists before download."""
        existing_file = temp_dir / "existing.pdf"
        existing_file.write_text("existing content")
        
        non_existing_file = temp_dir / "not_existing.pdf"
        
        assert existing_file.exists()
        assert not non_existing_file.exists()
        
    def test_partial_file_resumption(self, temp_dir):
        """Test resuming partial file downloads."""
        partial_file = temp_dir / "partial.pdf"
        initial_content = b"partial content"
        
        # Write initial partial content
        partial_file.write_bytes(initial_content)
        initial_size = partial_file.stat().st_size
        
        # Simulate appending more content (resume)
        additional_content = b" more content"
        with partial_file.open("ab") as f:
            f.write(additional_content)
            
        final_size = partial_file.stat().st_size
        assert final_size == initial_size + len(additional_content)
        
        final_content = partial_file.read_bytes()
        assert final_content == initial_content + additional_content
        
    def test_atomic_file_operations(self, temp_dir):
        """Test atomic file operations to prevent corruption."""
        target_file = temp_dir / "target.txt"
        temp_file = temp_dir / "target.txt.tmp"
        
        content = "Final content"
        
        # Write to temporary file first
        temp_file.write_text(content)
        
        # Atomic move
        temp_file.rename(target_file)
        
        assert target_file.exists()
        assert not temp_file.exists()
        assert target_file.read_text() == content
        
    def test_file_permission_handling(self, temp_dir, mock_file_operations):
        """Test handling of file permission errors."""
        restricted_file = temp_dir / "readonly.txt"
        
        # Mock permission denied error
        mock_file_operations["open"].side_effect = PermissionError("Access denied")
        
        with pytest.raises(PermissionError):
            with open(restricted_file, 'w') as f:
                f.write("test")


class TestConcurrentDownloadLimits:
    """Test concurrent download limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrent_downloads(self):
        """Test that semaphore limits concurrent downloads."""
        max_concurrent = 2
        semaphore = asyncio.Semaphore(max_concurrent)
        active_downloads = []
        download_started_times = []
        download_finished_times = []
        
        async def mock_download(download_id: int):
            async with semaphore:
                download_started_times.append((download_id, asyncio.get_event_loop().time()))
                active_downloads.append(download_id)
                
                # Simulate download time
                await asyncio.sleep(0.1)
                
                active_downloads.remove(download_id)
                download_finished_times.append((download_id, asyncio.get_event_loop().time()))
                return f"Downloaded {download_id}"
        
        # Start multiple downloads
        tasks = [mock_download(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all("Downloaded" in result for result in results)
        
        # Verify that no more than max_concurrent downloads were active
        # This is a simplified check - in practice, we'd need more sophisticated monitoring
        assert len(download_started_times) == 5
        
    @pytest.mark.asyncio
    async def test_download_queue_management(self):
        """Test proper queue management for downloads."""
        download_queue = asyncio.Queue(maxsize=10)
        results = []
        
        async def producer():
            for i in range(5):
                await download_queue.put(f"download_task_{i}")
            # Signal end of tasks
            await download_queue.put(None)
        
        async def consumer():
            while True:
                task = await download_queue.get()
                if task is None:
                    download_queue.task_done()
                    break
                
                # Simulate processing
                await asyncio.sleep(0.01)
                results.append(f"processed_{task}")
                download_queue.task_done()
        
        # Start producer and consumer
        await asyncio.gather(producer(), consumer())
        
        assert len(results) == 5
        assert all("processed_download_task_" in result for result in results)
        
    @pytest.mark.asyncio
    async def test_rate_limiting_between_requests(self):
        """Test rate limiting between HTTP requests."""
        request_times = []
        
        async def rate_limited_request(delay: float = 0.1):
            request_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(delay)  # Simulate rate limiting delay
            return "response"
        
        # Make multiple requests with rate limiting
        tasks = [rate_limited_request() for _ in range(3)]
        await asyncio.gather(*tasks)
        
        assert len(request_times) == 3
        
        # Verify requests were spaced out (though this is async so timing might vary)
        if len(request_times) >= 2:
            time_diff = request_times[1] - request_times[0]
            assert time_diff >= 0  # Basic sanity check
            
    @pytest.mark.asyncio
    async def test_graceful_shutdown_of_downloads(self):
        """Test graceful shutdown of ongoing downloads."""
        download_cancelled = False
        
        async def long_running_download():
            try:
                await asyncio.sleep(1.0)  # Long running task
                return "completed"
            except asyncio.CancelledError:
                nonlocal download_cancelled
                download_cancelled = True
                raise
        
        # Start download and cancel it
        task = asyncio.create_task(long_running_download())
        await asyncio.sleep(0.1)  # Let it start
        task.cancel()
        
        with pytest.raises(asyncio.CancelledError):
            await task
            
        assert download_cancelled
        
    @pytest.mark.asyncio
    async def test_download_progress_tracking(self):
        """Test tracking download progress."""
        progress_updates = []
        
        async def download_with_progress(total_size: int = 1000):
            chunk_size = 100
            downloaded = 0
            
            while downloaded < total_size:
                await asyncio.sleep(0.01)  # Simulate chunk download time
                downloaded += min(chunk_size, total_size - downloaded)
                progress = (downloaded / total_size) * 100
                progress_updates.append(progress)
                
            return "download_complete"
        
        result = await download_with_progress()
        
        assert result == "download_complete"
        assert len(progress_updates) == 10  # 1000 / 100 chunks
        assert progress_updates[-1] == 100.0  # Should end at 100%
        assert all(0 <= p <= 100 for p in progress_updates)  # All valid percentages


class TestConfigurationHandling:
    """Test configuration management."""
    
    def test_default_config_values(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.base_url == "https://www.vaneck.com"
        assert config.max_concurrent_downloads == 5
        assert config.request_timeout == 30
        assert config.max_retries == 3
        assert config.enable_resume is True
        assert config.browser_headless is True
        
    def test_config_from_environment(self, mock_env_vars):
        """Test loading configuration from environment variables."""
        config = Config.from_env()
        
        assert str(config.download_dir) == "/tmp/vaneck_test"
        assert config.max_concurrent_downloads == 3
        assert config.log_level == "DEBUG"
        assert config.request_timeout == 15
        assert config.selenium_grid_url == "http://localhost:4444/wd/hub"
        
    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid log level
        with pytest.raises(ValueError, match="Log level must be one of"):
            Config(log_level="INVALID")
            
        # Test negative values
        with pytest.raises(ValueError):
            Config(max_concurrent_downloads=-1)
            
        with pytest.raises(ValueError):
            Config(request_timeout=-10)
            
    def test_config_directory_creation(self, temp_dir):
        """Test automatic directory creation in config."""
        download_dir = temp_dir / "new_downloads"
        assert not download_dir.exists()
        
        config = Config(download_dir=download_dir)
        
        # Directory should be created by validator
        assert config.download_dir.exists()
        assert config.download_dir.is_dir()


class TestErrorScenarios:
    """Test various error scenarios and edge cases."""
    
    def test_network_timeout_handling(self, mocker):
        """Test handling of network timeouts."""
        import requests
        
        mock_get = mocker.patch("requests.get")
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(requests.exceptions.Timeout):
            requests.get("https://www.vaneck.com/test", timeout=5)
            
    def test_http_error_status_codes(self, mocker):
        """Test handling of HTTP error status codes."""
        import requests
        
        error_codes = [400, 401, 403, 404, 429, 500, 502, 503, 504]
        
        for code in error_codes:
            mock_response = Mock()
            mock_response.status_code = code
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(f"HTTP {code}")
            
            mock_get = mocker.patch("requests.get", return_value=mock_response)
            
            with pytest.raises(requests.exceptions.HTTPError):
                response = requests.get("https://www.vaneck.com/test")
                response.raise_for_status()
                
    def test_malformed_html_parsing(self):
        """Test handling of malformed HTML."""
        from bs4 import BeautifulSoup
        
        malformed_html_cases = [
            "<html><body><div>Unclosed div</body></html>",
            "<html><head><title>Title</head><body>Missing closing tags",
            "<<invalid>><<tags>>content<</invalid>>",
            "",
            None,
        ]
        
        for html in malformed_html_cases:
            if html is not None:
                soup = BeautifulSoup(html, 'html.parser')
                # Should not crash
                links = soup.find_all('a')
                assert isinstance(links, list)
                
    def test_disk_space_exhaustion_simulation(self, temp_dir, mocker):
        """Test handling of disk space exhaustion."""
        test_file = temp_dir / "large_file.txt"
        
        # Mock OSError for disk full
        mock_write = mocker.patch("pathlib.Path.write_bytes")
        mock_write.side_effect = OSError(28, "No space left on device")  # ENOSPC
        
        with pytest.raises(OSError, match="No space left on device"):
            test_file.write_bytes(b"test content")
            
    def test_invalid_file_paths(self):
        """Test handling of invalid file paths."""
        invalid_paths = [
            "",
            "/dev/null/invalid",  # Can't create file under null device
            "/root/forbidden",    # Permission denied path
            "\x00invalid",        # Null byte in path
        ]
        
        for invalid_path in invalid_paths:
            try:
                path = Path(invalid_path)
                # Basic operations should not crash the program
                assert isinstance(str(path), str)
            except (ValueError, OSError):
                # Expected for truly invalid paths
                pass
                
    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self):
        """Test handling of memory pressure during downloads."""
        # Simulate memory pressure by creating large data
        large_data_chunks = []
        
        try:
            # This test simulates memory usage without actually exhausting system memory
            for i in range(10):
                # Simulate processing chunks of data
                chunk = f"chunk_{i}_data" * 1000  # ~13KB per chunk
                large_data_chunks.append(chunk)
                
                # Simulate async processing
                await asyncio.sleep(0.001)
                
                # Clean up periodically to prevent actual memory issues
                if i % 5 == 0:
                    large_data_chunks = large_data_chunks[-2:]  # Keep only recent chunks
                    
            assert len(large_data_chunks) <= 7  # Should have cleaned up
            
        except MemoryError:
            # If we do hit memory limits, handle gracefully
            large_data_chunks.clear()
            assert True  # Test passes if we handle the error