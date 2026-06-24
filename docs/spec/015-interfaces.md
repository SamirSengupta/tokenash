# 015. Interfaces

**Status:** done

## CLI Surface

### `tokenash proxy`

Start the Tokenash proxy server.

```bash
tokenash proxy [OPTIONS]
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Bind host |
| `--port` | `8787` | Bind port |
| `--mode` | `token` | Optimization mode: `token` or `cache` |
| `--workers` | `1` | Uvicorn worker processes |
| `--limit-concurrency` | `1000` | Maximum concurrent connections before 503 |
| `--no-optimize` | `false` | Passthrough mode |
| `--no-cache` | `false` | Disable semantic cache |
| `--no-rate-limit` | `false` | Disable rate limiting |
| `--memory` | `false` | Enable persistent memory |
| `--learn` | `false` | Enable live traffic learning |
| `--backend` | `anthropic` | Backend: anthropic, bedrock, openrouter, anyllm, or litellm-* |
| `--telemetry` | `false` | Opt in to anonymous telemetry (off by default) |
| `--no-telemetry` | `false` | Force anonymous telemetry off (already the default) |
| `--stateless` | `false` | Disable filesystem writes |

---

### `tokenash evals`

Run evaluation suite.

```bash
tokenash evals [OPTIONS]
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--suite` | `all` | Evaluation suite to run |
| `--output` | - | Output file for results |

---

### `tokenash install`

Install agent integrations.

```bash
tokenash install [OPTIONS]
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--agent` | - | Agent type (claude/copilot/codex/aider/cursor/openclaw) |

---

### `tokenash mcp`

Manage the Tokenash MCP server.

```bash
tokenash mcp [OPTIONS] COMMAND [ARGS]...
```

**Commands:**
- `install` — Install the MCP server into detected coding agents
- `serve` — Start the stdio MCP server
- `status` — Check configuration status
- `uninstall` — Remove Tokenash MCP config

---

### `tokenash perf`

Run performance tests.

```bash
tokenash perf [OPTIONS]
```

---

### `tokenash wrap`

Wrap a command with Tokenash proxy.

```bash
tokenash wrap [OPTIONS] -- <command> [args...]
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `8787` | Proxy port |
| `--no-context-tool` / `--no-rtk` | `false` | Skip CLI context-tool setup |

**Supported Commands:**
- `claude` — Wrap Claude Code
- `copilot` — Wrap GitHub Copilot
- `codex` — Wrap OpenAI Codex
- `aider` — Wrap Aider
- `cursor` — Wrap Cursor
- `openclaw` — Wrap OpenClaw

---

### `tokenash memory`

Memory system management (requires numpy/hnswlib).

```bash
tokenash memory [OPTIONS]
```

**Commands:**
- `list` — List stored memories
- `stats` — Show memory statistics
- `search QUERY` — Search memories

---

### `tokenash learn`

Run learn mode analysis.

```bash
tokenash learn [OPTIONS]
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--project` | current directory | Project directory to analyze |
| `--all` | `false` | Analyze all discovered projects |
| `--apply` | `false` | Write recommendations instead of dry-run |
| `--agent` | `auto` | Agent to analyze: auto, claude, codex, gemini, or plugin |
| `--model` | auto | LLM model for analysis |
| `--workers` | auto | Parallel workers for session scanning |

---

### `tokenash stats`

Show savings statistics.

```bash
tokenash stats [OPTIONS]
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--period` | `24h` | Time period |
| `--format` | `table` | Output format (table, json, csv) |

---

### `tokenash config`

Manage configuration.

```bash
tokenash config [COMMAND] [OPTIONS]
```

**Commands:**
- `get KEY` — Get config value
- `set KEY VALUE` — Set config value
- `list` — List all config
- `export` — Export config to file

---

## HTTP API

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/livez` | Liveness check |
| `GET` | `/readyz` | Readiness check |
| `POST` | `/v1/messages` | Proxy chat completions |
| `POST` | `/v1/embeddings` | Proxy embeddings |
| `POST` | `/v1/compress` | Direct compression |
| `POST` | `/v1/retrieve` | CCR retrieval |
| `GET` | `/stats` | Compression statistics |
| `GET` | `/metrics` | Prometheus metrics |

### Request/Response Examples

**POST /v1/messages:**
```bash
curl -X POST http://localhost:8787/v1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-..." \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Response headers:**
```
X-Tokenash-Savings: 0.35
X-Tokenash-Original-Tokens: 8192
X-Tokenash-Compressed-Tokens: 5325
```

