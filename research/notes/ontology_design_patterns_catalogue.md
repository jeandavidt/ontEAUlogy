# Comprehensive Ontology Design Patterns Catalogue

**Author**: Compiled from W3C and Manchester sources  
**Date**: December 16, 2024  
**Status of OntologyDesignPatterns.org**: Effectively abandoned (last meaningful update ~2010, official catalogue empty)

---

## Executive Summary

The OntologyDesignPatterns.org portal you referenced is unfortunately a graveyard. The "official catalogue" is empty, and most submissions remain uncertified. However, two legitimate, usable pattern catalogues exist:

1. **W3C Semantic Web Best Practices** (4 core patterns)
2. **Manchester Bio-Ontology Design Patterns** (17 patterns)

This document provides a comprehensive, sourced catalogue of all patterns from both repositories.

---

## Table of Contents

1. [W3C Patterns (4)](#w3c-patterns)
   - [N-ary Relations](#1-n-ary-relations)
   - [Classes as Property Values](#2-classes-as-property-values)
   - [Value Partitions and Value Sets](#3-value-partitions-and-value-sets)
   - [Simple Part-Whole Relations](#4-simple-part-whole-relations)
2. [Manchester Patterns (17)](#manchester-patterns)
   - [Extension ODPs (3)](#extension-odps)
   - [Good Practice ODPs (9)](#good-practice-odps)
   - [Domain Modelling ODPs (5)](#domain-modelling-odps)
3. [Application to Water Systems](#application-to-water-systems)

---

## W3C Patterns

**Source**: W3C Semantic Web Best Practices and Deployment Working Group (2004-2006)  
**Status**: Official W3C Working Group Notes (closed September 2006)  
**Quality**: High - these are the most authoritative and well-tested patterns

---

### 1. N-ary Relations

**Source**: [Defining N-ary Relations on the Semantic Web](https://www.w3.org/TR/swbp-n-aryRelations), W3C Working Group Note, 12 April 2006  
**Editors**: Natasha Noy (Stanford), Alan Rector (Manchester)  
**Contributors**: Pat Hayes, Chris Welty

#### Problem

OWL/RDF properties are inherently binary (link only two individuals), but many real-world scenarios require:
- Properties of relations (certainty, strength, source)
- Relations among >2 individuals
- Relations with ordered sequences of participants

#### Solution Pattern 1: Introduce New Class for Relation

Create a class representing the relation itself, with properties linking to each participant.

**When to use**:
- Additional attributes on binary relations
- Multiple aspects of same relation
- N-ary relations with no distinguished participant

**Example 1: Additional Attributes**

Use case: "Christine has breast tumor with high probability"

```turtle
@prefix : <http://example.org/> .

:Christine  
    a :Person ;  
    :has_diagnosis _:Diagnosis_Relation_1 .

_:Diagnosis_Relation_1  
    a :Diagnosis_Relation ;  
    :diagnosis_value :Breast_Tumor_Christine ;
    :diagnosis_probability :HIGH .
```

**Example 2: Multiple Aspects**

Use case: "Steve has temperature, which is high but falling"

```turtle
:Steve  
    a :Person ;  
    :has_temperature _:Temperature_Observation_1 .

_:Temperature_Observation_1  
    a :Temperature_Observation ;  
    :temperature_value :High ;
    :temperature_trend :Falling .
```

**Example 3: No Distinguished Participant**

Use case: "John buys 'Lenny the Lion' from books.example.com for $15 as birthday gift"

```turtle
:Purchase_1  
    a :Purchase ;  
    :has_buyer :John ;  
    :has_seller :books.example.com ;
    :has_object :Lenny_The_Lion ;  
    :has_purpose :Birthday_Gift ;
    :has_amount 15 .
```

**OWL DL Status**: Outside OWL DL (if using classes as values directly), but compatible with OWL DL if using restrictions

**Trade-offs**:
- ✓ Intuitive and succinct
- ✓ Direct access to relation structure
- ✗ Creates maintenance burden for local range/cardinality restrictions
- ✗ Inverse properties require more work
- ✗ Can proliferate classes for all combinations

#### Solution Pattern 2: Use Lists for Arguments

When order matters and participants form a sequence, use RDF lists or custom ordering relations.

**When to use**:
- One participant + ordered list of others
- Temporal sequences
- Spatial paths

**Example: Flight Itinerary**

Use case: "United Airlines flight 3177 visits LAX, DFW, JFK"

```turtle
:Flight_3177  
    a :Flight ;
    :flight_sequence :Segment_1 .

:Segment_1  
    a :FlightSegment ;
    :destination :LAX ;
    :next_segment :Segment_2 .

:Segment_2  
    a :FlightSegment ;
    :destination :DFW ;
    :next_segment :Segment_3 .

:Segment_3  
    a :FinalFlightSegment ;
    :destination :JFK .

:FinalFlightSegment  
    rdfs:subClassOf :FlightSegment ;
    rdfs:subClassOf  
        [ a owl:Restriction ;  
          owl:maxCardinality "0" ;  
          owl:onProperty :next_segment ] .
```

**OWL DL Status**: OWL Lite compatible

**Alternative**: Use `rdf:List` vocabulary, but this puts ontology in OWL Full

**Trade-offs**:
- ✓ Natural for sequences
- ✓ Explicit ordering
- ✗ Verbose for long sequences
- ✗ Generic list vocabulary less semantically precise

#### Why Not RDF Reification?

The W3C explicitly chose not to use RDF reification (`rdf:Statement`) because:
- N-ary relations describe **relation instances**, not **statements about triples**
- Additional arguments characterize the relation itself, not the statement
- Reification is designed for provenance/meta-information about triples

---

### 2. Classes as Property Values

**Source**: [Representing Classes As Property Values on the Semantic Web](https://www.w3.org/TR/swbp-classes-as-values), W3C Working Group Note, 5 April 2005  
**Editor**: Natasha Noy (Stanford)  
**Contributors**: Michael Uschold (Boeing), Chris Welty (IBM)

#### Problem

Sometimes it's convenient to use a class (e.g., `Animal`) as a property value (e.g., book subject). OWL Full and RDFS allow this, but OWL DL/Lite prohibit classes as values for most properties.

#### Use Case

Annotate books with animal species as subjects:
- "Lions: Life in the Pride" → subject is `Lion` (the class)
- "The African Lion" → subject is `AfricanLion` (the class)
- Query for books about lions should retrieve books about African lions (via `rdfs:subClassOf`)

#### Solution Approach 1: Direct (OWL Full)

Simply use classes as values.

```turtle
:LionsLifeInThePrideBook  
    a :Book ;  
    dc:subject :Lion .

:Lion a owl:Class .
```

**OWL DL Status**: Outside OWL DL  
**Trade-offs**:
- ✓ Most succinct and intuitive
- ✓ Direct access to class hierarchy
- ✗ Not compatible with OWL DL

#### Solution Approach 2: Create Instances

Create individuals corresponding to each class, use individuals as values.

```turtle
:LionSubject a :Lion .

:LionsLifeInThePrideBook  
    a :Book ;  
    dc:subject :LionSubject .
```

**OWL DL Status**: OWL Lite/DL compatible  
**Trade-offs**:
- ✓ Compatible with OWL DL
- ✓ Range restrictions straightforward
- ✗ No direct relation between subject individuals (reasoners can't infer `LionSubject` relates to `AfricanLionSubject`)
- ✗ Maintenance burden (keep classes and individuals synchronized)
- ✗ Changes semantics if class hierarchy is imported

#### Solution Approach 3: Parallel Hierarchy

Create class `Subject`, make all subjects individuals of this class, use custom property (e.g., `parentSubject`) to recreate hierarchy.

```turtle
:Subject a owl:Class .

:LionSubject  
    a :Subject ;  
    rdfs:seeAlso :Lion .

:AfricanLionSubject  
    a :Subject ;  
    rdfs:seeAlso :AfricanLion ;
    :parentSubject :LionSubject .

:parentSubject  
    a owl:TransitiveProperty ;
    rdfs:domain :Subject ;
    rdfs:range :Subject .
```

**OWL DL Status**: OWL Lite/DL compatible  
**Alternative**: Use [SKOS-Core](https://www.w3.org/2004/02/skos/core/) properties (`skos:broader`, `skos:narrower`)

**Trade-offs**:
- ✓ Compatible with OWL DL
- ✓ DL reasoners can infer transitive relations
- ✓ Explicit separation of subject terminology from ontology
- ✗ Two parallel hierarchies = serious maintenance burden
- ✗ Annotation property `rdfs:seeAlso` usually ignored by reasoners

#### Solution Approach 4: Restrictions in Lieu of Values

Create classes representing "books about X", use `owl:someValuesFrom` restrictions.

```turtle
:BookAboutLions  
    owl:equivalentClass  
        [ a owl:Class ;  
          owl:intersectionOf (
              [ a owl:Restriction ;  
                owl:onProperty dc:subject ;  
                owl:someValuesFrom :Lion ]   
              :Book
          ) ] .

:LionsLifeInThePrideBook a :BookAboutLions .
```

**OWL DL Status**: OWL DL compatible  
**Interpretation**: Subject is **some unspecified instance(s)** of the class, not the class itself

**Trade-offs**:
- ✓ Compatible with OWL DL
- ✓ DL reasoners can classify books automatically
- ✓ Hierarchy of book classes parallels subject hierarchy
- ✗ Different interpretation (prototypical instance vs. whole class)
- ✗ Cumbersome to express simple facts

**Variant**: Merge into anonymous restriction:

```turtle
:LionsLifeInThePrideBook  
    a :Book ;
    a [ a owl:Restriction ;  
        owl:onProperty dc:subject ;  
        owl:someValuesFrom :Lion ] .
```

#### Solution Approach 5: Annotation Properties

Treat property as `owl:AnnotationProperty` (classes can be annotation values in OWL DL).

```turtle
dc:subject a owl:AnnotationProperty .

:LionsLifeInThePrideBook  
    a :Book ;  
    dc:subject :Lion .
```

**OWL DL Status**: OWL DL compatible  
**Trade-offs**:
- ✓ Compatible with OWL DL
- ✓ Succinct
- ✗ Property cannot be object/datatype property elsewhere
- ✗ No restrictions allowed (cardinality, domain/range)
- ✗ DL reasoners ignore annotation properties

---

### 3. Value Partitions and Value Sets

**Source**: [Representing Specified Values in OWL: "value partitions" and "value sets"](https://www.w3.org/TR/swbp-specified-values), W3C Working Group Note, 17 May 2005  
**Editor**: Alan Rector (Manchester)

#### Problem

Represent features/qualities with constrained enumerated values:
- Size: small, medium, large
- Health status: poor, medium, good
- Severity: mild, moderate, severe

Requirements:
- Only one value allowed per feature
- Values should be mutually exclusive
- Possibly allow further subdivision

#### Solution Approach 1: Values as Class Partitions

Treat the quality as a class partitioned by disjoint value subclasses.

**Interpretation**: "John is tall" means John's height (an individual) lies in the "Tall" partition of the Height quality space.

```turtle
:Height a owl:Class .

:Tall rdfs:subClassOf :Height .
:Medium rdfs:subClassOf :Height .
:Short rdfs:subClassOf :Height .

# Make mutually disjoint
:Tall owl:disjointWith :Medium, :Short .
:Medium owl:disjointWith :Short .

# Make exhaustive
:Height owl:equivalentClass [
    owl:unionOf (:Tall :Medium :Short)
] .

:Person  
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty :has_height ;
        owl:allValuesFrom :Height
    ] .

:Tall_Person owl:equivalentClass [
    owl:intersectionOf (
        :Person
        [ a owl:Restriction ;
          owl:onProperty :has_height ;
          owl:someValuesFrom :Tall ]
    )
] .
```

**OWL DL Status**: OWL Lite/DL compatible  
**Trade-offs**:
- ✓ Compatible with OWL DL
- ✓ DL reasoners can classify individuals automatically
- ✓ Allows further subpartitioning (e.g., "very tall" as subclass of "tall")
- ✓ Reasoners detect inconsistencies (being both tall and short)
- ✗ Verbose
- ✗ Actual height value is unnamed

#### Solution Approach 2: Values as Individuals (Enumeration)

Quality class is enumeration of named individuals.

**Interpretation**: "John is in good health" means John has the individual `good_health` as value for `health_status`.

```turtle
:Health_Value owl:equivalentClass [
    owl:oneOf (:good_health :medium_health :poor_health)
] .

# Must declare all different (no unique name assumption in OWL)
:good_health owl:differentFrom :medium_health, :poor_health .
:medium_health owl:differentFrom :poor_health .

:has_health_status  
    a owl:FunctionalProperty ;
    rdfs:range :Health_Value .

:john :has_health_status :good_health .
```

**OWL DL Status**: OWL Lite (without `oneOf`), OWL DL compatible  
**Trade-offs**:
- ✓ Compatible with OWL DL
- ✓ Simple, direct value assignment
- ✓ Values are named individuals
- ✗ No possibility of further subpartitioning
- ✗ Must explicitly declare all individuals different

#### When to Use Which

| Feature | Partition (Approach 1) | Enumeration (Approach 2) |
|---------|----------------------|-------------------------|
| Further subdivision | Yes | No |
| Named values | No (use qualified individuals) | Yes |
| DL classification | Yes | Limited |
| Verbosity | Higher | Lower |
| Best for | Continuous qualities with conceptual partitions | Discrete, fixed sets of named values |

---

### 4. Simple Part-Whole Relations

**Source**: [Simple Part-Whole Relations in OWL Ontologies](https://www.w3.org/2001/sw/BestPractices/OEP/SimplePartWhole/), W3C Working Group Note (draft)  
**Editors**: Alan Rector, Chris Welty

#### Problem

OWL provides no built-in primitives for part-whole relations (unlike `rdfs:subClassOf`). Part-whole relations are ubiquitous but complex (see mereology literature).

#### Scope

This note covers **straightforward cases only** for defining classes involving part-whole relations. It does not address:
- Complex mereological theories
- Temporal aspects (parts changing over time)
- All the nuances debated in philosophical literature

#### Common Patterns

**Note**: This document was never finalized, but the following patterns are referenced in the literature:

1. **Simple transitive parthood**: `has_part` / `part_of` as transitive properties
2. **Structural parthood**: Restrictions on what parts a whole must/may have
3. **Inventory of parts**: Representing concrete objects and their parts
4. **Hierarchical parts**: Parts of hypothetical wholes (types, not tokens)
5. **Location-based parthood**: Geographic containment

**General structure** (from references):

```turtle
:has_part  
    a owl:TransitiveProperty, owl:ObjectProperty ;
    owl:inverseOf :part_of .

:part_of  
    a owl:TransitiveProperty, owl:ObjectProperty .

# Example: Finger is part of Hand
:Finger rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty :part_of ;
    owl:someValuesFrom :Hand
] .
```

**Trade-offs**:
- ✓ Transitive reasoning supported
- ✓ Inverse properties easy to define
- ✗ Doesn't distinguish different kinds of parthood (component, member, portion, etc.)
- ✗ Temporal aspects not addressed

**Reference**: Alan Rector's work on parthood, including distinctions between:
- Compositional (engine part of car)
- Membership (player part of team)
- Portion (slice part of pie)
- Containment (object in container)

**For water systems**: This pattern is directly relevant for representing:
- Unit processes as parts of treatment trains
- Catchments as parts of larger watershed systems
- Flow paths composed of segments

---

## Manchester Patterns

**Source**: [Ontology Design Patterns Public Catalogue](http://www.gong.manchester.ac.uk/odp/html/), University of Manchester  
**Publication**: Egaña et al. (2008), "Ontology Design Patterns for bio-ontologies: a case study on the Cell Cycle Ontology", *BMC Bioinformatics*  
**Status**: Maintained ~2009, focused on bio-ontologies  
**Quality**: High - extensively tested in bio-ontology applications

**Important note**: Individual pattern pages are not accessible via the web. Descriptions below are compiled from the paper and related literature.

---

### Extension ODPs

**Purpose**: Bypass OWL expressivity limitations

#### 1. Nary_DataType_Relationship

**Problem**: Represent n-ary relations where some arguments are datatypes (literals).

**Solution**: Similar to W3C n-ary relations pattern, but specifically handles cases where data properties are involved.

**Example**: Measurement with value, unit, and uncertainty:

```turtle
:Measurement_1  
    a :Measurement ;
    :measured_value "37.5"^^xsd:float ;
    :measurement_unit :Celsius ;
    :measurement_error "0.1"^^xsd:float .
```

**Relation to W3C patterns**: Specialized version of n-ary relations for mixed object/data properties.

#### 2. Exception

**Problem**: Represent general rules with exceptions (OWL's open-world assumption makes exceptions tricky).

**Solution**: Use explicit exception classes and property restrictions to carve out exceptions from general statements.

**Example**: "All birds fly, except penguins and ostriches"

```turtle
:Bird rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty :has_ability ;
    owl:someValuesFrom :Flying
] .

:Flightless_Bird  
    rdfs:subClassOf :Bird ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty :has_ability ;
        owl:allValuesFrom [
            owl:complementOf :Flying
        ]
    ] .

:Penguin rdfs:subClassOf :Flightless_Bird .
:Ostrich rdfs:subClassOf :Flightless_Bird .
```

**Trade-offs**:
- ✓ Explicit exception handling
- ✗ Verbose
- ✗ Requires careful modeling to avoid inconsistencies

#### 3. Nary_Relationship

**Problem**: General n-ary relationships (not specific to datatypes).

**Solution**: Manchester's take on the W3C n-ary relations pattern, likely with bio-ontology-specific conventions.

**Note**: Functionally equivalent to W3C N-ary Relations Pattern 1.

---

### Good Practice ODPs

**Purpose**: Achieve more robust, cleaner, maintainable ontologies

#### 4. Entity_Feature_Value (EFV)

**Problem**: Represent entities with qualities/features that have specific values, common in phenotype descriptions.

**Solution**: Triple pattern: Entity → Feature → Value

**Example**: Phenotype description

```turtle
:Patient_123  
    :has_feature :Blood_Pressure_Feature .

:Blood_Pressure_Feature  
    a :Blood_Pressure ;
    :has_value :Elevated .

:Elevated  
    a :Blood_Pressure_Value ;
    rdfs:subClassOf :Abnormal_BP_Value .
```

**Relation to W3C patterns**: Combines aspects of value partitions with n-ary relations.

**For water systems**: Directly applicable to water quality parameters (Entity: Sample → Feature: pH → Value: Alkaline)

#### 5. Selector

**Problem**: Select specific individuals from a class based on criteria.

**Solution**: Use restrictions with `hasValue` or `someValuesFrom` to define selecting criteria.

**Example**: "Select all patients with diabetes"

```turtle
:Diabetes_Patient owl:equivalentClass [
    owl:intersectionOf (
        :Patient
        [ a owl:Restriction ;
          owl:onProperty :has_diagnosis ;
          owl:someValuesFrom :Diabetes ]
    )
] .
```

**Trade-offs**:
- ✓ Enables automated classification
- ✓ Criteria explicit in ontology
- ✗ Can proliferate classes

#### 6. Normalisation

**Problem**: Decompose ontologies into independent skeleton taxonomies to improve modularity and maintainability (analogous to database normalization).

**Solution**: 
1. Create simple tree hierarchies for each dimension
2. Use properties and restrictions to recombine them

**Example**: Separate anatomy and pathology hierarchies

```turtle
# Anatomy hierarchy (simple tree)
:Heart rdfs:subClassOf :Organ .
:Left_Ventricle rdfs:subClassOf :Heart_Part .

# Pathology hierarchy (simple tree)
:Disease a owl:Class .
:Cardiomyopathy rdfs:subClassOf :Disease .

# Recombine with properties
:Cardiomyopathy rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty :has_location ;
    owl:someValuesFrom :Heart
] .
```

**Source**: Rector, A. (2003), "Modularisation of Domain Ontologies Implemented in Description Logics"

**Trade-offs**:
- ✓ Reduces tangled hierarchies
- ✓ Easier maintenance
- ✓ Better reuse
- ✗ More complex structure
- ✗ Requires discipline to maintain separation

**For water systems**: Separate process type, contaminant, and location hierarchies.

#### 7. Upper_Level_Ontology

**Problem**: Provide foundational categories to organize domain ontology.

**Solution**: Import or align with upper ontology (BFO, DOLCE, SUMO) to ground domain concepts.

**Example**: Using BFO

```turtle
# BFO categories
bfo:Material_Entity a owl:Class .
bfo:Process a owl:Class .
bfo:Quality a owl:Class .

# Domain concepts
:Treatment_Plant rdfs:subClassOf bfo:Material_Entity .
:Aeration rdfs:subClassOf bfo:Process .
:Water_Quality rdfs:subClassOf bfo:Quality .
```

**Trade-offs**:
- ✓ Principled organization
- ✓ Interoperability with other ontologies using same upper ontology
- ✗ Learning curve
- ✗ Upper ontology choice is contentious
- ✗ Can be overly philosophical

#### 8. Closure

**Problem**: Define when a class is "closed" (all instances explicitly stated) vs. "open" (may have unknown instances).

**Solution**: Use `owl:oneOf` for closed classes, leave open for others.

**Example**: Days of week (closed)

```turtle
:Day_Of_Week owl:equivalentClass [
    owl:oneOf (:Monday :Tuesday :Wednesday :Thursday :Friday :Saturday :Sunday)
] .
```

**Trade-offs**:
- ✓ Makes closed-world assumptions explicit
- ✗ Changes reasoning behavior
- ✗ Must be used carefully

#### 9. Entity_Quality

**Problem**: Represent qualities/attributes of entities (PATO pattern from bio-ontologies).

**Solution**: Similar to Entity_Feature_Value, with emphasis on formally defined quality types.

**Example**: Cell shape quality

```turtle
:Cell_1  
    :has_quality :Shape_Quality_1 .

:Shape_Quality_1  
    a :Shape ;
    :quality_value :Spherical .
```

**Relation to other patterns**: Closely related to EFV, distinguished by ontological commitment to qualities as first-class entities.

#### 10. Value_Partition

**Problem**: Same as W3C Value Partitions pattern.

**Solution**: Manchester's version, likely with bio-ontology examples.

**Note**: Functionally equivalent to W3C Value Partitions pattern (Approach 1).

#### 11. Entity_Property_Quality (EPQ)

**Problem**: Represent complex property-quality relationships for entities.

**Solution**: Extension of Entity_Quality with explicit property dimension.

**Example**: "Protein X has high concentration in blood"

```turtle
:Protein_X  
    :has_property_quality :Concentration_Quality_1 .

:Concentration_Quality_1  
    a :Concentration ;
    :property_of :Protein_X ;
    :location :Blood ;
    :quality_value :High .
```

**Trade-offs**:
- ✓ Highly expressive
- ✗ Very verbose
- ✗ Complex to maintain

#### 12. DefinedClass_Description

**Problem**: Make class definitions explicit and complete for automated classification.

**Solution**: Use `owl:equivalentClass` with intersection/union of restrictions.

**Example**: Defined class vs. primitive class

```turtle
# Primitive (asserted only)
:Mammal a owl:Class .

# Defined (necessary and sufficient conditions)
:Viviparous_Mammal owl:equivalentClass [
    owl:intersectionOf (
        :Mammal
        [ a owl:Restriction ;
          owl:onProperty :reproduction_method ;
          owl:hasValue :Live_Birth ]
    )
] .
```

**Trade-offs**:
- ✓ Enables automated classification
- ✓ Makes modeling decisions explicit
- ✗ Requires complete knowledge
- ✗ Easy to over-constrain

---

### Domain Modelling ODPs

**Purpose**: Solutions for specific modeling problems in biology (applicable to other domains)

#### 13. Interactor_Role_Interaction

**Problem**: Represent interactions where entities play specific roles.

**Solution**: Model interaction as a class, with properties linking to role-playing entities.

**Example**: Protein interaction

```turtle
:Interaction_1  
    a :Protein_Interaction ;
    :has_participant [
        a :Interactor ;
        :has_role :Enzyme ;
        :played_by :Protein_A
    ] ;
    :has_participant [
        a :Interactor ;
        :has_role :Substrate ;
        :played_by :Protein_B
    ] .
```

**Relation to W3C patterns**: Specialized version of n-ary relations with explicit role modeling.

**For water systems**: Relevant for modeling chemical reactions, biological processes in treatment (e.g., nitrification: ammonia as substrate, nitrosomonas as catalyst).

#### 14. Sequence

**Problem**: Represent ordered sequences (DNA, protein sequences, process steps).

**Solution**: Use ordering properties or RDF lists.

**Example**: Process sequence

```turtle
:Treatment_Process  
    :first_step :Screening ;
    :next_step :Primary_Settling ;
    :next_step :Aeration ;
    :next_step :Secondary_Settling .

:first_step rdfs:subPropertyOf :has_step .
:next_step  
    a owl:TransitiveProperty ;
    rdfs:subPropertyOf :has_step .
```

**Relation to W3C patterns**: Similar to W3C N-ary Relations Pattern 2 (lists).

**For water systems**: Treatment train sequences, sampling sequences.

#### 15. CompositePropertyChain

**Problem**: Define properties as compositions of other properties.

**Solution**: Use `owl:propertyChainAxiom` (OWL 2) or indirect restrictions.

**Example**: Transitive location

```turtle
# OWL 2 syntax
:located_in owl:propertyChainAxiom (
    :part_of
    :located_in
) .

# "If X part_of Y and Y located_in Z, then X located_in Z"
```

**Trade-offs**:
- ✓ Powerful inferencing
- ✓ Reduces redundant assertions
- ✗ Requires OWL 2
- ✗ Can cause performance issues with reasoners

**For water systems**: Flow paths composed of segments, chemical transformations across unit processes.

#### 16. List

**Problem**: Represent ordered lists of items.

**Solution**: Use RDF list vocabulary or custom ordering properties.

**Example**: RDF list

```turtle
:Treatment_Steps rdf:first :Screening ;
                 rdf:rest [
                     rdf:first :Settling ;
                     rdf:rest [
                         rdf:first :Aeration ;
                         rdf:rest rdf:nil
                     ]
                 ] .
```

**Relation to W3C patterns**: Direct use of RDF list vocabulary mentioned in W3C N-ary Relations Pattern 2.

#### 17. Adapted_SEP

**Problem**: Represent information that varies along spatial, temporal, or other dimensions (SEP = "Specified Entry Point" from software patterns).

**Solution**: Create dimension-specific slices with properties linking to context.

**Example**: Temperature varying by location and time

```turtle
:Lake_Temperature_Reading_1  
    a :Temperature_Observation ;
    :observed_value "15.3"^^xsd:float ;
    :spatial_context :Lake_Surface ;
    :temporal_context :Summer_2024 .
```

**Trade-offs**:
- ✓ Flexible for multi-dimensional data
- ✗ Verbose
- ✗ Can require many observations

**For water systems**: Quality parameters varying spatially (upstream/downstream) and temporally (seasonal, diurnal).

---

## Application to Water Systems

### Patterns Directly Applicable

| Pattern | Water System Use Case | Priority |
|---------|----------------------|----------|
| N-ary Relations (W3C) | Flow connections with quality, quantity, timestamp | **High** |
| Value Partitions (W3C) | Water quality classes (potable, agricultural, industrial) | **High** |
| Entity_Feature_Value (Manchester) | Sample → Parameter → Value (e.g., Sample_A → pH → 7.2) | **High** |
| Normalisation (Manchester) | Separate process, contaminant, location hierarchies | **High** |
| Interactor_Role_Interaction (Manchester) | Chemical/biological reactions in treatment | **Medium** |
| Sequence (Manchester) | Treatment train process order | **High** |
| CompositePropertyChain (Manchester) | Transitive flow paths through network | **Medium** |
| Simple Part-Whole (W3C) | Unit processes part of treatment plant | **High** |
| Classes as Property Values (W3C) | Water reuse category taxonomy | **Medium** |

### Patterns Requiring Adaptation

| Pattern | Needs Adaptation For | Difficulty |
|---------|---------------------|------------|
| Exception (Manchester) | Treatment bypass conditions | Medium |
| Upper_Level_Ontology (Manchester) | Align with BFO or custom foundational | High |
| Adapted_SEP (Manchester) | Spatio-temporal variation of quality | Medium |
| Selector (Manchester) | Regulatory compliance queries | Low |

### Patterns Less Relevant

- **Entity_Property_Quality**: Overly complex for water domain
- **DefinedClass_Description**: Useful but not domain-specific
- **Closure**: Rarely need closed-world semantics in water systems

---

## Pattern Selection Decision Tree

```
START: What are you trying to represent?

├─ Relation with >2 participants or metadata?
│  └─ Use: N-ary Relations (W3C Pattern 1)
│     ├─ Need ordered sequence? → N-ary Relations Pattern 2
│     └─ Need role semantics? → Interactor_Role_Interaction (Manchester)
│
├─ Enumerated values for a quality?
│  └─ Use: Value Partitions (W3C or Manchester)
│     ├─ Need subpartitioning? → Partition approach
│     └─ Fixed named values? → Enumeration approach
│
├─ Entity + attribute + value triple?
│  └─ Use: Entity_Feature_Value (Manchester)
│
├─ Ordered sequence of steps/items?
│  └─ Use: Sequence (Manchester) or N-ary Relations Pattern 2 (W3C)
│
├─ Part-whole relationships?
│  └─ Use: Simple Part-Whole Relations (W3C)
│
├─ Classes as annotation values?
│  └─ Use: Classes as Property Values (W3C)
│     ├─ Can use OWL Full? → Approach 1
│     ├─ Must stay in OWL DL? → Approaches 2-5
│
├─ Tangled multiple hierarchies?
│  └─ Use: Normalisation (Manchester)
│
└─ General expressivity limitation?
   └─ Check: Extension ODPs (Manchester)
```

---

## Critical Assessment

### What Works

1. **W3C patterns are solid**: Well-documented, extensively tested, clear trade-offs.
2. **Manchester patterns fill gaps**: Bio-specific patterns like EFV and EPQ address real modeling needs.
3. **Clear application domains**: Easy to identify when to use each pattern.

### What's Missing

1. **Temporal aspects**: Neither catalogue adequately addresses time-varying properties (mentioned as "Fluents" in W3C but never finalized).
2. **Uncertainty**: No patterns for probabilistic or fuzzy information.
3. **Provenance**: Limited guidance on tracking data sources and transformations (PROV-O fills this gap but isn't in these catalogues).
4. **Process modeling**: Both catalogues lack patterns for dynamic processes, state transitions, mass/energy balances.
5. **Agent-based systems**: No patterns for representing computational agents, their capabilities, or invocation protocols.

### For Your Water System Ontology

**Must-use patterns**:
1. N-ary Relations (flow metadata)
2. Value Partitions (quality classes)
3. Entity_Feature_Value (water quality)
4. Sequence (treatment trains)
5. Simple Part-Whole (system topology)

**Consider patterns**:
6. Normalisation (separate concerns)
7. Interactor_Role_Interaction (reactions)
8. CompositePropertyChain (transitive flows)

**Supplement with**:
- SOSA/SSN for observation pattern
- PROV-O for provenance
- QUDT for units
- Custom patterns for:
  - Model metadata (parameters, I/O, decision variables)
  - Agent capabilities and invocation
  - Process dynamics

---

## References

### W3C

- Noy, N. & Rector, A. (2006). "Defining N-ary Relations on the Semantic Web". W3C Working Group Note. https://www.w3.org/TR/swbp-n-aryRelations
- Noy, N. (2005). "Representing Classes As Property Values on the Semantic Web". W3C Working Group Note. https://www.w3.org/TR/swbp-classes-as-values
- Rector, A. (2005). "Representing Specified Values in OWL: 'value partitions' and 'value sets'". W3C Working Group Note. https://www.w3.org/TR/swbp-specified-values
- Rector, A. & Welty, C. "Simple Part-Whole Relations in OWL Ontologies". W3C Working Draft. https://www.w3.org/2001/sw/BestPractices/OEP/SimplePartWhole/

### Manchester

- Egaña Aranguren, M., Antezana, E., Kuiper, M., & Stevens, R. (2008). "Ontology Design Patterns for bio-ontologies: a case study on the Cell Cycle Ontology". *BMC Bioinformatics*, 9(Suppl 5):S1. https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-S5-S1
- Egaña Aranguren, M., Rector, A., Stevens, R., & Antezana, E. (2008). "Applying Ontology Design Patterns in bio-ontologies". *EKAW 2008*, LNCS 5268, pp. 7-16.
- Manchester ODP Catalogue: http://www.gong.manchester.ac.uk/odp/html/
- SourceForge project: http://sourceforge.net/projects/odps/

### General

- Gangemi, A. (2005). "Ontology Design Patterns for Semantic Web Content". *ISWC 2005*.
- Rector, A. (2003). "Modularisation of Domain Ontologies Implemented in Description Logics and related formalisms including OWL". *K-CAP 2003*.

---

**Document Status**: Complete catalogue as of December 16, 2024  
**Next Steps**: Apply these patterns to water systems competency questions, evaluate coverage gaps, develop custom patterns for model/agent representation
