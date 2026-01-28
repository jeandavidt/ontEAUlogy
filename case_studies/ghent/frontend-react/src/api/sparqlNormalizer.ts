import { SparqlBindingSchema } from './validation';

export interface NormalizedResult {
  [key: string]: unknown;
}

export interface NormalizedSparqlResponse {
  head?: {
    vars: string[];
  };
  results: {
    bindings: NormalizedResult[];
  };
  format?: string;
  query_time_ms?: number;
}

/**
 * Normalizes different SPARQL response formats into a consistent structure.
 *
 * Handles:
 * - {results: {bindings: [...]}} - Standard SPARQL JSON format
 * - {results: [...]} - Flat array format
 * - Array directly - Direct array format
 *
 * Always returns consistent shape for components.
 */
export function normalizeSparqlResults(data: unknown): NormalizedSparqlResponse {
  // Case 1: Standard SPARQL JSON format with bindings
  if (
    typeof data === 'object' &&
    data !== null &&
    'results' in (data as any) &&
    (data as any).results !== null &&
    'bindings' in (data as any).results
  ) {
    const response = data as any;
    // Don't normalize individual bindings - keep the original structure
    // Each binding is an object with keys like {sourceId: {type, value}, targetId: {type, value}, ...}
    const bindings = Array.isArray(response.results.bindings)
      ? response.results.bindings
      : [];

    return {
      head: response.head || { vars: extractVariablesFromBindings(bindings) },
      results: { bindings },
      format: response.format || 'json',
      query_time_ms: response.query_time_ms,
    };
  }

  // Case 2: Flat array format {results: [...]}
  if (
    typeof data === 'object' &&
    data !== null &&
    'results' in (data as any) &&
    Array.isArray((data as any).results)
  ) {
    const response = data as any;
    const bindings = response.results.map(normalizeUnknownResult);

    return {
      head: { vars: extractVariablesFromBindings(bindings) },
      results: { bindings },
      format: response.format || 'json',
      query_time_ms: response.query_time_ms,
    };
  }

  // Case 3: Direct array format
  if (Array.isArray(data)) {
    const bindings = data.map(normalizeUnknownResult);

    return {
      head: { vars: extractVariablesFromBindings(bindings) },
      results: { bindings },
      format: 'json',
    };
  }

  // Case 4: Unknown format - wrap in empty structure
  console.warn('Unknown SPARQL response format:', data);
  return {
    head: { vars: [] },
    results: { bindings: [] },
    format: 'json',
  };
}

/**
 * Normalizes a SPARQL binding object, ensuring consistent structure.
 */
export function normalizeBinding(binding: unknown): NormalizedResult {
  // Validate the binding structure
  const parsed = SparqlBindingSchema.safeParse(binding);
  if (parsed.success) {
    return { value: parsed.data.value };
  }

  // If it's already a normalized result
  if (
    typeof binding === 'object' &&
    binding !== null &&
    'value' in binding
  ) {
    return binding as NormalizedResult;
  }

  // Handle other formats - wrap as value
  return {
    value: binding?.toString() || ''
  };
}

/**
 * Normalizes unknown result objects that might come from flat array format.
 */
function normalizeUnknownResult(result: unknown): NormalizedResult {
  if (typeof result === 'object' && result !== null && !Array.isArray(result)) {
    // If object already has normalized structure
    if ('value' in result) {
      return result as NormalizedResult;
    }

    // Convert object properties to normalized bindings
    const normalized: NormalizedResult = {};
    for (const [key, value] of Object.entries(result)) {
      normalized[key] = normalizeBinding(value);
    }
    return normalized;
  }

  // Handle primitive values
  return {
    value: result?.toString() || ''
  };
}

/**
 * Extracts variable names from raw SPARQL bindings (before normalization).
 */
function extractVariablesFromBindings(bindings: NormalizedResult[]): string[] {
  const variables = new Set<string>();

  if (bindings.length === 0) return [];

  // Get variables from first binding
  const firstBinding = bindings[0];
  if (typeof firstBinding === 'object' && firstBinding !== null) {
    Object.keys(firstBinding).forEach(key => {
      variables.add(key);
    });
  }

  return Array.from(variables).sort();
}

/**
 * Converts normalized bindings back to a simpler format for display.
 *
 * This function takes the normalized structure and converts it to a more
 * user-friendly format for components that expect simple key-value pairs.
 */
export function simplifyResults(bindings: NormalizedResult[]): Record<string, string>[] {
  return bindings.map(binding => {
    const simplified: Record<string, string> = {};

    Object.entries(binding).forEach(([key, value]) => {
      if (typeof value === 'object' && value !== null && 'value' in value) {
        simplified[key] = (value as any).value?.toString() || '';
      } else {
        simplified[key] = value?.toString() || '';
      }
    });

    return simplified;
  });
}

/**
 * Validates and normalizes SPARQL results with error handling.
 *
 * This is the main function that should be used in API query handlers.
 * It combines validation and normalization for robust error handling.
 */
export function processSparqlResults(
  data: unknown,
  context: string = 'SPARQL query'
): NormalizedSparqlResponse {
  try {
    const normalized = normalizeSparqlResults(data);

    // Basic validation
    if (!normalized.results || !Array.isArray(normalized.results.bindings)) {
      console.warn(`${context}: Invalid results structure after normalization`);
      return {
        head: { vars: [] },
        results: { bindings: [] },
        format: 'json',
      };
    }

    return normalized;
  } catch (error) {
    console.error(`${context}: Error processing SPARQL results:`, error);
    return {
      head: { vars: [] },
      results: { bindings: [] },
      format: 'json',
    };
  }
}

/**
 * Extracts specific values from normalized results by variable name.
 *
 * Useful for components that need to extract specific columns from SPARQL results.
 */
export function extractVariable(
  bindings: NormalizedResult[],
  variableName: string
): unknown[] {
  return bindings.map(binding => {
    if (variableName in binding) {
      const value = binding[variableName];
      if (typeof value === 'object' && value !== null && 'value' in value) {
        return (value as any).value;
      }
      return value;
    }
    return null;
  });
}

/**
 * Counts the number of results in a normalized SPARQL response.
 */
export function countResults(response: NormalizedSparqlResponse): number {
  return response.results?.bindings?.length || 0;
}

/**
 * Checks if a SPARQL response has any results.
 */
export function hasResults(response: NormalizedSparqlResponse): boolean {
  return countResults(response) > 0;
}