---

## Environment Variables

### Core

| Variable | Default | Description |
|----------|---------|-------------|
| `TOKENASH_MODE` | `token` | Proxy optimization mode (`token` or `cache`) |
| `TOKENASH_PORT` | `8787` | Proxy port |
| `TOKENASH_HOST` | `127.0.0.1` | Proxy host |
| `TOKENASH_WORKERS` | `1` | Uvicorn worker count |
| `TOKENASH_LIMIT_CONCURRENCY` | `1000` | Maximum concurrent connections before 503 |
| `TOKENASH_MAX_CONNECTIONS` | `500` | Maximum upstream HTTP connections |
| `TOKENASH_MAX_KEEPALIVE` | `100` | Maximum upstream keep-alive connections |
| `TOKENASH_BUDGET` | - | Daily budget limit in USD |
| `TOKENASH_TELEMETRY` | `off` (opt-in) | Set to `on` to opt in to anonymous telemetry |
| `TOKENASH_STATELESS` | `false` | Disable filesystem writes |

### Provider

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `GOOGLE_API_KEY` | - | Google AI API key |
| `COHERE_API_KEY` | - | Cohere API key |

### Features

| Variable | Default | Description |
|----------|---------|-------------|
| `TOKENASH_TELEMETRY` | `off` (opt-in) | Set to `on` to opt in to telemetry |
| `TOKENASH_MIN_EVIDENCE` | `5` | Minimum observations before live learning persists a pattern |
| `TOKENASH_PROXY_EXTENSIONS` | - | Comma-separated proxy extensions to enable |
| `TOKENASH_STATELESS` | `false` | Disable filesystem writes |
| `TOKENASH_MODEL_LIMITS` | - | Model limits override as JSON or file path |

### Compression

| Variable | Default | Description |
|----------|---------|-------------|
| `TOKENASH_MAX_TOKENS` | `4096` | Max tokens per request |
| `TOKENASH_TARGET_TOKENS` | - | Target tokens after compression |
| `TOKENASH_OVERLAP_TOKENS` | `512` | Overlap tokens for chunking |
| `TOKENASH_CONTENT_SENSITIVITY` | `0.5` | Content sensitivity (0-1) |
| `TOKENASH_PRESERVE_SYSTEM` | `true` | Preserve system messages |

---

## Plugin ABI

### Plugin Interface

```python
from abc import ABC, abstractmethod
from tokenash.learn.base import ConversationScanner, ContextWriter
from tokenash.learn.models import ProjectInfo, SessionData

class LearnPlugin(ConversationScanner):
    """A self-contained learn plugin for a single coding agent."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short lowercase identifier (e.g., 'claude', 'cursor')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g., 'Claude Code', 'Cursor')."""
        ...

    @abstractmethod
    def detect(self) -> bool:
        """Return True if this agent has data on the current machine."""
        ...

    @abstractmethod
    def discover_projects(self) -> list[ProjectInfo]:
        """Discover all projects with conversation data."""
        ...

    @abstractmethod
    def scan_project(self, project: ProjectInfo, max_workers: int = 1) -> list[SessionData]:
        """Scan all sessions for a project."""
        ...

    @abstractmethod
    def create_writer(self) -> ContextWriter:
        """Return the appropriate ContextWriter for this agent."""
        ...
```

### Plugin Registration

Plugins are auto-discovered from `tokenash/learn/plugins/` directory.

**Manual registration:**
```python
from tokenash.learn import plugin_registry

plugin_registry.register(MyPlugin())
```

### Plugin Config

```yaml
# ~/.tokenash/config.yaml
learn:
  enabled: true
  plugins:
    - name: claude
      enabled: true
      config:
        session_modes:
          - auto
          - learn
          - disabled
    - name: my_plugin
      enabled: true
      config:
        custom_option: value
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0-draft | 2026-04-16 | Initial interfaces document |
