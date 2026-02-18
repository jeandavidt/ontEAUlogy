import React from 'react';
import { Paper, Title, Text, Code, Stack, Badge, Group, Accordion } from '@mantine/core';
import type { TraceNode } from '../../api/traceTypes';

interface NodeDetailsProps {
    node: TraceNode | null;
}

const agentTypeColors: Record<string, string> = {
    orchestrator: 'indigo',
    sparql: 'violet',
    simulation: 'green',
    optimization: 'orange',
    composition: 'pink',
    llm: 'blue',
};

export const NodeDetails: React.FC<NodeDetailsProps> = ({ node }) => {
    if (!node) {
        return (
            <Paper p="md" withBorder>
                <Text c="dimmed">Select a node from the timeline to view details</Text>
            </Paper>
        );
    }

    return (
        <Paper p="md" withBorder>
            <Stack gap="sm">
                <Group justify="space-between">
                    <Title order={4}>Agent Details</Title>
                    <Badge color={agentTypeColors[node.agent_type] || 'gray'}>
                        {node.agent_type}
                    </Badge>
                </Group>

                <Text><strong>Agent ID:</strong> {node.agent_id}</Text>
                <Text><strong>Timestamp:</strong> {new Date(node.timestamp).toLocaleString()}</Text>
                <Text><strong>Node ID:</strong> <Code>{node.node_id.slice(0, 8)}...</Code></Text>

                <Text fw={500} mt="sm">What I did:</Text>
                <Paper p="xs" withBorder bg="gray.0">
                    <Text size="sm">{node.processing}</Text>
                </Paper>

                <Accordion variant="separated" mt="sm">
                    <Accordion.Item value="inputs">
                        <Accordion.Control>What I received (inputs)</Accordion.Control>
                        <Accordion.Panel>
                            <Code block style={{ maxHeight: 200, overflow: 'auto' }}>
                                {JSON.stringify(node.inputs, null, 2)}
                            </Code>
                        </Accordion.Panel>
                    </Accordion.Item>

                    <Accordion.Item value="outputs">
                        <Accordion.Control>What I sent (outputs)</Accordion.Control>
                        <Accordion.Panel>
                            <Code block style={{ maxHeight: 200, overflow: 'auto' }}>
                                {JSON.stringify(node.outputs, null, 2)}
                            </Code>
                        </Accordion.Panel>
                    </Accordion.Item>
                </Accordion>
            </Stack>
        </Paper>
    );
};
