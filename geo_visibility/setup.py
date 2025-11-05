"""
Setup configuration for GEO Visibility Assessment Tool.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="geo-visibility-assessment",
    version="1.0.0",
    description="GEO visibility assessment tool for First Line Software",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="First Line Software",
    author_email="info@firstlinesoftware.com",
    url="https://github.com/firstlinesoftware/geo-visibility-assessment",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.25.2",
        "pydantic>=2.5.0",
        "pyyaml>=6.0.1",
        "openai>=1.7.0",
        "anthropic>=0.8.0",
        "pandas>=2.1.4",
        "numpy>=1.25.2",
        "python-dateutil>=2.8.2",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "html5lib>=1.1",
        "markdown>=3.5.1",
        "aiofiles>=23.2.1",
        "structlog>=23.2.0",
        "click>=8.1.7",
        "tqdm>=4.66.1",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "python-dotenv>=1.0.0",
        "matplotlib>=3.8.2",
        "seaborn>=0.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "geo-assess=src.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
