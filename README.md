<div align="center"><pre>
  ████████╗  ██████╗  ██╗  ██╗ ███████╗ ███╗   ██╗  █████╗  ███████╗ ██╗  ██╗
  ╚══██╔══╝ ██╔═══██╗ ██║ ██╔╝ ██╔════╝ ████╗  ██║ ██╔══██╗ ██╔════╝ ██║  ██║
     ██║    ██║   ██║ █████╔╝  █████╗   ██╔██╗ ██║ ███████║ ███████╗ ███████║
     ██║    ██║   ██║ ██╔═██╗  ██╔══╝   ██║╚██╗██║ ██╔══██║ ╚════██║ ██╔══██║
     ██║    ╚██████╔╝ ██║  ██╗ ███████╗ ██║ ╚████║ ██║  ██║ ███████║ ██║  ██║
     ╚═╝     ╚═════╝  ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═══╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝
              The context optimization layer for LLM applications
</pre></div>

<p align="center"><strong>50–90% fewer tokens · same answers · library · proxy · MCP · CLI · local-first · reversible</strong></p>

---

**Tokenash** compresses everything your LLM application or AI agent reads — tool outputs, logs, RAG chunks, files, API responses, and conversation history — **before it reaches the model**. The model gets the same information in a fraction of the tokens, so you cut cost and fit far more into every context window. It runs locally, so your data never leaves your machine, and it's reversible: the full original is cached and can be retrieved on demand.

You can drop Tokenash into any stack four ways: as a **library**, a zero-code **proxy**, an **MCP server**, or a **CLI**.

## Table of contents

