# Getting Started with Tokenash

This guide will help you get up and running with Tokenash in under 5 minutes.

## Installation

**Python:**

```bash
# Core package (minimal dependencies)
pip install tokenash

# With proxy server
pip install tokenash[proxy]

# With semantic relevance (for smarter compression)
pip install tokenash[relevance]

# Everything
pip install tokenash[all]
```

**TypeScript / Node.js:**

```bash
npm install tokenash
```

**Docker-native:**

```bash
curl -fsSL https://raw.githubusercontent.com/SamirSengupta/tokenash/main/scripts/install.sh | bash
```

PowerShell:

```powershell
irm https://raw.githubusercontent.com/SamirSengupta/tokenash/main/scripts/install.ps1 | iex
```

See [Docker-native install](docker-install.md) for wrapper behavior, compose usage, and host-integrated `wrap` flows.

If you want Tokenash to stay up in the background and automatically serve supported tools, use [Persistent Installs](persistent-installs.md):

```bash
tokenash install apply --preset persistent-service --providers auto
```

## Quick Start: Proxy Mode (Recommended)

The easiest way to use Tokenash is as a proxy server:

```bash
# Start the proxy
tokenash proxy --port 8787
```

Then point your LLM client at it:

```bash
# Claude Code
ANTHROPIC_BASE_URL=http://localhost:8787 claude

# GitHub Copilot CLI (default Anthropic-style proxy route)
tokenash wrap copilot -- --model claude-sonnet-4-20250514

# OpenAI-compatible clients
OPENAI_BASE_URL=http://localhost:8787/v1 your-app
```

That's it! All your requests now go through Tokenash and get optimized automatically.

## Quick Start: Python SDK

If you want programmatic control:

```python
from tokenash import TokenashClient
from openai import OpenAI

# Create a wrapped client
client = TokenashClient(
    original_client=OpenAI(),
    default_mode="optimize",
)

# Use exactly like the original
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
```

## Modes

### Audit Mode

Observe without modifying:

```python
client = TokenashClient(
    original_client=OpenAI(),
    default_mode="audit",
)
# Logs metrics but doesn't change requests
```

### Optimize Mode

Apply transforms to reduce tokens:

```python
client = TokenashClient(
    original_client=OpenAI(),
    default_mode="optimize",
)
# Compresses tool outputs, aligns cache prefixes, etc.
```

### Simulate Mode

Preview what optimizations would do:

```python
plan = client.chat.completions.simulate(
    model="gpt-4o",
    messages=[...],
)
print(f"Would save {plan.tokens_saved} tokens")
print(f"Transforms: {plan.transforms_applied}")
```

## Next Steps

- [Proxy Server Documentation](proxy.md) - Configure the proxy
- [Transforms Reference](transforms.md) - Understand each transform
- [API Reference](api.md) - Full API documentation
