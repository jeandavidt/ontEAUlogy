# WaWO+ Ontology Competency Questions

This document defines competency questions to test the reasoning capabilities of the WaWO+ ontology.

## 1. Water Quality Classification

### CQ1.1: Can the system classify water as drinking water quality?
**Question**: Given a water mass with specific contaminant concentrations, can the reasoner infer that it qualifies as drinking water composition?

**Test Data**:
- Water sample with BOD < 5.0, COD < 10.0, SS < 10.0, TN < 2.0, TP < 0.5 mg/L
- Expected: Should be classified as `DrinkingWaterComposition`

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?composition
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:hasWaterComposition ?composition .
  ?composition a wawo:DrinkingWaterComposition .
}
```

### CQ1.2: Can the system identify contaminated water?
**Question**: Given a water mass that exceeds drinking water standards, can the reasoner classify it as wastewater?

**Test Data**:
- Water sample with BOD = 150.0 mg/L (exceeds standard)
- Expected: Should NOT be classified as `DrinkingWaterComposition`

### CQ1.3: What are the concentration levels for a given water mass?
**Question**: Can we query all water quality indicators for a water mass?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?bod ?cod ?ss ?tn ?tp
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:biologicalOxygenDemandConcentration ?bod ;
             wawo:chemicalOxygenDemandConcentration ?cod ;
             wawo:suspendedSolidConcentration ?ss ;
             wawo:totalNitrogenConcentration ?tn ;
             wawo:totalPhosphorusConcentration ?tp .
}
```

## 2. Treatment Facility Compliance

### CQ2.1: Which WWTPs are treating water?
**Question**: Can we identify all wastewater treatment plants that are performing treatment processes?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?wwtp ?process
WHERE {
  ?wwtp a wawo:WWTP ;
        wawo:performs ?process .
  ?process a wawo:Process .
}
```

### CQ2.2: Which WWTPs should have secondary treatment?
**Question**: Given WWTPs with population equivalent >= 10,000, which ones should perform secondary treatment?

**Test Data**:
- WWTP with populationEquivalent = 15000
- Expected: Should be identified as requiring secondary treatment

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?wwtp ?popEq
WHERE {
  ?wwtp a wawo:WWTP ;
        wawo:populationEquivalent ?popEq .
  FILTER(?popEq >= 10000)
}
```

### CQ2.3: Which WWTPs are non-compliant?
**Question**: Which WWTPs have population equivalent >= 10,000 but do NOT perform secondary treatment?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?wwtp ?popEq
WHERE {
  ?wwtp a wawo:WWTP ;
        wawo:populationEquivalent ?popEq .
  FILTER(?popEq >= 10000)
  FILTER NOT EXISTS {
    ?wwtp wawo:performs ?treatment .
    ?treatment a wawo:SecondaryTreatment .
  }
}
```

### CQ2.4: What water is being discharged by WWTPs?
**Question**: Can we track the water masses discharged by treatment plants?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?wwtp ?discharged ?bod ?cod
WHERE {
  ?wwtp a wawo:WWTP ;
        wawo:discharged ?discharged .
  ?discharged wawo:biologicalOxygenDemandConcentration ?bod ;
              wawo:chemicalOxygenDemandConcentration ?cod .
}
```

## 3. Water Mass Flow Tracking

### CQ3.1: What water sources are producing water masses?
**Question**: Can we identify all water sources and the water masses they produce?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?source ?waterMass ?sourceType
WHERE {
  ?source a ?sourceType ;
          wawo:produces ?waterMass .
  ?sourceType rdfs:subClassOf* wawo:WaterSource .
}
```

### CQ3.2: Can we distinguish between flow and static water masses?
**Question**: Given water masses, can we separate those that are flowing vs. static?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?flow
WHERE {
  ?waterMass a wawo:Flow_water_mass ;
             wawo:flow ?flow .
}
```

