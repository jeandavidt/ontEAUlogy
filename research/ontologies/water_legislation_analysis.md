# Water Legislation Ontology Research Report

**Analysis Date**: 2025-01-15
**Project**: ontEAUlogy - Water Quality and Quantity Legislation Representation
**Focus**: EU Water Framework Directive, Quebec Q-2 r.22, Quebec Q-2 r.40

---

## Executive Summary

This report analyzes the current state of the waterFRAME ontology regarding representation of water quality and quantity legislation, specifically:

1. **EU Water Framework Directive (WFD)** - 2000/60/EC
2. **Quebec Regulation Q-2 r.22** - Water withdrawals
3. **Quebec Regulation Q-2 r.40** - Waterworks and sewage systems

### Key Findings

| Aspect | Current Coverage | Gap Severity |
|--------|------------------|--------------|
| Water quality parameters | ✓ Good (BOD, COD, TSS, pH, etc.) | Low |
| Regulatory standards placeholder | ✓ Basic (EU WFD, EPA, WHO) | Medium |
| Water quantity concepts | ✗ None | **CRITICAL** |
| WFD water body classifications | ✗ None | **HIGH** |
| Quebec-specific regulations | ✗ None | **HIGH** |
| Discharge permits/emission limits | ✗ None | **HIGH** |
| Ecological status/classification | ✗ None | **HIGH** |
| Water allocation/rights | ✗ None | **CRITICAL** |
| Monitoring requirements | ✗ None | **MEDIUM** |

### Recommendation

**HIGH PRIORITY**: Develop a new `regulations.ttl` module to represent water legislation concepts. No existing ontologies were found that adequately cover EU WFD or Quebec regulations. Custom development is required.

---

## 1. Current Ontology State Analysis

### 1.1 Existing Regulatory Concepts (qualities.ttl)

```turtle
# Current classes for regulatory concepts
wf:RegulatoryStandard a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000027 ;  # Rule
    rdfs:label "Regulatory standard" ;
    rdfs:comment "A regulatory standard for water quality." .

wf:EUWaterFrameworkDirective a owl:Class ;
    rdfs:subClassOf wf:RegulatoryStandard ;
    rdfs:label "EU Water Framework Directive" ;
    rdfs:comment "European Union Water Framework Directive standards." .

wf:USEPAStandard a owl:Class ;
    rdfs:subClassOf wf:RegulatoryStandard ;
    rdfs:label "US EPA Standard" ;
    rdfs:comment "United States Environmental Protection Agency standards." .

wf:WHOGuideline a owl:Class ;
    rdfs:subClassOf wf:RegulatoryStandard ;
    rdfs:label "WHO Guideline" ;
    rdfs:comment "World Health Organization drinking water guidelines." .
```

**Assessment**: These are placeholder classes with no specific axioms, quality elements, or limit definitions. They provide a foundation but lack detail.

### 1.2 Water Quality Requirements (qualities.ttl)

```turtle
wf:WaterQualityRequirement a owl:Class ;
    rdfs:subClassOf bfo:BFO_0000023 ;  # Specifically dependent continuant
    rdfs:label "Water quality requirement" ;
    rdfs:comment "A requirement or limit for a water quality parameter." .

wf:hasWaterQualityParameter a owl:ObjectProperty ;
    rdfs:label "has water quality parameter" ;
    rdfs:domain wf:WaterQualityRequirement ;
    rdfs:range wf:WaterQualityParameter .

wf:hasLimitValue a owl:DatatypeProperty ;
    rdfs:label "has limit value" ;
    rdfs:domain wf:WaterQualityRequirement ;
    rdfs:range xsd:double .

wf:hasLimitType a owl:ObjectProperty ;
    rdfs:label "has limit type" ;
    rdfs:domain wf:WaterQualityRequirement ;
    rdfs:range wf:LimitType .

wf:LimitType a owl:Class ;
    rdfs:subClasses wf:MaximumLimit, wf:MinimumLimit, wf:RangeLimit, wf:AverageLimit .
```

