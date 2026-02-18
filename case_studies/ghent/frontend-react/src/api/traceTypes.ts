export interface TraceSummary {
    trace_id: string;
    root_agent: string;
    started_at: string;
    completed_at: string | null;
    status: string;
}

export interface TraceNode {
    node_id: string;
    trace_id: string;
    parent_id: string | null;
    agent_type: string;
    agent_id: string;
    timestamp: string;
    inputs: Record<string, unknown>;
    outputs: Record<string, unknown>;
    processing: string;
    children: string[];
}

export interface TraceDetail {
    trace_id: string;
    root_agent: string;
    started_at: string;
    completed_at: string | null;
    status: string;
    nodes: TraceNode[];
}

export interface TraceGraph {
    trace_id: string;
    root_agent: string;
    status: string;
    nodes: {
        id: string;
        agent_type: string;
        agent_id: string;
        timestamp: string;
        processing: string;
    }[];
    links: {
        source: string;
        target: string;
    }[];
}
