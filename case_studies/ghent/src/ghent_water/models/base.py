"""Abstract base model class for water system models.

Provides common functionality for all water system component stubs,
including self-description generation using the waterFRAME ontology.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
from datetime import datetime


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

    @abstractmethod
    async def get_state(self) -> Dict[str, Any]:
        """Return current model state (last run results).

        Returns:
            Dictionary containing current model state.
        """
        pass

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

    def _update_state(self, outputs: Dict[str, Any]) -> None:
        """Update internal state after simulation run.

        Args:
            outputs: Simulation output dictionary.
        """
        self._state = {
            "outputs": outputs,
            "timestamp": datetime.utcnow().isoformat(),
            "model_id": self.entity_id,
        }
        self._last_run = datetime.utcnow()

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
