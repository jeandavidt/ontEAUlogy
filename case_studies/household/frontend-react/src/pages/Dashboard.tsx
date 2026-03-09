import React, { useState } from 'react';
import {
    Container,
    Stack,
    Title,
    Text,
    Paper,
    Group,
    ThemeIcon,
    Button,
    SimpleGrid,
    Box,
    Badge,
    Textarea,
    TextInput,
    Alert,
} from '@mantine/core';
import {
    IconHome,
    IconFilter,
    IconDroplet,
    IconArrowsExchange,
    IconArrowRight,
    IconNetwork,
    IconAlertCircle,
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import SystemTopology from '../components/SystemTopology';
import SPARQLSection from '../components/common/SPARQLSection';
import QueryTimeline from '../components/QueryTimeline';
import { useEntities, useModelStatus, useAgentCompose } from '../api/queries';

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const { data: entities = [] } = useEntities();

    // Agent composition state
    const [paramsJson, setParamsJson] = useState('{}');
    const [targetOutputs, setTargetOutputs] = useState('');
    const [lastTraceId, setLastTraceId] = useState<string | null>(null);
    const [jsonError, setJsonError] = useState<string | null>(null);
    const composeMutation = useAgentCompose();

    // Find entities by type - using proper type matching
    const mbrEntity = entities.find(e => {
        const type = e.type?.toLowerCase() || '';
        const id = e.id?.toLowerCase() || '';
        return type.includes('membrane') || type.includes('mbr') || id.includes('membrane') || id.includes('mbr');
    });
    
    const roEntity = entities.find(e => {
        const type = e.type?.toLowerCase() || '';
        const id = e.id?.toLowerCase() || '';
        return type.includes('osmosis') || type.includes('ro') || id.includes('osmosis') || id.includes('ro');
    });
    
    const infiltrationEntity = entities.find(e => {
        const type = e.type?.toLowerCase() || '';
        const id = e.id?.toLowerCase() || '';
        return type.includes('infiltration') || id.includes('infiltration');
    });

    // Check model status via API
    const { data: mbrStatus } = useModelStatus('mbr');
    const { data: roStatus } = useModelStatus('ro');
    const { data: infiltrationStatus } = useModelStatus('infiltration');

    const modelCards = [
        {
            id: 'mbr',
            title: 'MBR System',
            subtitle: 'Membrane Bioreactor',
            description: 'Greywater treatment and recycling',
            icon: IconFilter,
            color: 'blue',
            entity: mbrEntity,
            status: mbrStatus?.connected ? 'active' : 'not connected',
            path: '/mbr'
        },
        {
            id: 'ro',
            title: 'RO System',
            subtitle: 'Reverse Osmosis',
            description: 'Rainwater purification',
            icon: IconDroplet,
            color: 'cyan',
            entity: roEntity,
            status: roStatus?.connected ? 'active' : 'not connected',
            path: '/ro'
        },
        {
            id: 'infiltration',
            title: 'Infiltration System',
            subtitle: 'Soil Infiltration',
            description: 'Groundwater recharge',
            icon: IconArrowsExchange,
            color: 'green',
            entity: infiltrationEntity,
            status: infiltrationStatus?.connected ? 'active' : 'not connected',
            path: '/infiltration'
        }
    ];

    return (
        <Container size="xl" py="xl">
            <Stack gap="xl">
                {/* Header */}
                <Group justify="space-between" align="flex-start">
                    <Box>
                        <Group gap="xs" mb={4}>
                            <ThemeIcon size="xl" radius="xl" color="blue">
                                <IconHome size={28} />
                            </ThemeIcon>
                            <Title order={1}>Household Water System</Title>
                        </Group>
                        <Text c="dimmed" size="sm">
                            Manage and monitor your household water treatment and recycling systems
                        </Text>
                    </Box>
                    <Badge size="lg" color="green" variant="light">
                        System Active
                    </Badge>
                </Group>

                {/* System Topology - Derived from Knowledge Graph */}
                <SystemTopology height={450} />

                {/* Model Cards */}
                <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
                    {modelCards.map((card) => (
                        <Paper 
                            key={card.id}
                            withBorder 
                            shadow="sm" 
                            radius="md" 
                            p="md"
                            style={{ cursor: 'pointer' }}
                            onClick={() => navigate(card.path)}
                        >
                            <Stack gap="sm">
                                <Group justify="space-between">
                                    <ThemeIcon 
                                        size="lg" 
                                        radius="md" 
                                        color={card.color}
                                        variant="light"
                                    >
                                        <card.icon size={24} />
                                    </ThemeIcon>
                                    <Badge 
                                        color={card.status === 'active' ? 'green' : 'red'} 
                                        variant="light"
                                        size="sm"
                                    >
                                        {card.status === 'active' ? 'Active' : 'Not Connected'}
                                    </Badge>
                                </Group>
                                
                                <Box>
                                    <Text fw={700} size="lg">{card.title}</Text>
                                    <Text size="sm" c="dimmed">{card.subtitle}</Text>
                                </Box>
                                
                                <Text size="sm">{card.description}</Text>
                                
                                {card.entity && (
                                    <Text size="xs" c="dimmed">
                                        Entity: {card.entity.label} ({card.entity.type})
                                    </Text>
                                )}
                                
                                <Button 
                                    variant="light" 
                                    color={card.color}
                                    rightSection={<IconArrowRight size={16} />}
                                    fullWidth
                                >
                                    View Details
                                </Button>
                            </Stack>
                        </Paper>
                    ))}
                </SimpleGrid>

                {/* SPARQL Section */}
                <SPARQLSection />

                {/* Agent Composition Section */}
                <Paper withBorder shadow="sm" radius="md" p="md">
                    <Stack gap="md">
                        <Group gap="xs">
                            <ThemeIcon size="md" radius="md" color="violet" variant="light">
                                <IconNetwork size={18} />
                            </ThemeIcon>
                            <Text fw={700}>Agent Composition Explorer</Text>
                        </Group>
                        <Text size="sm" c="dimmed">
                            Compose and execute a chain of agents to answer a query. Provide initial
                            parameter values and the target outputs you want computed.
                        </Text>

                        <Textarea
                            label="Initial parameters (JSON)"
                            placeholder='{"hydraulic_load": 150, "temperature": 20}'
                            minRows={3}
                            value={paramsJson}
                            onChange={(e) => {
                                setParamsJson(e.currentTarget.value);
                                setJsonError(null);
                            }}
                            styles={{ input: { fontFamily: 'monospace', fontSize: 12 } }}
                            error={jsonError}
                        />

                        <TextInput
                            label="Target outputs (comma-separated)"
                            placeholder="effluent_cod, treatment_efficiency"
                            value={targetOutputs}
                            onChange={(e) => setTargetOutputs(e.currentTarget.value)}
                        />

                        <Button
                            leftSection={<IconNetwork size={16} />}
                            color="violet"
                            loading={composeMutation.isPending}
                            onClick={() => {
                                let params: Record<string, unknown>;
                                try {
                                    params = JSON.parse(paramsJson || '{}');
                                } catch {
                                    setJsonError('Invalid JSON');
                                    return;
                                }
                                const outputs = targetOutputs
                                    .split(',')
                                    .map((s) => s.trim())
                                    .filter(Boolean);
                                composeMutation.mutate(
                                    { initial_parameters: params, target_outputs: outputs },
                                    {
                                        onSuccess: (data) => {
                                            if (data.trace_id) setLastTraceId(data.trace_id);
                                        },
                                    },
                                );
                            }}
                        >
                            Run Agent Composition
                        </Button>

                        {composeMutation.error && (
                            <Alert
                                icon={<IconAlertCircle size={16} />}
                                color="red"
                                title="Composition failed"
                            >
                                {composeMutation.error.message}
                            </Alert>
                        )}
                    </Stack>
                </Paper>

                {/* Execution Trace Visualization */}
                {lastTraceId && <QueryTimeline traceId={lastTraceId} />}
            </Stack>
        </Container>
    );
};

export default Dashboard;
