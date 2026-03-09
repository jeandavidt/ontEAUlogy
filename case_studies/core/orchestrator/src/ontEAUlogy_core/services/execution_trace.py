"""Execution trace service for tracking agent operations.

Provides two APIs:
- Legacy: start_trace / add_step / end_trace  (kept for backward compatibility)
- New:    start_query_trace / start_event / end_event / create_scenario / get_trace_json / to_prov_rdf
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of computational agents."""

    LLM = "llm"
    MODEL = "model"
    ORCHESTRATOR = "orchestrator"
    USER = "user"
    SPARQL = "sparql"


# ============================================================
# Legacy dataclasses (kept for backward compatibility)
# ============================================================


@dataclass
class ExecutionStep:
    """A single step in a legacy execution trace."""

    timestamp: datetime
    agent_type: AgentType
    operation: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Legacy execution trace (kept for backward compatibility)."""

    trace_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    steps: List[ExecutionStep] = field(default_factory=list)
    status: str = "running"
    error: Optional[str] = None


# ============================================================
# New rich dataclasses
# ============================================================


@dataclass
class EventParameter:
    """An input or output parameter for an execution event."""

    name: str
    value: Any
    unit: Optional[str] = None
    kg_node_uri: Optional[str] = None
    kg_node_label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "kg_node_uri": self.kg_node_uri,
            "kg_node_label": self.kg_node_label,
        }


@dataclass
class ExecutionEvent:
    """A single agent invocation within a query trace."""

    event_id: str
    agent_uri: str
    agent_name: str
    agent_type: AgentType
    operation_uri: str
    operation_name: str
    layer_index: Optional[int] = None
    scenario_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    inputs: List[EventParameter] = field(default_factory=list)
    outputs: List[EventParameter] = field(default_factory=list)
    status: str = "running"   # running | completed | failed
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "agent_uri": self.agent_uri,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type.value if isinstance(self.agent_type, AgentType) else self.agent_type,
            "operation_uri": self.operation_uri,
            "operation_name": self.operation_name,
            "layer_index": self.layer_index,
            "scenario_id": self.scenario_id,
            "parent_event_id": self.parent_event_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "inputs": [p.to_dict() for p in self.inputs],
            "outputs": [p.to_dict() for p in self.outputs],
            "status": self.status,
            "error": self.error,
        }


@dataclass
class ExecutionScenario:
    """One parallel branch within a multi-scenario query."""

    scenario_id: str
    label: str
    parent_scenario_id: Optional[str] = None
    branch_event_id: Optional[str] = None
    events: List[ExecutionEvent] = field(default_factory=list)
    status: str = "running"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "label": self.label,
            "parent_scenario_id": self.parent_scenario_id,
            "branch_event_id": self.branch_event_id,
            "events": [e.to_dict() for e in self.events],
            "status": self.status,
        }


@dataclass
class QueryTrace:
    """Complete trace for a single query execution."""

    trace_id: str
    query: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    events: List[ExecutionEvent] = field(default_factory=list)
    scenarios: List[ExecutionScenario] = field(default_factory=list)
    total_layers: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "events": [e.to_dict() for e in self.events],
            "scenarios": [s.to_dict() for s in self.scenarios],
            "total_layers": self.total_layers,
        }


# ============================================================
# Service
# ============================================================


class ExecutionTraceService:
    """Service for recording and managing execution traces.

    Supports both the legacy API (start_trace/add_step/end_trace) and the
    new rich API (start_query_trace/start_event/end_event/create_scenario).
    """

    def __init__(self):
        # Legacy storage
        self._traces: Dict[str, ExecutionTrace] = {}
        # New rich storage
        self._query_traces: Dict[str, QueryTrace] = {}
        # WebSocket broadcast callback (set externally)
        self._broadcast_callback: Optional[Callable] = None

    # ----------------------------------------------------------
    # WebSocket integration
    # ----------------------------------------------------------

    def set_broadcast_callback(self, callback: Callable) -> None:
        """Register an async callback that receives (message_dict) for WS push."""
        self._broadcast_callback = callback

    async def _broadcast(self, message: Dict[str, Any]) -> None:
        if self._broadcast_callback is not None:
            try:
                await self._broadcast_callback(message)
            except Exception as e:
                logger.warning(f"Broadcast failed: {e}")

    # ----------------------------------------------------------
    # Legacy API (backward-compatible)
    # ----------------------------------------------------------

    def start_trace(self, trace_id: str) -> ExecutionTrace:
        """Start a legacy execution trace."""
        trace = ExecutionTrace(trace_id=trace_id, start_time=datetime.utcnow())
        self._traces[trace_id] = trace
        logger.debug(f"Started legacy trace: {trace_id}")
        return trace

    def add_step(
        self,
        trace_id: str,
        agent_type: AgentType,
        operation: str,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Add a step to a legacy trace."""
        if trace_id not in self._traces:
            logger.warning(f"Legacy trace not found: {trace_id}")
            return
        step = ExecutionStep(
            timestamp=datetime.utcnow(),
            agent_type=agent_type,
            operation=operation,
            inputs=inputs or {},
            outputs=outputs or {},
            metadata=metadata or {},
        )
        self._traces[trace_id].steps.append(step)

    def end_trace(
        self, trace_id: str, status: str = "completed", error: Optional[str] = None
    ) -> None:
        """End a legacy execution trace."""
        if trace_id not in self._traces:
            logger.warning(f"Legacy trace not found: {trace_id}")
            return
        trace = self._traces[trace_id]
        trace.end_time = datetime.utcnow()
        trace.status = status
        trace.error = error
        logger.debug(f"Ended legacy trace {trace_id} with status: {status}")

    def get_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Get a legacy trace by ID."""
        return self._traces.get(trace_id)

    def list_traces(self) -> List[ExecutionTrace]:
        """List all legacy traces."""
        return list(self._traces.values())

    # ----------------------------------------------------------
    # New rich API
    # ----------------------------------------------------------

    def start_query_trace(self, trace_id: str, query: str) -> QueryTrace:
        """Start a new rich query trace."""
        qt = QueryTrace(
            trace_id=trace_id,
            query=query,
            start_time=datetime.utcnow(),
        )
        self._query_traces[trace_id] = qt
        logger.debug(f"Started query trace: {trace_id}")
        return qt

    def start_event(
        self,
        trace_id: str,
        agent_uri: str,
        agent_name: str,
        agent_type: AgentType,
        operation_uri: str,
        operation_name: str,
        *,
        layer_index: Optional[int] = None,
        scenario_id: Optional[str] = None,
        parent_event_id: Optional[str] = None,
        inputs: Optional[List[EventParameter]] = None,
    ) -> str:
        """Record the start of an agent invocation; returns event_id."""
        qt = self._query_traces.get(trace_id)
        if qt is None:
            logger.warning(f"Query trace not found for start_event: {trace_id}")
            return str(uuid.uuid4())

        event_id = str(uuid.uuid4())
        event = ExecutionEvent(
            event_id=event_id,
            agent_uri=agent_uri,
            agent_name=agent_name,
            agent_type=agent_type,
            operation_uri=operation_uri,
            operation_name=operation_name,
            layer_index=layer_index,
            scenario_id=scenario_id,
            parent_event_id=parent_event_id,
            start_time=datetime.utcnow(),
            inputs=inputs or [],
        )
        qt.events.append(event)

        # Also append to the scenario's event list
        if scenario_id is not None:
            scenario = next((s for s in qt.scenarios if s.scenario_id == scenario_id), None)
            if scenario is not None:
                scenario.events.append(event)

        logger.debug(f"Started event {event_id} for agent {agent_name} in trace {trace_id}")
        return event_id

    def end_event(
        self,
        trace_id: str,
        event_id: str,
        outputs: Optional[List[EventParameter]] = None,
        status: str = "completed",
        error: Optional[str] = None,
    ) -> None:
        """Record the completion of an agent invocation."""
        qt = self._query_traces.get(trace_id)
        if qt is None:
            logger.warning(f"Query trace not found for end_event: {trace_id}")
            return

        event = next((e for e in qt.events if e.event_id == event_id), None)
        if event is None:
            logger.warning(f"Event {event_id} not found in trace {trace_id}")
            return

        event.end_time = datetime.utcnow()
        event.outputs = outputs or []
        event.status = status
        event.error = error
        logger.debug(f"Ended event {event_id} with status {status}")

    def create_scenario(
        self,
        trace_id: str,
        label: str,
        parent_scenario_id: Optional[str] = None,
        branch_event_id: Optional[str] = None,
    ) -> str:
        """Create a new execution scenario; returns scenario_id."""
        qt = self._query_traces.get(trace_id)
        if qt is None:
            logger.warning(f"Query trace not found for create_scenario: {trace_id}")
            return str(uuid.uuid4())

        scenario_id = str(uuid.uuid4())
        scenario = ExecutionScenario(
            scenario_id=scenario_id,
            label=label,
            parent_scenario_id=parent_scenario_id,
            branch_event_id=branch_event_id,
        )
        qt.scenarios.append(scenario)
        logger.debug(f"Created scenario {scenario_id} ('{label}') in trace {trace_id}")
        return scenario_id

    def end_query_trace(
        self,
        trace_id: str,
        status: str = "completed",
        error: Optional[str] = None,
        total_layers: int = 0,
    ) -> None:
        """Mark a query trace as completed."""
        qt = self._query_traces.get(trace_id)
        if qt is None:
            logger.warning(f"Query trace not found for end_query_trace: {trace_id}")
            return
        qt.end_time = datetime.utcnow()
        qt.status = status
        qt.total_layers = total_layers
        logger.debug(f"Ended query trace {trace_id} with status {status}")

    def end_scenario(self, trace_id: str, scenario_id: str, status: str = "completed") -> None:
        """Mark a scenario as completed or failed."""
        qt = self._query_traces.get(trace_id)
        if qt is None:
            return
        scenario = next((s for s in qt.scenarios if s.scenario_id == scenario_id), None)
        if scenario is not None:
            scenario.status = status

    def get_query_trace(self, trace_id: str) -> Optional[QueryTrace]:
        """Get a rich query trace by ID."""
        return self._query_traces.get(trace_id)

    def list_query_traces(self) -> List[QueryTrace]:
        """List all rich query traces."""
        return list(self._query_traces.values())

    def get_trace_json(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Serialize a QueryTrace to a JSON-compatible dict."""
        qt = self._query_traces.get(trace_id)
        if qt is None:
            return None
        return qt.to_dict()

    def to_prov_rdf(self, trace_id: str):
        """Export a QueryTrace as PROV-O JSON-LD using rdflib.

        Returns a rdflib.ConjunctiveGraph or None if trace not found.
        """
        try:
            from rdflib import ConjunctiveGraph, Graph, URIRef, Literal, Namespace
            from rdflib.namespace import PROV, RDF, RDFS, XSD
        except ImportError:
            logger.error("rdflib not available for PROV-O export")
            return None

        qt = self._query_traces.get(trace_id)
        if qt is None:
            return None

        WF = Namespace("https://ugentbiomath.github.io/waterframe#")
        TRACE = Namespace(f"urn:trace:{trace_id}:")

        cg = ConjunctiveGraph()
        cg.bind("prov", PROV)
        cg.bind("wf", WF)
        cg.bind("trace", TRACE)

        # Trace-level bundle
        trace_uri = TRACE[f"trace/{trace_id}"]
        cg.add((trace_uri, RDF.type, PROV.Bundle))
        cg.add((trace_uri, RDFS.label, Literal(qt.query)))

        for event in qt.events:
            ev_uri = TRACE[f"event/{event.event_id}"]
            agent_uri = URIRef(event.agent_uri) if event.agent_uri.startswith("http") else TRACE[f"agent/{event.agent_uri}"]

            cg.add((ev_uri, RDF.type, PROV.Activity))
            cg.add((ev_uri, PROV.wasAssociatedWith, agent_uri))
            cg.add((agent_uri, RDF.type, PROV.Agent))
            cg.add((agent_uri, RDFS.label, Literal(event.agent_name)))

            if event.start_time:
                cg.add((ev_uri, PROV.startedAtTime, Literal(event.start_time.isoformat(), datatype=XSD.dateTime)))
            if event.end_time:
                cg.add((ev_uri, PROV.endedAtTime, Literal(event.end_time.isoformat(), datatype=XSD.dateTime)))
            if event.layer_index is not None:
                cg.add((ev_uri, WF.inLayer, Literal(event.layer_index, datatype=XSD.integer)))

            for i, inp in enumerate(event.inputs):
                param_uri = TRACE[f"param/{event.event_id}/in/{i}"]
                cg.add((param_uri, RDF.type, PROV.Entity))
                cg.add((param_uri, RDFS.label, Literal(inp.name)))
                cg.add((param_uri, WF.parameterValue, Literal(str(inp.value))))
                if inp.unit:
                    cg.add((param_uri, WF.parameterUnit, Literal(inp.unit)))
                if inp.kg_node_uri:
                    cg.add((param_uri, WF.refersToKGNode, URIRef(inp.kg_node_uri)))
                cg.add((ev_uri, PROV.used, param_uri))

            for i, out in enumerate(event.outputs):
                param_uri = TRACE[f"param/{event.event_id}/out/{i}"]
                cg.add((param_uri, RDF.type, PROV.Entity))
                cg.add((param_uri, RDFS.label, Literal(out.name)))
                cg.add((param_uri, WF.parameterValue, Literal(str(out.value))))
                if out.unit:
                    cg.add((param_uri, WF.parameterUnit, Literal(out.unit)))
                if out.kg_node_uri:
                    cg.add((param_uri, WF.refersToKGNode, URIRef(out.kg_node_uri)))
                cg.add((param_uri, PROV.wasGeneratedBy, ev_uri))

        for scenario in qt.scenarios:
            sc_uri = TRACE[f"scenario/{scenario.scenario_id}"]
            cg.add((sc_uri, RDF.type, PROV.Bundle))
            cg.add((sc_uri, RDFS.label, Literal(scenario.label)))

        return cg


# Global singleton
execution_trace_service = ExecutionTraceService()
