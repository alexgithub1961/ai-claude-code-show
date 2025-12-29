#!/usr/bin/env bash
#
# setup-tailscale.sh - Install and configure Tailscale in WSL2
#
# Tailscale creates a mesh VPN that gives your WSL2 instance a stable IP address,
# eliminating the need for port forwarding from Windows.
#

set -euo pipefail

# Colours
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo "========================================"
echo "Tailscale Setup for WSL2"
echo "========================================"
echo ""

# Check if Tailscale is already installed
if command -v tailscale &> /dev/null; then
    log_warn "Tailscale is already installed"
    tailscale version
    echo ""

    # Check status
    if tailscale status &> /dev/null; then
        log_success "Tailscale is connected"
        echo ""
        echo "Your Tailscale IP:"
        tailscale ip -4
        exit 0
    else
        log_warn "Tailscale is installed but not connected"
        echo "Run: sudo tailscale up"
        exit 0
    fi
fi

# Install Tailscale
log_info "Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

log_success "Tailscale installed successfully"

# Start Tailscale daemon if not running
log_info "Starting Tailscale daemon..."
sudo tailscaled &> /dev/null &
sleep 2

# Authenticate
echo ""
log_info "Authenticating Tailscale..."
echo "A browser window will open for authentication."
echo "If it doesn't, copy the URL displayed below."
echo ""

sudo tailscale up

# Show the Tailscale IP
echo ""
log_success "Tailscale is now connected!"
echo ""
echo "Your Tailscale IP address:"
tailscale ip -4
echo ""
echo "You can also use MagicDNS hostname if enabled in your Tailscale admin console."
echo ""
echo "Next steps:"
echo "  1. Note your Tailscale IP above"
echo "  2. Run ./setup-ssh.sh to set up SSH server"
echo "  3. Run ./setup-mosh.sh to install Mosh"
echo "  4. Configure Blink on your iPad with this IP"
