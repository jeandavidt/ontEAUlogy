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
import { Button, Box, Group, Text, Stack, Badge, Paper } from '@mantine/core';
import { IconRotateDot, IconPlus, IconMinus } from '@tabler/icons-react';
import * as d3 from 'd3';
import { useEntities, useRelationships } from '../api/queries';

// Type definitions for D3 force simulation
interface D3Node extends d3.SimulationNodeDatum {
    id: string;
    group: string;
    x?: number;
    y?: number;
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

// Define custom node and edge types
const nodeTypes: NodeTypes = {};
const edgeTypes: EdgeTypes = {};

// Helper to get Color for entity type
const getEntityColor = (type: string): string => {
    const lowerType = type.toLowerCase();
    if (lowerType.includes('membrane') || lowerType.includes('mbr')) return 'blue';
    if (lowerType.includes('osmosis') || lowerType.includes('ro')) return 'cyan';
    if (lowerType.includes('infiltration')) return 'green';
    if (lowerType.includes('storage') || lowerType.includes('tank')) return 'gray';
    if (lowerType.includes('fixture') || lowerType.includes('usage') || lowerType.includes('bathing') || lowerType.includes('cleaning')) return 'orange';
    if (lowerType.includes('rainwater')) return 'teal';
    if (lowerType.includes('blackwater')) return 'dark';
    return 'gray';
};

// Helper to get group for layout
const getEntityGroup = (id: string, type: string): string => {
    const lowerId = id.toLowerCase();
    const lowerType = type.toLowerCase();
    
    // Sources (left side)
    if (lowerId.includes('rainwater') && !lowerId.includes('storage')) return 'source';
    if (lowerType.includes('fixture') || lowerType.includes('usage') || lowerType.includes('bathing') || lowerType.includes('cleaning')) return 'source';
    
    // Treatment (center)
    if (lowerType.includes('membrane') || lowerType.includes('mbr')) return 'treatment';
    if (lowerType.includes('osmosis') || lowerType.includes('ro')) return 'treatment';
    
    // Storage (center-right)
    if (lowerType.includes('storage') || lowerType.includes('tank')) return 'storage';
    
    // Discharge (right)
    if (lowerType.includes('infiltration')) return 'discharge';
    
    return 'other';
};

interface SystemTopologyProps {
    height?: number;
    showControls?: boolean;
}

// Inner component that uses React Flow hooks
const SystemTopologyInner: React.FC<SystemTopologyProps> = ({ 
    height = 500,
    showControls = true 
}) => {
    const { data: entities, isLoading: loadingEntities } = useEntities();
    const { data: relationships, isLoading: loadingRels } = useRelationships();

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [neighborhoodDepth, setNeighborhoodDepth] = useState(3);
    const MIN_DEPTH = 1;
    const MAX_DEPTH = 5;

    // Calculate layout when data changes
    useEffect(() => {
        if (!entities || entities.length === 0 || !relationships) return;

        // Filter to neighborhood if selected
        let filteredEntities = entities;
        let filteredRels = relationships;

        if (selectedId) {
            const neighborhood = new Set<string>();
            neighborhood.add(selectedId);

            for (let depth = 0; depth < neighborhoodDepth; depth++) {
                const currentLevel = Array.from(neighborhood);
                relationships.forEach((rel) => {
                    if (currentLevel.includes(rel.source)) {
                        neighborhood.add(rel.target);
                    }
                    if (currentLevel.includes(rel.target)) {
                        neighborhood.add(rel.source);
                    }
                });
            }

            filteredEntities = entities.filter(e => neighborhood.has(e.id));
            filteredRels = relationships.filter(rel =>
                neighborhood.has(rel.source) && neighborhood.has(rel.target)
            );
        }

        // D3 Force Layout
        const d3Nodes: D3Node[] = filteredEntities.map(e => ({
            id: e.id,
            x: 0,
            y: 0,
            group: getEntityGroup(e.id, e.type),
        }));
        const d3Links: D3Link[] = filteredRels.map(r => ({ source: r.source, target: r.target }));

        // Create simulation with group-based positioning
        const simulation = d3.forceSimulation<D3Node>(d3Nodes)
            .force("link", d3.forceLink<D3Node, D3Link>(d3Links)
                .id((d) => d.id)
                .distance(() => 150)
            )
            .force("charge", d3.forceManyBody().strength(-600))
            .force("center", d3.forceCenter(450, 300))
            .force("collide", d3.forceCollide().radius(80).iterations(3))
            .force("x", d3.forceX<D3Node>((d) => {
                // Position by group
                const groupPositions: Record<string, number> = {
                    source: 100,
                    treatment: 300,
                    storage: 500,
                    discharge: 700,
                    other: 400
                };
                return groupPositions[d.group] || 400;
            }).strength(0.4))
            .force("y", d3.forceY<D3Node>(300).strength(0.1))
            .stop();

        for (let i = 0; i < 200; ++i) simulation.tick();

        // Create nodes
        const flowNodes: Node[] = filteredEntities.map((entity) => {
            const d3Node = d3Nodes.find(n => n.id === entity.id);
            const isSelected = entity.id === selectedId;
            const color = getEntityColor(entity.type);
            
            return {
                id: entity.id,
                data: { label: entity.label },
                position: { x: d3Node?.x || 0, y: d3Node?.y || 0 },
                style: {
                    background: isSelected ? '#e7f5ff' : '#ffffff',
                    border: isSelected ? '2px solid #228be6' : `2px solid var(--mantine-color-${color}-6)`,
                    borderRadius: '8px',
                    padding: '8px 12px',
                    width: 140,
                    fontSize: 11,
                    fontWeight: isSelected ? 600 : 400,
                    boxShadow: isSelected ? '0 0 0 2px rgba(34, 139, 230, 0.2)' : 'none',
                },
            };
        });

        // Create edges with arrows
        const flowEdges: Edge[] = filteredRels.map((rel, index) => {
            const isSelectedEdge = rel.source === selectedId || rel.target === selectedId;
            return {
                id: `e-${index}`,
                source: rel.source,
                target: rel.target,
                label: rel.label,
                type: 'default',
                animated: isSelectedEdge,
                style: isSelectedEdge ? EDGE_ANIMATED_STYLE : EDGE_STYLE,
                labelStyle: { fill: '#495057', fontWeight: 500, fontSize: 10, fontFamily: 'system-ui' },
                labelBgStyle: { fill: 'rgba(255, 255, 255, 0.9)', fillOpacity: 0.9, rx: 4 },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: isSelectedEdge ? '#228be6' : '#495057',
                    width: 14,
                    height: 14,
                },
                curvature: 0.15,
            };
        });

        setNodes(flowNodes);
        setEdges(flowEdges);
    }, [entities, relationships, selectedId, neighborhoodDepth, setNodes, setEdges]);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds: Edge[]) => addEdge({ ...params, type: ConnectionLineType.SmoothStep }, eds)),
        [setEdges]
    );

    const memoizedNodeTypes = useMemo(() => nodeTypes, []);
    const memoizedEdgeTypes = useMemo(() => edgeTypes, []);

    const reactFlowProps: Partial<ReactFlowProps> = useMemo(() => ({
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        onConnect,
        onNodeClick: (_: React.MouseEvent, node: Node) => setSelectedId(node.id),
        fitView: true,
        fitViewOptions: { padding: 0.2 },
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
                width: 12,
                height: 12,
            },
        },
    }), [nodes, edges, onNodesChange, onEdgesChange, onConnect, memoizedNodeTypes, memoizedEdgeTypes]);

    if (loadingEntities || loadingRels) {
        return (
            <Paper withBorder shadow="sm" radius="md" p="md">
                <Text c="dimmed" ta="center">Loading system topology from knowledge graph...</Text>
            </Paper>
        );
    }

    if (!entities || entities.length === 0) {
        return (
            <Paper withBorder shadow="sm" radius="md" p="md">
                <Text c="dimmed" ta="center">No entities found in knowledge graph.</Text>
            </Paper>
        );
    }

    return (
        <Paper withBorder shadow="sm" radius="md" p="md">
            <Stack gap="md">
                <Group justify="space-between">
                    <Group>
                        <Text fw={700} size="lg">Household Water System</Text>
                        <Badge color="blue" variant="light">
                            {entities.length} entities
                        </Badge>
                        <Badge color="cyan" variant="light">
                            {relationships?.length || 0} flows
                        </Badge>
                    </Group>
                </Group>

                <Text size="sm" c="dimmed">
                    Visualization derived from knowledge graph flow relationships (wf:flowsTo)
                </Text>

                {showControls && (
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
                        {selectedId && (
                            <Button
                                variant="light"
                                size="xs"
                                leftSection={<IconRotateDot size={14} />}
                                onClick={() => setSelectedId(null)}
                            >
                                Reset Selection
                            </Button>
                        )}
                    </Group>
                )}

                <div style={{ height, width: '100%', border: '1px solid #e9ecef', borderRadius: 8 }}>
                    <ReactFlow {...reactFlowProps}>
                        <Background color="#f1f3f5" gap={20} />
                        <Controls />
                    </ReactFlow>
                </div>

                {/* Legend */}
                <Group gap="md" justify="center">
                    <Group gap={4}>
                        <Box w={12} h={12} style={{ backgroundColor: 'var(--mantine-color-blue-6)', borderRadius: 4 }} />
                        <Text size="xs">MBR Treatment</Text>
                    </Group>
                    <Group gap={4}>
                        <Box w={12} h={12} style={{ backgroundColor: 'var(--mantine-color-cyan-6)', borderRadius: 4 }} />
                        <Text size="xs">RO Purification</Text>
                    </Group>
                    <Group gap={4}>
                        <Box w={12} h={12} style={{ backgroundColor: 'var(--mantine-color-green-6)', borderRadius: 4 }} />
                        <Text size="xs">Infiltration</Text>
                    </Group>
                    <Group gap={4}>
                        <Box w={12} h={12} style={{ backgroundColor: 'var(--mantine-color-gray-6)', borderRadius: 4 }} />
                        <Text size="xs">Storage</Text>
                    </Group>
                    <Group gap={4}>
                        <Box w={12} h={12} style={{ backgroundColor: 'var(--mantine-color-orange-6)', borderRadius: 4 }} />
                        <Text size="xs">Usage Points</Text>
                    </Group>
                </Group>
            </Stack>
        </Paper>
    );
};

// Wrapper component with ReactFlowProvider
const SystemTopology: React.FC<SystemTopologyProps> = (props) => {
    return (
        <ReactFlowProvider>
            <SystemTopologyInner {...props} />
        </ReactFlowProvider>
    );
};

export default SystemTopology;
