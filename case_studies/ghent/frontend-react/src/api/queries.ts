import { useQuery, useMutation } from '@tanstack/react-query';
import client from './client';
import { MOCK_ENTITIES, MOCK_RELATIONSHIPS, MOCK_TRIPLETS, MOCK_SENSOR_DATA } from './mockData';
import { processSparqlResults } from './sparqlNormalizer';
import type {
    WaterEntity,
    SimulationStartResponse,
    Relationship,
    Triplet,
    SparqlQueryRequest,
    SparqlQueryResponse,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
    EntityType
} from './types';

const USE_MOCK = false;

type EntityApiResponse = {
    id: string;
    uri?: string;
    label: string;
    type: string;
    lat: number;
    lon: number;
    zone?: string;
    capacity?: string;
    description?: string;
};
type SensorHistoryResponse = { sensor_data: Record<string, unknown> };

export const useEntities = () => {
    return useQuery<WaterEntity[]>({
        queryKey: ['entities'],
        queryFn: async () => {
            if (USE_MOCK) {
                await new Promise((r) => setTimeout(r, 800));
                return MOCK_ENTITIES;
            }
            const { data } = await client.get('/ontology/entities');

            // Validate the response with passthrough to handle unknown fields
            const validatedData = data;
            if (!validatedData) {
                console.warn('Entities response validation failed, using empty array');
                return [];
            }

            // Deduplicate entities by ID, preferring entities with valid coordinates
            const entityMap = new Map<string, any>();

            validatedData.entities.forEach((e: any) => {
                const validatedEntity = e;
                if (!validatedEntity) {
                    console.warn('Entity validation failed:', e);
                    return;
                }

                const id = validatedEntity.id;
                const existing = entityMap.get(id);

                // If no existing entity, or this one has better coordinates, use this one
                if (!existing ||
                    (validatedEntity.lat > 0 && validatedEntity.lon > 0 &&
                     (existing.lat === 0 || existing.lon === 0))) {
                    entityMap.set(id, validatedEntity);
                }
            });

            const deduplicatedEntities = Array.from(entityMap.values()).map((validatedEntity) => {
                return {
                    id: validatedEntity.id,
                    uri: validatedEntity.uri,
                    label: validatedEntity.label,
                    type: validatedEntity.type,
                    coordinates: [validatedEntity.lat, validatedEntity.lon],
                    zone: validatedEntity.zone,
                    capacity: validatedEntity.capacity,
                    description: validatedEntity.description
                };
            }).filter(Boolean) as WaterEntity[];

            return deduplicatedEntities;
        },
    });
};

export const useEntityState = (id: string | null) => {
    return useQuery({
        queryKey: ['entity-state', id],
        queryFn: async () => {
            if (!id) return null;
            if (USE_MOCK) {
                await new Promise((r) => setTimeout(r, 400));
                return MOCK_ENTITIES.find((e) => e.id === id) || null;
            }
            const { data } = await client.get<EntityApiResponse>(`/ontology/entities/${encodeURIComponent(id)}`);
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
            if (USE_MOCK) {
                await new Promise((r) => setTimeout(r, 300));
                return MOCK_TRIPLETS[id] || [];
            }
            const { data } = await client.get(`/ontology/entities/${encodeURIComponent(id)}/triplets`);

            // Validate the triplets response
            const validatedData = data;
            if (!validatedData) {
                console.warn(`Triplets response validation failed for entity ${id}`);
                return [];
            }

            return validatedData.triples;
        },
        enabled: !!id,
    });
};

export const useSensorData = (id: string | null) => {
    return useQuery<unknown>({
        queryKey: ['sensor-data', id],
        queryFn: async () => {
            if (!id) return null;
            if (USE_MOCK) {
                await new Promise((r) => setTimeout(r, 500));
                return MOCK_SENSOR_DATA[id] || [];
            }
            const { data } = await client.get<SensorHistoryResponse>(`/sensors/historical`);
            return data.sensor_data[id] || null;
        },
        enabled: !!id,
    });
};

export const useRunSimulation = () => {
    return useMutation<SimulationStartResponse, Error, { entityId: string | null; flow: number }>({
        mutationFn: async (payload) => {
            if (USE_MOCK) {
                await new Promise((r) => setTimeout(r, 2000));
                return {
                    job_id: 'job-123',
                    model_id: payload.entityId || 'unknown',
                    status: 'completed',
                    message: 'Mock simulation completed',
                };
            }
            const { data } = await client.post(`/simulation/models/${payload.entityId}/run`, {
                entity_ids: payload.entityId ? [payload.entityId] : [],
                parameters: { flow: payload.flow },
            });

            // Validate simulation response
            const validatedData = data;
            if (!validatedData) {
                throw new Error('Invalid simulation response format');
            }

            return validatedData;
        },
    });
};