**Assessment**: Good foundational pattern for requirements. Can be extended with regulatory context.

---

## 2. EU Water Framework Directive Analysis

### 2.1 WFD Key Concepts to Represent

The EU Water Framework Directive (2000/60/EC) establishes:

#### Water Body Classifications
- **Surface water bodies**:
  - Rivers
  - Lakes
  - Transitional waters (estuaries)
  - Coastal waters
- **Groundwater bodies**
- **Artificial water bodies**
- **Heavily modified water bodies**

#### Quality Elements (for status assessment)
- **Biological elements**: Phytoplankton, macroalgae, angiosperms, macroinvertebrates, fish
- **Hydromorphological elements**: Morphology, hydrological regime
- **Physico-chemical elements**: General conditions, specific pollutants
- **Chemical elements**: Priority substances, priority hazardous substances

#### Status Classifications
- **Ecological status**: High, Good, Moderate, Poor, Bad
- **Chemical status**: Good, Failing to achieve good

#### Monitoring Requirements
- Surveillance monitoring
- Operational monitoring
- Investigative monitoring

### 2.2 Gap Analysis for WFD

| WFD Concept | In Ontology? | Required Addition |
|-------------|--------------|-------------------|
| Water body types (river, lake, etc.) | Partial (River, Lake, Groundwater in material_entities) | Need transitional, coastal, artificial, heavily modified |
| Quality elements | No | New classes for biological, hydromorphological, physico-chemical, chemical |
| Ecological status | No | New value partition (High/Good/Moderate/Poor/Bad) |
| Chemical status | No | New value partition (Good/Failing) |
| Monitoring types | No | New classes for surveillance/operational/investigative |
| River basin districts | No | New class |
| Protected zones | No | New class |

### 2.3 Recommended WFD Module Structure

