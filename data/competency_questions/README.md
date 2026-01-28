# Competency Questions & Coverage Analysis

This directory contains competency questions for the waterFRAME ontology, along with coverage analysis and SPARQL queries.

## Directory Structure

```
data/competency_questions/
├── README.md                          # This file
├── competency_questions.md            # Complete list of competency questions
├── coverage_matrix.md                 # Original coverage matrix
├── coverage_analysis.md               # Detailed coverage analysis (generated)
├── COVERAGE_SUMMARY.md               # Executive summary with recommendations
├── sparql/                           # Original SPARQL queries (reference)
│   └── ... (17 queries)
└── sparql_updated/                   # Complete set of validated queries
    ├── System Topology (CQ1-5):
    │   ├── cq01_all_nodes.rq
    │   ├── cq02_flow_connections_updated.rq
    │   ├── cq02_flow_connections_port_based.rq
    │   ├── cq03_input_sources.rq
    │   ├── cq04_downstream_nodes.rq
    │   └── cq05_flow_path.rq
    ├── Water Quality (CQ10-12):
    │   ├── cq10_water_quality_parameters.rq
    │   ├── cq11_regulatory_limits.rq
    │   └── cq12_compliance_check.rq
    ├── Model Metadata (CQ17-23):
    │   ├── cq17_model_for_entity.rq
    │   ├── cq18_model_inputs.rq
    │   ├── cq19_model_outputs.rq
    │   ├── cq20_decision_variables.rq
    │   ├── cq21_parameter_range.rq
    │   ├── cq22_model_invocation.rq
    │   └── cq23_model_capabilities.rq
    ├── Optimization Agents (CQ25-27):
    │   ├── cq25_optimization_agents.rq
    │   ├── cq26_agent_capabilities.rq
    │   └── cq27_constraint_types.rq
    ├── Optimization Formulation (CQ30-33):
    │   ├── cq30_decision_variables.rq
    │   ├── cq31_io_constraints.rq
    │   └── cq33_model_invocation_sequence.rq
    └── Compliance & Sampling (CQ37-40):
        ├── cq37_find_violations.rq
        ├── cq38_sample_chain_of_custody.rq
        ├── cq39_load_calculation.rq
        └── cq40_sampling_points.rq

    Total: 26 queries covering all answerable competency questions
```

## Quick Start

### View Coverage Analysis

**Executive Summary:**
👉 **[COVERAGE_SUMMARY.md](COVERAGE_SUMMARY.md)** - Start here for high-level overview

**Detailed Analysis:**
👉 **[coverage_analysis.md](coverage_analysis.md)** - Full breakdown by competency question

### Run SPARQL Queries

**Updated Queries** (recommended):
```bash
cd data/competency_questions/sparql_updated/
```

**Original Queries** (reference):
```bash
cd data/competency_questions/sparql/
```

### Regenerate Analysis

```bash
# From project root
cd /Users/jeandavidt/Developer/jeandavidt/ontEAUlogy

# Analyze coverage
uv run python scripts/analyze_cq_coverage.py

# Generate updated queries
uv run python scripts/generate_updated_queries.py
```

## Coverage Summary

| **Coverage Level** | **Count** | **Percentage** |
|-------------------|-----------|----------------|
| ✅ Full           | 27        | 67.5%          |
| ⚠️ Partial        | 9         | 22.5%          |
| ⚡ Minimal        | 2         | 5.0%           |
| ❌ None           | 2         | 5.0%           |
| **Total**         | **40**    | **100%**       |

## Key Findings

### Strong Coverage (✅ Full)
- Water quality parameters and observations (CQ10-13)
- Regulatory compliance and sampling (CQ37-40)
- Model metadata and I/O (CQ17-21)
- Optimization agents and capabilities (CQ25-29)
- Optimization problem formulation (CQ30-33)

### Needs Attention (⚠️ Partial / ⚡ Minimal)
- System topology (CQ1-5) - Port-based connections available, needs instance validation
- Treatment configuration (CQ6-9) - Framework exists, needs instances
- Stream classification (CQ14) - Design gap
- Treatment capacity (CQ9) - Missing properties

## Ontology Modules

