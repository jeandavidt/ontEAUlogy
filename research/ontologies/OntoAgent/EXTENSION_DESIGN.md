# OntoAgent Extensions for Water Domain Optimization

## Extension Overview

This document proposes systematic extensions to OntoAgent to support optimization agents that can discover, orchestrate, and execute simulation agents for water treatment systems.

## Core Extension Areas

### 1. Simulation Agent Extensions

#### Plant Description Module
```turtle
@prefix ontosim: <http://example.org/ontology/simulation#> .
@prefix ontoagent: <http://www.jparksimulator.com/ontology/ontoad Agent#> .

# Plant hierarchy
ontosim:Plant a owl:Class ;
    rdfs:subClassOf ontoagent:AgentCapability .

ontosim:ProcessUnit a owl:Class ;
    rdfs:subClassOf ontoagent:ModelComponent .

ontosim:Submodel a owl:Class ;
    rdfs:subClassOf ontoagent:ModelComponent .

ontosim:Parameter a owl:Class ;
    rdfs:subClassOf msm:Parameter .

ontosim:hasProcessUnit a owl:ObjectProperty ;
    rdfs:domain ontosim:Plant ;
    rdfs:range ontosim:ProcessUnit .

ontosim:hasSubmodel a owl:ObjectProperty ;
    rdfs:domain ontosim:ProcessUnit ;
    rdfs:range ontosim:Submodel .

ontosim:hasParameter a owl:ObjectProperty ;
    rdfs:domain [owl:unionOf (ontosim:ProcessUnit ontosim:Submodel)] ;
    rdfs:range ontosim:Parameter .

# Flow connections
ontosim:FlowConnection a owl:Class ;
    rdfs:subClassOf ontoagent:ModelRelationship .

ontosim:connectsFrom a owl:ObjectProperty ;
    rdfs:domain ontosim:FlowConnection ;
    rdfs:range ontosim:ProcessUnit .

ontosim:connectsTo a owl:ObjectProperty ;
    rdfs:domain ontosim:FlowConnection ;
    rdfs:range ontosim:ProcessUnit .

ontosim:flowRate a owl:DatatypeProperty ;
    rdfs:domain ontosim:FlowConnection ;
    rdfs:range xsd:float .

# Data sources
ontosim:DataSource a owl:Class ;
    rdfs:subClassOf ontoagent:DataCapability .

ontosim:describesPartOf a owl:ObjectProperty ;
    rdfs:domain ontosim:DataSource ;
    rdfs:range ontosim:Plant .

ontosim:availableParameters a owl:ObjectProperty ;
    rdfs:domain ontosim:DataSource ;
    rdfs:range ontosim:Parameter .

ontosim:dataFreshness a owl:DatatypeProperty ;
    rdfs:domain ontosim:DataSource ;
    rdfs:range xsd:dateTime .

ontosim:dataQuality a owl:DatatypeProperty ;
    rdfs:domain ontosim:DataSource ;
    rdfs:range xsd:float .
```

#### Control System Module
```turtle
# Controllers
ontosim:Controller a owl:Class ;
    rdfs:subClassOf ontoagent:ControlCapability .

ontosim:controls a owl:ObjectProperty ;
    rdfs:domain ontosim:Controller ;
    rdfs:range ontosim:ProcessUnit .

ontosim:ControlAlgorithm a owl:Class ;
    rdfs:subClassOf ontoagent:Method .

ontosim:algorithm a owl:ObjectProperty ;
    rdfs:domain ontosim:Controller ;
    rdfs:range ontosim:ControlAlgorithm .

ontosim:controlledVariable a owl:ObjectProperty ;
    rdfs:domain ontosim:Controller ;
    rdfs:range ontosim:Parameter .

ontosim:manipulatedVariable a owl:ObjectProperty ;
    rdfs:domain ontosim:Controller ;
    rdfs:range ontosim:Parameter .

ontosim:algorithmInput a owl:ObjectProperty ;
    rdfs:domain ontosim:ControlAlgorithm ;
    rdfs:range ontosim:Parameter .
```

