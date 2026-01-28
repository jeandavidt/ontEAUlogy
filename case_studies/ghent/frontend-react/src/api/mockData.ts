import type { WaterEntity, SimulationResult, Relationship, Triplet } from './types';

export const MOCK_ENTITIES: WaterEntity[] = [
    { id: 'river-1', label: 'Lys River Upstream', type: 'River', zone: 'Upstream', coordinates: [51.05, 3.71], status: 'idle' },
    { id: 'dwp-1', label: 'Ghent DWP North', type: 'DWP', zone: 'Upstream', coordinates: [51.06, 3.73], status: 'idle' },
    { id: 'wwtp-1', label: 'Ghent Central WWTP', type: 'WWTP', zone: 'Downstream', coordinates: [51.07, 3.75], status: 'idle' },
    { id: 'ind-1', label: 'Industrial Zone A', type: 'Industry', zone: 'Downstream', coordinates: [51.08, 3.76], status: 'idle' },
    { id: 'res-1', label: 'Residential Area East', type: 'Residential', zone: 'Downstream', coordinates: [51.04, 3.78], status: 'idle' },
    { id: 'river-2', label: 'Lys River Branch', type: 'River', zone: 'Upstream', coordinates: [51.045, 3.72], status: 'idle' },
    { id: 'dwp-2', label: 'Backup DWP', type: 'DWP', zone: 'Upstream', coordinates: [51.055, 3.74], status: 'idle' },
    { id: 'wwtp-2', label: 'North WWTP', type: 'WWTP', zone: 'Downstream', coordinates: [51.09, 3.74], status: 'idle' },
    { id: 'ind-2', label: 'Langerbrugge Plant', type: 'Industry', zone: 'Downstream', coordinates: [51.10, 3.75], status: 'idle' },
    { id: 'res-2', label: 'Sint-Amandsberg Res', type: 'Residential', zone: 'Downstream', coordinates: [51.06, 3.77], status: 'idle' },
    { id: 'res-3', label: 'Wondelgem Res', type: 'Residential', zone: 'Upstream', coordinates: [51.08, 3.71], status: 'idle' },
    { id: 'river-3', label: 'Scheldt Junction', type: 'River', zone: 'Downstream', coordinates: [51.05, 3.76], status: 'idle' },
    { id: 'sensor-1', label: 'Flow Sensor North', type: 'Sensor', zone: 'Upstream', coordinates: [51.058, 3.725], status: 'running' },
    { id: 'sensor-2', label: 'BOD Sensor Central', type: 'Sensor', zone: 'Downstream', coordinates: [51.072, 3.755], status: 'running' },
];

export const MOCK_TRIPLETS: Record<string, Triplet[]> = {
    'river-1': [
        { subject: 'river-1', predicate: 'rdf:type', object: 'ont:River', isUri: true },
        { subject: 'river-1', predicate: 'ont:label', object: 'Lys River Upstream', isUri: false },
        { subject: 'river-1', predicate: 'ont:feeds', object: 'dwp-1', isUri: true },
        { subject: 'river-1', predicate: 'ont:inZone', object: 'ont:Upstream', isUri: true },
    ],
    'dwp-1': [
        { subject: 'dwp-1', predicate: 'rdf:type', object: 'ont:DWP', isUri: true },
        { subject: 'dwp-1', predicate: 'ont:label', object: 'Ghent DWP North', isUri: false },
        { subject: 'dwp-1', predicate: 'ont:supplies', object: 'res-3', isUri: true },
        { subject: 'dwp-1', predicate: 'ont:supplies', object: 'ind-2', isUri: true },
    ],
    'sensor-1': [
        { subject: 'sensor-1', predicate: 'rdf:type', object: 'ont:Sensor', isUri: true },
        { subject: 'sensor-1', predicate: 'ont:measures', object: 'ont:Flow', isUri: true },
        { subject: 'sensor-1', predicate: 'ont:locatedIn', object: 'river-1', isUri: true },
    ],
};

