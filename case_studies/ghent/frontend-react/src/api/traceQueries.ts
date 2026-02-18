import { useQuery } from '@tanstack/react-query';
import client from './client';
import type { TraceSummary, TraceDetail, TraceGraph } from './traceTypes';

export const useExecutionTraces = (limit: number = 50) => {
    return useQuery<TraceSummary[]>({
        queryKey: ['traces', limit],
        queryFn: async () => {
            const { data } = await client.get(`/traces?limit=${limit}`);
            return data.traces || [];
        },
    });
};

export const useTraceDetail = (traceId: string | null) => {
    return useQuery<TraceDetail>({
        queryKey: ['trace', traceId],
        queryFn: async () => {
            if (!traceId) return null;
            const { data } = await client.get(`/traces/${traceId}`);
            return data;
        },
        enabled: !!traceId,
    });
};

export const useTraceGraph = (traceId: string | null) => {
    return useQuery<TraceGraph>({
        queryKey: ['trace-graph', traceId],
        queryFn: async () => {
            if (!traceId) return null;
            const { data } = await client.get(`/traces/${traceId}/graph`);
            return data;
        },
        enabled: !!traceId,
    });
};
