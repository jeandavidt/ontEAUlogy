"""Query router for SPARQL and natural language query endpoints."""

import asyncio
import logging
import traceback
from typing import Any, Dict, Set
from fastapi import APIRouter, HTTPException
from ..schemas.models import (
    SparqlQueryRequest,
    SparqlQueryResponse,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
)
from ..services.ontology_store import ontology_store
from ..services.sparql_engine import sparql_engine
from ..services.llm_sparql import get_llm_sparql_translator
from ..services.execution_trace import execution_trace_service, AgentType
from ..services.agent_composer import get_agent_composer, CompositionResult
from ..services.query_analyzer import get_query_analyzer
from ..services.kg_analyzer import get_kg_analyzer
from ..services.model_registry import registry
from ..schemas.models import (
    AgentCompositionRequest,
    AgentCompositionResponse,
    CompositionLayerResponse,
)

import httpx
import asyncio

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
    """
    Discover agent composition to answer a query.
    
    Returns the execution plan without executing simulations.
    """
    logger.info(f"Composition discovery request: target={request.target_outputs}")
    
    await ontology_store.load_ontology()
    
    composer = get_agent_composer()
    
    result = await composer.compose(
        initial_data=set(request.initial_parameters.keys()),
        target_outputs=set(request.target_outputs),
        timeout_seconds=request.timeout_seconds
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
                inputs_needed={},  # Could be populated from ontology
                outputs_produced=list(layer.produced_outputs)
            )
            for layer in result.layers
        ],
        total_agents=sum(len(layer.agents) for layer in result.layers),
        estimated_execution_time_seconds=len(result.layers) * 5.0  # Rough estimate
    )


@router.post("/compose-and-execute")
async def compose_and_execute(request: AgentCompositionRequest):
    """
    Discover composition and immediately execute it.
    
    Returns final query results after all simulations complete.
    """
    logger.info(f"Compose-and-execute request: target={request.target_outputs}")
    
    await ontology_store.load_ontology()
    
    # Step 1: Discover composition
    composer = get_agent_composer()
    composition = await composer.compose(
        initial_data=set(request.initial_parameters.keys()),
        target_outputs=set(request.target_outputs),
        timeout_seconds=request.timeout_seconds
    )
    
    if not composition.found:
        return {
            "success": False,
            "error": f"Cannot satisfy query: {composition.describe_plan()}",
            "missing": list(composition.missing)
        }
    
    # Step 2: Execute the composition layers
    try:
        execution_results = await execute_composition_layers(composition)
        
        return {
            "success": True,
            "execution_plan": composition.describe_plan(),
            "layers_executed": len(composition.layers),
            "results": execution_results
        }
        
    except Exception as e:
        logger.error(f"Composition execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "execution_plan": composition.describe_plan()
        }


async def execute_composition_layers(composition: CompositionResult) -> Dict[str, Any]:
    """
    Execute agents in the discovered composition layers.
    
    Executes layers sequentially, with agents within a layer in parallel.
    """
    all_results = {}
    
    for layer in composition.layers:
        logger.info(f"Executing layer {layer.layer_index} with {len(layer.agents)} agents")
        
        # Execute agents in this layer in parallel
        tasks = []
        for agent in layer.agents:
            # Get inputs from previous results or initial data
            inputs = gather_inputs_for_agent(agent, all_results, composition.initial_data)
            
            task = execute_agent_simulation(agent, inputs)
            tasks.append(task)
        
        # Wait for all agents in layer to complete
        layer_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store results
        for agent, result in zip(layer.agents, layer_results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent.id} failed: {result}")
                raise result
            all_results[agent.id] = result
    
    return all_results


async def execute_agent_simulation(agent, inputs: Dict[str, float]) -> Dict[str, Any]:
    """Execute a single agent simulation via HTTP."""
    
    model_id = agent.model_id or agent.id
    
    # Check if model is registered
    model = registry.get_model(model_id)
    if not model:
        # Try on-demand registration
        from .simulation import try_register_model
        if await try_register_model(model_id):
            model = registry.get_model(model_id)
    
    if not model:
        raise ValueError(f"Model {model_id} not available")
    
    # Call model endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{model.endpoint}/simulate",
            json=inputs,
            timeout=300.0
        )
        response.raise_for_status()
        return response.json()


def gather_inputs_for_agent(
    agent, 
    all_results: Dict[str, Any], 
    initial_data: Set[str]
) -> Dict[str, float]:
    """
    Gather inputs for an agent from previous results or initial data.
    
    Maps parameter names between connected agents using simple heuristics.
    """
    inputs = {}
    
    for input_param in agent.required_inputs:
        # Check if it's produced by a previous agent
        for agent_id, results in all_results.items():
            # Map parameter names (e.g., mbr_effluent_cod → ro_feed_cod)
            mapped = map_parameter_name(input_param, agent_id, agent.id)
            if mapped in results:
                inputs[input_param] = results[mapped]
                break
    
    return inputs


def map_parameter_name(param: str, source_agent: str, target_agent: str) -> str:
    """
    Map parameter names between agents.
    
    Example: mbr.effluent_cod → ro.feed_cod
    """
    # Simple mapping - could use ontology wf:compatibleWith
    if "effluent" in param and target_agent == "ro":
        return param.replace("effluent", "feed")
    return param
