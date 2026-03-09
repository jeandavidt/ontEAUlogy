"""T1–T6: Query resolution trace visualization tests.

Tests the execution trace service and agent composition execution to verify:
- T1: SPARQL query → trace with 0 layers and 1 SPARQL event
- T2: NL/LLM query → trace with 0 layers and 1 LLM event
- T3: 1-layer composition → trace with 1 model event, kg_node_uri set, outputs match target
- T4: 2-layer composition (MBR→WQA) → 2 model events; MBR outputs overlap WQA inputs by name
- T5: 2 parallel scenarios → trace with 2 scenarios, each with 1 model event
- T6: 3 scenarios with 1 graceful failure → failed scenario has error, others complete

Agents at port 8101 (MBR) and 8104 (WQA) are mocked via httpx.MockTransport.
The trace service is imported directly from the core orchestrator to match the
same pattern used by the other household tests.
"""

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

# ---------------------------------------------------------------------------
# Import execution_trace from core (avoids package install issues)
# ---------------------------------------------------------------------------

_CORE_PATH = (
    Path(__file__).parent.parent.parent
    / "core"
    / "orchestrator"
    / "src"
    / "ontEAUlogy_core"
    / "services"
    / "execution_trace.py"
)

_spec = importlib.util.spec_from_file_location("execution_trace", _CORE_PATH)
_et_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_et_module)

ExecutionTraceService = _et_module.ExecutionTraceService
EventParameter = _et_module.EventParameter
AgentType = _et_module.AgentType
QueryTrace = _et_module.QueryTrace

# ---------------------------------------------------------------------------
# Import agent_composer from core
# ---------------------------------------------------------------------------

_COMPOSER_PATH = (
    Path(__file__).parent.parent.parent
    / "core"
    / "orchestrator"
    / "src"
    / "ontEAUlogy_core"
    / "services"
    / "agent_composer.py"
)

_cspec = importlib.util.spec_from_file_location("agent_composer", _COMPOSER_PATH)
_comp_module = importlib.util.module_from_spec(_cspec)
_cspec.loader.exec_module(_comp_module)

AgentComposer = _comp_module.AgentComposer
Agent = _comp_module.Agent
CompositionLayer = _comp_module.CompositionLayer
CompositionResult = _comp_module.CompositionResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_trace_service() -> ExecutionTraceService:
    """Return a fresh ExecutionTraceService instance."""
    return ExecutionTraceService()


def _make_agent(
    agent_id: str,
    name: str,
    required_inputs: List[str],
    produced_outputs: List[str],
    endpoint: str = "http://localhost:8101",
    model_id: Optional[str] = None,
) -> Agent:
    """Build an Agent stub for test composition layers."""
    agent = Agent(
        id=agent_id,
        name=name,
        endpoint=endpoint,
        required_inputs=set(required_inputs),
        produced_outputs=set(produced_outputs),
        operation_uri=f"urn:op:{agent_id}",
        model_id=model_id or agent_id,
    )
    return agent


def _make_composition(layers_spec: List[Dict]) -> CompositionResult:
    """Build a CompositionResult from a list of layer specs.

    Each spec: {"agents": [agent, ...], "produced": {param, ...}}
    """
    layers = []
    for i, spec in enumerate(layers_spec):
        layer = CompositionLayer(
            layer_index=i,
            agents=spec["agents"],
            produced_outputs=spec.get("produced", set()),
        )
        layers.append(layer)
    return CompositionResult(found=True, layers=layers, missing=set())


# ---------------------------------------------------------------------------
# Mock HTTP transport helpers
# ---------------------------------------------------------------------------

_MBR_OUTPUTS = {
    "effluent_cod": 42.0,
    "effluent_tss": 5.0,
    "effluent_flow": 1.4,
}

_WQA_OUTPUTS = {
    "water_quality_score": 0.87,
    "treatment_efficiency": 0.94,
}

