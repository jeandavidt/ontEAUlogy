# Ghent Water Models

Stub model implementations for the Ghent water system case study, using the waterFRAME ontology for self-description.

## Installation

```bash
cd case_studies/ghent
pip install -e .
```

## Running Models

### Using the CLI

```bash
# Run DWP1 on default port 8001
python -m ghent_water.models.runners.model_runner --model dwp1

# Run WWTP1 on port 8003
python -m ghent_water.models.runners.model_runner --model wwtp1 --port 8003

# Run with auto-reload
python -m ghent_water.models.runners.model_runner --model dwp2 --reload
```

### Supported Models

| Model | Port | Entity |
|-------|------|--------|
| dwp1 | 8001 | Drinking Water Plant 1 |
| dwp2 | 8002 | Drinking Water Plant 2 |
| wwtp1 | 8003 | Wastewater Treatment Plant 1 |
| wwtp2 | 8004 | Wastewater Treatment Plant 2 |
| texfin | 8005 | Textile Industry |
| foodpro | 8006 | Food Processing |
| chiptech | 8007 | Electronics Manufacturing |
| pharmagen | 8008 | Pharmaceutical |
| brewco | 8009 | Brewery |
| river | 8010 | Lieve River |
| dampoort | 8011 | Residential District (upstream) |
| muide | 8012 | Residential District (downstream) |

### API Endpoints

Each model exposes:

- `GET /describe` - JSON-LD self-description
- `GET /describe/turtle` - Turtle (TTL) self-description
- `POST /simulate` - Run simulation with inputs
- `GET /state` - Current model state
- `GET /health` - Health check

## Programmatic Usage

```python
from ghent_water.models.stubs.dwp import create_dwp_model

# Create a model instance
model = create_dwp_model(entity_id="DWP1", port=8001)

# Get self-description
description = await model.describe()

# Run simulation
result = await model.simulate({
    "raw_water_flow": 40000,
    "raw_water_turbidity": 10,
    "raw_water_toc": 5,
    "raw_water_ph": 7.5,
    "raw_water_coliforms": 100,
})
```

## Configuration

All model configurations are defined in `ghent_water/models/config.py`. Each entity has configurable:

- Input/output parameters
- Treatment/removal efficiencies
- Metadata (location, connections, etc.)

## Ontology

Models describe themselves using the waterFRAME ontology:
- `https://w3id.org/waterframe/` - Base namespace
- `https://w3id.org/waterframe/capability/` - Capability classes
- `https://w3id.org/waterframe/case/ghent/` - Ghent case study instances
