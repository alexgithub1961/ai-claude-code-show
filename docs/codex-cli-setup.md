# Codex CLI Setup Guide

## Overview

OpenAI Codex CLI is an AI-powered coding assistant that runs in your terminal. It supports OpenAI API, Azure OpenAI, and local models (LM Studio/Ollama).

## Installation

### Using npm (Recommended)

```bash
npm install -g @openai/codex
```

### Verify installation

```bash
codex --version
```

## Authentication

### Option 1: OpenAI API

```bash
export OPENAI_API_KEY="your-api-key"
codex
```

Or login interactively:
```bash
codex login
```

### Option 2: Azure OpenAI

Create `~/.codex/config.toml`:

```toml
model_provider = "azure"
model = "your-deployment-name"  # Must match exact Azure deployment name

[model_providers.azure]
name = "Azure OpenAI"
base_url = "https://your-resource.openai.azure.com/openai"
env_key = "AZURE_OPENAI_API_KEY"  # Environment variable containing API key
wire_api = "responses"
query_params = { api-version = "2024-12-01-preview" }
```

Set the environment variable:
```bash
export AZURE_OPENAI_API_KEY="your-azure-api-key"
```

### Option 3: Local Models (Ollama/LM Studio)

```bash
codex --oss
# or
codex --local-provider ollama
codex --local-provider lmstudio
```

## Configuration

Config file location: `~/.codex/config.toml`

### Full Azure Example

```toml
# ~/.codex/config.toml

model_provider = "azure"
model = "gpt-5.1-codex"  # Your Azure deployment name

[model_providers.azure]
name = "Azure GPT-5.1-Codex"
base_url = "https://your-resource.openai.azure.com/openai"
env_key = "AZURE_OPENAI_API_KEY"
wire_api = "responses"
query_params = { api-version = "2024-12-01-preview" }
stream_max_retries = 10
stream_idle_timeout_ms = 120000

[tools]
shell = { allowed = ["git *", "cd *"] }

[git]
worktree_base_dir = "../worktrees"
```

### Trust Projects

Add trusted project directories to skip confirmation prompts:

```toml
[projects."/path/to/your/project"]
trust_level = "trusted"
```

## Usage

### Interactive Mode

```bash
codex "your prompt"
codex -i "initial prompt"  # Continue interactively after prompt
```

### Non-Interactive (Headless)

```bash
codex exec "your prompt"
codex e "your prompt"  # Alias
```

### Code Review

```bash
codex review
```

### Sandbox Modes

```bash
codex -s read-only "prompt"        # Read-only (safest)
codex -s workspace-write "prompt"  # Can write to workspace
codex -s danger-full-access "prompt"  # Full access (dangerous)
```

### Approval Policies

```bash
codex -a untrusted "prompt"   # Ask for untrusted commands
codex -a on-failure "prompt"  # Only ask when commands fail
codex -a on-request "prompt"  # Model decides when to ask
codex -a never "prompt"       # Never ask (use with sandbox)
```

### Full Auto Mode

Low-friction automatic execution with workspace sandbox:
```bash
codex --full-auto "prompt"
```

### Resume Sessions

```bash
codex resume          # Pick from list
codex resume --last   # Resume most recent
```

### Specify Model

```bash
codex -m gpt-4o "prompt"
codex -m o3 "prompt"
```

## MCP Server (Experimental)

Run Codex as an MCP server:

```bash
codex mcp-server
```

Manage MCP servers:
```bash
codex mcp list
codex mcp add <name> <command>
codex mcp remove <name>
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `codex "prompt"` | Interactive mode |
| `codex exec "prompt"` | Non-interactive |
| `codex review` | Code review |
| `codex resume` | Resume session |
| `codex login status` | Check auth status |
| `codex --full-auto "prompt"` | Auto mode with sandbox |
| `codex -m <model> "prompt"` | Specify model |

## Troubleshooting

### 401 Unauthorized (Azure)

1. **Check deployment name**: Must match exactly what's in Azure portal
   ```bash
   az cognitiveservices account deployment list --name <resource> --resource-group <rg> -o table
   ```

2. **Check API key**: Ensure `env_key` points to correct environment variable
   ```bash
   echo $AZURE_OPENAI_API_KEY | head -c 20
   ```

3. **Check endpoint**: Verify `base_url` matches your Azure resource

### "Not logged in" with Azure

This is normal - Azure uses API key auth, not login. Check config file instead.

### Model Not Found

Ensure `model` in config.toml matches your Azure deployment name exactly (case-sensitive).

## Finding Azure Deployment Names

```bash
# List all Azure OpenAI resources
az cognitiveservices account list --query "[?kind=='OpenAI'].{name:name,endpoint:properties.endpoint}" -o table

# List deployments on a resource
az cognitiveservices account deployment list --name <resource-name> --resource-group <rg> -o table

# Get API key
az cognitiveservices account keys list --name <resource-name> --resource-group <rg> -o json
```

## References

- [Codex CLI GitHub](https://github.com/openai/codex)
- [Azure OpenAI Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/)
