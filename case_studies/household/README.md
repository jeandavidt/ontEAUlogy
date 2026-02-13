# Household Case Study — Decentralised Water Reuse System

Model services for a single-household decentralised water management system
featuring greywater recycling, rainwater harvesting, and on-site treatment.

## System Overview

```
Greywater sources                     Rainwater
(Bath, Sink, Washer,                  Collection
 Dishwasher, Kitchen, Cleaning)           │
         │                                │
         ▼                                ▼
  ┌──────────────┐              ┌─────────────────┐
  │     MBR      │              │  Rainwater Tank │
  │  (port 8101) │              └────────┬────────┘
  └──────┬───────┘                       │
         │ Reclaimed water               ▼
         ▼                      ┌──────────────────┐
  ┌──────────────────┐          │  RO  (port 8102) │
  │ Purified Grey-   │◄─────────│  purified water  │
  │ water Storage    │          └──────────────────┘
  └────────┬─────────┘
           │ Reuse (toilet, appliances)
           │
           │ Overflow
           ▼
  ┌──────────────────┐     Blackwater
  │   Infiltration   │◄────────────────  Toilet → Blackwater Tank
  │  (port 8103)     │
  └──────────────────┘
```

## Port Map

| Service | Port | Description |
|---------|------|-------------|
| MBR model | 8101 | Membrane Bioreactor greywater treatment |
| RO model | 8102 | Reverse Osmosis rainwater purification |
| Infiltration model | 8103 | Soil infiltration for blackwater/overflow |
| Shared orchestrator | 8080 | Ghent orchestrator (extended to include household) |
| Frontend | 3000 | React frontend (connects to orchestrator) |

## Startup

### Standalone model services (development)

```bash
cd case_studies/household

# Install dependencies
uv pip install -e .

# Start each model in a separate terminal
python -m household_water.runners.model_runner --model mbr
python -m household_water.runners.model_runner --model ro
python -m household_water.runners.model_runner --model infiltration
```

### Full stack with Docker Compose

```bash
cd case_studies/ghent

# Start all services including household models
docker-compose --profile full up -d

# Or start only household + orchestrator (no monitoring)
docker-compose --profile backend --profile household up -d
```

## Example curl Commands

### Health check
```bash
curl http://localhost:8101/health
curl http://localhost:8102/health
curl http://localhost:8103/health
```

### Self-description (JSON-LD)
```bash
curl http://localhost:8101/describe | python3 -m json.tool
```

### Self-description (Turtle)
```bash
curl http://localhost:8101/describe/turtle
curl http://localhost:8101/describe/agent
```

### Simulate MBR
```bash
curl -X POST http://localhost:8101/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "influent_flow_m3d": 1.5,
    "influent_cod_mg_l": 350.0,
    "influent_bod_mg_l": 200.0,
    "influent_tss_mg_l": 150.0,
    "influent_nh4_mg_l": 50.0,
    "influent_tp_mg_l": 8.0
  }'
```

Expected response:
```json
{
  "effluent_flow_m3d": 1.425,
  "effluent_cod_mg_l": 17.5,
  "effluent_tss_mg_l": 1.5,
  "effluent_nh4_mg_l": 7.5,
  "effluent_tp_mg_l": 3.2,
  "energy_kwh_d": 0.6,
  "sludge_kg_d": 0.0857,
  "recovery_fraction": 0.95
}
```

### Simulate RO
```bash
curl -X POST http://localhost:8102/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "feed_flow_m3d": 0.8,
    "feed_tds_mg_l": 100.0,
    "feed_turbidity_ntu": 1.0,
    "feed_conductivity_us_cm": 200.0
  }'
```

### Simulate Infiltration
```bash
curl -X POST http://localhost:8103/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "influent_flow_m3d": 0.3,
    "influent_cod_mg_l": 200.0,
    "influent_tss_mg_l": 50.0,
    "influent_nh4_mg_l": 40.0
  }'
```

### Query all agents via shared orchestrator SPARQL
```bash
curl -X POST http://localhost:8080/api/v1/query/sparql \
  -H "Content-Type: application/json" \
  -d '{"query": "PREFIX wf: <https://ugentbiomath.github.io/waterframe#> SELECT ?agent WHERE { ?agent a wf:SimulationAgent }"}'
```

## Running Tests

```bash
cd case_studies/household

# Unit tests (no services required)
uv run pytest tests/test_mbr.py tests/test_ro.py tests/test_infiltration.py -v

# Integration tests (requires full stack running)
uv run pytest tests/test_orchestrator_integration.py -v
```

## Ontology Gaps

See [MISSING_CONCEPTS.md](MISSING_CONCEPTS.md) for:
- QSDsan unit gaps (INF-01: no native Infiltration SanUnit; INF-02: MBR scale)
- `wf:ModelVariable` subclass gaps (non-blocking)
- Confirmation that all treatment unit classes, flow types, and tank subclasses
  are already present in the waterFRAME ontology

## Package Structure

```
case_studies/household/
├── Dockerfile
├── pyproject.toml
├── MISSING_CONCEPTS.md
├── README.md
├── data/
│   └── instances/          # (household-specific instance data if any)
├── src/household_water/
│   ├── models/
│   │   ├── base.py         # BaseHouseholdModel (CASE_HOUSEHOLD namespace)
│   │   ├── mbr.py          # MBR FastAPI service, port 8101
│   │   ├── ro.py           # RO FastAPI service, port 8102
│   │   └── infiltration.py # Infiltration FastAPI service, port 8103
│   └── runners/
│       └── model_runner.py # CLI entry point
└── tests/
    ├── test_mbr.py
    ├── test_ro.py
    ├── test_infiltration.py
    └── test_orchestrator_integration.py
```
