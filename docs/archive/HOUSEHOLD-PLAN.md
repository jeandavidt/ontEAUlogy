# Plan: Physics-Based Process Models for Household Case Study

## Context

The three household model services (MBR, RO, Infiltration) currently use analytical stubs — fixed removal fractions. The goal is to replace these with real physics-based implementations using scipy ODEs, add steady-state and dynamic simulation modes, add parameter calibration, link simulation runs to ontology **scenarios**, support **composite multi-step treatment unit** simulation, and ground all API I/O in the waterFRAME ontology (Turtle / JSON-LD).

**Library choice:** scipy (solve_ivp for dynamic ODEs, optimize.least_squares for calibration). No external framework needed — avoids QSDsan/numba Python version conflicts.

**Research finding:** The waterFRAME ontology already defines `wf:Scenario` (with `wf:BaselineScenario`, `wf:AlternativeScenario`, etc.) in `data/ontology_enhanced/modules/scenarios.ttl`. Treatment units can perform multiple processes (`wf:performsProcess` is multi-valued). A `wf:TreatmentTrain` concept is implicit but not yet formally defined.

---

## Key Architectural Concepts

### 1. Simulation Runs Linked to Scenarios
Every `/simulate` call produces a `wf:SimulationRun` instance in the response RDF. That run references the scenario it belongs to:
```turtle
case:MBR_Run_<id>  a wf:SimulationRun ;
    wf:inScenario  housecase1:Baseline_Scenario ;
    wf:producedBy  case:Membrane_bioreactor_Model ;
    wf:hasOutput   [ ... ] .
```
The scenario IRI is passed as an optional input field (`scenario_iri`). If omitted, a default baseline scenario IRI is used.

### 2. Multi-Step Treatment Unit Simulation
A treatment unit can have multiple sequential sub-steps, each with its own model (e.g., an MBR performs BiologicalOxidationProcess then MembraneFiltrationProcess). When a `/simulate` request targets a composite unit, three strategies are available:

| Strategy | Description | When to use |
|----------|-------------|-------------|
| **A — Cascade** | Sequential HTTP calls to each sub-model service; output of step N is input to step N+1 | Sub-models are independent services; default orchestrated approach |
| **B — Assembly** | Combine sub-model ODEs into one coupled system; solve jointly | Tight coupling between sub-steps (shared state variables); more accurate |
| **C — Lumped fallback** | Algebraic composed model using each component's known removal characteristics | Sub-model services unavailable; fast screening |

The strategy is selected via a `composition_strategy` field in the request, defaulting to `"cascade"`.

A new `/compose` endpoint accepts a list of sub-unit IRIs (from the ontology) and returns a composed simulation result using the selected strategy.

---

## File Structure

```
src/household_water/
├── models/
│   ├── base.py               MODIFIED — parameters, simulate_sync, calibration support
│   ├── mbr.py                REPLACED — physics model
│   ├── ro.py                 REPLACED — physics model
│   └── infiltration.py       REPLACED — physics model
│
├── physics/                  NEW
│   ├── __init__.py
│   ├── mbr_odes.py           MBR ODE system + analytical steady-state
│   ├── ro_equations.py       Solution-diffusion + concentration polarisation
│   └── infiltration_equations.py  Simplified Richards + first-order decay
│
├── schemas/                  NEW
│   ├── __init__.py
│   ├── common.py             SimulationMode, DynamicConfig, ScenarioRef,
│   │                         CalibrationRequest/Result, CompositionRequest
│   ├── mbr_schemas.py        MBRInput v2, MBRSteadyOutput, MBRDynamicOutput, MBRParameters
│   ├── ro_schemas.py
│   └── infiltration_schemas.py
│
├── semantic/                 NEW
│   ├── __init__.py
│   ├── namespaces.py         rdflib Namespace objects + field→IRI mappings
│   ├── io_parser.py          Turtle/JSON-LD request → plain dict
│   └── io_serializer.py      output dict → Turtle / JSON-LD (with scenario IRI)
│
└── composition/              NEW
    ├── __init__.py
    ├── cascade.py            Strategy A — sequential HTTP calls between sub-models
    ├── assembly.py           Strategy B — coupled ODE assembly
    └── lumped.py             Strategy C — algebraic fallback

tests/
├── test_physics_mbr.py       NEW
├── test_physics_ro.py        NEW
├── test_physics_infiltration.py  NEW
├── test_semantic_io.py       NEW
└── test_composition.py       NEW
```

