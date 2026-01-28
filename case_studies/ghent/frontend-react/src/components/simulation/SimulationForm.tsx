import React, { useState, useEffect } from 'react';
import { Stack, NumberInput, Button, Title, Text, Group, LoadingOverlay, Alert, Badge, Progress } from '@mantine/core';
import { IconAlertCircle, IconCheck } from '@tabler/icons-react';
import { useRunSimulation, useEntityState } from '../../api/queries';
import { useSelectionStore } from '../../stores/useSelectionStore';
import client from '../../api/client';

const SimulationForm: React.FC = () => {
    const selectedEntityId = useSelectionStore((state) => state.selectedEntityId);
    const { data: entity } = useEntityState(selectedEntityId);
    const { mutate, isPending: isStarting, data: startResult, error: startError, reset } = useRunSimulation();

    type JobStatus = {
        status?: string;
        progress?: number;
        results?: Record<string, unknown>;
        error?: string;
        job_id?: string;
    } | null;

    const [jobStatus, setJobStatus] = useState<JobStatus>(null);

    // Initial run handler
    const handleRun = () => {
        setJobStatus(null);
        reset();
            mutate({ entityId: selectedEntityId, flow: 1500 });
    };

    // Poll for job status when simulation starts
    useEffect(() => {
        if (startResult?.job_id) {
            const pollInterval = setInterval(async () => {
                try {
                    const { data } = await client.get(`/simulation/jobs/${startResult.job_id}`);
                    setJobStatus(data);

                    if (data.status === 'completed' || data.status === 'failed') {
                        clearInterval(pollInterval);
                    }
                } catch (err) {
                    console.error("Polling error:", err);
                    clearInterval(pollInterval);
                }
            }, 1000);

            return () => clearInterval(pollInterval);
        }
    }, [startResult?.job_id]);

    if (!selectedEntityId || (entity?.type !== 'WWTP' && entity?.type !== 'DWP')) {
        return null;
    }

    const isLoading = isStarting || (jobStatus?.status === 'running');
    const isCompleted = jobStatus?.status === 'completed';
    const isFailed = jobStatus?.status === 'failed';

    return (
        <Stack gap="md" p="md" style={{ position: 'relative' }}>
            <LoadingOverlay visible={isLoading} overlayProps={{ blur: 1 }} />
            <Title order={5}>Simulation Parameters</Title>

            <NumberInput
                label="Target Flow Rate (m³/day)"
                description="wf:isDecisionVariable: true"
                defaultValue={1000}
                min={0}
            />

            <Button onClick={handleRun} loading={isLoading} color={isFailed ? 'red' : 'blue'}>
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
    );
};

export default SimulationForm;
