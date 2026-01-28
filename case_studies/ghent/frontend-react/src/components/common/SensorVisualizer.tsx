import React, { useState, useMemo } from 'react';
import { Box, Paper, Title, Text, LoadingOverlay, SegmentedControl, Group, Badge, Stack } from '@mantine/core';
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { useSensorData } from '../../api/queries';
import { useSensorStream } from '../../api/webSocket';

interface SensorVisualizerProps {
    sensorId: string;
    label: string;
}

const SensorVisualizer: React.FC<SensorVisualizerProps> = ({ sensorId, label }) => {
    type SensorHistory = {
        sensor_id?: string;
        sensor_type?: string;
        parameters?: Record<string, { unit: string }>;
        current_readings?: Record<string, number>;
        history?: Array<Record<string, number | string>>;
    };

    type SensorPoint = Record<string, number | string> & { timestamp: string };

    const { data: sensorHistorical, isLoading } = useSensorData(sensorId);
    const readings = useSensorStream(sensorId);

    const [selectedParam, setSelectedParam] = useState<string | null>(null);

    const params = useMemo(() => {
        const historyData = sensorHistorical as SensorHistory | null;
        if (!historyData?.parameters) return [];
        return Object.keys(historyData.parameters).map(p => ({
            label: p,
            value: p,
            unit: historyData.parameters?.[p]?.unit || ''
        }));
    }, [sensorHistorical]);

    const historyData = sensorHistorical as SensorHistory | null;
    const historyPoints = (historyData?.history || []) as SensorPoint[];

    const combinedPoints = useMemo(() => {
        // Helper to round timestamp to nearest second for grouping
        const roundTimestamp = (ts: string): string => {
            const date = new Date(ts);
            date.setMilliseconds(0);
            return date.toISOString();
        };

        // Start with historical data
        const pointsMap = new Map<string, Record<string, number | string>>();

        // Add historical points to map
        historyPoints.forEach(point => {
            const roundedTs = roundTimestamp(point.timestamp);
            const existing = pointsMap.get(roundedTs);
            if (existing) {
                // Merge parameters if timestamps round to same second
                Object.assign(existing, point);
            } else {
                pointsMap.set(roundedTs, { ...point, timestamp: roundedTs });
            }
        });

        // Group live readings by rounded timestamp and merge all parameters
        if (readings && readings.length > 0) {
            readings.forEach(reading => {
                const roundedTs = roundTimestamp(reading.timestamp);
                const existing = pointsMap.get(roundedTs);
                if (existing) {
                    // Update existing point with new parameter value
                    existing[reading.parameter] = reading.value;
                } else {
                    // Create new point with this parameter
                    const newPoint: Record<string, number | string> = {
                        timestamp: roundedTs,
                        [reading.parameter]: reading.value,
                    };
                    pointsMap.set(roundedTs, newPoint);
                }
            });
        }

        // Convert map to array, sort by timestamp, and keep last 100 points
        return Array.from(pointsMap.values())
            .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
            .slice(-100);
    }, [historyPoints, readings]);

    const derivedSelectedParam = selectedParam || params[0]?.value || null;

    const chartData = useMemo(() => {
        return combinedPoints.map(point => ({
            ...point,
            time: new Date(point.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        }));
    }, [combinedPoints]);

    if (!sensorId) return null;

    const currentUnit = params.find(p => p.value === derivedSelectedParam)?.unit || '';

    return (
        <Paper withBorder shadow="sm" radius="md" p="md" mt="md" style={{ position: 'relative' }}>
            <LoadingOverlay visible={isLoading} />
            <Group justify="space-between" mb="md">
                <Stack gap={0}>
                    <Title order={6}>Sensor: {label}</Title>
                    <Text size="xs" c="dimmed">{sensorId}</Text>
                </Stack>
                {readings && readings.length > 0 && (
                    <Badge color="green" variant="dot">Live</Badge>
                )}
            </Group>

            {params.length > 1 && (
                <Box mb="md">
                    <Text size="xs" fw={500} mb={4} c="dimmed">Select Parameter:</Text>
                    <SegmentedControl
                        size="xs"
                        value={selectedParam || ''}
                        onChange={setSelectedParam}
                        data={params.map(p => p.value)}
                    />
                </Box>
            )}

            {chartData.length > 0 && derivedSelectedParam ? (
                <div style={{ width: '100%', height: 200 }}>
                    <ResponsiveContainer width="100%" height={200}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#be4bdb" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#be4bdb" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f3f5" />
                            <XAxis
                                dataKey="time"
                                fontSize={10}
                                tick={{ fill: '#868e96' }}
                                axisLine={{ stroke: '#dee2e6' }}
                            />
                            <YAxis
                                fontSize={10}
                                tick={{ fill: '#868e96' }}
                                axisLine={{ stroke: '#dee2e6' }}
                                label={{ value: currentUnit, angle: -90, position: 'insideLeft', fontSize: 10, offset: 10 }}
                            />
                            <Tooltip
                                contentStyle={{ borderRadius: '8px', border: '1px solid #dee2e6', fontSize: '10px' }}
                            />
                            <Area
                                type="monotone"
                                dataKey={derivedSelectedParam}
                                stroke="#be4bdb"
                                fillOpacity={1}
                                fill="url(#colorValue)"
                                strokeWidth={2}
                                isAnimationActive={false}
                                connectNulls={true}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            ) : (
                <Box h={200} display="flex" style={{ alignItems: 'center', justifyContent: 'center' }}>
                    <Text size="xs" c="dimmed">Waiting for sensor data...</Text>
                </Box>
            )}
        </Paper>
    );
};

export default SensorVisualizer;