_INFILTRATION_OUTPUTS = {
    "infiltrated_flow": 1.1,
}


def _mock_transport_mbr():
    """httpx MockTransport that returns MBR simulate response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_MBR_OUTPUTS)

    return httpx.MockTransport(handler)


def _mock_transport_wqa():
    """httpx MockTransport that returns WQA analyze response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_WQA_OUTPUTS)

    return httpx.MockTransport(handler)


def _mock_transport_infiltration():
    """httpx MockTransport that returns Infiltration simulate response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_INFILTRATION_OUTPUTS)

    return httpx.MockTransport(handler)


def _mock_transport_fail():
    """httpx MockTransport that returns 500."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "Agent unavailable"})

    return httpx.MockTransport(handler)


# ---------------------------------------------------------------------------
# Reusable async execution helper (mirrors _execute_composition_layers in
# query.py, but without the registry dependency — uses transport directly)
# ---------------------------------------------------------------------------


async def _run_layers(
    composition: "CompositionResult",
    initial_parameters: Dict[str, Any],
    trace_service: ExecutionTraceService,
    trace_id: str,
    scenario_id: Optional[str],
    agent_transports: Dict[str, httpx.MockTransport],
) -> Dict[str, Any]:
    """Execute agents layer by layer with mocked HTTP, emitting trace events."""
    all_results: Dict[str, Any] = {}

    for layer in composition.layers:
        tasks = []
        for agent in layer.agents:
            inputs = _gather(agent, all_results, initial_parameters)
            tasks.append(
                _call_agent(
                    agent,
                    inputs,
                    layer.layer_index,
                    trace_service,
                    trace_id,
                    scenario_id,
                    agent_transports,
                )
            )

        layer_results = await asyncio.gather(*tasks, return_exceptions=True)
        for agent, result in zip(layer.agents, layer_results):
            if isinstance(result, Exception):
                raise result
            all_results[agent.id] = result

    return all_results


def _gather(agent: Agent, all_results: Dict, initial: Dict) -> Dict[str, Any]:
    inputs: Dict[str, Any] = {}
    for param in agent.required_inputs:
        if param in initial:
            inputs[param] = initial[param]
            continue
        for prev in all_results.values():
            if isinstance(prev, dict) and param in prev:
                inputs[param] = prev[param]
                break
    return inputs


async def _call_agent(
    agent: Agent,
    inputs: Dict[str, Any],
    layer_index: int,
    service: ExecutionTraceService,
    trace_id: str,
    scenario_id: Optional[str],
    transports: Dict[str, httpx.MockTransport],
) -> Dict[str, Any]:
    input_params = [EventParameter(name=k, value=v) for k, v in inputs.items()]
    event_id = service.start_event(
        trace_id,
        agent_uri=agent.id,
        agent_name=agent.name,
        agent_type=AgentType.MODEL,
        operation_uri=agent.operation_uri,
        operation_name=agent.name,
        layer_index=layer_index,
        scenario_id=scenario_id,
        inputs=input_params,
    )

    transport = transports.get(agent.id)
    if transport is None:
        error_msg = f"No mock transport for agent '{agent.id}'"
        service.end_event(trace_id, event_id, outputs=[], status="failed", error=error_msg)
        raise ValueError(error_msg)

    async with httpx.AsyncClient(transport=transport) as client:
        try:
            resp = await client.post(f"{agent.endpoint}/simulate", json=inputs)
            resp.raise_for_status()
            result = resp.json()

            output_params = [EventParameter(name=k, value=v) for k, v in result.items()]
            service.end_event(trace_id, event_id, outputs=output_params, status="completed")
            return result

        except Exception as e:
            service.end_event(trace_id, event_id, outputs=[], status="failed", error=str(e))
            raise


# ---------------------------------------------------------------------------
# T1: SPARQL query → trace with 0 composition layers, 1 SPARQL event
# ---------------------------------------------------------------------------


