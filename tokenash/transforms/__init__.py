"""Transform modules for Tokenash SDK."""

from __future__ import annotations

import importlib.util
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Expose concrete types to static analysis while keeping runtime imports lazy.
    from tokenash.transforms.anchor_selector import (  # noqa: F401
        AnchorSelector,
        AnchorStrategy,
        AnchorWeights,
        DataPattern,
        calculate_information_score,
        compute_item_hash,
    )
    from tokenash.transforms.base import Transform  # noqa: F401
    from tokenash.transforms.cache_aligner import CacheAligner  # noqa: F401
    from tokenash.transforms.code_compressor import (  # noqa: F401
        CodeAwareCompressor,
        CodeCompressionResult,
        CodeCompressorConfig,
        CodeLanguage,
        DocstringMode,
        detect_language,
        is_tree_sitter_available,
    )
    from tokenash.transforms.content_detector import (  # noqa: F401
        ContentType,
        DetectionResult,
        detect_content_type,
    )
    from tokenash.transforms.content_router import (  # noqa: F401
        CompressionStrategy,
        ContentRouter,
        ContentRouterConfig,
        RouterCompressionResult,
    )
    from tokenash.transforms.diff_compressor import (  # noqa: F401
        DiffCompressionResult,
        DiffCompressor,
        DiffCompressorConfig,
    )
    from tokenash.transforms.html_extractor import (  # noqa: F401
        HTMLExtractionResult,
        HTMLExtractor,
        HTMLExtractorConfig,
        is_html_content,
    )
    from tokenash.transforms.log_compressor import (  # noqa: F401
        LogCompressionResult,
        LogCompressor,
        LogCompressorConfig,
    )
    from tokenash.transforms.pipeline import TransformPipeline  # noqa: F401
    from tokenash.transforms.search_compressor import (  # noqa: F401
        SearchCompressionResult,
        SearchCompressor,
        SearchCompressorConfig,
    )
    from tokenash.transforms.smart_crusher import SmartCrusher, SmartCrusherConfig  # noqa: F401
    from tokenash.transforms.tabular_ingest import (  # noqa: F401
        TabularCompressionResult,
        TabularCompressor,
        TabularCompressorConfig,
    )

_HTML_EXTRACTOR_AVAILABLE = importlib.util.find_spec("trafilatura") is not None

__all__ = [
    # Base
    "Transform",
    "TransformPipeline",
    # Anchor selection
    "AnchorSelector",
    "AnchorStrategy",
    "AnchorWeights",
    "DataPattern",
    "calculate_information_score",
    "compute_item_hash",
    # JSON compression
    "SmartCrusher",
    "SmartCrusherConfig",
    # Text compression (coding tasks)
    "ContentType",
    "DetectionResult",
    "detect_content_type",
    "SearchCompressor",
    "SearchCompressorConfig",
    "SearchCompressionResult",
    "LogCompressor",
    "LogCompressorConfig",
    "LogCompressionResult",
    "TabularCompressor",
    "TabularCompressorConfig",
    "TabularCompressionResult",
    "DiffCompressor",
    "DiffCompressorConfig",
    "DiffCompressionResult",
    # Code-aware compression (AST-based)
    "CodeAwareCompressor",
    "CodeCompressorConfig",
    "CodeCompressionResult",
    "CodeLanguage",
    "DocstringMode",
    "detect_language",
    "is_tree_sitter_available",
    # Content routing
    "ContentRouter",
    "ContentRouterConfig",
    "RouterCompressionResult",
    "CompressionStrategy",
    # Other transforms
    "CacheAligner",
    # HTML extraction (optional)
    "_HTML_EXTRACTOR_AVAILABLE",
]

