"""
Phase 3: Test SPARQL Queries Against Competency Questions
"""

from rdflib import Graph, Namespace
from datetime import datetime

# Load ontology and test data
print("="*80)
print("PHASE 3: SPARQL QUERY TESTING")
print("="*80)

g = Graph()

# Load the ontology
owl_path = "/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/research/ontologies/SAREF4WATER/saref4watr_github.owl"
test_data_path = "/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/research/ontologies/SAREF4WATER/test_data.ttl"

print(f"\nLoading ontology: {owl_path}")
g.parse(owl_path, format="xml")
print(f"  Ontology triples: {len(g)}")

print(f"\nLoading test data: {test_data_path}")
g.parse(test_data_path, format="turtle")
print(f"  Total triples after loading test data: {len(g)}")

# Define namespaces
TEST = Namespace("http://example.org/test/")
S4WATR = Namespace("https://w3id.org/def/S4WATR#")
SAREF = Namespace("https://w3id.org/saref#")
SAREF4CITY = Namespace("https://w3id.org/def/saref4city#")

g.bind("test", TEST)
g.bind("s4watr", S4WATR)
g.bind("saref", SAREF)
g.bind("saref4city", SAREF4CITY)

# Results tracking
results = []

def run_query(cq_id, cq_text, query_text, expected_result, category):
    """Run a SPARQL query and record results"""
    print(f"\n{'='*80}")
    print(f"{cq_id}: {cq_text}")
    print(f"Category: {category}")
    print(f"{'='*80}")
    print(f"Query:\n{query_text}\n")

    try:
        query_results = list(g.query(query_text))

        if query_results:
            print(f"Results ({len(query_results)} rows):")
            for i, row in enumerate(query_results[:10], 1):  # Show first 10
                print(f"  {i}. {row}")
            if len(query_results) > 10:
                print(f"  ... and {len(query_results) - 10} more")
        else:
            print("Results: No results found")

        # Determine status
        if len(query_results) > 0:
            status = "PASS"
        elif "NOT SUPPORTED" in expected_result:
            status = "NOT SUPPORTED"
        else:
            status = "FAIL"

        print(f"\nStatus: {status}")
        print(f"Expected: {expected_result}")

        results.append({
            'cq_id': cq_id,
            'cq_text': cq_text,
            'category': category,
            'status': status,
            'result_count': len(query_results),
            'expected': expected_result
        })

    except Exception as e:
        print(f"ERROR: {e}")
        results.append({
            'cq_id': cq_id,
            'cq_text': cq_text,
            'category': category,
            'status': 'ERROR',
            'result_count': 0,
            'expected': expected_result,
            'error': str(e)
        })

# ============================================================================
# SYSTEM TOPOLOGY QUERIES
# ============================================================================

run_query(
    "CQ1",
    "What are all the nodes (plants, sources, junctions, sinks) in a given catchment?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?asset ?type ?label
    WHERE {
        ?asset a ?type .
        ?type rdfs:subClassOf* s4watr:WaterAsset .
        OPTIONAL { ?asset rdfs:label ?label }
    }
    ORDER BY ?type ?asset
    """,
    "Should return all WaterAsset instances (PlantA, WellB, ReservoirC, DamD, GroundwaterWellE)",
    "System Topology"
)

run_query(
    "CQ2",
    "What flows connect Node A to Node B?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX test: <http://example.org/test/>

    SELECT ?pipe ?label
    WHERE {
        ?pipe a s4watr:Pipe .
        OPTIONAL { ?pipe rdfs:label ?label }
    }
    """,
    "NOT SUPPORTED - Ontology has Pipe class but no properties to represent flow direction or connectivity",
    "System Topology"
)

run_query(
    "CQ3",
    "What are the possible input sources for Plant X?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?source
    WHERE {
        ?source a s4watr:WaterAsset .
    }
    """,
    "NOT SUPPORTED - No properties to represent flow connectivity between assets",
    "System Topology"
)

run_query(
    "CQ4",
    "What downstream nodes receive effluent from Plant X?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?downstream
    WHERE {
        ?downstream a s4watr:WaterAsset .
    }
    """,
    "NOT SUPPORTED - No properties to represent downstream/upstream relationships",
    "System Topology"
)

# ============================================================================
# TREATMENT CONFIGURATION QUERIES
# ============================================================================