def test_T1_sparql_trace_structure():
    """T1: A SPARQL query produces a trace with total_layers=0 and one orchestrator/SPARQL event."""
    service = _make_trace_service()
    trace_id = "test-t1"

    service.start_query_trace(trace_id, "SELECT ?a WHERE { ?a a wf:ComputationalAgent }")
    event_id = service.start_event(
        trace_id,
        agent_uri="wf:SparqlAgent",
        agent_name="SPARQL Agent",
        agent_type=AgentType.SPARQL,
        operation_uri="wf:SparqlQuery",
        operation_name="SPARQL Query",
        layer_index=None,
    )
    service.end_event(trace_id, event_id, outputs=[], status="completed")
    service.end_query_trace(trace_id, status="completed", total_layers=0)

    trace = service.get_query_trace(trace_id)
    assert trace is not None, "Trace must be recorded"
    assert trace.total_layers == 0
    assert len(trace.events) == 1
    assert trace.events[0].agent_type == AgentType.SPARQL
    assert trace.events[0].end_time is not None, "end_time must be set"
    assert trace.events[0].status == "completed"
    assert trace.status == "completed"


# ---------------------------------------------------------------------------
# T2: NL query → trace with 0 layers, 1 LLM event
# ---------------------------------------------------------------------------


def test_T2_nl_trace_structure():
    """T2: A natural-language query produces a trace with one LLM event and 0 layers."""
    service = _make_trace_service()
    trace_id = "test-t2"

    service.start_query_trace(trace_id, "What agents are available?")
    event_id = service.start_event(
        trace_id,
        agent_uri="wf:LLMTranslator",
        agent_name="LLM Translator",
        agent_type=AgentType.LLM,
        operation_uri="wf:TranslateNL",
        operation_name="Translate Natural Language",
        layer_index=None,
        inputs=[EventParameter(name="question", value="What agents are available?")],
    )
    service.end_event(
        trace_id,
        event_id,
        outputs=[EventParameter(name="sparql", value="SELECT ?a WHERE { ?a a wf:ComputationalAgent }")],
        status="completed",
    )
    service.end_query_trace(trace_id, status="completed", total_layers=0)

    trace = service.get_query_trace(trace_id)
    assert trace is not None
    assert trace.total_layers == 0
    assert len(trace.events) == 1

    evt = trace.events[0]
    assert evt.agent_type == AgentType.LLM
    assert evt.start_time is not None
    assert evt.end_time is not None
    assert evt.start_time <= evt.end_time
    assert trace.status == "completed"


