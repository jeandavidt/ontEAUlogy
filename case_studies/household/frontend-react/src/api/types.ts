export interface WaterEntity {
    id: string;
    uri: string;
    label: string;
    type: string;
    coordinates: [number, number];
    zone?: string;
    capacity?: string;
    description?: string;
}

export interface Relationship {
    source: string;
    target: string;
    predicate: string;
    label?: string;
}

export interface Triplet {
    subject: string;
    predicate: string;
    object: string;
}

export interface SimulationStartResponse {
    job_id: string;
    model_id: string;
    status: string;
    message: string;
}

export interface SparqlQueryRequest {
    query: string;
}

export interface SparqlQueryResponse {
    head?: {
        vars?: string[];
    };
    results?: {
        bindings?: Array<Record<string, { value?: string; type?: string }>>;
    };
    query?: string;
    format?: string;
    query_time_ms?: number;
}

export interface NaturalLanguageQueryRequest {
    question: string;
}

export interface NaturalLanguageQueryResponse {
    original_question: string;
    generated_sparql: string;
    results: Array<Record<string, unknown>>;
    execution_plan: string;
    simulation_required: boolean;
    suggested_models: string[];
}

export interface EntityType {
    uri: string;
    localName: string;
    displayLabel: string;
    displayColor: string;
    displayIcon: string;
    description: string;
    label: string;
}

export interface JobStatus {
    job_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    results?: Record<string, unknown>;
    error?: string;
}

// === Trace / Execution Visualization Types ===

export interface EventParameter {
    name: string;
    value: unknown;
    unit?: string;
    kgNodeUri?: string;
    kgNodeLabel?: string;
}

export interface ExecutionEvent {
    eventId: string;
    agentUri: string;
    agentName: string;
    agentType: 'llm' | 'model' | 'orchestrator' | 'user' | 'sparql';
    operationUri: string;
    operationName: string;
    layerIndex?: number;
    scenarioId?: string;
    parentEventId?: string;
    startTime: string;       // ISO 8601
    endTime?: string;
    inputs: EventParameter[];
    outputs: EventParameter[];
    status: 'running' | 'completed' | 'failed';
    error?: string;
}

export interface ExecutionScenario {
    scenarioId: string;
    label: string;
    parentScenarioId?: string;
    branchEventId?: string;
    events: ExecutionEvent[];
    status: 'running' | 'completed' | 'failed';
}

export interface QueryTrace {
    traceId: string;
    query: string;
    startTime: string;
    endTime?: string;
    status: 'running' | 'completed' | 'failed';
    events: ExecutionEvent[];
    scenarios: ExecutionScenario[];
    totalLayers: number;
}

export interface QueryTraceSummary {
    traceId: string;
    query: string;
    status: 'running' | 'completed' | 'failed';
    startTime?: string;
    totalLayers: number;
}

// === Agent Composition Types ===

export interface AgentCompositionRequest {
    initial_parameters: Record<string, unknown>;
    target_outputs: string[];
    max_layers?: number;
    timeout_seconds?: number;
}

export interface AgentCompositionResponse {
    trace_id?: string;
    status: string;
    total_layers: number;
    layers: unknown[];
    execution_results: Record<string, unknown>;
}

// WebSocket message types from the trace router
export type TraceWsMessage =
    | { type: 'event_started';    trace_id: string; event: Record<string, unknown> }
    | { type: 'event_completed';  trace_id: string; event: Record<string, unknown> }
    | { type: 'scenario_created'; trace_id: string; scenario: Record<string, unknown> }
    | { type: 'trace_completed';  trace_id: string };