---

## Step 1 — Dependencies (`pyproject.toml`)

File: `case_studies/household/pyproject.toml`

Add to `dependencies`:
```toml
"scipy>=1.13.0",
"numpy>=1.26.0",
```

---

## Step 2 — `semantic/` Package

### `semantic/namespaces.py`
```python
WF   = Namespace("https://ugentbiomath.github.io/waterframe#")
CAP  = Namespace("https://ugentbiomath.github.io/waterframe/capability#")
HC1  = Namespace("https://ugentbiomath.github.io/ontology/index.ttl#")
CASE = Namespace("https://w3id.org/waterframe/case/household/")
```

Field→IRI mappings per model, e.g.:
```python
MBR_VAR_IRIS = {
    "effluent_cod_mg_l": WF.EffluentCOD,
    "biomass_x_mg_l":    WF.BiomassConcentration,
    "dissolved_o2_mg_l": WF.DissolvedOxygen,
    "cod_removal_pct":   WF.CODRemovalEfficiency,
    "energy_kwh_d":      WF.EnergyConsumption,
    "sludge_production_kg_d": WF.SludgeProduction,
}
```

### `semantic/io_serializer.py`
```python
def serialize_outputs_to_turtle(
    outputs: Dict, model_id: str, var_iris: Dict,
    simulation_mode: str, scenario_iri: str = None, run_id: str = None
) -> str:
```
Graph shape:
```turtle
case:MBR_Run_<id>  a wf:SimulationRun ;
    wf:hasSimulationMode "steady_state" ;
    wf:inScenario        <scenario_iri_or_default> ;
    wf:producedBy        case:Membrane_bioreactor_Model ;
    wf:hasOutput [
        a wf:StateVariable ;
        wf:parameterName "effluent_cod_mg_l" ;
        rdf:type  wf:EffluentCOD ;
        rdf:value "17.5"^^xsd:float ;
        wf:hasUnit "mg/L"
    ] .
```

`params_to_turtle(model_id, params_dict)` → `wf:Parameter` triples.

### `semantic/io_parser.py`
SPARQL-based extraction from parsed Turtle/JSON-LD:
```sparql
SELECT ?name ?value WHERE {
    ?input wf:parameterName ?name ; rdf:value ?value .
}
```
Fallback: iterate triples matching WF property local names.

---

## Step 3 — `schemas/` Package

### `schemas/common.py`
```python
class SimulationMode(str, Enum):
    steady_state = "steady_state"
    dynamic = "dynamic"

class CompositionStrategy(str, Enum):
    cascade  = "cascade"    # A: sequential HTTP calls
    assembly = "assembly"   # B: coupled ODE
    lumped   = "lumped"     # C: algebraic fallback

class DynamicConfig(BaseModel):
    t_start: float = 0.0
    t_end: float = 10.0       # days
    n_points: int = 100

class CalibrationObservation(BaseModel):
    inputs: Dict[str, float]
    observed_outputs: Dict[str, float]

class CalibrationRequest(BaseModel):
    observations: List[CalibrationObservation]   # min 2
    parameters_to_fit: List[str]
    method: str = "least_squares"

class CalibrationResult(BaseModel):
    calibrated_parameters: Dict[str, float]
    parameter_uncertainties: Dict[str, float]
    residual_norm: float
    converged: bool
    n_iterations: int
    semantic_turtle: Optional[str] = None

class CompositionRequest(BaseModel):
    """Request to simulate a multi-step treatment unit."""
    unit_iri: str                               # IRI of the composite treatment unit
    sub_unit_iris: List[str]                    # ordered list of sub-unit IRIs
    sub_unit_endpoints: List[str]               # corresponding HTTP endpoints (for cascade)
    inputs: Dict[str, float]                    # feed stream to first unit
    simulation_mode: SimulationMode = SimulationMode.steady_state
    dynamic_config: Optional[DynamicConfig] = None
    composition_strategy: CompositionStrategy = CompositionStrategy.cascade
    scenario_iri: Optional[str] = None
```

