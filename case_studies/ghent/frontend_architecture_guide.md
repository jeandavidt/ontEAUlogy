# Frontend Architecture Guide: Ghent Synthetic Case Study

## 1. Project Scope
This project is a scientific dashboard for the **Ghent Synthetic Water System**. It visualizes a distributed simulation of upstream/downstream water entities (WWTPs, Drinking Water Plants, Rivers).

The system relies on an **Orchestrator API** (FastAPI) which exposes ontology data, simulation capabilities, and SPARQL endpoints.

## 2. Technology Stack (Strict)
*   **Framework:** React 18 (Vite template) + TypeScript
*   **UI Library:** Mantine UI v7 (for AppShell, Forms, Modals, Inputs)
*   **Icons:** Tabler Icons React
*   **State/API Management:** TanStack Query (React Query) v5
*   **Maps:** React Leaflet (Leaflet wrapper)
*   **Node Graph:** React Flow (for DAG topology visualization)
*   **Charts:** Recharts (for time-series simulation results)
*   **HTTP Client:** Axios

## 3. Directory Structure
Adhere to this folder structure for all component generation:

```text
src/
├── api/
│   ├── client.ts             # Axios instance configuration
│   ├── types.ts              # TS Interfaces matching Ontology entities
│   ├── queries.ts            # GET hooks (useQuery)
│   └── mutations.ts          # POST hooks (useMutation)
├── components/
│   ├── common/               # Generic UI atoms (Loading, ErrorState)
│   ├── map/                  # Leaflet layers and Entity markers
│   ├── topology/             # React Flow node/edge custom components
│   ├── simulation/           # Simulation parameter forms
│   └── results/              # Recharts implementations
├── layouts/
│   ├── DashboardLayout.tsx   # Main AppShell (Navbar + Header + Outlet)
│   └── MapGraphSplitView.tsx # Layout logic for switching Map/Graph views
├── stores/
│   └── useSelectionStore.ts  # Zustand store for selected Entity ID
├── pages/
│   ├── Dashboard.tsx         # Main entry point
│   └── Settings.tsx
├── utils/
│   ├── ontologyHelpers.ts    # Parsers for TTL/SPARQL JSON responses
│   └── formatting.ts         # Unit conversion (e.g., m3/day)
└── App.tsx
4. Key Implementation Rules

A. Routing & Layout

Use <DashboardLayout> as the wrapper.
The Left Sidebar (Navbar) must contain the "Entity Details Panel" and "Query Input".
The Main Area must support toggling between two views:
Map View: Geographic locations of components.
Logic View: ReactFlow diagram showing flow connections.
B. State Management

Selected Entity: When a user clicks a Marker (Map) or Node (Graph), update the selectedEntityId in a global store (Zustand).
Reactivity: The Sidebar must reactively fetch details for selectedEntityId.
Server State: Use useQuery for fetching GET /api/v1/models/{id}/state.
C. Map Implementation (React Leaflet)

Center map on Ghent (51.0560, 3.7400).
Use icons relative to entity type (e.g., 🏭 for Industry, 💧 for DWP).
Render connection lines (Streams) based on the ontology connectsTo property.
D. Simulation Form Logic

Forms must be generated dynamically based on the Model Capabilities (capabilities.ttl from backend).
If wf:isDecisionVariable is true, render an editable Input.
Upon submission, trigger mutation.mutate(payload).
While simulation runs (status: 'running'), show a polling indicator using refetchInterval in React Query.
E. Styling

Use Mantine's sx prop or CSS Modules.
Color coding:
Upstream: Blue/Teal shades.
Downstream: Orange/Red warning shades.
Alerts: Red (if VLAREM II limits exceeded).
5. Mock Data Strategy (Phase 1)

Since the backend might not be ready, creates src/api/mockData.ts.

Topology: Return 12 fixed nodes and 18 edges (as defined in Appendix B of the design doc).
Simulation: Return a "Success" response after a 2-second delay with random time-series data for Charts.
6. Types Definition

All components must use strict constraints matching the Ontology:


export interface WaterEntity {
  id: string; // URI
  label: string;
  type: 'DWP' | 'WWTP' | 'Industry' | 'Residential' | 'River';
  zone: 'Upstream' | 'Downstream';
  coordinates: [number, number];
  status: 'idle' | 'running' | 'error';
}

export interface SimulationResult {
  jobId: string;
  outputs: Record<string, number>; // e.g., { bod: 15.2, flow: 1750 }
  timeSeries?: { time: string; value: number }[];
}

