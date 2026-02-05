# Gemini CLI Setup Guide

## Overview

Gemini CLI is Google's official command-line interface for interacting with Gemini AI models directly from your terminal.

## Installation

### Install via npm (globally)

```bash
sudo npm install -g @google/gemini-cli@latest
```

### Verify installation

```bash
gemini --version
```

## Updating

To update to the latest version:

```bash
sudo npm install -g @google/gemini-cli@latest
```

> **Note**: `sudo` is required because global npm packages are installed in `/usr/lib/node_modules/` which requires elevated privileges.

## Authentication

Gemini CLI supports multiple authentication methods:

### Option 1: Google Cloud Auth (Recommended)

If you have `gcloud` CLI configured:

1. Run `gemini` in your terminal
2. It will open a browser for OAuth authentication
3. Sign in with your Google account
4. Press `r` to restart Gemini CLI after authentication succeeds

The credentials are cached in `~/.gemini/` for future sessions.

### Option 2: API Key

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Set the environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
gemini
```

To make it permanent, add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Option 3: Vertex AI

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
gemini
```

## Troubleshooting

### "Invalid auth method selected"

This error occurs when the authentication configuration is invalid or expired.

**Fix:**
1. Delete the settings file: `rm ~/.gemini/settings.json`
2. Run `gemini` again to trigger fresh authentication

### "EACCES: permission denied"

This occurs when installing without `sudo`.

**Fix:**
```bash
sudo npm install -g @google/gemini-cli@latest
```

### Re-authentication Required

If your OAuth tokens expire:
1. Run `gemini` in your terminal
2. Complete the OAuth flow in your browser
3. Press `r` to restart after "Authentication succeeded" message

## Usage

### Interactive mode

```bash
gemini
```

### Non-interactive (headless) mode

```bash
gemini -p "Your prompt here"
```

### Common options

| Option | Description |
|--------|-------------|
| `-p, --prompt` | Run in non-interactive mode with given prompt |
| `-m, --model` | Specify model to use |
| `-y, --yolo` | Auto-accept all actions |
| `-r, --resume` | Resume previous session |
| `-v, --version` | Show version |
| `-h, --help` | Show help |

## Configuration

Settings are stored in `~/.gemini/settings.json`:

```json
{
  "security": {
    "auth": {
      "selectedType": "google-cloud"
    }
  },
  "general": {
    "previewFeatures": true,
    "vimMode": true
  }
}
```

## MCP Server Management

```bash
gemini mcp list              # List configured MCP servers
gemini mcp add <name> <cmd>  # Add a server
gemini mcp remove <name>     # Remove a server
gemini mcp enable <name>     # Enable a server
gemini mcp disable <name>    # Disable a server
```

## References

- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Gemini CLI Releases](https://github.com/google-gemini/gemini-cli/releases)
- [Google AI Studio](https://aistudio.google.com/)