Per-model schemas add `simulation_mode`, `dynamic_config`, `parameters` (physics override), and `scenario_iri` to inputs, and split outputs into Steady / Dynamic variants.

---

## Step 4 — Physics Engines

### `physics/mbr_odes.py` — MBR Physics

**State:** S (substrate mg COD/L), X (biomass VSS mg/L), So (DO mg/L)

**ODE system (Monod, CSTR, membrane retains all X):**
```
dS/dt  = Q_in/V*(S_in - S) - mu_max*S/(K_s+S)*X/Y
dX/dt  = mu_max*S/(K_s+S)*X - b*X - Q_waste/V*X
dSo/dt = K_La*(So_sat - So) - mu*X*(1-Y)/Y*1.07
```

**Analytical steady-state (closed-form):**
```
mu_ss = b + Q_waste/V
S*    = K_s * mu_ss / (mu_max - mu_ss)
X*    = Y*(Q_in/V)*(S_in - S*) / mu_ss
So*   = So_sat - mu_ss*X*(1-Y)/Y*1.07 / K_La
```

**Membrane flux (Darcy):** `Jw = TMP_Pa / (mu_water * R_m)`; `Q_permeate = Jw * A_m * 86400`

**Calibratable params + bounds:**
| Param | Default | Low | High |
|-------|---------|-----|------|
| mu_max | 6.0 | 0.1 | 20.0 |
| K_s | 20.0 | 1.0 | 200.0 |
| Y | 0.67 | 0.3 | 0.8 |
| b | 0.15 | 0.01 | 1.0 |

---

### `physics/ro_equations.py` — RO Physics

**Solution-diffusion + concentration polarisation (iterative):**
```
C_m     = C_feed * exp(Jw / k_m)           # film model
delta_pi = pi(C_m) - pi(C_p)              # osmotic pressure diff (van't Hoff)
Jw      = A * (TMP_Pa - delta_pi_Pa)       # water flux m/s
Js      = B * (C_m - C_p)                  # salt flux m/s
C_p     = Js / Jw                           # iterate to convergence
```

**New inputs:** `applied_pressure_bar` (default 8.0), `membrane_area_m2` (default 2.0)

**Dynamic mode:** concentration polarisation ODE.

**Calibratable params:** A [1e-9–1e-5], B [1e-10–1e-4]

---

### `physics/infiltration_equations.py` — Infiltration Physics

**Steady-state (plug-flow first-order decay):**
```
q_inf   = min(Q_in/area_m2, K_sat)
HRT     = theta_eff * soil_depth / q_inf
C_X_out = C_X_in * exp(-k_X * HRT)
```

**Dynamic ODE (simplified Richards + advective transport):**
```
dtheta/dt = q/L - K(theta)/L           # K(theta) = K_sat * Se^(2+3/n)
dC_X/dt   = (q/L)*(C_in - C) - k_X*C
```

**New inputs:** `area_m2` (default 10.0), `soil_depth_m` (default 1.0)

**Calibratable params:** k_COD [0.01–10], k_TSS [0.01–20], k_NH4 [0.01–5]

---

## Step 5 — `base.py` Additions

New state on `BaseHouseholdModel`:
- `_parameters: Dict[str, float]` — current parameter values (initially defaults)
- `_PARAM_BOUNDS: Dict[str, Tuple[float, float]]` — defined per subclass
- `_default_scenario_iri: str` — e.g. `"https://ugentbiomath.github.io/ontology/index.ttl#Baseline_Scenario"`

