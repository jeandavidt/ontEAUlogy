import { useQuery, useMutation } from '@tanstack/react-query';
import { useEffect, useRef } from 'react';
import client from './client';
import type {
    WaterEntity,
    SimulationStartResponse,
    Relationship,
    Triplet,
    SparqlQueryRequest,
    SparqlQueryResponse,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
    EntityType,
    JobStatus,
    EventParameter,
    ExecutionEvent,
    ExecutionScenario,
    QueryTrace,
    QueryTraceSummary,
    TraceWsMessage,
    AgentCompositionRequest,
    AgentCompositionResponse,
} from './types';

// Entity API Hooks
export const useEntities = () => {
    return useQuery<WaterEntity[]>({
        queryKey: ['entities'],
        queryFn: async () => {
            // Query entities that participate in flowsTo relationships (sources or targets)
            // These are the actual physical infrastructure components
            const query = `
                PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT DISTINCT ?id ?label ?type WHERE {
                    {
                        ?id wf:flowsTo ?target .
                    } UNION {
                        ?source wf:flowsTo ?id .
                    }
                    OPTIONAL { ?id a ?type }
                    OPTIONAL { ?id rdfs:label ?label }
                    FILTER(STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Rainwater_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#RainwaterTank_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Bath_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#BathroomSink_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#WashingMachine_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Dishwasher_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#KitchenSink_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Cleaning_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Toilet_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#MBR_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#RO_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#GreywaterTank_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#BlackwaterTank_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#PotableTank_Output"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Gardening_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Bath_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#BathroomSink_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#WashingMachine_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Dishwasher_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#KitchenSink_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Toilet_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#MBR_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#RO_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#GreywaterTank_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#BlackwaterTank_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#PotableTank_Input"))
                    FILTER(!STRSTARTS(STR(?id), "https://ugentbiomath.github.io/ontology/index.ttl#Infiltration_Input"))
                }
                LIMIT 50
            `;

            try {
                const { data } = await client.post('/query/sparql', { query });
                const bindings = data.results?.bindings || [];

                return bindings.map((b: any, index: number) => {
                    const uri = b.id?.value || '';
                    const typeUri = b.type?.value || '';
                    // Extract type name from URI
                    const typeName = typeUri.split('#').pop() || 'Entity';
                    
                    return {
                        id: uri.split('#').pop() || `entity-${index}`,
                        uri: uri,
                        label: b.label?.value || uri.split('#').pop() || 'Unknown',
                        type: typeName,
                        coordinates: [0, 0] as [number, number],
                        zone: 'household',
                        capacity: undefined,
                        description: undefined
                    };
                });
            } catch {
                return [];
            }
        },
    });
};

export const useEntityState = (id: string | null) => {
    return useQuery<WaterEntity | null>({
        queryKey: ['entity-state', id],
        queryFn: async () => {
            if (!id) return null;
            const { data } = await client.get(`/ontology/entities/${encodeURIComponent(id)}`);
            return {
                id: data.id,
                uri: data.uri,
                label: data.label,
                type: data.type,
                coordinates: [data.lat, data.lon],
                zone: data.zone,
                capacity: data.capacity,
                description: data.description
            };
        },
        enabled: !!id,
    });
};

export const useEntityTriplets = (id: string | null) => {
    return useQuery<Triplet[]>({
        queryKey: ['entity-triplets', id],
        queryFn: async () => {
            if (!id) return [];
            const { data } = await client.get(`/ontology/entities/${encodeURIComponent(id)}/triplets`);
            return data.triples || [];
        },
        enabled: !!id,
    });
};

// Model/Simulation Hooks
export const useRunSimulation = () => {
    return useMutation<SimulationStartResponse, Error, { entityId: string; parameters?: Record<string, unknown> }>({
        mutationFn: async (payload) => {
            const { data } = await client.post(`/simulation/models/${payload.entityId}/run`, {
                entity_ids: [payload.entityId],
                parameters: payload.parameters || {},
            });
            return data;
        },
    });
};

export const useJobStatus = (jobId: string | null) => {
    return useQuery<JobStatus>({
        queryKey: ['job-status', jobId],
        queryFn: async () => {
            if (!jobId) return null as unknown as JobStatus;
            const { data } = await client.get(`/simulation/jobs/${jobId}`);
            return data;
        },
        enabled: !!jobId,
        refetchInterval: (query) => {
            const data = query.state.data;
            if (data?.status === 'running') {
                return 1000;
            }
            return false;
        },
    });
};

