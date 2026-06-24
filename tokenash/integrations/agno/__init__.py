"""Agno integration for Tokenash SDK.

This module provides seamless integration with Agno (formerly Phidata),
enabling automatic context optimization for Agno agents.

Components:
1. TokenashAgnoModel - Wraps any Agno model to apply Tokenash transforms
2. create_tokenash_hooks - Creates pre/post hooks for Agno agents
3. optimize_messages - Standalone function for manual optimization

Example:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from tokenash.integrations.agno import TokenashAgnoModel

    # Wrap any Agno model
    model = OpenAIChat(id="gpt-4o")
    optimized_model = TokenashAgnoModel(model)

    # Use with agent
    agent = Agent(model=optimized_model)
    response = agent.run("Hello!")
"""

from .hooks import (
    TokenashPostHook,
    TokenashPreHook,
    HookMetrics,
    create_tokenash_hooks,
)
from .model import (
    TokenashAgnoModel,
    OptimizationMetrics,
    agno_available,
    optimize_messages,
)
from .providers import get_tokenash_provider, get_model_name_from_agno

__all__ = [
    # Model wrapper
    "TokenashAgnoModel",
    "OptimizationMetrics",
    "agno_available",
    "optimize_messages",
    # Hooks
    "create_tokenash_hooks",
    "TokenashPreHook",
    "TokenashPostHook",
    "HookMetrics",
    # Provider detection
    "get_tokenash_provider",
    "get_model_name_from_agno",
]
