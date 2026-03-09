/**
 * Shared React hooks
 */

import { useState, useEffect, useCallback } from 'react';
import type { SensorReading } from '../types/index.js';

/**
 * Hook for managing WebSocket connections
 */
export function useWebSocket(url: string | null) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
  const [error, setError] = useState<Event | null>(null);

  useEffect(() => {
    if (!url) return;

    const ws = new WebSocket(url);

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = (e) => setError(e);
    ws.onmessage = (msg) => setLastMessage(msg);

    return () => {
      ws.close();
    };
  }, [url]);

  return { connected, lastMessage, error };
}

/**
 * Hook for fetching entity data
 */
export function useEntities(orchestratorUrl: string) {
  const [entities, setEntities] = useState<Array<{ id: string; label: string; type: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEntities = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${orchestratorUrl}/discovery/entities`);
      const data = await response.json();
      setEntities(data.entities || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [orchestratorUrl]);

  useEffect(() => {
    fetchEntities();
  }, [fetchEntities]);

  return { entities, loading, error, refetch: fetchEntities };
}

/**
 * Hook for managing sensor data
 */
export function useSensors(orchestratorUrl: string, entityId?: string) {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const wsUrl = orchestratorUrl.replace('http', 'ws') + '/ws/sensors';
  const { connected, lastMessage } = useWebSocket(wsUrl);

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data);
        if (data.type === 'sensor_update') {
          setReadings((prev) => [...prev.slice(-100), data.reading]);
        }
      } catch {
        // Ignore parse errors
      }
    }
  }, [lastMessage]);

  const filteredReadings = entityId
    ? readings.filter((r) => r.entityId === entityId)
    : readings;

  return { readings: filteredReadings, connected };
}
