"""LangChain integration for Tokenash.

This package provides seamless integration with LangChain, including:
- TokenashChatModel: Drop-in wrapper for any LangChain chat model
- TokenashChatMessageHistory: Automatic conversation compression
- TokenashDocumentCompressor: Relevance-based document filtering
- TokenashToolWrapper: Tool output compression for agents
- StreamingMetricsTracker: Token counting during streaming
- TokenashLangSmithCallbackHandler: LangSmith trace enrichment
- compress_tool_messages: LangGraph pre-model hook for ToolMessage compression
- create_compress_tool_messages_node: LangGraph node factory

Example:
    from langchain_openai import ChatOpenAI
    from tokenash.integrations.langchain import TokenashChatModel

    # Wrap any LangChain model
    llm = TokenashChatModel(ChatOpenAI(model="gpt-4o"))

    # Use like normal - optimization happens automatically
    response = llm.invoke("Hello!")

Install: pip install tokenash[langchain]
"""

# Agent tool wrapping
from .agents import (
    TokenashToolWrapper,
    ToolCompressionMetrics,
    ToolMetricsCollector,
    get_tool_metrics,
    reset_tool_metrics,
    wrap_tools_with_tokenash,
)

# Core chat model wrapper
from .chat_model import (
    TokenashCallbackHandler,
    TokenashChatModel,
    TokenashRunnable,
    OptimizationMetrics,
    langchain_available,
    optimize_messages,
)

# LangGraph integration
from .langgraph import (
    CompressToolMessagesConfig,
    CompressToolMessagesResult,
    ToolMessageCompressionMetrics,
    compress_tool_messages,
    create_compress_tool_messages_node,
)

# LangSmith integration
from .langsmith import (
    TokenashLangSmithCallbackHandler,
    is_langsmith_available,
    is_langsmith_tracing_enabled,
)

# Memory integration
from .memory import TokenashChatMessageHistory

# Provider auto-detection
from .providers import (
    detect_provider,
    get_tokenash_provider,
    get_model_name_from_langchain,
)

# Retriever integration
from .retriever import CompressionMetrics, TokenashDocumentCompressor

# Streaming metrics
from .streaming import (
    StreamingMetrics,
    StreamingMetricsCallback,
    StreamingMetricsTracker,
    track_async_streaming_response,
    track_streaming_response,
)

__all__ = [
    # Core
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
    # LangGraph
    "compress_tool_messages",
    "create_compress_tool_messages_node",
    "CompressToolMessagesConfig",
    "CompressToolMessagesResult",
    "ToolMessageCompressionMetrics",
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
]
