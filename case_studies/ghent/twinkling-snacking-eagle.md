# Plan: Robust Inter-Service Communication for Ontology Evolution

## Problem Summary
The current architecture has brittle communication between services because:
1. **Type mappings are duplicated** in 3+ places (backend ontology.py x2, frontend WaterMap.tsx)
2. **Model ports are duplicated** in 2 places (main.py, simulation.py)
3. **No runtime validation** - frontend TypeScript types provide zero protection
4. **Hardcoded ontology assumptions** - URI patterns, property names scattered in SPARQL queries and LLM prompts
5. **Inconsistent response shapes** - different endpoints return different structures

## Solution Overview
A **contract-driven architecture** where the ontology becomes the single source of truth for types, with code generation and runtime validation to catch breaking changes early.

---

## Phase 1: Consolidate Duplicated Code (Quick Wins)

### 1.1 Centralize MODEL_PORTS
- **File**: [config.py](src/ghent_water/models/config.py)
- Add `MODEL_PORTS` dict derived from existing `ALL_CONFIGS`
- Update imports in:
  - [main.py](src/ghent_water/orchestrator/main.py) (lines 55-68)
  - [simulation.py](src/ghent_water/orchestrator/routers/simulation.py) (lines 21-34)

### 1.2 Centralize TYPE_MAPPING
- **Create**: `src/ghent_water/orchestrator/services/type_mappings.py`
- Extract the mapping from [ontology.py](src/ghent_water/orchestrator/routers/ontology.py) (appears at lines 131-140 AND 319-328)
- Single source of truth for `DrinkingWaterPlant → DWP` etc.

---

## Phase 2: Add Runtime Validation (Frontend Protection)

### 2.1 Install and Configure Zod
```bash
cd frontend-react && npm install zod
```

### 2.2 Create Validation Schemas (Priority: SPARQL Results)
- **Create**: `frontend-react/src/api/validation.ts`
- Define Zod schemas for:
  - `SparqlBindingSchema` - handles `{value: string, type?: string}` structure
  - `SparqlResultsSchema` - handles both `{bindings: [...]}` and flat array formats
  - `NLQueryResultsSchema` - handles natural language query responses
  - `EntitySchema` - validates entity objects
  - `EntitiesResponseSchema` - validates /ontology/entities response
  - `SimulationResponseSchema` - validates simulation results

### 2.3 Normalize SPARQL Response Shapes
The backend returns different shapes for SPARQL results. Create a normalizer:
```typescript
// frontend-react/src/api/sparqlNormalizer.ts
export function normalizeSparqlResults(data: unknown): NormalizedResult[] {
  // Handle: {results: {bindings: [...]}}
  // Handle: {results: [...]}
  // Handle: Array directly
  // Always return consistent shape for components
}
```

### 2.3 Wrap API Queries with Validation
- **Modify**: [queries.ts](frontend-react/src/api/queries.ts)
- Use `safeParse()` to validate responses
- Log warnings on validation failures instead of crashing
- Graceful fallback with `.passthrough()` for unknown fields

---

## Phase 3: Contract Testing (Catch Breaking Changes)

### 3.1 Backend Contract Tests
- **Create**: `tests/contract/test_api_contracts.py`
- Verify response shapes for critical endpoints:
  - `/api/v1/ontology/entities` returns `{entities: [], count: N}`
  - `/api/v1/query/sparql` returns standard SPARQL JSON format
  - `/api/v1/simulation/models/{id}/run` returns `{job_id, status, ...}`

### 3.2 Schema Regression Tests
- Test that Pydantic models can deserialize actual API responses
- Add `npm run type-check` to CI for TypeScript compatibility

---

## Phase 4: Dynamic Type Registry from Ontology

### 4.1 Extend Ontology with Display Metadata
Add to waterframe.ttl (or new visualization module):
```turtle
wf:DrinkingWaterPlant wf:displayLabel "DWP" ;
    wf:displayColor "#15aabf" ;
    wf:displayIcon "droplet-filled" .
```

### 4.2 Create TypeRegistry Service
- **Create**: `src/ghent_water/orchestrator/services/type_registry.py`
- Queries ontology at startup for type metadata
- Methods: `get_display_label()`, `get_all_types()`, `get_color()`

### 4.3 Add `/api/v1/ontology/types` Endpoint
Returns all entity types with their display metadata:
```json
{
  "types": [
    {"localName": "DrinkingWaterPlant", "displayLabel": "DWP", "displayColor": "#15aabf", "displayIcon": "droplet-filled"}
  ]
}
```

### 4.4 Update Frontend to Use Dynamic Types
- **Modify**: [WaterMap.tsx](frontend-react/src/components/map/WaterMap.tsx)
- Replace hardcoded `TYPE_COLORS` with `useEntityTypes()` hook
- Graceful fallback for unknown types

---

## Phase 5: Schema Generation Pipeline (OpenAPI-based)

### 5.1 Set Up Type Generation Script
FastAPI already generates OpenAPI spec. Create generation script:

**Create**: `shared/generate-types.sh`
```bash
#!/bin/bash
# Export OpenAPI from running server
curl -s http://localhost:8080/openapi.json > shared/openapi.json

# Generate TypeScript types
npx openapi-typescript shared/openapi.json -o frontend-react/src/api/generated-types.ts

echo "Types generated successfully"
```

### 5.2 Install Dependencies
```bash
cd frontend-react && npm install -D openapi-typescript
```

### 5.3 Add to Package Scripts
```json
{
  "scripts": {
    "generate-types": "../shared/generate-types.sh",
    "type-check": "tsc --noEmit"
  }
}
```

### 5.4 Update Frontend to Use Generated Types
- Import from `generated-types.ts` instead of manual `types.ts`
- Keep manual types as fallback during transition

---

## Files to Modify/Create

| File | Action | Phase |
|------|--------|-------|
| `src/ghent_water/models/config.py` | Add MODEL_PORTS | 1 |
| `src/ghent_water/orchestrator/main.py` | Import MODEL_PORTS | 1 |
| `src/ghent_water/orchestrator/routers/simulation.py` | Import MODEL_PORTS | 1 |
| `src/ghent_water/orchestrator/services/type_mappings.py` | Create | 1 |
| `src/ghent_water/orchestrator/routers/ontology.py` | Use shared TYPE_MAPPING | 1 |
| `frontend-react/src/api/validation.ts` | Create Zod schemas | 2 |
| `frontend-react/src/api/queries.ts` | Add validation | 2 |
| `tests/contract/test_api_contracts.py` | Create | 3 |
| `src/ghent_water/orchestrator/services/type_registry.py` | Create | 4 |
| `frontend-react/src/components/map/WaterMap.tsx` | Use dynamic types | 4 |
| `shared/generate-types.sh` | Create | 5 |

---

## Verification

### After Phase 1:
- Run existing tests: `pytest tests/`
- Verify backend starts: `docker-compose up orchestrator`
- Check no import errors

### After Phase 2:
- Run frontend: `npm run dev`
- Check browser console for validation warnings
- Test SPARQL queries in the UI - verify results render correctly
- Test natural language queries - verify the different response shapes are handled
- Intentionally break a response to verify Zod catches it (console warning, not crash)

### After Phase 3:
- Run contract tests: `pytest tests/contract/`
- CI should catch type mismatches

### After Phase 4:
- Add a new entity type to ontology
- Verify it appears in frontend without code changes
- Check `/api/v1/ontology/types` returns new type

### After Phase 5:
- Modify a Pydantic model
- Regenerate TypeScript types
- Verify `npm run type-check` catches any issues