### CQ3.3: What is the water composition in river sections?
**Question**: Can we query water quality in specific geographical locations?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?riverSection ?waterMass ?composition
WHERE {
  ?riverSection a wawo:RiverSection ;
                wawo:hasWaterMass ?waterMass .
  ?waterMass wawo:hasWaterComposition ?composition .
}
```

## 4. Heavy Metal and Contaminant Tracking

### CQ4.1: Which water masses contain heavy metals?
**Question**: Can we identify water masses with heavy metal contamination?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?concentration
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:heavyMetalConcentration ?concentration .
  FILTER(?concentration > 0.0)
}
```

### CQ4.2: Are there mercury levels exceeding limits?
**Question**: Can we detect mercury concentrations above regulatory limits (0.005 mg/L)?

**Test Data**:
- Water sample with mercury concentration = 0.006 mg/L
- Expected: Should be flagged as exceeding limit

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?mercury
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:heavyMetalConcentration ?mercury .
  FILTER(?mercury >= 0.005)
}
```

### CQ4.3: Which water masses contain emerging contaminants?
**Question**: Can we track emerging pharmaceutical contaminants?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?waterMass ?concentration
WHERE {
  ?waterMass a wawo:WaterMass ;
             wawo:emergingPollutantConcentration ?concentration .
}
```

## 5. Meteorological Events

### CQ5.1: Can we identify heavy rain events?
**Question**: Given precipitation data, can we identify events qualifying as heavy rain?

**Test Data**:
- Rainfall with amount >= 200 m³ and duration <= 3 hours
- Expected: Should be classified as `HeavyPrecipitation`

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?event ?amount ?duration
WHERE {
  ?event a wawo:Rainfall ;
         wawo:precipitationAmount ?amount ;
         wawo:duration ?duration .
  FILTER(?amount >= 200 && ?duration <= "PT3H"^^xsd:duration)
}
```

### CQ5.2: What situations are classified as abnormal?
**Question**: Can we query all abnormal situations (droughts, heavy precipitation)?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?situation ?type
WHERE {
  ?situation a ?type .
  ?type rdfs:subClassOf* wawo:AbnormalSituation .
}
```

### CQ5.3: When did precipitation events occur?
**Question**: Can we query temporal information about precipitation events?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?event ?startTime ?endTime ?amount
WHERE {
  ?event a wawo:Precipitation ;
         wawo:hasTimestampStart ?startTime ;
         wawo:hasTimestampEnd ?endTime ;
         wawo:precipitationAmount ?amount .
}
```

## 6. Infrastructure and Networks

### CQ6.1: What conveyor units are connected?
**Question**: Can we trace connections between water infrastructure components?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?unit1 ?unit2
WHERE {
  ?unit1 a wawo:ConveyorUnit ;
         wawo:connectedTo ?unit2 .
}
```

### CQ6.2: What processes are performed at treatment facilities?
**Question**: Can we list all processes performed at each treatment facility?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?facility ?process ?processType
WHERE {
  ?facility a wawo:WaterTreatmentFacility ;
            wawo:performs ?process .
  ?process a ?processType .
}
```

### CQ6.3: Where are water sources located?
**Question**: Can we query geographical locations of water sources?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?source ?location
WHERE {
  ?source a wawo:WaterSource ;
          wawo:locatedIn ?location .
  ?location a wawo:GeographicalFeature .
}
```

## 7. Actor and Management

### CQ7.1: Who manages the river basin?
**Question**: Can we identify actors managing water systems?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?actor ?system
WHERE {
  ?actor a wawo:Actor ;
         wawo:manages ?system .
}
```

### CQ7.2: Which authorities oversee river basins?
**Question**: Can we identify river basin authorities?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?authority ?basin
WHERE {
  ?authority a wawo:RiverBasinAuthority ;
             wawo:manages ?basin .
  ?basin a wawo:RiverBasin .
}
```

## 8. Industrial Sources

