"""Unit tests for configuration management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from vaneck_downloader.config import Config


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = Config()
        
        assert config.base_url == "https://www.vaneck.com"
        assert config.max_concurrent_downloads == 5
        assert config.request_timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.rate_limit_delay == 1.0
        assert config.enable_resume is True
        assert config.browser_headless is True
        assert config.chunk_size == 8192
        assert config.log_level == "INFO"
        
    def test_default_download_extensions(self):
        """Test default file extensions for downloads."""
        config = Config()
        
        expected_extensions = [".pdf", ".xlsx", ".csv", ".json", ".xml"]
        assert config.download_extensions == expected_extensions
        
    def test_default_user_agent(self):
        """Test default user agent string."""
        config = Config()
        
        assert "Mozilla/5.0" in config.user_agent
        assert "Chrome" in config.user_agent
        assert "Safari" in config.user_agent
        
    def test_default_urls(self):
        """Test default URL configurations."""
        config = Config()
        
        assert config.base_url == "https://www.vaneck.com"
        assert "etf-mutual-fund-finder" in config.etf_finder_url
        assert config.etf_finder_url.startswith(config.base_url)


class TestConfigValidation:
    """Test configuration validation."""

    def test_valid_log_levels(self):
        """Test validation of log levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            config = Config(log_level=level)
            assert config.log_level == level
            
        for level in valid_levels:
            config = Config(log_level=level.lower())
            assert config.log_level == level.upper()
            
    def test_invalid_log_level(self):
        """Test validation fails for invalid log levels."""
        with pytest.raises(ValueError, match="Log level must be one of"):
            Config(log_level="INVALID")
            
    def test_negative_concurrent_downloads(self):
        """Test validation of concurrent downloads."""
        with pytest.raises(ValueError):
            Config(max_concurrent_downloads=-1)
            
    def test_negative_timeout(self):
        """Test validation of timeout values."""
        with pytest.raises(ValueError):
            Config(request_timeout=-10)
            
    def test_negative_retries(self):
        """Test validation of retry values.""" 
        with pytest.raises(ValueError):
            Config(max_retries=-1)


class TestDownloadDirectoryHandling:
    """Test download directory creation and validation."""

    def test_directory_creation_from_string(self, tmp_path):
        """Test directory creation from string path."""
        download_dir = str(tmp_path / "new_download_dir")
        config = Config(download_dir=download_dir)
        
        assert config.download_dir.exists()
        assert config.download_dir.is_dir()
        assert str(config.download_dir) == download_dir
        
    def test_directory_creation_from_path(self, tmp_path):
        """Test directory creation from Path object."""
        download_dir = tmp_path / "another_download_dir"
        config = Config(download_dir=download_dir)
        
        assert config.download_dir.exists()
        assert config.download_dir.is_dir()
        assert config.download_dir == download_dir
        
    def test_existing_directory_handling(self, tmp_path):
        """Test handling of existing directories."""
        download_dir = tmp_path / "existing_dir"
        download_dir.mkdir()
        
        # Create a file in the directory to verify it's not overwritten
        test_file = download_dir / "test.txt"
        test_file.write_text("test content")
        
        config = Config(download_dir=download_dir)
        
        assert config.download_dir.exists()
        assert test_file.exists()
        assert test_file.read_text() == "test content"
        
    def test_nested_directory_creation(self, tmp_path):
        """Test creation of nested directories."""
        nested_dir = tmp_path / "level1" / "level2" / "downloads"
        config = Config(download_dir=nested_dir)
        
        assert config.download_dir.exists()
        assert config.download_dir.is_dir()
        assert config.download_dir.name == "downloads"