```turtle
# ========== WFD WATER BODY CLASSIFICATIONS ==========

wf:WFDWaterBody rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "WFD water body" ;
    rdfs:comment "A water body as defined by the EU Water Framework Directive." .

wf:SurfaceWaterBody rdfs:subClassOf wf:WFDWaterBody ;
    rdfs:label "Surface water body" ;
    rdfs:comment "Surface water including rivers, lakes, transitional and coastal waters." .

wf:RiverWaterBody rdfs:subClassOf wf:SurfaceWaterBody ;
    rdfs:label "River water body" ;
    rdfs:comment "A river water body as defined by WFD." .

wf:LakeWaterBody rdfs:subClassOf wf:SurfaceWaterBody ;
    rdfs:label "Lake water body" ;
    rdfs:comment "A lake water body as defined by WFD." .

wf:TransitionalWaterBody rdfs:subClassOf wf:SurfaceWaterBody ;
    rdfs:label "Transitional water body" ;
    rdfs:comment "Estuaries and other transitional waters." .

wf:CoastalWaterBody rdfs:subClassOf wf:SurfaceWaterBody ;
    rdfs:label "Coastal water body" ;
    rdfs:comment "Coastal waters as defined by WFD." .

wf:GroundwaterBody rdfs:subClassOf wf:WFDWaterBody ;
    rdfs:label "Groundwater body" ;
    rdfs:comment "A groundwater body as defined by WFD." .

wf:ArtificialWaterBody rdfs:subClassOf wf:SurfaceWaterBody ;
    rdfs:label "Artificial water body" ;
    rdfs:comment "Water bodies designated as artificial." .

wf:HeavilyModifiedWaterBody rdfs:subClassOf wf:SurfaceWaterBody ;
    rdfs:label "Heavily modified water body" ;
    rdfs:comment "Water bodies designated as heavily modified." .

# ========== WFD QUALITY ELEMENTS ==========

wf:WFDQualityElement rdfs:subClassOf bfo:BFO_0000019 ;
    rdfs:label "WFD quality element" ;
    rdfs:comment "A quality element for WFD status assessment." .

wf:BiologicalQualityElement rdfs:subClassOf wf:WFDQualityElement ;
    rdfs:label "Biological quality element" ;
    rdfs:comment "Biological quality elements for ecological status." .

wf:HydromorphologicalQualityElement rdfs:subClassOf wf:WFDQualityElement ;
    rdfs:label "Hydromorphological quality element" ;
    rdfs:comment "Hydromorphological quality elements." .

wf:PhysicoChemicalQualityElement rdfs:subClassOf wf:WFDQualityElement ;
    rdfs:subClassOf wf:WFDQualityElement ;
    rdfs:comment "Physico-chemical quality elements." .

wf:ChemicalQualityElement rdfs:subClassOf wf:WFDQualityElement ;
    rdfs:label "Chemical quality element" ;
    rdfs:comment "Chemical quality elements (priority substances)." .

# ========== WFD STATUS CLASSIFICATIONS ==========

wf:EcologicalStatus rdfs:subClassOf bfo:BFO_0000026 ;
    rdfs:label "Ecological status" ;
    rdfs:comment "Ecological status classification under WFD." .

wf:EcologicalStatusHigh rdfs:subClassOf wf:EcologicalStatus ;
    rdfs:label "High ecological status" ;
    rdfs:comment "No or very minor deviation from undisturbed conditions." .

wf:EcologicalStatusGood rdfs:subClassOf wf:EcologicalStatus ;
    rdfs:label "Good ecological status" ;
    rdfs:comment "Slight deviation from undisturbed conditions." .

wf:EcologicalStatusModerate rdfs:subClassOf wf:EcologicalStatus ;
    rdfs:label "Moderate ecological status" ;
    rdfs:comment "Moderate deviation from undisturbed conditions." .

wf:EcologicalStatusPoor rdfs:subClassOf wf:EcologicalStatus ;
    rdfs:subClassOf wf:EcologicalStatus ;
    rdfs:comment "Poor ecological status." .

wf:EcologicalStatusBad rdfs:subClassOf wf:EcologicalStatus ;
    rdfs:label "Bad ecological status" ;
    rdfs:comment "Severe deviation from undisturbed conditions." .

wf:ChemicalStatus rdfs:subClassOf bfo:BFO_0000026 ;
    rdfs:label "Chemical status" ;
    rdfs:comment "Chemical status classification under WFD." .

wf:ChemicalStatusGood rdfs:subClassOf wf:ChemicalStatus ;
    rdfs:label "Good chemical status" ;
    rdfs:comment "Concentrations below environmental quality standards." .

wf:ChemicalStatusFailing rdfs:subClassOf wf:ChemicalStatus ;
    rdfs:label "Failing to achieve good chemical status" ;
    rdfs:comment "Concentrations exceed environmental quality standards." .

# ========== WFD MONITORING ==========

wf:WFDMonitoring rdfs:subClassOf bfo:BFO_0000015 ;
    rdfs:label "WFD monitoring" ;
    rdfs:comment "Monitoring activities under WFD." .

wf:SurveillanceMonitoring rdfs:subClassOf wf:WFDMonitoring ;
    rdfs:label "Surveillance monitoring" ;
    rdfs:comment "General overview of water body status." .

wf:OperationalMonitoring rdfs:subClassOf wf:WFDMonitoring ;
    rdfs:label "Operational monitoring" ;
    rdfs:comment "Monitoring to establish status of water bodies at risk." .

wf:InvestigativeMonitoring rdfs:subClassOf wf:WFDMonitoring ;
    rdfs:label "Investigative monitoring" ;
    rdfs:comment "Investigation of causes of unknown pollution." .
```

---

## 3. Quebec Regulation Q-2 r.22 Analysis

### 3.1 Q-2 r.22 Overview

