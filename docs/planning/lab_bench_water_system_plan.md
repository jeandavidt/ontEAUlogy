# Lab Bench Water System - Implementation Plan

## Executive Summary

This plan transforms the current stub-based Ghent case study into a fully functional **Lab Bench Water System** that demonstrates the ontEAUlogy's ability to support decision-making for urban water infrastructure. The system will serve as both a demonstration platform and a testbed for ontology-driven water system analysis.

**Current State**: Functional architecture with stubs, UI interaction issues, no real physics
**Target State**: Working end-to-end system with real-ish physics, working UI, decision support workflows

---

## Phase 1: Fix Critical UI Bugs (Priority: HIGH)

### 1.1 SPARQL Example Selector Not Populating Query Field

**Problem**: Clicking example queries in the dropdown doesn't populate the text area
**Root Cause**: Streamlit's `on_change` callback executes before the text area is re-rendered

**Solution** ([`query_panel.py`](case_studies/ghent/src/ghent_water/frontend/components/query_panel.py)):
```python
# Current problematic pattern:
st.selectbox(..., on_change=on_example_select)

# Fix: Use value_callback to ensure proper state update
st.selectbox(
    "Example Queries",
    options=options,
    index=default_idx,
    key="sparql_example_selector",
    on_change=on_example_select,
)
```

**Better Fix**: Use session state more directly:
```python
def on_example_select():
    example_name = st.session_state.sparql_example_selector
    if example_name != "Custom Query" and example_name in EXAMPLE_SPARQL_QUERIES:
        st.session_state.sparql_editor = EXAMPLE_SPARQL_QUERIES[example_name]
    else:
        st.session_state.sparql_editor = ""
```

### 1.2 Natural Language Example Questions Not Populating Input

**Problem**: Clicking example question chips doesn't populate the text input
**Root Cause**: Button click handlers run before the text_input is re-evaluated

**Solution** ([`query_panel.py`](case_studies/ghent/src/ghent_water/frontend/components/query_panel.py)):
```python
# Current:
if st.button(question, key=f"nl_example_{i}"):
    st.session_state.nl_question_input = question
    st.rerun()

# Fix: Use st.feedback or st.pills for better UX, or restructure the callback
# Option 1: Use form pattern
with st.form("nl_form"):
    cols = st.columns(2)
    for i, question in enumerate(EXAMPLE_NL_QUESTIONS):
        with cols[i % 2]:
            if st.form_submit_button(question):
                st.session_state.nl_question_input = question

    question_text = st.text_input("Your question:", key="nl_question_input")
```

### 1.3 "Run Simulation" Button Not Working

**Problem**: Clicking "Run Simulation" on an entity does nothing visible
**Root Cause**: Multiple issues:
1. Entity status in `map_view.py` ENTITIES dict doesn't get updated
2. No visual feedback during/after simulation
3. Simulation status panel doesn't reflect entity-level status

**Solution**:

1. **Update entity status when simulation runs** ([`app.py`](case_studies/ghent/src/ghent_water/frontend/app.py)):
```python
def handle_run_simulation(entity_id: str) -> None:
    # ... existing code ...
    new_job = {
        "job_id": result.get("job_id"),
        "model_name": entity_id.upper(),
        "status": result.get("status", "pending"),
        "progress": 0,
        "started_at": datetime.now().isoformat(),
    }
    st.session_state.jobs.append(new_job)
    
    # CRITICAL: Update entity status in map
    from ghent_water.frontend.components.map_view import ENTITIES
    if entity_id in ENTITIES:
        ENTITIES[entity_id]["status"] = "running"
    
    st.success(f"Simulation started! Job ID: {result.get('job_id')}")
    st.rerun()
```

2. **Add polling for job completion** ([`simulation_status.py`](case_studies/ghent/src/ghent_water/frontend/components/simulation_status.py)):
```python
def _render_job_card(job: dict) -> None:
    # ... existing code ...
    # Update entity status when job completes
    if job["status"] == "completed" and "model_name" in job:
        from ghent_water.frontend.components.map_view import ENTITIES
        entity_id = job["model_name"].lower()
        if entity_id in ENTITIES:
            ENTITIES[entity_id]["status"] = "idle"
```

---

## Phase 2: Working Simulation Pipeline (Priority: HIGH)

### 2.1 Ensure All Services Start Correctly

**Current Issues**:
- `run_all.py` may have timing issues between service starts
- No health check verification before next service starts

