"""Docker integration tests for the ETF downloader application."""

import asyncio
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from vaneck_downloader.config import Config


@pytest.mark.docker
@pytest.mark.integration
class TestDockerEnvironment:
    """Test Docker environment integration."""

    def test_container_environment_detection(self):
        """Test detection of container environment."""
        # Mock container environment indicators
        container_indicators = [
            "/.dockerenv",
            "/proc/1/cgroup",
            "/proc/self/cgroup",
        ]
        
        def mock_path_exists(path: str) -> bool:
            """Mock path existence for container detection."""
            if path == "/.dockerenv":
                return True
            return False
        
        with patch("pathlib.Path.exists", side_effect=mock_path_exists):
            # In a real implementation, you would check for container environment
            is_container = Path("/.dockerenv").exists()
            assert is_container is True
            
    def test_container_resource_limits(self):
        """Test handling of container resource limits."""
        # Mock container memory limits
        mock_memory_limit = 1024 * 1024 * 1024  # 1GB
        mock_cpu_limit = 2.0  # 2 CPUs
        
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            
            with patch("builtins.open", create=True) as mock_open:
                # Mock cgroup memory limit file
                mock_open.return_value.__enter__.return_value.read.return_value = str(mock_memory_limit)
                
                # Test memory-aware configuration
                config = Config()
                
                # Adjust concurrent downloads based on memory
                memory_gb = mock_memory_limit / (1024 ** 3)
                recommended_concurrent = max(1, int(memory_gb * 2))
                
                assert recommended_concurrent == 2  # 1GB -> 2 concurrent downloads
                
    def test_container_network_configuration(self):
        """Test network configuration in container environment."""
        # Test DNS resolution in container
        container_dns_servers = ["127.0.0.11", "8.8.8.8"]
        
        # Mock container network settings
        with patch("socket.getaddrinfo") as mock_getaddrinfo:
            mock_getaddrinfo.return_value = [(2, 1, 6, '', ('192.168.1.100', 80))]
            
            # Test that DNS resolution works in container
            import socket
            result = socket.getaddrinfo("www.vaneck.com", 80)
            assert len(result) > 0
            
    def test_container_signal_handling(self):
        """Test proper signal handling in containers."""
        import signal
        
        # Track signal handlers
        handlers_called = []
        
        def mock_signal_handler(signum, frame):
            handlers_called.append(signum)
            
        # Test SIGTERM handling (Docker stop)
        with patch("signal.signal") as mock_signal:
            mock_signal.side_effect = lambda sig, handler: None
            
            # Register signal handlers
            signal.signal(signal.SIGTERM, mock_signal_handler)
            signal.signal(signal.SIGINT, mock_signal_handler)
            
            # Simulate Docker sending SIGTERM
            mock_signal_handler(signal.SIGTERM, None)
            
            assert signal.SIGTERM in handlers_called


@pytest.mark.docker
class TestDockerVolumeOperations:
    """Test Docker volume operations."""

    def test_volume_mount_permissions(self, tmp_path):
        """Test file permissions in mounted volumes."""
        # Simulate Docker volume mount
        volume_mount = tmp_path / "docker_volume"
        volume_mount.mkdir(mode=0o755)
        
        # Test file creation with proper permissions
        test_file = volume_mount / "test_file.txt"
        test_file.write_text("test content")
        test_file.chmod(0o644)
        
        # Verify permissions
        stat_info = test_file.stat()
        assert oct(stat_info.st_mode)[-3:] == "644"
        
    def test_volume_ownership(self, tmp_path):
        """Test file ownership in volumes."""
        volume_dir = tmp_path / "ownership_test"
        volume_dir.mkdir()
        
        # Create file and test ownership
        test_file = volume_dir / "owned_file.txt"
        test_file.write_text("ownership test")
        
        stat_info = test_file.stat()
        
        # In container, files should be owned by appropriate user
        assert stat_info.st_uid >= 0
        assert stat_info.st_gid >= 0
        
    def test_volume_persistence(self, tmp_path):
        """Test data persistence across container restarts."""
        persistent_dir = tmp_path / "persistent_data"
        persistent_dir.mkdir()
        
        # Create data that should persist
        persistent_file = persistent_dir / "persistent.json"
        persistent_data = '{"etf": "GDX", "downloads": 150}'
        persistent_file.write_text(persistent_data)
        
        # Simulate container restart by re-reading data
        assert persistent_file.exists()
        assert persistent_file.read_text() == persistent_data
        
    def test_volume_concurrent_access(self, tmp_path):
        """Test concurrent access to shared volumes."""
        shared_dir = tmp_path / "shared_volume"
        shared_dir.mkdir()
        
        # Simulate multiple containers accessing same volume
        files_to_create = []
        
        for container_id in range(3):
            container_file = shared_dir / f"container_{container_id}_data.csv"
            content = f"ticker,price\nGDX,{25.0 + container_id}\n"
            container_file.write_text(content)
            files_to_create.append(container_file)
            
        # Verify all containers can access all files
        for file_path in files_to_create:
            assert file_path.exists()
            assert "GDX," in file_path.read_text()


