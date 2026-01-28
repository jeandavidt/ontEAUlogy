import React, { useEffect, useCallback, useMemo, useState } from 'react';
import ReactFlow, {
    Background,
    Controls,
    useNodesState,
    useEdgesState,
    addEdge,
    MarkerType,
    type Node,
    type Edge,
    type Connection,
    type ReactFlowProps,
    type NodeTypes,
    type EdgeTypes,
    ConnectionLineType,
    ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useEntities, useRelationships } from '../../api/queries';
import { useSelectionStore } from '../../stores/useSelectionStore';
import { Button, Box, Group, Text, Stack, Badge } from '@mantine/core';
import { IconRotateDot, IconPlus, IconMinus } from '@tabler/icons-react';
import type { Relationship } from '../../api/types';
import * as d3 from 'd3';
import { Breadcrumbs } from './Breadcrumbs';

// Define custom node and edge types (empty for now, but defined to avoid recreation)
const nodeTypes: NodeTypes = {};
const edgeTypes: EdgeTypes = {};

// Type definitions for D3 force simulation
interface D3Node extends d3.SimulationNodeDatum {
    id: string;
    group: string;
}

interface D3Link extends d3.SimulationLinkDatum<D3Node> {
    source: string | D3Node;
    target: string | D3Node;
}

// Custom edge styles for better visibility
const EDGE_STYLE = {
    stroke: '#495057',
    strokeWidth: 2,
    strokeOpacity: 0.8,
};

const EDGE_ANIMATED_STYLE = {
    stroke: '#228be6',
    strokeWidth: 2,
    strokeOpacity: 0.9,
};

