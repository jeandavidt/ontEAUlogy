"""Query router for SPARQL, NL, and agent-composition query endpoints."""

import asyncio
import logging
import traceback
import uuid
from typing import Any, Dict, List, Optional, Set

import httpx
from fastapi import APIRouter, HTTPException

from ..schemas.models import (
    AgentCompositionRequest,
    AgentCompositionResponse,
    CompositionLayerResponse,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
    SparqlQueryRequest,
    SparqlQueryResponse,
)
from ..services.agent_composer import get_ontology_composer
from ..services.execution_trace import AgentType, EventParameter, execution_trace_service
from ..services.llm_sparql import get_llm_sparql_translator
from ..services.model_registry import registry
from ..services.ontology_store import ontology_store
from ..services.sparql_engine import sparql_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/query", tags=["Query"])

# Security limits for SPARQL queries
MAX_QUERY_LENGTH = 10000  # characters
MAX_QUERY_TIME = 30.0  # seconds
MAX_RESULTS = 10000  # results


def validate_sparql_query(query: str) -> None:
    """Validate SPARQL query for safety.

    Args:
        query: SPARQL query string to validate

    Raises:
        ValueError: If query is invalid or unsafe
    """
    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(f"Query too long (max {MAX_QUERY_LENGTH} characters)")

    # Prevent modification queries (only SELECT, ASK, CONSTRUCT, DESCRIBE allowed)
    query_upper = query.strip().upper()
    forbidden_ops = [
        "INSERT",
        "DELETE",
        "CLEAR",
        "DROP",
        "CREATE",
        "LOAD",
        "MOVE",
        "COPY",
        "ADD",
    ]
    for op in forbidden_ops:
        # Check for the operation as a separate word (not part of a URI or variable name)
        if f" {op} " in f" {query_upper} " or query_upper.startswith(f"{op} "):
            raise ValueError(
                f"Operation {op} not allowed - only read queries permitted"
            )


@router.post("/sparql", response_model=SparqlQueryResponse)
async def execute_sparql_query(request: SparqlQueryRequest):
    """Execute a SPARQL query against the unified graph."""
    logger.info(f"Received SPARQL query request (format={request.format})")

    trace_id = None
    node_id = None

    try:
        trace_id = execution_trace_service.start_trace(
            "sparql_agent", {"query": request.query, "format": request.format}
        )
    except Exception as e:
        logger.warning(f"Could not start trace: {e}")

    # Validate query for safety
    try:
        validate_sparql_query(request.query)
    except ValueError as e:
        logger.warning(f"Query validation failed: {e}")
        if node_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.SPARQL,
                    "sparql_agent",
                    {"query": request.query},
                    {"error": str(e)},
                    "Query validation failed",
                )
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))

    # Ensure ontology is loaded
    await ontology_store.load_ontology()

    try:
        # Add node for query execution
        if trace_id:
            try:
                node_id = execution_trace_service.add_node(
                    trace_id,
                    None,
                    AgentType.SPARQL,
                    "sparql_agent",
                    {"query": request.query},
                    {},
                    "Executing SPARQL query against ontology",
                )
            except Exception as e:
                logger.warning(f"Could not add trace node: {e}")

        # Execute with timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(
                sparql_engine.execute_query, request.query, request.format
            ),
            timeout=MAX_QUERY_TIME,
        )

        # Check result size
        if isinstance(result.get("results"), dict):
            bindings = result["results"].get("bindings", [])
            if len(bindings) > MAX_RESULTS:
                raise ValueError(
                    f"Result set too large ({len(bindings)} > {MAX_RESULTS})"
                )

        # Update trace with results
        if trace_id and node_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.SPARQL,
                    "sparql_agent",
                    {"query": request.query},
                    result,
                    f"Query returned {len(result.get('results', {}).get('bindings', []))} results",
                )
                execution_trace_service.complete_trace(trace_id)
            except Exception as e:
                logger.warning(f"Could not update trace: {e}")

        logger.info(f"SPARQL query completed successfully")
        return SparqlQueryResponse(
            head=result.get("head"),
            results=result.get("results"),
            format=result.get("format", "json"),
            query_time_ms=result.get("query_time_ms", 0.0),
        )
    except asyncio.TimeoutError:
        logger.error(f"SPARQL query timed out after {MAX_QUERY_TIME}s")
        if trace_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.SPARQL,
                    "sparql_agent",
                    {"query": request.query},
                    {"error": "timeout"},
                    f"Query timed out after {MAX_QUERY_TIME}s",
                )
                execution_trace_service.complete_trace(trace_id, "failed")
            except:
                pass
        raise HTTPException(
            status_code=408, detail=f"Query timeout after {MAX_QUERY_TIME}s"
        )
    except ValueError as e:
        logger.error(f"SPARQL query validation failed: {e}")
        if trace_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.SPARQL,
                    "sparql_agent",
                    {"query": request.query},
                    {"error": str(e)},
                    "Query validation failed",
                )
                execution_trace_service.complete_trace(trace_id, "failed")
            except:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SPARQL query failed: {e}\n{traceback.format_exc()}")
        if trace_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.SPARQL,
                    "sparql_agent",
                    {"query": request.query},
                    {"error": str(e)},
                    "Query execution failed",
                )
                execution_trace_service.complete_trace(trace_id, "failed")
            except:
                pass
        raise HTTPException(
            status_code=400, detail=f"SPARQL execution failed: {str(e)}"
        )