New methods:
- `get_default_params_dict() → Dict`
- `update_parameters(params: Dict)`
- `get_param_bounds(names) → Tuple[List, List]`
- `simulate_sync(inputs: Dict, params_override: Dict) → Dict` — synchronous, called inside scipy callbacks
- `params_to_turtle(params: Dict) → str`

---

## Step 6 — Model Service Updates

### New endpoints (all three services):
```
GET  /capabilities     → JSON-LD: SteadyStateSimulation, DynamicSimulation,
                         MassBalance, WaterQualityPrediction, Calibration
GET  /parameters       → JSON (or Turtle via Accept: text/turtle)
POST /calibrate        → CalibrationRequest → CalibrationResult
```

### Extended `/simulate` — content-type negotiation:
```python
@app.post("/simulate")
async def simulate(request: Request):
    ct     = request.headers.get("content-type", "application/json")
    accept = request.headers.get("accept",       "application/json")

    if "text/turtle" in ct:
        inputs = parse_turtle_to_dict(await request.body(), FIELD_MAPPING)
    elif "application/ld+json" in ct:
        inputs = parse_jsonld_to_dict(await request.body(), FIELD_MAPPING)
    else:
        inputs = ModelInput(**(await request.json())).model_dump()

    result = _model.simulate_sync(inputs, inputs.pop("parameters", {}))

    scenario_iri = inputs.get("scenario_iri")
    mode = inputs.get("simulation_mode", "steady_state")

    if "text/turtle" in accept:
        ttl = serialize_outputs_to_turtle(result, model_id, VAR_IRIS, mode, scenario_iri)
        return PlainTextResponse(ttl, media_type="text/turtle")
    elif "application/ld+json" in accept:
        g = Graph().parse(data=ttl, format="turtle")
        return JSONResponse(json.loads(g.serialize(format="json-ld")),
                           media_type="application/ld+json")
    return JSONResponse(result | {"simulation_run_iri": f"case:{model_id}_Run_{uuid4().hex[:8]}"})
```

### Calibration (same pattern for all three):
```python
@app.post("/calibrate", response_model=CalibrationResult)
async def calibrate(body: CalibrationRequest):
    result = least_squares(
        _calibration_residuals,
        x0=[_model._parameters[n] for n in body.parameters_to_fit],
        bounds=_model.get_param_bounds(body.parameters_to_fit),
        args=(body.parameters_to_fit, body.observations, _model.simulate_sync),
        method='trf', max_nfev=1000,
    )
    # Uncertainty from Jacobian: cov = inv(J^T J) * cost / (n_obs - n_par)
    # Update model._parameters with calibrated values
    # Return CalibrationResult with semantic_turtle (wf:Parameter triples)
```

---

## Step 7 — `composition/` Package

### `composition/cascade.py` — Strategy A
```python
async def cascade_simulate(request: CompositionRequest) -> Dict:
    """
    Sequential HTTP calls: output of step N fed as input to step N+1.
    Uses httpx.AsyncClient.
    Merges cumulative outputs (last step's effluent = final output).
    Records each intermediate SimulationRun IRI.
    """
    current_inputs = dict(request.inputs)
    run_iris = []
    for sub_iri, endpoint in zip(request.sub_unit_iris, request.sub_unit_endpoints):
        payload = {**current_inputs,
                   "simulation_mode": request.simulation_mode,
                   "scenario_iri": request.scenario_iri}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{endpoint}/simulate", json=payload, timeout=30)
        resp.raise_for_status()
        step_output = resp.json()
        run_iris.append(step_output.get("simulation_run_iri"))
        # Map step output to next step's input (field name translation via ontology)
        current_inputs = _map_output_to_next_input(step_output, sub_iri)
    return {"final_outputs": current_inputs, "step_run_iris": run_iris}
```

