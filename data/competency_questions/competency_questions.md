## Competency Questions

### System topology

- **CQ1** [O]: What are all the nodes (plants, sources, junctions, sinks) in a given catchment?
- **CQ2** [O]: What flows connect Node A to Node B? (directed edges, flow type: water, sludge, chemical)
- **CQ3** [O]: What are the possible input sources for Plant X?
- **CQ4** [O]: What downstream nodes receive effluent from Plant X?
- **CQ5** [O/R]: What is the complete flow path from Source S to Sink K? (may require transitive reasoning)

### Treatment configuration

- **CQ6** [O]: What unit processes comprise the treatment train at Plant X?
- **CQ7** [O]: What is the sequence/topology of unit processes within Plant X?
- **CQ8** [O]: What treatment technologies are available for a given contaminant removal objective?
- **CQ9** [O]: What is the design capacity of Unit Process U?

### Water quality and fitness-for-purpose

- **CQ10** [O]: What quality parameters characterize the water at Node N? → [SPARQL](sparql/cq10_water_quality_parameters.rq)
- **CQ11** [O]: What are the regulatory limits for Parameter P for Reuse Category R? → [SPARQL](sparql/cq11_regulatory_limits.rq)
- **CQ12** [O/R/M]: Does the effluent quality at Plant X meet the requirements for agricultural reuse? (may require comparison reasoning or model output) → [SPARQL](sparql/cq12_compliance_check.rq)
- **CQ13** [O]: What contaminants are present in Source S above threshold T?

### Source/stream classification

- **CQ14** [O]: Is Stream S classified as greywater or blackwater?
- **CQ15** [O]: What sources in the catchment are classified as fit-for-purpose Category C?
- **CQ16** [O/R]: What treatment is required to upgrade water from Quality Class Q1 to Q2?

### Model metadata

- **CQ17** [O]: What computational model is associated with Unit Process U?
- **CQ18** [O]: What are the input variables for Model M? → [SPARQL](sparql/cq18_model_inputs.rq)
- **CQ19** [O]: What are the output variables for Model M? → [SPARQL](sparql/cq19_model_outputs.rq)
- **CQ20** [O]: Which parameters of Model M are fixed vs. manipulable (decision variables)? → [SPARQL](sparql/cq20_decision_variables.rq)
- **CQ21** [O]: What is the valid range for Parameter P in Model M?
- **CQ22** [O]: How is Model M invoked? (API endpoint, function signature, agent reference)
- **CQ23** [O]: What mass/quality balances does Model M compute? → [SPARQL](sparql/cq23_model_capabilities.rq)
- **CQ24** [O]: What time resolution does Model M operate at? (steady-state, dynamic, event-based)

### Optimization agent metadata

- **CQ25** [O]: What optimization agents are available in the system?
- **CQ26** [O]: What objective function types can Agent A handle? (linear, quadratic, nonlinear, multi-objective)
- **CQ27** [O]: What constraint types can Agent A handle? (equality, inequality, logical, chance)
- **CQ28** [O]: What solvers does Agent A have access to?
- **CQ29** [O]: How is Agent A invoked?

### Optimization problem formulation

- **CQ30** [O]: For a given objective (minimize energy, maximize reuse, minimize cost), which nodes have relevant decision variables?
- **CQ31** [O]: What constraints link the outputs of upstream nodes to the inputs of downstream nodes?
- **CQ32** [O]: What is the set of decision variables for a catchment-wide source selection problem?
- **CQ33** [O]: What models must be invoked to evaluate a candidate solution?

### Provenance and metadata

- **CQ34** [O]: When was the model/data for Node N last updated?
- **CQ35** [O]: What is the source of the regulatory limits for Parameter P?
- **CQ36** [O]: Who is responsible for maintaining Model M?

### Regulatory compliance and sampling

- **CQ37** [O]: What are all the regulatory violations recorded in the system? → [SPARQL](sparql/cq37_find_violations.rq)
- **CQ38** [O]: What is the chain of custody for Sample S (collection point, method, equipment, timestamp)? → [SPARQL](sparql/cq38_sample_chain_of_custody.rq)
- **CQ39** [O]: What is the calculated pollutant load for Parameter P at Discharge Point D? → [SPARQL](sparql/cq39_load_calculation.rq)
- **CQ40** [O]: What sampling points exist in the system and what are their types (influent, effluent, process, ambient)? → [SPARQL](sparql/cq40_sampling_points.rq)
