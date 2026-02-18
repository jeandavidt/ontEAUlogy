"""Trace router for execution trace API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/traces", tags=["Traces"])


class TraceListResponse(BaseModel):
    """Response for listing traces."""

    traces: list
    count: int


class TraceDetailResponse(BaseModel):
    """Response for getting trace details."""

    trace_id: str
    root_agent: str
    started_at: str
    completed_at: Optional[str]
    status: str
    nodes: list


@router.get("/", response_model=TraceListResponse)
async def list_traces(limit: int = Query(50, ge=1, le=100)):
    """List recent execution traces."""
    from ..services.execution_trace import execution_trace_service

    traces = execution_trace_service.list_traces(limit=limit)
    return TraceListResponse(traces=traces, count=len(traces))


@router.get("/{trace_id}")
async def get_trace(trace_id: str):
    """Get a specific trace with all nodes."""
    from ..services.execution_trace import execution_trace_service

    trace = execution_trace_service.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    return trace.to_dict()


@router.get("/{trace_id}/export")
async def export_trace(
    trace_id: str, format: str = Query("json", regex="^(json|turtle)$")
):
    """Export a trace in the specified format."""
    from ..services.execution_trace import execution_trace_service

    trace = execution_trace_service.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    if format == "turtle":
        return execution_trace_service.export_trace_turtle(trace_id)

    return trace.to_dict()


@router.get("/{trace_id}/graph")
async def get_trace_graph(trace_id: str):
    """Get trace in graph format for D3.js visualization."""
    from ..services.execution_trace import execution_trace_service

    trace = execution_trace_service.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    nodes = []
    links = []

    for node in trace.nodes:
        nodes.append(
            {
                "id": node.node_id,
                "agent_type": node.agent_type,
                "agent_id": node.agent_id,
                "timestamp": node.timestamp.isoformat(),
                "processing": node.processing,
            }
        )

        if node.parent_id:
            links.append(
                {
                    "source": node.parent_id,
                    "target": node.node_id,
                }
            )

    return {
        "trace_id": trace.trace_id,
        "root_agent": trace.root_agent,
        "status": trace.status,
        "nodes": nodes,
        "links": links,
    }
