# Ghent Water Models

Stub model implementations for the Ghent water system case study, using the waterFRAME ontology for self-description.

## Installation

### Option 1: Local Installation (Recommended for Development)

```bash
cd case_studies/ghent
pip install -e .
```

### Option 2: Docker (Recommended for Production/Testing)

```bash
cd case_studies/ghent
docker-compose up -d
```

See [README.docker.md](README.docker.md) for detailed Docker instructions.

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
# Ghent Synthetic Water System Case Study

This case study represents a synthetic urban water system based on the Ghent, Belgium metropolitan area. It demonstrates the waterFRAME ontology's ability to model complex water infrastructure networks including:

- Natural water bodies (Lieve River)
- Drinking water treatment plants
- Wastewater treatment plants
- Residential districts
- Industrial facilities with diverse water requirements

## System Overview

The system is divided into two zones along the Lieve River:

### Upstream Zone
- **DWP-1**: Drinking water plant (2,000 m3/day capacity)
- **WWTP-1**: Wastewater treatment plant (2,000 m3/day capacity)
- **Dampoort**: Residential district (3,000 inhabitants, 450 m3/day)
- **Texfin**: Textile industry (500 m3/day, high COD output)
- **FoodPro**: Food processing industry (800 m3/day, high BOD output)

### Downstream Zone
- **DWP-2**: Drinking water plant (2,500 m3/day capacity)
- **WWTP-2**: Wastewater treatment plant (2,500 m3/day capacity)
- **Muide**: Residential district (5,000 inhabitants, 750 m3/day)
- **ChipTech**: Electronics manufacturing (200 m3/day, ultra-pure water needs)
- **PharmaGen**: Pharmaceutical industry (400 m3/day)
- **BrewCo**: Brewery (600 m3/day, high BOD output)

## Flow Topology

```
                    UPSTREAM ZONE                          DOWNSTREAM ZONE

    [Lieve River Segment 1] -----> [Lieve River Segment 2] -----> [Lieve River Segment 3]
           |                              ^                              |
           v                              |                              v
        [DWP-1]                      [WWTP-1]                        [DWP-2]
           |                              ^                              |
           v                              |                              v
    +------+------+              +--------+--------+           +--------+--------+
    |             |              |        |        |           |        |        |
 [Dampoort]  [Industrial]   wastewater flows     [Muide]   [Industrial]
    |        [Texfin]            |                    |      [ChipTech]
    |        [FoodPro]           |                    |      [PharmaGen]
    +------------+---------------+                    |      [BrewCo]
                                                      +--------+--------+
                                                               |
                                                               v
                                                           [WWTP-2]
                                                               |
                                                               v
                                                    [Lieve River Segment 3]
```

## Data Files

- `data/system.ttl` - Master file that imports all instance files
- `data/instances/` - Individual entity TTL files:
  - `lieve_river.ttl` - River segments
  - `dwp1.ttl`, `dwp2.ttl` - Drinking water plants
  - `wwtp1.ttl`, `wwtp2.ttl` - Wastewater treatment plants
  - `dampoort_residential.ttl`, `muide_residential.ttl` - Residential districts
  - `texfin.ttl`, `foodpro.ttl`, `chiptech.ttl`, `pharmagen.ttl`, `brewco.ttl` - Industrial facilities

## Regulatory Context

This case study uses VLAREM II (Flemish environmental regulations) discharge limits where applicable, following Belgian/Flemish environmental standards for:
- BOD: 25 mg/L (max discharge)
- COD: 125 mg/L (max discharge)
- TSS: 35 mg/L (max discharge)
- Total Nitrogen: 15 mg/L (max discharge)
- Total Phosphorus: 2 mg/L (max discharge)

## Geographic Coordinates

All coordinates are based on the Ghent metropolitan area (approximately 51.05°N, 3.72°E) and follow the actual course of the Lieve canal/river system.

## Usage

Load the system using the master file:

```sparql
LOAD <file:///path/to/case_studies/ghent/data/system.ttl>
```

Or query individual entities:

```sparql
PREFIX ghent: <https://w3id.org/waterframe/case/ghent/>
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?entity ?type ?label
WHERE {
    ?entity a ?type ;
            rdfs:label ?label .
    FILTER(STRSTARTS(STR(?entity), STR(ghent:)))
}
```