# Conditionally add HTML extractor exports
if _HTML_EXTRACTOR_AVAILABLE:
    __all__.extend(
        [
            "HTMLExtractor",
            "HTMLExtractorConfig",
            "HTMLExtractionResult",
            "is_html_content",
        ]
    )

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    # Base
    "Transform": ("tokenash.transforms.base", "Transform"),
    "TransformPipeline": ("tokenash.transforms.pipeline", "TransformPipeline"),
    # Anchor selection
    "AnchorSelector": ("tokenash.transforms.anchor_selector", "AnchorSelector"),
    "AnchorStrategy": ("tokenash.transforms.anchor_selector", "AnchorStrategy"),
    "AnchorWeights": ("tokenash.transforms.anchor_selector", "AnchorWeights"),
    "DataPattern": ("tokenash.transforms.anchor_selector", "DataPattern"),
    "calculate_information_score": (
        "tokenash.transforms.anchor_selector",
        "calculate_information_score",
    ),
    "compute_item_hash": ("tokenash.transforms.anchor_selector", "compute_item_hash"),
    # JSON compression
    "SmartCrusher": ("tokenash.transforms.smart_crusher", "SmartCrusher"),
    "SmartCrusherConfig": ("tokenash.transforms.smart_crusher", "SmartCrusherConfig"),
    # Text compression (coding tasks)
    "ContentType": ("tokenash.transforms.content_detector", "ContentType"),
    "DetectionResult": ("tokenash.transforms.content_detector", "DetectionResult"),
    "detect_content_type": ("tokenash.transforms.content_detector", "detect_content_type"),
    "SearchCompressor": ("tokenash.transforms.search_compressor", "SearchCompressor"),
    "SearchCompressorConfig": (
        "tokenash.transforms.search_compressor",
        "SearchCompressorConfig",
    ),
    "SearchCompressionResult": (
        "tokenash.transforms.search_compressor",
        "SearchCompressionResult",
    ),
    "LogCompressor": ("tokenash.transforms.log_compressor", "LogCompressor"),
    "LogCompressorConfig": ("tokenash.transforms.log_compressor", "LogCompressorConfig"),
    "LogCompressionResult": ("tokenash.transforms.log_compressor", "LogCompressionResult"),
    "TabularCompressor": ("tokenash.transforms.tabular_ingest", "TabularCompressor"),
    "TabularCompressorConfig": (
        "tokenash.transforms.tabular_ingest",
        "TabularCompressorConfig",
    ),
    "TabularCompressionResult": (
        "tokenash.transforms.tabular_ingest",
        "TabularCompressionResult",
    ),
    "DiffCompressor": ("tokenash.transforms.diff_compressor", "DiffCompressor"),
    "DiffCompressorConfig": ("tokenash.transforms.diff_compressor", "DiffCompressorConfig"),
    "DiffCompressionResult": (
        "tokenash.transforms.diff_compressor",
        "DiffCompressionResult",
    ),
    # Code-aware compression (AST-based)
    "CodeAwareCompressor": ("tokenash.transforms.code_compressor", "CodeAwareCompressor"),
    "CodeCompressorConfig": ("tokenash.transforms.code_compressor", "CodeCompressorConfig"),
    "CodeCompressionResult": (
        "tokenash.transforms.code_compressor",
        "CodeCompressionResult",
    ),
    "CodeLanguage": ("tokenash.transforms.code_compressor", "CodeLanguage"),
    "DocstringMode": ("tokenash.transforms.code_compressor", "DocstringMode"),
    "detect_language": ("tokenash.transforms.code_compressor", "detect_language"),
    "is_tree_sitter_available": (
        "tokenash.transforms.code_compressor",
        "is_tree_sitter_available",
    ),
    # Content routing
    "ContentRouter": ("tokenash.transforms.content_router", "ContentRouter"),
    "ContentRouterConfig": ("tokenash.transforms.content_router", "ContentRouterConfig"),
    "RouterCompressionResult": (
        "tokenash.transforms.content_router",
        "RouterCompressionResult",
    ),
    "CompressionStrategy": ("tokenash.transforms.content_router", "CompressionStrategy"),
    # Other transforms
    "CacheAligner": ("tokenash.transforms.cache_aligner", "CacheAligner"),
    # HTML extraction (optional dependency - requires trafilatura)
    "HTMLExtractor": ("tokenash.transforms.html_extractor", "HTMLExtractor"),
    "HTMLExtractorConfig": ("tokenash.transforms.html_extractor", "HTMLExtractorConfig"),
    "HTMLExtractionResult": ("tokenash.transforms.html_extractor", "HTMLExtractionResult"),
    "is_html_content": ("tokenash.transforms.html_extractor", "is_html_content"),
}


def __getattr__(name: str) -> object:
    if name == "__path__":
        raise AttributeError(name)
    if name == "_HTML_EXTRACTOR_AVAILABLE":
        return _HTML_EXTRACTOR_AVAILABLE

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