// SPARQL Hooks
export const useSparqlQuery = () => {
    return useMutation<SparqlQueryResponse, Error, SparqlQueryRequest>({
        mutationFn: async (payload) => {
            const { data } = await client.post('/query/sparql', payload);
            return data;
        },
    });
};

export const useNaturalLanguageQuery = () => {
    return useMutation<NaturalLanguageQueryResponse, Error, NaturalLanguageQueryRequest>({
        mutationFn: async (payload) => {
            const { data } = await client.post('/query/natural', payload);
            return {
                original_question: data.original_question,
                generated_sparql: data.generated_sparql || '',
                results: data.results || [],
                execution_plan: data.execution_plan,
                simulation_required: data.simulation_required || false,
                suggested_models: data.suggested_models || [],
            };
        },
    });
};

// Ontology Hooks
export const useEntityTypes = () => {
    return useQuery<EntityType[]>({
        queryKey: ['entity-types'],
        queryFn: async () => {
            const { data } = await client.get('/ontology/types');
            return data.types || [];
        },
    });
};

export const useRelationships = () => {
    return useQuery<Relationship[]>({
        queryKey: ['relationships'],
        queryFn: async () => {
            // Query for direct wf:flowsTo relationships between main entities (not ports)
            // Filter out port-level connections (Input/Output ports)
            const query = `
                PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT DISTINCT ?sourceEntity ?sourceLabel ?targetEntity ?targetLabel
                WHERE {
                    ?sourceEntity wf:flowsTo ?targetEntity .
                    
                    OPTIONAL { ?sourceEntity rdfs:label ?sourceLabel }
                    OPTIONAL { ?targetEntity rdfs:label ?targetLabel }
                    
                    FILTER(STRSTARTS(STR(?sourceEntity), "https://ugentbiomath.github.io/ontology/index.ttl#"))
                    FILTER(STRSTARTS(STR(?targetEntity), "https://ugentbiomath.github.io/ontology/index.ttl#"))
                    
                    FILTER(!CONTAINS(STR(?sourceEntity), "_Output"))
                    FILTER(!CONTAINS(STR(?sourceEntity), "_Input"))
                    FILTER(!CONTAINS(STR(?targetEntity), "_Output"))
                    FILTER(!CONTAINS(STR(?targetEntity), "_Input"))
                }
            `;

            try {
                const { data } = await client.post('/query/sparql', { query });
                const bindings = data.results?.bindings || [];

                return bindings
                    .map((b: any) => ({
                        source: b.sourceEntity?.value?.split('#').pop() || b.sourceEntity?.value,
                        target: b.targetEntity?.value?.split('#').pop() || b.targetEntity?.value,
                        predicate: 'wf:flowsTo',
                        label: 'flows to'
                    }))
                    .filter((r: Relationship) => Boolean(r.source && r.target));
            } catch {
                return [];
            }
        },
    });
};

// === Trace / Execution Visualization Hooks ===

function toEventParameter(p: Record<string, unknown>): EventParameter {
    return {
        name: String(p.name ?? ''),
        value: p.value,
        unit: p.unit != null ? String(p.unit) : undefined,
        kgNodeUri: p.kg_node_uri != null ? String(p.kg_node_uri) : undefined,
        kgNodeLabel: p.kg_node_label != null ? String(p.kg_node_label) : undefined,
    };
}

function toExecutionEvent(e: Record<string, unknown>): ExecutionEvent {
    return {
        eventId: String(e.event_id ?? ''),
        agentUri: String(e.agent_uri ?? ''),
        agentName: String(e.agent_name ?? ''),
        agentType: (e.agent_type as ExecutionEvent['agentType']) ?? 'llm',
        operationUri: String(e.operation_uri ?? ''),
        operationName: String(e.operation_name ?? ''),
        layerIndex: e.layer_index != null ? Number(e.layer_index) : undefined,
        scenarioId: e.scenario_id != null ? String(e.scenario_id) : undefined,
        parentEventId: e.parent_event_id != null ? String(e.parent_event_id) : undefined,
        startTime: String(e.start_time ?? ''),
        endTime: e.end_time != null ? String(e.end_time) : undefined,
        inputs: ((e.inputs as unknown[]) ?? []).map(p => toEventParameter(p as Record<string, unknown>)),
        outputs: ((e.outputs as unknown[]) ?? []).map(p => toEventParameter(p as Record<string, unknown>)),
        status: (e.status as ExecutionEvent['status']) ?? 'running',
        error: e.error != null ? String(e.error) : undefined,
    };
}

