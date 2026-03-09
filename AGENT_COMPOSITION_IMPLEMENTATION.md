# Agent Composition Implementation Guide

This document provides concrete code implementation details for the graph-based agent composition algorithm.

## Core Algorithm Implementation

### 1. Agent Composer Service

**File**: `case_studies/ghent/src/ghent_water/orchestrator/services/agent_composer.py`

```python
"""Agent composition service implementing the graph-based discovery algorithm."""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Represents a computational agent that can be discovered and executed."""
    id: str
    name: str
    operation_uri: str
    endpoint: str
    required_inputs: Set[str]
    produced_outputs: Set[str]
    capabilities: List[str] = field(default_factory=list)
    model_id: Optional[str] = None
    
    def can_execute_with(self, available_data: Set[str]) -> bool:
        """Check if this agent's inputs are satisfied by available data."""
        return self.required_inputs.issubset(available_data)


@dataclass
class CompositionLayer:
    """A layer of agents that can execute in parallel."""
    layer_index: int
    agents: List[Agent]
    
    @property
    def required_inputs(self) -> Set[str]:
        """All inputs needed by this layer."""
        inputs = set()
        for agent in self.agents:
            inputs.update(agent.required_inputs)
        return inputs
    
    @property
    def produced_outputs(self) -> Set[str]:
        """All outputs produced by this layer."""
        outputs = set()
        for agent in self.agents:
            outputs.update(agent.produced_outputs)
        return outputs
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_index": self.layer_index,
            "agent_ids": [a.id for a in self.agents],
            "agent_names": [a.name for a in self.agents],
            "inputs": list(self.required_inputs),
            "outputs": list(self.produced_outputs),
        }


@dataclass
class CompositionResult:
    """Result of agent composition discovery."""
    found: bool
    layers: List[CompositionLayer]
    initial_data: Set[str]
    target_outputs: Set[str]
    missing: Set[str] = field(default_factory=set)
    discovery_iterations: int = 0
    execution_time_ms: float = 0.0
    
    def describe_plan(self) -> str:
        """Generate human-readable execution plan."""
        if not self.found:
            return f"Cannot answer query. Missing data: {self.missing}"
        
        lines = [f"Execution Plan ({len(self.layers)} layers):"]
        for layer in self.layers:
            agent_names = ", ".join(a.name for a in layer.agents)
            lines.append(f"  Layer {layer.layer_index}: {agent_names}")
        return "\n".join(lines)
    
    def get_all_agent_ids(self) -> List[str]:
        """Get all agent IDs in execution order."""
        return [a.id for layer in self.layers for a in layer.agents]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "found": self.found,
            "plan": self.describe_plan(),
            "layers": [layer.to_dict() for layer in self.layers],
            "total_agents": sum(len(layer.agents) for layer in self.layers),
            "iterations": self.discovery_iterations,
            "missing": list(self.missing) if self.missing else None,
        }


class AgentComposer:
    """
    Implements the graph-based agent composition algorithm from Zhou et al. (2019).
    
    The algorithm iteratively discovers agents whose inputs are satisfied by
    currently available data, simulates their outputs, and repeats until the
    target outputs become available.
    """
    
    def __init__(self, ontology_store, model_registry, max_iterations: int = 10):
        self._ontology = ontology_store
        self._registry = model_registry
        self._max_iterations = max_iterations
        
    async def compose(
        self,
        initial_data: Set[str],
        target_outputs: Set[str],
        timeout_seconds: float = 30.0
    ) -> CompositionResult:
        """
        Discover agent composition to produce target outputs.
        
        Algorithm (from Zhou et al.):
        1. G ← ∅ (final composition result)
        2. C ← ∅ (all agents discovered)
        3. D_collected ← I₀ (initial available data)
        4. repeat:
        5.   i ← i + 1
        6.   Lᵢ ← ∅ (new layer)
        7.   A ← discover_agent(D_collected)
        8.   for all a ∈ A:
        9.     if a ∉ C:
        10.      Lᵢ ← Lᵢ ∪ {a}
        11.      D_collected ← D_collected ∪ {Oₐ}
        12.    C ← C ∪ A
        13.    G ← G ∪ {Lᵢ}
        14.  until O₀ ⊆ D_collected or timeout
        
        Args:
            initial_data: Parameter names currently available in KG
            target_outputs: Parameter names needed for the query
            timeout_seconds: Maximum time for discovery
            
        Returns:
            CompositionResult with discovered layers
        """
        start_time = datetime.utcnow()
        
        # Line 1-3: Initialize
        layers: List[CompositionLayer] = []  # G
        discovered_agents: Dict[str, Agent] = {}  # C (agent_id → Agent)
        available_data = set(initial_data)  # D_collected
        
        iteration = 0
        
        logger.info(f"Starting composition: target={target_outputs}, initial={initial_data}")
        
        # Line 5-14: Iterate until target satisfied or max iterations
        while iteration < self._max_iterations:
            iteration += 1
            
            # Check if we already have all target outputs
            if target_outputs.issubset(available_data):
                logger.info(f"Target outputs available after {iteration-1} iterations")
                break
            
            # Line 7: Discover agents whose inputs are satisfied
            candidates = await self._discover_agents(available_data)
            
            # Line 8-11: Filter to new agents, add to layer, simulate outputs
            new_agents = []
            for agent in candidates:
                if agent.id not in discovered_agents:
                    new_agents.append(agent)
                    discovered_agents[agent.id] = agent
                    # Line 11: Simulate outputs by adding to available data
                    available_data.update(agent.produced_outputs)
                    logger.debug(f"Discovered agent {agent.id}, outputs: {agent.produced_outputs}")
            
            if not new_agents:
                # No new agents discovered - can't make progress
                logger.warning(f"No new agents discovered at iteration {iteration}")
                break
            
            # Line 12-13: Create layer and add to composition
            layer = CompositionLayer(layer_index=iteration-1, agents=new_agents)
            layers.append(layer)
            logger.info(f"Layer {layer.layer_index}: added {len(new_agents)} agents")
        
        elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Check if we satisfied the target
        found = target_outputs.issubset(available_data)
        missing = target_outputs - available_data if not found else set()
        
        if found:
            logger.info(f"Composition found: {len(layers)} layers, {len(discovered_agents)} agents")
        else:
            logger.warning(f"Composition failed, missing: {missing}")
        
        return CompositionResult(
            found=found,
            layers=layers,
            initial_data=initial_data,
            target_outputs=target_outputs,
            missing=missing,
            discovery_iterations=iteration,
            execution_time_ms=elapsed_ms
        )
    
    async def _discover_agents(self, available_data: Set[str]) -> List[Agent]:
        """
        Query ontology for agents whose inputs are satisfied.
        
        SPARQL query finds all ComputationalAgents where ALL required
        inputs are in the available_data set.
        
        Args:
            available_data: Set of parameter names currently available
            
        Returns:
            List of Agent objects that can execute
        """
        if not self._ontology.is_loaded():
            logger.warning("Ontology not loaded, cannot discover agents")
            return []
        
        # Query for all agent operations
        query = """
        PREFIX wf: <https://w3id.org/waterframe/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?agent ?agentLabel ?operation ?software ?endpoint ?modelId
        WHERE {
            ?agent a wf:ComputationalAgent ;
                   wf:offersOperation ?operation ;
                   wf:runsOn ?software .
            OPTIONAL { ?agent rdfs:label ?agentLabel }
            OPTIONAL { ?software wf:apiEndpoint ?endpoint }
            OPTIONAL { ?software wf:serviceId ?modelId }
        }
        """
        
        try:
            results = self._ontology.query_sparql(query)
            agents = []
            
            for binding in results.get("results", {}).get("bindings", []):
                agent_uri = binding.get("agent", {}).get("value", "")
                operation_uri = binding.get("operation", {}).get("value", "")
                endpoint = binding.get("endpoint", {}).get("value", "")
                model_id = binding.get("modelId", {}).get("value")
                name = binding.get("agentLabel", {}).get("value") or agent_uri.split("#")[-1]
                
                # Get inputs and outputs for this operation
                inputs, outputs = await self._get_operation_io(operation_uri)
                
                agent = Agent(
                    id=agent_uri.split("#")[-1] or agent_uri.split("/")[-1],
                    name=name,
                    operation_uri=operation_uri,
                    endpoint=endpoint,
                    required_inputs=inputs,
                    produced_outputs=outputs,
                    model_id=model_id
                )
                
                # Only include agents whose inputs are satisfied
                if agent.can_execute_with(available_data):
                    agents.append(agent)
                    
            return agents
            
        except Exception as e:
            logger.error(f"Agent discovery failed: {e}")
            return []
    
    async def _get_operation_io(self, operation_uri: str) -> tuple[Set[str], Set[str]]:
        """
        Get input and output parameters for an operation.
        
        Args:
            operation_uri: URI of the operation
            
        Returns:
            Tuple of (input_params, output_params) as sets of parameter names
        """
        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        
        SELECT ?param ?paramName ?isInput
        WHERE {{
            <{operation_uri}> wf:requiresInput ?input .
            ?input wf:parameterName ?paramName .
            BIND(true AS ?isInput)
        }}
        UNION
        {{
            <{operation_uri}> wf:producesOutput ?output .
            ?output wf:parameterName ?paramName .
            BIND(false AS ?isInput)
        }}
        """
        
        try:
            results = self._ontology.query_sparql(query)
            inputs = set()
            outputs = set()
            
            for binding in results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                is_input = binding.get("isInput", {}).get("value", "false") == "true"
                
                if is_input:
                    inputs.add(param_name)
                else:
                    outputs.add(param_name)
                    
            return inputs, outputs
            
        except Exception as e:
            logger.error(f"Failed to get I/O for {operation_uri}: {e}")
            return set(), set()


# Global instance
agent_composer: Optional[AgentComposer] = None


def get_agent_composer() -> AgentComposer:
    """Get or create the global AgentComposer instance."""
    global agent_composer
    if agent_composer is None:
        from .ontology_store import ontology_store
        from .model_registry import registry
        agent_composer = AgentComposer(ontology_store, registry)
    return agent_composer
```

