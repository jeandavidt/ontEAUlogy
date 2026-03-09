/**
 * Core types for ontEAUlogy frontend
 */

export interface Entity {
  id: string;
  type: string;
  label: string;
  description?: string;
  properties?: Record<string, unknown>;
}

export interface ModelInfo {
  id: string;
  name: string;
  endpoint: string;
  capabilities: string[];
  entities: string[];
  description?: string;
}

export interface SimulationResult {
  modelId: string;
  status: 'success' | 'error' | 'pending';
  outputs?: Record<string, number>;
  error?: string;
  executionTime?: number;
}

export interface SensorReading {
  sensorId: string;
  entityId: string;
  property: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface SPARQLResult {
  head: {
    vars: string[];
  };
  results: {
    bindings: Array<Record<string, {
      type: string;
      value: string;
      datatype?: string;
    }>>;
  };
}

export interface OntologyClass {
  uri: string;
  label: string;
  description?: string;
  parentClasses?: string[];
}

export interface NamespaceConfig {
  prefix: string;
  uri: string;
}

export interface FrontendConfig {
  app: {
    name: string;
    title: string;
    description: string;
    version: string;
  };
  branding: {
    primaryColor: string;
    secondaryColor: string;
  };
  api: {
    baseUrl: string;
    orchestratorUrl: string;
    timeout: number;
  };
  features: {
    sparqlQuery: boolean;
    naturalLanguage: boolean;
    simulation: boolean;
    sensors: boolean;
    map: boolean;
    topology: boolean;
    timeline: boolean;
  };
}
