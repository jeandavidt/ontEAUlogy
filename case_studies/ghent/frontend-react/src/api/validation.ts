import { z } from 'zod';

// SPARQL Binding Schema - handles {value: string, type?: string} structure
export const SparqlBindingSchema = z.object({
  value: z.string(),
  type: z.string().optional(),
  datatype: z.string().optional(),
  'xml:lang': z.string().optional(),
});

// SPARQL Results Schema - handles different response formats
export const SparqlResultsSchema = z.union([
  // Standard SPARQL JSON format: {results: {bindings: [...]}}
  z.object({
    head: z.object({
      vars: z.array(z.string()),
    }),
    results: z.object({
      bindings: z.array(z.record(z.string(), z.union([SparqlBindingSchema, z.unknown()]))),
    }),
  }),
  // Flat array format: {results: [...]}
  z.object({
    results: z.array(z.unknown()),
  }),
  // Direct array format
  z.array(z.unknown()),
]);

// Natural Language Query Results Schema
export const NLQueryResultsSchema = z.object({
  original_question: z.string(),
  generated_sparql: z.string().optional(),
  results: z.unknown().optional(), // Will be validated with SparqlResultsSchema
  execution_plan: z.string().optional(),
  simulation_required: z.boolean().optional(),
  suggested_models: z.array(z.string()).optional(),
  error: z.string().optional(),
});

// Entity Schema
export const EntitySchema = z.object({
  id: z.string(),
  uri: z.string().optional(),
  label: z.string(),
  type: z.string(),
  lat: z.number(),
  lon: z.number(),
  zone: z.string().optional(),
  capacity: z.string().optional(),
  description: z.string().optional(),
});

// Entities Response Schema
export const EntitiesResponseSchema = z.object({
  entities: z.array(EntitySchema),
  count: z.number().optional(),
});

// Triplet Schema
export const TripletSchema = z.object({
  subject: z.string(),
  predicate: z.string(),
  object: z.string(),
  isUri: z.boolean().optional(),
});

// Triplets Response Schema
export const TripletsResponseSchema = z.object({
  triples: z.array(TripletSchema),
});

// Simulation Response Schema
export const SimulationStartResponseSchema = z.object({
  job_id: z.string(),
  model_id: z.string(),
  status: z.string(),
  message: z.string(),
});

export const SimulationResultSchema = z.object({
  job_id: z.string(),
  outputs: z.record(z.string(), z.number()),
  timeSeries: z.array(z.object({
    time: z.string(),
    value: z.number(),
  })).optional(),
});

// Sensor Data Schema
export const SensorDataSchema = z.record(z.string(), z.unknown());

// Error Response Schema
export const ErrorResponseSchema = z.object({
  detail: z.string(),
  error_code: z.string().optional(),
  timestamp: z.string().optional(),
});

// Helper function to validate responses safely
export function safeValidate<T>(schema: z.ZodSchema<T>, data: unknown): T | null {
  const result = schema.safeParse(data);
  if (!result.success) {
    console.warn('Validation warning:', result.error.message);
    // Log detailed error for debugging
    console.warn('Validation details:', JSON.stringify(result.error.issues, null, 2));
    return null;
  }
  return result.data;
}

// Helper function to validate with passthrough (allows unknown fields)
export function validateWithPassthrough<T>(schema: z.ZodSchema<T>, data: unknown): T | null {
  const result = schema.safeParse(data);
  if (!result.success) {
    console.warn('Validation warning:', result.error.message);
    return null;
  }
  return result.data;
}

// Validation logging levels
export const ValidationLogLevel = {
  NONE: 'none',
  WARN: 'warn', 
  ERROR: 'error',
} as const;

// Configuration for validation behavior
export const validationConfig = {
  logLevel: ValidationLogLevel.WARN,
  strict: false, // If true, validation errors throw exceptions
};

// Main validation function that respects configuration
export function validateResponse<T>(
  schema: z.ZodSchema<T>,
  data: unknown,
  options: {
    passthrough?: boolean;
    logLevel?: string;
    context?: string;
  } = {}
): T | null {
  const { logLevel = validationConfig.logLevel, context = 'Response' } = options;

  const result = schema.safeParse(data);

  if (!result.success) {
    const message = `${context} validation failed: ${result.error.message}`;

    switch (logLevel) {
      case 'error':
        console.error(message);
        break;
      case 'warn':
        console.warn(message);
        break;
      case 'none':
        break;
    }
    
    if (validationConfig.strict) {
      throw new Error(message);
    }
    
    return null;
  }
  
  return result.data;
}