/**
 * Shared state management using Zustand
 */

import { create } from 'zustand';
import type { Entity, ModelInfo } from '../types/index.js';

interface SelectionState {
  selectedEntity: Entity | null;
  selectedModel: ModelInfo | null;
  setSelectedEntity: (entity: Entity | null) => void;
  setSelectedModel: (model: ModelInfo | null) => void;
  clearSelection: () => void;
}

export const useSelectionStore = create<SelectionState>((set) => ({
  selectedEntity: null,
  selectedModel: null,
  setSelectedEntity: (entity) => set({ selectedEntity: entity }),
  setSelectedModel: (model) => set({ selectedModel: model }),
  clearSelection: () => set({ selectedEntity: null, selectedModel: null }),
}));

interface ConfigState {
  orchestratorUrl: string;
  setOrchestratorUrl: (url: string) => void;
}

export const useConfigStore = create<ConfigState>((set) => ({
  orchestratorUrl: 'http://localhost:8080',
  setOrchestratorUrl: (url) => set({ orchestratorUrl: url }),
}));

interface QueryState {
  sparqlQuery: string;
  queryResults: unknown | null;
  isLoading: boolean;
  error: string | null;
  setSparqlQuery: (query: string) => void;
  setQueryResults: (results: unknown) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useQueryStore = create<QueryState>((set) => ({
  sparqlQuery: '',
  queryResults: null,
  isLoading: false,
  error: null,
  setSparqlQuery: (query) => set({ sparqlQuery: query }),
  setQueryResults: (results) => set({ queryResults: results }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));
