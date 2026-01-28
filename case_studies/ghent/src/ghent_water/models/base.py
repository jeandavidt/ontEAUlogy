"""Abstract base model class for water system models.

Provides common functionality for all water system component stubs,
including self-description generation using the waterFRAME ontology.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
from datetime import datetime


class ModelStatus:
    """Model status constants."""
    READY = "Ready"
    RUNNING = "Running"
    ERROR = "Error"


# Ontology namespace constants
WATERFRAME_BASE = "https://w3id.org/waterframe/"
WF = WATERFRAME_BASE
CAP = f"{WATERFRAME_BASE}capability/"
CASE_GHENT = f"{WATERFRAME_BASE}case/ghent/"


class BaseWaterModel(ABC):
    """Abstract base class for all water system models.

    Provides core interfaces for:
    - Self-description (JSON-LD/Turtle)
    - Simulation execution
    - State management
    - Health checks
    """

    def __init__(
        self,
        entity_id: str,
        entity_name: str,
        entity_type: str,
        port: int,
        capabilities: Optional[list] = None,
        inputs: Optional[list] = None,
        outputs: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize base water model.

        Args:
            entity_id: Unique identifier for the entity (e.g., "DWP1")
            entity_name: Human-readable name (e.g., "Drinking Water Plant 1")
            entity_type: Type of entity (e.g., "ProcessModel")
            port: HTTP port for the model service
            capabilities: List of capability identifiers
            inputs: List of input parameter definitions
            outputs: List of output parameter definitions
            metadata: Additional entity metadata
        """
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.port = port
        self.capabilities = capabilities or []
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.metadata = metadata or {}
        self._state: Dict[str, Any] = {}
        self._last_run: Optional[datetime] = None
        self._status: str = ModelStatus.READY

    @property
    def api_endpoint(self) -> str:
        """Return the API endpoint URL for this model."""
        return f"http://localhost:{self.port}"

    @property
    def model_iri(self) -> str:
        """Return the full IRI for this model."""
        return f"{CASE_GHENT}{self.entity_id}_Model"

    @property
    def entity_iri(self) -> str:
        """Return the IRI for the entity this model represents."""
        return f"{CASE_GHENT}{self.entity_id}"

    @abstractmethod
    async def describe(self) -> Dict[str, Any]:
        """Return JSON-LD self-description using waterFRAME ontology.

        Returns:
            Dictionary containing JSON-LD formatted self-description.
        """
        pass

    @abstractmethod
    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run simulation with given inputs, return outputs.

        Args:
            inputs: Dictionary of input parameters for simulation.

        Returns:
            Dictionary containing simulation results.
        """
        pass

    async def get_state(self) -> Dict[str, Any]:
        """Return current model state (last run results).

        Returns:
            Dictionary containing current model state including status.
        """
        return {
            **self._state,
            "status": self._status,
            "model": self.entity_id,
            "type": self.entity_type,
            "endpoint": self.api_endpoint,
        }

    def generate_ttl_description(self) -> str:
        """Generate Turtle self-description for this model.

        Returns:
            String containing TTL formatted self-description.
        """
        capabilities_ttl = "\n    ".join(
            f"[ a cap:{cap} ]" for cap in self.capabilities
        ) if self.capabilities else ""

        inputs_ttl = "\n    ".join(
            f'''[ wf:parameterName "{inp["name"]}" ;
              wf:hasUnit "{inp.get("unit", "dimensionless")}" ;
              wf:hasDataType "{inp.get("datatype", "float")}" ]'''
            for inp in self.inputs
        ) if self.inputs else ""

        outputs_ttl = "\n    ".join(
            f'''[ wf:parameterName "{out["name"]}" ;
              wf:hasUnit "{out.get("unit", "dimensionless")}" ;
              wf:hasDataType "{out.get("datatype", "float")}" ]'''
            for out in self.outputs
        ) if self.outputs else ""

        metadata_ttl = ""
        for key, value in self.metadata.items():
            if isinstance(value, str):
                metadata_ttl += f'\n    wf:{key} "{value}" ;'
            elif isinstance(value, bool):
                metadata_ttl += f'\n    wf:{key} {"true" if value else "false"} ;'
            elif isinstance(value, (int, float)):
                metadata_ttl += f'\n    wf:{key} {value} ;'

        ttl = f"""@prefix wf: <{WATERFRAME_BASE}> .
@prefix cap: <{CAP}> .
@prefix ghent: <{CASE_GHENT}> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ghent:{self.entity_id}_Model a wf:{self.entity_type} ;
    rdfs:label "{self.entity_name}" ;
    wf:representsEntity ghent:{self.entity_id} ;
    wf:hasIdentifier "{self.entity_id}" ;{capabilities_ttl}
    wf:hasInput {inputs_ttl if inputs_ttl else "[]"} ;
    wf:hasOutput {outputs_ttl if outputs_ttl else "[]"} ;
    wf:implementedBy "stub" ;
    wf:apiEndpoint <{self.api_endpoint}> ;{metadata_ttl}
    wf:port {self.port} .
"""
        return ttl

    def generate_agent_ttl(self) -> str:
        """Generate Turtle description for agent, software system, and operation.

        This extends the base model description with agent-aware semantics,
        enabling compositional reasoning and service discovery.

        Returns:
            String containing TTL formatted agent description.
        """
        # Generate base model TTL
        base_ttl = self.generate_ttl_description()

        # Generate software system instance (REUSE existing SoftwareSystem class!)
        software_ttl = f"""