### 2. Query Analyzer Service

**File**: `case_studies/ghent/src/ghent_water/orchestrator/services/query_analyzer.py`

```python
"""Service to analyze natural language queries for required outputs."""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .namespace_manager import namespace_manager

logger = logging.getLogger(__name__)


@dataclass
class QueryRequirements:
    """What a query needs to be answered."""
    target_outputs: Set[str]  # Parameter names
    involved_entities: Set[str]  # Entity URIs or IDs
    requires_aggregation: bool
    aggregation_type: Optional[str]  # sum, avg, max, min
    simulation_required: bool  # Whether we need to run models


class QueryAnalyzer:
    """
    Analyzes natural language queries to extract:
    - What output parameters are being asked for
    - What entities are involved
    - Whether simulation/aggregation is needed
    """
    
    # Common patterns for water quality parameters
    PARAMETER_PATTERNS = {
        "cod": ["cod", "chemical oxygen demand"],
        "bod": ["bod", "biological oxygen demand"],
        "tss": ["tss", "total suspended solids", "suspended solids"],
        "tn": ["tn", "total nitrogen", "nitrogen"],
        "tp": ["tp", "total phosphorus", "phosphorus"],
        "flow": ["flow", "flow rate", "discharge", "influent", "effluent"],
        "concentration": ["concentration", "level", "amount"],
        "energy": ["energy", "power consumption", "kwh"],
        "sludge": ["sludge", "biosolids"],
    }
    
    # Entity patterns
    ENTITY_PATTERNS = {
        "mbr": ["mbr", "membrane bioreactor", "bioreactor"],
        "ro": ["ro", "reverse osmosis", "osmosis", "membrane filtration"],
        "infiltration": ["infiltration", "soil", "groundwater"],
        "wwtp": ["wwtp", "wastewater treatment", "treatment plant"],
        "dwp": ["dwp", "drinking water", "water treatment"],
    }
    
    def __init__(self):
        self._ns = namespace_manager
    
    async def analyze(self, question: str) -> QueryRequirements:
        """
        Analyze a natural language question.
        
        Examples:
        - "What is the RO permeate COD?" → {target_outputs: {"ro_permeate_cod"}}
        - "MBR effluent quality?" → {target_outputs: {"mbr_effluent_cod", "mbr_effluent_tss"}}
        - "Total energy consumption?" → {target_outputs: {"energy"}, aggregation: "sum"}
        """
        question_lower = question.lower()
        
        # Extract entities mentioned
        entities = self._extract_entities(question_lower)
        
        # Extract parameters
        params = self._extract_parameters(question_lower, entities)
        
        # Check for aggregation
        aggregation, agg_type = self._detect_aggregation(question_lower)
        
        # Simulation is required if asking about outputs not currently in KG
        simulation = self._requires_simulation(params)
        
        return QueryRequirements(
            target_outputs=params,
            involved_entities=entities,
            requires_aggregation=aggregation,
            aggregation_type=agg_type,
            simulation_required=simulation
        )
    
    def _extract_entities(self, question: str) -> Set[str]:
        """Find entity mentions in the question."""
        entities = set()
        for entity, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in question:
                    entities.add(entity)
                    break
        return entities
    
    def _extract_parameters(self, question: str, entities: Set[str]) -> Set[str]:
        """
        Find parameter names being asked about.
        
        Combines entity context with parameter type.
        """
        params = set()
        
        # Check for compound mentions like "RO permeate COD"
        for entity in entities:
            for param, patterns in self.PARAMETER_PATTERNS.items():
                for pattern in patterns:
                    # Check for patterns like "{entity} {param}" or "{param} of {entity}"
                    if f"{entity} {pattern}" in question or \
                       f"{pattern} of the {entity}" in question or \
                       f"{entity}'s {pattern}" in question:
                        params.add(f"{entity}_{param}")
                        break
        
        # If no specific parameters found, infer from question type
        if not params:
            if "quality" in question:
                # Quality queries usually want multiple parameters
                for entity in entities:
                    params.update([f"{entity}_cod", f"{entity}_tss", f"{entity}_tn"])
            elif "performance" in question:
                params.add("efficiency")
                params.add("energy")
        
        return params
    
    def _detect_aggregation(self, question: str) -> tuple[bool, Optional[str]]:
        """Check if question asks for aggregated values."""
        agg_patterns = {
            "sum": ["total", "sum", "combined", "overall"],
            "avg": ["average", "mean"],
            "max": ["maximum", "max", "highest", "peak"],
            "min": ["minimum", "min", "lowest"],
        }
        
        for agg_type, patterns in agg_patterns.items():
            for pattern in patterns:
                if pattern in question:
                    return True, agg_type
        
        return False, None
    
    def _requires_simulation(self, params: Set[str]) -> bool:
        """
        Check if these parameters require simulation to obtain.
        
        This would query the KG to see if values exist, or check
        if they're classified as "simulated outputs" in ontology.
        """
        # For now, assume any effluent/permeate output requires simulation
        simulated_indicators = ["effluent", "permeate", "outlet", "output"]
        for param in params:
            for indicator in simulated_indicators:
                if indicator in param:
                    return True
        return False


# Global instance
query_analyzer: Optional[QueryAnalyzer] = None


def get_query_analyzer() -> QueryAnalyzer:
    """Get or create the global QueryAnalyzer instance."""
    global query_analyzer
    if query_analyzer is None:
        query_analyzer = QueryAnalyzer()
    return query_analyzer
```