export const useRelationships = () => {
    return useQuery<Relationship[]>({
        queryKey: ['relationships'],
        queryFn: async () => {
            if (USE_MOCK) {
                return MOCK_RELATIONSHIPS;
            }

            const query = `
                PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX ghent: <https://w3id.org/waterframe/case/ghent/>

                SELECT DISTINCT ?sourceId ?targetId ?label
                WHERE {
                    {
                        # Pattern 1: Entity has output port that flows to input port of another entity
                        ?sourceEntity wf:hasOutputPort ?out .
                        ?out wf:flowsTo ?in .
                        ?targetEntity wf:hasInputPort ?in .
                        OPTIONAL { ?out rdfs:label ?label . }
                    } UNION {
                        # Pattern 2: Entity has output port that flows to another entity directly
                        ?sourceEntity wf:hasOutputPort ?out .
                        ?out wf:flowsTo ?targetEntity .
                        OPTIONAL { ?out rdfs:label ?label . }
                    } UNION {
                        # Pattern 3: Entity has output port with source flowing to input port of another entity
                        ?sourceEntity wf:hasOutputPort ?out .
                        ?out wf:hasSource ?sourcePort .
                        ?sourcePort wf:flowsTo ?in .
                        ?targetEntity wf:hasInputPort ?in .
                        OPTIONAL { ?out rdfs:label ?label . }
                    }

                    # Filter to only include Ghent case study entities
                    FILTER(STRSTARTS(STR(?sourceEntity), "https://w3id.org/waterframe/case/ghent/"))
                    FILTER(STRSTARTS(STR(?targetEntity), "https://w3id.org/waterframe/case/ghent/"))

                    BIND(REPLACE(STR(?sourceEntity), "^.*[/|#]", "") AS ?sourceId)
                    BIND(REPLACE(STR(?targetEntity), "^.*[/|#]", "") AS ?targetId)
                }
            `;

            const { data } = await client.post('/query/sparql', { query });

            // Process and normalize SPARQL results
            const normalizedData = processSparqlResults(data, 'Relationships query');
            const bindings = normalizedData.results.bindings;

            return bindings
                .map((b) => {
                    // Extract values from normalized bindings
                    const sourceId = typeof b.sourceId === 'object' && b.sourceId ? (b.sourceId as any).value : b.sourceId;
                    const targetId = typeof b.targetId === 'object' && b.targetId ? (b.targetId as any).value : b.targetId;
                    const label = typeof b.label === 'object' && b.label ? (b.label as any).value : b.label;

                    return {
                        source: sourceId,
                        target: targetId,
                        predicate: 'wf:flowsTo',
                        label: label || 'Flow'
                    };
                })
                .filter((r): r is Relationship => Boolean(r.source && r.target));
        },
    });
};

export const useSparqlQuery = () => {
    return useMutation<SparqlQueryResponse, Error, SparqlQueryRequest>({
        mutationFn: async (payload) => {
            const { data } = await client.post('/query/sparql', payload);

            // Process and normalize SPARQL results
            const normalizedData = processSparqlResults(data, 'SPARQL query');

            return {
                ...normalizedData,
                // Preserve any additional fields from original response
                query: payload.query,
                format: data?.format || 'json',
                query_time_ms: data?.query_time_ms || 0,
            };
        },
    });
};

export const useEntityTypes = () => {
    return useQuery<EntityType[]>({
        queryKey: ['entity-types'],
        queryFn: async () => {
            if (USE_MOCK) {
                await new Promise((r) => setTimeout(r, 300));
                return [
                    {
                        uri: "https://ugentbiomath.github.io/waterframe#DrinkingWaterPlant",
                        localName: "DrinkingWaterPlant",
                        displayLabel: "DWP",
                        displayColor: "#15aabf",
                        displayIcon: "droplet-filled",
                        description: "Drinking Water Plant",
                        label: "Drinking Water Plant"
                    },
                    {
                        uri: "https://ugentbiomath.github.io/waterframe#WastewaterTreatmentPlant",
                        localName: "WastewaterTreatmentPlant",
                        displayLabel: "WWTP",
                        displayColor: "#f59e0b",
                        displayIcon: "building-factory",
                        description: "Wastewater Treatment Plant",
                        label: "Wastewater Treatment Plant"
                    },
                    {
                        uri: "https://ugentbiomath.github.io/waterframe#River",
                        localName: "River",
                        displayLabel: "River",
                        displayColor: "#06b6d4",
                        displayIcon: "wave",
                        description: "River or natural water body",
                        label: "River"
                    }
                ];
            }

            const { data } = await client.get('/ontology/types');
            return data.types || [];
        },
    });
};

export const useNaturalLanguageQuery = () => {
    return useMutation<NaturalLanguageQueryResponse, Error, NaturalLanguageQueryRequest>({
        mutationFn: async (payload) => {
            const { data } = await client.post('/query/natural', payload);

            // Validate natural language query response
            const validatedData = data;
            if (!validatedData) {
                console.warn('Natural language query response validation failed');
                return {
                    original_question: payload.question,
                    generated_sparql: '',
                    results: [],
                    execution_plan: 'Validation failed',
                    simulation_required: false,
                    suggested_models: [],
                };
            }

            return {
                original_question: validatedData.original_question,
                generated_sparql: validatedData.generated_sparql || '',
                results: validatedData.results || [],
                execution_plan: validatedData.execution_plan,
                simulation_required: validatedData.simulation_required || false,
                suggested_models: validatedData.suggested_models || [],
            };
        },
    });
};
