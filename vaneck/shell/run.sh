#!/bin/bash
# Run script for VanEck ETF Downloader using Docker

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Configuration
IMAGE_NAME="vaneck-etf-downloader"
CONTAINER_NAME="vaneck-etf-downloader"
DOWNLOAD_DIR="${PROJECT_ROOT}/download"

# Function to print coloured messages
print_message() {
    local colour=$1
    local message=$2
    echo -e "${colour}[RUN]${NC} ${message}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_message "$RED" "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if image exists
if ! docker images | grep -q "$IMAGE_NAME"; then
    print_message "$YELLOW" "Docker image not found. Building it first..."
    ./shell/build.sh
fi

# Create download directory if it doesn't exist
if [ ! -d "$DOWNLOAD_DIR" ]; then
    print_message "$BLUE" "Creating download directory..."
    mkdir -p "$DOWNLOAD_DIR"
fi

# Ensure download directory is writable
chmod 777 "$DOWNLOAD_DIR" 2>/dev/null || true

# Stop and remove existing container if running
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    print_message "$BLUE" "Stopping and removing existing container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# Prepare environment file if it exists
ENV_FILE=""
if [ -f ".env" ]; then
    ENV_FILE="--env-file .env"
    print_message "$BLUE" "Using .env file for environment variables"
fi

# Run the Docker container
print_message "$GREEN" "Starting VanEck ETF Downloader container..."
docker run \
    --name "$CONTAINER_NAME" \
    --rm \
    -v "$DOWNLOAD_DIR:/app/download" \
    $ENV_FILE \
    "$IMAGE_NAME:latest" \
    "$@"

print_message "$GREEN" "Container execution completed!"