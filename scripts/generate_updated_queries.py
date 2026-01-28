#!/usr/bin/env python3
"""
Generate Updated SPARQL Queries

Creates SPARQL queries aligned with the current waterFRAME ontology structure.
Focuses on queries that have full or partial coverage in the ontology.
"""

from pathlib import Path
from typing import Dict


def get_query_templates() -> Dict[str, str]:
    """Return dictionary of SPARQL query templates aligned with current ontology"""

    queries = {}

    # CQ1: What are all the nodes in a catchment?
    queries['cq01_all_nodes'] = """# CQ1: What are all the nodes (plants, sources, junctions, sinks) in a given catchment?
# Updated to use current ontology classes

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX bfo: <http://purl.obolibrary.org/obo/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?node ?nodeType ?nodeLabel ?comment
WHERE {
    # Material entities that are part of water infrastructure
    {
        # Treatment plants
        ?node a ?nodeType .
        VALUES ?nodeType {
            wf:WastewaterTreatmentPlant
            wf:DrinkingWaterPlant
        }
    } UNION {
        # Industrial facilities
        ?node a ?nodeType .
        VALUES ?nodeType {
            wf:IndustrialFacility
            wf:TextileIndustry
            wf:FoodProcessingIndustry
            wf:ElectronicsManufacturing
            wf:PharmaceuticalIndustry
            wf:Brewery
        }
    } UNION {
        # Residential areas
        ?node a ?nodeType .
        VALUES ?nodeType {
            wf:ResidentialDistrict
            wf:Household
        }
    } UNION {
        # Natural water bodies
        ?node a ?nodeType .
        VALUES ?nodeType {
            wf:River
            wf:RiverSegment
            wf:Lake
            wf:Groundwater
        }
    } UNION {
        # Water system components
        ?node a ?nodeType .
        ?nodeType rdfs:subClassOf wf:WaterSystemComponent .
    }

    # Optional metadata
    OPTIONAL { ?node rdfs:label ?nodeLabel }
    OPTIONAL { ?node rdfs:comment ?comment }
}
ORDER BY ?nodeType ?nodeLabel
"""

    # CQ2: Flow connections between nodes
    queries['cq02_flow_connections_updated'] = """# CQ2: What flows connect Node A to Node B?
# Updated to use port-based connections and flow properties

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Query 1: Direct flow connections via flowsTo property
SELECT ?source ?target ?sourceLabel ?targetLabel
WHERE {
    ?source wf:flowsTo ?target .

    OPTIONAL { ?source rdfs:label ?sourceLabel }
    OPTIONAL { ?target rdfs:label ?targetLabel }
}
ORDER BY ?sourceLabel ?targetLabel

# Query 2: Port-based connections
# SELECT ?sourceNode ?sourcePort ?targetPort ?targetNode ?sourceLabel ?targetLabel
# WHERE {
#     # Source node has an output port
#     ?sourceNode wf:hasOutputPort ?sourcePort .
#     ?sourcePort a wf:OutputPort .
#
#     # Target node has an input port
#     ?targetNode wf:hasInputPort ?targetPort .
#     ?targetPort a wf:InputPort .
#
#     # Ports are connected (need connection property)
#     ?sourcePort wf:connectsTo ?targetPort .
#
#     OPTIONAL { ?sourceNode rdfs:label ?sourceLabel }
#     OPTIONAL { ?targetNode rdfs:label ?targetLabel }
# }
# ORDER BY ?sourceLabel ?targetLabel
"""

    # CQ10: Water quality parameters
    queries['cq10_water_quality_parameters'] = """# CQ10: What quality parameters characterize the water at Node N?
# Updated to use WaterQualityObservation and observation properties

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?observation ?parameter ?paramLabel ?value ?unit ?observedAt ?timestamp
WHERE {
    # Find all observations
    ?observation a wf:WaterQualityObservation ;
                wf:observedParameter ?parameter ;
                wf:observedValue ?value .

    # Optional: Filter by specific node/location
    # FILTER(STR(?observedAt) = "YourNodeIdentifier")

    # Get parameter label
    OPTIONAL {
        ?parameter rdfs:label ?paramLabel
    }

    # Optional observation metadata
    OPTIONAL { ?observation wf:observedAt ?observedAt }
    OPTIONAL { ?observation wf:observedOn ?timestamp }
    OPTIONAL { ?parameter wf:hasUnit ?unit }
}
ORDER BY ?observedAt ?paramLabel
"""

    # CQ17: Computational model for entity
    queries['cq17_model_for_entity'] = """# CQ17: What computational model is associated with Unit Process U?
# Uses ProcessModel and ComputationalAgent classes

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Query 1: Find models representing an entity
SELECT ?entity ?entityLabel ?model ?modelLabel ?modelType
WHERE {
    # Specify the entity of interest
    # BIND(wf:WWTP1 AS ?entity)

    ?entity rdfs:label ?entityLabel .

    # Find model that represents this entity
    ?model wf:representsEntity ?entity ;
           a ?modelType .

    FILTER(?modelType IN (wf:ProcessModel, wf:SimulationModel, wf:MathematicalModel))

    OPTIONAL { ?model rdfs:label ?modelLabel }
}
ORDER BY ?entityLabel ?modelLabel

# Query 2: Find computational agents simulating an entity
SELECT ?entity ?entityLabel ?agent ?agentLabel ?agentType ?model
WHERE {
    # Entity to find agents for
    # BIND(wf:WWTP1 AS ?entity)

    ?entity rdfs:label ?entityLabel .

    # Find agent simulating this entity
    ?agent wf:simulates ?entity ;
           a ?agentType .

    # Optionally get the model implemented by the agent
    OPTIONAL {
        ?agent wf:implements ?model
    }

    OPTIONAL { ?agent rdfs:label ?agentLabel }
}
ORDER BY ?entityLabel ?agentLabel
"""

    # CQ21: Parameter valid range
    queries['cq21_parameter_range'] = """# CQ21: What is the valid range for Parameter P in Model M?
# Uses ModelVariable properties

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?model ?modelLabel ?param ?paramLabel ?paramName ?minVal ?maxVal ?defaultVal ?unit ?isDecisionVar
WHERE {
    # Specify model
    # BIND(wf:WWTP1_Model AS ?model)

    ?model a wf:ProcessModel .
    OPTIONAL { ?model rdfs:label ?modelLabel }

    # Get parameters or inputs with ranges
    {
        ?model wf:hasParameter ?param .
    } UNION {
        ?model wf:hasInput ?param .
    } UNION {
        ?model wf:hasInputVariable ?param .
    }

    # Get range constraints
    OPTIONAL { ?param rdfs:label ?paramLabel }
    OPTIONAL { ?param wf:parameterName ?paramName }
    OPTIONAL { ?param wf:minValue ?minVal }
    OPTIONAL { ?param wf:maxValue ?maxVal }
    OPTIONAL { ?param wf:defaultValue ?defaultVal }
    OPTIONAL { ?param wf:hasUnit ?unit }
    OPTIONAL { ?param wf:isDecisionVariable ?isDecisionVar }
}
ORDER BY ?modelLabel ?paramName
"""

    # CQ22: How is model invoked?
    queries['cq22_model_invocation'] = """# CQ22: How is Model M invoked? (API endpoint, function signature, agent reference)
# Uses SoftwareSystem, ComputationalAgent, and HTTPGrounding

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Query 1: Find software system implementing a model
SELECT ?model ?modelLabel ?software ?apiEndpoint ?apiVersion
WHERE {
    # Specify the model
    # BIND(wf:WWTP1_Model AS ?model)

    ?model a wf:ProcessModel .
    OPTIONAL { ?model rdfs:label ?modelLabel }

    # Find software system
    ?model wf:implementedBy ?software .

    # Get API details
    OPTIONAL { ?software wf:apiEndpoint ?apiEndpoint }
    OPTIONAL { ?software wf:apiVersion ?apiVersion }
}

# Query 2: Find agent and operation details with HTTP grounding
SELECT ?agent ?agentLabel ?operation ?opLabel ?httpMethod ?opPath ?requestFormat ?responseFormat ?requiresAuth
WHERE {
    # Find agent implementing a model
    # ?agent wf:implements wf:WWTP1_Model .

    ?agent a wf:ComputationalAgent .
    OPTIONAL { ?agent rdfs:label ?agentLabel }

    # Get operations offered by agent
    ?agent wf:offersOperation ?operation .
    OPTIONAL { ?operation rdfs:label ?opLabel }

    # Get HTTP grounding details
    OPTIONAL {
        ?operation wf:hasHTTPGrounding ?grounding .
        ?grounding wf:httpMethod ?httpMethod ;
                  wf:operationPath ?opPath .
        OPTIONAL { ?grounding wf:requestFormat ?requestFormat }
        OPTIONAL { ?grounding wf:responseFormat ?responseFormat }
        OPTIONAL { ?grounding wf:requiresAuthentication ?requiresAuth }
    }
}
ORDER BY ?agentLabel ?opLabel
"""

    # CQ25: What optimization agents are available?
    queries['cq25_optimization_agents'] = """# CQ25: What optimization agents are available in the system?
# Uses ComputationalAgent and agent type hierarchy

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cap: <https://ugentbiomath.github.io/waterframe/capability#>

# Query 1: All computational agents
SELECT ?agent ?agentLabel ?agentType ?agentVersion ?capabilities
WHERE {
    ?agent a ?agentType .

    # Filter for agent types
    FILTER(?agentType IN (wf:ComputationalAgent, wf:OptimizationAgent, wf:SimulationAgent,
                          wf:DataTransformAgent, wf:ReasoningAgent))

    OPTIONAL { ?agent rdfs:label ?agentLabel }
    OPTIONAL { ?agent wf:agentVersion ?agentVersion }

    # Get capabilities (grouped)
    OPTIONAL {
        ?agent wf:hasCapability ?capability .
        ?capability rdfs:label ?capLabel
    }
}
GROUP BY ?agent ?agentLabel ?agentType ?agentVersion
ORDER BY ?agentType ?agentLabel

# Query 2: Specifically optimization agents
SELECT ?agent ?agentLabel ?operations ?software ?endpoint
WHERE {
    ?agent a wf:OptimizationAgent .
    OPTIONAL { ?agent rdfs:label ?agentLabel }

    # Operations offered
    OPTIONAL {
        ?agent wf:offersOperation ?op .
        ?op rdfs:label ?opLabel
    }

    # Where it runs
    OPTIONAL {
        ?agent wf:runsOn ?software .
        ?software wf:apiEndpoint ?endpoint
    }
}
GROUP BY ?agent ?agentLabel ?software ?endpoint
ORDER BY ?agentLabel
"""

    # CQ26: Agent capabilities
    queries['cq26_agent_capabilities'] = """# CQ26: What objective function types can Agent A handle?
# Uses capability system

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX cap: <https://ugentbiomath.github.io/waterframe/capability#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?agent ?agentLabel ?capability ?capLabel ?capType
WHERE {
    # Specify agent
    # BIND(wf:OptimizationAgent1 AS ?agent)

    ?agent a ?agentType .
    FILTER(?agentType IN (wf:ComputationalAgent, wf:OptimizationAgent))

    OPTIONAL { ?agent rdfs:label ?agentLabel }

    # Get capabilities
    ?agent wf:hasCapability ?capability .
    ?capability a ?capType .

    OPTIONAL { ?capability rdfs:label ?capLabel }
}
ORDER BY ?agentLabel ?capLabel
"""

    # CQ27: Constraint types
    queries['cq27_constraint_types'] = """# CQ27: What constraint types can Agent A handle?
# Uses preconditions and postconditions

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?agent ?agentLabel ?operation ?opLabel ?conditionType ?constraint ?constrainedParam
WHERE {
    # Specify agent
    # BIND(wf:OptimizationAgent1 AS ?agent)

    ?agent a ?agentType .
    FILTER(?agentType IN (wf:ComputationalAgent, wf:OptimizationAgent))

    OPTIONAL { ?agent rdfs:label ?agentLabel }

    # Get operations
    ?agent wf:offersOperation ?operation .
    OPTIONAL { ?operation rdfs:label ?opLabel }

    # Get preconditions and postconditions
    {
        ?operation wf:hasPrecondition ?condition .
        BIND("Precondition" AS ?conditionType)
    } UNION {
        ?operation wf:hasPostcondition ?condition .
        BIND("Postcondition" AS ?conditionType)
    }

    # Get constraint details
    OPTIONAL { ?condition wf:constraintExpression ?constraint }
    OPTIONAL { ?condition wf:constrainsParameter ?constrainedParam }
}
ORDER BY ?agentLabel ?opLabel ?conditionType
"""

    # CQ30-33: Optimization formulation queries
    queries['cq30_decision_variables'] = """# CQ30: For a given objective, which nodes have relevant decision variables?
# CQ32: What is the set of decision variables for a catchment-wide problem?

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Query 1: Find all decision variables in system
SELECT ?entity ?entityLabel ?model ?modelLabel ?decisionVar ?varLabel ?paramName ?minVal ?maxVal ?unit
WHERE {
    # Find models
    ?model a wf:ProcessModel .
    OPTIONAL { ?model rdfs:label ?modelLabel }

    # Model represents an entity
    OPTIONAL {
        ?model wf:representsEntity ?entity .
        ?entity rdfs:label ?entityLabel
    }

    # Get decision variables
    {
        ?model wf:hasParameter ?decisionVar .
        ?decisionVar wf:isDecisionVariable "true"^^xsd:boolean .
    } UNION {
        ?model wf:hasInputVariable ?decisionVar .
        ?decisionVar wf:isDecisionVariable "true"^^xsd:boolean .
    } UNION {
        ?model wf:hasInput ?decisionVar .
        ?decisionVar a wf:DecisionVariable .
    }

    # Get variable details
    OPTIONAL { ?decisionVar rdfs:label ?varLabel }
    OPTIONAL { ?decisionVar wf:parameterName ?paramName }
    OPTIONAL { ?decisionVar wf:minValue ?minVal }
    OPTIONAL { ?decisionVar wf:maxValue ?maxVal }
    OPTIONAL { ?decisionVar wf:hasUnit ?unit }
}
ORDER BY ?entityLabel ?paramName

# Query 2: Decision variables in a specific catchment
# SELECT ?entity ?entityLabel ?decisionVar ?varLabel ?paramName
# WHERE {
#     # Entities in catchment
#     ?entity wf:locatedInCatchment wf:GhentCatchment .
#     OPTIONAL { ?entity rdfs:label ?entityLabel }
#
#     # Their models
#     ?model wf:representsEntity ?entity .
#
#     # Decision variables (as above)
#     ?model wf:hasParameter ?decisionVar .
#     ?decisionVar wf:isDecisionVariable "true"^^xsd:boolean .
#
#     OPTIONAL { ?decisionVar rdfs:label ?varLabel }
#     OPTIONAL { ?decisionVar wf:parameterName ?paramName }
# }
# ORDER BY ?entityLabel ?paramName
"""

    queries['cq31_io_constraints'] = """# CQ31: What constraints link outputs of upstream nodes to inputs of downstream nodes?
# Uses operation composition via dataFlowsTo property chain axiom

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Query 1: Find composable operation sequences
SELECT ?upstreamOp ?upstreamLabel ?downstreamOp ?downstreamLabel ?sharedParam ?paramLabel
WHERE {
    # Upstream operation produces output
    ?upstreamOp wf:producesOutput ?output .

    # Downstream operation requires that output as input
    ?downstreamOp wf:requiresInput ?input .

    # Check if they're the same parameter type
    ?output wf:correspondsToVariable ?sharedParam .
    ?input wf:correspondsToVariable ?sharedParam .

    OPTIONAL { ?upstreamOp rdfs:label ?upstreamLabel }
    OPTIONAL { ?downstreamOp rdfs:label ?downstreamLabel }
    OPTIONAL { ?sharedParam rdfs:label ?paramLabel }
}
ORDER BY ?upstreamLabel ?downstreamLabel

# Query 2: Use inferred dataFlowsTo property (if reasoner active)
# SELECT ?upstreamOp ?upstreamLabel ?downstreamOp ?downstreamLabel
# WHERE {
#     # Automatically inferred via property chain axiom
#     ?upstreamOp wf:dataFlowsTo ?downstreamOp .
#
#     OPTIONAL { ?upstreamOp rdfs:label ?upstreamLabel }
#     OPTIONAL { ?downstreamOp rdfs:label ?downstreamLabel }
# }
# ORDER BY ?upstreamLabel ?downstreamLabel
"""

    queries['cq33_model_invocation_sequence'] = """# CQ33: What models must be invoked to evaluate a candidate solution?
# Uses agent and model dependencies

PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?agent ?agentLabel ?model ?modelLabel ?operation ?opLabel ?entity
WHERE {
    # Find agents in the system
    ?agent a ?agentType .
    FILTER(?agentType IN (wf:ComputationalAgent, wf:SimulationAgent, wf:OptimizationAgent))

    OPTIONAL { ?agent rdfs:label ?agentLabel }

    # Model implemented by agent
    OPTIONAL {
        ?agent wf:implements ?model .
        ?model rdfs:label ?modelLabel
    }

    # Entity simulated
    OPTIONAL {
        ?agent wf:simulates ?entity
    }

    # Operations to invoke
    OPTIONAL {
        ?agent wf:offersOperation ?operation .
        ?operation rdfs:label ?opLabel
    }
}
ORDER BY ?entity ?agentLabel
"""

    return queries


def save_queries(queries: Dict[str, str], output_dir: Path) -> None:
    """Save generated queries to files"""
    output_dir.mkdir(parents=True, exist_ok=True)

    for query_name, query_content in queries.items():
        output_file = output_dir / f"{query_name}.rq"
        with open(output_file, 'w') as f:
            f.write(query_content)
        print(f"✅ Generated: {output_file.name}")


def main():
    """Generate updated SPARQL queries"""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "data" / "competency_questions" / "sparql_updated"

    print("🔧 Generating Updated SPARQL Queries")
    print(f"   Output directory: {output_dir}")
    print()

    # Get query templates
    queries = get_query_templates()

    # Save queries
    print(f"📝 Saving {len(queries)} queries...")
    save_queries(queries, output_dir)

    print()
    print("=" * 60)
    print(f"✅ Successfully generated {len(queries)} updated SPARQL queries")
    print(f"   Location: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