### 3. KG Analyzer Service

**File**: `case_studies/ghent/src/ghent_water/orchestrator/services/kg_analyzer.py`

```python
"""Service to analyze Knowledge Graph data availability."""

import logging
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class KGAnalyzer:
    """
    Analyzes the current state of the Knowledge Graph to determine
    what data is available and what needs to be computed.
    """
    
    def __init__(self, ontology_store):
        self._ontology = ontology_store
    
    async def get_available_parameters(self, entity_filter: Optional[str] = None) -> Set[str]:
        """
        Query the KG to find all parameters that have values.
        
        Returns set of parameter names (via wf:parameterName).
        """
        if not self._ontology.is_loaded():
            return set()
        
        entity_clause = ""
        if entity_filter:
            entity_clause = f'?entity wf:hasId "{entity_filter}" .'
        
        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        
        SELECT DISTINCT ?paramName
        WHERE {{
            {entity_clause}
            ?entity wf:hasParameter ?param .
            ?param wf:parameterName ?paramName ;
                   rdf:value ?value .
        }}
        """
        
        try:
            results = self._ontology.query_sparql(query)
            params = set()
            
            for binding in results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                if param_name:
                    params.add(param_name)
                    
            return params
            
        except Exception as e:
            logger.error(f"Failed to get available parameters: {e}")
            return set()
    
    async def has_parameter_value(self, param_name: str) -> bool:
        """Check if a specific parameter has a value in the KG."""
        query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        
        ASK {{
            ?param wf:parameterName "{param_name}" ;
                   rdf:value ?value .
        }}
        """
        
        try:
            results = self._ontology.query_sparql(query)
            return results.get("boolean", False)
        except Exception as e:
            logger.error(f"Failed to check parameter {param_name}: {e}")
            return False


# Global instance
kg_analyzer: Optional[KGAnalyzer] = None


def get_kg_analyzer() -> KGAnalyzer:
    """Get or create the global KGAnalyzer instance."""
    global kg_analyzer
    if kg_analyzer is None:
        from .ontology_store import ontology_store
        kg_analyzer = KGAnalyzer(ontology_store)
    return kg_analyzer
```

