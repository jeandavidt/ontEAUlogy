import React, { useEffect, useMemo, useState } from 'react';
import ReactFlow, {
    Background,
    Controls,
    ReactFlowProvider,
    useNodesState,
    useEdgesState,
    type Node,
    type Edge,
    type NodeTypes,
    type EdgeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
    Paper,
    Stack,
    Group,
    Text,
    Badge,
    SegmentedControl,
    Tabs,
    Loader,
} from '@mantine/core';
import type { ExecutionEvent, QueryTrace } from '../api/types';
import { useQueryTrace, useTraceWebSocket } from '../api/queries';
import AgentEventNode from './trace/AgentEventNode';
import LayerGroupNode from './trace/LayerGroupNode';
import DataFlowEdge, { type DataFlowEdgeData } from './trace/DataFlowEdge';
import TraceTimeline from './trace/TraceTimeline';

// ── Layout constants ──────────────────────────────────────────────────────────
const NODE_WIDTH = 190;
const NODE_HEIGHT = 80;
const COL_GAP = 60;
const ROW_GAP = 20;
const GROUP_PAD_X = 12;
const GROUP_PAD_TOP = 30;
const GROUP_PAD_BOTTOM = 14;

const LAYER_COLORS = [
    'rgba(224,242,254,0.55)',
    'rgba(209,250,229,0.55)',
    'rgba(255,251,235,0.55)',
    'rgba(243,232,255,0.55)',
    'rgba(255,235,235,0.55)',
];

// ── Layout builder ────────────────────────────────────────────────────────────
function buildLayout(events: ExecutionEvent[]): { nodes: Node[]; edges: Edge[] } {
    // Group events by layerIndex (-1 for orchestration/no-layer events)
    const layerMap = new Map<number, ExecutionEvent[]>();
    events.forEach((evt) => {
        const layer = evt.layerIndex ?? -1;
        if (!layerMap.has(layer)) layerMap.set(layer, []);
        layerMap.get(layer)!.push(evt);
    });

    const sortedLayers = Array.from(layerMap.keys()).sort((a, b) => a - b);
    const colWidth = NODE_WIDTH + 2 * GROUP_PAD_X;
    const colStep = colWidth + COL_GAP;

    const nodes: Node[] = [];
    const edges: Edge[] = [];

    sortedLayers.forEach((layer, colIdx) => {
        const layerEvents = layerMap.get(layer)!;
        const colX = colIdx * colStep;
        const nodeX = colX + GROUP_PAD_X;

        const groupHeight =
            GROUP_PAD_TOP +
            layerEvents.length * (NODE_HEIGHT + ROW_GAP) -
            ROW_GAP +
            GROUP_PAD_BOTTOM;

        // Background group node
        nodes.push({
            id: `layer-${layer}`,
            type: 'layerGroup',
            position: { x: colX, y: 0 },
            style: { width: colWidth, height: groupHeight, zIndex: -1 },
            data: {
                label: layer === -1 ? 'Orchestration' : `Layer ${layer}`,
                color: LAYER_COLORS[colIdx % LAYER_COLORS.length],
            },
            draggable: false,
            selectable: false,
        });

        // Event nodes
        layerEvents.forEach((evt, rowIdx) => {
            const nodeY = GROUP_PAD_TOP + rowIdx * (NODE_HEIGHT + ROW_GAP);
            nodes.push({
                id: evt.eventId,
                type: 'agentEvent',
                position: { x: nodeX, y: nodeY },
                data: { event: evt },
                style: { width: NODE_WIDTH },
            });
        });
    });

    // Build data-flow edges: output.name === input.name across different events
    const eventList = events;
    const edgeSet = new Set<string>();

    eventList.forEach((target) => {
        target.inputs.forEach((inp) => {
            eventList.forEach((source) => {
                if (source.eventId === target.eventId) return;
                const match = source.outputs.find((out) => out.name === inp.name);
                if (match) {
                    const key = `${source.eventId}->${target.eventId}::${inp.name}`;
                    if (!edgeSet.has(key)) {
                        edgeSet.add(key);
                        edges.push({
                            id: `edge-${key}`,
                            source: source.eventId,
                            target: target.eventId,
                            type: 'dataFlow',
                            data: { parameterName: inp.name } satisfies DataFlowEdgeData,
                            animated: target.status === 'running' || source.status === 'running',
                        });
                    }
                }
            });
        });
    });

    return { nodes, edges };
}

// ── Custom types ──────────────────────────────────────────────────────────────
const NODE_TYPES: NodeTypes = {
    agentEvent: AgentEventNode,
    layerGroup: LayerGroupNode,
};

const EDGE_TYPES: EdgeTypes = {
    dataFlow: DataFlowEdge,
};

// ── Diagram sub-component (needs ReactFlowProvider context) ───────────────────
interface DiagramInnerProps {
    events: ExecutionEvent[];
}