export const MOCK_SENSOR_DATA: Record<string, { time: string; value: number }[]> = {
    'sensor-1': [
        { time: '2026-01-23T10:00:00Z', value: 1200 },
        { time: '2026-01-23T10:05:00Z', value: 1210 },
        { time: '2026-01-23T10:10:00Z', value: 1195 },
        { time: '2026-01-23T10:15:00Z', value: 1205 },
        { time: '2026-01-23T10:20:00Z', value: 1220 },
    ],
    'sensor-2': [
        { time: '2026-01-23T10:00:00Z', value: 12.5 },
        { time: '2026-01-23T10:05:00Z', value: 12.8 },
        { time: '2026-01-23T10:10:00Z', value: 13.2 },
        { time: '2026-01-23T10:15:00Z', value: 13.0 },
        { time: '2026-01-23T10:20:00Z', value: 12.7 },
    ],
};

export const MOCK_RELATIONSHIPS: Relationship[] = [
    { id: 'r1', source: 'river-1', target: 'dwp-1', label: 'feeds', predicate: 'ont:feeds' },
    { id: 'r2', source: 'river-1', target: 'river-2', label: 'diverges_to', predicate: 'ont:diverges_to' },
    { id: 'r3', source: 'dwp-1', target: 'res-3', label: 'supplies', predicate: 'ont:supplies' },
    { id: 'r4', source: 'res-3', target: 'wwtp-1', label: 'discharges_to', predicate: 'ont:discharges_to' },
    { id: 'r5', source: 'river-2', target: 'dwp-2', label: 'feeds', predicate: 'ont:feeds' },
    { id: 'r6', source: 'dwp-2', target: 'res-2', label: 'supplies', predicate: 'ont:supplies' },
    { id: 'r7', source: 'res-2', target: 'wwtp-2', label: 'discharges_to', predicate: 'ont:discharges_to' },
    { id: 'r8', source: 'ind-1', target: 'wwtp-1', label: 'discharges_to', predicate: 'ont:discharges_to' },
    { id: 'r9', source: 'ind-2', target: 'wwtp-2', label: 'discharges_to', predicate: 'ont:discharges_to' },
    { id: 'r10', source: 'wwtp-1', target: 'river-3', label: 'outfalls_to', predicate: 'ont:outfalls_to' },
    { id: 'r11', source: 'wwtp-2', target: 'river-3', label: 'outfalls_to', predicate: 'ont:outfalls_to' },
    { id: 'r12', source: 'river-3', target: 'ind-1', label: 'cooling_water_for', predicate: 'ont:cooling_water_for' },
    { id: 'r13', source: 'res-1', target: 'wwtp-1', label: 'discharges_to', predicate: 'ont:discharges_to' },
    { id: 'r14', source: 'river-2', target: 'res-1', label: 'supplies', predicate: 'ont:supplies' },
    { id: 'r15', source: 'dwp-1', target: 'ind-2', label: 'supplies', predicate: 'ont:supplies' },
    { id: 'r16', source: 'river-3', target: 'res-2', label: 'supplies', predicate: 'ont:supplies' },
    { id: 'r17', source: 'river-1', target: 'res-3', label: 'feeds', predicate: 'ont:feeds' },
];

export const MOCK_SIMULATION_RESULT: SimulationResult = {
    jobId: 'job-123',
    outputs: {
        bod: 12.5,
        cod: 45.0,
        nitrate: 8.2,
        flow: 1200,
    },
    timeSeries: [
        { time: '2026-01-23T10:00:00Z', value: 10.5 },
        { time: '2026-01-23T11:00:00Z', value: 12.8 },
        { time: '2026-01-23T12:00:00Z', value: 15.2 },
        { time: '2026-01-23T13:00:00Z', value: 14.1 },
        { time: '2026-01-23T14:00:00Z', value: 13.5 },
    ],
};