### 2. Scenario Description Extensions

#### Scenario Specification
```turtle
# Scenario types
ontosim:SimulationScenario a owl:Class ;
    rdfs:subClassOf ontoagent:TaskSpecification .

ontosim:HistoricalScenario a owl:Class ;
    rdfs:subClassOf ontosim:SimulationScenario .

ontosim:ProspectiveScenario a owl:Class ;
    rdfs:subClassOf ontosim:SimulationScenario .

ontosim:AlternateScenario a owl:Class ;
    rdfs:subClassOf ontosim:SimulationScenario .

# Scenario properties
ontosim:hasPurpose a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range [owl:oneOf (ontosim:Calibration ontosim:Optimization ontosim:Computation)] .

ontosim:hasInitialCondition a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range ontosim:Parameter .

ontosim:timePeriod a owl:DatatypeProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range xsd:duration .

ontosim:modelledQuantities a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range ontosim:Parameter .
```

#### Data Requirements and Outputs
```turtle
# Data requirement tracking
ontosim:DataRequirement a owl:Class ;
    rdfs:subClassOf ontoagent:Constraint .

ontosim:requiresData a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range ontosim:DataRequirement .

ontosim:requiredFields a owl:ObjectProperty ;
    rdfs:domain ontosim:DataRequirement ;
    rdfs:range ontosim:Parameter .

ontosim:hasKnownData a owl:ObjectProperty ;
    rdfs:domain ontosim:DataRequirement ;
    rdfs:range ontosim:Parameter .

ontosim:desiredOutput a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range ontosim:Parameter .
```

### 3. Simulation Execution Extensions

#### Critical Missing: Numerical Configuration
```turtle
# Solver configuration
ontosim:NumericalSolver a owl:Class ;
    rdfs:subClassOf ontoagent:ExecutionParameter .

ontosim:solverType a owl:ObjectProperty ;
    rdfs:domain ontosim:NumericalSolver ;
    rdfs:range [owl:oneOf (ontosim:Euler ontosim:RungeKutta ontosim:DASSL ontosim:Adams)] .

ontosim:timeStep a owl:DatatypeProperty ;
    rdfs:domain ontosim:NumericalSolver ;
    rdfs:range xsd:float .

ontosim:minTimeStep a owl:DatatypeProperty ;
    rdfs:domain ontosim:NumericalSolver ;
    rdfs:range xsd:float .

ontosim:maxTimeStep a owl:DatatypeProperty ;
    rdfs:domain ontosim:NumericalSolver ;
    rdfs:range xsd:float .

ontosim:convergenceTolerance a owl:DatatypeProperty ;
    rdfs:domain ontosim:NumericalSolver ;
    rdfs:range xsd:float .

ontosim:maxIterations a owl:DatatypeProperty ;
    rdfs:domain ontosim:NumericalSolver ;
    rdfs:range xsd:integer .

# Integration parameters
ontosim:hasSolver a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range ontosim:NumericalSolver .
```

#### Computational Resources
```turtle
ontosim:ComputationalResource a owl:Class ;
    rdfs:subClassOf ontoagent:SystemConstraint .

ontosim:memoryLimit a owl:DatatypeProperty ;
    rdfs:domain ontosim:ComputationalResource ;
    rdfs:range xsd:integer .

ontosim:maxProcessingTime a owl:DatatypeProperty ;
    rdfs:domain ontosim:ComputationalResource ;
    rdfs:range xsd:duration .

ontosim:parallelProcessing a owl:DatatypeProperty ;
    rdfs:domain ontosim:ComputationalResource ;
    rdfs:range xsd:boolean .

ontosim:hasResourceRequirement a owl:ObjectProperty ;
    rdfs:domain ontosim:SimulationScenario ;
    rdfs:range ontosim:ComputationalResource .
```

### 4. Optimization Agent Extensions

