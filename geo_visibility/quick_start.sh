#!/bin/bash
# Quick-start script for browser-based GEO assessment
# Validates SearchAPI vs Real Browser results

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║    Browser-Based GEO Visibility Assessment - Quick Start     ║"
echo "║    Validates if real browsers see different results          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "browser_search_engine.py" ]; then
    echo -e "${RED}Error: browser_search_engine.py not found${NC}"
    echo "Please run this script from the geo_visibility directory"
    exit 1
fi

# Step 1: Check Python
echo -e "${YELLOW}[1/6]${NC} Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}[2/6]${NC} Installing Python dependencies..."
if pip3 show playwright &> /dev/null; then
    echo -e "${GREEN}✓${NC} Playwright already installed"
else
    echo "Installing playwright..."
    pip3 install playwright
fi

if pip3 show httpx &> /dev/null; then
    echo -e "${GREEN}✓${NC} httpx already installed"
else
    echo "Installing httpx..."
    pip3 install httpx
fi
echo ""

# Step 3: Install browsers
echo -e "${YELLOW}[3/6]${NC} Installing Chromium browser..."
if [ -d "$HOME/.cache/ms-playwright/chromium-"* ]; then
    echo -e "${GREEN}✓${NC} Chromium already installed"
else
    echo "Installing Chromium (this may take a few minutes)..."
    python3 -m playwright install chromium
fi
echo ""

# Step 4: Create screenshots directory
echo -e "${YELLOW}[4/6]${NC} Creating screenshots directory..."
mkdir -p screenshots
echo -e "${GREEN}✓${NC} Screenshots will be saved to: $(pwd)/screenshots"
echo ""

# Step 5: Test DNS resolution
echo -e "${YELLOW}[5/6]${NC} Testing network connectivity..."
if ping -c 1 google.com &> /dev/null; then
    echo -e "${GREEN}✓${NC} Network connectivity OK"
else
    echo -e "${RED}✗ Cannot reach google.com${NC}"
    echo ""
    echo "Possible solutions:"
    echo "  1. Check your internet connection"
    echo "  2. If in Docker, ensure DNS is configured (see DOCKER_DNS_FIX.md)"
    echo "  3. Try running with: docker run --dns 8.8.8.8 --dns 8.8.4.4 ..."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# Step 6: Set API key
echo -e "${YELLOW}[6/6]${NC} Configuring SearchAPI..."
if [ -z "$SEARCHAPI_API_KEY" ]; then
    echo "SEARCHAPI_API_KEY not set in environment"
    echo "Using default from code: dUngVqvqnKPAr1p1BKqKENJW"
else
    echo -e "${GREEN}✓${NC} Using SEARCHAPI_API_KEY from environment"
fi
echo ""

# Ready to run
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "What would you like to do?"
echo ""
echo "  1) Quick test (single query comparison)"
echo "  2) Full assessment (5 critical queries)"
echo "  3) Extended assessment (20 queries)"
echo "  4) Custom query"
echo "  5) Exit"
echo ""
read -p "Choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Running quick test with query: 'EPAM software company'"
        echo ""
        python3 -c "
import asyncio
from browser_search_engine import compare_api_vs_browser

asyncio.run(compare_api_vs_browser(
    'EPAM software company',
    '${SEARCHAPI_API_KEY:-dUngVqvqnKPAr1p1BKqKENJW}'
))
"
        ;;
    2)
        echo ""
        echo "Running full assessment (5 critical queries)..."
        echo "This will take approximately 2-3 minutes"
        echo ""
        python3 browser_assessment_critical.py
        ;;
    3)
        echo ""
        echo "Running extended assessment (20 queries)..."
        echo "This will take approximately 10-15 minutes"
        echo ""
        python3 browser_assessment_full.py
        ;;
    4)
        echo ""
        read -p "Enter your search query: " query
        echo ""
        echo "Searching for: $query"
        echo ""
        python3 -c "
import asyncio
from browser_search_engine import compare_api_vs_browser

asyncio.run(compare_api_vs_browser(
    '$query',
    '${SEARCHAPI_API_KEY:-dUngVqvqnKPAr1p1BKqKENJW}'
))
"
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}Assessment complete!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Screenshots saved to: $(pwd)/screenshots"
echo ""
echo "Next steps:"
echo "  • Review screenshots to verify results"
echo "  • Check if AI Overview appears more in browser vs API"
echo "  • Look for company mentions in browser results"
echo "  • Run more queries if needed"
echo ""