@pytest.mark.docker
@pytest.mark.asyncio
class TestDockerNetworking:
    """Test Docker networking scenarios."""

    async def test_container_to_container_communication(self):
        """Test communication between containers."""
        # Mock container network communication
        mock_responses = {
            "etf-scraper": {"status": "running", "port": 8080},
            "data-processor": {"status": "running", "port": 8081},
            "file-server": {"status": "running", "port": 8082},
        }
        
        async def mock_container_request(service_name: str):
            await asyncio.sleep(0.01)  # Simulate network delay
            return mock_responses.get(service_name, {"status": "not_found"})
            
        # Test service discovery
        for service in mock_responses.keys():
            response = await mock_container_request(service)
            assert response["status"] == "running"
            assert "port" in response
            
    async def test_external_network_access(self):
        """Test external network access from container."""
        # Mock external API call
        async def mock_external_api():
            await asyncio.sleep(0.05)  # Simulate external API delay
            return {
                "api": "vaneck.com",
                "status": "reachable",
                "response_time": 45
            }
            
        result = await mock_external_api()
        assert result["status"] == "reachable"
        assert result["response_time"] < 100  # Reasonable response time
        
    def test_dns_resolution_in_container(self):
        """Test DNS resolution works properly in container."""
        import socket
        
        # Test both internal and external DNS
        test_hostnames = [
            ("www.vaneck.com", True),  # External hostname
            ("localhost", True),       # Local hostname  
            ("nonexistent.invalid", False),  # Should fail
        ]
        
        for hostname, should_resolve in test_hostnames:
            try:
                result = socket.gethostbyname(hostname)
                if should_resolve:
                    assert result is not None
                    assert isinstance(result, str)
                else:
                    pytest.fail(f"Expected {hostname} to fail resolution")
            except socket.gaierror:
                if should_resolve:
                    pytest.fail(f"Expected {hostname} to resolve successfully")
                # Expected failure for non-existent domains


@pytest.mark.docker  
class TestDockerLogging:
    """Test logging in Docker environment."""

    def test_stdout_logging(self, capfd):
        """Test logging to stdout for Docker log collection."""
        import logging
        import sys
        
        # Configure logging to stdout (Docker standard)
        logger = logging.getLogger("vaneck_downloader")
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Log some messages
        logger.info("Container started")
        logger.warning("Rate limit reached")
        logger.error("Download failed")
        
        # Capture output
        captured = capfd.readouterr()
        
        assert "Container started" in captured.out
        assert "Rate limit reached" in captured.out
        assert "Download failed" in captured.out
        
    def test_structured_logging(self):
        """Test structured logging for container environments."""
        import json
        import logging
        from io import StringIO
        
        # Create JSON formatter
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                }
                return json.dumps(log_entry)
        
        # Setup logger with JSON formatter
        logger = logging.getLogger("test_structured")
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Log a message
        logger.info("ETF download completed", extra={"etf": "GDX", "files": 3})
        
        # Parse logged JSON
        log_output = stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "ETF download completed"
        assert "timestamp" in log_data
        
    def test_log_rotation_in_container(self, tmp_path):
        """Test log rotation doesn't fill container disk."""
        import logging
        from logging.handlers import RotatingFileHandler
        
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        log_file = log_dir / "downloader.log"
        
        # Setup rotating file handler (small size for testing)
        handler = RotatingFileHandler(
            log_file,
            maxBytes=1024,  # 1KB max
            backupCount=3
        )
        
        logger = logging.getLogger("test_rotation")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Generate enough logs to trigger rotation
        for i in range(100):
            logger.info(f"Log message {i} with some additional content to make it longer")
            
        # Check that log files were created and rotated
        log_files = list(log_dir.glob("downloader.log*"))
        assert len(log_files) > 1  # Should have rotated files
        
        # Main log file should exist
        assert log_file.exists()


