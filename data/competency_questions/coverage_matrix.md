# Competency Question Coverage Matrix

| CQ | Question | Status | Notes | Last Updated |
|----|----------|--------|-------|--------------|
| CQ1 | What are all the nodes (plants, sources, junctions, sinks) in a given catchment? | ✓ Full | Can query WaterSystemComponent hierarchy with typed classification | 2025-12-16 |
| CQ2 | What flows connect Node A to Node B? | ✗ None | Need to define flowsTo property in properties.ttl | 2025-12-16 |
| CQ3 | What are the possible input sources for Plant X? | ◐ Partial | Can identify source types but not flow connections | 2025-12-16 |
| CQ4 | What downstream nodes receive effluent from Plant X? | ✗ None | Requires flow topology properties | 2025-12-16 |
| CQ5 | What is the complete flow path from Source S to Sink K? | ✗ None | Requires transitive flow reasoning | 2025-12-16 |
| CQ6 | What unit processes comprise the treatment train at Plant X? | ◐ Partial | Can identify treatment units but not internal processes | 2025-12-16 |
| CQ7 | What is the sequence/topology of unit processes within Plant X? | ✗ None | Requires process modeling and sequencing | 2025-12-16 |
| CQ8 | What treatment technologies are available for a given contaminant removal objective? | ✗ None | Requires technology-capability relationships | 2025-12-16 |
| CQ9 | What is the design capacity of Unit Process U? | ✗ None | Requires qualities module for parameters | 2025-12-16 |
| CQ10 | What quality parameters characterize the water at Node N? | ✗ None | Requires qualities and observations modeling | 2025-12-16 |
| CQ11 | What are the regulatory limits for Parameter P for Reuse Category R? | ✗ None | Requires regulatory information modeling | 2025-12-16 |
| CQ12 | Does the effluent quality at Plant X meet the requirements for agricultural reuse? | ✗ None | Requires quality comparison reasoning | 2025-12-16 |
| CQ13 | What contaminants are present in Source S above threshold T? | ✗ None | Requires quality measurements and thresholds | 2025-12-16 |
| CQ14 | Is Stream S classified as greywater or blackwater? | ◐ Partial | Can classify fixtures by type but not stream water quality | 2025-12-16 |
| CQ15 | What sources in the catchment are classified as fit-for-purpose Category C? | ✗ None | Requires fitness-for-purpose classification | 2025-12-16 |
| CQ16 | What treatment is required to upgrade water from Quality Class Q1 to Q2? | ✗ None | Requires treatment capability mapping | 2025-12-16 |
| CQ17 | What computational model is associated with Unit Process U? | ✗ None | Requires information entities module | 2025-12-16 |
| CQ18 | What are the input variables for Model M? | ✗ None | Requires model metadata structure | 2025-12-16 |
| CQ19 | What are the output variables for Model M? | ✗ None | Requires model metadata structure | 2025-12-16 |
| CQ20 | Which parameters of Model M are fixed vs. manipulable (decision variables)? | ✗ None | Requires roles module for decision variables | 2025-12-16 |
| CQ21 | What is the valid range for Parameter P in Model M? | ✗ None | Requires parameter constraint modeling | 2025-12-16 |
| CQ22 | How is Model M invoked? (API endpoint, function signature, agent reference) | ✗ None | Requires model protocol specification | 2025-12-16 |
| CQ23 | What mass/quality balances does Model M compute? | ✗ None | Requires model capability description | 2025-12-16 |
| CQ24 | What time resolution does Model M operate at? (steady-state, dynamic, event-based) | ✗ None | Requires temporal modeling | 2025-12-16 |
| CQ25 | What optimization agents are available in the system? | ✗ None | Requires agent metadata modeling | 2025-12-16 |
| CQ26 | What objective function types can Agent A handle? (linear, quadratic, nonlinear, multi-objective) | ✗ None | Requires agent capability modeling | 2025-12-16 |
| CQ27 | What constraint types can Agent A handle? (equality, inequality, logical, chance) | ✗ None | Requires agent capability modeling | 2025-12-16 |
| CQ28 | What solvers does Agent A have access to? | ✗ None | Requires agent-solver relationships | 2025-12-16 |
| CQ29 | How is Agent A invoked? | ✗ None | Requires agent protocol specification | 2025-12-16 |
| CQ30 | For a given objective (minimize energy, maximize reuse, minimize cost), which nodes have relevant decision variables? | ✗ None | Requires decision variable mapping | 2025-12-16 |
| CQ31 | What constraints link the outputs of upstream nodes to the inputs of downstream nodes? | ✗ None | Requires flow constraint modeling | 2025-12-16 |
| CQ32 | What is the set of decision variables for a catchment-wide source selection problem? | ✗ None | Requires optimization problem formulation | 2025-12-16 |
| CQ33 | What models must be invoked to evaluate a candidate solution? | ✗ None | Requires model dependency modeling | 2025-12-16 |
| CQ34 | When was the model/data for Node N last updated? | ✗ None | Requires provenance tracking | 2025-12-16 |
| CQ35 | What is the source of the regulatory limits for Parameter P? | ✗ None | Requires provenance and reference modeling | 2025-12-16 |
| CQ36 | Who is responsible for maintaining Model M? | ✗ None | Requires provenance and responsibility modeling | 2025-12-16 |

## Coverage Summary

**Current Status**: 1/36 CQs fully answerable (2.8%)  
**Partially Answerable**: 3/36 CQs (8.3%)  
**Not Answerable**: 32/36 CQs (88.9%)

### What's Working (✓ Full)
- **CQ1**: System topology enumeration through material entities classification

### What's Partially Working (◐ Partial)  
- **CQ3**: Can identify source types but not flow connections
- **CQ6**: Can identify treatment units but not internal processes  
- **CQ14**: Can classify fixtures by type but not stream water quality

### Next Priority Modules
1. **properties.ttl** - Define flow connections (CQ2, CQ4, CQ5)
2. **processes.ttl** - Model treatment operations (CQ6, CQ7)  
3. **qualities.ttl** - Water quality parameters (CQ9, CQ10, CQ13)
4. **information.ttl** - Model metadata (CQ17-CQ24)
5. **roles.ttl** - Decision variables and agent metadata (CQ20, CQ25-CQ33)
6. **bridges/sosa_alignment.ttl** - Observations and measurements (CQ10, CQ12)