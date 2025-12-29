# WSL2 SSH & Mosh Setup for Blink on iOS/iPad

This directory contains scripts to configure WSL2/Ubuntu for remote access via SSH and Mosh,
optimised for use with [Blink Shell](https://blink.sh/) on iOS/iPad.

## Quick Start (Recommended: Tailscale)

If you have Tailscale on your iPhone/iPad, this is the simplest approach:

```bash
# Run the complete setup
./setup-all.sh

# Or run individual scripts:
./setup-tailscale.sh   # Install and configure Tailscale
./setup-ssh.sh         # Install and configure SSH server
./setup-mosh.sh        # Install Mosh server
./start-services.sh    # Start SSH service
```

Then in Blink on your iPad:
1. Get your Tailscale IP: `tailscale ip -4`
2. Add a new host using that IP
3. Import your SSH key
4. Connect!

## Alternative: Traditional Port Forwarding

If not using Tailscale, you'll need to set up port forwarding from Windows to WSL2:

```powershell
# Run in PowerShell as Administrator (on Windows)
.\setup-firewall.ps1   # Configure Windows Firewall
.\port-forward.ps1     # Set up port forwarding
```

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `setup-all.sh` | Master script - runs everything |
| `setup-tailscale.sh` | Install and configure Tailscale (recommended) |
| `setup-ssh.sh` | Install and configure OpenSSH server |
| `setup-mosh.sh` | Install Mosh server |
| `start-services.sh` | Start SSH service (run on WSL startup) |
| `setup-firewall.ps1` | Windows Firewall rules (non-Tailscale only) |
| `port-forward.ps1` | WSL2 port forwarding (non-Tailscale only) |
| `wsl-startup.vbs` | Silent launcher for Windows Task Scheduler |

## Blink Shell Configuration

### With Tailscale (Recommended)

1. **Add Host**
   - Name: `wsl2` (or any name)
   - Hostname: Your Tailscale IP (e.g., `100.x.x.x`) or MagicDNS hostname
   - Port: `22`
   - User: Your WSL username

2. **Add Key**
   - Generate an Ed25519 key in Blink or import existing
   - Copy public key to WSL: `~/.ssh/authorized_keys`

3. **Connect**
   - SSH: `ssh wsl2`
   - Mosh: `mosh wsl2`

### Without Tailscale

1. Use your Windows machine's local IP address
2. Ensure port forwarding is running (see `port-forward.ps1`)
3. Windows Firewall must allow SSH (TCP 22) and Mosh (UDP 60000-60010)

## Troubleshooting

### Connection hangs with no output
**Most common cause: Tailscale not connected on iOS/iPad!**

1. Open the Tailscale app on your iPhone/iPad
2. Ensure it shows "Connected" (not "Not Connected" or "Connecting")
3. Verify your device appears in: `tailscale status` on WSL2
4. Try again: `ssh user@<tailscale-ip>`

### SSH won't start
```bash
sudo service ssh status
sudo service ssh start
# Check logs
sudo journalctl -u ssh
```

### Tailscale connection issues
```bash
# Check status on WSL2
tailscale status

# Look for your iOS device - it should show as online, not "offline"
# If offline, open Tailscale app on iOS and connect

# Reset Tailscale if needed
sudo tailscale up --reset
```

### "Permission denied" errors
Your public key isn't in `~/.ssh/authorized_keys`. Add it:
```bash
echo 'your-public-key-here' >> ~/.ssh/authorized_keys
```

### Mosh won't connect
- Ensure Mosh server is installed: `which mosh-server`
- Check UDP ports are open (60000-60010)
- With Tailscale, UDP should work automatically

### WSL2 IP changed
This is why Tailscale is recommended! If not using Tailscale:
```powershell
# Re-run port forwarding (PowerShell as Admin)
.\port-forward.ps1
```

## WSL Startup Automation

To ensure SSH starts automatically when WSL boots:

1. Add to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   # Start SSH if not running
   if ! pgrep -x "sshd" > /dev/null; then
       sudo service ssh start
   fi
   ```

2. Or use Windows Task Scheduler with `wsl-startup.vbs`

## Security Notes

- SSH is configured for **key-based authentication only** (password disabled)
- Ed25519 keys are recommended over RSA
- Tailscale adds an extra layer of authentication via your Tailscale account
- All connections are encrypted (SSH/Mosh/Tailscale)
