import React, { useMemo, useState } from 'react';
import { Box, Stack } from '@mantine/core';
import type { QueryTrace, ExecutionEvent } from '../../api/types';

interface TraceTimelineProps {
    trace: QueryTrace;
    scenarioId?: string;
}

const AGENT_TYPE_FILL: Record<string, string> = {
    orchestrator: '#845ef7',
    model: '#20c997',
    llm: '#fd7e14',
    user: '#adb5bd',
    sparql: '#4dabf7',
};

const ROW_HEIGHT = 30;
const LABEL_WIDTH = 160;
const BAR_HEIGHT = 18;
const BAR_Y_OFFSET = (ROW_HEIGHT - BAR_HEIGHT) / 2;
const MIN_DURATION_PX = 4;
const TICK_COUNT = 5;
const SVG_WIDTH = 680;
const AXIS_HEIGHT = 20;

const TraceTimeline: React.FC<TraceTimelineProps> = ({ trace, scenarioId }) => {
    const [hovered, setHovered] = useState<string | null>(null);

    const events: ExecutionEvent[] = useMemo(() => {
        if (scenarioId) {
            const scenario = trace.scenarios.find((s) => s.scenarioId === scenarioId);
            return scenario?.events ?? trace.events;
        }
        return trace.events;
    }, [trace, scenarioId]);

    const traceStart = useMemo(() => new Date(trace.startTime).getTime(), [trace.startTime]);

    const traceEnd = useMemo(() => {
        const endTimes = events
            .filter((e) => e.endTime)
            .map((e) => new Date(e.endTime!).getTime());
        return endTimes.length > 0 ? Math.max(...endTimes) : traceStart + 1000;
    }, [events, traceStart]);

    const totalDuration = Math.max(traceEnd - traceStart, 1);

    const agents = useMemo(() => {
        const seen = new Map<string, string>();
        events.forEach((e) => {
            if (!seen.has(e.agentUri)) seen.set(e.agentUri, e.agentName);
        });
        return Array.from(seen.entries()).map(([uri, name]) => ({ uri, name }));
    }, [events]);

    const usableWidth = SVG_WIDTH - LABEL_WIDTH - 8;
    const svgHeight = agents.length * ROW_HEIGHT + AXIS_HEIGHT;

    const msToPx = (ms: number) => (ms / totalDuration) * usableWidth;

    const ticks = Array.from({ length: TICK_COUNT + 1 }, (_, i) => ({
        ms: Math.round((i / TICK_COUNT) * totalDuration),
        px: (i / TICK_COUNT) * usableWidth,
    }));

    return (
        <Stack gap="xs">
            <Box style={{ overflowX: 'auto' }}>
                <svg
                    width={SVG_WIDTH}
                    height={svgHeight}
                    style={{ fontFamily: 'system-ui, sans-serif', display: 'block' }}
                >
                    {/* Tick lines */}
                    {ticks.map((tick, i) => (
                        <g key={i} transform={`translate(${LABEL_WIDTH + tick.px}, 0)`}>
                            <line
                                x1={0}
                                y1={0}
                                x2={0}
                                y2={svgHeight - AXIS_HEIGHT}
                                stroke="#dee2e6"
                                strokeWidth={1}
                            />
                            <text
                                y={svgHeight - 4}
                                textAnchor="middle"
                                fontSize={9}
                                fill="#868e96"
                            >
                                {tick.ms}ms
                            </text>
                        </g>
                    ))}

                    {/* Swimlane rows */}
                    {agents.map((agent, rowIdx) => {
                        const y = rowIdx * ROW_HEIGHT;
                        const agentEvents = events.filter((e) => e.agentUri === agent.uri);
                        const truncName =
                            agent.name.length > 20 ? agent.name.slice(0, 18) + '…' : agent.name;

                        return (
                            <g key={agent.uri}>
                                <rect
                                    x={0}
                                    y={y}
                                    width={SVG_WIDTH}
                                    height={ROW_HEIGHT}
                                    fill={rowIdx % 2 === 0 ? '#f8f9fa' : '#ffffff'}
                                />
                                <text
                                    x={LABEL_WIDTH - 6}
                                    y={y + ROW_HEIGHT / 2 + 4}
                                    textAnchor="end"
                                    fontSize={10}
                                    fill="#495057"
                                >
                                    {truncName}
                                </text>

                                {agentEvents.map((evt) => {
                                    const startMs =
                                        new Date(evt.startTime).getTime() - traceStart;
                                    const endMs = evt.endTime
                                        ? new Date(evt.endTime).getTime() - traceStart
                                        : totalDuration;
                                    const barX = LABEL_WIDTH + msToPx(startMs);
                                    const barW = Math.max(
                                        MIN_DURATION_PX,
                                        msToPx(endMs - startMs),
                                    );
                                    const fill = AGENT_TYPE_FILL[evt.agentType] ?? '#adb5bd';
                                    const isRunning = evt.status === 'running';
                                    const isHov = hovered === evt.eventId;

                                    return (
                                        <g key={evt.eventId}>
                                            <rect
                                                x={barX}
                                                y={y + BAR_Y_OFFSET}
                                                width={barW}
                                                height={BAR_HEIGHT}
                                                rx={3}
                                                fill={fill}
                                                opacity={isRunning ? 0.5 : isHov ? 1 : 0.8}
                                                style={{ cursor: 'pointer' }}
                                                onMouseEnter={() => setHovered(evt.eventId)}
                                                onMouseLeave={() => setHovered(null)}
                                            />
                                            {isRunning && (
                                                <rect
                                                    x={barX}
                                                    y={y + BAR_Y_OFFSET}
                                                    width={barW}
                                                    height={BAR_HEIGHT}
                                                    rx={3}
                                                    fill={fill}
                                                    opacity={0.3}
                                                >
                                                    <animate
                                                        attributeName="opacity"
                                                        values="0.2;0.6;0.2"
                                                        dur="1.2s"
                                                        repeatCount="indefinite"
                                                    />
                                                </rect>
                                            )}
                                        </g>
                                    );
                                })}
                            </g>
                        );
                    })}
                </svg>
            </Box>
        </Stack>
    );
};

export default TraceTimeline;
