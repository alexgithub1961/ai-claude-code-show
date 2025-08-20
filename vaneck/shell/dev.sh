#!/bin/bash
# Development setup script for VanEck ETF Downloader

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

echo "Setting up development environment..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file to configure your settings."
fi

# Run static analysis
echo "Running static analysis..."

# Format code
echo "Formatting code with black..."
black src/ tests/ --line-length 88

echo "Sorting imports with isort..."
isort src/ tests/ --profile black

# Lint code
echo "Linting with ruff..."
ruff check src/ tests/ --fix

echo "Type checking with mypy..."
mypy src/vaneck_downloader/

# Run tests
echo "Running tests..."
pytest tests/ -v --cov=src/vaneck_downloader --cov-report=html --cov-report=term

echo ""
echo "Development environment setup complete!"
echo "To activate the environment: source venv/bin/activate"
echo "To run the downloader: python src/etf_downloader.py"
echo "To run tests: pytest"
echo "Coverage report available at: htmlcov/index.html"