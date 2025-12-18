# QUDT Competency Questions for waterFRAME

## Purpose
Test QUDT's ability to handle unit conversions, dimensional analysis, and mass/flow balance calculations across a water treatment network where data may be reported in different units.

---

## Flow and Mass Balance Questions

### CQ-QUDT-1: Sum flows in different volumetric units
**Question:** Can I calculate total influent flow to a junction when upstream sources report in different units?

**Scenario:**
- Source A reports: 10,000 m³/day
- Source B reports: 100 L/s
- Source C reports: 1.5 MGD (million gallons per day)

**Expected:** System should sum to a single unit (e.g., m³/day) with automatic conversion

**SPARQL Type:** Query with BIND for unit conversion or reasoning with conversion factors

---

### CQ-QUDT-2: Calculate mass loading from flow and concentration
**Question:** Given flow rate and pollutant concentration, can I calculate mass loading (mass/time)?

**Scenario:**
- Flow: 15,000 m³/day
- BOD concentration: 250 mg/L
- Expected mass loading: ? kg/day

**Calculation:**
```
15,000 m³/day × 250 mg/L = 15,000,000 L/day × 250 mg/L
                          = 3,750,000,000 mg/day
                          = 3,750 kg/day
```

**Expected:** System should handle dimensional analysis (volume/time × mass/volume = mass/time)

---

### CQ-QUDT-3: Sum mass loadings with different concentration units
**Question:** Can I sum pollutant loads when concentrations are in different units?

**Scenario:** Three streams entering a treatment plant:
- Stream A: 5,000 m³/day @ 200 mg/L BOD
- Stream B: 50 L/s @ 0.15 g/L BOD
- Stream C: 0.5 MGD @ 180 ppm BOD

**Expected:** Total BOD loading in kg/day after unit conversions

---

### CQ-QUDT-4: Check dimensional compatibility
**Question:** Can the system prevent nonsensical operations (e.g., adding temperature to flow rate)?

**Test:**
- Valid: 10 m³/day + 100 L/s (both volumetric flow rates)
- Invalid: 20°C + 50 m³/day (temperature + flow rate)

**Expected:** Validation based on `qudt:quantityKind`

---

### CQ-QUDT-5: Balance check across a node
**Question:** Does mass in = mass out at a junction (accounting for unit differences)?

**Scenario:** Junction with:
**Inputs:**
- Pipe 1: 8,000 m³/day @ 150 mg/L TN
- Pipe 2: 75 L/s @ 0.12 g/L TN

**Output:**
- Pipe 3: Should carry combined flow with averaged concentration

**Expected:**
- Flow out = flow in (after unit conversion)
- Mass out = mass in (TN loading)

---

## Sensor/Observation Questions

### CQ-QUDT-6: Compare observations in different units
**Question:** Can I identify which observations exceed a threshold when they're reported in different units?

**Scenario:** Regulatory limit for ammonia: 5 mg/L

**Observations:**
- Sensor A reports: 4.8 mg/L (PASS)
- Sensor B reports: 6,000 µg/L (FAIL - converts to 6 mg/L)
- Sensor C reports: 0.005 g/L (PASS - converts to 5 mg/L)

**Expected:** Query should handle conversions and identify exceedances

---

### CQ-QUDT-7: Aggregate time-series data with unit changes
**Question:** Can I calculate daily average when sensor switches units mid-day?

**Scenario:**
- 00:00-12:00: Readings in mg/L
- 12:00-24:00: Readings in µg/L (sensor recalibration)

**Expected:** Unified daily average after conversion

---

## Model Parameter Questions

### CQ-QUDT-8: Validate model input parameter units
**Question:** Can the system check if a parameter value has compatible units for a model input?

**Scenario:** ASM1 model expects:
- `Influent_Flow`: volumetric flow rate [L³/T]
- `Influent_COD`: mass concentration [M/L³]

**Test:**
- Valid: 10,000 m³/day (correct dimension)
- Invalid: 250 mg/L for flow (wrong dimension)

**Expected:** Validation via `qudt:quantityKind`

---

### CQ-QUDT-9: Convert model output to desired reporting units
**Question:** Can model outputs be automatically converted to user-preferred units?

**Scenario:**
- Model outputs effluent TN: 12.5 mg/L
- User wants report in: kg/day (given flow of 15,000 m³/day)

**Expected:** Automatic conversion: 12.5 mg/L × 15,000 m³/day = 187.5 kg/day

---

## Process Design Questions

### CQ-QUDT-10: Calculate hydraulic retention time (HRT)
**Question:** Given tank volume and flow rate in different units, calculate HRT?

**Scenario:**
- Tank volume: 5,000 m³
- Influent flow: 150 L/s

**Calculation:**
```
HRT = Volume / Flow
    = 5,000 m³ / (150 L/s × 86,400 s/day × 0.001 m³/L)
    = 5,000 m³ / 12,960 m³/day
    = 0.386 days
    = 9.26 hours
```

**Expected:** System handles volume/flow → time conversion

---

### CQ-QUDT-11: Organic loading rate (OLR)
**Question:** Calculate OLR in different unit systems?

**Scenario:**
- BOD loading: 3,750 kg/day
- Reactor volume: 5,000 m³

**Expected OLR:**
- 0.75 kg BOD/(m³·day)
- Also expressible as: 46.8 lb BOD/(1000 ft³·day) for US units

**Expected:** Support for both SI and US customary units

---

## Energy and Cost Questions

### CQ-QUDT-12: Energy consumption per volume treated
**Question:** Calculate specific energy consumption in different units?

**Scenario:**
- Power consumption: 150 kW
- Flow treated: 10,000 m³/day

**Expected:**
- 0.36 kWh/m³
- Also: 1.36 kWh/1000 gal

---

## Implementation Categories

### [O] - Ontology/SPARQL only
Pure queries using QUDT unit definitions and conversions

### [C] - Computational
Requires external calculation (Python, etc.) but uses QUDT for unit validation

### [R] - Reasoning
Requires OWL reasoning with QUDT axioms

---

## Test Data Requirements

For each CQ, we need:
1. **Observations** with different units for same quantity kind
2. **Conversion factors** (QUDT provides these)
3. **Expected results** for validation
4. **SPARQL queries** demonstrating the solution approach
5. **Python scripts** showing computational approach with unit validation

---

## Success Criteria

✓ Unit conversions work correctly (no manual conversion needed)
✓ Dimensional analysis prevents invalid operations
✓ Mass/flow balances close to within numerical precision
✓ Same results whether using SI or US customary units
✓ Model parameters validated against expected dimensions
✓ Clear error messages for unit mismatches