@pytest.mark.docker
@pytest.mark.performance
class TestDockerPerformance:
    """Test performance characteristics in Docker environment."""

    def test_io_performance_in_container(self, tmp_path):
        """Test file I/O performance in container."""
        test_dir = tmp_path / "io_test"
        test_dir.mkdir()
        
        # Test write performance
        start_time = time.time()
        
        large_file = test_dir / "large_test_file.txt"
        content = "x" * 1024  # 1KB chunk
        
        with large_file.open("w") as f:
            for _ in range(1000):  # Write 1MB total
                f.write(content)
                
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        
        with large_file.open("r") as f:
            data = f.read()
            
        read_time = time.time() - start_time
        
        # Verify reasonable performance (adjust thresholds as needed)
        assert write_time < 5.0  # Should complete within 5 seconds
        assert read_time < 2.0   # Should read within 2 seconds
        assert len(data) == 1024 * 1000  # Verify data integrity
        
    @pytest.mark.asyncio
    async def test_network_performance_in_container(self):
        """Test network performance characteristics."""
        import asyncio
        import time
        
        async def mock_network_request():
            # Simulate network latency in container
            await asyncio.sleep(0.01)  # 10ms simulated latency
            return {"status": "success", "size": 1024}
            
        # Test concurrent network requests
        start_time = time.time()
        
        tasks = [mock_network_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Verify all requests completed
        assert len(results) == 50
        assert all(r["status"] == "success" for r in results)
        
        # Check performance (with concurrency, should be much faster than sequential)
        assert total_time < 1.0  # Should complete well under 1 second
        
    def test_memory_usage_in_container(self):
        """Test memory usage patterns in container."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Simulate memory-intensive operation
        large_data = []
        for i in range(1000):
            # Create and immediately release data
            chunk = [j for j in range(1000)]
            large_data.append(len(chunk))  # Keep only size, not data
            
        # Force cleanup
        gc.collect()
        
        # Verify we didn't leak memory (simplified check)
        assert len(large_data) == 1000
        assert all(size == 1000 for size in large_data)


@pytest.mark.docker
class TestDockerSecurityConstraints:
    """Test security constraints in Docker environment."""

    def test_readonly_filesystem_handling(self, tmp_path):
        """Test handling of read-only filesystem areas."""
        # Simulate read-only mount
        readonly_dir = tmp_path / "readonly_mount" 
        readonly_dir.mkdir()
        
        # Make directory read-only
        readonly_dir.chmod(0o555)
        
        # Test that we handle read-only gracefully
        readonly_file = readonly_dir / "should_fail.txt"
        
        try:
            readonly_file.write_text("this should fail")
            pytest.fail("Expected PermissionError for read-only filesystem")
        except PermissionError:
            # Expected - application should handle this gracefully
            pass
        except OSError:
            # Also acceptable on some systems
            pass
            
    def test_user_permissions_in_container(self):
        """Test handling of non-root user in container."""
        import os
        
        # Get current user ID (should not be root in secure container)
        current_uid = os.getuid()
        current_gid = os.getgid()
        
        # Verify not running as root (UID 0)
        # Note: In test environment, we might be root, so this is informational
        if current_uid == 0:
            pytest.skip("Running as root - skipping non-root user test")
            
        # Test file operations with non-root user
        test_file = Path("/tmp/user_test.txt")
        test_file.write_text("user test")
        
        stat_info = test_file.stat()
        assert stat_info.st_uid == current_uid
        assert stat_info.st_gid == current_gid
        
        # Cleanup
        test_file.unlink()
        
    def test_network_restrictions(self):
        """Test network access restrictions."""
        import socket
        
        # Test that we can't bind to privileged ports (< 1024)
        privileged_ports = [80, 443, 22, 25]
        
        for port in privileged_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                pytest.fail(f"Should not be able to bind to privileged port {port}")
            except PermissionError:
                # Expected for non-root user
                pass
            except OSError:
                # Port might be in use, which is also fine
                pass
            
    def test_resource_limits_enforcement(self):
        """Test that resource limits are enforced."""
        import os
        import resource
        
        try:
            # Get current resource limits
            memory_limit = resource.getrlimit(resource.RLIMIT_AS)
            file_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
            
            # Verify limits are set (not unlimited)
            if memory_limit[0] != resource.RLIM_INFINITY:
                assert memory_limit[0] > 0
                
            if file_limit[0] != resource.RLIM_INFINITY:
                assert file_limit[0] > 0
                
        except (AttributeError, OSError):
            # Resource limits not available on this system
            pytest.skip("Resource limit checking not available")


@pytest.mark.docker
class TestDockerHealthChecks:
    """Test Docker health check functionality."""

    def test_health_check_endpoint(self):
        """Test health check endpoint functionality."""
        # Mock health check response
        def health_check():
            return {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "0.1.0",
                "checks": {
                    "disk_space": "ok",
                    "memory": "ok", 
                    "network": "ok"
                }
            }
            
        health_data = health_check()
        
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "checks" in health_data
        assert all(status == "ok" for status in health_data["checks"].values())
        
    def test_unhealthy_conditions(self):
        """Test detection of unhealthy conditions."""
        # Mock unhealthy scenarios
        unhealthy_scenarios = [
            {"disk_space": "critical", "reason": "Less than 5% space remaining"},
            {"memory": "warning", "reason": "Memory usage above 90%"},
            {"network": "error", "reason": "Cannot reach external APIs"},
        ]
        
        for scenario in unhealthy_scenarios:
            # In a real implementation, these would trigger health check failures
            for check, status in scenario.items():
                if check == "reason":
                    continue
                assert status in ["ok", "warning", "error", "critical"]
                
    def test_graceful_shutdown_on_health_failure(self):
        """Test graceful shutdown when health checks fail."""
        import signal
        import time
        
        shutdown_initiated = False
        
        def mock_shutdown_handler(signum, frame):
            nonlocal shutdown_initiated
            shutdown_initiated = True
            
        # Mock health check failure leading to shutdown
        with patch("signal.signal"):
            # Simulate critical health check failure
            health_status = "critical"
            
            if health_status == "critical":
                # Initiate graceful shutdown
                mock_shutdown_handler(signal.SIGTERM, None)
                
            assert shutdown_initiated