"""Agent composition service implementing the graph-based discovery algorithm.

This module provides two composers:
1. AgentComposer: Original string-matching based composition
2. OntologyComposer: Ontology-native composition using waterFRAME property chains

The OntologyComposer leverages:
- wf:dataFlowsTo property chain for automatic composition inference
- wf:requiresInput/wf:producesOutput for operation I/O
- wf:hasCapability for capability-based discovery
- wf:hasPrecondition/wf:hasPostcondition for execution validation
- wf:HTTPGrounding for operation invocation
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
import httpx

try:
    from .execution_trace import EventParameter, AgentType, execution_trace_service
except ImportError:
    # When loaded as a standalone file (e.g. via importlib in some tests),
    # fall back to an absolute import so the symbols are still available.
    try:
        from ontEAUlogy_core.services.execution_trace import (  # type: ignore[no-redef]
            EventParameter, AgentType, execution_trace_service,
        )
    except ImportError:
        EventParameter = None  # type: ignore[assignment,misc]
        AgentType = None       # type: ignore[assignment,misc]
        execution_trace_service = None  # type: ignore[assignment]

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
    inferred_mappings: Dict[str, str] = field(default_factory=dict)
    
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
            "inferred_mappings": self.inferred_mappings,
        }


@dataclass
class ValidationResult:
    """Result of precondition validation."""
    valid: bool
    violations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "violations": self.violations,
        }


@dataclass
class InvocationResult:
    """Result of operation invocation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code,
        }


