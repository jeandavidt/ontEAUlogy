import React, { useState } from 'react';
import { Container, Tabs, Paper, Group, Stack, Box } from '@mantine/core';
import { IconMap, IconHierarchy2 } from '@tabler/icons-react';
import WaterMap from '../components/map/WaterMap.tsx';
import WaterTopology from '../components/topology/WaterTopology.tsx';
import SimulationForm from '../components/simulation/SimulationForm.tsx';
import SimulationCharts from '../components/results/SimulationCharts.tsx';
import SPARQLSection from '../components/common/SPARQLSection.tsx';
import SensorVisualizer from '../components/common/SensorVisualizer.tsx';
import { useSelectionStore } from '../stores/useSelectionStore';
import { useEntityState } from '../api/queries';

const Dashboard: React.FC = () => {
    const [activeTab, setActiveTab] = useState<string | null>('map');
    const selectedEntityId = useSelectionStore((state) => state.selectedEntityId);
    const { data: entity } = useEntityState(selectedEntityId);

    return (
        <Container fluid>
            <Tabs value={activeTab} onChange={setActiveTab}>
                <Tabs.List mb="md">
                    <Tabs.Tab value="map" leftSection={<IconMap size={16} />}>
                        Geographic View
                    </Tabs.Tab>
                    <Tabs.Tab value="topology" leftSection={<IconHierarchy2 size={16} />}>
                        Logic View (DAG)
                    </Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="map">
                    <Group align="flex-start" grow>
                        <Paper withBorder shadow="sm" radius="md" h={600} style={{ position: 'relative', overflow: 'hidden', flex: 2 }}>
                            <WaterMap />
                        </Paper>
                        <Stack style={{ flex: 1 }}>
                            <Paper withBorder shadow="sm" radius="md">
                                <SimulationForm />
                            </Paper>
                            <Paper withBorder shadow="sm" radius="md">
                                <SimulationCharts />
                            </Paper>
                            {entity?.type === 'Sensor' && (
                                <SensorVisualizer sensorId={entity.id} label={entity.label} />
                            )}
                        </Stack>
                    </Group>
                </Tabs.Panel>

                <Tabs.Panel value="topology">
                    <Paper withBorder shadow="sm" radius="md" h={600} style={{ position: 'relative' }}>
                        <WaterTopology />
                    </Paper>
                </Tabs.Panel>
            </Tabs>

            <Box mt="md">
                <SPARQLSection />
            </Box>
        </Container>
    );
};

export default Dashboard;