### `composition/assembly.py` — Strategy B
```python
def assemble_and_solve(request: CompositionRequest) -> Dict:
    """
    Combine ODE systems for each sub-unit into one joint system.
    Currently supports MBR+membrane (BiologicalOxidation + MembraneFiltration).

    The MBR already models both processes in one ODE; this strategy is
    extensible to cases like pre-treatment + MBR (e.g., screening + bioreactor).

    Implementation:
      1. Look up sub-unit physics modules by IRI pattern
      2. Concatenate state vectors: y = [y_unit1, y_unit2, ...]
      3. Couple via outlet/inlet linkage terms in combined rhs
      4. Call solve_ivp on assembled system
    """
```

### `composition/lumped.py` — Strategy C
```python
def lumped_simulate(request: CompositionRequest) -> Dict:
    """
    Algebraic composed model:
    - For each sub-unit, use known default removal efficiencies
    - Apply sequentially: C_out_N = C_in_N * (1 - removal_fraction_N)
    - No HTTP calls, no ODE solving — instant fallback
    """
```

### New `/compose` endpoint (added to each model service OR a new orchestrator endpoint):
```python
@app.post("/compose")
async def compose(body: CompositionRequest):
    if body.composition_strategy == "cascade":
        result = await cascade_simulate(body)
    elif body.composition_strategy == "assembly":
        result = assemble_and_solve(body)
    else:
        result = lumped_simulate(body)
    return JSONResponse(result)
```

**Note:** The `/compose` endpoint is best placed on the **household orchestrator** (or a new household coordinator service at port 8100) so it can call sub-models by HTTP. For now, add it to each individual model service with the understanding that `sub_unit_endpoints` are caller-supplied.

---

## Step 8 — Ontology Additions

Declare inline in `base.py` TTL generation and in `semantic/namespaces.py`. Also propose additions to the household case TTL or `scenarios.ttl`.

**New `cap:` classes:**
```turtle
cap:DynamicSimulation  rdfs:subClassOf wf:ModelCapability .
cap:Calibration        rdfs:subClassOf wf:ModelCapability .
```

**New `wf:` classes:**
```turtle
wf:SimulationRun    rdfs:subClassOf wf:Process .
wf:CalibrationRun   rdfs:subClassOf wf:Process .
wf:CompositeSimulationRun rdfs:subClassOf wf:SimulationRun .
wf:StateVariable    rdfs:subClassOf wf:ModelOutput .
wf:KPI              rdfs:subClassOf wf:ModelOutput .
wf:TreatmentTrain   rdfs:subClassOf wf:WaterSystemComponent .
```

**New `wf:` properties:**
```turtle
wf:hasSimulationMode       a owl:DatatypeProperty .
wf:inScenario              a owl:ObjectProperty ; rdfs:range wf:Scenario .
wf:parameterUncertainty    a owl:DatatypeProperty .
wf:residualNorm            a owl:DatatypeProperty .
wf:composedOf              a owl:ObjectProperty ; rdfs:domain wf:TreatmentTrain .
wf:hasCompositionStrategy  a owl:DatatypeProperty .
wf:stepRunIRI              a owl:DatatypeProperty .
```

**Household instance — add a baseline scenario:**
In `data/ontology/instances/household_case1.ttl`:
```turtle
housecase1:Baseline_Scenario a wf:BaselineScenario ;
    wf:scenarioName "Household Case 1 — Baseline" ;
    wf:scenarioComponent housecase1:Membrane_bioreactor,
                         housecase1:Reverse_osmosis,
                         housecase1:Infiltration .
```

---

## Implementation Sequence