@router.post("/natural", response_model=NaturalLanguageQueryResponse)
async def execute_natural_query(request: NaturalLanguageQueryRequest):
    """Execute a natural language query (NL → SPARQL → results)."""
    logger.info(f"Received natural language query: {request.question[:100]}...")

    trace_id = None
    node_id = None

    try:
        trace_id = execution_trace_service.start_trace(
            "llm_agent", {"question": request.question}
        )
    except Exception as e:
        logger.warning(f"Could not start trace: {e}")

    # Ensure ontology is loaded
    await ontology_store.load_ontology()

    # Get translator instance
    translator = get_llm_sparql_translator()

    # Ensure LLM translator is initialized
    if not translator._initialized:
        logger.info("Initializing LLM translator on first request...")
        await translator.initialize()

    try:
        # Add node for LLM translation
        if trace_id:
            try:
                node_id = execution_trace_service.add_node(
                    trace_id,
                    None,
                    AgentType.LLM,
                    "llm_translator",
                    {"question": request.question},
                    {},
                    "Translating natural language to SPARQL",
                )
            except Exception as e:
                logger.warning(f"Could not add trace node: {e}")

        # Translate and execute
        logger.info("Translating question to SPARQL...")
        result = await translator.execute_query(request.question, sparql_engine)

        response = NaturalLanguageQueryResponse(
            original_question=request.question,
            generated_sparql=result.get("generated_sparql"),
            results=result.get("results", {}).get("bindings")
            if isinstance(result.get("results"), dict)
            else result.get("results"),
            execution_plan=result.get("execution_plan"),
            simulation_required=result.get("simulation_required", False),
            suggested_models=result.get("suggested_models", []),
        )

        # Validate results and provide helpful feedback
        if response.results is None or len(response.results) == 0:
            logger.warning("Query returned no results")
            response.execution_plan = (
                "No results found. Try rephrasing your question or being more specific. "
                f"Generated SPARQL: {response.generated_sparql}"
            )

        # Update trace with results
        if trace_id and node_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.LLM,
                    "llm_translator",
                    {"question": request.question},
                    response.model_dump(),
                    f"Translated to SPARQL, returned {len(response.results or [])} results",
                )
                execution_trace_service.complete_trace(trace_id)
            except Exception as e:
                logger.warning(f"Could not update trace: {e}")

        return response

    except ValueError as e:
        # Translation validation failed - provide helpful error
        logger.warning(f"NL to SPARQL translation failed: {e}")
        if trace_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.LLM,
                    "llm_translator",
                    {"question": request.question},
                    {"error": str(e)},
                    "Translation validation failed",
                )
                execution_trace_service.complete_trace(trace_id, "failed")
            except:
                pass
        return NaturalLanguageQueryResponse(
            original_question=request.question,
            generated_sparql=None,
            results=[],
            execution_plan=f"Translation error: {str(e)}. Please rephrase your question.",
            simulation_required=False,
            suggested_models=[],
        )
    except RuntimeError as e:
        # SPARQL execution failed - return partial results
        logger.error(f"SPARQL execution failed: {e}")
        if trace_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.LLM,
                    "llm_translator",
                    {"question": request.question},
                    {"error": str(e)},
                    "SPARQL execution failed",
                )
                execution_trace_service.complete_trace(trace_id, "failed")
            except:
                pass
        return NaturalLanguageQueryResponse(
            original_question=request.question,
            generated_sparql=None,
            results=[],
            execution_plan=f"Query execution error: {str(e)}. The generated query may be too complex.",
            simulation_required=False,
            suggested_models=[],
        )
    except Exception as e:
        logger.error(f"Natural language query failed: {e}\n{traceback.format_exc()}")
        if trace_id:
            try:
                execution_trace_service.add_node(
                    trace_id,
                    node_id,
                    AgentType.LLM,
                    "llm_translator",
                    {"question": request.question},
                    {"error": str(e)},
                    "Query processing failed",
                )
                execution_trace_service.complete_trace(trace_id, "failed")
            except:
                pass
        raise HTTPException(
            status_code=500, detail=f"Query processing failed: {str(e)}"
        )


