#!/bin/bash
# Setup tmux + Claude Code for remote access via Blink (iPhone SSH/Mosh client)
# Run this on WSL2/Ubuntu to configure persistent tmux sessions with auto-attach on SSH

set -e

echo "=== Setting up tmux + Claude for Blink remote access ==="

# Create tmux configuration
echo "Creating ~/.tmux.conf..."
cat > ~/.tmux.conf << 'EOF'
# Improve colours
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",xterm-256color:Tc"

# Increase scrollback
set -g history-limit 50000

# Mouse support (useful for scrolling)
set -g mouse on

# Start windows/panes at 1 (easier to reach)
set -g base-index 1
setw -g pane-base-index 1

# Reduce escape delay (better for vim/claude)
set -sg escape-time 10

# Status bar
set -g status-position bottom
set -g status-style 'bg=#1a1b26 fg=#a9b1d6'
set -g status-left '#[fg=#7aa2f7,bold][#S] '
set -g status-right '#[fg=#bb9af7]%H:%M '

# Easy reload
bind r source-file ~/.tmux.conf \; display "Config reloaded"

# Keep current path when splitting
bind '"' split-window -c "#{pane_current_path}"
bind % split-window -h -c "#{pane_current_path}"
EOF

# Create auto-attach script
echo "Creating ~/.local/bin/tmux-claude..."
mkdir -p ~/.local/bin
cat > ~/.local/bin/tmux-claude << 'EOF'
#!/bin/bash
# Auto-attach to existing tmux session or create new one

SESSION_NAME="claude"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    exec tmux attach-session -t "$SESSION_NAME"
else
    exec tmux new-session -s "$SESSION_NAME" -c ~/projects
fi
EOF
chmod +x ~/.local/bin/tmux-claude

# Add to bashrc if not already present
BASHRC_MARKER="# tmux-claude auto-attach"
if ! grep -q "$BASHRC_MARKER" ~/.bashrc 2>/dev/null; then
    echo "Updating ~/.bashrc..."
    cat >> ~/.bashrc << 'EOF'

# tmux-claude auto-attach
# Ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Auto-attach to tmux for SSH sessions (not for local terminals)
if [[ -n "$SSH_CONNECTION" ]] && [[ -z "$TMUX" ]] && command -v tmux &>/dev/null; then
    ~/.local/bin/tmux-claude
fi
EOF
else
    echo "~/.bashrc already configured, skipping..."
fi

# Ensure SSH directory exists
echo "Setting up SSH directory..."
mkdir -p ~/.ssh && chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys

# Verify installation
echo ""
echo "=== Setup complete ==="
echo ""
echo "Installed:"
echo "  - ~/.tmux.conf (tmux configuration)"
echo "  - ~/.local/bin/tmux-claude (auto-attach script)"
echo "  - ~/.bashrc (updated with auto-attach on SSH)"
echo ""
echo "Next steps:"
echo "  1. Run Windows firewall commands (see setup-windows-firewall.ps1)"
echo "  2. Add your Blink SSH public key to ~/.ssh/authorized_keys"
echo "  3. Connect from Blink: ssh $(whoami)@$(hostname -I | awk '{print $1}')"
echo ""
