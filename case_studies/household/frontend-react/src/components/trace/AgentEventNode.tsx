import React, { useState } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { Paper, Text, Badge, Stack, Group, Collapse, ActionIcon, Box } from '@mantine/core';
import { IconChevronDown, IconChevronUp } from '@tabler/icons-react';
import type { ExecutionEvent, EventParameter } from '../../api/types';
import KGNodeTooltip from './KGNodeTooltip';

export interface AgentEventNodeData {
    event: ExecutionEvent;
}

const AGENT_TYPE_COLORS: Record<string, string> = {
    llm: 'orange',
    model: 'teal',
    orchestrator: 'violet',
    user: 'gray',
    sparql: 'blue',
};

const AgentEventNode: React.FC<NodeProps<AgentEventNodeData>> = ({ data }) => {
    const [expanded, setExpanded] = useState(false);
    const { event } = data;

    const duration = event.endTime
        ? `${Math.round(new Date(event.endTime).getTime() - new Date(event.startTime).getTime())}ms`
        : 'running…';

    const typeColor = AGENT_TYPE_COLORS[event.agentType] ?? 'gray';
    const statusColor =
        event.status === 'completed' ? 'green' : event.status === 'failed' ? 'red' : 'yellow';

    return (
        <Paper
            withBorder
            shadow="xs"
            radius="md"
            p="xs"
            style={{
                width: 190,
                cursor: 'default',
                borderColor: event.status === 'failed' ? 'var(--mantine-color-red-5)' : undefined,
            }}
        >
            <Handle type="target" position={Position.Left} style={{ background: '#868e96' }} />

            <Stack gap={4}>
                <Group justify="space-between" wrap="nowrap" gap={4}>
                    <Text size="xs" fw={600} lineClamp={1} style={{ flex: 1 }}>
                        {event.agentName}
                    </Text>
                    <ActionIcon
                        size="xs"
                        variant="subtle"
                        color="gray"
                        onClick={(e) => {
                            e.stopPropagation();
                            setExpanded((v) => !v);
                        }}
                    >
                        {expanded ? <IconChevronUp size={11} /> : <IconChevronDown size={11} />}
                    </ActionIcon>
                </Group>

                <Group gap={4} wrap="nowrap">
                    <Badge size="xs" color={typeColor} variant="light">
                        {event.agentType}
                    </Badge>
                    <Badge size="xs" color={statusColor} variant="dot">
                        {duration}
                    </Badge>
                </Group>

                <Collapse in={expanded}>
                    <Stack gap={4} mt={4}>
                        {event.inputs.length > 0 && (
                            <Box>
                                <Text size="xs" c="dimmed" mb={2}>
                                    Inputs
                                </Text>
                                {event.inputs.map((p, i) => (
                                    <ParameterChip key={i} param={p} />
                                ))}
                            </Box>
                        )}
                        {event.outputs.length > 0 && (
                            <Box>
                                <Text size="xs" c="dimmed" mb={2}>
                                    Outputs
                                </Text>
                                {event.outputs.map((p, i) => (
                                    <ParameterChip key={i} param={p} />
                                ))}
                            </Box>
                        )}
                    </Stack>
                </Collapse>
            </Stack>

            <Handle type="source" position={Position.Right} style={{ background: '#868e96' }} />
        </Paper>
    );
};

const ParameterChip: React.FC<{ param: EventParameter }> = ({ param }) => {
    const label = `${param.name}${param.unit ? ` (${param.unit})` : ''}`;

    if (param.kgNodeUri) {
        return (
            <KGNodeTooltip uri={param.kgNodeUri} label={param.kgNodeLabel ?? param.name}>
                <Badge
                    size="xs"
                    variant="outline"
                    color="blue"
                    style={{ cursor: 'help', display: 'block', marginBottom: 2 }}
                >
                    {label}
                </Badge>
            </KGNodeTooltip>
        );
    }
    return (
        <Badge
            size="xs"
            variant="outline"
            color="gray"
            style={{ display: 'block', marginBottom: 2 }}
        >
            {label}
        </Badge>
    );
};

export default AgentEventNode;
