"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# === Discovery Models ===


class SystemInfo(BaseModel):
    """System description for API discovery."""

    name: str
    version: str
    description: str
    endpoints: Dict[str, str]


class ModelInfo(BaseModel):
    """Information about a registered model."""

    id: str
    name: str
    description: Optional[str] = None
    endpoint: str
    capabilities: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    registered_at: datetime = Field(default_factory=datetime.utcnow)


class ModelListResponse(BaseModel):
    """Response for listing registered models."""

    models: List[ModelInfo]
    count: int


class ModelDescription(BaseModel):
    """Model self-description response."""

    model: ModelInfo
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    outputs: List[Dict[str, Any]] = Field(default_factory=list)


# === Query Models ===

from typing import Any, Dict, List, Literal, Optional, Union


class SparqlQueryRequest(BaseModel):
    """SPARQL query request."""

    query: str
    format: Literal["json", "csv", "json-ld"] = "json"  # json, csv, json-ld


class SimulationRequest(BaseModel):
    """Request to run a simulation."""

    entity_ids: List[str] = Field(default_factory=list)
    scenario: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    wait_for_result: bool = True
    timeout_seconds: int = 300


class SparqlQueryResponse(BaseModel):
    """SPARQL query response."""

    head: Optional[Dict[str, Any]] = None
    results: Union[Dict[str, Any], List[Dict[str, Any]], str]
    format: str
    query_time_ms: float


class NaturalLanguageQueryRequest(BaseModel):
    """Natural language query request."""

    question: str
    target_format: str = "sparql"  # sparql, results


class NaturalLanguageQueryResponse(BaseModel):
    """Natural language query response."""

    original_question: str
    generated_sparql: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    execution_plan: Optional[str] = None
    simulation_required: bool = False
    suggested_models: List[str] = Field(default_factory=list)


# === Simulation Models ===


class SimulationJob(BaseModel):
    """Simulation job information."""

    job_id: str
    model_id: str
    status: str  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SimulationJobResponse(BaseModel):
    """Simulation job response."""

    job: SimulationJob


class SimulationResponse(BaseModel):
    """Response after running a simulation."""

    job_id: str
    model_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    message: str


class JobResponse(BaseModel):
    """Job response for async operations."""

    job_id: str
    model_id: str
    status: str
    message: str


class ModelStateResponse(BaseModel):
    """Current state of a model."""

    model_id: str
    state: Dict[str, Any]
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# === Ontology Models ===


class OntologyInfo(BaseModel):
    """Information about the ontology."""

    graph_size: int
    namespaces: List[str]
    entities_count: Dict[str, int]


class EntityTriplesResponse(BaseModel):
    """Triples about an entity."""

    uri: str
    triples: List[Dict[str, Any]]


class ValidationRequest(BaseModel):
    """SHACL validation request."""

    data_graph: str  # URI or inline Turtle
    shape_graph: Optional[str] = None


class ValidationResponse(BaseModel):
    """SHACL validation response."""

    conforms: bool
    results: List[Dict[str, Any]] = Field(default_factory=list)


# === Registration Models ===


class ModelRegistrationRequest(BaseModel):
    """Request to register a model."""

    id: str
    name: str
    description: Optional[str] = None
    endpoint: str
    capabilities: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    self_description_url: Optional[str] = None


class RegistrationResponse(BaseModel):
    """Response after model registration."""

    success: bool
    model_id: str
    message: str


# === Health Models ===


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    components: Dict[str, str]


# === Error Models ===


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None


# === Agent Composition Models ===


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
