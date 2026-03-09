/**
 * Utility functions
 */

/**
 * Format a number with specified precision
 */
export function formatNumber(value: number, precision = 2): string {
  return value.toFixed(precision);
}

/**
 * Format a timestamp to local string
 */
export function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString();
}

/**
 * Truncate a string to specified length
 */
export function truncate(str: string, maxLength = 50): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + '...';
}

/**
 * Extract local name from URI
 */
export function getLocalName(uri: string): string {
  const hashIndex = uri.lastIndexOf('#');
  if (hashIndex >= 0) return uri.slice(hashIndex + 1);
  const slashIndex = uri.lastIndexOf('/');
  if (slashIndex >= 0) return uri.slice(slashIndex + 1);
  return uri;
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Parse SPARQL result bindings
 */
export function parseSparqlBindings(bindings: Array<Record<string, { type: string; value: string }>>): Record<string, string>[] {
  return bindings.map((binding) => {
    const parsed: Record<string, string> = {};
    for (const [key, value] of Object.entries(binding)) {
      parsed[key] = value.value;
    }
    return parsed;
  });
}