#### Objective and Constraint Modeling
```turtle
# Optimization objectives
ontoopt:OptimizationObjective a owl:Class ;
    rdfs:subClassOf ontoagent:AgentCapability .

ontoopt:objectiveType a owl:ObjectProperty ;
    rdfs:domain ontoopt:OptimizationObjective ;
    rdfs:range [owl:oneOf (ontoopt:MinimizeCost ontopt:MaximizeEfficiency ontopt:MinimizeEnergy ontopt:MaximizeReuse)] .

ontoopt:targetVariable a owl:ObjectProperty ;
    rdfs:domain ontopt:OptimizationObjective ;
    rdfs:range ontosim:Parameter .

ontoopt:weight a owl:DatatypeProperty ;
    rdfs:domain ontoopt:OptimizationObjective ;
    rdfs:range xsd:float .

# Decision variables
ontoopt:DecisionVariable a owl:Class ;
    rdfs:subClassOf ontosim:Parameter .

ontoopt:hasDecisionVariable a owl:ObjectProperty ;
    rdfs:domain ontoopt:OptimizationScenario ;
    rdfs:range ontoopt:DecisionVariable .

ontoopt:variableBounds a owl:DatatypeProperty ;
    rdfs:domain ontopt:DecisionVariable ;
    rdfs:range xsd:string .  # Format: "min,max"

# Constraints
ontoopt:Constraint a owl:Class ;
    rdfs:subClassOf ontoagent:SystemConstraint .

ontoopt:constraintType a owl:ObjectProperty ;
    rdfs:domain ontopt:Constraint ;
    rdfs:range [owl:oneOf (ontoopt:MassBalance ontopt:QualityLimits ontopt:CapacityLimits ontopt:RegulatoryCompliance)] .

ontoopt:constraintExpression a owl:DatatypeProperty ;
    rdfs:domain ontopt:Constraint ;
    rdfs:range xsd:string .  # Mathematical expression
```

### 5. Agent Capability Extensions

#### Performance Metrics
```turtle
# Agent performance description
ontoperf:AgentPerformance a owl:Class ;
    rdfs:subClassOf ontoagent:QualityAttribute .

ontoperf:simulationSpeed a owl:DatatypeProperty ;
    rdfs:domain ontoperf:AgentPerformance ;
    rdfs:range xsd:float .

ontoperf:accuracy a owl:DatatypeProperty ;
    rdfs:domain ontoperf:AgentPerformance ;
    rdfs:range xsd:float .

ontoperf:computationalCost a owl:DatatypeProperty ;
    rdfs:domain ontoperf:AgentPerformance ;
    rdfs:range xsd:float .

ontoperf:hasPerformance a owl:ObjectProperty ;
    rdfs:domain ontoagent:Agent ;
    rdfs:range ontoperf:AgentPerformance .
```

#### Data Quality and Provenance
```turtle
# Data quality metrics
ontodq:DataQuality a owl:Class ;
    rdfs:subClassOf ontoagent:QualityAttribute .

ontodq:freshness a owl:DatatypeProperty ;
    rdfs:domain ontodq:DataQuality ;
    rdfs:range xsd:duration .

ontodq:accuracy a owl:DatatypeProperty ;
    rdfs:domain ontodq:DataQuality ;
    rdfs:range xsd:float .

ontodq:sourceReliability a owl:DatatypeProperty ;
    rdfs:domain ontodq:DataQuality ;
    rdfs:range xsd:float .

ontodq:hasDataQuality a owl:ObjectProperty ;
    rdfs:domain ontosim:DataSource ;
    rdfs:range ontodq:DataQuality .

# Provenance
ontoprov:Provenance a owl:Class ;
    rdfs:subClassOf ontoagent:Metadata .

ontoprov:source a owl:DatatypeProperty ;
    rdfs:domain ontoprov:Provenance ;
    rdfs:range xsd:string .

ontoprov:lastUpdated a owl:DatatypeProperty ;
    rdfs:domain ontoprov:Provenance ;
    rdfs:range xsd:dateTime .

ontoprov:hasProvenance a owl:ObjectProperty ;
    rdfs:domain [owl:unionOf (ontosim:DataSource ontosim:Parameter)] ;
    rdfs:range ontoprov:Provenance .
```