# Software System
ghent:{self.entity_id}_Software a wf:SoftwareSystem ;
    rdfs:label "{self.entity_name} Software" ;
    wf:apiEndpoint <{self.api_endpoint}> ;
    wf:apiVersion "1.0" .
"""

        # Generate agent instance
        capabilities_refs = ", ".join(
            f"cap:{cap}" for cap in self.capabilities
        ) if self.capabilities else ""

        agent_ttl = f"""
# Computational Agent
ghent:{self.entity_id}_Agent a wf:SimulationAgent ;
    rdfs:label "{self.entity_name} Agent" ;
    wf:implements ghent:{self.entity_id}_Model ;
    wf:simulates ghent:{self.entity_id} ;
    wf:runsOn ghent:{self.entity_id}_Software ;"""

        if capabilities_refs:
            agent_ttl += f"""
    wf:hasCapability {capabilities_refs} ;"""

        agent_ttl += f"""
    wf:offersOperation ghent:{self.entity_id}_SimulateOp ;
    wf:agentVersion "1.0.0" .
"""

        # Generate operation instance (REUSE same input/output objects as model!)
        # Build input/output references
        input_refs = ", ".join(
            f"ghent:{inp['name']}_Input" for inp in self.inputs
        ) if self.inputs else ""

        output_refs = ", ".join(
            f"ghent:{out['name']}_Output" for out in self.outputs
        ) if self.outputs else ""

        operation_ttl = f"""
# Operation
ghent:{self.entity_id}_SimulateOp a wf:Operation ;
    rdfs:label "Simulate {self.entity_name}" ;"""

        if input_refs:
            operation_ttl += f"""
    wf:requiresInput {input_refs} ;"""

        if output_refs:
            operation_ttl += f"""
    wf:producesOutput {output_refs} ;"""

        # Add preconditions for numeric inputs (must be >= 0)
        preconditions = []
        for inp in self.inputs:
            if inp.get("datatype", "float") in ["float", "int", "integer", "number"]:
                preconditions.append(f"""
    wf:hasPrecondition [
        a wf:Precondition ;
        wf:constrainsParameter ghent:{inp['name']}_Input ;
        wf:constraintExpression "{inp['name']} >= 0" ;
        rdfs:comment "{inp['name'].replace('_', ' ').title()} cannot be negative"
    ] ;""")

        operation_ttl += "".join(preconditions)

        # Add HTTP grounding
        operation_ttl += f"""
    wf:hasHTTPGrounding [
        a wf:HTTPGrounding ;
        wf:httpMethod "POST" ;
        wf:operationPath "/simulate" ;
        wf:requestFormat "application/json" ;
        wf:responseFormat "application/json" ;
        wf:requiresAuthentication "false"^^xsd:boolean
    ] ;
    wf:estimatedExecutionTime "2.0"^^xsd:float ;
    wf:computationalComplexity "O(n)" .
"""

        # Combine all parts
        return base_ttl + software_ttl + agent_ttl + operation_ttl

    @property
    def agent_iri(self) -> str:
        """Return the IRI for this agent."""
        return f"{CASE_GHENT}{self.entity_id}_Agent"

    @property
    def operation_iri(self) -> str:
        """Return the IRI for this agent's main operation."""
        return f"{CASE_GHENT}{self.entity_id}_SimulateOp"

    @property
    def software_iri(self) -> str:
        """Return the IRI for this agent's software system."""
        return f"{CASE_GHENT}{self.entity_id}_Software"

    async def register_with_orchestrator(self, orchestrator_url: str) -> Dict[str, Any]:
        """Register model with orchestrator service.

        Args:
            orchestrator_url: URL of the orchestrator service.

        Returns:
            Response from orchestrator.
        """
        import httpx

        description = await self.describe()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{orchestrator_url}/register",
                json=description,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the model service.

        Returns:
            Health status dictionary.
        """
        return {
            "status": "healthy",
            "model": self.entity_id,
            "type": self.entity_type,
            "endpoint": self.api_endpoint,
            "last_run": self._last_run.isoformat() if self._last_run else None,
        }

    def _update_state(self, outputs: Dict[str, Any], status: Optional[str] = None) -> None:
        """Update internal state after simulation run.
        
        Args:
            outputs: Simulation output dictionary.
            status: Optional status to set (defaults to Ready after simulation).
        """
        self._state = {
            "outputs": outputs,
            "timestamp": datetime.utcnow().isoformat(),
            "model_id": self.entity_id,
            "status": status or ModelStatus.READY,
        }
        self._last_run = datetime.utcnow()
        self._status = status or ModelStatus.READY

    def _get_parameter_value(
        self, inputs: Dict[str, Any], param_name: str, default: Any = None
    ) -> Any:
        """Get parameter value from inputs, with fallback to default.

        Args:
            inputs: Input dictionary.
            param_name: Name of parameter to retrieve.
            default: Default value if parameter not found.

        Returns:
            Parameter value or default.
        """
        # Try direct match first
        if param_name in inputs:
            return inputs[param_name]

        # Try with prefix/suffix variations
        variations = [
            f"input_{param_name}",
            param_name.replace(" ", "_"),
            param_name.lower().replace(" ", "_"),
        ]
        for var in variations:
            if var in inputs:
                return inputs[var]

        return default
