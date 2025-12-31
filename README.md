# tmux + Claude Code + Blink Setup for WSL2

Remote access to Claude Code from iPhone using [Blink](https://blink.sh) via SSH/Mosh, with persistent tmux sessions.

## Architecture

```
iPhone (Blink) → SSH/Mosh → Windows Host → WSL2 (mirrored) → tmux → Claude Code
```

## Prerequisites

- **Windows 11 22H2+** (for mirrored networking)
- **WSL2** with Ubuntu
- **Blink app** on iPhone/iPad
- **tmux** and **mosh** installed: `sudo apt install tmux mosh`

## Quick Setup (Fresh Box)

### 1. Configure WSL2 Networking

Create/edit `%USERPROFILE%\.wslconfig` on Windows:

```ini
[wsl2]
networkingMode=mirrored
```

Restart WSL: `wsl --shutdown` from PowerShell.

### 2. Run Setup Script

```bash
./setup-tmux-blink.sh
```

This installs:
- `~/.tmux.conf` — tmux configuration with sensible defaults
- `~/.local/bin/tmux-claude` — auto-attach script
- `~/.bashrc` additions — auto-attach on SSH login

### 3. Configure Windows Firewall

Run `setup-windows-firewall.ps1` in PowerShell as Administrator, or manually:

```powershell
New-NetFirewallRule -DisplayName "WSL2 SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow
New-NetFirewallRule -DisplayName "WSL2 Mosh" -Direction Inbound -Protocol UDP -LocalPort 60000-61000 -Action Allow
```

### 4. Add SSH Key

Add your Blink public key to `~/.ssh/authorized_keys`:

```bash
echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys
```

### 5. Configure Blink

1. **Add Host**:
   - Host: Your Windows IP (find with `hostname -I` in WSL)
   - Port: 22
   - User: your-username
   - Key: Select your key

2. **Enable Mosh** (optional, recommended for mobile):
   - Toggle "Mosh" on
   - Server: `/usr/bin/mosh-server`

## Usage

Connect from Blink — you'll land directly in a tmux session named `claude`:

```bash
ssh user@host-ip
```

### tmux Key Bindings

| Key | Action |
|-----|--------|
| `Ctrl+B, D` | Detach (closes SSH cleanly) |
| `Ctrl+B, C` | New window |
| `Ctrl+B, N/P` | Next/previous window |
| `Ctrl+B, "` | Split horizontally |
| `Ctrl+B, %` | Split vertically |
| `Ctrl+B, R` | Reload config |

### Session Persistence

- tmux sessions persist through SSH disconnects
- Reconnecting re-attaches to the same session
- Run `claude` inside tmux for Claude Code

## Why Mosh?

> **Note**: Mosh is not yet working from iPhone — SSH works fine. This is a known issue being investigated.

Mosh is recommended over plain SSH for mobile because it:
- Handles network roaming (WiFi ↔ mobile data)
- Survives sleep/wake cycles
- Shows local echo immediately (feels more responsive)
- Reconnects automatically after network changes

## Files

| File | Purpose |
|------|---------|
| `setup-tmux-blink.sh` | Main setup script for WSL2 |
| `setup-windows-firewall.ps1` | Windows firewall rules |
| `README.md` | This documentation |

## Troubleshooting

**Can't connect from Blink:**
1. Check Windows firewall rules are applied
2. Verify SSH is running: `sudo systemctl status ssh`
3. Confirm WSL2 mirrored mode: check `.wslconfig`

**Mosh not connecting:**
1. Ensure UDP ports 60000-61000 are open
2. Check mosh-server is installed: `which mosh-server`

**tmux not auto-attaching:**
1. Verify `~/.bashrc` has the auto-attach code
2. Check `SSH_CONNECTION` is set: `echo $SSH_CONNECTION`
