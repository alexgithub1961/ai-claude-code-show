# NotebookLM CLI & MCP Setup Guide

## Overview

`notebooklm-mcp-cli` provides both a CLI tool (`nlm`) and an MCP server (`notebooklm-mcp`) for interacting with Google NotebookLM from the terminal or AI assistants like Claude Code.

> **Note**: This uses unofficial/internal APIs that may change without notice.

## Installation

### Using uv (Recommended)

```bash
uv tool install notebooklm-mcp-cli
```

### Using pip

```bash
pip install notebooklm-mcp-cli
```

### Using pipx

```bash
pipx install notebooklm-mcp-cli
```

### Verify installation

```bash
nlm --version
```

## Authentication

### Initial login

```bash
nlm login
```

This launches Chrome for Google OAuth authentication. Sign in with your Google account that has NotebookLM access.

### Check authentication status

```bash
nlm login --check
```

### Multiple profiles

```bash
# Create named profiles
nlm login --profile work
nlm login --profile personal

# Switch between profiles
nlm login switch work

# List profiles
nlm login profile list

# Delete a profile
nlm login profile delete <name>
```

## Claude Code Integration (MCP Server)

### Add MCP server to Claude Code

```bash
claude mcp add --scope user notebooklm-mcp notebooklm-mcp
```

### Verify connection

```bash
claude mcp list
```

You should see:
```
notebooklm-mcp: notebooklm-mcp - ✓ Connected
```

### Manual configuration

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "notebooklm-mcp"
    }
  }
}
```

### Restart Claude Code

After adding the MCP server, restart Claude Code to load the new tools:

```bash
# Exit and restart, or use /mcp command
```

## CLI Commands

### Notebook management

```bash
nlm notebook list                    # List all notebooks
nlm notebook create "Name"           # Create a notebook
nlm notebook delete <id>             # Delete a notebook
nlm notebook query <id> "question"   # Ask questions about notebook content
```

### Source management

```bash
nlm source add <notebook> --url "https://..."     # Add URL source
nlm source add <notebook> --file path/to/file.pdf # Add file source
nlm source add <notebook> --youtube "video-url"   # Add YouTube video
nlm source list <notebook>                         # List sources
nlm source delete <notebook> <source-id>          # Remove source
```

### Content generation

```bash
nlm audio create <notebook>          # Create audio overview (podcast)
nlm video create <notebook>          # Create video overview
nlm report create <notebook>         # Create report
nlm quiz create <notebook>           # Create quiz
nlm flashcards create <notebook>     # Create flashcards
nlm mindmap create <notebook>        # Create mind map
nlm slides create <notebook>         # Create slide deck
nlm infographic create <notebook>    # Create infographic
```

### Downloads

```bash
nlm download audio <notebook> <artifact-id>    # Download MP3
nlm download video <notebook> <artifact-id>    # Download MP4
nlm download report <notebook> <artifact-id>   # Download report
```

### Sharing

```bash
nlm share public <notebook>              # Make notebook public
nlm share invite <notebook> email@...    # Invite collaborator
```

### Research

```bash
nlm research start "topic"    # Start web research on a topic
```

## Using with Claude Code

Once the MCP server is connected, you can use natural language in Claude Code:

- "List my NotebookLM notebooks"
- "Create a notebook called 'AI Research'"
- "Add this URL as a source to my notebook"
- "Generate an audio podcast from my notebook"
- "Query my notebook about [topic]"

## Configuration

### View config

```bash
nlm config show
```

### Set options

```bash
nlm configure <option> <value>
```

## Troubleshooting

### "Profile not found"

Run `nlm login` to create the default profile.

### "Authentication failed"

Re-authenticate:
```bash
nlm login
```

### MCP server not connecting

1. Check the server is installed: `which notebooklm-mcp`
2. Restart Claude Code
3. Check logs: `claude mcp list` for connection status

### Chrome doesn't launch

Ensure Chrome/Chromium is installed and accessible from the command line.

## References

- [notebooklm-mcp-cli GitHub](https://github.com/jacob-bd/notebooklm-mcp-cli)
- [NotebookLM](https://notebooklm.google.com/)
