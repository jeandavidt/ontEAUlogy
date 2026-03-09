import React from 'react';
import {
    Container,
    Stack,
    Title,
    Text,
    Paper,
    Group,
    ThemeIcon,
    Button,
    Grid,
    Box,
    Badge,
    Table,
    ScrollArea
} from '@mantine/core';
import {
    IconDroplet,
    IconArrowLeft,
    IconInfoCircle,
    IconSettings
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import SimulationForm from '../components/simulation/SimulationForm';
import SimulationCharts from '../components/results/SimulationCharts';
import { useEntities, useEntityTriplets } from '../api/queries';

const ROView: React.FC = () => {
    const navigate = useNavigate();
    const { data: entities = [] } = useEntities();
    
    // Find RO entity
    const roEntity = entities.find(e =>
        e.type.toLowerCase().includes('osmosis') ||
        e.type.toLowerCase().includes('ro')
    );
    
    const { data: triplets = [] } = useEntityTriplets(roEntity?.id || null);

    // RO specifications
    const specifications = [
        { property: 'Treatment Capacity', value: '50-200 L/day', unit: '' },
        { property: 'Membrane Type', value: 'Thin Film Composite', unit: '' },
        { property: 'Rejection Rate', value: '95-99', unit: '%' },
        { property: 'Operating Pressure', value: '3-8', unit: 'bar' },
        { property: 'Recovery Rate', value: '50-75', unit: '%' },
        { property: 'Power Consumption', value: '1.5-3.0', unit: 'kWh/m³' },
    ];

    return (
        <Container size="xl" py="xl">
            <Stack gap="xl">
                {/* Header */}
                <Group justify="space-between">
                    <Group>
                        <Button 
                            variant="subtle" 
                            leftSection={<IconArrowLeft size={16} />}
                            onClick={() => navigate('/')}
                        >
                            Back to Dashboard
                        </Button>
                    </Group>
                </Group>

                <Group gap="xs">
                    <ThemeIcon size="xl" radius="xl" color="cyan" variant="light">
                        <IconDroplet size={28} />
                    </ThemeIcon>
                    <Box>
                        <Title order={2}>RO System</Title>
                        <Text c="dimmed" size="sm">Reverse Osmosis - Rainwater Purification</Text>
                    </Box>
                    <Badge color="green" variant="light" ml="auto">
                        {roEntity ? 'Active' : 'Not Connected'}
                    </Badge>
                </Group>

                <Grid>
                    {/* Left Column - Info & Simulation */}
                    <Grid.Col span={{ base: 12, md: 7 }}>
                        <Stack gap="md">
                            {/* Description */}
                            <Paper withBorder shadow="sm" radius="md" p="md">
                                <Group mb="md">
                                    <ThemeIcon size="lg" variant="light" color="cyan">
                                        <IconInfoCircle size={20} />
                                    </ThemeIcon>
                                    <Text fw={600}>System Overview</Text>
                                </Group>
                                <Text size="sm">
                                    The Reverse Osmosis (RO) system purifies rainwater collected from roofs 
                                    and surfaces. It uses a semi-permeable membrane to remove dissolved salts, 
                                    contaminants, and impurities, producing high-quality drinking water or 
                                    water for sensitive applications like aquariums and humidifiers.
                                </Text>
                            </Paper>

                            {/* Specifications */}
                            <Paper withBorder shadow="sm" radius="md" p="md">
                                <Group mb="md">
                                    <ThemeIcon size="lg" variant="light" color="cyan">
                                        <IconSettings size={20} />
                                    </ThemeIcon>
                                    <Text fw={600}>Specifications</Text>
                                </Group>
                                <Table>
                                    <Table.Tbody>
                                        {specifications.map((spec, i) => (
                                            <Table.Tr key={i}>
                                                <Table.Td fw={500}>{spec.property}</Table.Td>
                                                <Table.Td ta="right">
                                                    {spec.value} {spec.unit}
                                                </Table.Td>
                                            </Table.Tr>
                                        ))}
                                    </Table.Tbody>
                                </Table>
                            </Paper>

                            {/* Ontology Triplets */}
                            {triplets.length > 0 && (
                                <Paper withBorder shadow="sm" radius="md" p="md">
                                    <Group mb="md">
                                        <ThemeIcon size="lg" variant="light" color="cyan">
                                            <IconInfoCircle size={20} />
                                        </ThemeIcon>
                                        <Text fw={600}>Ontology Data</Text>
                                    </Group>
                                    <ScrollArea h={200}>
                                        <Table>
                                            <Table.Thead>
                                                <Table.Tr>
                                                    <Table.Th>Subject</Table.Th>
                                                    <Table.Th>Predicate</Table.Th>
                                                    <Table.Th>Object</Table.Th>
                                                </Table.Tr>
                                            </Table.Thead>
                                            <Table.Tbody>
                                                {triplets.slice(0, 10).map((t, i) => (
                                                    <Table.Tr key={i}>
                                                        <Table.Td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                            {t.subject.split('#').pop() || t.subject}
                                                        </Table.Td>
                                                        <Table.Td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                            {t.predicate.split('#').pop() || t.predicate}
                                                        </Table.Td>
                                                        <Table.Td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                            {t.object.split('#').pop() || t.object}
                                                        </Table.Td>
                                                    </Table.Tr>
                                                ))}
                                            </Table.Tbody>
                                        </Table>
                                    </ScrollArea>
                                </Paper>
                            )}
                        </Stack>
                    </Grid.Col>

                    {/* Right Column - Simulation */}
                    <Grid.Col span={{ base: 12, md: 5 }}>
                        <Stack gap="md">
                            {roEntity && (
                                <SimulationForm 
                                    entityId={roEntity.id}
                                    entityName={roEntity.label}
                                    entityType={roEntity.type}
                                />
                            )}
                            <SimulationCharts />
                        </Stack>
                    </Grid.Col>
                </Grid>
            </Stack>
        </Container>
    );
};

export default ROView;