**Regulation respecting the water withdrawal and consumption regime** (Loi sur la qualité de l'environnement)

**Key Concepts**:
- Water withdrawal permits
- Groundwater and surface water withdrawals
- Water allocation limits
- Reporting requirements
- Metering and measurement requirements
- Protected zones (headwaters, wetlands)

### 3.2 Key Requirements to Represent

| Aspect | Description |
|--------|-------------|
| Withdrawal permit | Authorization to withdraw water |
| Maximum daily withdrawal | Limit on volume per day |
| Maximum annual withdrawal | Limit on volume per year |
| Protected zones | Areas with special protection |
| Wetland protection | Specific protection for wetlands |
| Reporting frequency | How often withdrawals must be reported |
| Metering requirements | Measurement device specifications |

### 3.3 Gap Analysis for Q-2 r.22

| Q-2 r.22 Concept | In Ontology? | Required Addition |
|------------------|--------------|-------------------|
| Water withdrawal permit | No | New class |
| Withdrawal point | No | New class |
| Maximum daily withdrawal volume | No | New data property |
| Maximum annual withdrawal volume | No | New data property |
| Protected zone | No | New class |
| Wetland | No (partial in Catchment) | New class |
| Reporting requirement | No | New class |
| Metering requirement | No | New class |

### 3.4 Recommended Q-2 r.22 Module Structure

```turtle
# ========== WATER WITHDRAWAL CONCEPTS ==========

wf:WaterWithdrawal rdfs:subClassOf bfo:BFO_0000015 ;
    rdfs:label "Water withdrawal" ;
    rdfs:comment "The act of taking water from a water body." .

wf:WithdrawalPermit rdfs:subClassOf bfo:BFO_0000027 ;
    rdfs:label "Water withdrawal permit" ;
    rdfs:comment "Authorization to withdraw water under Q-2 r.22." .

wf:withdrawalPermitNumber a owl:DatatypeProperty ;
    rdfs:label "withdrawal permit number" ;
    rdfs:domain wf:WithdrawalPermit ;
    rdfs:range xsd:string .

wf:hasWithdrawalPermit a owl:ObjectProperty ;
    rdfs:label "has withdrawal permit" ;
    rdfs:domain wf:WaterSource ;
    rdfs:range wf:WithdrawalPermit .

wf:maximumDailyWithdrawal a owl:DatatypeProperty ;
    rdfs:label "maximum daily withdrawal" ;
    rdfs:domain [ owl:unionOf (wf:WaterSource wf:WithdrawalPermit) ] ;
    rdfs:range xsd:double ;
    wf:hasUnit <http://qudt.org/vocab/unit/CubicMeterPerDay> .

wf:maximumAnnualWithdrawal a owl:DatatypeProperty ;
    rdfs:label "maximum annual withdrawal" ;
    rdfs:domain [ owl:unionOf (wf:WaterSource wf:WithdrawalPermit) ] ;
    rdfs:range xsd:double ;
    wf:hasUnit <http://qudt.org/vocab/unit/CubicMeterPerYear> .

wf:actualWithdrawal a owl:DatatypeProperty ;
    rdfs:label "actual withdrawal" ;
    rdfs:domain wf:WaterWithdrawal ;
    rdfs:range xsd:double ;
    wf:hasUnit <http://qudt.org/vocab/unit/CubicMeter> .

wf:withdrawalReportedOn a owl:DatatypeProperty ;
    rdfs:label "withdrawal reported on" ;
    rdfs:domain wf:WaterWithdrawal ;
    rdfs:range xsd:dateTime .

# ========== PROTECTED ZONES ==========

wf:ProtectedZone rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Protected zone" ;
    rdfs:comment "Zone with special protection under environmental regulations." .

wf:Wetland rdfs:subClassOf wf:ProtectedZone ;
    rdfs:label "Wetland" ;
    rdfs:comment "Land permanently or temporarily submerged." .

wf:HeadwaterZone rdfs:subClassOf wf:ProtectedZone ;
    rdfs:label "Headwater zone" ;
    rdfs:comment "Headwater area with special protection." .

wf:isInProtectedZone a owl:ObjectProperty ;
    rdfs:label "is in protected zone" ;
    rdfs:domain wf:WaterSource ;
    rdfs:range wf:ProtectedZone .

# ========== REPORTING AND METERING ==========

wf:WithdrawalReport rdfs:subClassOf bfo:BFO_0000031 ;
    rdfs:label "Withdrawal report" ;
    rdfs:comment "Report of water withdrawal quantities." .

wf:hasReport a owl:ObjectProperty ;
    rdfs:label "has report" ;
    rdfs:domain wf:WaterSource ;
    rdfs:range wf:WithdrawalReport .

wf:reportFrequency a owl:DatatypeProperty ;
    rdfs:label "report frequency" ;
    rdfs:domain wf:WithdrawalPermit ;
    rdfs:range xsd:string .  # e.g., "monthly", "annually"

wf:MeteringRequirement rdfs:subClassOf bfo:BFO_0000027 ;
    rdfs:label "Metering requirement" ;
    rdfs:comment "Requirement for measuring water withdrawals." .

wf:hasMeteringRequirement a owl:ObjectProperty ;
    rdfs:label "has metering requirement" ;
    rdfs:domain wf:WithdrawalPermit ;
    rdfs:range wf:MeteringRequirement .
```

---

## 4. Quebec Regulation Q-2 r.40 Analysis

### 4.1 Q-2 r.40 Overview

**Regulation respecting waterworks and sewer systems** (Loi sur la qualité de l'environnement)

**Key Concepts**:
- Drinking water systems
- Sewage collection and treatment systems
- Discharge permits (authorizations)
- Effluent quality standards
- Monitoring and reporting
- System certification and operation

### 4.2 Key Requirements to Represent

| Aspect | Description |
|--------|-------------|
| Waterworks permit | Authorization to operate drinking water system |
| Sewer system permit | Authorization to operate sewer system |
| Discharge authorization | Authorization to discharge effluent |
| Effluent quality standards | Quality limits for discharges |
| Monitoring program | Required monitoring activities |
| Sampling point | Location of effluent sampling |
| Reporting frequency | How often reports must be submitted |
| System certification | Operator certification requirements |

### 4.3 Gap Analysis for Q-2 r.40

| Q-2 r.40 Concept | In Ontology? | Required Addition |
|------------------|--------------|-------------------|
| Waterworks permit | No | New class |
| Sewer system permit | No | New class |
| Discharge authorization | No | New class |
| Effluent quality standard | Partial (WaterQualityRequirement) | Extend with Q-2 r.40 specifics |
| Monitoring program | No | New class |
| Sampling point | No | New class |
| Reporting frequency | No | New data property |
| Operator certification | No | New class |

### 4.4 Recommended Q-2 r.40 Module Structure

```turtle
# ========== WATERWORKS CONCEPTS ==========

wf:Waterworks rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Waterworks" ;
    rdfs:comment "Drinking water treatment and distribution system." .

wf:WaterworksPermit rdfs:subClassOf bfo:BFO_0000027 ;
    rdfs:label "Waterworks permit" ;
    rdfs:comment "Authorization to operate waterworks under Q-2 r.40." .

wf:hasWaterworksPermit a owl:ObjectProperty ;
    rdfs:label "has waterworks permit" ;
    rdfs:domain wf:DrinkingWaterPlant ;
    rdfs:range wf:WaterworksPermit .

wf:waterworksPermitNumber a owl:DatatypeProperty ;
    rdfs:label "waterworks permit number" ;
    rdfs:domain wf:WaterworksPermit ;
    rdfs:range xsd:string .

# ========== SEWER SYSTEM CONCEPTS ==========

wf:SewerSystem rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Sewer system" ;
    rdfs:comment "Sewage collection and conveyance system." .

wf:SewerSystemPermit rdfs:subClassOf bfo:BFO_0000027 ;
    rdfs:label "Sewer system permit" ;
    rdfs:comment "Authorization to operate sewer system under Q-2 r.40." .

wf:hasSewerSystemPermit a owl:ObjectProperty ;
    rdfs:label "has sewer system permit" ;
    rdfs:domain wf:SewerSystem ;
    rdfs:range wf:SewerSystemPermit .

# ========== DISCHARGE AUTHORIZATION ==========

wf:DischargeAuthorization rdfs:subClassOf bfo:BFO_0000027 ;
    rdfs:label "Discharge authorization" ;
    rdfs:comment "Authorization to discharge effluent under Q-2 r.40." .

wf:hasDischargeAuthorization a owl:ObjectProperty ;
    rdfs:label "has discharge authorization" ;
    rdfs:domain wf:WastewaterTreatmentPlant ;
    rdfs:range wf:DischargeAuthorization .

wf:dischargeAuthorizationNumber a owl:DatatypeProperty ;
    rdfs:label "discharge authorization number" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range xsd:string .

wf:effectiveDate a owl:DatatypeProperty ;
    rdfs:label "effective date" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range xsd:date .

wf:expirationDate a owl:DatatypeProperty ;
    rdfs:label "expiration date" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range xsd:date .

# ========== EFFLUENT QUALITY STANDARDS ==========

wf:EffluentQualityStandard rdfs:subClassOf wf:WaterQualityRequirement ;
    rdfs:label "Effluent quality standard" ;
    rdfs:comment "Quality standard for effluent discharge." .

wf:appliesToDischarge a owl:ObjectProperty ;
    rdfs:label "applies to discharge" ;
    rdfs:domain wf:EffluentQualityStandard ;
    rdfs:range wf:DischargeAuthorization .

wf:compliancePoint rdfs:subClassOf bfo:BFO_0000040 ;
    rdfs:label "Compliance point" ;
    rdfs:comment "Location where effluent quality is measured for compliance." .

wf:hasCompliancePoint a owl:ObjectProperty ;
    rdfs:label "has compliance point" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range wf:CompliancePoint .

wf:samplingFrequency a owl:DatatypeProperty ;
    rdfs:label "sampling frequency" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range xsd:string .  # e.g., "weekly", "monthly"

# ========== MONITORING AND REPORTING ==========

wf:DischargeMonitoringProgram rdfs:subClassOf bfo:BFO_0000031 ;
    rdfs:label "Discharge monitoring program" ;
    rdfs:comment "Program for monitoring effluent discharge." .

wf:hasMonitoringProgram a owl:ObjectProperty ;
    rdfs:label "has monitoring program" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range wf:DischargeMonitoringProgram .

wf:DischargeReport rdfs:subClassOf bfo:BFO_0000031 ;
    rdfs:label "Discharge report" ;
    rdfs:comment "Report of discharge monitoring results." .

wf:hasDischargeReport a owl:ObjectProperty ;
    rdfs:label "has discharge report" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range wf:DischargeReport .

wf:reportDueDate a owl:DatatypeProperty ;
    rdfs:label "report due date" ;
    rdfs:domain wf:DischargeAuthorization ;
    rdfs:range xsd:string .  # e.g., "March 31", "end of February"

# ========== OPERATOR CERTIFICATION ==========

wf:OperatorCertification rdfs:subClassOf bfo:BFO_0000027 ;
    rdfs:label "Operator certification" ;
    rdfs:comment "Certification requirements for system operators." .

wf:hasOperatorCertification a owl:ObjectProperty ;
    rdfs:label "has operator certification" ;
    rdfs:domain [ owl:unionOf (wf:Waterworks wf:SewerSystem) ] ;
    rdfs:range wf:OperatorCertification .

wf:certificationClass a owl:DatatypeProperty ;
    rdfs:label "certification class" ;
    rdfs:domain wf:OperatorCertification ;
    rdfs:range xsd:string .  # e.g., "1", "2", "3", "4"
```

---

## 5. Water Quantity Concepts (Cross-Cutting)

### 5.1 Missing Water Quantity Concepts

The ontology currently has no representation of water quantity concepts, which are critical for:
- Water allocation optimization
- Withdrawal management
- Flow requirements for ecosystems
- Drought management

### 5.2 Recommended Water Quantity Module

```turtle
# ========== WATER QUANTITY BASE CLASSES ==========

wf:WaterQuantity rdfs:subClassOf bfo:BFO_0000019 ;
    rdfs:label "Water quantity" ;
    rdfs:comment "A measurable quantity of water." .

wf:FlowRate rdfs:subClassOf wf:WaterQuantity ;
    rdfs:label "Flow rate" ;
    rdfs:comment "Volume of water flowing per unit time." .

wf:Volume rdfs:subClassOf wf:WaterQuantity ;
    rdfs:label "Volume" ;
    rdfs:comment "Total amount of water." .

wf:Level rdfs:subClassOf wf:WaterQuantity ;
    rdfs:label "Water level" ;
    rdfs:comment "Height of water surface." .

# ========== FLOW RATE PROPERTIES ==========

wf:hasFlowRate a owl:ObjectProperty ;
    rdfs:label "has flow rate" ;
    rdfs:domain [ owl:unionOf (wf:WaterSource wf:WaterFlow wf:Port) ] ;
    rdfs:range wf:FlowRate .

wf:flowRateValue a owl:DatatypeProperty ;
    rdfs:label "flow rate value" ;
    rdfs:domain wf:FlowRate ;
    rdfs:range xsd:double ;
    wf:hasUnit <http://qudt.org/vocab/unit/CubicMeterPerSecond> .

wf:inletFlowRate a owl:ObjectProperty ;
    rdfs:label "inlet flow rate" ;
    rdfs:domain wf:WaterSystemComponent ;
    rdfs:range wf:FlowRate .

wf:outletFlowRate a owl:ObjectProperty ;
    rdfs:label "outlet flow rate" ;
    rdfs:domain wf:WaterSystemComponent ;
    rdfs:range wf:FlowRate .

# ========== ALLOCATION CONCEPTS ==========

wf:WaterAllocation rdfs:subClassOf bfo:BFO_0000023 ;
    rdfs:label "Water allocation" ;
    rdfs:comment "Allocated water quantity for a specific use." .

wf:allocatedVolume a owl:DatatypeProperty ;
    rdfs:label "allocated volume" ;
    rdfs:domain wf:WaterAllocation ;
    rdfs:range xsd:double ;
    wf:hasUnit <http://qudt.org/vocab/unit/CubicMeter> .

wf:allocatesTo a owl:ObjectProperty ;
    rdfs:label "allocates to" ;
    rdfs:domain wf:WaterAllocation ;
    rdfs:range wf:WaterSource .

# ========== MINIMUM FLOW REQUIREMENTS ==========

wf:EnvironmentalFlowRequirement rdfs:subClassOf bfo:BFO_0000023 ;
    rdfs:label "Environmental flow requirement" ;
    rdfs:comment "Minimum flow required for ecosystem health." .

wf:minimumFlowRate a owl:ObjectProperty ;
    rdfs:label "minimum flow rate" ;
    rdfs:domain [ owl:unionOf (wf:River wf:RiverSegment) ] ;
    rdfs:range wf:FlowRate .
```

---

## 6. Comparison of Researched Ontologies

### 6.1 Existing Research Summary

| Ontology | Focus | Regulatory Coverage | Recommendation |
|----------|-------|---------------------|----------------|
| **SAREF4WATER** | IoT/smart water | Low (devices only) | Use for sensor concepts only |
| **OntoCAPE** | Process engineering | None | Use for process modeling |
| **SOSA/SSN** | Observations | None | Use for monitoring data |
| **QUDT** | Units | None | Use for unit definitions |
| **WaWO** | Wastewater | Unavailable | Cannot use |
| **HyFO** | Hydrological features | Partial (water bodies) | Evaluate for WFD concepts |

### 6.2 HyFO (Hydrological Features Ontology) Evaluation

HyFO from OGC/ISO could provide some WFD water body concepts. Key classes:
- `hyf:River`, `hyf:Lake`, `hyf:GroundWaterBody`
- `hyf:WaterBody`, `hyf:Catchment`

**Recommendation**: Consider importing HyFO or HY_Features for water body classifications, but custom extension will still be needed for WFD-specific quality elements and status classifications.

### 6.3 INSPIRE Hydrography

INSPIRE data specification for hydrography includes:
- Water bodies, networks, physical plans
- Geographic representation

**Recommendation**: Align with INSPIRE for spatial aspects if EU context is primary.

---

## 7. Recommendations

### 7.1 Priority 1: Critical Gaps (Immediate Action)

**Water Quantity Module** (`quantity.ttl`)
- Flow rates, volumes, levels
- Water allocation concepts
- Environmental flow requirements
- Withdrawal tracking

### 7.2 Priority 2: High Priority (Short-term)

**EU WFD Module** (`wfd.ttl`)
- Water body classifications (surface, groundwater, transitional, coastal)
- Quality elements (biological, hydromorphological, physico-chemical, chemical)
- Status classifications (ecological, chemical)
- Monitoring types

### 7.3 Priority 3: Medium Priority (Medium-term)

**Quebec Regulations Module** (`quebec_regulations.ttl`)
- Q-2 r.22 water withdrawal concepts
- Q-2 r.40 waterworks and sewer system concepts
- Permits, authorizations
- Compliance monitoring

### 7.4 Implementation Strategy

```
Phase 1 (Immediate):
├── Create quantity.ttl module
│   └── Flow rates, allocations, environmental requirements
└── Extend qualities.ttl
    └── WFD-specific quality elements

Phase 2 (Short-term):
├── Create wfd.ttl module
│   └── Water body classifications, status, monitoring
└── Extend properties.ttl
    └── Water body relationships

Phase 3 (Medium-term):
├── Create quebec_regulations.ttl
│   └── Q-2 r.22 and Q-2 r.40 concepts
└── Create compliance module
    └── Compliance assessment, violation tracking
```

### 7.5 Competency Questions Affected

| CQ | Description | Module Needed |
|----|-------------|---------------|
| CQ11 | Regulatory limits for parameters | qualities.ttl extension |
| CQ12 | Effluent meets reuse requirements | compliance module |
| CQ35 | Source of regulatory limits | regulations.ttl |

---

## 8. Conclusion

The current waterFRAME ontology provides a solid foundation for water reuse systems but lacks comprehensive coverage of water quality and quantity legislation. Specifically:

1. **No water quantity concepts**: Critical for water allocation and withdrawal management
2. **No WFD-specific concepts**: EU Water Framework Directive requires dedicated module
3. **No Quebec regulatory concepts**: Q-2 r.22 and Q-2 r.40 need custom development
4. **No compliance assessment**: Cannot determine if systems meet regulatory requirements

**No existing ontologies** adequately cover EU WFD or Quebec regulations. Custom development following the patterns in this report is required.

**Next Steps**:
1. Prioritize water quantity module development
2. Design WFD module for EU contexts
3. Develop Quebec regulations module for regional compliance
4. Create compliance assessment patterns

---

## References

1. EU Water Framework Directive (2000/60/EC): https://environment.ec.europa.eu/topics/water/water-framework-directive_en
2. Quebec Regulation Q-2 r.22: https://www.legisquebec.gouv.qc.ca/en/document rc/Q-2,%20r.%2022/
3. Quebec Regulation Q-2 r.40: https://www.legisquebec.gouv.qc.ca/en/document rc/Q-2,%20r.%2040/
4. OGC HY_Features: https://www.ogc.org/standard/hy-features/
5. INSPIRE Hydrography: https://inspire.ec.europa.eu/Themes/93/5892