**Solution** ([`run_all.py`](case_studies/ghent/scripts/run_all.py)):
```python
def wait_for_service(url: str, timeout: float = 10.0) -> bool:
    """Wait for a service to become available."""
    import httpx
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = httpx.get(f"{url}/health", timeout=1.0)
            if resp.status_code == 200:
                return True
        except httpx.ConnectError:
            pass
        time.sleep(0.5)
    return False

# In main():
# After starting orchestrator
wait_for_service(f"http://localhost:{args.orchestrator_port}")
# After starting each model
for model_name, port, _ in models_to_run:
    wait_for_service(f"http://localhost:{port}")
```

### 2.2 Connect Orchestrator to Models

**Current Issue**: Models need to register with orchestrator, but registration may fail

**Solution** ([`simulation.py`](case_studies/ghent/src/ghent_water/orchestrator/routers/simulation.py)):
```python
# Add startup event to orchestrator that auto-discovers running models
@router.on_event("startup")
async def discover_models():
    """Auto-discover and register all running models."""
    for model_id, port in MODEL_PORTS.items():
        try:
            await try_register_model(model_id)
        except Exception as e:
            logger.warning(f"Could not auto-register {model_id}: {e}")
```

### 2.3 Improve Job Tracking

**Current Issue**: Job status updates aren't reliable

**Solution** ([`model_registry.py`](case_studies/ghent/src/ghent_water/orchestrator/services/model_registry.py)):
```python
class ModelRegistry:
    """Enhanced registry with better job tracking."""
    
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._jobs: Dict[str, JobInfo] = {}
    
    def create_job(self, model_id: str, request: Dict) -> str:
        """Create job with timestamp and initial state."""
        job_id = str(uuid.uuid4())[:8]
        self._jobs[job_id] = {
            "job_id": job_id,
            "model_id": model_id,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "request": request,
        }
        return job_id
    
    def update_job_status(self, job_id: str, status: str, **updates):
        """Update job status with progress tracking."""
        if job_id in self._jobs:
            self._jobs[job_id].update({
                "status": status,
                "updated_at": datetime.now().isoformat(),
                **updates,
            })
```

---

## Phase 3: Enhance Stub Models (Priority: MEDIUM)

### 3.1 Add Realistic Parameter Ranges

**Current Issue**: Stub models return arbitrary values

**Solution**: Enhance each stub to use realistic ranges from the planning document:
- DWP models: Use actual treatment efficiencies for each process step
- WWTP models: Use realistic removal rates (BOD 85-95%, COD 80-90%, etc.)
- Industry models: Use sector-specific water quality profiles
- River model: Use Streeter-Phelps dissolved oxygen balance

**Implementation** ([`models/stubs/wwtp.py`](case_studies/ghent/src/ghent_water/models/stubs/wwtp.py)):
```python
class WastewaterTreatmentPlantStub:
    """Enhanced WWTP with realistic process modeling."""
    
    # Process-based treatment stages
    PROCESS_STAGES = {
        "primary": {"BOD": 0.30, "COD": 0.35, "TSS": 0.60, "TN": 0.15, "TP": 0.15},
        "secondary": {"BOD": 0.90, "COD": 0.85, "TSS": 0.92, "TN": 0.40, "TP": 0.25},
        "tertiary": {"BOD": 0.95, "COD": 0.92, "TSS": 0.97, "TN": 0.65, "TP": 0.85},
    }
    
    def simulate(self, inputs: Dict) -> Dict:
        """Simulate each treatment stage sequentially."""
        # Apply each stage's removal efficiency
        current = influent.copy()
        for stage in ["primary", "secondary", "tertiary"]:
            efficiency = self.PROCESS_STAGES[stage]
            current = self._apply_efficiency(current, efficiency)
        return current
```

### 3.2 Add Scenario Support

**Current Issue**: Models only run baseline scenarios

**Solution**: Add scenario parameter support:
```python
class WWTPStub:
    async def simulate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        scenario = inputs.get("scenario", "baseline")
        
        if scenario == "high_load":
            # Increase influent concentrations
            inputs["influent_BOD"] *= 1.5
            inputs["influent_TSS"] *= 1.3
        elif scenario == "low_efficiency":
            # Reduce treatment efficiencies
            self.treatment_efficiencies = {k: v * 0.8 for k, v in self.treatment_efficiencies.items()}
```

### 3.3 Add Compliance Checking

**Current Issue**: No connection to regulatory limits