The waterFRAME ontology consists of 14 modules with 141 classes and 134 properties:

### Core
- [`material_entities.ttl`](../ontology/modules/core/material_entities.ttl) - Physical components
- [`properties.ttl`](../ontology/modules/core/properties.ttl) - Core relationships

### Information
- [`information.ttl`](../ontology/modules/information.ttl) - Model metadata
- [`capabilities.ttl`](../ontology/modules/capabilities.ttl) - Model capabilities
- [`qualities.ttl`](../ontology/modules/qualities.ttl) - Water quality
- [`agents.ttl`](../ontology/modules/agents.ttl) - Computational agents

### Regulatory
- [`sampling.ttl`](../ontology/modules/sampling.ttl) - Sample metadata
- [`compliance.ttl`](../ontology/modules/compliance.ttl) - Compliance checking

### Bridges
- [`sosa_alignment.ttl`](../ontology/bridges/sosa_alignment.ttl) - SOSA observations
- [`envo_alignment.ttl`](../ontology/bridges/envo_alignment.ttl) - Environmental context

## Query Examples

### Find All Nodes in System ([`cq01_all_nodes.rq`](sparql_updated/cq01_all_nodes.rq))
```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?node ?nodeType ?nodeLabel
WHERE {
    ?node a ?nodeType .
    VALUES ?nodeType {
        wf:WastewaterTreatmentPlant
        wf:DrinkingWaterPlant
        wf:IndustrialFacility
        wf:River
    }
    OPTIONAL { ?node rdfs:label ?nodeLabel }
}
```

### Water Quality Parameters ([`cq10_water_quality_parameters.rq`](sparql_updated/cq10_water_quality_parameters.rq))
```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?observation ?parameter ?paramLabel ?value ?timestamp
WHERE {
    ?observation a wf:WaterQualityObservation ;
                wf:observedParameter ?parameter ;
                wf:observedValue ?value .
    OPTIONAL { ?parameter rdfs:label ?paramLabel }
    OPTIONAL { ?observation wf:observedOn ?timestamp }
}
```

### Regulatory Violations ([`cq37_find_violations.rq`](sparql/cq37_find_violations.rq))
```sparql
PREFIX wf: <https://ugentbiomath.github.io/waterframe#>

SELECT ?violation ?parameter ?observedValue ?limitValue ?severity
WHERE {
    ?violation a wf:ViolationRecord ;
               wf:violatingObservation ?observation ;
               wf:violatedRequirement ?requirement .

    ?observation wf:observedParameter ?paramClass ;
                 wf:observedValue ?observedValue .
    ?paramClass rdfs:label ?parameter .

    ?requirement wf:hasLimitValue ?limitValue .

    OPTIONAL {
        ?violation wf:hasSeverity ?severityClass .
        ?severityClass rdfs:label ?severity
    }
}
```

## Recommendations

### Priority 1: Critical Gaps
1. Add stream type classification (`wf:StreamType`, `wf:Greywater`, `wf:Blackwater`)
2. Add treatment capacity properties (`wf:designCapacity`, `wf:maxFlowRate`)
3. Validate `WaterSystemComponent` class hierarchy

### Priority 2: Instance Development
4. Develop treatment unit instances for case studies
5. Create flow connection instances
6. Add treatment technology-contaminant mappings

### Priority 3: Nice to Have
7. Add provenance timestamps (`wf:lastUpdated`)
8. Add maintainer properties (`wf:maintainedBy`)
9. Extend solver metadata for optimization agents

## References

- **Competency Questions:** See [`competency_questions.md`](competency_questions.md)
- **Coverage Analysis:** See [`COVERAGE_SUMMARY.md`](COVERAGE_SUMMARY.md)
- **Ontology Documentation:** See [`../../docs/`](../../docs/)
- **Case Studies:** See [`../../case_studies/ghent/`](../../case_studies/ghent/)

## Scripts

- [`scripts/analyze_cq_coverage.py`](../../scripts/analyze_cq_coverage.py) - Analyze ontology coverage
- [`scripts/generate_updated_queries.py`](../../scripts/generate_updated_queries.py) - Generate SPARQL queries

## License

Part of the waterFRAME ontology project. See main repository for license information.
