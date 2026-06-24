"""Evaluation runners for different scenarios."""

from tokenash.evals.runners.before_after import BeforeAfterRunner
from tokenash.evals.runners.compression_only import CompressionOnlyRunner

__all__ = ["BeforeAfterRunner", "CompressionOnlyRunner"]