### 4. Enhanced Query Router

**File**: `case_studies/ghent/src/ghent_water/orchestrator/routers/query.py`

Add these imports and the new endpoint:

```python
# Add to existing imports
from ..services.agent_composer import get_agent_composer, CompositionResult
from ..services.query_analyzer import get_query_analyzer
from ..services.kg_analyzer import get_kg_analyzer
from ..services.model_registry import registry

import httpx


# New endpoint for composition discovery
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
                inputs_needed={},  # Could be populated
                outputs_produced=list(layer.produced_outputs)
            )
            for layer in result.layers
        ],
        total_agents=sum(len(layer.agents) for layer in result.layers),
        estimated_execution_time_seconds=len(result.layers) * 5.0  # Rough estimate
    )


# Modified natural query endpoint with composition
@router.post("/natural", response_model=NaturalLanguageQueryResponse)
async def execute_natural_query(request: NaturalLanguageQueryRequest):
    """Execute natural language query with automatic agent composition."""
    
    logger.info(f"Query: {request.question}")
    
    # Step 1: Analyze what the query needs
    analyzer = get_query_analyzer()
    requirements = await analyzer.analyze(request.question)
    
    logger.info(f"Query requires: {requirements.target_outputs}")
    
    # Step 2: Check current KG state
    await ontology_store.load_ontology()
    kg_analyzer = get_kg_analyzer()
    available_data = await kg_analyzer.get_available_parameters()
    
    # Step 3: Check if we can answer directly
    if requirements.target_outputs.issubset(available_data):
        logger.info("Query can be answered directly from KG")
        # ... execute SPARQL normally ...
        return await execute_direct_query(request, requirements)
    
    # Step 4: Need agent composition
    logger.info("Query requires agent composition")
    
    composer = get_agent_composer()
    composition = await composer.compose(
        initial_data=available_data,
        target_outputs=requirements.target_outputs
    )
    
    if not composition.found:
        return NaturalLanguageQueryResponse(
            original_question=request.question,
            generated_sparql=None,
            results=[],
            execution_plan=f"Cannot answer query: {composition.describe_plan()}",
            simulation_required=True,
            suggested_models=[]
        )
    
    # Step 5: Execute the composition
    try:
        execution_results = await execute_composition_layers(composition)
        
        # Step 6: Now query the results
        final_answer = await query_simulation_results(
            requirements.target_outputs,
            execution_results
        )
        
        return NaturalLanguageQueryResponse(
            original_question=request.question,
            generated_sparql=None,  # We didn't use SPARQL, we ran simulations
            results=final_answer,
            execution_plan=composition.describe_plan(),
            simulation_required=True,
            suggested_models=composition.get_all_agent_ids()
        )
        
    except Exception as e:
        logger.error(f"Composition execution failed: {e}")
        return NaturalLanguageQueryResponse(
            original_question=request.question,
            generated_sparql=None,
            results=[],
            execution_plan=f"Execution failed: {str(e)}",
            simulation_required=True,
            suggested_models=[]
        )


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
    
    # Create job
    job_id = registry.create_job(model_id, {"parameters": inputs})
    
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
    
    Maps parameter names between connected agents using ontology relationships.
    """
    inputs = {}
    
    for input_param in agent.required_inputs:
        # Check if it's in initial data
        if input_param in initial_data:
            # Would need to get actual value from KG
            continue
        
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
```

