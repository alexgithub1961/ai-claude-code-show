# Windows Firewall rules for SSH and Mosh access to WSL2
# Run this in PowerShell as Administrator

Write-Host "Adding firewall rules for SSH and Mosh..." -ForegroundColor Cyan

# SSH (TCP port 22)
New-NetFirewallRule -DisplayName "WSL2 SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -ErrorAction SilentlyContinue
if ($?) {
    Write-Host "  SSH (port 22) - Added" -ForegroundColor Green
} else {
    Write-Host "  SSH (port 22) - Already exists or failed" -ForegroundColor Yellow
}

# Mosh (UDP ports 60000-61000)
New-NetFirewallRule -DisplayName "WSL2 Mosh" -Direction Inbound -Protocol UDP -LocalPort 60000-61000 -Action Allow -ErrorAction SilentlyContinue
if ($?) {
    Write-Host "  Mosh (ports 60000-61000) - Added" -ForegroundColor Green
} else {
    Write-Host "  Mosh (ports 60000-61000) - Already exists or failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done! You can now connect to WSL2 via SSH/Mosh." -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Ensure WSL2 has networkingMode=mirrored in %USERPROFILE%\.wslconfig" -ForegroundColor Gray
