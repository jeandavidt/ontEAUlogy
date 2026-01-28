/**
 * Tests for API client configuration
 * Verifies that axios client is properly configured for backend communication
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import client from '../client';

describe('API Client Configuration', () => {
  it('has correct base URL configuration', () => {
    expect(client.defaults.baseURL).toBeDefined();
    // Should use /api/v1 or environment variable
    const expectedBase = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    expect(client.defaults.baseURL).toBe(expectedBase);
  });

  it('has correct Content-Type header', () => {
    expect(client.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('has response error interceptor configured', () => {
    // Client should have interceptors for error handling
    expect(client.interceptors.response.handlers.length).toBeGreaterThan(0);
  });

  it('handles successful responses', async () => {
    const mockResponse = {
      data: { test: 'data' },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    };

    // Test response interceptor with success
    const successHandler = client.interceptors.response.handlers[0].fulfilled;
    if (successHandler) {
      const result = successHandler(mockResponse);
      expect(result).toEqual(mockResponse);
    }
  });

  it('handles error responses', async () => {
    const mockError = {
      response: {
        data: { detail: 'Test error' },
        status: 400,
        statusText: 'Bad Request',
        headers: {},
        config: {} as any
      },
      isAxiosError: true,
      message: 'Request failed with status code 400',
      name: 'AxiosError',
      config: {} as any,
      toJSON: () => ({})
    };

    // Spy on console.error to verify logging
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Test error interceptor
    const errorHandler = client.interceptors.response.handlers[0].rejected;
    if (errorHandler) {
      await expect(errorHandler(mockError)).rejects.toEqual(mockError);
      expect(consoleSpy).toHaveBeenCalledWith(
        'API Error:',
        expect.any(Object)
      );
    }

    consoleSpy.mockRestore();
  });

  it('logs errors without response data', async () => {
    const mockError = {
      message: 'Network Error',
      isAxiosError: true,
      name: 'AxiosError',
      config: {} as any,
      toJSON: () => ({})
    };

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const errorHandler = client.interceptors.response.handlers[0].rejected;
    if (errorHandler) {
      await expect(errorHandler(mockError)).rejects.toEqual(mockError);
      expect(consoleSpy).toHaveBeenCalledWith(
        'API Error:',
        'Network Error'
      );
    }

    consoleSpy.mockRestore();
  });

  it('is an axios instance', () => {
    expect(client).toBeInstanceOf(Function);
    expect(client.defaults).toBeDefined();
    expect(client.interceptors).toBeDefined();
  });

  describe('HTTP Methods', () => {
    it('has GET method', () => {
      expect(typeof client.get).toBe('function');
    });

    it('has POST method', () => {
      expect(typeof client.post).toBe('function');
    });

    it('has PUT method', () => {
      expect(typeof client.put).toBe('function');
    });

    it('has DELETE method', () => {
      expect(typeof client.delete).toBe('function');
    });

    it('has PATCH method', () => {
      expect(typeof client.patch).toBe('function');
    });
  });
});
