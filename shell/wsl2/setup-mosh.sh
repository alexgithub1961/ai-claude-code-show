#!/usr/bin/env bash
#
# setup-mosh.sh - Install Mosh server in WSL2
#
# Mosh (mobile shell) provides connection persistence that survives:
# - Network changes (WiFi to cellular)
# - IP address changes
# - Sleep/wake cycles
# - Brief disconnections
#
# Perfect for mobile development on iPad!
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
echo "Mosh Server Setup for WSL2"
echo "========================================"
echo ""

# Check if Mosh is already installed
if command -v mosh-server &> /dev/null; then
    log_warn "Mosh is already installed"
    mosh-server --version 2>&1 | head -1
    echo ""
    echo "Mosh server location: $(which mosh-server)"
    exit 0
fi

# Install Mosh
log_info "Installing Mosh..."
sudo apt-get update -qq
sudo apt-get install -y mosh

# Verify installation
if command -v mosh-server &> /dev/null; then
    log_success "Mosh installed successfully"
    mosh-server --version 2>&1 | head -1
else
    log_error "Mosh installation failed"
    exit 1
fi

echo ""
echo "========================================"
log_success "Mosh Setup Complete!"
echo "========================================"
echo ""
echo "Mosh uses UDP ports 60000-61000 (by default, first 10 ports: 60000-60010)"
echo ""
echo "With Tailscale: UDP works automatically - no firewall configuration needed!"
echo ""
echo "Without Tailscale: You need to:"
echo "  1. Open UDP ports in Windows Firewall (see setup-firewall.ps1)"
echo "  2. Set up port forwarding (see port-forward.ps1)"
echo ""
echo "Connect from Blink:"
if command -v tailscale &> /dev/null && tailscale status &> /dev/null 2>&1; then
    echo "  mosh $(whoami)@$(tailscale ip -4)"
else
    echo "  mosh $(whoami)@<your-ip-address>"
fi
echo ""
echo "Tip: Mosh automatically uses your SSH keys for authentication,"
echo "     then switches to its own encrypted UDP protocol."
