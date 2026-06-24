"""Tokenash Cache Optimization Module.

This module provides a plugin-based architecture for cache optimization
across different LLM providers. Each provider has different caching
mechanisms and this module abstracts those differences.

Provider Caching Differences:
- Anthropic: Explicit cache_control blocks, 90% savings, 5-min TTL
- OpenAI: Automatic prefix caching, 50% savings, no user control
- Google: Separate CachedContent API, 75% savings + storage costs

Usage:
    from tokenash.cache import CacheOptimizerRegistry, SemanticCacheLayer

    # Get provider-specific optimizer
    optimizer = CacheOptimizerRegistry.get("anthropic")
    result = optimizer.optimize(messages, context)

    # With semantic caching layer
    semantic = SemanticCacheLayer(optimizer, similarity_threshold=0.95)
    result = semantic.process(messages, context)

    # Register custom optimizer
    CacheOptimizerRegistry.register("my-provider", MyOptimizer)
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Expose concrete types to static analysis while keeping runtime imports lazy.
    from tokenash.cache.anthropic import AnthropicCacheOptimizer  # noqa: F401
    from tokenash.cache.base import (  # noqa: F401
        BaseCacheOptimizer,
        CacheBreakpoint,
        CacheConfig,
        CacheMetrics,
        CacheOptimizer,
        CacheResult,
        CacheStrategy,
        OptimizationContext,
    )
    from tokenash.cache.compression_cache import CompressionCache  # noqa: F401
    from tokenash.cache.dynamic_detector import (  # noqa: F401
        DetectorConfig,
        DynamicCategory,
        DynamicContentDetector,
        DynamicSpan,
        detect_dynamic_content,
    )
    from tokenash.cache.google import GoogleCacheOptimizer  # noqa: F401
    from tokenash.cache.openai import OpenAICacheOptimizer  # noqa: F401
    from tokenash.cache.prefix_tracker import (  # noqa: F401
        FreezeStats,
        PrefixCacheTracker,
        PrefixFreezeConfig,
        SessionTrackerStore,
    )
    from tokenash.cache.registry import CacheOptimizerRegistry  # noqa: F401
    from tokenash.cache.semantic import SemanticCache, SemanticCacheLayer  # noqa: F401

__all__ = [
    # Base types
    "BaseCacheOptimizer",
    "CacheBreakpoint",
    "CacheConfig",
    "CacheMetrics",
    "CacheOptimizer",
    "CacheResult",
    "CacheStrategy",
    "OptimizationContext",
    # Dynamic content detection
    "DetectorConfig",
    "DynamicCategory",
    "DynamicContentDetector",
    "DynamicSpan",
    "detect_dynamic_content",
    # Registry
    "CacheOptimizerRegistry",
    # Provider implementations
    "AnthropicCacheOptimizer",
    "OpenAICacheOptimizer",
    "GoogleCacheOptimizer",
    # Semantic caching
    "SemanticCacheLayer",
    "SemanticCache",
    # Compression cache (token tokenash mode)
    "CompressionCache",
    # Prefix cache tracking
    "PrefixCacheTracker",
    "PrefixFreezeConfig",
    "FreezeStats",
    "SessionTrackerStore",
]

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    # Base types
    "BaseCacheOptimizer": ("tokenash.cache.base", "BaseCacheOptimizer"),
    "CacheBreakpoint": ("tokenash.cache.base", "CacheBreakpoint"),
    "CacheConfig": ("tokenash.cache.base", "CacheConfig"),
    "CacheMetrics": ("tokenash.cache.base", "CacheMetrics"),
    "CacheOptimizer": ("tokenash.cache.base", "CacheOptimizer"),
    "CacheResult": ("tokenash.cache.base", "CacheResult"),
    "CacheStrategy": ("tokenash.cache.base", "CacheStrategy"),
    "OptimizationContext": ("tokenash.cache.base", "OptimizationContext"),
    # Dynamic content detection
    "DetectorConfig": ("tokenash.cache.dynamic_detector", "DetectorConfig"),
    "DynamicCategory": ("tokenash.cache.dynamic_detector", "DynamicCategory"),
    "DynamicContentDetector": ("tokenash.cache.dynamic_detector", "DynamicContentDetector"),
    "DynamicSpan": ("tokenash.cache.dynamic_detector", "DynamicSpan"),
    "detect_dynamic_content": ("tokenash.cache.dynamic_detector", "detect_dynamic_content"),
    # Registry
    "CacheOptimizerRegistry": ("tokenash.cache.registry", "CacheOptimizerRegistry"),
    # Provider implementations
    "AnthropicCacheOptimizer": ("tokenash.cache.anthropic", "AnthropicCacheOptimizer"),
    "OpenAICacheOptimizer": ("tokenash.cache.openai", "OpenAICacheOptimizer"),
    "GoogleCacheOptimizer": ("tokenash.cache.google", "GoogleCacheOptimizer"),
    # Semantic caching
    "SemanticCacheLayer": ("tokenash.cache.semantic", "SemanticCacheLayer"),
    "SemanticCache": ("tokenash.cache.semantic", "SemanticCache"),
    # Compression cache
    "CompressionCache": ("tokenash.cache.compression_cache", "CompressionCache"),
    # Prefix cache tracking
    "PrefixCacheTracker": ("tokenash.cache.prefix_tracker", "PrefixCacheTracker"),
    "PrefixFreezeConfig": ("tokenash.cache.prefix_tracker", "PrefixFreezeConfig"),
    "FreezeStats": ("tokenash.cache.prefix_tracker", "FreezeStats"),
    "SessionTrackerStore": ("tokenash.cache.prefix_tracker", "SessionTrackerStore"),
}


def __getattr__(name: str) -> object:
    if name == "__path__":
        raise AttributeError(name)

    try:
        module_name, attr_name = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
