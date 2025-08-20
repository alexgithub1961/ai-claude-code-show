"""
Health Check Utility

This module provides health check functionality for the ETF downloader
application, used by Docker health checks and monitoring systems.

Functions:
    check_health(): Performs comprehensive health check
    check_api_connectivity(): Tests API endpoint connectivity
    check_storage(): Validates storage system accessibility
    get_health_status(): Returns detailed health status information

Example:
    >>> from src.utils.health import check_health
    >>> is_healthy = check_health()
    >>> print(f"Application healthy: {is_healthy}")

Author: VanEck Data Team
"""

import os
import sys
import logging
from typing import Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

try:
    import httpx
    import yaml
    from ..utils.config import Config
except ImportError as e:
    # Fallback for health checks when some dependencies might not be available
    print(f"Warning: Some dependencies not available for health check: {e}")
    httpx = None
    yaml = None
    Config = None


def check_health() -> bool:
    """
    Perform a comprehensive health check of the application.
    
    This function checks various aspects of the application:
    - Configuration validity
    - Storage accessibility
    - Import capability
    - Basic system resources
    
    Returns:
        bool: True if all health checks pass, False otherwise
        
    Example:
        >>> if check_health():
        ...     print("Application is healthy")
        ... else:
        ...     print("Application has health issues")
    """
    try:
        # Check if we can import core modules
        if not _check_imports():
            return False
        
        # Check configuration
        if not _check_configuration():
            return False
        
        # Check storage accessibility
        if not _check_storage():
            return False
        
        # Check system resources
        if not _check_system_resources():
            return False
        
        return True
        
    except Exception as e:
        print(f"Health check failed with exception: {e}")
        return False


def _check_imports() -> bool:
    """
    Check if core application modules can be imported.
    
    Returns:
        bool: True if all imports successful, False otherwise
    """
    try:
        # Test critical imports
        import asyncio
        import json
        from decimal import Decimal
        from datetime import datetime
        
        # Test application-specific imports if available
        try:
            sys.path.insert(0, '/app')
            from src.downloader.core import ETFDownloader
            from src.utils.exceptions import ETFDownloaderError
        except ImportError:
            # This is acceptable in some deployment scenarios
            pass
        
        return True
        
    except ImportError as e:
        print(f"Import check failed: {e}")
        return False