# ---------------------------------------------------------------------------
# T3: 1-layer composition → 1 model event, inputs have names, outputs contain target
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_T3_single_layer_composition_trace():
    """T3: 1-layer composition: 1 MBR model event; inputs recorded; output contains effluent_cod."""
    service = _make_trace_service()
    trace_id = "test-t3"

    initial_params = {
        "influent_flow": 1.5,
        "influent_cod": 350.0,
        "hydraulic_retention_time": 8.0,
    }

    mbr_agent = _make_agent(
        "mbr",
        "Membrane Bioreactor Model",
        required_inputs=list(initial_params.keys()),
        produced_outputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        endpoint="http://localhost:8101",
        model_id="mbr",
    )

    composition = _make_composition(
        [{"agents": [mbr_agent], "produced": {"effluent_cod", "effluent_tss", "effluent_flow"}}]
    )

    service.start_query_trace(trace_id, "compose-and-execute:['effluent_cod']")
    results = await _run_layers(
        composition,
        initial_params,
        service,
        trace_id,
        scenario_id=None,
        agent_transports={"mbr": _mock_transport_mbr()},
    )
    service.end_query_trace(trace_id, status="completed", total_layers=len(composition.layers))

    trace = service.get_query_trace(trace_id)
    assert trace is not None
    assert trace.total_layers == 1

    # Check model events
    model_events = [e for e in trace.events if e.agent_type == AgentType.MODEL]
    assert len(model_events) == 1, "Exactly 1 model event expected"

    evt = model_events[0]
    assert evt.layer_index == 0
    assert evt.status == "completed"
    assert len(evt.inputs) > 0
    # All inputs must have a name
    for inp in evt.inputs:
        assert inp.name, "Every input parameter must have a name"

    # Outputs must include effluent_cod
    output_names = {p.name for p in evt.outputs}
    assert "effluent_cod" in output_names

    # Results dict must include effluent_cod from MBR
    assert results["mbr"]["effluent_cod"] == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# T4: 2-layer chain MBR→WQA: 2 events; MBR outputs overlap WQA inputs by name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_T4_two_layer_chain_trace():
    """T4: 2-layer MBR→WQA chain; MBR outputs[names] overlap WQA inputs[names]."""
    service = _make_trace_service()
    trace_id = "test-t4"

    initial_params = {
        "influent_flow": 1.5,
        "influent_cod": 350.0,
        "hydraulic_retention_time": 8.0,
    }

    mbr_agent = _make_agent(
        "mbr",
        "Membrane Bioreactor Model",
        required_inputs=list(initial_params.keys()),
        produced_outputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        endpoint="http://localhost:8101",
    )
    wqa_agent = _make_agent(
        "wqa",
        "Water Quality Analyzer",
        required_inputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        produced_outputs=["water_quality_score", "treatment_efficiency"],
        endpoint="http://localhost:8104",
    )

    composition = _make_composition(
        [
            {"agents": [mbr_agent], "produced": {"effluent_cod", "effluent_tss", "effluent_flow"}},
            {
                "agents": [wqa_agent],
                "produced": {"water_quality_score", "treatment_efficiency"},
            },
        ]
    )

    service.start_query_trace(trace_id, "compose-and-execute:['water_quality_score']")
    await _run_layers(
        composition,
        initial_params,
        service,
        trace_id,
        scenario_id=None,
        agent_transports={
            "mbr": _mock_transport_mbr(),
            "wqa": _mock_transport_wqa(),
        },
    )
    service.end_query_trace(trace_id, status="completed", total_layers=2)

    trace = service.get_query_trace(trace_id)
    assert trace is not None
    assert trace.total_layers == 2

    model_events = [e for e in trace.events if e.agent_type == AgentType.MODEL]
    assert len(model_events) == 2

    # Events by layer
    by_layer = {e.layer_index: e for e in model_events}
    assert 0 in by_layer and 1 in by_layer

    mbr_evt = by_layer[0]
    wqa_evt = by_layer[1]

    # MBR outputs overlap with WQA inputs by name
    mbr_output_names = {p.name for p in mbr_evt.outputs}
    wqa_input_names = {p.name for p in wqa_evt.inputs}
    overlap = mbr_output_names & wqa_input_names
    assert len(overlap) > 0, (
        f"MBR outputs {mbr_output_names} must share at least one name with WQA inputs {wqa_input_names}"
    )

    # Both events completed
    assert mbr_evt.status == "completed"
    assert wqa_evt.status == "completed"
    assert mbr_evt.start_time <= wqa_evt.start_time


