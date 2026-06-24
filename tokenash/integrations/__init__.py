"""Tokenash integrations with popular LLM frameworks.

Available integrations:

LangChain (pip install tokenash[langchain]):
    - TokenashChatModel: Drop-in wrapper for any LangChain chat model
    - TokenashChatMessageHistory: Automatic conversation compression
    - TokenashDocumentCompressor: Relevance-based document filtering
    - TokenashToolWrapper: Tool output compression for agents
    - StreamingMetricsTracker: Token counting during streaming
    - TokenashLangSmithCallbackHandler: LangSmith trace enrichment

Agno (pip install agno):
    - TokenashAgnoModel: Drop-in wrapper for any Agno model
    - TokenashPreHook/TokenashPostHook: Agent-level hooks for tracking
    - create_tokenash_hooks: Convenience function to create hook pairs

MCP (Model Context Protocol):
    - TokenashMCPCompressor: Compress MCP tool results
    - compress_tool_result: Simple function for tool compression

Example:
    # LangChain integration
    from tokenash.integrations import TokenashChatModel
    # or explicitly:
    from tokenash.integrations.langchain import TokenashChatModel

    # Agno integration
    from tokenash.integrations.agno import TokenashAgnoModel
    # or explicitly:
    from tokenash.integrations.agno import TokenashAgnoModel

    # MCP integration
    from tokenash.integrations import compress_tool_result
    # or explicitly:
    from tokenash.integrations.mcp import compress_tool_result
"""

# Re-export from langchain subpackage for backwards compatibility
from .langchain import (
    # Retrievers
    CompressionMetrics,
    # Core
    TokenashCallbackHandler,
    # Memory
    TokenashChatMessageHistory,
    TokenashChatModel,
    TokenashDocumentCompressor,
    # LangSmith
    TokenashLangSmithCallbackHandler,
    TokenashRunnable,
    # Agents
    TokenashToolWrapper,
    OptimizationMetrics,
    # Streaming
    StreamingMetrics,
    StreamingMetricsCallback,
    StreamingMetricsTracker,
    ToolCompressionMetrics,
    ToolMetricsCollector,
    # Provider Detection
    detect_provider,
    get_tokenash_provider,
    get_model_name_from_langchain,
    get_tool_metrics,
    is_langsmith_available,
    is_langsmith_tracing_enabled,
    langchain_available,
    optimize_messages,
    reset_tool_metrics,
    track_async_streaming_response,
    track_streaming_response,
    wrap_tools_with_tokenash,
)

# Re-export from mcp subpackage for backwards compatibility
from .mcp import (
    DEFAULT_MCP_PROFILES,
    TokenashMCPClientWrapper,
    TokenashMCPCompressor,
    MCPCompressionResult,
    MCPToolProfile,
    compress_tool_result,
    compress_tool_result_with_metrics,
    create_tokenash_mcp_proxy,
)

# Re-export from agno subpackage (optional dependency)
try:
    from .agno import (
        TokenashAgnoModel,
        TokenashPostHook,
        TokenashPreHook,
        agno_available,
        create_tokenash_hooks,
        get_model_name_from_agno,
    )
    from .agno import OptimizationMetrics as AgnoOptimizationMetrics
    from .agno import get_tokenash_provider as get_agno_provider
    from .agno import optimize_messages as optimize_agno_messages

    _AGNO_AVAILABLE = True
except ImportError:
    _AGNO_AVAILABLE = False

__all__ = [
    # LangChain Core
    "TokenashChatModel",
    "TokenashCallbackHandler",
    "TokenashRunnable",
    "OptimizationMetrics",
    "optimize_messages",
    "langchain_available",
    # Provider Detection
    "detect_provider",
    "get_tokenash_provider",
    "get_model_name_from_langchain",
    # Memory
    "TokenashChatMessageHistory",
    # Retrievers
    "TokenashDocumentCompressor",
    "CompressionMetrics",
    # Agents
    "TokenashToolWrapper",
    "ToolCompressionMetrics",
    "ToolMetricsCollector",
    "wrap_tools_with_tokenash",
    "get_tool_metrics",
    "reset_tool_metrics",
    # LangSmith
    "TokenashLangSmithCallbackHandler",
    "is_langsmith_available",
    "is_langsmith_tracing_enabled",
    # Streaming
    "StreamingMetricsTracker",
    "StreamingMetricsCallback",
    "StreamingMetrics",
    "track_streaming_response",
    "track_async_streaming_response",
    # MCP
    "TokenashMCPCompressor",
    "TokenashMCPClientWrapper",
    "MCPCompressionResult",
    "MCPToolProfile",
    "compress_tool_result",
    "compress_tool_result_with_metrics",
    "create_tokenash_mcp_proxy",
    "DEFAULT_MCP_PROFILES",
    # Agno
    "TokenashAgnoModel",
    "TokenashPreHook",
    "TokenashPostHook",
    "agno_available",
    "create_tokenash_hooks",
    "get_agno_provider",
    "get_model_name_from_agno",
    "AgnoOptimizationMetrics",
    "optimize_agno_messages",
]