### CQ8.1: What types of industries produce wastewater?
**Question**: Can we classify industrial wastewater producers by sector?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?industry ?sector ?waterMass
WHERE {
  ?industry a wawo:Industry ;
            wawo:produces ?waterMass .
  # Optional: link to industrial sector if available
}
```

### CQ8.2: What is the population equivalent of wastewater producers?
**Question**: Can we aggregate wastewater loads by population equivalent?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?producer ?popEq (SUM(?popEq) as ?totalLoad)
WHERE {
  ?producer a wawo:WastewaterProducer ;
            wawo:populationEquivalent ?popEq .
}
GROUP BY ?producer
```

## 9. Normative Reasoning

### CQ9.1: What are the components of regulatory norms?
**Question**: Can we query the structure of a regulative norm?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?norm ?activation ?maintenance ?expiration
WHERE {
  ?norm a wawo:RegulativeNorm ;
        wawo:hasActivationCondition ?activation ;
        wawo:hasMaintenanceCondition ?maintenance ;
        wawo:hasExpirationCondition ?expiration .
}
```

### CQ9.2: Which norms are obligations vs prohibitions?
**Question**: Can we distinguish between different types of deontic norms?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?norm ?type
WHERE {
  ?norm a ?type .
  ?type rdfs:subClassOf* wawo:DeonticNorm .
}
```

### CQ9.3: What sanctions apply to norm violations?
**Question**: Can we query sanctions associated with regulatory norms?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?norm ?sanction
WHERE {
  ?norm a wawo:RegulativeNorm ;
        wawo:hasSanction ?sanction .
}
```

## 10. Aggregate Statistics

### CQ10.1: What are average water quality indicators across river sections?
**Question**: Can we compute statistics on water quality across locations?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT
  (AVG(?bod) as ?avgBOD) (MAX(?bod) as ?maxBOD) (MIN(?bod) as ?minBOD)
  (AVG(?cod) as ?avgCOD) (MAX(?cod) as ?maxCOD) (MIN(?cod) as ?minCOD)
  (AVG(?ss) as ?avgSS) (MAX(?ss) as ?maxSS) (MIN(?ss) as ?minSS)
  (AVG(?tn) as ?avgTN) (MAX(?tn) as ?maxTN) (MIN(?tn) as ?minTN)
  (AVG(?tp) as ?avgTP) (MAX(?tp) as ?maxTP) (MIN(?tp) as ?minTP)
WHERE {
  ?riverSection a wawo:RiverSection ;
                wawo:hasWaterMass ?waterMass .
  ?waterMass wawo:biologicalOxygenDemandConcentration ?bod ;
             wawo:chemicalOxygenDemandConcentration ?cod ;
             wawo:suspendedSolidConcentration ?ss ;
             wawo:totalNitrogenConcentration ?tn ;
             wawo:totalPhosphorusConcentration ?tp .
}
```

### CQ10.2: How many treatment facilities are in each basin?
**Question**: Can we count facilities by geographical region?

**SPARQL Query**:
```sparql
PREFIX wawo: <http://www.semanticweb.org/riverbasin#>

SELECT ?basin (COUNT(?facility) as ?facilityCount)
WHERE {
  ?facility a wawo:WaterTreatmentFacility ;
            wawo:locatedIn ?basin .
  ?basin a wawo:RiverBasin .
}
GROUP BY ?basin
```

## Summary

These competency questions cover:
1. **Water quality classification** - testing reasoning with concentration thresholds
2. **Regulatory compliance** - checking WWTP requirements
3. **Flow tracking** - following water through the system
4. **Contaminant monitoring** - detecting pollutants
5. **Event detection** - identifying meteorological situations
6. **Infrastructure mapping** - tracing network connections
7. **Stakeholder management** - identifying responsibilities
8. **Industrial loads** - tracking wastewater sources
9. **Normative structure** - understanding regulatory norms
10. **Aggregate analysis** - computing statistics

The Python test suite will validate that the ontology can answer all these questions correctly using SPARQL queries and OWL reasoning.