run_query(
    "CQ6",
    "What unit processes comprise the treatment train at Plant X?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?process
    WHERE {
        ?process a ?type .
    }
    LIMIT 1
    """,
    "NOT SUPPORTED - No representation of unit processes or treatment trains",
    "Treatment Configuration"
)

run_query(
    "CQ9",
    "What is the design capacity of Unit Process U?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?capacity
    WHERE {
        ?asset a s4watr:WaterAsset .
    }
    """,
    "NOT SUPPORTED - No capacity property defined for WaterAsset",
    "Treatment Configuration"
)

# ============================================================================
# WATER QUALITY QUERIES
# ============================================================================

run_query(
    "CQ10",
    "What quality parameters characterize the water at Node N?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX saref: <https://w3id.org/saref#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?property ?label
    WHERE {
        {
            ?property a s4watr:WaterProperty .
        } UNION {
            ?property a s4watr:Physical .
        } UNION {
            ?property a s4watr:Chemical .
        }
        OPTIONAL { ?property rdfs:label ?label }
    }
    """,
    "Should return water quality properties (Physical and Chemical subclasses)",
    "Water Quality"
)

run_query(
    "CQ11",
    "What are the regulatory limits for Parameter P for Reuse Category R?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?limit
    WHERE {
        ?param a s4watr:WaterProperty .
    }
    """,
    "NOT SUPPORTED - No representation of regulatory limits or standards",
    "Water Quality"
)

run_query(
    "CQ13",
    "What contaminants are present in Source S above threshold T?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX saref: <https://w3id.org/saref#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?measurement ?value ?property
    WHERE {
        ?measurement a saref:Measurement ;
                    saref:hasValue ?value ;
                    saref:relatesToProperty ?property .
        FILTER(?value > 5.0)
    }
    """,
    "Partially supported - Can query measurements but no threshold/limit representation",
    "Water Quality"
)

# ============================================================================
# SOURCE/STREAM CLASSIFICATION QUERIES
# ============================================================================

run_query(
    "CQ14",
    "Is Stream S classified as greywater or blackwater?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?stream ?classification
    WHERE {
        ?stream a s4watr:WaterAsset .
    }
    """,
    "NOT SUPPORTED - No greywater/blackwater classification in ontology",
    "Source Classification"
)

run_query(
    "CQ15",
    "What sources in the catchment are classified as fit-for-purpose Category C?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?source
    WHERE {
        ?source a s4watr:WaterAsset .
    }
    """,
    "NOT SUPPORTED - No fit-for-purpose classification",
    "Source Classification"
)

# ============================================================================
# MODEL METADATA QUERIES
# ============================================================================

run_query(
    "CQ17",
    "What computational model is associated with Unit Process U?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?model
    WHERE {
        ?asset a s4watr:WaterAsset .
    }
    """,
    "NOT SUPPORTED - No representation of computational models",
    "Model Metadata"
)

run_query(
    "CQ18-22",
    "What are the input/output variables, parameters, and invocation methods for Model M?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?model
    WHERE {
        ?model a ?type .
    }
    LIMIT 1
    """,
    "NOT SUPPORTED - No model metadata representation",
    "Model Metadata"
)

# ============================================================================
# OPTIMIZATION AGENT QUERIES
# ============================================================================

run_query(
    "CQ25-29",
    "What optimization agents are available and what are their capabilities?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>

    SELECT ?agent
    WHERE {
        ?agent a ?type .
    }
    LIMIT 1
    """,
    "NOT SUPPORTED - No agent representation in ontology",
    "Optimization Agents"
)

# ============================================================================
# DEVICE AND MEASUREMENT QUERIES (What SAREF4WATER actually supports)
# ============================================================================

run_query(
    "ACTUAL-1",
    "What sensors are deployed in the water infrastructure?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX saref: <https://w3id.org/saref#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?sensor ?type ?label ?infrastructure
    WHERE {
        ?sensor a ?type .
        ?type rdfs:subClassOf* saref:Sensor .
        OPTIONAL { ?sensor rdfs:label ?label }
        OPTIONAL { ?sensor s4watr:usedIn ?infrastructure }
    }
    ORDER BY ?type ?sensor
    """,
    "Should return all sensor instances with their types and locations",
    "Actual Capabilities"
)

run_query(
    "ACTUAL-2",
    "What measurements have been made and what properties do they measure?",
    """
    PREFIX saref: <https://w3id.org/saref#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?measurement ?value ?unit ?property ?timestamp ?device
    WHERE {
        ?measurement a saref:Measurement ;
                    saref:hasValue ?value ;
                    saref:isMeasuredIn ?unit ;
                    saref:relatesToProperty ?property .
        OPTIONAL { ?measurement saref:hasTimeStamp ?timestamp }
        OPTIONAL { ?measurement saref:measurementMadeBy ?device }
    }
    ORDER BY ?timestamp
    """,
    "Should return all measurement instances with values, units, and timestamps",
    "Actual Capabilities"
)

run_query(
    "ACTUAL-3",
    "What properties does each sensor measure?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX saref: <https://w3id.org/saref#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?sensor ?property ?propLabel
    WHERE {
        ?sensor saref:measuresProperty ?property .
        OPTIONAL { ?property rdfs:label ?propLabel }
    }
    ORDER BY ?sensor
    """,
    "Should return sensor-to-property mappings",
    "Actual Capabilities"
)

