"""Trace router: REST endpoints + WebSocket push for query execution traces."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from ..schemas.models import EventParameterResponse, ExecutionEventResponse, ExecutionScenarioResponse, QueryTraceResponse, QueryTraceSummary
from ..services.execution_trace import execution_trace_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/traces", tags=["Traces"])

# ============================================================
# WebSocket connection manager (trace subscriptions)
# ============================================================


class _TraceConnectionManager:
    """Manages WebSocket connections subscribed to trace updates."""

    def __init__(self):
        # trace_id → set of connected WebSockets
        self._subs: dict[str, set[WebSocket]] = {}
        # broadcast to all connections (no trace_id filter)
        self._all: set[WebSocket] = set()

    async def connect(self, ws: WebSocket, trace_id: Optional[str] = None) -> None:
        await ws.accept()
        if trace_id:
            self._subs.setdefault(trace_id, set()).add(ws)
        else:
            self._all.add(ws)

    def disconnect(self, ws: WebSocket, trace_id: Optional[str] = None) -> None:
        if trace_id and trace_id in self._subs:
            self._subs[trace_id].discard(ws)
        self._all.discard(ws)

    async def broadcast(self, message: dict) -> None:
        """Broadcast to all trace WebSocket subscribers."""
        tid = message.get("trace_id")
        targets: set[WebSocket] = set(self._all)
        if tid and tid in self._subs:
            targets.update(self._subs[tid])

        disconnected: set[WebSocket] = set()
        for ws in targets:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        for ws in disconnected:
            self.disconnect(ws)


_manager = _TraceConnectionManager()

# Wire the trace service to broadcast on mutations
execution_trace_service.set_broadcast_callback(_manager.broadcast)


# ============================================================
# Helpers
# ============================================================


def _event_to_response(event) -> ExecutionEventResponse:
    return ExecutionEventResponse(
        event_id=event.event_id,
        agent_uri=event.agent_uri,
        agent_name=event.agent_name,
        agent_type=event.agent_type.value if hasattr(event.agent_type, "value") else str(event.agent_type),
        operation_uri=event.operation_uri,
        operation_name=event.operation_name,
        layer_index=event.layer_index,
        scenario_id=event.scenario_id,
        parent_event_id=event.parent_event_id,
        start_time=event.start_time.isoformat() if event.start_time else None,
        end_time=event.end_time.isoformat() if event.end_time else None,
        inputs=[
            EventParameterResponse(
                name=p.name, value=p.value, unit=p.unit,
                kg_node_uri=p.kg_node_uri, kg_node_label=p.kg_node_label
            )
            for p in event.inputs
        ],
        outputs=[
            EventParameterResponse(
                name=p.name, value=p.value, unit=p.unit,
                kg_node_uri=p.kg_node_uri, kg_node_label=p.kg_node_label
            )
            for p in event.outputs
        ],
        status=event.status,
        error=event.error,
    )


def _scenario_to_response(scenario) -> ExecutionScenarioResponse:
    return ExecutionScenarioResponse(
        scenario_id=scenario.scenario_id,
        label=scenario.label,
        parent_scenario_id=scenario.parent_scenario_id,
        branch_event_id=scenario.branch_event_id,
        events=[_event_to_response(e) for e in scenario.events],
        status=scenario.status,
    )


def _trace_to_response(qt) -> QueryTraceResponse:
    return QueryTraceResponse(
        trace_id=qt.trace_id,
        query=qt.query,
        start_time=qt.start_time.isoformat() if qt.start_time else None,
        end_time=qt.end_time.isoformat() if qt.end_time else None,
        status=qt.status,
        events=[_event_to_response(e) for e in qt.events],
        scenarios=[_scenario_to_response(s) for s in qt.scenarios],
        total_layers=qt.total_layers,
    )


# ============================================================
# REST endpoints
# ============================================================


@router.get("", response_model=list[QueryTraceSummary])
async def list_traces():
    """List all query traces (summary only)."""
    traces = execution_trace_service.list_query_traces()
    return [
        QueryTraceSummary(
            trace_id=qt.trace_id,
            query=qt.query,
            status=qt.status,
            start_time=qt.start_time.isoformat() if qt.start_time else None,
            total_layers=qt.total_layers,
        )
        for qt in traces
    ]


@router.get("/{trace_id}", response_model=QueryTraceResponse)
async def get_trace(trace_id: str):
    """Get full trace details by ID."""
    qt = execution_trace_service.get_query_trace(trace_id)
    if qt is None:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found")
    return _trace_to_response(qt)


@router.get("/{trace_id}/prov")
async def get_trace_prov(trace_id: str):
    """Export trace as PROV-O JSON-LD."""
    qt = execution_trace_service.get_query_trace(trace_id)
    if qt is None:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found")

    graph = execution_trace_service.to_prov_rdf(trace_id)
    if graph is None:
        raise HTTPException(status_code=500, detail="PROV-O export failed (rdflib not available)")

    try:
        json_ld = graph.serialize(format="json-ld")
        return json.loads(json_ld)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Serialization error: {e}")


# ============================================================
# WebSocket endpoint
# ============================================================


@router.websocket("/ws")
async def trace_websocket(ws: WebSocket, trace_id: Optional[str] = None):
    """Subscribe to live trace events.

    Query parameter: ?trace_id=<id>  (optional — subscribe to a specific trace)
    Messages follow the schema:
      {"type": "event_started",    "trace_id": "...", "event": {...}}
      {"type": "event_completed",  "trace_id": "...", "event": {...}}
      {"type": "scenario_created", "trace_id": "...", "scenario": {...}}
      {"type": "trace_completed",  "trace_id": "..."}
    """
    await _manager.connect(ws, trace_id)
    try:
        while True:
            await ws.receive_text()  # Keep alive; ignore client messages
    except WebSocketDisconnect:
        _manager.disconnect(ws, trace_id)
    except Exception:
        _manager.disconnect(ws, trace_id)
