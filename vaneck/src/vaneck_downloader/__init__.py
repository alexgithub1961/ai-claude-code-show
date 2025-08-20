"""VanEck ETF Data Downloader

A robust system for downloading ETF data from VanEck's website.
"""

__version__ = "0.1.0"
__author__ = "VanEck ETF Downloader Team"
__email__ = "dev@example.com"

from .config import Config
from .downloader import ETFDownloader
from .scraper import VanEckScraper
from .storage import StorageManager

__all__ = ["Config", "ETFDownloader", "VanEckScraper", "StorageManager"]