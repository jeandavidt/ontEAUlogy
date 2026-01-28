import { useEffect, useState, useRef } from 'react';

const WS_URL = 'ws://localhost:8080/ws/sensor-data';
const MAX_POINTS = 100;

interface SensorReading {
    sensor_id: string;
    parameter: string;
    value: number;
    unit: string;
    timestamp: string;
}

export const useSensorStream = (sensorId: string | null) => {
    const [readings, setReadings] = useState<SensorReading[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!sensorId) return;

        const connect = () => {
            const socket = new WebSocket(WS_URL);

            socket.onopen = () => {
                console.log('Sensor WebSocket connected');
            };

            socket.onmessage = (event) => {
                const message = JSON.parse(event.data);

                if (message.type === 'sensor_batch') {
                    const batchReadings = message.readings as SensorReading[];

                    // Get ALL readings for this sensor (may have multiple parameters)
                    const sensorReadings = batchReadings.filter(r => r.sensor_id === sensorId);

                    if (sensorReadings.length > 0) {
                        setReadings(prev => {
                            let updated = [...prev];

                            // Add each new reading for this sensor
                            sensorReadings.forEach(reading => {
                                // Check if reading with same timestamp and parameter already exists
                                const exists = updated.some(r =>
                                    r.timestamp === reading.timestamp &&
                                    r.parameter === reading.parameter
                                );
                                if (!exists) {
                                    updated.push(reading);
                                }
                            });

                            // Keep last MAX_POINTS readings
                            return updated.slice(-MAX_POINTS);
                        });
                    }
                }
            };

            socket.onclose = () => {
                console.log('Sensor WebSocket disconnected. Attempting to reconnect...');
                setTimeout(connect, 3000);
            };

            socket.onerror = (error) => {
                console.error('Sensor WebSocket error:', error);
                socket.close();
            };

            ws.current = socket;
        };

        connect();

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [sensorId]);

    return readings;
};