# ---------------------------------------------------------------------------
# T5: 2 parallel scenarios, each with 1 model event, both completed
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_T5_parallel_scenarios():
    """T5: 2 parallel scenarios; each has 1 model event; both have status=='completed'."""
    service = _make_trace_service()
    trace_id = "test-t5"

    initial_params = {
        "influent_flow": 1.5,
        "influent_cod": 350.0,
        "hydraulic_retention_time": 8.0,
    }

    mbr_agent = _make_agent(
        "mbr",
        "Membrane Bioreactor Model",
        required_inputs=list(initial_params.keys()),
        produced_outputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        endpoint="http://localhost:8101",
    )
    wqa_agent = _make_agent(
        "wqa",
        "Water Quality Analyzer",
        required_inputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        produced_outputs=["water_quality_score", "treatment_efficiency"],
        endpoint="http://localhost:8104",
    )

    service.start_query_trace(trace_id, "compose-and-execute:parallel_scenarios")

    sid1 = service.create_scenario(trace_id, label="MBR Scenario")
    sid2 = service.create_scenario(trace_id, label="WQA Scenario")

    comp1 = _make_composition([{"agents": [mbr_agent], "produced": {"effluent_cod"}}])
    comp2 = _make_composition([{"agents": [wqa_agent], "produced": {"water_quality_score"}}])

    # Run scenario 2's initial params include the WQA prerequisites
    wqa_initial = {
        "effluent_cod": 42.0,
        "effluent_tss": 5.0,
        "effluent_flow": 1.4,
    }

    results1, results2 = await asyncio.gather(
        _run_layers(
            comp1, initial_params, service, trace_id, sid1,
            agent_transports={"mbr": _mock_transport_mbr()},
        ),
        _run_layers(
            comp2, wqa_initial, service, trace_id, sid2,
            agent_transports={"wqa": _mock_transport_wqa()},
        ),
    )
    service.end_scenario(trace_id, sid1, status="completed")
    service.end_scenario(trace_id, sid2, status="completed")
    service.end_query_trace(trace_id, status="completed", total_layers=1)

    trace = service.get_query_trace(trace_id)
    assert trace is not None
    assert len(trace.scenarios) == 2

    for scenario in trace.scenarios:
        assert scenario.status == "completed", f"Scenario '{scenario.label}' must be completed"
        assert len(scenario.events) == 1, f"Scenario '{scenario.label}' must have exactly 1 event"
        evt = scenario.events[0]
        assert evt.status == "completed"


# ---------------------------------------------------------------------------
# T6: 3 scenarios — scenario 3 fails gracefully (no transport registered)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_T6_parallel_scenarios_graceful_failure():
    """T6: 3 scenarios; scenario 3 fails gracefully; others complete; error field set."""
    service = _make_trace_service()
    trace_id = "test-t6"

    initial_params = {
        "influent_flow": 1.5,
        "influent_cod": 350.0,
        "hydraulic_retention_time": 8.0,
    }
    wqa_initial = {
        "effluent_cod": 42.0,
        "effluent_tss": 5.0,
        "effluent_flow": 1.4,
    }
    ro_initial_incomplete: Dict[str, Any] = {}  # missing required params → agent call fails

    mbr_agent = _make_agent(
        "mbr",
        "Membrane Bioreactor Model",
        required_inputs=list(initial_params.keys()),
        produced_outputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        endpoint="http://localhost:8101",
    )
    wqa_agent = _make_agent(
        "wqa",
        "Water Quality Analyzer",
        required_inputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        produced_outputs=["water_quality_score", "treatment_efficiency"],
        endpoint="http://localhost:8104",
    )
    # Scenario 3: agent with no registered transport → will fail
    failing_agent = _make_agent(
        "unregistered_agent",
        "Unregistered Agent",
        required_inputs=[],
        produced_outputs=["permeate_flow"],
        endpoint="http://localhost:9999",
    )

    service.start_query_trace(trace_id, "compose-and-execute:parallel_scenarios_t6")
    sid1 = service.create_scenario(trace_id, label="MBR scenario")
    sid2 = service.create_scenario(trace_id, label="WQA scenario")
    sid3 = service.create_scenario(trace_id, label="Failing scenario")

    comp1 = _make_composition([{"agents": [mbr_agent], "produced": {"effluent_cod"}}])
    comp2 = _make_composition([{"agents": [wqa_agent], "produced": {"water_quality_score"}}])
    comp3 = _make_composition([{"agents": [failing_agent], "produced": {"permeate_flow"}}])

    async def run_scenario(comp, params, sid, transports):
        try:
            result = await _run_layers(comp, params, service, trace_id, sid, transports)
            service.end_scenario(trace_id, sid, status="completed")
            return {"success": True, "result": result}
        except Exception as e:
            service.end_scenario(trace_id, sid, status="failed")
            return {"success": False, "error": str(e)}

    outcomes = await asyncio.gather(
        run_scenario(comp1, initial_params, sid1, {"mbr": _mock_transport_mbr()}),
        run_scenario(comp2, wqa_initial, sid2, {"wqa": _mock_transport_wqa()}),
        run_scenario(comp3, ro_initial_incomplete, sid3, {}),  # no transport → fails
    )

    service.end_query_trace(trace_id, status="completed", total_layers=1)

    trace = service.get_query_trace(trace_id)
    assert trace is not None
    assert len(trace.scenarios) == 3

    statuses = {s.label: s.status for s in trace.scenarios}
    assert statuses["MBR scenario"] == "completed"
    assert statuses["WQA scenario"] == "completed"
    assert statuses["Failing scenario"] == "failed"

    # Failed outcome must have an error message
    failed_outcome = outcomes[2]
    assert not failed_outcome["success"]
    assert failed_outcome["error"]

    # Events for the failed scenario must be marked failed or not exist
    failing_events = [e for e in trace.events if e.scenario_id == sid3]
    for e in failing_events:
        assert e.status == "failed", "Failed scenario events must have status=failed"

    # T6 additional: scenario events are consistent (scenario.events ⊆ trace.events)
    trace_event_ids = {e.event_id for e in trace.events}
    for scenario in trace.scenarios:
        for e in scenario.events:
            assert e.event_id in trace_event_ids, (
                f"Scenario event {e.event_id} must also appear in trace.events"
            )


