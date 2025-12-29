#!/usr/bin/env bash
#
# start-services.sh - Start SSH and Tailscale services in WSL2
#
# Run this script when WSL2 starts to ensure services are running.
# Can be added to ~/.bashrc or ~/.zshrc, or called from Windows Task Scheduler.
#

set -euo pipefail

# Colours (optional, for interactive use)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

QUIET=${1:-""}

log_info() { [[ -z "$QUIET" ]] && echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { [[ -z "$QUIET" ]] && echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { [[ -z "$QUIET" ]] && echo -e "${YELLOW}[WARN]${NC} $1"; }

# Start SSH if not running
if ! pgrep -x "sshd" > /dev/null; then
    log_info "Starting SSH service..."
    sudo service ssh start > /dev/null 2>&1
    if pgrep -x "sshd" > /dev/null; then
        log_success "SSH started"
    else
        log_warn "Failed to start SSH"
    fi
else
    log_info "SSH already running"
fi

# Start Tailscale if installed and not running
if command -v tailscale &> /dev/null; then
    if ! pgrep -x "tailscaled" > /dev/null; then
        log_info "Starting Tailscale daemon..."
        sudo tailscaled > /dev/null 2>&1 &
        sleep 2

        # Check if connected
        if tailscale status > /dev/null 2>&1; then
            log_success "Tailscale connected"
        else
            log_warn "Tailscale started but not connected. Run: sudo tailscale up"
        fi
    else
        if tailscale status > /dev/null 2>&1; then
            log_info "Tailscale already running and connected"
        else
            log_warn "Tailscale daemon running but not connected. Run: sudo tailscale up"
        fi
    fi
fi

# Print connection info (unless quiet mode)
if [[ -z "$QUIET" ]]; then
    echo ""
    echo "Connection Info:"
    echo "  User: $(whoami)"

    if command -v tailscale &> /dev/null && tailscale status > /dev/null 2>&1; then
        echo "  Tailscale IP: $(tailscale ip -4 2>/dev/null || echo 'N/A')"
    fi

    # Show WSL2 internal IP (for reference)
    WSL_IP=$(hostname -I | awk '{print $1}')
    echo "  WSL2 IP: $WSL_IP (internal)"
fi