### 5. Schema Additions

**File**: `case_studies/ghent/src/ghent_water/orchestrator/schemas/models.py`

```python
# Add these models to the existing file

class AgentCompositionRequest(BaseModel):
    """Request agent composition discovery."""
    initial_parameters: Dict[str, float] = Field(default_factory=dict)
    target_outputs: List[str]  # Parameter names needed
    max_layers: int = 10
    timeout_seconds: float = 30.0


class CompositionLayerResponse(BaseModel):
    """Serializable layer representation."""
    layer_index: int
    agent_ids: List[str]
    agent_names: List[str]
    parallelizable: bool
    inputs_needed: Dict[str, str]  # Parameter → source
    outputs_produced: List[str]


class AgentCompositionResponse(BaseModel):
    """Response with discovered composition."""
    composition_found: bool
    execution_plan: str
    layers: List[CompositionLayerResponse]
    total_agents: int
    estimated_execution_time_seconds: float
```

## Ontology Template for Household Case

**File**: `case_studies/household/data/agent_declarations.ttl`

```turtle
@prefix wf: <https://w3id.org/waterframe/> .
@prefix cap: <https://w3id.org/waterframe/capability/> .
@prefix case: <https://w3id.org/waterframe/case/household/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# ==================== Services ====================

case:MBR_Service a wf:ModelService ;
    rdfs:label "MBR Model Service" ;
    wf:apiEndpoint "http://localhost:8101" ;
    wf:serviceId "mbr" .

case:RO_Service a wf:ModelService ;
    rdfs:label "RO Model Service" ;
    wf:apiEndpoint "http://localhost:8102" ;
    wf:serviceId "ro" .

case:Infiltration_Service a wf:ModelService ;
    rdfs:label "Infiltration Model Service" ;
    wf:apiEndpoint "http://localhost:8103" ;
    wf:serviceId "infiltration" .

# ==================== Agents ====================

case:MBR_Agent a wf:ComputationalAgent ;
    rdfs:label "Membrane Bioreactor Model" ;
    wf:hasCapability cap:DynamicSimulation, cap:MassBalance, cap:WaterQualityPrediction ;
    wf:implements case:Membrane_bioreactor_Model ;
    wf:runsOn case:MBR_Service ;
    wf:offersOperation case:MBR_Simulation .

case:RO_Agent a wf:ComputationalAgent ;
    rdfs:label "Reverse Osmosis Model" ;
    wf:hasCapability cap:DynamicSimulation, cap:MassBalance, cap:WaterQualityPrediction ;
    wf:implements case:Reverse_osmosis_Model ;
    wf:runsOn case:RO_Service ;
    wf:offersOperation case:RO_Simulation .

case:Infiltration_Agent a wf:ComputationalAgent ;
    rdfs:label "Soil Infiltration Model" ;
    wf:hasCapability cap:DynamicSimulation, cap:MassBalance ;
    wf:implements case:Infiltration_Model ;
    wf:runsOn case:Infiltration_Service ;
    wf:offersOperation case:Infiltration_Simulation .

# ==================== Operations ====================

case:MBR_Simulation a wf:Operation ;
    rdfs:label "Run MBR Simulation" ;
    wf:requiresInput case:MBR_Influent_Flow, 
                     case:MBR_Influent_COD ;
    wf:producesOutput case:MBR_Effluent_Flow, 
                      case:MBR_Effluent_COD,
                      case:MBR_Biomass_Concentration,
                      case:MBR_Energy_Consumption,
                      case:MBR_Sludge_Production .

case:RO_Simulation a wf:Operation ;
    rdfs:label "Run RO Simulation" ;
    wf:requiresInput case:RO_Feed_Flow, 
                     case:RO_Feed_COD ;
    wf:producesOutput case:RO_Permeate_Flow, 
                      case:RO_Permeate_COD,
                      case:RO_Concentrate_Flow,
                      case:RO_Energy_Consumption .

case:Infiltration_Simulation a wf:Operation ;
    rdfs:label "Run Infiltration Simulation" ;
    wf:requiresInput case:INF_Influent_Flow ;
    wf:producesOutput case:INF_Outflow,
                      case:INF_COD_Removed .

# ==================== Parameters ====================

# MBR Inputs
case:MBR_Influent_Flow a wf:InputParameter ;
    wf:parameterName "influent_flow_m3d" ;
    wf:hasUnit "m³/d" .

case:MBR_Influent_COD a wf:InputParameter ;
    wf:parameterName "influent_cod_mg_l" ;
    wf:hasUnit "mg/L" .

# MBR Outputs
case:MBR_Effluent_Flow a wf:OutputParameter ;
    wf:parameterName "effluent_flow_m3d" ;
    wf:hasUnit "m³/d" ;
    wf:compatibleWith case:RO_Feed_Flow .

case:MBR_Effluent_COD a wf:OutputParameter ;
    wf:parameterName "effluent_cod_mg_l" ;
    wf:hasUnit "mg/L" ;
    wf:compatibleWith case:RO_Feed_COD .

case:MBR_Energy_Consumption a wf:OutputParameter ;
    wf:parameterName "energy_kwh_d" ;
    wf:hasUnit "kWh/d" .

# RO Inputs (linked to MBR outputs via compatibleWith)
case:RO_Feed_Flow a wf:InputParameter ;
    wf:parameterName "feed_flow_m3d" ;
    wf:hasUnit "m³/d" .

case:RO_Feed_COD a wf:InputParameter ;
    wf:parameterName "feed_cod_mg_l" ;
    wf:hasUnit "mg/L" .

# RO Outputs
case:RO_Permeate_COD a wf:OutputParameter ;
    wf:parameterName "permeate_cod_mg_l" ;
    wf:hasUnit "mg/L" .

# ==================== Data Flows ====================

# Explicit data flow relationships
case:MBR_Simulation wf:dataFlowsTo case:RO_Simulation .
```

