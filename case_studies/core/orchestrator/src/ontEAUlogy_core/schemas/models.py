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


class CompositionAgentInfo(BaseModel):
    """Information about an agent in a composition."""

    id: str
    name: str
    operation_uri: str
    endpoint: str
    required_inputs: List[str] = Field(default_factory=list)
    produced_outputs: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    model_id: Optional[str] = None


class CompositionLayerInfo(BaseModel):
    """Information about a composition layer."""

    layer_index: int
    agents: List[CompositionAgentInfo]
    required_inputs: List[str] = Field(default_factory=list)
    produced_outputs: List[str] = Field(default_factory=list)


class CompositionResultInfo(BaseModel):
    """Result of agent composition discovery."""

    found: bool
    layers: List[CompositionLayerInfo]
    initial_data: List[str] = Field(default_factory=list)
    target_outputs: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)
    discovery_iterations: int = 0
    execution_time_ms: float = 0.0
    inferred_mappings: Dict[str, str] = Field(default_factory=dict)
    plan_description: Optional[str] = None


class ValidationResultInfo(BaseModel):
    """Result of precondition validation."""

    valid: bool
    violations: List[str] = Field(default_factory=list)


class InvocationResultInfo(BaseModel):
    """Result of operation invocation."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class CompositionChainInfo(BaseModel):
    """A chain of composable operations."""

    source_agent: str
    target_agent: str
    shared_output: str
    flow_path: Optional[str] = None


class CapabilityDiscoveryRequest(BaseModel):
    """Request to discover agents by capability."""

    required_capabilities: List[str]
    available_data: List[str] = Field(default_factory=list)


class CapabilityDiscoveryResponse(BaseModel):
    """Response for capability-based agent discovery."""

    agents: List[CompositionAgentInfo]
    count: int


class PhysicalFlowRequest(BaseModel):
    """Request to discover composition via physical flows."""

    source_entity: str


class PhysicalFlowResponse(BaseModel):
    """Response for physical flow-based composition."""

    chains: List[CompositionChainInfo]
    count: int


class OperationValidationRequest(BaseModel):
    """Request to validate operation execution."""

    operation: str
    input_data: Dict[str, Any] = Field(default_factory=dict)


class OperationInvocationRequest(BaseModel):
    """Request to invoke an operation."""

    operation: str
    input_data: Dict[str, Any] = Field(default_factory=dict)


# === Agent Composition (core) ===


class ScenarioSpec(BaseModel):
    """Specification for a single parallel scenario."""

    initial_parameters: Dict[str, Any] = Field(default_factory=dict)
    target_outputs: List[str]
    label: str = ""


class AgentCompositionRequest(BaseModel):
    """Request agent composition discovery and optional execution."""

    initial_parameters: Dict[str, Any] = Field(default_factory=dict)
    target_outputs: List[str]
    max_layers: int = 10
    timeout_seconds: float = 30.0
    parallel_scenarios: Optional[List[ScenarioSpec]] = None


class CompositionLayerResponse(BaseModel):
    """Serializable layer representation."""

    layer_index: int
    agent_ids: List[str] = Field(default_factory=list)
    agent_names: List[str] = Field(default_factory=list)
    parallelizable: bool = False
    inputs_needed: Dict[str, str] = Field(default_factory=dict)
    outputs_produced: List[str] = Field(default_factory=list)


class AgentCompositionResponse(BaseModel):
    """Response with discovered composition."""

    composition_found: bool
    execution_plan: str
    layers: List[CompositionLayerResponse] = Field(default_factory=list)
    total_agents: int = 0
    estimated_execution_time_seconds: float = 0.0
    trace_id: Optional[str] = None


# === Trace Response Models ===


class EventParameterResponse(BaseModel):
    """Serialized EventParameter for API responses."""

    name: str
    value: Any = None
    unit: Optional[str] = None
    kg_node_uri: Optional[str] = None
    kg_node_label: Optional[str] = None


class ExecutionEventResponse(BaseModel):
    """Serialized ExecutionEvent for API responses."""

    event_id: str
    agent_uri: str
    agent_name: str
    agent_type: str
    operation_uri: str
    operation_name: str
    layer_index: Optional[int] = None
    scenario_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    inputs: List[EventParameterResponse] = Field(default_factory=list)
    outputs: List[EventParameterResponse] = Field(default_factory=list)
    status: str = "running"
    error: Optional[str] = None


class ExecutionScenarioResponse(BaseModel):
    """Serialized ExecutionScenario for API responses."""

    scenario_id: str
    label: str
    parent_scenario_id: Optional[str] = None
    branch_event_id: Optional[str] = None
    events: List[ExecutionEventResponse] = Field(default_factory=list)
    status: str = "running"


class QueryTraceResponse(BaseModel):
    """Full serialized QueryTrace for API responses."""

    trace_id: str
    query: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: str = "running"
    events: List[ExecutionEventResponse] = Field(default_factory=list)
    scenarios: List[ExecutionScenarioResponse] = Field(default_factory=list)
    total_layers: int = 0


class QueryTraceSummary(BaseModel):
    """Summary row for trace list endpoint."""

    trace_id: str
    query: str
    status: str
    start_time: Optional[str] = None
    total_layers: int = 0
