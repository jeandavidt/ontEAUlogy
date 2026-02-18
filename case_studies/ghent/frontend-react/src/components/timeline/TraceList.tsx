import React from 'react';
import { Paper, Table, Text, Badge, ActionIcon, Group, Stack } from '@mantine/core';
import { IconEye } from '@tabler/icons-react';
import type { TraceSummary } from '../../api/traceTypes';

interface TraceListProps {
    traces: TraceSummary[];
    onSelectTrace: (traceId: string) => void;
    selectedTraceId?: string;
}

const statusColors: Record<string, string> = {
    running: 'yellow',
    completed: 'green',
    failed: 'red',
};

export const TraceList: React.FC<TraceListProps> = ({ traces, onSelectTrace, selectedTraceId }) => {
    if (traces.length === 0) {
        return (
            <Paper p="md" withBorder>
                <Text c="dimmed">No execution traces found. Run a query or simulation to generate traces.</Text>
            </Paper>
        );
    }

    return (
        <Paper p="md" withBorder>
            <Stack gap="sm">
                <Text fw={500}>Recent Executions</Text>
                <Table striped highlightOnHover>
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>Root Agent</Table.Th>
                            <Table.Th>Started</Table.Th>
                            <Table.Th>Status</Table.Th>
                            <Table.Th></Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {traces.map((trace) => (
                            <Table.Tr 
                                key={trace.trace_id}
                                bg={selectedTraceId === trace.trace_id ? 'blue.0' : undefined}
                            >
                                <Table.Td>
                                    <Text size="sm">{trace.root_agent}</Text>
                                </Table.Td>
                                <Table.Td>
                                    <Text size="sm" c="dimmed">
                                        {new Date(trace.started_at).toLocaleString()}
                                    </Text>
                                </Table.Td>
                                <Table.Td>
                                    <Badge color={statusColors[trace.status] || 'gray'} size="sm">
                                        {trace.status}
                                    </Badge>
                                </Table.Td>
                                <Table.Td>
                                    <Group gap="xs" justify="flex-end">
                                        <ActionIcon 
                                            variant="subtle" 
                                            onClick={() => onSelectTrace(trace.trace_id)}
                                            title="View trace"
                                        >
                                            <IconEye size={16} />
                                        </ActionIcon>
                                    </Group>
                                </Table.Td>
                            </Table.Tr>
                        ))}
                    </Table.Tbody>
                </Table>
            </Stack>
        </Paper>
    );
};
