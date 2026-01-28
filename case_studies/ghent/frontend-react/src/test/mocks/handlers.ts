/**
 * MSW (Mock Service Worker) handlers for API mocking in tests
 * These handlers simulate backend API responses
 */
import { http, HttpResponse } from 'msw';

const API_BASE = '/api/v1';

export const handlers = [
  // ===== Ontology Endpoints =====

  // GET /api/v1/ontology/entities - Get all entities
  http.get(`${API_BASE}/ontology/entities`, () => {
    return HttpResponse.json({
      entities: [
        {
          uri: 'https://w3id.org/waterframe/case/ghent/DWP1',
          id: 'DWP1',
          label: 'Drinking Water Plant 1',
          type: 'DWP',
          raw_type: 'DrinkingWaterPlant',
          description: 'Main drinking water treatment facility',
          lat: 51.0543,
          lon: 3.7174,
          zone: 'Zone_A',
          capacity: '2000',
          population: '',
          observes: '',
          monitorsPort: '',
          attachedTo: ''
        },
        {
          uri: 'https://w3id.org/waterframe/case/ghent/WWTP1',
          id: 'WWTP1',
          label: 'Wastewater Treatment Plant 1',
          type: 'WWTP',
          raw_type: 'WastewaterTreatmentPlant',
          description: 'Primary wastewater treatment facility',
          lat: 51.0456,
          lon: 3.7234,
          zone: 'Zone_B',
          capacity: '5000',
          population: '',
          observes: '',
          monitorsPort: '',
          attachedTo: ''
        },
        {
          uri: 'https://w3id.org/waterframe/case/ghent/River_Lieve',
          id: 'River_Lieve',
          label: 'River Lieve',
          type: 'River',
          raw_type: 'RiverSegment',
          description: 'Main river segment',
          lat: 51.0500,
          lon: 3.7200,
          zone: '',
          capacity: '',
          population: '',
          observes: '',
          monitorsPort: '',
          attachedTo: ''
        }
      ],
      count: 3
    });
  }),

  // GET /api/v1/ontology/entities/:id/triplets - Get entity triplets
  http.get(`${API_BASE}/ontology/entities/:id/triplets`, ({ params }) => {
    const { id } = params;
    const uri = `https://w3id.org/waterframe/case/ghent/${id}`;

    return HttpResponse.json({
      uri,
      triples: [
        {
          subject: uri,
          predicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
          object: 'https://ugentbiomath.github.io/waterframe#DrinkingWaterPlant'
        },
        {
          subject: uri,
          predicate: 'http://www.w3.org/2000/01/rdf-schema#label',
          object: `${id}`
        },
        {
          subject: uri,
          predicate: 'http://www.w3.org/2003/01/geo/wgs84_pos#lat',
          object: '51.0543'
        },
        {
          subject: uri,
          predicate: 'http://www.w3.org/2003/01/geo/wgs84_pos#long',
          object: '3.7174'
        }
      ]
    });
  }),

  // GET /api/v1/ontology/prefixes - Get SPARQL prefixes
  http.get(`${API_BASE}/ontology/prefixes`, () => {
    return HttpResponse.json({
      prefixes: `PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>`,
      namespaces: {
        wf: 'https://ugentbiomath.github.io/waterframe#',
        rdfs: 'http://www.w3.org/2000/01/rdf-schema#',
        geo: 'http://www.w3.org/2003/01/geo/wgs84_pos#'
      }
    });
  }),

  // ===== Query Endpoints =====

  // POST /api/v1/query/sparql - Execute SPARQL query
  http.post(`${API_BASE}/query/sparql`, async ({ request }) => {
    const body = await request.json() as { query: string; format?: string };

    // Simulate query validation errors
    if (body.query.includes('INVALID')) {
      return HttpResponse.json(
        { detail: 'SPARQL execution failed: syntax error' },
        { status: 400 }
      );
    }

    return HttpResponse.json({
      head: {
        vars: ['entity', 'label']
      },
      results: {
        bindings: [
          {
            entity: {
              type: 'uri',
              value: 'https://w3id.org/waterframe/case/ghent/DWP1'
            },
            label: {
              type: 'literal',
              value: 'Drinking Water Plant 1'
            }
          },
          {
            entity: {
              type: 'uri',
              value: 'https://w3id.org/waterframe/case/ghent/WWTP1'
            },
            label: {
              type: 'literal',
              value: 'Wastewater Treatment Plant 1'
            }
          }
        ]
      },
      format: body.format || 'json',
      query_time_ms: 45.2
    });
  }),

  // POST /api/v1/query/natural - Execute natural language query
  http.post(`${API_BASE}/query/natural`, async ({ request }) => {
    const body = await request.json() as { question: string };

    return HttpResponse.json({
      original_question: body.question,
      generated_sparql: `PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
SELECT ?dwp WHERE { ?dwp a wf:DrinkingWaterPlant }`,
      results: [
        {
          dwp: {
            type: 'uri',
            value: 'https://w3id.org/waterframe/case/ghent/DWP1'
          }
        }
      ],
      execution_plan: 'Query executed successfully',
      simulation_required: false,
      suggested_models: []
    });
  }),

  // ===== Simulation Endpoints =====

  // POST /api/v1/simulation/run - Run simulation
  http.post(`${API_BASE}/simulation/run`, async ({ request }) => {
    const body = await request.json() as { entity_ids: string[]; scenario: any; parameters: any };

    return HttpResponse.json({
      simulation_id: 'sim-123',
      status: 'completed',
      entity_ids: body.entity_ids,
      results: {
        timeseries: [
          {
            timestamp: '2024-01-20T10:00:00Z',
            values: {
              flow: 125.5,
              pressure: 2.5,
              quality: 95.0
            }
          },
          {
            timestamp: '2024-01-20T11:00:00Z',
            values: {
              flow: 130.2,
              pressure: 2.6,
              quality: 94.8
            }
          }
        ],
        summary: {
          avg_flow: 127.85,
          max_pressure: 2.6,
          min_quality: 94.8
        }
      }
    });
  }),

  // ===== Sensor Endpoints =====

  // GET /api/v1/sensors/historical - Get historical sensor data
  http.get(`${API_BASE}/sensors/historical`, () => {
    return HttpResponse.json({
      sensor_data: {
        DWP1: [
          {
            sensor_id: 'SENSOR_DWP1_FLOW',
            timestamp: '2024-01-20T10:00:00Z',
            value: 125.5,
            unit: 'm3/h'
          },
          {
            sensor_id: 'SENSOR_DWP1_FLOW',
            timestamp: '2024-01-20T11:00:00Z',
            value: 130.2,
            unit: 'm3/h'
          }
        ],
        WWTP1: [
          {
            sensor_id: 'SENSOR_WWTP1_INFLOW',
            timestamp: '2024-01-20T10:00:00Z',
            value: 450.0,
            unit: 'm3/h'
          }
        ]
      }
    });
  }),
];

// Error handlers for testing error scenarios
export const errorHandlers = [
  // Network error
  http.get(`${API_BASE}/ontology/entities`, () => {
    return HttpResponse.error();
  }),

  // 500 Internal Server Error
  http.post(`${API_BASE}/query/sparql`, () => {
    return HttpResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }),

  // 404 Not Found
  http.get(`${API_BASE}/ontology/entities/:id/triplets`, () => {
    return HttpResponse.json(
      { detail: 'Entity not found' },
      { status: 404 }
    );
  }),
];
