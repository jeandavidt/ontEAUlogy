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
    IconArrowsExchange,
    IconArrowLeft,
    IconInfoCircle,
    IconSettings
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import SimulationForm from '../components/simulation/SimulationForm';
import SimulationCharts from '../components/results/SimulationCharts';
import { useEntities, useEntityTriplets } from '../api/queries';

const InfiltrationView: React.FC = () => {
    const navigate = useNavigate();
    const { data: entities = [] } = useEntities();
    
    // Find Infiltration entity
    const infiltrationEntity = entities.find(e =>
        e.type.toLowerCase().includes('infiltration')
    );
    
    const { data: triplets = [] } = useEntityTriplets(infiltrationEntity?.id || null);

    // Infiltration specifications
    const specifications = [
        { property: 'Design Flow', value: '0-100 L/day', unit: '' },
        { property: 'Infiltration Rate', value: '10-50', unit: 'mm/h' },
        { property: 'Soil Type', value: 'Sandy Loam', unit: '' },
        { property: 'Depth', value: '1.0-1.5', unit: 'm' },
        { property: 'Surface Area', value: '10-20', unit: 'm²' },
        { property: 'Retention Time', value: '12-24', unit: 'h' },
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
                    <ThemeIcon size="xl" radius="xl" color="green" variant="light">
                        <IconArrowsExchange size={28} />
                    </ThemeIcon>
                    <Box>
                        <Title order={2}>Infiltration System</Title>
                        <Text c="dimmed" size="sm">Soil Infiltration - Groundwater Recharge</Text>
                    </Box>
                    <Badge color="green" variant="light" ml="auto">
                        {infiltrationEntity ? 'Active' : 'Not Connected'}
                    </Badge>
                </Group>

                <Grid>
                    {/* Left Column - Info & Simulation */}
                    <Grid.Col span={{ base: 12, md: 7 }}>
                        <Stack gap="md">
                            {/* Description */}
                            <Paper withBorder shadow="sm" radius="md" p="md">
                                <Group mb="md">
                                    <ThemeIcon size="lg" variant="light" color="green">
                                        <IconInfoCircle size={20} />
                                    </ThemeIcon>
                                    <Text fw={600}>System Overview</Text>
                                </Group>
                                <Text size="sm">
                                    The Infiltration System manages excess water that cannot be treated 
                                    or stored by discharging it into the soil. This promotes groundwater 
                                    recharge, reduces stormwater runoff, and helps maintain natural 
                                    hydrological cycles. The system includes monitoring of infiltration 
                                    rates and soil saturation levels.
                                </Text>
                            </Paper>

                            {/* Specifications */}
                            <Paper withBorder shadow="sm" radius="md" p="md">
                                <Group mb="md">
                                    <ThemeIcon size="lg" variant="light" color="green">
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
                                        <ThemeIcon size="lg" variant="light" color="green">
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
                            {infiltrationEntity && (
                                <SimulationForm 
                                    entityId={infiltrationEntity.id}
                                    entityName={infiltrationEntity.label}
                                    entityType={infiltrationEntity.type}
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

export default InfiltrationView;
