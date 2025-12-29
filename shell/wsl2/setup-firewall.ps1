# setup-firewall.ps1 - Configure Windows Firewall for SSH and Mosh
#
# IMPORTANT: This script is only needed if NOT using Tailscale.
# With Tailscale, firewall rules are not required.
#
# Run this script in PowerShell as Administrator:
#   Set-ExecutionPolicy Bypass -Scope Process
#   .\setup-firewall.ps1
#

#Requires -RunAsAdministrator

Write-Host "========================================"
Write-Host "Windows Firewall Setup for WSL2 SSH/Mosh"
Write-Host "========================================"
Write-Host ""

# SSH (TCP 22)
Write-Host "[INFO] Creating firewall rule for SSH (TCP 22)..."
$sshRule = Get-NetFirewallRule -DisplayName "WSL2 SSH" -ErrorAction SilentlyContinue
if ($sshRule) {
    Write-Host "[WARN] SSH rule already exists, updating..."
    Remove-NetFirewallRule -DisplayName "WSL2 SSH"
}

New-NetFirewallRule -DisplayName "WSL2 SSH" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 22 `
    -Action Allow `
    -Profile Any `
    -Description "Allow SSH connections to WSL2"

Write-Host "[SUCCESS] SSH firewall rule created"

# Mosh (UDP 60000-60010)
Write-Host ""
Write-Host "[INFO] Creating firewall rule for Mosh (UDP 60000-60010)..."
$moshRule = Get-NetFirewallRule -DisplayName "WSL2 Mosh" -ErrorAction SilentlyContinue
if ($moshRule) {
    Write-Host "[WARN] Mosh rule already exists, updating..."
    Remove-NetFirewallRule -DisplayName "WSL2 Mosh"
}

New-NetFirewallRule -DisplayName "WSL2 Mosh" `
    -Direction Inbound `
    -Protocol UDP `
    -LocalPort 60000-60010 `
    -Action Allow `
    -Profile Any `
    -Description "Allow Mosh connections to WSL2"

Write-Host "[SUCCESS] Mosh firewall rule created"

Write-Host ""
Write-Host "========================================"
Write-Host "Firewall Setup Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "Rules created:"
Write-Host "  - WSL2 SSH: TCP 22 (Inbound)"
Write-Host "  - WSL2 Mosh: UDP 60000-60010 (Inbound)"
Write-Host ""
Write-Host "Next step: Run port-forward.ps1 to set up port forwarding"
Write-Host ""

# Verify rules
Write-Host "Verifying firewall rules..."
Get-NetFirewallRule -DisplayName "WSL2*" | Format-Table DisplayName, Enabled, Direction, Action
