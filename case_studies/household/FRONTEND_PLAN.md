# Household Frontend Development Plan

## Background
The household case study needs its own React frontend that uses the shared core component library. This frontend should be simpler than Ghent's since there are only 3 models (MBR, RO, Infiltration) vs 12+ entities in Ghent.

## Goals
1. Create a functional React frontend for the household case study
2. Use shared components from the core library
3. Household-specific visualizations and layouts
4. Integrate with the core orchestrator

## Target Structure

```
household/frontend-react/
├── package.json              # Dependencies, imports from core
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
├── src/
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   ├── index.css            # Styles
│   ├── pages/               # Household-specific pages
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── MBRView.tsx      # MBR model details
│   │   ├── ROView.tsx       # RO model details
│   │   └── InfiltrationView.tsx
│   └── components/          # Household-specific components
│       ├── SystemDiagram.tsx    # Visual system layout
│       ├── HouseholdMap.tsx     # Simple location view
│       └── WaterFlowChart.tsx   # Flow visualization
└── public/
    └── index.html
```

## Key Features Needed

### 1. Dashboard Page
- System overview diagram showing MBR → RO → Infiltration flow
- Quick status of all 3 models
- Recent simulation results
- SPARQL query interface (shared component)

### 2. Model-Specific Views
- **MBR View**: Greywater treatment details, inputs/outputs, simulation form
- **RO View**: Rainwater purification details, simulation form
- **Infiltration View**: Soil infiltration details, simulation form

### 3. Shared Components to Use (from core)
- SPARQLSection (query interface)
- SimulationForm (model inputs)
- SimulationCharts (results display)
- SensorVisualizer (if applicable)

### 4. Household-Specific Components
- SystemDiagram: Visual flow chart showing water movement
- Simple map or layout view
- Water balance chart

## Technical Approach

### Option A: Monorepo with Core Components (Recommended)
1. Set up household/frontend-react as a standard React app
2. Import shared components from core/frontend/src/core/
3. Use npm workspaces or similar to manage dependencies
4. Build process copies/bundles shared components

### Option B: Component Library Package
1. Build core components as an npm package
2. Install package in household frontend
3. More complex build process

### Option C: Direct Copy (Quick & Dirty)
1. Copy shared components from ghent to household
2. Modify for household needs
3. Not ideal for maintenance

## Implementation Tasks

### Phase 1: Setup (COMPLETED)
- [x] Create household/frontend-react/ directory structure
- [x] Initialize React project with Vite + TypeScript
- [x] Set up package.json with dependencies
- [x] Configure build tools
- [ ] Create Dockerfile

### Phase 2: Shared Components (COMPLETED - simplified approach)
- [x] SPARQLSection (query interface)
- [x] SimulationForm (model inputs)
- [x] SimulationCharts (results display)
- Note: Components kept in frontend-react for simplicity; can be refactored to core later

### Phase 3: Household Pages (COMPLETED)
- [x] Dashboard page with system diagram
- [x] MBRView page
- [x] ROView page
- [x] InfiltrationView page
- [x] Routing between pages

### Phase 4: Integration (IN PROGRESS)
- [x] API client configured (proxy to localhost:8080)
- [x] React Query hooks for entities, simulations, SPARQL
- [ ] Test data flow with running orchestrator
- [ ] Add error handling
- [ ] Test all simulations work

### Phase 5: Styling (COMPLETED)
- [x] Apply consistent styling with Mantine
- [x] Looks professional
- [x] Responsive design
- [ ] Test on different screen sizes

## Total Estimated Time: 10-14 hours

## Current Status: BUILD VERIFIED ✓
Build completed successfully on Feb 18, 2026. All TypeScript and Mantine v8 compatibility issues resolved.

## Success Criteria
- [x] Frontend builds with `npm run build`
- [ ] Can view dashboard with system overview (needs orchestrator running)
- [ ] Can run simulations on all 3 models (needs orchestrator)
- [ ] Can execute SPARQL queries (needs orchestrator)
- [ ] Looks polished and professional ✓
- [ ] Responsive design works ✓

## Notes for Implementer
- Keep it simpler than Ghent - fewer entities = cleaner UI
- Focus on the water flow visualization
- Use Mantine UI (same as Ghent) for consistency
- The core orchestrator is already working - just need to connect to it
- Test with the backend running on port 8080

## Open Questions
1. Do we want a map view or just a schematic diagram?
2. Should we show real-time sensor data?
3. What charts/visualizations are most important for household?