function toExecutionScenario(s: Record<string, unknown>): ExecutionScenario {
    return {
        scenarioId: String(s.scenario_id ?? ''),
        label: String(s.label ?? ''),
        parentScenarioId: s.parent_scenario_id != null ? String(s.parent_scenario_id) : undefined,
        branchEventId: s.branch_event_id != null ? String(s.branch_event_id) : undefined,
        events: ((s.events as unknown[]) ?? []).map(e => toExecutionEvent(e as Record<string, unknown>)),
        status: (s.status as ExecutionScenario['status']) ?? 'running',
    };
}

function toQueryTrace(data: Record<string, unknown>): QueryTrace {
    return {
        traceId: String(data.trace_id ?? ''),
        query: String(data.query ?? ''),
        startTime: String(data.start_time ?? ''),
        endTime: data.end_time != null ? String(data.end_time) : undefined,
        status: (data.status as QueryTrace['status']) ?? 'running',
        events: ((data.events as unknown[]) ?? []).map(e => toExecutionEvent(e as Record<string, unknown>)),
        scenarios: ((data.scenarios as unknown[]) ?? []).map(s => toExecutionScenario(s as Record<string, unknown>)),
        totalLayers: Number(data.total_layers ?? 0),
    };
}

export const useQueryTraceSummaries = () => {
    return useQuery<QueryTraceSummary[]>({
        queryKey: ['traces'],
        queryFn: async () => {
            const { data } = await client.get('/traces');
            return (data as unknown[]).map((t: unknown) => {
                const r = t as Record<string, unknown>;
                return {
                    traceId: String(r.trace_id ?? ''),
                    query: String(r.query ?? ''),
                    status: (r.status as QueryTraceSummary['status']) ?? 'running',
                    startTime: r.start_time != null ? String(r.start_time) : undefined,
                    totalLayers: Number(r.total_layers ?? 0),
                } satisfies QueryTraceSummary;
            });
        },
    });
};

export const useQueryTrace = (traceId?: string) => {
    return useQuery<QueryTrace | null>({
        queryKey: ['trace', traceId],
        queryFn: async () => {
            if (!traceId) return null;
            const { data } = await client.get(`/traces/${traceId}`);
            return toQueryTrace(data as Record<string, unknown>);
        },
        enabled: !!traceId,
        refetchInterval: (query) => {
            const d = query.state.data;
            return d?.status === 'running' ? 500 : false;
        },
    });
};

/** Subscribe to live trace events over WebSocket. */
export const useTraceWebSocket = (
    traceId?: string,
    onMessage?: (msg: TraceWsMessage) => void,
) => {
    const onMessageRef = useRef(onMessage);
    onMessageRef.current = onMessage;

    useEffect(() => {
        if (!traceId) return;

        const wsBase = client.defaults.baseURL?.replace(/^http/, 'ws') ?? '';
        const url = `${wsBase}/traces/ws?trace_id=${encodeURIComponent(traceId)}`;
        const ws = new WebSocket(url);

        ws.onmessage = (evt) => {
            try {
                const msg = JSON.parse(evt.data) as TraceWsMessage;
                onMessageRef.current?.(msg);
            } catch {
                // ignore malformed frames
            }
        };

        return () => {
            ws.close();
        };
    }, [traceId]);
};

export const useAgentCompose = () => {
    return useMutation<AgentCompositionResponse, Error, AgentCompositionRequest>({
        mutationFn: async (payload) => {
            const { data } = await client.post('/query/compose-and-execute', payload);
            return data as AgentCompositionResponse;
        },
    });
};

// Hook to get model status for entities
export const useModelStatus = (modelId: string | null) => {
    return useQuery<{ connected: boolean; status: string }>({
        queryKey: ['model-status', modelId],
        queryFn: async () => {
            if (!modelId) return { connected: false, status: 'unknown' };
            try {
                const { data } = await client.get(`/simulation/models/${modelId}/status`);
                return { connected: true, status: data.status || 'available' };
            } catch {
                return { connected: false, status: 'not connected' };
            }
        },
        enabled: !!modelId,
        refetchInterval: 5000, // Check every 5 seconds
    });
};
