"""Execution trace service wrapper for ghent orchestrator.

This imports the execution trace service from waterframe_core.
"""

from waterframe_core.orchestrator.services.execution_trace import (
    execution_trace_service,
    AgentType,
)

__all__ = ["execution_trace_service", "AgentType"]