@dataclass
class CompositionChain:
    """A chain of composable operations discovered via ontology."""
    source_agent: str
    target_agent: str
    shared_output: str
    flow_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "shared_output": self.shared_output,
            "flow_path": self.flow_path,
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
        timeout_seconds: float = 30.0,
        trace_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
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
            trace_id: Optional trace ID for event recording
            scenario_id: Optional scenario ID for parallel scenario support

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

            # Emit layer-discovery event if tracing
            layer_event_id: Optional[str] = None
            if trace_id:
                try:
                    layer_event_id = execution_trace_service.start_event(
                        trace_id,
                        agent_uri="wf:ComposerAgent",
                        agent_name="Composer Agent",
                        agent_type=AgentType.ORCHESTRATOR,
                        operation_uri="wf:DiscoverLayer",
                        operation_name=f"Discover Layer {iteration - 1}",
                        layer_index=iteration - 1,
                        scenario_id=scenario_id,
                        inputs=[EventParameter(name="available_data", value=sorted(available_data))],
                    )
                except Exception:
                    pass

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

            if trace_id and layer_event_id:
                try:
                    execution_trace_service.end_event(
                        trace_id,
                        layer_event_id,
                        outputs=[EventParameter(name="discovered_agents", value=[a.id for a in new_agents])],
                        status="completed",
                    )
                except Exception:
                    pass

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
                
                # Extract short ID from URI (handle both #fragment and /path endings)
                agent_id = agent_uri.split("#")[-1] if "#" in agent_uri else agent_uri.rstrip("/").split("/")[-1]
                
                agent = Agent(
                    id=agent_id,
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
        # Query inputs separately for better SPARQL compatibility
        input_query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        SELECT ?paramName
        WHERE {{
            <{operation_uri}> wf:requiresInput ?input .
            ?input wf:parameterName ?paramName .
        }}
        """
        
        # Query outputs separately for better SPARQL compatibility
        output_query = f"""
        PREFIX wf: <https://w3id.org/waterframe/>
        SELECT ?paramName
        WHERE {{
            <{operation_uri}> wf:producesOutput ?output .
            ?output wf:parameterName ?paramName .
        }}
        """
        
        try:
            inputs = set()
            outputs = set()
            
            # Get inputs
            input_results = self._ontology.query_sparql(input_query)
            for binding in input_results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                if param_name:
                    inputs.add(param_name)
            
            # Get outputs
            output_results = self._ontology.query_sparql(output_query)
            for binding in output_results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                if param_name:
                    outputs.add(param_name)
                    
            return inputs, outputs
            
        except Exception as e:
            logger.error(f"Failed to get I/O for {operation_uri}: {e}")
            return set(), set()


class OntologyComposer:
    """
    Agent composer using waterFRAME ontology property chains for semantic composition.

    Leverages ontology-native capabilities:
    - wf:dataFlowsTo (inferred via property chain: producesOutput + inverse requiresInput)
    - wf:requiresInput/wf:producesOutput for operation I/O specification
    - wf:flowsTo for port-based flow topology
    - wf:hasCapability for capability-based agent discovery
    - wf:hasPrecondition/wf:hasPostcondition for execution validation
    - wf:HTTPGrounding for operation invocation
    """

    def __init__(self, ontology_store, base_url: str = "", max_iterations: int = 10):
        self._ontology = ontology_store
        self._base_url = base_url
        self._max_iterations = max_iterations
        # Cache for kg_uri_for() to avoid repeated SPARQL queries per session
        self._kg_uri_cache: Dict[str, Optional[str]] = {}

    def kg_uri_for(self, param_name: str) -> Optional[str]:
        """Return the KG node URI for a parameter name, or None if not found.

        Result is cached per composer instance (session-level cache).
        """
        if param_name in self._kg_uri_cache:
            return self._kg_uri_cache[param_name]

        if not self._ontology.is_loaded():
            self._kg_uri_cache[param_name] = None
            return None

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?node WHERE {{
            ?node wf:parameterName "{param_name}" .
        }}
        LIMIT 1
        """
        try:
            results = self._ontology.query_sparql(query)
            bindings = results.get("results", {}).get("bindings", [])
            uri = bindings[0]["node"]["value"] if bindings else None
        except Exception:
            uri = None

        self._kg_uri_cache[param_name] = uri
        return uri

    async def compose(
        self,
        initial_data: Set[str],
        target_outputs: Set[str],
        timeout_seconds: float = 30.0,
        trace_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
    ) -> CompositionResult:
        """
        Compose agents using ontology relationships.

        Leverages the wf:dataFlowsTo property chain which is inferred when:
        - Operation A producesOutput X
        - Operation B requiresInput X

        Args:
            initial_data: Set of parameter names currently available
            target_outputs: Set of parameter names needed for the query
            timeout_seconds: Maximum time for discovery
            trace_id: Optional trace ID for event recording
            scenario_id: Optional scenario ID for parallel scenario support

        Returns:
            CompositionResult with discovered layers and inferred mappings
        """
        start_time = datetime.utcnow()

        # Initialize
        layers: List[CompositionLayer] = []
        discovered_agents: Dict[str, Agent] = {}
        available_data = set(initial_data)
        inferred_mappings: Dict[str, str] = {}

        iteration = 0

        logger.info(f"Starting ontology-based composition: target={target_outputs}, initial={initial_data}")

        while iteration < self._max_iterations:
            iteration += 1

            # Check if we already have all target outputs
            if target_outputs.issubset(available_data):
                logger.info(f"Target outputs available after {iteration-1} iterations")
                break

            # Emit layer-discovery event if tracing
            layer_event_id: Optional[str] = None
            if trace_id:
                try:
                    layer_event_id = execution_trace_service.start_event(
                        trace_id,
                        agent_uri="wf:ComposerAgent",
                        agent_name="Composer Agent",
                        agent_type=AgentType.ORCHESTRATOR,
                        operation_uri="wf:DiscoverLayer",
                        operation_name=f"Discover Layer {iteration - 1}",
                        layer_index=iteration - 1,
                        scenario_id=scenario_id,
                        inputs=[EventParameter(name="available_data", value=sorted(available_data))],
                    )
                except Exception:
                    pass

            # Discover agents using ontology property chains
            candidates = await self._discover_agents_ontology_based(available_data)

            new_agents = []
            for agent in candidates:
                if agent.id not in discovered_agents:
                    new_agents.append(agent)
                    discovered_agents[agent.id] = agent
                    available_data.update(agent.produced_outputs)

                    # Track inferred mappings via dataFlowsTo
                    mappings = await self._get_inferred_mappings(agent.operation_uri)
                    inferred_mappings.update(mappings)

                    logger.debug(f"Discovered agent {agent.id}, outputs: {agent.produced_outputs}")

            if trace_id and layer_event_id:
                try:
                    execution_trace_service.end_event(
                        trace_id,
                        layer_event_id,
                        outputs=[EventParameter(name="discovered_agents", value=[a.id for a in new_agents])],
                        status="completed",
                    )
                except Exception:
                    pass

            if not new_agents:
                logger.warning(f"No new agents discovered at iteration {iteration}")
                break

            layer = CompositionLayer(layer_index=iteration-1, agents=new_agents)
            layers.append(layer)
            logger.info(f"Layer {layer.layer_index}: added {len(new_agents)} agents")

        elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

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
            execution_time_ms=elapsed_ms,
            inferred_mappings=inferred_mappings
        )

    async def _discover_agents_ontology_based(self, available_data: Set[str]) -> List[Agent]:
        """
        Discover agents using ontology property chains.

        Uses SPARQL to find operations where wf:dataFlowsTo is inferred
        via the property chain axiom.

        Args:
            available_data: Set of parameter names currently available

        Returns:
            List of Agent objects that can execute
        """
        if not self._ontology.is_loaded():
            logger.warning("Ontology not loaded, cannot discover agents")
            return []

        # Build filter for available data parameters
        data_filter = ", ".join(f'"{d}"' for d in available_data)

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?agent ?agentLabel ?operation ?software ?endpoint ?modelId
        WHERE {{
            ?agent a wf:ComputationalAgent ;
                   wf:offersOperation ?operation ;
                   wf:runsOn ?software .

            ?operation wf:requiresInput ?input .
            ?input wf:parameterName ?paramName .

            FILTER(?paramName IN ({data_filter}))

            OPTIONAL {{ ?agent rdfs:label ?agentLabel }}
            OPTIONAL {{ ?software wf:apiEndpoint ?endpoint }}
            OPTIONAL {{ ?software wf:serviceId ?modelId }}
        }}
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
                inputs, outputs = await self._get_operation_io_ontology(operation_uri)

                # Check if all required inputs are available (using ontology reasoning)
                if inputs.issubset(available_data):
                    agent_id = agent_uri.split("#")[-1] if "#" in agent_uri else agent_uri.rstrip("/").split("/")[-1]

                    agent = Agent(
                        id=agent_id,
                        name=name,
                        operation_uri=operation_uri,
                        endpoint=endpoint,
                        required_inputs=inputs,
                        produced_outputs=outputs,
                        model_id=model_id
                    )
                    agents.append(agent)

            return agents

        except Exception as e:
            logger.error(f"Ontology-based agent discovery failed: {e}")
            return []

    async def _get_operation_io_ontology(self, operation_uri: str) -> Tuple[Set[str], Set[str]]:
        """
        Get input and output parameters for an operation using ontology patterns.

        Args:
            operation_uri: URI of the operation

        Returns:
            Tuple of (input_params, output_params) as sets of parameter names
        """
        # Query inputs using wf:requiresInput
        input_query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?paramName
        WHERE {{
            <{operation_uri}> wf:requiresInput ?input .
            ?input wf:parameterName ?paramName .
        }}
        """

        # Query outputs using wf:producesOutput
        output_query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?paramName
        WHERE {{
            <{operation_uri}> wf:producesOutput ?output .
            ?output wf:parameterName ?paramName .
        }}
        """

        try:
            inputs = set()
            outputs = set()

            # Get inputs
            input_results = self._ontology.query_sparql(input_query)
            for binding in input_results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                if param_name:
                    inputs.add(param_name)

            # Get outputs
            output_results = self._ontology.query_sparql(output_query)
            for binding in output_results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                if param_name:
                    outputs.add(param_name)

            return inputs, outputs

        except Exception as e:
            logger.error(f"Failed to get I/O for {operation_uri}: {e}")
            return set(), set()

    async def _get_inferred_mappings(self, operation_uri: str) -> Dict[str, str]:
        """
        Get inferred data flow mappings via wf:dataFlowsTo property chain.

        Args:
            operation_uri: URI of the source operation

        Returns:
            Dictionary mapping outputs to target operation inputs
        """
        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        SELECT ?targetOp ?sharedOutput ?paramName
        WHERE {{
            <{operation_uri}> wf:producesOutput ?sharedOutput .
            ?sharedOutput wf:parameterName ?paramName .

            # dataFlowsTo is inferred by reasoner via property chain
            <{operation_uri}> wf:dataFlowsTo ?targetOp .
        }}
        """

        try:
            results = self._ontology.query_sparql(query)
            mappings = {}

            for binding in results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                target_op = binding.get("targetOp", {}).get("value", "")
                if param_name and target_op:
                    mappings[param_name] = target_op

            return mappings

        except Exception as e:
            logger.error(f"Failed to get inferred mappings for {operation_uri}: {e}")
            return {}

    async def discover_by_capability(
        self,
        required_capabilities: List[str],
        available_data: Set[str]
    ) -> List[Agent]:
        """
        Discover agents by capability using cap:* taxonomy.

        Capabilities from capabilities.ttl:
        - cap:DynamicSimulation
        - cap:WaterQualityPrediction
        - cap:MassBalance
        - cap:Optimization

        Args:
            required_capabilities: List of capability IRIs or short names
            available_data: Set of available parameter names

        Returns:
            List of agents matching the required capabilities
        """
        if not self._ontology.is_loaded():
            logger.warning("Ontology not loaded, cannot discover by capability")
            return []

        # Build capability filter
        cap_filter = ", ".join(f"<{cap}>" if not cap.startswith("http") else f"<{cap}>"
                               for cap in required_capabilities)

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
        PREFIX cap: <https://ugentbiomath.github.io/waterframe/capability#>

        SELECT DISTINCT ?agent ?agentLabel ?operation ?endpoint ?modelId
        WHERE {{
            ?agent a wf:ComputationalAgent ;
                   wf:hasCapability ?cap ;
                   wf:offersOperation ?operation ;
                   wf:runsOn ?software .

            FILTER(?cap IN ({cap_filter}))

            OPTIONAL {{ ?agent rdfs:label ?agentLabel }}
            OPTIONAL {{ ?software wf:apiEndpoint ?endpoint }}
            OPTIONAL {{ ?software wf:serviceId ?modelId }}
        }}
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

                inputs, outputs = await self._get_operation_io_ontology(operation_uri)

                agent_id = agent_uri.split("#")[-1] if "#" in agent_uri else agent_uri.rstrip("/").split("/")[-1]

                agent = Agent(
                    id=agent_id,
                    name=name,
                    operation_uri=operation_uri,
                    endpoint=endpoint,
                    required_inputs=inputs,
                    produced_outputs=outputs,
                    model_id=model_id
                )
                agents.append(agent)

            return agents

        except Exception as e:
            logger.error(f"Capability-based discovery failed: {e}")
            return []

    async def compose_via_physical_flows(
        self,
        source_entity: str
    ) -> List[CompositionChain]:
        """
        Discover composition chains via physical flow connections.

        Uses port topology:
        - wf:OutputPort flowsTo wf:InputPort
        - Component hasDownstreamComponent Component

        Args:
            source_entity: URI of the source entity (e.g., case:WWTP1)

        Returns:
            List of composition chains discovered via physical flows
        """
        if not self._ontology.is_loaded():
            logger.warning("Ontology not loaded, cannot compose via physical flows")
            return []

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

        SELECT ?sourceAgent ?targetAgent ?outPort ?inPort
        WHERE {{
            # Source entity has output port
            <{source_entity}> wf:hasOutputPort ?outPort .

            # Port flows to downstream input port (transitive)
            ?outPort wf:flowsTo+ ?inPort .

            # Find target entity with this input port
            ?targetEntity wf:hasInputPort ?inPort .

            # Find agents monitoring these ports
            ?sourceAgent wf:monitorsPort ?outPort .
            ?targetAgent wf:monitorsPort ?inPort .
        }}
        """

        try:
            results = self._ontology.query_sparql(query)
            chains = []

            for binding in results.get("results", {}).get("bindings", []):
                source_agent = binding.get("sourceAgent", {}).get("value", "")
                target_agent = binding.get("targetAgent", {}).get("value", "")
                out_port = binding.get("outPort", {}).get("value", "")

                chain = CompositionChain(
                    source_agent=source_agent,
                    target_agent=target_agent,
                    shared_output="",  # Would need additional query for parameter
                    flow_path=out_port
                )
                chains.append(chain)

            return chains

        except Exception as e:
            logger.error(f"Physical flow composition failed: {e}")
            return []

    async def validate_execution(
        self,
        operation: str,
        input_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate operation execution against preconditions.

        Uses wf:hasPrecondition, wf:constraintExpression from agents.ttl

        Args:
            operation: URI of the operation to validate
            input_data: Dictionary of input parameter values

        Returns:
            ValidationResult indicating if execution is valid
        """
        if not self._ontology.is_loaded():
            logger.warning("Ontology not loaded, cannot validate execution")
            return ValidationResult(valid=True)  # Allow execution if no ontology

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

        SELECT ?constraint ?expression ?paramName
        WHERE {{
            <{operation}> wf:hasPrecondition ?precond .
            ?precond wf:constrainsParameter ?constraint ;
                     wf:constraintExpression ?expression .
            OPTIONAL {{ ?constraint wf:parameterName ?paramName }}
        }}
        """

        try:
            results = self._ontology.query_sparql(query)
            violations = []

            for binding in results.get("results", {}).get("bindings", []):
                param_name = binding.get("paramName", {}).get("value", "")
                expr = binding.get("expression", {}).get("value", "")

                if param_name in input_data:
                    if not self._evaluate_constraint(expr, input_data[param_name]):
                        violations.append(f"{param_name}: {expr}")

            return ValidationResult(
                valid=len(violations) == 0,
                violations=violations
            )

        except Exception as e:
            logger.error(f"Execution validation failed: {e}")
            return ValidationResult(valid=False, violations=[str(e)])

    def _evaluate_constraint(self, expression: str, value: Any) -> bool:
        """
        Evaluate a constraint expression against a value.

        Args:
            expression: Constraint expression (e.g., "flow_rate > 0")
            value: Value to check

        Returns:
            True if constraint is satisfied
        """
        try:
            # Simple constraint evaluation for common patterns
            expression = expression.strip()

            # Handle comparison operators - check multi-char operators first
            if ">=" in expression:
                parts = expression.split(">=", 1)
                if len(parts) == 2:
                    threshold = float(parts[1].strip())
                    return float(value) >= threshold

            if "<=" in expression:
                parts = expression.split("<=", 1)
                if len(parts) == 2:
                    threshold = float(parts[1].strip())
                    return float(value) <= threshold

            if "==" in expression:
                parts = expression.split("==", 1)
                if len(parts) == 2:
                    expected = parts[1].strip().strip('"\'')
                    return str(value) == expected

            # Single-char operators after multi-char ones
            if ">" in expression:
                parts = expression.split(">", 1)
                if len(parts) == 2:
                    threshold = float(parts[1].strip())
                    return float(value) > threshold

            if "<" in expression:
                parts = expression.split("<", 1)
                if len(parts) == 2:
                    threshold = float(parts[1].strip())
                    return float(value) < threshold

            # Default: allow execution
            return True

        except (ValueError, TypeError) as e:
            logger.warning(f"Could not evaluate constraint '{expression}' with value '{value}': {e}")
            return True

    async def invoke_operation(
        self,
        operation: str,
        input_data: Dict[str, Any]
    ) -> InvocationResult:
        """
        Invoke operation using HTTP grounding from ontology.

        Uses wf:hasHTTPGrounding, wf:httpMethod, wf:operationPath

        Args:
            operation: URI of the operation to invoke
            input_data: Input data for the operation

        Returns:
            InvocationResult with success status and response data
        """
        if not self._ontology.is_loaded():
            return InvocationResult(
                success=False,
                error="Ontology not loaded, cannot invoke operation"
            )

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

        SELECT ?method ?path ?requestFormat ?responseFormat
        WHERE {{
            <{operation}> wf:hasHTTPGrounding ?grounding .
            ?grounding wf:httpMethod ?method ;
                       wf:operationPath ?path ;
                       wf:requestFormat ?requestFormat ;
                       wf:responseFormat ?responseFormat .
        }}
        """

        try:
            results = self._ontology.query_sparql(query)
            bindings = results.get("results", {}).get("bindings", [])

            if not bindings:
                return InvocationResult(
                    success=False,
                    error=f"No HTTP grounding found for operation {operation}"
                )

            binding = bindings[0]
            method = binding.get("method", {}).get("value", "POST")
            path = binding.get("path", {}).get("value", "")
            request_format = binding.get("requestFormat", {}).get("value", "application/json")
            response_format = binding.get("responseFormat", {}).get("value", "application/json")

            # Build full URL
            url = f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"

            # Validate preconditions before invocation
            validation = await self.validate_execution(operation, input_data)
            if not validation.valid:
                return InvocationResult(
                    success=False,
                    error=f"Precondition validation failed: {validation.violations}"
                )

            # Invoke via HTTP
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=input_data)
                else:
                    response = await client.post(
                        url,
                        json=input_data,
                        headers={"Content-Type": request_format}
                    )

                # Parse response
                if response_format == "application/json":
                    data = response.json()
                else:
                    data = response.text

                return InvocationResult(
                    success=response.status_code == 200,
                    data=data,
                    status_code=response.status_code,
                    error=None if response.status_code == 200 else response.text
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP invocation failed for {operation}: {e}")
            return InvocationResult(
                success=False,
                error=f"HTTP error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Invocation failed for {operation}: {e}")
            return InvocationResult(
                success=False,
                error=str(e)
            )

    async def find_composable_operations(
        self,
        source_operation: str
    ) -> List[Dict[str, Any]]:
        """
        Find operations that can be composed with the source operation.

        Uses the wf:dataFlowsTo property chain inference.

        Args:
            source_operation: URI of the source operation

        Returns:
            List of composable operations with shared outputs
        """
        if not self._ontology.is_loaded():
            logger.warning("Ontology not loaded, cannot find composable operations")
            return []

        query = f"""
        PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

        SELECT ?sourceOp ?targetOp ?sharedOutput ?paramName
        WHERE {{
            <{source_operation}> wf:producesOutput ?sharedOutput .
            ?sharedOutput wf:parameterName ?paramName .

            ?targetOp wf:requiresInput ?sharedOutput .

            # dataFlowsTo is inferred by reasoner via property chain
            <{source_operation}> wf:dataFlowsTo ?targetOp .
        }}
        """

        try:
            results = self._ontology.query_sparql(query)
            compositions = []

            for binding in results.get("results", {}).get("bindings", []):
                compositions.append({
                    "source_operation": binding.get("sourceOp", {}).get("value", ""),
                    "target_operation": binding.get("targetOp", {}).get("value", ""),
                    "shared_output": binding.get("sharedOutput", {}).get("value", ""),
                    "parameter_name": binding.get("paramName", {}).get("value", "")
                })

            return compositions

        except Exception as e:
            logger.error(f"Failed to find composable operations: {e}")
            return []


# Global instances
agent_composer: Optional[AgentComposer] = None
ontology_composer: Optional[OntologyComposer] = None


def get_agent_composer() -> AgentComposer:
    """Get or create the global AgentComposer instance."""
    global agent_composer
    if agent_composer is None:
        from .ontology_store import ontology_store
        from .model_registry import registry
        agent_composer = AgentComposer(ontology_store, registry)
    return agent_composer


def get_ontology_composer(base_url: str = "") -> OntologyComposer:
    """Get or create the global OntologyComposer instance."""
    global ontology_composer
    if ontology_composer is None:
        from .ontology_store import ontology_store
        ontology_composer = OntologyComposer(ontology_store, base_url=base_url)
    return ontology_composer