## Testing the Implementation

### Test Script

**File**: `case_studies/household/tests/test_composition.py`

```python
"""Tests for agent composition algorithm."""

import pytest
from unittest.mock import Mock, AsyncMock

from household_water.orchestrator.services.agent_composer import (
    AgentComposer, Agent, CompositionResult
)


@pytest.fixture
def mock_ontology():
    """Mock ontology store."""
    ontology = Mock()
    ontology.is_loaded.return_value = True
    return ontology


@pytest.fixture
def mock_registry():
    """Mock model registry."""
    return Mock()


@pytest.fixture
def composer(mock_ontology, mock_registry):
    """AgentComposer instance with mocks."""
    return AgentComposer(mock_ontology, mock_registry, max_iterations=5)


@pytest.mark.asyncio
async def test_mbr_to_ro_composition(composer, mock_ontology):
    """Test discovering MBR→RO chain."""
    
    # Setup: MBR agent available
    mbr_agent = Agent(
        id="mbr",
        name="MBR Model",
        operation_uri="case:MBR_Simulation",
        endpoint="http://localhost:8101",
        required_inputs={"influent_flow_m3d", "influent_cod_mg_l"},
        produced_outputs={"effluent_flow_m3d", "effluent_cod_mg_l", "energy_kwh_d"},
        model_id="mbr"
    )
    
    ro_agent = Agent(
        id="ro",
        name="RO Model",
        operation_uri="case:RO_Simulation",
        endpoint="http://localhost:8102",
        required_inputs={"feed_flow_m3d", "feed_cod_mg_l"},
        produced_outputs={"permeate_flow_m3d", "permeate_cod_mg_l"},
        model_id="ro"
    )
    
    # Mock discovery to return agents in sequence
    discovery_calls = [
        [mbr_agent],  # First call: only MBR inputs satisfied
        [ro_agent],   # Second call: after MBR outputs added, RO inputs satisfied
    ]
    
    composer._discover_agents = AsyncMock(side_effect=discovery_calls)
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    # Execute
    result = await composer.compose(
        initial_data={"influent_flow_m3d", "influent_cod_mg_l"},
        target_outputs={"permeate_cod_mg_l"}
    )
    
    # Assert
    assert result.found is True
    assert len(result.layers) == 2
    assert result.layers[0].agents[0].id == "mbr"
    assert result.layers[1].agents[0].id == "ro"


@pytest.mark.asyncio
async def test_parallel_agent_discovery(composer, mock_ontology):
    """Test that independent agents are grouped in same layer."""
    
    # Two agents that can both run with initial data
    agent1 = Agent(
        id="agent1",
        name="Agent 1",
        operation_uri="op:1",
        endpoint="http://localhost:8001",
        required_inputs={"input_a"},
        produced_outputs={"output_1"}
    )
    
    agent2 = Agent(
        id="agent2",
        name="Agent 2",
        operation_uri="op:2",
        endpoint="http://localhost:8002",
        required_inputs={"input_a"},
        produced_outputs={"output_2"}
    )
    
    composer._discover_agents = AsyncMock(return_value=[agent1, agent2])
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    result = await composer.compose(
        initial_data={"input_a"},
        target_outputs={"output_1", "output_2"}
    )
    
    # Both agents should be in layer 0 (can run in parallel)
    assert result.found is True
    assert len(result.layers) == 1
    assert len(result.layers[0].agents) == 2


@pytest.mark.asyncio
async def test_no_composition_possible(composer, mock_ontology):
    """Test when target cannot be reached."""
    
    composer._discover_agents = AsyncMock(return_value=[])
    composer._get_operation_io = AsyncMock(return_value=(set(), set()))
    
    result = await composer.compose(
        initial_data={"input_a"},
        target_outputs={"unreachable_output"}
    )
    
    assert result.found is False
    assert "unreachable_output" in result.missing
```

## Integration Steps

1. **Add the service files** to `orchestrator/services/`
2. **Update schemas** in `schemas/models.py`
3. **Add endpoint** to `routers/query.py`
4. **Create ontology declarations** TTL file
5. **Run tests**: `pytest tests/test_composition.py -v`
6. **Test manually**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/compose \
     -H "Content-Type: application/json" \
     -d '{
       "initial_parameters": {"influent_flow_m3d": 1.5, "influent_cod_mg_l": 350},
       "target_outputs": ["permeate_cod_mg_l"]
     }'
   ```
