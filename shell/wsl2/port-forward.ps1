# port-forward.ps1 - Set up port forwarding from Windows to WSL2
#
# IMPORTANT: This script is only needed if NOT using Tailscale.
# With Tailscale, port forwarding is not required.
#
# WSL2 runs in a virtual machine with a dynamic IP address that changes
# on each Windows restart. This script creates port forwarding rules
# to route traffic from Windows to WSL2.
#
# Run this script in PowerShell as Administrator:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\port-forward.ps1
#
# For automatic startup, use Windows Task Scheduler with wsl-startup.vbs
#

#Requires -RunAsAdministrator

Write-Host "========================================"
Write-Host "WSL2 Port Forwarding Setup"
Write-Host "========================================"
Write-Host ""

# Get WSL2 IP address
Write-Host "[INFO] Getting WSL2 IP address..."
$wslIP = (wsl hostname -I).Trim().Split()[0]

if ([string]::IsNullOrEmpty($wslIP)) {
    Write-Host "[ERROR] Could not get WSL2 IP address. Is WSL2 running?"
    exit 1
}

Write-Host "[INFO] WSL2 IP: $wslIP"
Write-Host ""

# Clear existing port proxy rules for our ports
Write-Host "[INFO] Clearing existing port forwarding rules..."
netsh interface portproxy delete v4tov4 listenport=22 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60001 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60002 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60003 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60004 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60005 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60006 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60007 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60008 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60009 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=60010 listenaddress=0.0.0.0 2>$null

# Set up SSH port forwarding (TCP 22)
Write-Host "[INFO] Setting up SSH port forwarding (TCP 22)..."
netsh interface portproxy add v4tov4 listenport=22 listenaddress=0.0.0.0 connectport=22 connectaddress=$wslIP
Write-Host "[SUCCESS] SSH forwarding: 0.0.0.0:22 -> ${wslIP}:22"

# Set up Mosh port forwarding (UDP 60000-60010)
# Note: netsh portproxy only works with TCP. For UDP, we need a different approach.
Write-Host ""
Write-Host "[WARN] Mosh uses UDP which netsh portproxy doesn't support directly."
Write-Host "[INFO] For Mosh, traffic must reach WSL2's IP directly or use Tailscale."
Write-Host ""

# Show current port proxy rules
Write-Host "Current port forwarding rules:"
Write-Host "========================================"
netsh interface portproxy show v4tov4
Write-Host ""

Write-Host "========================================"
Write-Host "Port Forwarding Setup Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "SSH is now accessible at:"
Write-Host "  - localhost:22 (from this machine)"
Write-Host "  - <Windows-IP>:22 (from local network)"
Write-Host ""
Write-Host "For Mosh to work without Tailscale, you need to:"
Write-Host "  1. Connect to the WSL2 IP directly ($wslIP)"
Write-Host "  2. Or use a UDP forwarding tool"
Write-Host "  3. Or (recommended) use Tailscale instead!"
Write-Host ""
Write-Host "NOTE: WSL2 IP changes on restart. Re-run this script after each restart,"
Write-Host "      or set up Windows Task Scheduler with wsl-startup.vbs"
Write-Host ""