**Solution**: Add VLAREM II compliance check:
```python
VLAREM_II_LIMITS = {
    "BOD": 25,  # mg/L
    "COD": 125,
    "TSS": 35,
    "Total_N": 15,
    "Total_P": 2,
}

def check_compliance(effluent: Dict) -> Dict[str, bool]:
    """Check effluent against VLAREM II limits."""
    violations = {}
    for param, limit in VLAREM_II_LIMITS.items():
        if param in effluent:
            violations[param] = effluent[param] > limit
    return violations
```

---

## Phase 4: Natural Language Interface (Priority: MEDIUM)

### 4.1 Fix LLM SPARQL Translation

**Current Issue**: LLM endpoint returns demo data when API fails

**Solution** ([`llm_sparql.py`](case_studies/ghent/src/ghent_water/orchestrator/services/llm_sparql.py)):
```python
class LLMService:
    """LLM service for natural language to SPARQL translation."""
    
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key)
        self.ontology_context = self._load_ontology_context()
    
    def translate_to_sparql(self, question: str) -> Dict[str, Any]:
        """Translate natural language question to SPARQL."""
        prompt = f"""
        You are a SPARQL expert for a water system ontology.
        
        Ontology context:
        {self.ontology_context}
        
        Available entity types: DWP, WWTP, Industry, Residential, River
        Available parameters: BOD, COD, TSS, TN, TP, flow, capacity
        
        Translate this question to a SPARQL SELECT query:
        "{question}"
        
        Return JSON:
        {{
            "sparql_query": "SELECT ...",
            "requires_simulation": true/false,
            "entities_to_query": ["entity1", "entity2"]
        }}
        """
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
```

### 4.2 Add Sample Questions That Actually Work

**Solution**: Create a library of working questions with pre-defined queries:
```python
WORKING_QUESTIONS = {
    "What is the BOD at WWTP-1 effluent?": {
        "sparql": """SELECT ?value WHERE {
            ghent:WWTP1 wf:hasEffluent ?eff .
            ?eff wf:hasBOD ?value .
        }""",
        "requires_simulation": True,
        "model": "wwtp1",
    },
    "Which entities are in the upstream zone?": {
        "sparql": """SELECT ?entity ?name WHERE {
            ?entity wf:locatedInZone "upstream" ;
                    rdfs:label ?name .
        }""",
        "requires_simulation": False,
    },
    # Add more...
}
```

---

## Phase 5: Decision Support Workflows (Priority: MEDIUM)

### 5.1 Scenario Comparison

**Feature**: Compare results across different scenarios

**Implementation**:
```python
class ScenarioComparison:
    """Compare simulation results across scenarios."""
    
    async def compare(
        self, 
        entity_id: str, 
        scenarios: List[str]
    ) -> pd.DataFrame:
        """Run entity for multiple scenarios and return comparison."""
        results = []
        for scenario in scenarios:
            result = await self.run_simulation(entity_id, {"scenario": scenario})
            result["scenario"] = scenario
            results.append(result)
        
        return pd.DataFrame(results)
```

### 5.2 Sensitivity Analysis

**Feature**: Show how outputs change with input variations

**Implementation**:
```python
class SensitivityAnalyzer:
    """Perform sensitivity analysis on model parameters."""
    
    async def analyze(
        self, 
        entity_id: str, 
        parameter: str, 
        range_pct: float = 0.2
    ) -> Dict:
        """Vary parameter by ±range_pct and measure output changes."""
        base = await self.run_simulation(entity_id, {})
        base_value = base.get(parameter, 0)
        
        variations = [-range_pct, -range_pct/2, 0, range_pct/2, range_pct]
        results = []
        
        for pct in variations:
            inputs = {parameter: base_value * (1 + pct)}
            result = await self.run_simulation(entity_id, inputs)
            results.append({
                "pct_change": pct * 100,
                "output": result.get("effluent_BOD", 0),
            })
        
        return {"parameter": parameter, "sensitivity": results}
```

### 5.3 Compliance Dashboard

**Feature**: Visual overview of regulatory compliance

**Implementation**:
```python
class ComplianceDashboard:
    """Display compliance status for all entities."""
    
    def render(self, results: List[Dict]) -> None:
        """Render compliance overview."""
        for result in results:
            violations = check_compliance(result)
            status = "✅ Compliant" if not any(violations.values()) else "❌ Violations"
            st.markdown(f"**{result['entity']}**: {status}")
            
            for param, is_violation in violations.items():
                if is_violation:
                    limit = VLAREM_II_LIMITS.get(param)
                    actual = result.get(param)
                    st.error(f"  - {param}: {actual} > {limit}")
```

