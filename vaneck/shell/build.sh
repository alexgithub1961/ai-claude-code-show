#!/bin/bash
set -euo pipefail

# VanEck ETF Downloader - Build Script
# Builds the Docker image for the ETF downloader

PROJECT_NAME="vaneck-etf-downloader"
IMAGE_TAG="latest"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

log() {
    echo -e "${BLUE}[BUILD]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build the VanEck ETF Downloader Docker image.

OPTIONS:
    -t, --tag TAG       Set image tag (default: latest)
    -n, --no-cache      Build without cache
    -p, --push          Push image to registry after build
    -h, --help          Show this help message

EXAMPLES:
    $0                  Build with default settings
    $0 -t v1.0.0        Build with specific tag
    $0 --no-cache       Build without Docker cache
    $0 -t v1.0.0 -p     Build and push to registry

EOF
}

# Parse command line arguments
NO_CACHE=false
PUSH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -n|--no-cache)
            NO_CACHE=true
            shift
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
log "Validating build environment..."

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    log_error "pyproject.toml not found. Run this script from the project root."
    exit 1
fi

if [[ ! -f "Dockerfile" ]]; then
    log_error "Dockerfile not found. Run this script from the project root."
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

# Create download directory if it doesn't exist
log "Creating download directory..."
mkdir -p download

# Build the image
IMAGE_NAME="${PROJECT_NAME}:${IMAGE_TAG}"
log "Building Docker image: ${IMAGE_NAME}"

# Build arguments
BUILD_ARGS=(
    --build-arg "BUILD_DATE=${BUILD_DATE}"
    --build-arg "GIT_COMMIT=${GIT_COMMIT}"
    --build-arg "VERSION=${IMAGE_TAG}"
    --tag "${IMAGE_NAME}"
    --label "org.opencontainers.image.created=${BUILD_DATE}"
    --label "org.opencontainers.image.revision=${GIT_COMMIT}"
    --label "org.opencontainers.image.version=${IMAGE_TAG}"
    --label "org.opencontainers.image.source=https://github.com/vaneck/etf-downloader"
    --label "org.opencontainers.image.title=VanEck ETF Downloader"
    --label "org.opencontainers.image.description=A robust ETF data downloader for VanEck funds"
)

# Add no-cache flag if requested
if [[ "${NO_CACHE}" == "true" ]]; then
    BUILD_ARGS+=(--no-cache)
    log "Building without cache..."
fi

# Execute build
if docker build "${BUILD_ARGS[@]}" .; then
    log_success "Docker image built successfully: ${IMAGE_NAME}"
else
    log_error "Docker build failed"
    exit 1
fi

# Show image info
log "Image information:"
docker images "${PROJECT_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"

# Push if requested
if [[ "${PUSH}" == "true" ]]; then
    log "Pushing image to registry..."
    if docker push "${IMAGE_NAME}"; then
        log_success "Image pushed successfully"
    else
        log_error "Failed to push image"
        exit 1
    fi
fi

# Security scan (if available)
if command -v docker &> /dev/null && docker version --format '{{.Server.Version}}' | grep -q "20\|21\|22\|23\|24"; then
    log "Running security scan..."
    if docker scan "${IMAGE_NAME}" 2>/dev/null || true; then
        log "Security scan completed"
    else
        log_warning "Security scan not available or failed"
    fi
fi

log_success "Build completed successfully!"
log "To run the container:"
log "  docker run --rm -v \$(pwd)/download:/app/download ${IMAGE_NAME} --help"
log ""
log "To run interactive shell:"
log "  docker run --rm -it -v \$(pwd)/download:/app/download ${IMAGE_NAME} bash"