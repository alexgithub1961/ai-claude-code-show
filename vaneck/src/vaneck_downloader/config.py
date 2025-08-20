"""Configuration management for VanEck ETF downloader."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Application configuration."""

    # Base URLs
    base_url: str = "https://www.vaneck.com"
    etf_finder_url: str = (
        "https://www.vaneck.com/us/en/etf-mutual-fund-finder/"
        "?InvType=etf&AssetClass=c,nr,t,cb,ei,ib,mb,fr,c-ra,c-da,c-g"
        "&Funds=emf,grf,iigf,mwmf,embf,ccif&ShareClass=a,c,i,y,z"
        "&tab=ov&Sort=name&SortDesc=true"
    )

    # Storage configuration
    download_dir: Path = Field(default_factory=lambda: Path("./download"))
    max_concurrent_downloads: int = 5
    
    # Request configuration
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_delay: float = 1.0
    
    # User agent for web requests
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # File types to download
    download_extensions: list[str] = Field(
        default_factory=lambda: [".pdf", ".xlsx", ".csv", ".json", ".xml"]
    )
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Resume capability
    enable_resume: bool = True
    chunk_size: int = 8192
    
    # Browser automation (Selenium fallback)
    browser_headless: bool = True
    browser_timeout: int = 30
    selenium_grid_url: Optional[str] = None

    @field_validator("download_dir", mode='before')
    @classmethod
    def ensure_download_dir_exists(cls, v: Path) -> Path:
        """Ensure download directory exists."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            download_dir=Path(os.getenv("VANECK_DOWNLOAD_DIR", "./download")),
            max_concurrent_downloads=int(
                os.getenv("VANECK_MAX_CONCURRENT", "5")
            ),
            request_timeout=int(os.getenv("VANECK_REQUEST_TIMEOUT", "30")),
            max_retries=int(os.getenv("VANECK_MAX_RETRIES", "3")),
            rate_limit_delay=float(os.getenv("VANECK_RATE_LIMIT", "1.0")),
            log_level=os.getenv("VANECK_LOG_LEVEL", "INFO"),
            enable_resume=os.getenv("VANECK_ENABLE_RESUME", "true").lower()
            == "true",
            browser_headless=os.getenv("VANECK_HEADLESS", "true").lower()
            == "true",
            selenium_grid_url=os.getenv("SELENIUM_GRID_URL"),
        )

    model_config = {
        "env_prefix": "VANECK_",
        "case_sensitive": False
    }