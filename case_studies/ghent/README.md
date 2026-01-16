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
