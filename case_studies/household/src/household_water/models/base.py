"""Abstract base model class for household water system models.

Adapted from ghent_water BaseWaterModel with household-specific namespace.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from rdflib import Graph, Literal, Namespace, RDF, XSD
from rdflib.term import BNode


class ModelStatus:
    """Model status constants."""
    READY = "Ready"
    RUNNING = "Running"
    ERROR = "Error"


# Ontology namespace constants
WATERFRAME_BASE = "https://ugentbiomath.github.io/waterframe#"
WF = WATERFRAME_BASE
CAP = "https://ugentbiomath.github.io/waterframe/capability#"
CASE_HOUSEHOLD = "https://w3id.org/waterframe/case/household/"
HOUSECASE1 = "https://ugentbiomath.github.io/ontology/index.ttl#"


class BaseHouseholdModel(ABC):
    """Abstract base class for household water system models."""

    # Subclasses may override these class-level attributes.
    _PARAM_BOUNDS: Dict[str, Tuple[float, float]] = {}
    _default_params: Dict[str, float] = {}
    _default_scenario_iri: str = (
        "https://ugentbiomath.github.io/ontology/index.ttl#Baseline_Scenario"
    )

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
        self._parameters: Dict[str, float] = dict(self._default_params)

    @property
    def api_endpoint(self) -> str:
        return f"http://localhost:{self.port}"

    @property
    def model_iri(self) -> str:
        return f"{CASE_HOUSEHOLD}{self.entity_id}_Model"

    @property
    def entity_iri(self) -> str:
        """IRI of the physical entity in household_case1.ttl."""
        return f"{HOUSECASE1}{self.entity_id}"

    # ------------------------------------------------------------------
    # Parameter management
    # ------------------------------------------------------------------

    def get_default_params_dict(self) -> Dict[str, float]:
        """Return a copy of the class-level default parameters.

        Returns:
            A shallow copy of ``_default_params``.
        """
        return dict(self._default_params)

    def update_parameters(self, params: Dict[str, float]) -> None:
        """Merge *params* into the instance parameter store.

        Args:
            params: Mapping of parameter name to new value.
        """
        self._parameters.update(params)

    def get_param_bounds(
        self, names: List[str]
    ) -> Tuple[List[float], List[float]]:
        """Return lower and upper bounds for the requested parameter names.

        Args:
            names: Ordered list of parameter names to look up.

        Returns:
            A tuple ``(lows, highs)`` where each element is a list
            aligned with *names*.

        Raises:
            KeyError: If a name is not present in ``_PARAM_BOUNDS``.
        """
        lows = [self._PARAM_BOUNDS[n][0] for n in names]
        highs = [self._PARAM_BOUNDS[n][1] for n in names]
        return lows, highs

    def simulate_sync(
        self,
        inputs: Dict[str, Any],
        params_override: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Synchronous simulation entry point.

        Subclasses must override this method.  Any values in
        *params_override* are merged into ``self._parameters``
        temporarily before the simulation runs and restored afterwards.

        Args:
            inputs: Model input values.
            params_override: Optional parameter overrides applied only
                for this call.

        Returns:
            Simulation output dictionary.

        Raises:
            NotImplementedError: Always — subclasses must override.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement simulate_sync"
        )

    def params_to_turtle(self, params: Dict[str, float]) -> str:
        """Serialise *params* as Turtle ``wf:Parameter`` blank nodes.

        Args:
            params: Mapping of parameter name to numeric value.

        Returns:
            A Turtle-formatted string with one ``wf:Parameter`` blank
            node per key-value pair, using the WaterFrame namespace.

        Example::

            @prefix wf: <https://ugentbiomath.github.io/waterframe#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            [] a wf:Parameter ;
                wf:parameterName "mu_max" ;
                rdf:value "6.0"^^xsd:float .
        """
        _WF = Namespace(WATERFRAME_BASE)
        _RDF = RDF

        g = Graph()
        g.bind("wf", _WF)
        g.bind("xsd", XSD)
        g.bind("rdf", _RDF)

        for name, value in params.items():
            node = BNode()
            g.add((node, _RDF.type, _WF.Parameter))
            g.add((node, _WF.parameterName, Literal(name)))
            g.add((node, _RDF.value, Literal(float(value), datatype=XSD.float)))

        return g.serialize(format="turtle")

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def describe(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def get_state(self) -> Dict[str, Any]:
        return {
            **self._state,
            "status": self._status,
            "model": self.entity_id,
            "type": self.entity_type,
            "endpoint": self.api_endpoint,
        }

    def generate_ttl_description(self) -> str:
        inputs_ttl = "\n    ".join(
            f'[ wf:parameterName "{inp["name"]}" ;'
            f' wf:hasUnit "{inp.get("unit", "dimensionless")}" ;'
            f' wf:hasDataType "{inp.get("datatype", "float")}" ]'
            for inp in self.inputs
        ) if self.inputs else "[]"

        outputs_ttl = "\n    ".join(
            f'[ wf:parameterName "{out["name"]}" ;'
            f' wf:hasUnit "{out.get("unit", "dimensionless")}" ;'
            f' wf:hasDataType "{out.get("datatype", "float")}" ]'
            for out in self.outputs
        ) if self.outputs else "[]"

        return f"""@prefix wf: <{WATERFRAME_BASE}> .