---

## Phase 6: Integration with Real Physics Engines (Priority: LOW)

### 6.1 QSDsan Integration (Future)

Research indicates QSDsan provides:
- Built-in treatment process models
- Life cycle assessment
- Uncertainty quantification

**Implementation path**:
1. Create `models/qsdsan/wwtp.py` with QSDsan process models
2. Map QSDsan outputs to waterFRAME ontology terms
3. Create adapter layer for the `/simulate` endpoint

### 6.2 Ribasim Integration (Future)

Ribasim provides:
- River basin simulation
- Water allocation
- Reservoir operations

**Implementation path**:
1. Create `models/ribasim/river.py` with Ribasim integration
2. Use Ribasim's built-in water quality modules
3. Map outputs to river segment descriptions

---

## Implementation Roadmap

### Sprint 1: Critical Fixes (Week 1)
- [ ] Fix SPARQL example selector
- [ ] Fix NL example questions
- [ ] Fix "Run Simulation" button
- [ ] Add service health checks to `run_all.py`

### Sprint 2: Working Pipeline (Week 2)
- [ ] Auto-register models at startup
- [ ] Fix job status tracking
- [ ] Add visual status updates to map
- [ ] Document running instructions

### Sprint 3: Enhanced Models (Week 3)
- [ ] Add process-based treatment modeling
- [ ] Add scenario support
- [ ] Add compliance checking
- [ ] Add realistic parameter ranges

### Sprint 4: Decision Support (Week 4)
- [ ] Scenario comparison feature
- [ ] Sensitivity analysis
- [ ] Compliance dashboard
- [ ] Demo workflows

---

## Testing Plan

### Unit Tests
- Stub model simulations return expected output structure
- SPARQL queries execute without syntax errors
- Natural language translation produces valid JSON

### Integration Tests
- Frontend → Orchestrator communication
- Orchestrator → Model communication
- Job creation through full pipeline

### User Acceptance Tests
- Click "Run Simulation" → Status changes to "running" → "completed"
- Click example query → Query field populates → Results display
- Ask NL question → SPARQL generated → Results returned

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| UI Responsiveness | All clicks work within 1s | Manual testing |
| Simulation Success Rate | >95% of runs complete | Automated test suite |
| Query Success Rate | >90% return results | Log analysis |
| Decision Support Workflows | 3+ workflows implemented | Feature checklist |
| Documentation | All features documented | Docs completeness |

---

## Appendix A: File Reference

| File | Purpose | Changes Needed |
|------|---------|----------------|
| [`query_panel.py`](case_studies/ghent/src/ghent_water/frontend/components/query_panel.py) | SPARQL/NL query interface | Fix example selection callbacks |
| [`entity_details.py`](case_studies/ghent/src/ghent_water/frontend/components/entity_details.py) | Entity info panel | Update status display |
| [`simulation_status.py`](case_studies/ghent/src/ghent_water/frontend/components/simulation_status.py) | Job tracking | Fix status updates |
| [`app.py`](case_studies/ghent/src/ghent_water/frontend/app.py) | Main Streamlit app | Update handlers |
| [`run_all.py`](case_studies/ghent/scripts/run_all.py) | Service launcher | Add health checks |
| [`simulation.py`](case_studies/ghent/src/ghent_water/orchestrator/routers/simulation.py) | Simulation endpoints | Auto-register models |
| [`llm_sparql.py`](case_studies/ghent/src/ghent_water/orchestrator/services/llm_sparql.py) | NL→SPARQL | Connect to real LLM |
| [`models/stubs/*.py`](case_studies/ghent/src/ghent_water/models/stubs/) | Stub implementations | Add realistic physics |

## Appendix B: Quick Start After Implementation

```bash
# Start everything
cd case_studies/ghent
python scripts/run_all.py

# Or step by step:
# Terminal 1: Start orchestrator
python scripts/run_orchestrator.py

# Terminal 2: Start models
python -m ghent_water.models.runners.model_runner --model dwp1 --port 8001 &
python -m ghent_water.models.runners.model_runner --model wwtp1 --port 8003 &
# ... etc

# Terminal 3: Start frontend
cd src/ghent_water/frontend
streamlit run app.py
```

Then open http://localhost:8501 and:
1. Click "Run Simulation" on WWTP-1
2. Watch status change to "Running" then "Completed"
3. Click example queries to populate the editor
4. Ask natural language questions