@router.get("/translate")
async def translate_question(question: str):
    """Translate a natural language question to SPARQL (without executing)."""
    logger.info(f"Received translate request: {question[:100]}...")
    translator = get_llm_sparql_translator()
    try:
        result = await translator.translate(question)
        logger.info(f"Translation complete. Valid: {result.is_valid}")
        return result
    except Exception as e:
        logger.error(f"Translation failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Agent Composition Endpoints
# =============================================================================


@router.post("/compose", response_model=AgentCompositionResponse)
async def discover_composition(request: AgentCompositionRequest):
    """Discover agent composition to answer a query (dry-run, no execution)."""
    logger.info(f"Composition discovery request: target={request.target_outputs}")

    await ontology_store.load_ontology()

    trace_id = str(uuid.uuid4())
    execution_trace_service.start_query_trace(trace_id, f"compose:{request.target_outputs}")

    composer = get_ontology_composer()
    result = await composer.compose(
        initial_data=set(request.initial_parameters.keys()),
        target_outputs=set(request.target_outputs),
        timeout_seconds=request.timeout_seconds,
        trace_id=trace_id,
        scenario_id=None,
    )

    execution_trace_service.end_query_trace(
        trace_id,
        status="completed" if result.found else "failed",
        total_layers=len(result.layers),
    )

    return AgentCompositionResponse(
        composition_found=result.found,
        execution_plan=result.describe_plan(),
        layers=[
            CompositionLayerResponse(
                layer_index=layer.layer_index,
                agent_ids=[a.id for a in layer.agents],
                agent_names=[a.name for a in layer.agents],
                parallelizable=len(layer.agents) > 1,
                inputs_needed={},
                outputs_produced=list(layer.produced_outputs),
            )
            for layer in result.layers
        ],
        total_agents=sum(len(layer.agents) for layer in result.layers),
        estimated_execution_time_seconds=len(result.layers) * 5.0,
        trace_id=trace_id,
    )


@router.post("/compose-and-execute")
async def compose_and_execute(request: AgentCompositionRequest):
    """Discover composition and immediately execute it.

    Supports parallel_scenarios: if provided, each scenario runs its own
    composition + execution in parallel and results are merged into one trace.
    """
    logger.info(f"Compose-and-execute request: target={request.target_outputs}")

    await ontology_store.load_ontology()

    trace_id = str(uuid.uuid4())
    execution_trace_service.start_query_trace(trace_id, f"compose-and-execute:{request.target_outputs}")

    try:
        if request.parallel_scenarios:
            result = await _execute_parallel_scenarios(request, trace_id)
        else:
            result = await _execute_single_scenario(request, trace_id, scenario_id=None)

        return result

    except Exception as e:
        logger.error(f"Compose-and-execute failed: {e}\n{traceback.format_exc()}")
        execution_trace_service.end_query_trace(trace_id, status="failed")
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_single_scenario(
    request: AgentCompositionRequest,
    trace_id: str,
    scenario_id: Optional[str],
) -> Dict[str, Any]:
    """Compose and execute a single scenario."""
    composer = get_ontology_composer()
    composition = await composer.compose(
        initial_data=set(request.initial_parameters.keys()),
        target_outputs=set(request.target_outputs),
        timeout_seconds=request.timeout_seconds,
        trace_id=trace_id,
        scenario_id=scenario_id,
    )

    if not composition.found:
        execution_trace_service.end_query_trace(trace_id, status="failed", total_layers=0)
        return {
            "success": False,
            "trace_id": trace_id,
            "error": f"Cannot satisfy query: {composition.describe_plan()}",
            "missing": list(composition.missing),
        }

    try:
        execution_results = await _execute_composition_layers(
            composition, request.initial_parameters, trace_id, scenario_id
        )
        execution_trace_service.end_query_trace(
            trace_id, status="completed", total_layers=len(composition.layers)
        )
        return {
            "success": True,
            "trace_id": trace_id,
            "execution_plan": composition.describe_plan(),
            "layers_executed": len(composition.layers),
            "results": execution_results,
        }

    except Exception as e:
        logger.error(f"Composition execution failed: {e}")
        execution_trace_service.end_query_trace(trace_id, status="failed")
        return {
            "success": False,
            "trace_id": trace_id,
            "error": str(e),
            "execution_plan": composition.describe_plan(),
        }


async def _execute_parallel_scenarios(
    request: AgentCompositionRequest,
    trace_id: str,
) -> Dict[str, Any]:
    """Run multiple scenarios in parallel, each with its own scenario_id."""
    specs = request.parallel_scenarios or []
    composer = get_ontology_composer()

    # Create a scenario per spec
    scenario_ids: List[str] = []
    for spec in specs:
        sid = execution_trace_service.create_scenario(
            trace_id,
            label=spec.label or f"Scenario {len(scenario_ids)}",
        )
        scenario_ids.append(sid)

    async def run_scenario(spec, sid: str) -> Dict[str, Any]:
        sub_request = AgentCompositionRequest(
            initial_parameters=spec.initial_parameters,
            target_outputs=spec.target_outputs,
            max_layers=request.max_layers,
            timeout_seconds=request.timeout_seconds,
        )
        composition = await composer.compose(
            initial_data=set(spec.initial_parameters.keys()),
            target_outputs=set(spec.target_outputs),
            timeout_seconds=request.timeout_seconds,
            trace_id=trace_id,
            scenario_id=sid,
        )

        if not composition.found:
            error_msg = f"Cannot satisfy scenario '{spec.label}': missing {list(composition.missing)}"
            execution_trace_service.end_scenario(trace_id, sid, status="failed")
            return {
                "scenario_id": sid,
                "label": spec.label,
                "success": False,
                "error": error_msg,
                "missing": list(composition.missing),
            }

        try:
            results = await _execute_composition_layers(
                composition, spec.initial_parameters, trace_id, sid
            )
            execution_trace_service.end_scenario(trace_id, sid, status="completed")
            return {
                "scenario_id": sid,
                "label": spec.label,
                "success": True,
                "layers_executed": len(composition.layers),
                "results": results,
            }
        except Exception as e:
            execution_trace_service.end_scenario(trace_id, sid, status="failed")
            return {
                "scenario_id": sid,
                "label": spec.label,
                "success": False,
                "error": str(e),
            }

    scenario_results = await asyncio.gather(
        *[run_scenario(spec, sid) for spec, sid in zip(specs, scenario_ids)],
        return_exceptions=False,
    )

    all_layers = max(
        (r.get("layers_executed", 0) for r in scenario_results if isinstance(r, dict)),
        default=0,
    )
    execution_trace_service.end_query_trace(trace_id, status="completed", total_layers=all_layers)

    return {
        "success": True,
        "trace_id": trace_id,
        "scenarios": list(scenario_results),
    }


async def _execute_composition_layers(
    composition,
    initial_parameters: Dict[str, Any],
    trace_id: str,
    scenario_id: Optional[str],
) -> Dict[str, Any]:
    """Execute agents layer-by-layer, emitting trace events for each agent."""
    composer = get_ontology_composer()
    all_results: Dict[str, Any] = {}

    for layer in composition.layers:
        logger.info(f"Executing layer {layer.layer_index} with {len(layer.agents)} agents")

        tasks = []
        for agent in layer.agents:
            inputs = _gather_inputs(agent, all_results, initial_parameters)
            tasks.append(
                _execute_agent_with_trace(agent, inputs, layer.layer_index, trace_id, scenario_id, composer)
            )

        layer_results = await asyncio.gather(*tasks, return_exceptions=True)

        for agent, result in zip(layer.agents, layer_results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent.id} failed: {result}")
                raise result
            all_results[agent.id] = result

    return all_results


async def _execute_agent_with_trace(
    agent,
    inputs: Dict[str, Any],
    layer_index: int,
    trace_id: str,
    scenario_id: Optional[str],
    composer,
) -> Dict[str, Any]:
    """Execute a single agent and record start/end trace events."""
    # Build EventParameter list with kg_node_uri from ontology
    input_params = [
        EventParameter(
            name=k,
            value=v,
            kg_node_uri=composer.kg_uri_for(k),
        )
        for k, v in inputs.items()
    ]

    event_id: Optional[str] = None
    if trace_id:
        try:
            event_id = execution_trace_service.start_event(
                trace_id,
                agent_uri=agent.operation_uri or agent.id,
                agent_name=agent.name,
                agent_type=AgentType.MODEL,
                operation_uri=agent.operation_uri or "",
                operation_name=agent.name,
                layer_index=layer_index,
                scenario_id=scenario_id,
                inputs=input_params,
            )
        except Exception:
            pass

    try:
        result = await _call_agent_http(agent, inputs)

        output_params = [
            EventParameter(
                name=k,
                value=v,
                kg_node_uri=composer.kg_uri_for(k),
            )
            for k, v in result.items()
        ]

        if trace_id and event_id:
            try:
                execution_trace_service.end_event(
                    trace_id, event_id, outputs=output_params, status="completed"
                )
            except Exception:
                pass

        return result

    except Exception as e:
        if trace_id and event_id:
            try:
                execution_trace_service.end_event(
                    trace_id, event_id, outputs=[], status="failed", error=str(e)
                )
            except Exception:
                pass
        raise


async def _call_agent_http(agent, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Call an agent's HTTP endpoint."""
    model_id = agent.model_id or agent.id
    model = registry.get_model(model_id)

    if not model:
        raise ValueError(f"Model '{model_id}' not registered")

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(f"{model.endpoint}/simulate", json=inputs)
        response.raise_for_status()
        return response.json()


def _gather_inputs(agent, all_results: Dict[str, Any], initial_parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Gather inputs for an agent from previous layer results or initial parameters."""
    inputs: Dict[str, Any] = {}

    for param in agent.required_inputs:
        # Try initial parameters first
        if param in initial_parameters:
            inputs[param] = initial_parameters[param]
            continue

        # Try outputs from previous agents (by parameter name, exact match)
        for prev_result in all_results.values():
            if isinstance(prev_result, dict) and param in prev_result:
                inputs[param] = prev_result[param]
                break

    return inputs
