export interface WaterEntity {
    id: string; // entity slug (e.g., DWP1)
    uri?: string;
    label: string;
    type: string;
    zone?: string;
    coordinates: [number, number];
    status?: 'idle' | 'running' | 'error';
    description?: string;
    capacity?: string;
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

export interface Triplet {
    subject: string;
    predicate: string;
    object: string;
    isUri?: boolean;
}

export interface Relationship {
    id?: string;
    source: string;
    target: string;
    predicate: string;
    label: string;
}

export interface SimulationResult {
    jobId: string;
    outputs: Record<string, number>; // e.g., { bod: 15.2, flow: 1750 }
    timeSeries?: { time: string; value: number }[];
}

export interface SimulationStartResponse {
    job_id: string;
    model_id: string;
    status: string;
    message: string;
}

export interface ModelCapability {
    id: string;
    label: string;
    unit?: string;
    isDecisionVariable: boolean;
    defaultValue?: number;
    min?: number;
    max?: number;
}

export interface SparqlQueryRequest {
    query: string;
    format?: string;
}

export interface SparqlQueryResponse {
    head?: { vars: string[] };
    results: unknown;
    format: string;
    query_time_ms: number;
}

export interface NaturalLanguageQueryRequest {
    question: string;
    target_format?: string;
}

export interface NaturalLanguageQueryResponse {
    original_question: string;
    generated_sparql?: string;
    results?: Array<Record<string, unknown>>;
    execution_plan?: string;
    simulation_required: boolean;
    suggested_models: string[];
}