1. Add `scipy` + `numpy` to `pyproject.toml` ✅
2. Create `semantic/` package (namespaces → serializer → parser) ✅
3. Create `schemas/` package (common → per-model) ✅
4. Create `physics/mbr_odes.py` + `test_physics_mbr.py` ✅
5. Update `base.py` (parameter management, simulate_sync, default scenario IRI) ✅
6. Update `mbr.py` (physics, new endpoints, content negotiation) + update `test_mbr.py` ✅
7. Create `physics/ro_equations.py` + update `ro.py` + `test_physics_ro.py` ✅
8. Create `physics/infiltration_equations.py` + update `infiltration.py` + `test_physics_infiltration.py` ✅
9. Create `composition/` package (cascade → assembly → lumped) + `test_composition.py` ✅
10. Add `/compose` endpoint to services ✅
11. Add household baseline scenario to instance TTL ✅
12. Add `test_semantic_io.py` ✅
13. Final: `pytest tests/` all green ✅

---

## Critical Files

| File | Action |
|------|--------|
| `case_studies/household/pyproject.toml` | Add scipy, numpy |
| `case_studies/household/src/household_water/models/base.py` | Add parameter mgmt + calibration support |
| `case_studies/household/src/household_water/models/mbr.py` | Replace with physics model |
| `case_studies/household/src/household_water/models/ro.py` | Replace with physics model |
| `case_studies/household/src/household_water/models/infiltration.py` | Replace with physics model |
| `data/ontology/instances/household_case1.ttl` | Add baseline scenario instance |

---

## Verification

**Unit tests (no services):**
```bash
cd case_studies/household
pytest tests/test_physics_*.py tests/test_semantic_io.py -v
```

**Integration tests (services running):**
```bash
# Start services
python -m household_water.runners.model_runner --model mbr
python -m household_water.runners.model_runner --model ro
python -m household_water.runners.model_runner --model infiltration

pytest tests/test_mbr.py tests/test_ro.py tests/test_infiltration.py tests/test_composition.py -v
```

**Manual spot checks:**
```bash
# Turtle output with scenario IRI
curl -X POST http://localhost:8101/simulate \
  -H "Accept: text/turtle" \
  -d '{"simulation_mode":"steady_state","scenario_iri":"https://ugentbiomath.github.io/ontology/index.ttl#Baseline_Scenario"}'
# Expect: wf:inScenario triple present, wf:SimulationRun type

# Dynamic simulation
curl -X POST http://localhost:8101/simulate \
  -d '{"simulation_mode":"dynamic","dynamic_config":{"t_end":5,"n_points":50}}'
# Expect: time_days array of length 50, substrate_s_mg_l decreases toward S*

# Calibration
curl -X POST http://localhost:8101/calibrate \
  -d '{"observations":[{"inputs":{"influent_flow_m3d":1.5,"influent_cod_mg_l":350},"observed_outputs":{"effluent_cod_mg_l":17}},{"inputs":{"influent_flow_m3d":2,"influent_cod_mg_l":400},"observed_outputs":{"effluent_cod_mg_l":20}}],"parameters_to_fit":["mu_max","K_s"]}'
# Expect: converged:true, semantic_turtle contains wf:Parameter

# Cascade composition (MBR → RO chain)
curl -X POST http://localhost:8101/compose \
  -d '{"unit_iri":"...","sub_unit_iris":["...MBR","...RO"],"sub_unit_endpoints":["http://localhost:8101","http://localhost:8102"],"inputs":{"influent_flow_m3d":1.5,"influent_cod_mg_l":350},"composition_strategy":"cascade"}'
# Expect: final_outputs includes RO permeate quality, step_run_iris has 2 entries

# Lumped fallback (no services needed)
curl -X POST http://localhost:8101/compose \
  -d '{...same as above but "composition_strategy":"lumped"}'
# Expect: instant response, algebraic removal applied sequentially
```

**Key assertions:**
- MBR physics: `effluent_cod_mg_l` varies with `influent_flow_m3d` (not fixed 5%)
- Calibration: returned params differ from defaults; `converged: true`
- Turtle: parseable by rdflib; contains `wf:SimulationRun`, `wf:inScenario`, `wf:StateVariable`
- Cascade: step 2 receives step 1's effluent quality as its feed
- Lumped: consistent with (but faster than) cascade for default parameters
