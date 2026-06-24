"""Handler mixins for TokenashProxy.

Each mixin class contains methods extracted from TokenashProxy that handle
requests for a specific provider or concern. The mixins rely on TokenashProxy's
__init__ for all self.* attributes (duck typing).
"""

from tokenash.proxy.handlers.anthropic import AnthropicHandlerMixin
from tokenash.proxy.handlers.batch import BatchHandlerMixin
from tokenash.proxy.handlers.bedrock import BedrockHandlerMixin
from tokenash.proxy.handlers.gemini import GeminiHandlerMixin
from tokenash.proxy.handlers.openai import OpenAIHandlerMixin
from tokenash.proxy.handlers.streaming import StreamingMixin

__all__ = [
    "AnthropicHandlerMixin",
    "BatchHandlerMixin",
    "BedrockHandlerMixin",
    "GeminiHandlerMixin",
    "OpenAIHandlerMixin",
    "StreamingMixin",
]
