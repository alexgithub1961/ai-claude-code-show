#!/usr/bin/env bash
#
# worktree-new.sh - Create a new git worktree with proper setup
#
# Usage: ./shell/worktree-new.sh <branch-name> [worktree-dir-name]
#
# This script:
#   1. Creates a new git worktree in the sibling worktrees directory
#   2. Symlinks git-ignored files (.env) from the main repo
#   3. Prints next steps for setting up the worktree
#
# Examples:
#   ./shell/worktree-new.sh feature/my-feature
#   ./shell/worktree-new.sh feature/my-feature my-feature-dir

set -euo pipefail

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_REPO="$(dirname "$SCRIPT_DIR")"
REPO_NAME="$(basename "$MAIN_REPO")"
WORKTREES_DIR="$(dirname "$MAIN_REPO")/${REPO_NAME}-worktrees"

usage() {
    echo "Usage: $0 <branch-name> [worktree-dir-name]"
    echo ""
    echo "Arguments:"
    echo "  branch-name       Name of the branch to create (e.g., feature/my-feature)"
    echo "  worktree-dir-name Optional: Directory name for the worktree (default: derived from branch)"
    echo ""
    echo "Examples:"
    echo "  $0 feature/wsl2-ssh-setup"
    echo "  $0 feature/wsl2-ssh-setup wsl2-ssh"
    exit 1
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [[ $# -lt 1 ]]; then
    usage
fi

BRANCH_NAME="$1"

# Derive worktree directory name from branch if not provided
if [[ $# -ge 2 ]]; then
    WORKTREE_DIR_NAME="$2"
else
    # Convert branch name to directory name (feature/my-feature -> my-feature)
    WORKTREE_DIR_NAME="${BRANCH_NAME##*/}"
fi

WORKTREE_PATH="${WORKTREES_DIR}/${WORKTREE_DIR_NAME}"

# Validate we're in a git repo
if ! git -C "$MAIN_REPO" rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not a git repository: $MAIN_REPO"
    exit 1
fi

# Check if branch already exists
if git -C "$MAIN_REPO" show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    log_warn "Branch '${BRANCH_NAME}' already exists"
    CREATE_BRANCH=""
else
    CREATE_BRANCH="-b"
fi

# Check if worktree path already exists
if [[ -d "$WORKTREE_PATH" ]]; then
    log_error "Worktree directory already exists: $WORKTREE_PATH"
    exit 1
fi

# Create worktrees directory if needed
if [[ ! -d "$WORKTREES_DIR" ]]; then
    log_info "Creating worktrees directory: $WORKTREES_DIR"
    mkdir -p "$WORKTREES_DIR"
fi

# Create the worktree
log_info "Creating worktree at: $WORKTREE_PATH"
log_info "Branch: $BRANCH_NAME"

if [[ -n "$CREATE_BRANCH" ]]; then
    git -C "$MAIN_REPO" worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"
else
    git -C "$MAIN_REPO" worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
fi

log_success "Worktree created successfully"

# Symlink git-ignored files from main repo
log_info "Setting up symlinks for git-ignored files..."

# Symlink vaneck/.env if it exists in main repo
MAIN_ENV="${MAIN_REPO}/vaneck/.env"
WORKTREE_ENV="${WORKTREE_PATH}/vaneck/.env"

if [[ -f "$MAIN_ENV" ]]; then
    if [[ -d "${WORKTREE_PATH}/vaneck" ]]; then
        ln -sf "$MAIN_ENV" "$WORKTREE_ENV"
        log_success "Symlinked: vaneck/.env"
    fi
else
    log_warn "No .env file found at $MAIN_ENV - create one from .env.example if needed"
fi

# Print summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Worktree setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Worktree location: $WORKTREE_PATH"
echo "Branch: $BRANCH_NAME"
echo ""
echo "Next steps:"
echo "  1. cd $WORKTREE_PATH"
echo "  2. If Python work needed:"
echo "     cd vaneck && uv venv && source .venv/bin/activate && uv pip install -r requirements.txt"
echo ""
echo "To list all worktrees: git worktree list"
echo "To remove this worktree: git worktree remove $WORKTREE_PATH"