@prefix cap: <{CAP}> .
@prefix household: <{CASE_HOUSEHOLD}> .
@prefix housecase1: <{HOUSECASE1}> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

household:{self.entity_id}_Model a wf:SimulationModel ;
    rdfs:label "{self.entity_name}" ;
    wf:representsEntity housecase1:{self.entity_id} ;
    wf:hasIdentifier "{self.entity_id}" ;
    wf:hasInput {inputs_ttl} ;
    wf:hasOutput {outputs_ttl} ;
    wf:implementedBy "qsdsan" ;
    wf:apiEndpoint <{self.api_endpoint}> ;
    wf:port {self.port} .
"""

    def generate_agent_ttl(self) -> str:
        base_ttl = self.generate_ttl_description()

        software_ttl = f"""
# Software System
household:{self.entity_id}_Software a wf:SoftwareSystem ;
    rdfs:label "{self.entity_name} Software" ;
    wf:apiEndpoint <{self.api_endpoint}> ;
    wf:apiVersion "1.0" .
"""

        caps_refs = ", ".join(f"cap:{c}" for c in self.capabilities) if self.capabilities else ""
        agent_ttl = f"""
# Computational Agent
household:{self.entity_id}_Agent a wf:SimulationAgent ;
    rdfs:label "{self.entity_name} Agent" ;
    wf:implements household:{self.entity_id}_Model ;
    wf:simulates housecase1:{self.entity_id} ;
    wf:runsOn household:{self.entity_id}_Software ;"""

        if caps_refs:
            agent_ttl += f"\n    wf:hasCapability {caps_refs} ;"

        agent_ttl += f"""
    wf:offersOperation household:{self.entity_id}_SimulateOp ;
    wf:agentVersion "1.0.0" .
"""

        operation_ttl = f"""
# Operation
household:{self.entity_id}_SimulateOp a wf:Operation ;
    rdfs:label "Simulate {self.entity_name}" ;
    wf:hasHTTPGrounding [
        a wf:HTTPGrounding ;
        wf:httpMethod "POST" ;
        wf:operationPath "/simulate" ;
        wf:requestFormat "application/json" ;
        wf:responseFormat "application/json" ;
        wf:requiresAuthentication "false"^^xsd:boolean
    ] ;
    wf:estimatedExecutionTime "1.0"^^xsd:float ;
    wf:computationalComplexity "O(1)" .
"""
        return base_ttl + software_ttl + agent_ttl + operation_ttl

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "model": self.entity_id,
            "type": self.entity_type,
            "endpoint": self.api_endpoint,
            "last_run": self._last_run.isoformat() if self._last_run else None,
        }

    def _update_state(self, outputs: Dict[str, Any], status: Optional[str] = None) -> None:
        self._state = {
            "outputs": outputs,
            "timestamp": datetime.utcnow().isoformat(),
            "model_id": self.entity_id,
            "status": status or ModelStatus.READY,
        }
        self._last_run = datetime.utcnow()
        self._status = status or ModelStatus.READY

    def _get_parameter_value(self, inputs: Dict[str, Any], param_name: str, default: Any = None) -> Any:
        if param_name in inputs:
            return inputs[param_name]
        for var in [f"input_{param_name}", param_name.lower().replace(" ", "_")]:
            if var in inputs:
                return inputs[var]
        return default
