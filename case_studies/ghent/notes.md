# Phase 5 Planning Notes - COMPLETE

## Sources

### Research Document
- File: `.planning/phases/05-frontend-stack-review/05-RESEARCH.md`
- Key findings:
  - NiceGUI recommended over Streamlit for real-time updates
  - Native WebSocket support through socket.io
  - Built-in Leaflet integration for maps
  - pyvis for graph visualization
  - Event-driven architecture vs script reruns

### Current Project Structure
- Main app: `src/ghent_water/frontend/app.py` (Streamlit)
- Components: map_view, sensor_panel, query_panel, entity_details
- Services: api_client, websocket_client
- Dependencies: streamlit, folium, streamlit-folium

### Key Requirements
- Interactive map with dynamic markers
- Real-time sensor data display
- Graph visualization from SPARQL results
- Multi-page structure (dashboard, query, simulation)
- WebSocket integration for live updates

## Synthesized Findings

### Migration Strategy
1. **Foundation**: Install NiceGUI and supporting libraries
2. **Core Migration**: Convert app.py structure to NiceGUI multi-page
3. **Component Migration**: Migrate each component with NiceGUI patterns
4. **Real-time Integration**: Implement WebSocket handler with background tasks
5. **Testing**: Add E2E testing with pytest-playwright

### Technical Decisions
- **Frontend Framework**: NiceGUI 3.0+ (event-driven, native WebSocket)
- **Maps**: ui.leaflet (built-in Leaflet integration)
- **Graph Viz**: pyvis + NetworkX (interactive graphs)
- **Testing**: pytest-playwright (E2E browser testing)
- **State Management**: app.storage (NiceGUI native)

### Risk Mitigation
- Migration complexity → Start with sensor panel pilot
- Performance issues → Limit graph nodes (<500)
- Multi-user support → Test with load testing
- Learning curve → Use NiceGUI examples and patterns

### Migration Strategy Finalized
1. **Foundation (05-01)**: Install NiceGUI ecosystem
2. **Core Structure (05-02)**: Multi-page NiceGUI application
3. **Map Component (05-03)**: Interactive Leaflet with dynamic markers
4. **Real-time Sensors (05-04)**: WebSocket integration for live data
5. **Graph Visualization (05-05)**: pyvis + NetworkX for knowledge graphs
6. **Query Interface (05-06)**: SPARQL and natural language querying
7. **Simulation Controls (05-07)**: Real-time simulation monitoring
8. **E2E Testing (05-08)**: Playwright test suite for validation

### Dependencies Resolved
- Wave 1: Foundation and core app structure (01, 02)
- Wave 2: Map and real-time sensors (03, 04) 
- Wave 3: Query and graph visualization (05, 06)
- Wave 4: Simulation controls (07)
- Wave 5: Comprehensive testing (08)

All plans created with proper dependency chains and wave assignments.