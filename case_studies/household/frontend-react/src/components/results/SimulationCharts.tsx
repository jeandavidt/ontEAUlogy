import React from 'react';
import { Paper, Text, Box, Stack, Group, ThemeIcon } from '@mantine/core';
import { IconChartBar, IconInfoCircle } from '@tabler/icons-react';

interface SimulationChartsProps {
    results?: Record<string, unknown>;
}

const SimulationCharts: React.FC<SimulationChartsProps> = ({ results }) => {
    if (!results || Object.keys(results).length === 0) {
        return (
            <Paper withBorder shadow="sm" radius="md" p="md">
                <Stack gap="md">
                    <Group>
                        <ThemeIcon size="lg" variant="light" color="blue">
                            <IconChartBar size={20} />
                        </ThemeIcon>
                        <Text fw={600}>Simulation Results</Text>
                    </Group>
                    <Box p="xl" style={{ textAlign: 'center' }}>
                        <ThemeIcon size="xl" variant="light" color="gray" mb="md">
                            <IconInfoCircle size={32} />
                        </ThemeIcon>
                        <Text c="dimmed">Run a simulation to view results.</Text>
                        <Text size="sm" c="dimmed">Results will appear here after a successful simulation run.</Text>
                    </Box>
                </Stack>
            </Paper>
        );
    }

    // Filter out non-primitive values and internal fields
    const displayResults = Object.entries(results).filter(([key, val]) => {
        return typeof val !== 'object' && !key.startsWith('_') && key !== 'job_id';
    });

    return (
        <Paper withBorder shadow="sm" radius="md" p="md">
            <Stack gap="md">
                <Group>
                    <ThemeIcon size="lg" variant="light" color="green">
                        <IconChartBar size={20} />
                    </ThemeIcon>
                    <Text fw={600}>Simulation Results</Text>
                </Group>

                <Box>
                    {displayResults.map(([key, val]) => (
                        <Group key={key} justify="space-between" py={8} style={{ borderBottom: '1px solid #eee' }}>
                            <Text size="sm" fw={500} tt="capitalize">
                                {key.replace(/_/g, ' ')}
                            </Text>
                            <Text size="sm" c="blue" fw={600}>
                                {String(val)}
                            </Text>
                        </Group>
                    ))}
                </Box>
            </Stack>
        </Paper>
    );
};

export default SimulationCharts;
