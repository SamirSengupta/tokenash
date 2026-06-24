"""
Tokenash - The Context Optimization Layer for LLM Applications.

Cut your LLM costs by 50-90% without losing accuracy.

Tokenash wraps LLM clients to provide:
- Smart compression of tool outputs (keeps errors, anomalies, relevant items)
- Cache-aligned prefix optimization for better provider cache hits
- Rolling window token management for long conversations
- Full streaming support with zero accuracy loss

Quick Start:

    from tokenash import TokenashClient, OpenAIProvider
    from openai import OpenAI

    # Wrap your existing client
    client = TokenashClient(
        original_client=OpenAI(),
        provider=OpenAIProvider(),
        default_mode="optimize",
    )

    # Use exactly like the original client
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Hello!"},
        ],
    )

    # Check savings
    stats = client.get_stats()
    print(f"Tokens saved: {stats['session']['tokens_saved_total']}")

Verify It's Working:

    # Validate configuration
    result = client.validate_setup()
    if not result["valid"]:
        print("Issues:", result)

    # Enable logging to see what's happening
    import logging
    logging.basicConfig(level=logging.INFO)
    # INFO:tokenash.transforms.pipeline:Pipeline complete: 45000 -> 4500 tokens

Simulate Before Sending:

    plan = client.chat.completions.simulate(
        model="gpt-4o",
        messages=large_messages,
    )
    print(f"Would save {plan.tokens_saved} tokens")
    print(f"Transforms: {plan.transforms}")

Error Handling:

    from tokenash import TokenashError, ConfigurationError, ProviderError

    try:
        response = client.chat.completions.create(...)
    except ConfigurationError as e:
        print(f"Config issue: {e.details}")
    except TokenashError as e:
        print(f"Tokenash error: {e}")

For more examples, see https://github.com/tokenash-sdk/tokenash/tree/main/examples
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from ._ort import ensure_ort_dylib_pinned
from ._version import __version__  # noqa: F401

# Must run before anything can import `tokenash._core`: on Windows the
# Rust core resolves onnxruntime.dll at runtime (ort load-dynamic), and
# the bare DLL search lands on the Windows ML System32 build, which
# deadlocks ort session init (Win11 24H2+). Windows-gated, idempotent,
# ~microseconds. See `tokenash/_ort.py` for the full story.
ensure_ort_dylib_pinned()

from .compress import CompressConfig, CompressResult, compress, compress_spreadsheet  # noqa: E402

# Keep a real callable bound for the one-function compression API so
# `from tokenash import compress` is never shadowed by the submodule object.

__all__ = [
    # Main client
    "TokenashClient",
    # Providers
    "Provider",
    "TokenCounter",
    "OpenAIProvider",
    "AnthropicProvider",
    # Exceptions
    "TokenashError",
    "ConfigurationError",
    "ProviderError",
    "StorageError",
    "CompressionError",
    "TokenizationError",
    "CacheError",
    "ValidationError",
    "TransformError",
    # Config
    "TokenashConfig",
    "TokenashMode",
    "SmartCrusherConfig",
    "CacheAlignerConfig",
    "CacheOptimizerConfig",
    "RelevanceScorerConfig",
    # Data models
    "Block",
    "CachePrefixMetrics",
    "DiffArtifact",
    "RequestMetrics",
    "SimulationResult",
    "TransformDiff",
    "TransformResult",
    "WasteSignals",
    # Transforms
    "SmartCrusher",
    "CacheAligner",
    "TransformPipeline",
    # Cache optimizers
    "BaseCacheOptimizer",
    "CacheConfig",
    "CacheMetrics",
    "CacheResult",
    "CacheStrategy",
    "OptimizationContext",
    "CacheOptimizerRegistry",
    "AnthropicCacheOptimizer",
    "OpenAICacheOptimizer",
    "GoogleCacheOptimizer",
    "SemanticCache",
    "SemanticCacheLayer",
    # Relevance scoring - BM25 always available, embeddings require sentence-transformers
    "RelevanceScore",
    "RelevanceScorer",
    "BM25Scorer",
    "EmbeddingScorer",
    "HybridScorer",
    "create_scorer",
    "embedding_available",
    # Utilities
    "Tokenizer",
    "count_tokens_text",
    "count_tokens_messages",
    "generate_report",
    # Observability
    "TokenashOtelMetrics",
    "TokenashTracer",
    "LangfuseTracingConfig",
    "OTelMetricsConfig",
    "configure_otel_metrics",
    "configure_langfuse_tracing",
    "get_tokenash_tracer",
    "get_langfuse_tracing_status",
    "get_otel_metrics",
    "get_otel_metrics_status",
    "reset_tokenash_tracing",
    "reset_otel_metrics",
    # Memory - optional hierarchical memory system
    "with_memory",  # Main user-facing API
    "Memory",
    "ScopeLevel",
    "HierarchicalMemory",
    "MemoryConfig",
    "EmbedderBackend",
    # One-function compression API
    "compress",
    "compress_spreadsheet",
    "CompressConfig",
    "CompressResult",
    # Hooks
    "CompressionHooks",
    "CompressContext",
    "CompressEvent",
    # Canonical pipeline
    "PipelineStage",
    "PipelineEvent",
    "PipelineExtensionManager",
    "CANONICAL_PIPELINE_STAGES",
    # Shared context for multi-agent workflows
    "SharedContext",
]

# Keep package-level imports lightweight so `import tokenash` does not eagerly
# load provider SDKs, ML stacks, or optional proxy/runtime integrations.
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    # Main client
    "TokenashClient": ("tokenash.client", "TokenashClient"),
    # Providers
    "Provider": ("tokenash.providers", "Provider"),
    "TokenCounter": ("tokenash.providers", "TokenCounter"),
    "OpenAIProvider": ("tokenash.providers", "OpenAIProvider"),
    "AnthropicProvider": ("tokenash.providers", "AnthropicProvider"),
    # Exceptions
    "TokenashError": ("tokenash.exceptions", "TokenashError"),
    "ConfigurationError": ("tokenash.exceptions", "ConfigurationError"),
    "ProviderError": ("tokenash.exceptions", "ProviderError"),
    "StorageError": ("tokenash.exceptions", "StorageError"),
    "CompressionError": ("tokenash.exceptions", "CompressionError"),
    "TokenizationError": ("tokenash.exceptions", "TokenizationError"),
    "CacheError": ("tokenash.exceptions", "CacheError"),
    "ValidationError": ("tokenash.exceptions", "ValidationError"),
    "TransformError": ("tokenash.exceptions", "TransformError"),
    # Config
    "TokenashConfig": ("tokenash.config", "TokenashConfig"),
    "TokenashMode": ("tokenash.config", "TokenashMode"),
    "SmartCrusherConfig": ("tokenash.config", "SmartCrusherConfig"),
    "CacheAlignerConfig": ("tokenash.config", "CacheAlignerConfig"),
    "CacheOptimizerConfig": ("tokenash.config", "CacheOptimizerConfig"),
    "RelevanceScorerConfig": ("tokenash.config", "RelevanceScorerConfig"),
    # Data models
    "Block": ("tokenash.config", "Block"),
    "CachePrefixMetrics": ("tokenash.config", "CachePrefixMetrics"),
    "DiffArtifact": ("tokenash.config", "DiffArtifact"),
    "RequestMetrics": ("tokenash.config", "RequestMetrics"),
    "SimulationResult": ("tokenash.config", "SimulationResult"),
    "TransformDiff": ("tokenash.config", "TransformDiff"),
    "TransformResult": ("tokenash.config", "TransformResult"),
    "WasteSignals": ("tokenash.config", "WasteSignals"),
    # Transforms
    "SmartCrusher": ("tokenash.transforms", "SmartCrusher"),
    "CacheAligner": ("tokenash.transforms", "CacheAligner"),
    "TransformPipeline": ("tokenash.transforms", "TransformPipeline"),
    # Cache optimizers
    "BaseCacheOptimizer": ("tokenash.cache", "BaseCacheOptimizer"),
    "CacheConfig": ("tokenash.cache", "CacheConfig"),
    "CacheMetrics": ("tokenash.cache", "CacheMetrics"),
    "CacheResult": ("tokenash.cache", "CacheResult"),
    "CacheStrategy": ("tokenash.cache", "CacheStrategy"),
    "OptimizationContext": ("tokenash.cache", "OptimizationContext"),
    "CacheOptimizerRegistry": ("tokenash.cache", "CacheOptimizerRegistry"),
    "AnthropicCacheOptimizer": ("tokenash.cache", "AnthropicCacheOptimizer"),
    "OpenAICacheOptimizer": ("tokenash.cache", "OpenAICacheOptimizer"),
    "GoogleCacheOptimizer": ("tokenash.cache", "GoogleCacheOptimizer"),
    "SemanticCache": ("tokenash.cache", "SemanticCache"),
    "SemanticCacheLayer": ("tokenash.cache", "SemanticCacheLayer"),
    # Relevance scoring
    "RelevanceScore": ("tokenash.relevance", "RelevanceScore"),
    "RelevanceScorer": ("tokenash.relevance", "RelevanceScorer"),
    "BM25Scorer": ("tokenash.relevance", "BM25Scorer"),
    "EmbeddingScorer": ("tokenash.relevance", "EmbeddingScorer"),
    "HybridScorer": ("tokenash.relevance", "HybridScorer"),
    "create_scorer": ("tokenash.relevance", "create_scorer"),
    "embedding_available": ("tokenash.relevance", "embedding_available"),
    # Utilities
    "Tokenizer": ("tokenash.tokenizer", "Tokenizer"),
    "count_tokens_text": ("tokenash.tokenizer", "count_tokens_text"),
    "count_tokens_messages": ("tokenash.tokenizer", "count_tokens_messages"),
    "generate_report": ("tokenash.reporting", "generate_report"),
    # Observability
    "TokenashOtelMetrics": ("tokenash.observability", "TokenashOtelMetrics"),
    "TokenashTracer": ("tokenash.observability", "TokenashTracer"),
    "LangfuseTracingConfig": ("tokenash.observability", "LangfuseTracingConfig"),
    "OTelMetricsConfig": ("tokenash.observability", "OTelMetricsConfig"),
    "configure_otel_metrics": ("tokenash.observability", "configure_otel_metrics"),
    "configure_langfuse_tracing": ("tokenash.observability", "configure_langfuse_tracing"),
    "get_tokenash_tracer": ("tokenash.observability", "get_tokenash_tracer"),
    "get_langfuse_tracing_status": ("tokenash.observability", "get_langfuse_tracing_status"),
    "get_otel_metrics": ("tokenash.observability", "get_otel_metrics"),
    "get_otel_metrics_status": ("tokenash.observability", "get_otel_metrics_status"),
    "reset_tokenash_tracing": ("tokenash.observability", "reset_tokenash_tracing"),
    "reset_otel_metrics": ("tokenash.observability", "reset_otel_metrics"),
    # One-function API
    "compress": ("tokenash.compress", "compress"),
    "compress_spreadsheet": ("tokenash.compress", "compress_spreadsheet"),
    # Hooks
    "CompressionHooks": ("tokenash.hooks", "CompressionHooks"),
    "CompressContext": ("tokenash.hooks", "CompressContext"),
    "CompressEvent": ("tokenash.hooks", "CompressEvent"),
    # Canonical pipeline
    "PipelineStage": ("tokenash.pipeline", "PipelineStage"),
    "PipelineEvent": ("tokenash.pipeline", "PipelineEvent"),
    "PipelineExtensionManager": ("tokenash.pipeline", "PipelineExtensionManager"),
    "CANONICAL_PIPELINE_STAGES": ("tokenash.pipeline", "CANONICAL_PIPELINE_STAGES"),
    # Shared context
    "SharedContext": ("tokenash.shared_context", "SharedContext"),
}

# Memory remains optional and preserves the long-standing behavior of exposing
# `None` when the extra dependencies are not installed.
_OPTIONAL_EXPORTS = {
    "with_memory": ("tokenash.memory", "with_memory"),
    "Memory": ("tokenash.memory", "Memory"),
    "ScopeLevel": ("tokenash.memory", "ScopeLevel"),
    "HierarchicalMemory": ("tokenash.memory", "HierarchicalMemory"),
    "MemoryConfig": ("tokenash.memory", "MemoryConfig"),
    "EmbedderBackend": ("tokenash.memory", "EmbedderBackend"),
}


def __getattr__(name: str) -> Any:
    """Resolve package exports lazily while preserving legacy import paths."""
    module_attr = _LAZY_EXPORTS.get(name)
    if module_attr is not None:
        module_name, attr_name = module_attr
        value = getattr(import_module(module_name), attr_name)
        globals()[name] = value
        return value

    optional_module_attr = _OPTIONAL_EXPORTS.get(name)
    if optional_module_attr is not None:
        module_name, attr_name = optional_module_attr
        try:
            value = getattr(import_module(module_name), attr_name)
        except ImportError:
            value = None
        globals()[name] = value
        return value

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