## Integration Example: Complete Simulation Request

```turtle
@prefix ex: <http://example.org/watersystem/> .
@prefix ontosim: <http://example.org/ontology/simulation#> .
@prefix ontoagent: <http://www.jparksimulator.com/ontology/ontoad Agent#> .

# The optimization agent
ex:WaterSystemOptimizer a ontoagent:Agent ;
    rdfs:label "Water Treatment System Optimizer" ;
    ontoagent:hasCapability ontoopt:SystemOptimization ;
    ontoagent:canUse ex:GPSSimulator, ex:WESTSimulator ;
    ontoagent:hasPerformance ex:OptimizerPerformance .

# Available simulation agents
ex:GPSSimulator a ontoagent:Agent ;
    rdfs:label "GPS-X Simulation Agent" ;
    ontoagent:hasService ex:GPSService ;
    ontoagent:supportsModels [ontosim:ProcessType ontosim:ActivatedSludge] ;
    ontoperf:hasPerformance ex:GPSPerformance .

ex:WESTSimulator a ontoagent:Agent ;
    rdfs:label "WEST Simulation Agent" ;
    ontoagent:hasService ex:WESTService ;
    ontoagent:supportsModels [ontosim:ProcessType ontosim:MembraneBioreactor] ;
    ontoperf:hasPerformance ex:WESTPerformance .

# Simulation scenario specification
ex:TreatmentOptimizationScenario a ontosim:SimulationScenario ;
    rdfs:label "WWTP Optimization Scenario" ;
    ontosim:hasPurpose ontosim:Optimization ;
    ontosim:timePeriod "P30D"^^xsd:duration ;
    ontosim:hasSolver ex:SolverConfig ;
    ontosim:hasResourceRequirement ex:ResourceLimits ;
    ontosim:requiresData ex:DataRequirements ;
    ontosim:desiredOutput ex:OptimizationResults .

# Numerical solver configuration (CRITICAL - was missing from original list)
ex:SolverConfig a ontosim:NumericalSolver ;
    ontosim:solverType ontosim:DASSL ;
    ontosim:timeStep "0.1"^^xsd:float ;
    ontosim:minTimeStep "0.001"^^xsd:float ;
    ontosim:maxTimeStep "1.0"^^xsd:float ;
    ontosim:convergenceTolerance "1.0E-6"^^xsd:float ;
    ontosim:maxIterations "1000"^^xsd:integer .

# Plant description
ex:WWTPPlant a ontosim:Plant ;
    ontosim:hasProcessUnit ex:PrimaryClarifier, ex:AerationTank, ex:SecondaryClarifier ;
    ontosim:hasDataSource ex:SCADASystem ;
    ontosim:hasController ex:DOController, ex:FlowController .

# Data requirements with availability tracking
ex:DataRequirements a ontosim:DataRequirement ;
    ontosim:requiredFields ex:InfluentFlow, ex:InfluentBOD, ex:InfluentCOD, ex:Temperature ;
    ontosim:hasKnownData ex:InfluentFlow, ex:Temperature ;
    ontosim:missingData ex:InfluentBOD, ex:InfluentCOD .
```

## Assessment Summary

### ✅ Your Original List Covers (90%):
- Plant hierarchy and topology
- Control system modeling  
- Scenario specification
- Data requirements tracking
- Output specification

### ⚠️ Critical Additions Needed:
1. **Numerical Solver Configuration** - Essential for simulation initiation
2. **Computational Resource Limits** - Required for execution constraints
3. **Agent Performance Metrics** - Needed for intelligent agent selection
4. **Data Quality/Provenance** - Essential for reliable optimization

### 🎯 Final Recommendation:
Your component list is excellent and covers 90% of what's needed. The extensions above fill the remaining 10% and provide the ontological framework to make it operational with OntoAgent.