def _check_configuration() -> bool:
    """
    Check if configuration file exists and is valid.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    try:
        config_file = os.environ.get('CONFIG_FILE', '/app/config/config.yaml')
        
        if not os.path.exists(config_file):
            print(f"Configuration file not found: {config_file}")
            return False
        
        # Try to parse the configuration
        if yaml is None:
            print("YAML parser not available, skipping configuration validation")
            return True
            
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Basic configuration validation
        if not isinstance(config_data, dict):
            print("Configuration is not a valid dictionary")
            return False
        
        # Check for required sections
        required_sections = ['data_sources', 'output']
        for section in required_sections:
            if section not in config_data:
                print(f"Missing required configuration section: {section}")
                return False
        
        return True
        
    except Exception as e:
        print(f"Configuration check failed: {e}")
        return False


def _check_storage() -> bool:
    """
    Check if storage directories are accessible.
    
    Returns:
        bool: True if storage is accessible, False otherwise
    """
    try:
        data_dir = os.environ.get('DATA_DIR', '/app/data')
        logs_dir = os.path.dirname(os.environ.get('LOG_FILE', '/app/logs/app.log'))
        
        # Check data directory
        data_path = Path(data_dir)
        if not data_path.exists():
            try:
                data_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Cannot create data directory {data_dir}: {e}")
                return False
        
        if not os.access(data_dir, os.W_OK):
            print(f"Data directory is not writable: {data_dir}")
            return False
        
        # Check logs directory
        logs_path = Path(logs_dir)
        if not logs_path.exists():
            try:
                logs_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Cannot create logs directory {logs_dir}: {e}")
                return False
        
        if not os.access(logs_dir, os.W_OK):
            print(f"Logs directory is not writable: {logs_dir}")
            return False
        
        # Test write capability
        test_file = data_path / 'health_check_test'
        try:
            test_file.write_text('test')
            test_file.unlink()
        except Exception as e:
            print(f"Cannot write to data directory: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Storage check failed: {e}")
        return False


def _check_system_resources() -> bool:
    """
    Check basic system resources and constraints.
    
    Returns:
        bool: True if system resources are adequate, False otherwise
    """
    try:
        # Check available disk space
        data_dir = os.environ.get('DATA_DIR', '/app/data')
        stat = os.statvfs(data_dir)
        free_bytes = stat.f_frsize * stat.f_available
        free_mb = free_bytes / (1024 * 1024)
        
        # Require at least 100MB free space
        if free_mb < 100:
            print(f"Low disk space: {free_mb:.1f}MB available")
            return False
        
        # Check if we can create processes (basic async functionality test)
        try:
            import asyncio
            
            async def test_async():
                await asyncio.sleep(0.001)
                return True
            
            # Run a simple async test
            result = asyncio.run(test_async())
            if not result:
                print("Async functionality test failed")
                return False
                
        except Exception as e:
            print(f"Async functionality check failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"System resources check failed: {e}")
        return False


def check_api_connectivity() -> bool:
    """
    Test connectivity to configured API endpoints.
    
    Returns:
        bool: True if at least one API endpoint is reachable, False otherwise
    """
    if httpx is None:
        print("HTTP client not available, skipping API connectivity check")
        return True
    
    try:
        # Test basic internet connectivity
        test_urls = [
            'https://httpbin.org/status/200',
            'https://www.google.com',
            'https://api.github.com'
        ]
        
        with httpx.Client(timeout=5.0) as client:
            for url in test_urls:
                try:
                    response = client.get(url)
                    if response.status_code == 200:
                        return True
                except Exception:
                    continue
        
        print("No API endpoints are reachable")
        return False
        
    except Exception as e:
        print(f"API connectivity check failed: {e}")
        return False


def get_health_status() -> Dict[str, Any]:
    """
    Get detailed health status information.
    
    Returns:
        Dict[str, Any]: Detailed health status including:
            - overall_health: Boolean overall health status
            - timestamp: When the check was performed
            - checks: Individual check results
            - system_info: Basic system information
    
    Example:
        >>> status = get_health_status()
        >>> print(f"Health: {status['overall_health']}")
        >>> print(f"Checks: {status['checks']}")
    """
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Perform individual checks
    checks = {
        'imports': _check_imports(),
        'configuration': _check_configuration(),
        'storage': _check_storage(),
        'system_resources': _check_system_resources(),
        'api_connectivity': check_api_connectivity()
    }
    
    # Overall health
    overall_health = all(checks.values())
    
    # System information
    system_info = {
        'python_version': sys.version,
        'platform': sys.platform,
        'data_dir': os.environ.get('DATA_DIR', '/app/data'),
        'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
        'config_file': os.environ.get('CONFIG_FILE', '/app/config/config.yaml')
    }
    
    return {
        'overall_health': overall_health,
        'timestamp': timestamp,
        'checks': checks,
        'system_info': system_info
    }


if __name__ == '__main__':
    """
    Command-line interface for health checks.
    
    Usage:
        python -m src.utils.health           # Basic health check
        python -m src.utils.health --detailed  # Detailed health status
    """
    import sys
    
    if '--detailed' in sys.argv:
        status = get_health_status()
        import json
        print(json.dumps(status, indent=2))
        sys.exit(0 if status['overall_health'] else 1)
    else:
        is_healthy = check_health()
        print(f"Health check: {'PASS' if is_healthy else 'FAIL'}")
        sys.exit(0 if is_healthy else 1)