class TestEnvironmentConfiguration:
    """Test configuration from environment variables."""

    def test_from_env_basic(self):
        """Test basic environment variable loading."""
        env_vars = {
            "VANECK_DOWNLOAD_DIR": "/tmp/test_downloads",
            "VANECK_MAX_CONCURRENT": "8",
            "VANECK_REQUEST_TIMEOUT": "45",
            "VANECK_MAX_RETRIES": "5",
            "VANECK_RATE_LIMIT": "0.5",
            "VANECK_LOG_LEVEL": "debug",
            "VANECK_ENABLE_RESUME": "false",
            "VANECK_HEADLESS": "false",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config.from_env()
            
            assert str(config.download_dir) == "/tmp/test_downloads"
            assert config.max_concurrent_downloads == 8
            assert config.request_timeout == 45
            assert config.max_retries == 5
            assert config.rate_limit_delay == 0.5
            assert config.log_level == "DEBUG"
            assert config.enable_resume is False
            assert config.browser_headless is False
            
    def test_from_env_with_selenium_grid(self):
        """Test environment loading with Selenium Grid URL."""
        env_vars = {
            "SELENIUM_GRID_URL": "http://selenium-hub:4444/wd/hub",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config.from_env()
            assert config.selenium_grid_url == "http://selenium-hub:4444/wd/hub"
            
    def test_from_env_partial_override(self):
        """Test partial environment override with defaults."""
        env_vars = {
            "VANECK_MAX_CONCURRENT": "10",
            "VANECK_LOG_LEVEL": "ERROR",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config.from_env()
            
            # Overridden values
            assert config.max_concurrent_downloads == 10
            assert config.log_level == "ERROR"
            
            # Default values should remain
            assert config.request_timeout == 30
            assert config.max_retries == 3
            assert config.enable_resume is True
            
    def test_from_env_boolean_parsing(self):
        """Test boolean parsing from environment variables."""
        boolean_test_cases = [
            ("true", True),
            ("TRUE", True), 
            ("True", True),
            ("1", True),
            ("false", False),
            ("FALSE", False),
            ("False", False),
            ("0", False),
            ("", False),
            ("invalid", False),
        ]
        
        for env_value, expected in boolean_test_cases:
            env_vars = {"VANECK_ENABLE_RESUME": env_value}
            
            with patch.dict(os.environ, env_vars):
                config = Config.from_env()
                assert config.enable_resume == expected, f"Failed for env_value: {env_value}"
                
    def test_from_env_invalid_numeric_values(self):
        """Test handling of invalid numeric environment values."""
        invalid_cases = [
            ("VANECK_MAX_CONCURRENT", "not_a_number"),
            ("VANECK_REQUEST_TIMEOUT", "invalid"),
            ("VANECK_MAX_RETRIES", "text"),
            ("VANECK_RATE_LIMIT", "not_float"),
        ]
        
        for env_var, invalid_value in invalid_cases:
            env_vars = {env_var: invalid_value}
            
            with patch.dict(os.environ, env_vars):
                with pytest.raises(ValueError):
                    Config.from_env()
                    
    def test_from_env_empty_values(self):
        """Test handling of empty environment variable values."""
        env_vars = {
            "VANECK_DOWNLOAD_DIR": "",
            "VANECK_MAX_CONCURRENT": "",
            "VANECK_LOG_LEVEL": "",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config.from_env()
            
            # Should fall back to defaults for empty values
            assert str(config.download_dir) == "./download"
            assert config.max_concurrent_downloads == 5
            assert config.log_level == "INFO"


class TestConfigurationSerialization:
    """Test configuration serialization and representation."""

    def test_config_dict_conversion(self):
        """Test converting config to dictionary."""
        config = Config(
            max_concurrent_downloads=3,
            log_level="DEBUG",
            enable_resume=False
        )
        
        config_dict = config.model_dump()
        
        assert config_dict["max_concurrent_downloads"] == 3
        assert config_dict["log_level"] == "DEBUG"
        assert config_dict["enable_resume"] is False
        assert "base_url" in config_dict
        assert "download_extensions" in config_dict
        
    def test_config_json_serialization(self):
        """Test JSON serialization of config."""
        config = Config(max_concurrent_downloads=7)
        
        json_str = config.model_dump_json()
        
        assert '"max_concurrent_downloads":7' in json_str
        assert '"base_url":"https://www.vaneck.com"' in json_str
        
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_data = {
            "max_concurrent_downloads": 6,
            "log_level": "WARNING", 
            "request_timeout": 60,
            "enable_resume": False,
        }
        
        config = Config(**config_data)
        
        assert config.max_concurrent_downloads == 6
        assert config.log_level == "WARNING"
        assert config.request_timeout == 60
        assert config.enable_resume is False
        
    def test_config_partial_dict(self):
        """Test creating config from partial dictionary."""
        config_data = {
            "max_concurrent_downloads": 4,
        }
        
        config = Config(**config_data)
        
        # Specified value
        assert config.max_concurrent_downloads == 4
        
        # Default values should still be present
        assert config.request_timeout == 30
        assert config.log_level == "INFO"
        assert config.enable_resume is True


class TestConfigurationEdgeCases:
    """Test edge cases and error conditions."""

    def test_very_large_concurrent_downloads(self):
        """Test handling of very large concurrent download values."""
        config = Config(max_concurrent_downloads=1000)
        assert config.max_concurrent_downloads == 1000
        
    def test_very_small_timeouts(self):
        """Test handling of very small timeout values."""
        config = Config(request_timeout=1)
        assert config.request_timeout == 1
        
    def test_zero_retries(self):
        """Test handling of zero retries."""
        config = Config(max_retries=0)
        assert config.max_retries == 0
        
    def test_empty_download_extensions(self):
        """Test handling of empty download extensions list."""
        config = Config(download_extensions=[])
        assert config.download_extensions == []
        
    def test_custom_user_agent(self):
        """Test custom user agent configuration."""
        custom_ua = "Custom-VanEck-Bot/1.0"
        config = Config(user_agent=custom_ua)
        assert config.user_agent == custom_ua
        
    def test_path_with_spaces(self, tmp_path):
        """Test handling of paths with spaces."""
        space_dir = tmp_path / "directory with spaces"
        config = Config(download_dir=space_dir)
        
        assert config.download_dir.exists()
        assert " " in str(config.download_dir)
        
    def test_unicode_path(self, tmp_path):
        """Test handling of Unicode characters in paths."""
        unicode_dir = tmp_path / "测试目录"  # Chinese characters
        config = Config(download_dir=unicode_dir)
        
        assert config.download_dir.exists()
        
    def test_very_long_path(self, tmp_path):
        """Test handling of very long paths."""
        # Create a reasonably long path
        long_segments = ["very"] * 20
        long_path = tmp_path
        for segment in long_segments:
            long_path = long_path / segment
            
        config = Config(download_dir=long_path)
        assert config.download_dir.exists()


class TestConfigurationIntegration:
    """Test configuration integration with other components."""

    def test_config_with_pydantic_validation(self):
        """Test Pydantic validation features."""
        # Test that Pydantic validation works
        with pytest.raises(ValueError):
            Config(max_concurrent_downloads="not_an_int")  # type: ignore
            
    def test_config_inheritance(self):
        """Test configuration inheritance patterns."""
        base_config = Config(max_concurrent_downloads=5)
        
        # Create derived configuration
        derived_config = Config(
            **base_config.model_dump(),
            log_level="DEBUG"
        )
        
        assert derived_config.max_concurrent_downloads == 5
        assert derived_config.log_level == "DEBUG"
        
    def test_config_environment_precedence(self, tmp_path):
        """Test precedence between different configuration sources."""
        # Create config file content
        config_file = tmp_path / ".env"
        config_file.write_text("VANECK_MAX_CONCURRENT=8\n")
        
        # Environment variable should take precedence
        with patch.dict(os.environ, {"VANECK_MAX_CONCURRENT": "10"}):
            config = Config.from_env()
            assert config.max_concurrent_downloads == 10
            
    def test_config_validation_ordering(self):
        """Test that validation occurs in the correct order."""
        # This should fail validation before directory creation
        with pytest.raises(ValueError, match="Log level must be one of"):
            Config(
                log_level="INVALID",
                download_dir="/tmp/should_not_be_created"
            )