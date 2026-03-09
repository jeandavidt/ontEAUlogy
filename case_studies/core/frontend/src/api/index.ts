/**
 * API client utilities
 */

export interface APIClientConfig {
  baseUrl: string;
  timeout?: number;
}

export class APIClient {
  private baseUrl: string;
  private timeout: number;

  constructor(config: APIClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    this.timeout = config.timeout || 30000;
  }

  private async fetchWithTimeout(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  async get<T>(path: string): Promise<T> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}${path}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json() as Promise<T>;
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    const response = await this.fetchWithTimeout(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json() as Promise<T>;
  }
}

// Health check
export async function checkHealth(orchestratorUrl: string): Promise<{
  status: string;
  version: string;
  components: Record<string, string>;
}> {
  const response = await fetch(`${orchestratorUrl}/health`);
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
}