# ---------------------------------------------------------------------------
# Extra: verify get_trace_json serialization round-trip for a completed trace
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_trace_json_serialization():
    """Extra: get_trace_json returns a complete, serializable dict for T3 trace."""
    service = _make_trace_service()
    trace_id = "test-json"

    initial_params = {"influent_flow": 1.5, "influent_cod": 350.0, "hydraulic_retention_time": 8.0}
    mbr_agent = _make_agent(
        "mbr",
        "Membrane Bioreactor Model",
        required_inputs=list(initial_params.keys()),
        produced_outputs=["effluent_cod", "effluent_tss", "effluent_flow"],
        endpoint="http://localhost:8101",
    )
    composition = _make_composition(
        [{"agents": [mbr_agent], "produced": {"effluent_cod", "effluent_tss", "effluent_flow"}}]
    )

    service.start_query_trace(trace_id, "json-round-trip-test")
    await _run_layers(
        composition,
        initial_params,
        service,
        trace_id,
        scenario_id=None,
        agent_transports={"mbr": _mock_transport_mbr()},
    )
    service.end_query_trace(trace_id, status="completed", total_layers=1)

    data = service.get_trace_json(trace_id)
    assert data is not None
    assert data["trace_id"] == trace_id
    assert data["status"] == "completed"
    assert data["total_layers"] == 1
    assert len(data["events"]) == 1

    evt = data["events"][0]
    assert "event_id" in evt
    assert "agent_name" in evt
    assert "start_time" in evt
    assert "end_time" in evt
    assert isinstance(evt["inputs"], list)
    assert isinstance(evt["outputs"], list)
    for p in evt["inputs"]:
        assert "name" in p
        assert "value" in p
    for p in evt["outputs"]:
        assert "name" in p
        assert "value" in p


# ---------------------------------------------------------------------------
# Extra: trace service list and lookup
# ---------------------------------------------------------------------------


def test_list_query_traces():
    """Extra: list_query_traces returns all started traces."""
    service = _make_trace_service()
    service.start_query_trace("a", "query a")
    service.start_query_trace("b", "query b")

    traces = service.list_query_traces()
    ids = {t.trace_id for t in traces}
    assert "a" in ids
    assert "b" in ids


def test_get_nonexistent_trace_returns_none():
    """Extra: get_query_trace on unknown id returns None."""
    service = _make_trace_service()
    assert service.get_query_trace("nonexistent-id") is None