const DiagramInner: React.FC<DiagramInnerProps> = ({ events }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    useEffect(() => {
        const { nodes: n, edges: e } = buildLayout(events);
        setNodes(n);
        setEdges(e);
    }, [events, setNodes, setEdges]);

    return (
        <div
            style={{
                width: '100%',
                height: 420,
                border: '1px solid #e9ecef',
                borderRadius: 8,
            }}
        >
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={NODE_TYPES}
                edgeTypes={EDGE_TYPES}
                fitView
                fitViewOptions={{ padding: 0.2 }}
                proOptions={{ hideAttribution: true }}
            >
                <Background color="#f1f3f5" gap={20} />
                <Controls />
            </ReactFlow>
        </div>
    );
};

const Diagram: React.FC<DiagramInnerProps> = (props) => (
    <ReactFlowProvider>
        <DiagramInner {...props} />
    </ReactFlowProvider>
);

// ── Main QueryTimeline component ──────────────────────────────────────────────
interface QueryTimelineProps {
    traceId: string;
}

const QueryTimeline: React.FC<QueryTimelineProps> = ({ traceId }) => {
    const [mode, setMode] = useState<'diagram' | 'timeline'>('diagram');
    const [activeScenario, setActiveScenario] = useState<string | null>(null);

    // Polling hook — refetches every 500ms while running
    const { data: trace, isLoading } = useQueryTrace(traceId);

    // Live WebSocket updates are already handled by the polling hook;
    // the WS hook here is a no-op callback so the WS connection is still opened
    // and future events arrive promptly.
    useTraceWebSocket(traceId);

    const scenarios = trace?.scenarios ?? [];
    const hasScenarios = scenarios.length > 1;

    const activeEvents: ExecutionEvent[] = useMemo(() => {
        if (!trace) return [];
        if (activeScenario) {
            const s = trace.scenarios.find((sc) => sc.scenarioId === activeScenario);
            return s?.events ?? trace.events;
        }
        return trace.events;
    }, [trace, activeScenario]);

    if (isLoading || !trace) {
        return (
            <Paper withBorder shadow="sm" radius="md" p="md">
                <Group justify="center">
                    <Loader size="sm" />
                    <Text c="dimmed" size="sm">
                        Loading execution trace…
                    </Text>
                </Group>
            </Paper>
        );
    }

    return (
        <Paper withBorder shadow="sm" radius="md" p="md">
            <Stack gap="md">
                {/* Header row */}
                <Group justify="space-between" wrap="nowrap">
                    <Group gap="sm">
                        <Text fw={700} size="lg">
                            Query Execution Trace
                        </Text>
                        <Badge
                            color={
                                trace.status === 'completed'
                                    ? 'green'
                                    : trace.status === 'failed'
                                      ? 'red'
                                      : 'yellow'
                            }
                            variant="light"
                        >
                            {trace.status}
                        </Badge>
                        <Badge color="blue" variant="light">
                            {trace.totalLayers} layer{trace.totalLayers !== 1 ? 's' : ''}
                        </Badge>
                        <Badge color="gray" variant="light">
                            {trace.events.length} event{trace.events.length !== 1 ? 's' : ''}
                        </Badge>
                    </Group>
                    <SegmentedControl
                        size="xs"
                        data={[
                            { label: 'Diagram', value: 'diagram' },
                            { label: 'Timeline', value: 'timeline' },
                        ]}
                        value={mode}
                        onChange={(v) => setMode(v as 'diagram' | 'timeline')}
                    />
                </Group>

                {/* Scenario tabs */}
                {hasScenarios && (
                    <Tabs
                        value={activeScenario ?? '__all__'}
                        onChange={(v) => setActiveScenario(v === '__all__' ? null : v)}
                    >
                        <Tabs.List>
                            <Tabs.Tab value="__all__">All Scenarios</Tabs.Tab>
                            {scenarios.map((s) => (
                                <Tabs.Tab key={s.scenarioId} value={s.scenarioId}>
                                    {s.label}
                                    <Badge
                                        size="xs"
                                        ml={4}
                                        color={
                                            s.status === 'completed'
                                                ? 'green'
                                                : s.status === 'failed'
                                                  ? 'red'
                                                  : 'yellow'
                                        }
                                        variant="dot"
                                    />
                                </Tabs.Tab>
                            ))}
                        </Tabs.List>
                    </Tabs>
                )}

                {/* Visualization */}
                {activeEvents.length === 0 ? (
                    <Text c="dimmed" size="sm" ta="center">
                        No events recorded yet.
                    </Text>
                ) : mode === 'diagram' ? (
                    <Diagram events={activeEvents} />
                ) : (
                    <TraceTimeline
                        trace={trace}
                        scenarioId={activeScenario ?? undefined}
                    />
                )}
            </Stack>
        </Paper>
    );
};

export default QueryTimeline;
