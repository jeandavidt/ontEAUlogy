import React, { useState } from 'react';
import { 
    Stack, 
    NumberInput, 
    Button, 
    Title, 
    Text, 
    Group, 
    LoadingOverlay, 
    Alert, 
    Badge, 
    Progress,
    Paper,
    Box
} from '@mantine/core';
import { IconAlertCircle, IconCheck, IconPlayerPlay } from '@tabler/icons-react';
import { useRunSimulation, useJobStatus } from '../../api/queries';

interface SimulationFormProps {
    entityId: string;
    entityName: string;
    entityType: string;
}

const SimulationForm: React.FC<SimulationFormProps> = ({ entityId, entityName, entityType }) => {
    const [flowRate, setFlowRate] = useState<number>(100);
    const [startedJobId, setStartedJobId] = useState<string | null>(null);
    
    const { mutate: runSimulation, isPending: isStarting, error: startError } = useRunSimulation();
    const { data: jobStatus } = useJobStatus(startedJobId);

    const handleRun = () => {
        setStartedJobId(null);
        runSimulation(
            { 
                entityId, 
                parameters: { flow_rate: flowRate } 
            },
            {
                onSuccess: (data) => {
                    setStartedJobId(data.job_id);
                }
            }
        );
    };

    const isLoading = isStarting || (jobStatus?.status === 'running');
    const isCompleted = jobStatus?.status === 'completed';
    const isFailed = jobStatus?.status === 'failed';

    // Get model-specific parameters based on entity type
    const getModelParams = () => {
        switch (entityType) {
            case 'MembraneBioreactor':
            case 'MBR':
                return {
                    title: 'MBR Simulation Parameters',
                    description: 'Configure greywater treatment simulation',
                    defaultFlow: 100,
                    minFlow: 10,
                    maxFlow: 500,
                    unit: 'L/day'
                };
            case 'ReverseOsmosis':
            case 'RO':
                return {
                    title: 'RO Simulation Parameters',
                    description: 'Configure rainwater purification simulation',
                    defaultFlow: 50,
                    minFlow: 5,
                    maxFlow: 200,
                    unit: 'L/day'
                };
            case 'InfiltrationSystem':
            case 'Infiltration':
                return {
                    title: 'Infiltration Simulation Parameters',
                    description: 'Configure soil infiltration simulation',
                    defaultFlow: 30,
                    minFlow: 0,
                    maxFlow: 100,
                    unit: 'L/day'
                };
            default:
                return {
                    title: 'Simulation Parameters',
                    description: 'Configure simulation parameters',
                    defaultFlow: 100,
                    minFlow: 0,
                    maxFlow: 1000,
                    unit: 'L/day'
                };
        }
    };

    const params = getModelParams();

    return (
        <Paper withBorder shadow="sm" radius="md" p="md" pos="relative">
            <LoadingOverlay visible={isLoading} overlayProps={{ blur: 1 }} />
            
            <Stack gap="md">
                <Box>
                    <Title order={5}>{params.title}</Title>
                    <Text size="sm" c="dimmed">{params.description}</Text>
                    <Text size="xs" c="blue">Entity: {entityName}</Text>
                </Box>

                <NumberInput
                    label={`Flow Rate (${params.unit})`}
                    description={`Range: ${params.minFlow} - ${params.maxFlow} ${params.unit}`}
                    value={flowRate}
                    onChange={(val) => setFlowRate(Number(val) || 0)}
                    min={params.minFlow}
                    max={params.maxFlow}
                    step={10}
                />

                <Button 
                    leftSection={<IconPlayerPlay size={16} />}
                    onClick={handleRun} 
                    loading={isLoading} 
                    color={isFailed ? 'red' : 'blue'}
                >
                    {isFailed ? 'Retry Simulation' : 'Run Simulation'}
                </Button>

                {jobStatus && (
                    <Stack gap="xs" mt="sm">
                        <Group justify="space-between">
                            <Text size="sm" fw={500}>Status:</Text>
                            <Badge color={
                                jobStatus.status === 'completed' ? 'green' :
                                    jobStatus.status === 'failed' ? 'red' :
                                        jobStatus.status === 'running' ? 'blue' : 'gray'
                            }>
                                {(jobStatus.status || 'unknown').toUpperCase()}
                            </Badge>
                        </Group>

                        {jobStatus.status === 'running' && (
                            <Progress value={jobStatus.progress || 0} animated striped />
                        )}

                        {isCompleted && jobStatus.results && (
                            <>
                                <Alert icon={<IconCheck size={16} />} title="Success" color="green" variant="light">
                                    Simulation completed successfully.
                                </Alert>
                                <Text size="xs" c="dimmed">Job ID: {jobStatus.job_id}</Text>
                                <Group gap="xs">
                                    {Object.entries(jobStatus.results || {}).map(([key, val]) => (
                                        typeof val !== 'object' && (
                                            <Text key={key} size="xs" bg="gray.1" p={4} style={{ borderRadius: 4 }}>
                                                {key.toUpperCase()}: {String(val)}
                                            </Text>
                                        )
                                    ))}
                                </Group>
                            </>
                        )}

                        {isFailed && (
                            <Alert icon={<IconAlertCircle size={16} />} title="Simulation Failed" color="red">
                                {jobStatus.error || "An unknown error occurred during simulation."}
                            </Alert>
                        )}
                    </Stack>
                )}

                {startError && (
                    <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red" mt="sm">
                        {startError.message || "Failed to start simulation."}
                    </Alert>
                )}
            </Stack>
        </Paper>
    );
};

export default SimulationForm;
