# SDK Guide

The Tokenash SDK wraps your existing LLM client to add compression and optimization transparently.

## Installation

```bash
pip install tokenash openai
```

## Quick Start

```python
from tokenash import TokenashClient, OpenAIProvider
from openai import OpenAI

# Create wrapped client
client = TokenashClient(
    original_client=OpenAI(),
    provider=OpenAIProvider(),
    default_mode="optimize",
)

# Use exactly like the original client
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Hello!"},
    ],
)

print(response.choices[0].message.content)
```

## Tool Output Compression

Real savings happen with tool outputs. Here's where Tokenash shines:

```python
import json

# Conversation with large tool output
messages = [
    {"role": "user", "content": "Search for Python tutorials"},
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": "call_123",
            "type": "function",
            "function": {"name": "search", "arguments": '{"q": "python"}'},
        }],
    },
    {
        "role": "tool",
        "tool_call_id": "call_123",
        "content": json.dumps({
            "results": [
                {"title": f"Tutorial {i}", "score": 100-i}
                for i in range(500)
            ]
        }),
    },
    {"role": "user", "content": "What are the top 3?"},
]

# Tokenash compresses 500 results to ~15, keeping highest-scoring items
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages
)

# Check savings
stats = client.get_stats()
print(f"Tokens saved: {stats['session']['tokens_saved_total']}")
# Typical output: "Tokens saved: 3500"
```

## Supported Providers

### OpenAI

```python
from tokenash import TokenashClient, OpenAIProvider
from openai import OpenAI

client = TokenashClient(
    original_client=OpenAI(),
    provider=OpenAIProvider(),
)
```

### Anthropic

```python
from tokenash import TokenashClient, AnthropicProvider
from anthropic import Anthropic

client = TokenashClient(
    original_client=Anthropic(),
    provider=AnthropicProvider(),
)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
```

### Google

```python
from tokenash import TokenashClient, GoogleProvider
import google.generativeai as genai

client = TokenashClient(
    original_client=genai,
    provider=GoogleProvider(),
)
```

## Check Stats

```python
# Session stats (no database query)
stats = client.get_stats()
print(stats)
# {
#   "session": {"requests_total": 10, "tokens_saved_total": 5000, ...},
#   "config": {"mode": "optimize", "provider": "openai", ...},
#   "transforms": {"smart_crusher_enabled": True, ...}
# }
```

## Validate Setup

```python
result = client.validate_setup()
if not result["valid"]:
    print("Setup issues:", result["issues"])
```

## Modes

### Optimize (Default)

Applies all safe transforms:

```python
client = TokenashClient(
    original_client=OpenAI(),
    provider=OpenAIProvider(),
    default_mode="optimize",
)
```

### Audit

Observes and logs without modifying:

```python
client = TokenashClient(
    original_client=OpenAI(),
    provider=OpenAIProvider(),
    default_mode="audit",
)
```

### Simulate

Returns a plan without making the API call:

```python
plan = client.chat.completions.simulate(
    model="gpt-4o",
    messages=large_conversation,
)

print(f"Would save {plan.tokens_saved} tokens")
print(f"Transforms: {plan.transforms}")
```

## Per-Request Overrides

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],

    # Override mode for this request
    tokenash_mode="audit",

    # Reserve more tokens for output
    tokenash_output_buffer_tokens=8000,

    # Keep last N turns
    tokenash_keep_turns=5,
)
```

## Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

# Now you'll see:
# INFO:tokenash.transforms.pipeline:Pipeline complete: 45000 -> 4500 tokens
# INFO:tokenash.transforms.smart_crusher:SmartCrusher: kept 15 of 1000 items
```

## Streaming

Streaming works transparently:

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Error Handling

```python
from tokenash import (
    TokenashClient,
    TokenashError,
    ConfigurationError,
    ProviderError,
)

try:
    response = client.chat.completions.create(...)
except ConfigurationError as e:
    print(f"Config issue: {e}")
except ProviderError as e:
    print(f"Provider issue: {e}")
except TokenashError as e:
    print(f"Tokenash error: {e}")
```

## Historical Metrics

Query stored metrics:

```python
from datetime import datetime, timedelta

metrics = client.get_metrics(
    start_time=datetime.utcnow() - timedelta(hours=1),
    limit=100,
)

for m in metrics:
    print(f"{m.timestamp}: {m.tokens_input_before} -> {m.tokens_input_after}")
```

## Advanced Configuration

See [Configuration](configuration.md) for full options:

```python
client = TokenashClient(
    original_client=OpenAI(),
    provider=OpenAIProvider(),
    default_mode="optimize",
    enable_cache_optimizer=True,
    enable_semantic_cache=False,
    model_context_limits={
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
    },
)
```

## Comparison with Proxy

| Aspect | SDK | Proxy |
|--------|-----|-------|
| Setup | Wrap client | Point URL |
| Control | Fine-grained | Global |
| Metrics | In-process | Centralized |
| Best for | Custom apps | Existing tools |

Use the SDK when you need fine-grained control. Use the proxy for existing tools like Claude Code, Cursor, etc.
