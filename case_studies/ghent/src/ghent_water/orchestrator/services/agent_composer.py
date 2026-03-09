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
        
        SELECT ?paramName ?isInput
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
