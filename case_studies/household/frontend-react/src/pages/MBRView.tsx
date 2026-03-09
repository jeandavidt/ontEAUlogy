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
    IconFilter,
    IconArrowLeft,
    IconInfoCircle,
    IconSettings
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import SimulationForm from '../components/simulation/SimulationForm';
import SimulationCharts from '../components/results/SimulationCharts';
import { useEntities, useEntityTriplets } from '../api/queries';

const MBRView: React.FC = () => {
    const navigate = useNavigate();
    const { data: entities = [] } = useEntities();

    // Find MBR entity
    const mbrEntity = entities.find(e =>
        e.type.toLowerCase().includes('membrane') ||
        e.type.toLowerCase().includes('mbr')
    );

    const { data: triplets = [] } = useEntityTriplets(mbrEntity?.id || null);

    // MBR specifications (example data)
    const specifications = [
        { property: 'Treatment Capacity', value: '100-500 L/day', unit: '' },
        { property: 'Membrane Type', value: 'Hollow Fiber', unit: '' },
        { property: 'Pore Size', value: '0.1', unit: 'μm' },
        { property: 'Operating Pressure', value: '0.1-0.3', unit: 'bar' },
        { property: 'Recovery Rate', value: '85-95', unit: '%' },
        { property: 'Power Consumption', value: '0.5-1.2', unit: 'kWh/m³' },
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
                    <ThemeIcon size="xl" radius="xl" color="blue" variant="light">
                        <IconFilter size={28} />
                    </ThemeIcon>
                    <Box>
                        <Title order={2}>MBR System</Title>
                        <Text c="dimmed" size="sm">Membrane Bioreactor - Greywater Treatment</Text>
                    </Box>
                    <Badge color="green" variant="light" ml="auto">
                        {mbrEntity ? 'Active' : 'Not Connected'}
                    </Badge>
                </Group>

                <Grid>
                    {/* Left Column - Info & Simulation */}
                    <Grid.Col span={{ base: 12, md: 7 }}>
                        <Stack gap="md">
                            {/* Description */}
                            <Paper withBorder shadow="sm" radius="md" p="md">
                                <Group mb="md">
                                    <ThemeIcon size="lg" variant="light" color="blue">
                                        <IconInfoCircle size={20} />
                                    </ThemeIcon>
                                    <Text fw={600}>System Overview</Text>
                                </Group>
                                <Text size="sm">
                                    The Membrane Bioreactor (MBR) system treats greywater from showers, 
                                    sinks, and washing machines. It uses membrane filtration to separate 
                                    treated water from biomass, producing high-quality effluent suitable 
                                    for reuse in toilet flushing, irrigation, and other non-potable applications.
                                </Text>
                            </Paper>

                            {/* Specifications */}
                            <Paper withBorder shadow="sm" radius="md" p="md">
                                <Group mb="md">
                                    <ThemeIcon size="lg" variant="light" color="blue">
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
                                        <ThemeIcon size="lg" variant="light" color="blue">
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
                            {mbrEntity && (
                                <SimulationForm
                                    entityId={mbrEntity.id}
                                    entityName={mbrEntity.label}
                                    entityType={mbrEntity.type}
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

export default MBRView;