- [Why Tokenash](#why-tokenash)
- [How it works](#how-it-works)
- [Install](#install)
- [Quick start](#quick-start)
- [Usage](#usage)
  - [Library](#1-library)
  - [Proxy](#2-proxy-zero-code-any-language)
  - [CLI](#3-cli)
  - [MCP server](#4-mcp-server)
- [What compresses well](#what-compresses-well-honest-expectations)
- [Configuration](#configuration)
- [Benefits](#benefits)
- [Project layout](#project-layout)
- [License](#license)

## Why Tokenash

Large language models are billed per token, and agent loops make it worse: every turn re-sends a growing pile of context, and most of that context is **bloat** — verbose JSON tool results, repetitive log lines, search hits, and stale conversation history. You pay for all of it, on every call, and eventually it overflows the context window entirely.

Tokenash sits between your application and the model and removes that redundancy intelligently:

- It **detects** what each piece of content actually is (JSON, code, logs, prose, search results).
- It **compresses** each type with a purpose-built strategy — losslessly where it can, and conservatively where details matter.
- It **preserves** the original locally, so nothing is permanently lost; the model can ask for the full version if it ever needs it.

The result: the same answers for a fraction of the input tokens, lower bills, and more room in the context window.

## How it works

```
 Your app / agent
   (your code, a coding agent, a framework like LangChain, …)
        │   prompts · tool outputs · logs · RAG results · files
        ▼
   ┌──────────────────────────────────────────────────┐
   │  Tokenash   (runs locally — your data stays here) │
   │  ───────────────────────────────────────────────  │
   │  ContentRouter  →  CacheAligner  →  CCR            │
   │     ├─ SmartCrusher    (JSON, structural)         │
   │     ├─ CodeCompressor  (source code, AST-aware)   │
   │     └─ Kompress        (prose / text, model-based)│
   └──────────────────────────────────────────────────┘
        │   compressed prompt  +  on-demand retrieval
        ▼
 LLM provider  (OpenAI · Anthropic · Gemini · Bedrock · any OpenAI-compatible endpoint)
```

The core pieces:

- **ContentRouter** — inspects each message and routes it to the right compressor based on detected content type. If content isn't worth compressing, it's left untouched.
- **SmartCrusher** — structural compression for JSON. Collapses repetitive arrays and objects down to their schema plus representative samples, so a 200-row API dump becomes a compact, model-readable summary.
- **CodeCompressor** — AST-aware compression for source code: keeps signatures and structure, trims noise.
- **Kompress** — a model-backed compressor for prose and free text, used when structural strategies don't apply.
- **CacheAligner** — stabilizes the prompt prefix so the provider's prompt/KV cache keeps hitting across turns instead of being invalidated.
- **CCR (reversible compression)** — every original is stored locally before compression. If the model needs the full content, it can retrieve it on demand, so compression never loses information permanently.

The performance-critical detection and structural compression run in a small native (Rust) extension; everything else is Python (with a TypeScript SDK for Node).

## Install

Requirements: **Python 3.10+**. Building from source compiles the native extension, so you also need a **Rust toolchain**, and on **Windows** the **C++ Build Tools**.

```bash
# from the project folder
pip install -e .
```

Optional feature extras (install only what you need):

```bash
pip install -e ".[all]"     # everything
pip install -e ".[proxy]"   # the proxy server
pip install -e ".[ml]"      # the Kompress text model
pip install -e ".[code]"    # AST code compression
pip install -e ".[mcp]"     # MCP server
```

### Windows prerequisites

The native module needs a compiler and linker that don't ship with Windows. Install them once:

```bat
winget install Rustlang.Rustup
rustup default stable
winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override "--quiet --wait --norestart --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
```

Open a fresh terminal afterward, then run `pip install -e .`. A successful build ends with `Successfully installed tokenash-…`.

## Quick start

```bash
tokenash --help        # see every command
tokenash perf          # built-in performance/savings report
tokenash proxy         # start the optimization proxy
```

## Usage

### 1. Library

The simplest way to use Tokenash — no proxy, no config. Pass messages, get compressed messages back plus metrics.

```python
from tokenash import compress

result = compress(messages, model="gpt-4o")

print(result.tokens_before, "→", result.tokens_after)   # e.g. 30,631 → 11,485
print(f"{result.compression_ratio:.0%} reduction")        # e.g. 63% reduction
print(result.transforms_applied)                          # which strategies fired

# send result.messages to your LLM instead of the originals
```

`compress()` returns a `CompressResult` with: `messages`, `tokens_before`, `tokens_after`, `tokens_saved`, `compression_ratio`, and `transforms_applied`. Useful keyword arguments:

- `model` — used for token counting and the context limit.
- `compress_user_messages=True` — also compress user-role messages (off by default, which protects the human's prompt).
- `target_ratio=0.4` — be more aggressive on text compression (keep ~40% of tokens).
- `optimize=False` — passthrough mode, for A/B comparisons.

### 2. Proxy (zero code, any language)

Run the proxy and point your existing client at it instead of the provider. No code changes.

```bash
tokenash proxy --port 8787
```

- **OpenAI-style clients:** set the base URL to `http://localhost:8787/v1`.
- **Anthropic-style clients:** set the base URL to `http://localhost:8787`.

Forward to **any** upstream, including an OpenAI-compatible endpoint running locally:

```bash
tokenash proxy --port 8787 --openai-api-url http://127.0.0.1:8317
```

The proxy compresses each request, forwards it on, and streams the response back. Watch the savings live with `tokenash dashboard` or summarize them with `tokenash perf`.

On Windows, set these so the proxy detects and compresses structured content the way the library does:

```bat
set TOKENASH_DETECT_BACKEND=rust
set TOKENASH_COMPRESS_USER_MESSAGES=1
set TOKENASH_PROTECT_RECENT=0
tokenash proxy --port 8787 --mode token
```

### 3. CLI

`tokenash` is the command-line entry point. The most useful commands:

| Command | What it does |
|---|---|
| `tokenash proxy` | Start the optimization proxy server. |
| `tokenash perf` | Analyze proxy logs and report token savings. |
| `tokenash dashboard` | Open the live savings dashboard in your browser. |
| `tokenash doctor` | Check that the proxy and client routing are wired correctly. |
| `tokenash output-savings` | Estimate the reduction in tokens the model writes back. |
| `tokenash learn` | Mine past failed sessions and write corrections to your agent's memory file. |
| `tokenash memory` | Manage the local memory store. |
| `tokenash wrap <tool>` | Run a supported CLI tool through Tokenash automatically. |
| `tokenash mcp` | Run/install the MCP server. |
| `tokenash savings` | Show durable compression savings over time. |
| `tokenash update` | Update Tokenash to the latest release. |

Run `tokenash <command> --help` for the full options on any command.

### 4. MCP server

Expose Tokenash to any MCP-compatible client:

```bash
tokenash mcp install
```

This registers three tools — `tokenash_compress`, `tokenash_retrieve`, and `tokenash_stats` — so an MCP client can compress content, retrieve originals on demand, and read statistics.

## What compresses well (honest expectations)

Tokenash earns its biggest wins on **bloated, repetitive, low-information-density content**: large JSON API responses, log dumps, search results, and RAG chunks. On those it routinely strips **60–90%** of the tokens because the redundancy is real and removing it changes nothing.

On **dense, every-detail-matters content** — a short prompt, or text where each fact shapes the answer — it stays conservative *by design*. It would rather keep the content intact than risk dropping a detail the model needs. So a single small prompt may compress little; that's correct behavior, not a failure. Point Tokenash at the bulky, mechanical parts of your context and let it leave the high-value parts alone.

## Configuration

Most behavior is controlled by environment variables (or the matching `tokenash proxy` flags):

| Variable | Purpose |
|---|---|
| `TOKENASH_DETECT_BACKEND` | `rust` or `python` content detector. Use `rust` on Windows so JSON/code are detected. |
| `TOKENASH_MODE` | `token` (maximize compression) or `cache` (freeze prefixes for max cache hits). |
| `TOKENASH_COMPRESS_USER_MESSAGES` | `1` to also compress user-role messages. |
| `TOKENASH_PROTECT_RECENT` | Number of most-recent messages to leave untouched. |
| `TOKENASH_TARGET_RATIO` | Keep-ratio for text compression (lower = more aggressive). |
| `OPENAI_TARGET_API_URL` | Upstream OpenAI-compatible endpoint the proxy forwards to. |
| `ANTHROPIC_TARGET_API_URL` | Upstream Anthropic endpoint the proxy forwards to. |
| `TOKENASH_OUTPUT_SHAPER` | `1` to also trim the tokens the model writes back. |

## Benefits

- **Lower cost** — 50–90% fewer input tokens on suitable workloads goes straight to your bill.
- **More context** — fit far more into a fixed context window.
- **Reversible** — originals are cached locally and retrievable on demand; nothing is lost.
- **Local-first** — runs entirely on your machine; your data never leaves it.
- **Drop-in** — the proxy needs zero code changes and works with any language.
- **Provider-agnostic** — OpenAI, Anthropic, Gemini, Bedrock, and any OpenAI-compatible endpoint.
- **Observable** — a live dashboard and `perf`/`savings` reports show exactly what you saved.

## Project layout

```
tokenash/          Python package — pipeline, proxy, CLI, transforms, MCP, memory
crates/            Rust core — native content detection and structural compression
sdk/typescript/    TypeScript / Node SDK
plugins/           Integrations and agent plugins
examples/          Usage examples
docs/              Documentation sources
tests/             Test suite
```

## License

Tokenash is released under the **Apache License 2.0** — see [LICENSE](LICENSE). Attribution and third-party notices are in [NOTICE](NOTICE).