// Inner component that uses React Flow hooks
const WaterTopologyInner: React.FC = () => {
    const { data: entities, isLoading: loadingEntities } = useEntities();
    const { data: relationships, isLoading: loadingRels } = useRelationships();

    const selectedEntityId = useSelectionStore((state) => state.selectedEntityId);
    const topologyAnchorId = useSelectionStore((state) => state.topologyAnchorId);
    const setTopologyAnchorId = useSelectionStore((state) => state.setTopologyAnchorId);
    const resetTopologyAnchor = useSelectionStore((state) => state.resetTopologyAnchor);

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [neighborhoodDepth, setNeighborhoodDepth] = useState(2);
    const MIN_DEPTH = 1;
    const MAX_DEPTH = 5;

    // Calculate neighborhood and initial layout when anchor or data changes
    useEffect(() => {
        if (!entities || !relationships || !topologyAnchorId) return;

        // Calculate neighborhood with configurable depth
        const neighborhood = new Set<string>();
        neighborhood.add(topologyAnchorId);

        // BFS traversal up to neighborhoodDepth
        for (let depth = 0; depth < neighborhoodDepth; depth++) {
            const currentLevel = Array.from(neighborhood);
            relationships.forEach((rel: Relationship) => {
                if (currentLevel.includes(rel.source)) {
                    neighborhood.add(rel.target);
                }
                if (currentLevel.includes(rel.target)) {
                    neighborhood.add(rel.source);
                }
            });
        }

        const filteredEntities = entities.filter(e => neighborhood.has(e.id));
        const filteredRels = relationships.filter((rel: Relationship) =>
            neighborhood.has(rel.source) && neighborhood.has(rel.target)
        );

        // --- D3 Force Layout with collision detection and improved spacing ---
        const d3Nodes = filteredEntities.map(e => ({
            id: e.id,
            x: 0,
            y: 0,
            // Group nodes by type for better clustering
            group: e.id.includes('residential') ? 'residential' :
                   e.id.includes('industry') ? 'industry' :
                   e.id.includes('dwp') ? 'dwp' :
                   e.id.includes('wwtp') ? 'wwtp' :
                   e.id.includes('river') ? 'river' : 'other'
        }));
        const d3Links = filteredRels.map(r => ({ source: r.source, target: r.target }));

        // Create the simulation with multiple forces
        const simulation = d3.forceSimulation<D3Node>(d3Nodes)
            // Link force with variable distance based on relationship
            .force("link", d3.forceLink<D3Node, D3Link>(d3Links)
                .id((d) => d.id)
                .distance(() => 180)
            )
            // Charge force for repulsion (nodes push each other apart)
            .force("charge", d3.forceManyBody().strength(-800))
            // Center force to keep graph in view
            .force("center", d3.forceCenter(400, 300))
            // Collision detection to prevent overlapping
            .force("collide", d3.forceCollide().radius(100).iterations(3))
            // Force to spread out nodes horizontally based on groups
            .force("x", d3.forceX<D3Node>((d) => {
                const groupPositions: Record<string, number> = {
                    residential: 100,
                    industry: 250,
                    dwp: 400,
                    wwtp: 550,
                    river: 700,
                    other: 400
                };
                return groupPositions[d.group] || 400;
            }).strength(0.3))
            .force("y", d3.forceY<D3Node>(300).strength(0.1))
            .stop();

        // Run simulation for more ticks to get better positions
        for (let i = 0; i < 200; ++i) simulation.tick();

        const flowNodes: Node[] = filteredEntities.map((entity) => {
            const d3Node = d3Nodes.find(n => n.id === entity.id);
            const isAnchor = entity.id === topologyAnchorId;
            return {
                id: entity.id,
                data: { label: entity.label },
                position: { x: d3Node?.x || 0, y: d3Node?.y || 0 },
                style: {
                    background: isAnchor ? '#e7f5ff' : '#ffffff',
                    border: isAnchor ? '2px solid #228be6' : '1px solid #adb5bd',
                    borderRadius: '8px',
                    padding: '10px',
                    width: 160,
                    fontSize: 12,
                    fontWeight: isAnchor ? 600 : 400,
                    boxShadow: isAnchor ? '0 0 0 2px rgba(34, 139, 230, 0.2)' : 'none',
                },
            };
        });

        // Create edges with arrow markers for directionality
        const flowEdges: Edge[] = filteredRels.map((rel: Relationship) => {
            const isAnchorEdge = rel.source === topologyAnchorId || rel.target === topologyAnchorId;
            return {
                id: `e-${rel.id || Math.random()}`,
                source: rel.source,
                target: rel.target,
                label: rel.label,
                type: 'default',
                animated: isAnchorEdge,
                style: isAnchorEdge ? EDGE_ANIMATED_STYLE : EDGE_STYLE,
                labelStyle: { fill: '#495057', fontWeight: 500, fontSize: 11, fontFamily: 'system-ui' },
                labelBgStyle: { fill: 'rgba(255, 255, 255, 0.8)', fillOpacity: 0.8, rx: 4 },
                // Arrow marker pointing from source to target (downstream direction)
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: isAnchorEdge ? '#228be6' : '#495057',
                    width: 16,
                    height: 16,
                },
                // Curved edges to reduce visual overlap
                curvature: 0.2,
            };
        });

        // Debug logging
        console.log('Topology Debug:', {
            topologyAnchorId,
            neighborhoodSize: neighborhood.size,
            neighborhoodDepth,
            filteredEntitiesCount: filteredEntities.length,
            filteredRelsCount: filteredRels.length,
            nodesGenerated: flowNodes.length,
            edgesGenerated: flowEdges.length,
            allRelationshipsCount: relationships?.length
        });

        setNodes(flowNodes);
        setEdges(flowEdges);
    }, [entities, relationships, topologyAnchorId, neighborhoodDepth, setNodes, setEdges]);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge({ ...params, type: ConnectionLineType.SmoothStep }, eds)),
        [setEdges]
    );

    // Memoize nodeTypes and edgeTypes to avoid recreation warnings
    const memoizedNodeTypes = useMemo(() => nodeTypes, []);
    const memoizedEdgeTypes = useMemo(() => edgeTypes, []);

    // Memoize ReactFlow props to avoid recreation on each render
    const reactFlowProps: Partial<ReactFlowProps> = useMemo(() => ({
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        onConnect,
        onNodeClick: (_, node) => setTopologyAnchorId(node.id),
        fitView: true,
        fitViewOptions: { padding: 0.25 },
        style: { width: '100%', height: '100%' },
        proOptions: { hideAttribution: true },
        nodeTypes: memoizedNodeTypes,
        edgeTypes: memoizedEdgeTypes,
        snapToGrid: false,
        defaultEdgeOptions: {
            type: 'smoothstep',
            markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#495057',
                width: 14,
                height: 14,
            },
        },
    }), [nodes, edges, onNodesChange, onEdgesChange, onConnect, setTopologyAnchorId, memoizedNodeTypes, memoizedEdgeTypes]);

    if (loadingEntities || loadingRels) return <div>Loading Topology...</div>;
    if (!topologyAnchorId) return <Box p="md"><Text c="dimmed">Select an entity on the map to view the layout.</Text></Box>;

    return (
        <div style={{ height: '100%', width: '100%', position: 'relative', minHeight: 600 }}>
            <Stack style={{ position: 'absolute', top: 10, left: 10, right: 10, zIndex: 10 }} gap="xs">
                <Breadcrumbs />
                <Group justify="space-between">
                    <Group gap="xs">
                        <Button
                            variant="light"
                            size="xs"
                            leftSection={<IconMinus size={12} />}
                            onClick={() => setNeighborhoodDepth(Math.max(MIN_DEPTH, neighborhoodDepth - 1))}
                            disabled={neighborhoodDepth <= MIN_DEPTH}
                        >
                            Less
                        </Button>
                        <Badge variant="light" size="lg">
                            Depth: {neighborhoodDepth}
                        </Badge>
                        <Button
                            variant="light"
                            size="xs"
                            rightSection={<IconPlus size={12} />}
                            onClick={() => setNeighborhoodDepth(Math.min(MAX_DEPTH, neighborhoodDepth + 1))}
                            disabled={neighborhoodDepth >= MAX_DEPTH}
                        >
                            More
                        </Button>
                    </Group>
                    <Group gap="xs">
                        <Button
                            variant="light"
                            size="xs"
                            leftSection={<IconRotateDot size={14} />}
                            onClick={resetTopologyAnchor}
                            disabled={topologyAnchorId === selectedEntityId}
                        >
                            Reset
                        </Button>
                    </Group>
                </Group>
            </Stack>

            <div style={{ width: '100%', height: '100%', minHeight: 550 }}>
                <ReactFlow
                    {...reactFlowProps}
                >
                    <Background color="#f1f3f5" gap={20} />
                    <Controls />
                </ReactFlow>
            </div>
        </div>
    );
};

// Wrapper component with ReactFlowProvider for proper context
const WaterTopology: React.FC = () => {
    return (
        <ReactFlowProvider>
            <WaterTopologyInner />
        </ReactFlowProvider>
    );
};

export default WaterTopology;
