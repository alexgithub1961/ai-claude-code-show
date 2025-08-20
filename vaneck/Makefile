# VanEck ETF Downloader Makefile
# Provides convenient commands for development and testing

.PHONY: help install install-dev test test-unit test-integration test-coverage clean format lint type-check all-checks docker-test

# Default target
help:  ## Show this help message
	@echo "VanEck ETF Downloader - Available Commands:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install:  ## Install package in production mode
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e .[dev]

# Testing
test:  ## Run all tests with coverage
	./shell/test.sh

test-unit:  ## Run only unit tests (fast)
	./shell/test.sh --unit

test-integration:  ## Run integration tests (requires network)
	./shell/test.sh --integration

test-coverage:  ## Run tests and generate HTML coverage report
	./shell/test.sh --html

test-performance:  ## Run performance tests only
	pytest -m performance -v

test-docker:  ## Run Docker-specific tests
	pytest -m docker -v

test-selenium:  ## Run Selenium browser tests
	pytest -m selenium -v

test-network:  ## Run network-dependent tests
	pytest -m network -v

test-clean:  ## Clean test artifacts and run tests
	./shell/test.sh --clean

test-parallel:  ## Run tests in parallel
	./shell/test.sh --parallel

test-verbose:  ## Run tests with verbose output
	./shell/test.sh --verbose

test-quick:  ## Run quick tests (no slow/network tests)
	pytest -m "not slow and not network" -x

# Code Quality
format:  ## Format code with black and isort
	black src tests
	isort src tests

format-check:  ## Check code formatting without making changes
	black --check --diff src tests
	isort --check-only --diff src tests

lint:  ## Run linting with flake8 and ruff
	flake8 src tests
	ruff check src tests

lint-fix:  ## Run linting and fix auto-fixable issues
	ruff check --fix src tests

type-check:  ## Run type checking with mypy
	mypy src

# Combined quality checks
all-checks: format-check lint type-check test-unit  ## Run all code quality checks and unit tests

# Development
dev-setup:  ## Setup development environment
	python -m venv .venv
	. .venv/bin/activate && pip install -e .[dev]
	@echo "Development environment ready! Activate with: source .venv/bin/activate"

dev-shell:  ## Start development shell with environment activated
	@echo "Starting development shell..."
	. .venv/bin/activate && $$SHELL

# Cleaning
clean:  ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf test-reports/
	rm -rf .coverage*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete

clean-all: clean  ## Deep clean including virtual environment
	rm -rf .venv/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# Documentation
docs:  ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

docs-serve:  ## Serve documentation locally (placeholder)
	@echo "Documentation serving not yet implemented"

# Docker
docker-build:  ## Build Docker image (placeholder)
	@echo "Docker build not yet implemented - add Dockerfile first"

docker-test-env:  ## Start Docker test environment (placeholder)
	@echo "Docker test environment not yet implemented"

# CI/CD
ci-install:  ## Install dependencies for CI environment
	pip install -e .[dev]

ci-test:  ## Run tests suitable for CI
	./shell/test.sh --xml --cov-fail --no-cov

ci-security:  ## Run security checks (placeholder)
	@echo "Security checks not yet implemented - consider adding bandit"

# Release
version-bump:  ## Bump version (placeholder)
	@echo "Version bumping not yet implemented - consider adding bump2version"

release:  ## Create release (placeholder)
	@echo "Release process not yet implemented"

# Utility
requirements:  ## Generate requirements.txt from pyproject.toml
	pip-compile pyproject.toml

requirements-dev:  ## Update development requirements
	pip-compile pyproject.toml --extra dev -o requirements-dev.txt

check-deps:  ## Check for outdated dependencies
	pip list --outdated

# Environment info
env-info:  ## Show environment information
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-Not activated}"
	@echo "Current directory: $$(pwd)"
	@echo "Git branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repository')"

# Testing shortcuts
t: test-unit  ## Shortcut for unit tests
ti: test-integration  ## Shortcut for integration tests
tc: test-coverage  ## Shortcut for coverage tests
tf: format  ## Shortcut for formatting
tl: lint  ## Shortcut for linting

# Development workflow
dev: install-dev format lint test-unit  ## Complete development workflow

# Pre-commit checks
pre-commit: format lint type-check test-unit  ## Run pre-commit checks

# Get test info
test-info:  ## Show test information and statistics
	@echo "Test Statistics:"
	@echo "=================="
	@echo "Total test files: $$(find tests -name 'test_*.py' | wc -l)"
	@echo "Total test functions: $$(grep -r '^def test_' tests | wc -l)"
	@echo "Test markers available:"
	@pytest --markers | grep -E '^@pytest.mark' || echo "No custom markers found"
	@echo
	@echo "Recent test runs:"
	@ls -la test-reports/ 2>/dev/null || echo "No test reports found"

# File watching (requires entr)
test-watch:  ## Watch files and run tests on changes (requires 'entr')
	@which entr > /dev/null || (echo "Please install 'entr' for file watching: sudo apt-get install entr"; exit 1)
	find src tests -name '*.py' | entr -c make test-unit