run_query(
    "ACTUAL-4",
    "What devices manage which water assets?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?device ?asset ?deviceLabel ?assetLabel
    WHERE {
        ?device s4watr:manageWaterAsset ?asset .
        OPTIONAL { ?device rdfs:label ?deviceLabel }
        OPTIONAL { ?asset rdfs:label ?assetLabel }
    }
    """,
    "Should return device-to-asset management relationships",
    "Actual Capabilities"
)

run_query(
    "ACTUAL-5",
    "What infrastructure components exist and what assets do they contain?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?infrastructure ?asset ?label
    WHERE {
        ?infrastructure a s4watr:WaterInfrastructure ;
                       s4watr:isComposedBy ?asset .
        OPTIONAL { ?infrastructure rdfs:label ?label }
    }
    """,
    "Should return infrastructure composition relationships",
    "Actual Capabilities"
)

run_query(
    "ACTUAL-6",
    "What indicators are assigned to cities and which assets have indicators?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?indicator ?city ?asset
    WHERE {
        ?indicator a s4watr:Indicator .
        OPTIONAL { ?indicator s4watr:assignedTo ?city }
        OPTIONAL { ?asset s4watr:hasIndicator ?indicator }
    }
    """,
    "Should return indicator assignments",
    "Actual Capabilities"
)

run_query(
    "ACTUAL-7",
    "What are the device metadata (manufacturer, model, firmware, etc.)?",
    """
    PREFIX s4watr: <https://w3id.org/def/S4WATR#>
    PREFIX saref: <https://w3id.org/saref#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?device ?label ?manufacturer ?model ?firmware ?hardware ?fabrication
    WHERE {
        ?device a saref:Device .
        OPTIONAL { ?device rdfs:label ?label }
        OPTIONAL { ?device saref:hasManufacture ?manufacturer }
        OPTIONAL { ?device saref:hasModel ?model }
        OPTIONAL { ?device s4watr:hasFirmwareVersion ?firmware }
        OPTIONAL { ?device s4watr:hasHardwareVersion ?hardware }
        OPTIONAL { ?device s4watr:hasFabricationNo ?fabrication }
    }
    """,
    "Should return device metadata for all devices",
    "Actual Capabilities"
)

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n" + "="*80)
print("QUERY TEST SUMMARY")
print("="*80)

categories = {}
for result in results:
    cat = result['category']
    if cat not in categories:
        categories[cat] = {'PASS': 0, 'FAIL': 0, 'NOT SUPPORTED': 0, 'ERROR': 0}
    categories[cat][result['status']] += 1

print("\nResults by Category:")
for cat, counts in categories.items():
    total = sum(counts.values())
    print(f"\n{cat}:")
    for status, count in counts.items():
        if count > 0:
            pct = (count / total) * 100
            print(f"  {status}: {count}/{total} ({pct:.1f}%)")

total_queries = len(results)
status_counts = {'PASS': 0, 'FAIL': 0, 'NOT SUPPORTED': 0, 'ERROR': 0}
for result in results:
    status_counts[result['status']] += 1

print(f"\nOverall Results:")
for status, count in status_counts.items():
    if count > 0:
        pct = (count / total_queries) * 100
        print(f"  {status}: {count}/{total_queries} ({pct:.1f}%)")

print("\n" + "="*80)
print("DETAILED RESULTS")
print("="*80)

for result in results:
    print(f"\n{result['cq_id']}: {result['status']}")
    print(f"  Query: {result['cq_text']}")
    print(f"  Category: {result['category']}")
    print(f"  Result count: {result['result_count']}")
    print(f"  Expected: {result['expected']}")
    if 'error' in result:
        print(f"  Error: {result['error']}")

print("\n" + "="*80)
print("PHASE 3 COMPLETE")
print("="*80)
