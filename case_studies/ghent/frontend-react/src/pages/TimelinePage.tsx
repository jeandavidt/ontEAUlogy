import React, { useState } from 'react';
import { Container, Grid, Title, Text, Paper } from '@mantine/core';
import { AgentTimeline, NodeDetails, TraceList } from './components/timeline';
import { useExecutionTraces, useTraceGraph, useTraceDetail } from './api/traceQueries';
import type { TraceNode } from './api/traceTypes';

const TimelinePage: React.FC = () => {
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

    const { data: traces = [] } = useExecutionTraces(50);
    const { data: traceGraph } = useTraceGraph(selectedTraceId);
    const { data: traceDetail } = useTraceDetail(selectedTraceId);

    const handleSelectTrace = (traceId: string) => {
        setSelectedTraceId(traceId);
        setSelectedNodeId(null);
    };

    const handleNodeClick = (nodeId: string) => {
        setSelectedNodeId(nodeId);
    };

    const selectedNode: TraceNode | null = traceDetail?.nodes
        ? traceDetail.nodes.find(n => n.node_id === selectedNodeId) || null
        : null;

    return (
        <Container fluid p="md">
            <Title order={2} mb="md">Agent Execution Timeline</Title>
            <Text c="dimmed" mb="lg">
                Visualize agent interactions and trace how queries flow through the system.
                Click on a trace to see the execution timeline, then click on nodes to see details.
            </Text>

            <Grid>
                <Grid.Col span={12}>
                    <TraceList
                        traces={traces}
                        onSelectTrace={handleSelectTrace}
                        selectedTraceId={selectedTraceId || undefined}
                    />
                </Grid.Col>

                {traceGraph && (
                    <Grid.Col span={12}>
                        <Paper p="md" withBorder>
                            <Title order={4} mb="sm">Execution Flow</Title>
                            <AgentTimeline
                                traceGraph={traceGraph}
                                onNodeClick={handleNodeClick}
                                selectedNodeId={selectedNodeId || undefined}
                            />
                        </Paper>
                    </Grid.Col>
                )}

                <Grid.Col span={{ base: 12, md: 6 }}>
                    <NodeDetails node={selectedNode} />
                </Grid.Col>
            </Grid>
        </Container>
    );
};

export default TimelinePage;
