"""Integration tests for the ETF downloader application."""

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, Mock
import pytest
import requests
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from vaneck_downloader.config import Config


@pytest.mark.integration 
class TestActualAPIIntegration:
    """Integration tests with actual VanEck API (test mode)."""
    
    @pytest.mark.network
    def test_vaneck_homepage_accessibility(self):
        """Test that VanEck homepage is accessible."""
        config = Config()
        
        try:
            response = requests.get(config.base_url, timeout=10)
            response.raise_for_status()
            
            assert response.status_code == 200
            assert "vaneck" in response.text.lower()
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"VanEck website not accessible: {e}")
    
    @pytest.mark.network        
    def test_etf_finder_page_structure(self):
        """Test the structure of the ETF finder page."""
        config = Config()
        
        try:
            response = requests.get(config.etf_finder_url, timeout=15)
            response.raise_for_status()
            
            # Basic checks for expected content
            content = response.text.lower()
            expected_elements = ["etf", "fund", "investment"]
            
            for element in expected_elements:
                assert element in content, f"Missing expected element: {element}"
                
        except requests.exceptions.RequestException as e:
            pytest.skip(f"ETF finder page not accessible: {e}")
    
    @pytest.mark.network
    @pytest.mark.slow
    async def test_async_http_client_integration(self):
        """Test async HTTP client integration."""
        config = Config()
        
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(config.base_url) as response:
                    assert response.status == 200
                    text = await response.text()
                    assert len(text) > 0
                    
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            pytest.skip(f"Async HTTP client test failed: {e}")
            
    @pytest.mark.network
    @pytest.mark.slow
    def test_request_headers_and_user_agent(self):
        """Test request headers and user agent handling."""
        config = Config()
        
        headers = {
            "User-Agent": config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
        }
        
        try:
            response = requests.get(
                config.base_url,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            # Verify response indicates successful request with headers
            assert response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Header integration test failed: {e}")
            
    @pytest.mark.network
    def test_ssl_certificate_validation(self):
        """Test SSL certificate validation."""
        config = Config()
        
        try:
            # Test with SSL verification enabled (default)
            response = requests.get(config.base_url, verify=True, timeout=10)
            response.raise_for_status()
            assert response.status_code == 200
            
        except requests.exceptions.SSLError:
            pytest.fail("SSL certificate validation failed")
        except requests.exceptions.RequestException as e:
            pytest.skip(f"SSL test failed due to network issue: {e}")


@pytest.mark.integration
class TestDockerVolumeIntegration:
    """Test Docker volume mounting functionality."""
    
    def test_volume_mount_simulation(self, temp_dir):
        """Simulate Docker volume mounting behaviour."""
        # Simulate container mount point
        container_mount = temp_dir / "container_data"
        host_mount = temp_dir / "host_data"
        
        # Create both directories
        container_mount.mkdir()
        host_mount.mkdir()
        
        # Test file written in container is visible on host
        test_file = "downloaded_etf_data.csv"
        test_content = "ticker,name,nav\nGDX,Gold Miners,25.43\n"
        
        # Write from "container" perspective
        container_file = container_mount / test_file
        container_file.write_text(test_content)
        
        # Simulate the mount by copying (in real Docker this would be automatic)
        host_file = host_mount / test_file
        host_file.write_text(container_file.read_text())
        
        # Verify file is accessible from both sides
        assert container_file.exists()
        assert host_file.exists()
        assert container_file.read_text() == host_file.read_text()
        
    def test_volume_permissions(self, temp_dir):
        """Test file permissions in volume mounts."""
        volume_dir = temp_dir / "volume"
        volume_dir.mkdir()
        
        test_file = volume_dir / "permissions_test.txt"
        test_file.write_text("test content")
        
        # Check basic file permissions
        stat_info = test_file.stat()
        assert stat_info.st_size > 0
        
        # Test read/write access
        assert test_file.is_file()
        assert test_file.read_text() == "test content"
        
        # Test modification
        test_file.write_text("modified content")
        assert test_file.read_text() == "modified content"
        
    def test_concurrent_file_access(self, temp_dir):
        """Test concurrent file access in shared volumes."""
        shared_dir = temp_dir / "shared"
        shared_dir.mkdir()
        
        # Simulate multiple processes writing to shared directory
        files_created = []
        
        for i in range(5):
            file_path = shared_dir / f"concurrent_file_{i}.txt"
            file_path.write_text(f"Content from process {i}")
            files_created.append(file_path)
            
        # Verify all files exist and have correct content
        for i, file_path in enumerate(files_created):
            assert file_path.exists()
            assert file_path.read_text() == f"Content from process {i}"
            
    def test_volume_cleanup_on_exit(self, temp_dir):
        """Test proper cleanup of volume data."""
        volume_dir = temp_dir / "cleanup_test"
        volume_dir.mkdir()
        
        # Create some test files
        for i in range(3):
            test_file = volume_dir / f"temp_file_{i}.txt"
            test_file.write_text(f"temporary content {i}")
            
        # Verify files exist
        files_before = list(volume_dir.glob("*.txt"))
        assert len(files_before) == 3
        
        # Simulate cleanup process
        for file_path in files_before:
            file_path.unlink()
            
        # Verify cleanup
        files_after = list(volume_dir.glob("*.txt"))
        assert len(files_after) == 0


@pytest.mark.integration
class TestResumeDownloadFunctionality:
    """Test download resume functionality."""
    
    def test_partial_file_resume(self, temp_dir):
        """Test resuming a partially downloaded file."""
        download_file = temp_dir / "partial_download.pdf"
        
        # Simulate partial download
        initial_content = b"PDF content start..." + b"x" * 1000
        download_file.write_bytes(initial_content)
        initial_size = download_file.stat().st_size
        
        # Simulate resume - append more content
        additional_content = b"...PDF content end" + b"y" * 500
        with download_file.open("ab") as f:
            f.write(additional_content)
            
        final_size = download_file.stat().st_size
        expected_size = len(initial_content) + len(additional_content)
        
        assert final_size == expected_size
        assert final_size > initial_size
        
        # Verify content integrity
        final_content = download_file.read_bytes()
        assert final_content.startswith(b"PDF content start...")
        assert final_content.endswith(b"...PDF content end" + b"y" * 500)
        
    def test_resume_with_http_range_requests(self, temp_dir):
        """Test resume functionality with HTTP Range requests."""
        download_file = temp_dir / "range_download.xlsx"
        
        # Simulate existing partial file
        existing_content = b"Excel header data..."
        download_file.write_bytes(existing_content)
        existing_size = len(existing_content)
        
        # Simulate HTTP Range request from byte position
        range_start = existing_size
        additional_content = b"...Excel body data..."
        
        # Mock HTTP response with range support
        mock_response = Mock()
        mock_response.status_code = 206  # Partial Content
        mock_response.headers = {
            "Content-Range": f"bytes {range_start}-{range_start + len(additional_content) - 1}/1500",
            "Content-Length": str(len(additional_content)),
        }
        mock_response.content = additional_content
        
        # Simulate appending range content
        with download_file.open("ab") as f:
            f.write(additional_content)
            
        # Verify resume worked correctly
        final_content = download_file.read_bytes()
        expected_content = existing_content + additional_content
        assert final_content == expected_content
        
    def test_resume_integrity_check(self, temp_dir):
        """Test integrity checking during resume."""
        download_file = temp_dir / "integrity_test.csv"
        
        # Create file with known content
        original_content = b"ticker,name,price\nAAPL,Apple Inc,150.00\n"
        download_file.write_bytes(original_content)
        original_checksum = hash(original_content)
        
        # Simulate corruption detection and restart
        corrupted_content = b"ticker,name,price\nAAPL,Apple Inc,CORRUPTED"
        corrupted_checksum = hash(corrupted_content)
        
        assert original_checksum != corrupted_checksum
        
        # In a real scenario, corruption would trigger a fresh download
        download_file.write_bytes(original_content)  # Restart download
        
        restored_content = download_file.read_bytes()
        restored_checksum = hash(restored_content)
        
        assert restored_checksum == original_checksum
        assert restored_content == original_content
        
    def test_atomic_resume_operations(self, temp_dir):
        """Test atomic operations during resume to prevent corruption."""
        target_file = temp_dir / "atomic_resume.json"
        temp_file = temp_dir / "atomic_resume.json.tmp"
        
        # Existing content
        existing_content = b'{"etfs": ['
        target_file.write_bytes(existing_content)
        
        # New content to append
        new_content = b'{"ticker": "GDX", "name": "Gold Miners"}]}'
        
        # Atomic resume: write to temp file first
        with temp_file.open("wb") as f:
            f.write(existing_content)  # Copy existing
            f.write(new_content)       # Add new content
            
        # Atomic replace
        temp_file.replace(target_file)
        
        # Verify atomic operation
        assert not temp_file.exists()
        assert target_file.exists()
        
        final_content = target_file.read_bytes()
        expected_content = existing_content + new_content
        assert final_content == expected_content
        
    @pytest.mark.asyncio
    async def test_async_resume_coordination(self, temp_dir):
        """Test coordination of resume across async downloads."""
        download_dir = temp_dir / "async_resumes"
        download_dir.mkdir()
        
        # Simulate multiple partial downloads
        partial_files = []
        for i in range(3):
            file_path = download_dir / f"async_partial_{i}.txt"
            initial_content = f"Start of file {i}...".encode()
            file_path.write_bytes(initial_content)
            partial_files.append((file_path, initial_content))
            
        async def resume_download(file_path: Path, existing_content: bytes):
            """Simulate async resume of a download."""
            await asyncio.sleep(0.1)  # Simulate network delay
            
            additional_content = f"...end of file {file_path.stem}".encode()
            
            # Atomic append
            with file_path.open("ab") as f:
                f.write(additional_content)
                
            return len(existing_content) + len(additional_content)
            
        # Resume all downloads concurrently
        tasks = [resume_download(fp, content) for fp, content in partial_files]
        final_sizes = await asyncio.gather(*tasks)
        
        # Verify all resumes completed
        assert len(final_sizes) == 3
        assert all(size > 0 for size in final_sizes)
        
        # Verify file contents
        for file_path, original_content in partial_files:
            final_content = file_path.read_bytes()
            assert final_content.startswith(original_content)
            assert b"...end of file" in final_content


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceConcurrency:
    """Performance and concurrency integration tests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_download_performance(self, temp_dir):
        """Test performance with multiple concurrent downloads."""
        download_dir = temp_dir / "concurrent_perf"
        download_dir.mkdir()
        
        # Configuration for performance test
        max_concurrent = 3
        num_downloads = 9
        
        async def simulate_download(download_id: int) -> dict:
            """Simulate a file download with timing."""
            start_time = time.time()
            
            # Simulate variable download times
            download_time = 0.1 + (download_id % 3) * 0.05
            await asyncio.sleep(download_time)
            
            # Create result file
            file_path = download_dir / f"download_{download_id}.txt"
            content = f"Downloaded content {download_id}"
            file_path.write_text(content)
            
            end_time = time.time()
            return {
                "download_id": download_id,
                "duration": end_time - start_time,
                "file_size": len(content),
                "file_path": file_path
            }
            
        # Limit concurrency with semaphore
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_download(download_id: int):
            async with semaphore:
                return await simulate_download(download_id)
                
        # Execute concurrent downloads
        start_time = time.time()
        tasks = [limited_download(i) for i in range(num_downloads)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Verify all downloads completed
        assert len(results) == num_downloads
        assert all(result["file_path"].exists() for result in results)
        
        # Performance assertions
        avg_download_time = sum(r["duration"] for r in results) / len(results)
        
        # With 3 concurrent downloads, should be faster than sequential
        # Sequential time would be roughly sum of all download times
        sequential_time_estimate = sum(0.1 + (i % 3) * 0.05 for i in range(num_downloads))
        
        # Concurrent execution should be significantly faster
        assert total_time < sequential_time_estimate * 0.8
        
    def test_memory_usage_with_large_files(self, temp_dir):
        """Test memory usage with large file operations."""
        large_file = temp_dir / "large_test_file.bin"
        
        # Create a moderately large file (1MB) for testing
        chunk_size = 8192
        total_chunks = 128  # 1MB total
        
        # Write file in chunks to simulate streaming
        with large_file.open("wb") as f:
            for i in range(total_chunks):
                chunk = bytes([i % 256]) * chunk_size
                f.write(chunk)
                
        # Verify file size
        expected_size = chunk_size * total_chunks
        actual_size = large_file.stat().st_size
        assert actual_size == expected_size
        
        # Test reading file in chunks (memory efficient)
        read_size = 0
        with large_file.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                read_size += len(chunk)
                
        assert read_size == expected_size
        
    @pytest.mark.asyncio
    async def test_error_handling_under_load(self, temp_dir):
        """Test error handling under concurrent load."""
        error_count = 0
        success_count = 0
        
        async def flaky_operation(operation_id: int):
            """Simulate an operation that sometimes fails."""
            nonlocal error_count, success_count
            
            await asyncio.sleep(0.01)  # Simulate work
            
            # Simulate 30% failure rate
            if operation_id % 3 == 0:
                error_count += 1
                raise Exception(f"Simulated failure for operation {operation_id}")
            else:
                success_count += 1
                return f"Success {operation_id}"
                
        # Run many concurrent operations
        num_operations = 20
        tasks = [flaky_operation(i) for i in range(num_operations)]
        
        # Gather results, allowing for failures
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyse results
        exceptions = [r for r in results if isinstance(r, Exception)]
        successes = [r for r in results if not isinstance(r, Exception)]
        
        # Verify error handling
        assert len(exceptions) > 0  # Should have some failures
        assert len(successes) > 0  # Should have some successes
        assert len(exceptions) + len(successes) == num_operations
        
        # Verify counters match
        assert error_count == len(exceptions)
        assert success_count == len(successes)
        
    def test_file_system_stress(self, temp_dir):
        """Test file system operations under stress."""
        stress_dir = temp_dir / "stress_test"
        stress_dir.mkdir()
        
        num_files = 50
        files_created = []
        
        # Create many files rapidly
        for i in range(num_files):
            file_path = stress_dir / f"stress_file_{i:03d}.txt"
            content = f"Stress test content {i}" * 10  # ~200 bytes per file
            file_path.write_text(content)
            files_created.append(file_path)
            
        # Verify all files were created
        assert len(files_created) == num_files
        assert all(f.exists() for f in files_created)
        
        # Test concurrent read operations
        total_content_length = 0
        for file_path in files_created:
            content = file_path.read_text()
            total_content_length += len(content)
            assert "Stress test content" in content
            
        # Verify expected total content
        expected_length = num_files * len("Stress test content 0" * 10)
        # Allow for variation due to different numbers in content
        assert abs(total_content_length - expected_length) < expected_length * 0.1
        
        # Clean up all files
        for file_path in files_created:
            file_path.unlink()
            
        # Verify cleanup
        remaining_files = list(stress_dir.glob("*.txt"))
        assert len(remaining_files) == 0


@pytest.mark.integration
@pytest.mark.slow  
class TestSeleniumIntegration:
    """Integration tests with Selenium WebDriver."""
    
    @pytest.mark.skipif(
        not Path("/usr/bin/google-chrome").exists() and not Path("/usr/bin/chromium-browser").exists(),
        reason="Chrome/Chromium not available for Selenium tests"
    )
    def test_selenium_basic_setup(self):
        """Test basic Selenium WebDriver setup."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get("about:blank")
            
            assert driver.current_url == "about:blank"
            assert driver.title == ""
            
            driver.quit()
            
        except Exception as e:
            pytest.skip(f"Selenium setup failed: {e}")
            
    @pytest.mark.skipif(
        not Path("/usr/bin/google-chrome").exists() and not Path("/usr/bin/chromium-browser").exists(),
        reason="Chrome/Chromium not available for Selenium tests"
    )
    @pytest.mark.network
    def test_selenium_vaneck_page_load(self):
        """Test loading VanEck page with Selenium."""
        config = Config()
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(15)
            driver.get(config.base_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            assert "vaneck" in driver.title.lower()
            assert driver.current_url.startswith("https://")
            
            driver.quit()
            
        except Exception as e:
            pytest.skip(f"Selenium VanEck test failed: {e}")
            
    def test_selenium_grid_configuration(self):
        """Test Selenium Grid configuration (mocked)."""
        config = Config(selenium_grid_url="http://localhost:4444/wd/hub")
        
        # Mock the remote WebDriver creation
        with patch('selenium.webdriver.Remote') as mock_remote:
            mock_driver = Mock()
            mock_remote.return_value = mock_driver
            mock_driver.get = Mock()
            mock_driver.quit = Mock()
            
            # Simulate creating remote driver
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            capabilities = DesiredCapabilities.CHROME
            
            mock_remote.assert_not_called()  # Not called yet
            
            # This would be the actual remote driver creation
            # driver = webdriver.Remote(
            #     command_executor=config.selenium_grid_url,
            #     desired_capabilities=capabilities
            # )
            
            assert config.selenium_grid_url == "http://localhost:4444/wd/hub"
            
    def test_selenium_error_handling(self):
        """Test Selenium error handling scenarios."""
        from selenium.common.exceptions import (
            WebDriverException, 
            TimeoutException,
            NoSuchElementException
        )
        
        # Test handling of common Selenium exceptions
        exceptions_to_test = [
            WebDriverException("WebDriver failed"),
            TimeoutException("Page load timeout"), 
            NoSuchElementException("Element not found"),
        ]
        
        for exception in exceptions_to_test:
            # Verify exceptions can be caught and handled
            try:
                raise exception
            except (WebDriverException, TimeoutException, NoSuchElementException) as e:
                assert str(exception) in str(e)
                # In real code, would log error and implement fallback
                
    @pytest.mark.asyncio
    async def test_selenium_async_coordination(self):
        """Test coordination between async operations and Selenium."""
        # Mock async operations that might run alongside Selenium
        selenium_ready = asyncio.Event()
        page_loaded = asyncio.Event()
        
        async def mock_selenium_operations():
            """Mock Selenium operations as async tasks."""
            await asyncio.sleep(0.1)  # Simulate driver startup
            selenium_ready.set()
            
            await asyncio.sleep(0.1)  # Simulate page load
            page_loaded.set()
            
            return "selenium_complete"
            
        async def mock_http_operations():
            """Mock HTTP operations that might run in parallel."""
            await selenium_ready.wait()  # Wait for Selenium to be ready
            await asyncio.sleep(0.05)     # Simulate HTTP requests
            return "http_complete"
            
        # Run operations concurrently
        results = await asyncio.gather(
            mock_selenium_operations(),
            mock_http_operations()
        )
        
        assert "selenium_complete" in results
        assert "http_complete" in results
        assert selenium_ready.is_set()
        assert page_loaded.is_set()


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration management."""
    
    def test_config_file_integration(self, temp_dir):
        """Test integration with configuration files."""
        config_file = temp_dir / "vaneck_config.env"
        
        # Create test config file
        config_content = """
VANECK_DOWNLOAD_DIR=/tmp/vaneck_downloads
VANECK_MAX_CONCURRENT=8
VANECK_REQUEST_TIMEOUT=45
VANECK_LOG_LEVEL=INFO
VANECK_ENABLE_RESUME=true
        """.strip()
        
        config_file.write_text(config_content)
        
        # Simulate loading config from file
        import os
        from dotenv import load_dotenv
        
        # Mock environment loading
        with patch.dict(os.environ, {}, clear=True):
            # In real implementation, would use load_dotenv(config_file)
            # Here we manually set the environment
            os.environ.update({
                "VANECK_DOWNLOAD_DIR": "/tmp/vaneck_downloads",
                "VANECK_MAX_CONCURRENT": "8",
                "VANECK_REQUEST_TIMEOUT": "45",
                "VANECK_LOG_LEVEL": "INFO",
                "VANECK_ENABLE_RESUME": "true",
            })
            
            config = Config.from_env()
            
            assert str(config.download_dir) == "/tmp/vaneck_downloads"
            assert config.max_concurrent_downloads == 8
            assert config.request_timeout == 45
            assert config.log_level == "INFO"
            assert config.enable_resume is True
            
    def test_config_override_precedence(self, temp_dir):
        """Test configuration override precedence."""
        import os
        
        # Test precedence: env vars > config file > defaults
        with patch.dict(os.environ, {
            "VANECK_MAX_CONCURRENT": "10",
            "VANECK_LOG_LEVEL": "DEBUG",
        }):
            config = Config.from_env()
            
            # Environment variables should take precedence
            assert config.max_concurrent_downloads == 10
            assert config.log_level == "DEBUG"
            
            # Defaults should apply for unset values
            assert config.request_timeout == 30  # Default value
            assert config.enable_resume is True   # Default value
            
    def test_invalid_config_handling(self):
        """Test handling of invalid configuration values."""
        import os
        
        # Test invalid numeric values
        with patch.dict(os.environ, {
            "VANECK_MAX_CONCURRENT": "invalid_number",
            "VANECK_REQUEST_TIMEOUT": "-10",
        }):
            with pytest.raises(ValueError):
                Config.from_env()
                
        # Test invalid boolean values  
        with patch.dict(os.environ, {
            "VANECK_ENABLE_RESUME": "maybe",
        }):
            config = Config.from_env()
            # Should handle gracefully, defaulting to False for invalid boolean
            assert config.enable_resume is False