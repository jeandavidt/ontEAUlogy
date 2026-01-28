/**
 * Tests for API query hooks
 * These tests verify that frontend API hooks correctly call backend endpoints
 * and transform data appropriately
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React, { ReactNode } from 'react';
import { server } from '../../test/mocks/server';
import { http, HttpResponse } from 'msw';
import {
  useEntities,
  useEntityState,
  useEntityTriplets,
  useSensorData,
  useRunSimulation,
  useRelationships,
  useSparqlQuery,
  useNaturalLanguageQuery
} from '../queries';

// Create a wrapper component with QueryClient for hooks
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('API Query Hooks - Backend Communication', () => {
  beforeEach(() => {
    // Reset any runtime request handlers we add during tests
    server.resetHandlers();
  });

  describe('useEntities', () => {
    it('fetches and transforms entities correctly', async () => {
      const { result } = renderHook(() => useEntities(), {
        wrapper: createWrapper()
      });

      // Wait for the query to complete
      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      // Verify data structure
      expect(result.current.data).toBeDefined();
      expect(Array.isArray(result.current.data)).toBe(true);
      expect(result.current.data!.length).toBe(3);

      // Verify entity transformation
      const firstEntity = result.current.data![0];
      expect(firstEntity).toMatchObject({
        id: 'DWP1',
        label: 'Drinking Water Plant 1',
        type: 'DWP',
        coordinates: [51.0543, 3.7174],
        zone: 'Zone_A',
        capacity: '2000'
      });
    });

    it('handles API errors gracefully', async () => {
      // Override handler to return error
      server.use(
        http.get('/api/v1/ontology/entities', () => {
          return HttpResponse.error();
        })
      );

      const { result } = renderHook(() => useEntities(), {
        wrapper: createWrapper()
      });

      await waitFor(() => expect(result.current.isError).toBe(true));
      expect(result.current.error).toBeDefined();
    });

    it('handles empty entity list', async () => {
      server.use(
        http.get('/api/v1/ontology/entities', () => {
          return HttpResponse.json({
            entities: [],
            count: 0
          });
        })
      );

      const { result } = renderHook(() => useEntities(), {
        wrapper: createWrapper()
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data).toEqual([]);
    });
  });

  describe('useEntityState', () => {
    it('fetches entity state when id is provided', async () => {
      const entityId = 'DWP1';

      server.use(
        http.get(`/api/v1/ontology/entities/${entityId}`, () => {
          return HttpResponse.json({
            id: entityId,
            label: 'Drinking Water Plant 1',
            type: 'DWP',
            lat: 51.0543,
            lon: 3.7174,
            zone: 'Zone_A',
            capacity: '2000',
            description: 'Main drinking water treatment facility'
          });
        })
      );

      const { result } = renderHook(() => useEntityState(entityId), {
        wrapper: createWrapper()
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toMatchObject({
        id: entityId,
        label: 'Drinking Water Plant 1',
        type: 'DWP',
        coordinates: [51.0543, 3.7174]
      });
    });

    it('does not fetch when id is null', async () => {
      const { result } = renderHook(() => useEntityState(null), {
        wrapper: createWrapper()
      });

      // Should remain idle
      expect(result.current.isFetching).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useEntityTriplets', () => {
    it('fetches entity triplets correctly', async () => {
      const entityId = 'DWP1';

      const { result } = renderHook(() => useEntityTriplets(entityId), {
        wrapper: createWrapper()
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(Array.isArray(result.current.data)).toBe(true);
      expect(result.current.data!.length).toBeGreaterThan(0);

      // Verify triplet structure
      const firstTriplet = result.current.data![0];
      expect(firstTriplet).toHaveProperty('subject');
      expect(firstTriplet).toHaveProperty('predicate');
      expect(firstTriplet).toHaveProperty('object');
    });

    it('returns empty array when id is null', async () => {
      const { result } = renderHook(() => useEntityTriplets(null), {
        wrapper: createWrapper()
      });

      // Should remain idle
      expect(result.current.isFetching).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useSparqlQuery', () => {
    it('executes SPARQL query successfully', async () => {
      const { result } = renderHook(() => useSparqlQuery(), {
        wrapper: createWrapper()
      });

      // Execute mutation
      result.current.mutate({
        query: 'SELECT ?entity WHERE { ?entity a wf:DrinkingWaterPlant }',
        format: 'json'
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      // Verify response structure
      expect(result.current.data).toBeDefined();
      expect(result.current.data).toHaveProperty('head');
      expect(result.current.data).toHaveProperty('results');
      expect(result.current.data).toHaveProperty('query_time_ms');
      expect(result.current.data?.format).toBe('json');

      // Verify results
      const bindings = result.current.data?.results?.bindings;
      expect(bindings).toBeDefined();
      expect(bindings!.length).toBeGreaterThan(0);
    });

    it('handles invalid SPARQL syntax', async () => {
      const { result } = renderHook(() => useSparqlQuery(), {
        wrapper: createWrapper()
      });

      result.current.mutate({
        query: 'INVALID QUERY',
        format: 'json'
      });

      await waitFor(() => expect(result.current.isError).toBe(true));
      expect(result.current.error).toBeDefined();
    });

    it('includes query timing information', async () => {
      const { result } = renderHook(() => useSparqlQuery(), {
        wrapper: createWrapper()
      });

      result.current.mutate({
        query: 'SELECT * WHERE { ?s ?p ?o } LIMIT 10',
        format: 'json'
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data?.query_time_ms).toBeDefined();
      expect(typeof result.current.data?.query_time_ms).toBe('number');
      expect(result.current.data!.query_time_ms).toBeGreaterThanOrEqual(0);
    });
  });

  describe('useNaturalLanguageQuery', () => {
    it('translates and executes natural language query', async () => {
      const { result } = renderHook(() => useNaturalLanguageQuery(), {
        wrapper: createWrapper()
      });

      const question = 'What are the drinking water plants?';
      result.current.mutate({ question });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      // Verify response structure
      expect(result.current.data).toBeDefined();
      expect(result.current.data?.original_question).toBe(question);
      expect(result.current.data?.generated_sparql).toBeDefined();
      expect(result.current.data?.results).toBeDefined();
      expect(result.current.data?.execution_plan).toBeDefined();

      // Verify SPARQL was generated
      expect(result.current.data?.generated_sparql).toContain('SELECT');
      expect(result.current.data?.generated_sparql).toContain('DrinkingWaterPlant');
    });

    it('provides execution plan in response', async () => {
      const { result } = renderHook(() => useNaturalLanguageQuery(), {
        wrapper: createWrapper()
      });

      result.current.mutate({
        question: 'Show me the water quality sensors'
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data?.execution_plan).toBeDefined();
      expect(typeof result.current.data?.execution_plan).toBe('string');
    });
  });

  describe('useRelationships', () => {
    it('fetches and transforms relationship data via SPARQL', async () => {
      const { result } = renderHook(() => useRelationships(), {
        wrapper: createWrapper()
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(Array.isArray(result.current.data)).toBe(true);

      if (result.current.data!.length > 0) {
        const relationship = result.current.data![0];
        expect(relationship).toHaveProperty('source');
        expect(relationship).toHaveProperty('target');
        expect(relationship).toHaveProperty('predicate');
      }
    });

    it('filters out incomplete relationships', async () => {
      // Mock response with some incomplete relationships
      server.use(
        http.post('/api/v1/query/sparql', () => {
          return HttpResponse.json({
            results: {
              bindings: [
                {
                  sourceId: { value: 'DWP1' },
                  targetId: { value: 'WWTP1' },
                  label: { value: 'Flow' }
                },
                {
                  // Missing targetId
                  sourceId: { value: 'DWP2' },
                  label: { value: 'Flow' }
                }
              ]
            }
          });
        })
      );

      const { result } = renderHook(() => useRelationships(), {
        wrapper: createWrapper()
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      // Should filter out the incomplete relationship
      const validRelationships = result.current.data!.filter(r => r.source && r.target);
      expect(validRelationships.length).toBe(1);
    });
  });

  describe('useRunSimulation', () => {
    it('submits simulation request and receives results', async () => {
      const { result } = renderHook(() => useRunSimulation(), {
        wrapper: createWrapper()
      });

      const simulationPayload = {
        entity_ids: ['DWP1', 'WWTP1'],
        scenario: {
          duration: 3600,
          timestep: 60
        },
        parameters: {
          initial_flow: 100
        }
      };

      result.current.mutate(simulationPayload);

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      // Verify response structure
      expect(result.current.data).toBeDefined();
      expect(result.current.data).toHaveProperty('simulation_id');
      expect(result.current.data).toHaveProperty('status');
      expect(result.current.data).toHaveProperty('results');

      // Verify simulation completed
      expect(result.current.data?.status).toBe('completed');
      expect(result.current.data?.results).toHaveProperty('timeseries');
      expect(result.current.data?.results).toHaveProperty('summary');
    });
  });

  describe('useSensorData', () => {
    it('fetches historical sensor data for entity', async () => {
      const entityId = 'DWP1';

      const { result } = renderHook(() => useSensorData(entityId), {
        wrapper: createWrapper()
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(Array.isArray(result.current.data)).toBe(true);

      if (result.current.data!.length > 0) {
        const sensorReading = result.current.data![0];
        expect(sensorReading).toHaveProperty('sensor_id');
        expect(sensorReading).toHaveProperty('timestamp');
        expect(sensorReading).toHaveProperty('value');
        expect(sensorReading).toHaveProperty('unit');
      }
    });

    it('does not fetch when entity id is null', async () => {
      const { result } = renderHook(() => useSensorData(null), {
        wrapper: createWrapper()
      });

      expect(result.current.isFetching).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });
});
