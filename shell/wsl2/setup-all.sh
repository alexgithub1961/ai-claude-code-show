#!/usr/bin/env bash
#
# setup-all.sh - Complete WSL2 SSH/Mosh setup with Tailscale
#
# This is the recommended way to set up remote access to WSL2 from Blink on iOS.
# It runs all setup scripts in the correct order.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colours
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       WSL2 Remote Access Setup for Blink on iOS/iPad       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in WSL
if [[ ! -f /proc/version ]] || ! grep -qi microsoft /proc/version; then
    echo -e "${RED}[ERROR]${NC} This script must be run inside WSL2"
    exit 1
fi

echo "This script will set up:"
echo "  1. Tailscale - for stable IP and easy connectivity"
echo "  2. SSH server - for secure shell access"
echo "  3. Mosh - for persistent connections"
echo ""
echo "Press Enter to continue, or Ctrl+C to cancel..."
read -r

# Run setup scripts
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 1/4: Setting up Tailscale${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
"$SCRIPT_DIR/setup-tailscale.sh"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 2/4: Setting up SSH Server${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
"$SCRIPT_DIR/setup-ssh.sh"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 3/4: Setting up Mosh${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
"$SCRIPT_DIR/setup-mosh.sh"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 4/4: Starting Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
"$SCRIPT_DIR/start-services.sh"

# Final summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Setup Complete!                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get connection info
TAILSCALE_IP=""
if command -v tailscale &> /dev/null && tailscale status > /dev/null 2>&1; then
    TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "")
fi

echo "Connection details for Blink on iOS:"
echo ""
if [[ -n "$TAILSCALE_IP" ]]; then
    echo "  Hostname/IP: $TAILSCALE_IP"
    echo "  User: $(whoami)"
    echo "  Port: 22"
    echo ""
    echo "  SSH command:  ssh $(whoami)@$TAILSCALE_IP"
    echo "  Mosh command: mosh $(whoami)@$TAILSCALE_IP"
else
    echo "  Tailscale IP not available. Run: tailscale ip -4"
fi

echo ""
echo "Next steps:"
echo "  1. Add your SSH public key from Blink to ~/.ssh/authorized_keys"
echo "  2. Create a new host in Blink with the details above"
echo "  3. Connect and enjoy!"
echo ""
echo "To ensure services start automatically, add this to ~/.bashrc:"
echo "  $SCRIPT_DIR/start-services.sh --quiet"
echo ""
