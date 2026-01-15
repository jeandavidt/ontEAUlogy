"""
Phase 1: Load and Inspect SAREF4WATER Ontology
"""

from rdflib import Graph, Namespace
from owlready2 import get_ontology
import os

# Load with rdflib
print("="*80)
print("PHASE 1: LOAD AND INSPECT SAREF4WATER")
print("="*80)

owl_path = "/Users/jeandavidt/Developer/jeandavidt/ontEAUlogy/research/ontologies/SAREF4WATER/saref4watr_github.owl"

print(f"\nLoading ontology from: {owl_path}")
print(f"File exists: {os.path.exists(owl_path)}")
print(f"File size: {os.path.getsize(owl_path)} bytes")

# Load with rdflib for basic inspection
g = Graph()
try:
    g.parse(owl_path, format="xml")
    print(f"\n✓ Successfully loaded with rdflib")
    print(f"  Total triples: {len(g)}")
except Exception as e:
    print(f"\n✗ Failed to load with rdflib: {e}")
    exit(1)

# Define namespaces
S4WATR = Namespace("https://w3id.org/def/S4WATR#")
SAREF = Namespace("https://w3id.org/saref#")
SAREF4CITY = Namespace("https://w3id.org/def/saref4city#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")

# Extract ontology metadata
print("\n" + "="*80)
print("ONTOLOGY METADATA")
print("="*80)

query_metadata = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX terms: <http://purl.org/dc/terms/>

SELECT ?property ?value
WHERE {
    <https://w3id.org/def/S4WATR> ?property ?value .
}
"""

for row in g.query(query_metadata):
    print(f"  {row.property}: {row.value}")

# Count classes
print("\n" + "="*80)
print("CLASS COUNT")
print("="*80)

query_classes = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT (COUNT(DISTINCT ?class) as ?count)
WHERE {
    ?class a owl:Class .
}
"""

for row in g.query(query_classes):
    print(f"  Total classes defined: {row.count}")

# List all S4WATR classes
query_s4watr_classes = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX s4watr: <https://w3id.org/def/S4WATR#>

SELECT ?class ?label ?comment
WHERE {
    ?class a owl:Class .
    FILTER(STRSTARTS(STR(?class), "https://w3id.org/def/S4WATR#"))
    OPTIONAL { ?class rdfs:label ?label }
    OPTIONAL { ?class rdfs:comment ?comment }
}
ORDER BY ?class
"""

print("\nS4WATR-specific classes:")
for row in g.query(query_s4watr_classes):
    label = row.label if row.label else "No label"
    print(f"  - {row['class'].split('#')[1]}: {label}")

# Count object properties
print("\n" + "="*80)
print("OBJECT PROPERTIES")
print("="*80)

query_obj_props = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?property ?label ?domain ?range
WHERE {
    ?property a owl:ObjectProperty .
    FILTER(STRSTARTS(STR(?property), "https://w3id.org/def/S4WATR#"))
    OPTIONAL { ?property rdfs:label ?label }
    OPTIONAL { ?property rdfs:domain ?domain }
    OPTIONAL { ?property rdfs:range ?range }
}
ORDER BY ?property
"""

print("\nS4WATR object properties:")
for row in g.query(query_obj_props):
    prop_name = str(row.property).split('#')[1]
    domain_name = str(row.domain).split('#')[1] if row.domain else "Not specified"
    range_name = str(row.range).split('#')[1] if row.range else "Not specified"
    print(f"  - {prop_name}")
    print(f"    Domain: {domain_name}")
    print(f"    Range: {range_name}")

# Count data properties
print("\n" + "="*80)
print("DATA PROPERTIES")
print("="*80)

query_data_props = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?property ?label ?domain ?range
WHERE {
    ?property a owl:DatatypeProperty .
    FILTER(STRSTARTS(STR(?property), "https://w3id.org/def/S4WATR#"))
    OPTIONAL { ?property rdfs:label ?label }
    OPTIONAL { ?property rdfs:domain ?domain }
    OPTIONAL { ?property rdfs:range ?range }
}
ORDER BY ?property
"""

print("\nS4WATR data properties:")
for row in g.query(query_data_props):
    prop_name = str(row.property).split('#')[1]
    domain_name = str(row.domain).split('#')[1] if row.domain else "Not specified"
    range_name = str(row.range).split('#')[1] if row.range else "Not specified"
    print(f"  - {prop_name}")
    print(f"    Domain: {domain_name}")
    print(f"    Range: {range_name}")

# List individuals
print("\n" + "="*80)
print("NAMED INDIVIDUALS")
print("="*80)

query_individuals = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?individual ?type ?label
WHERE {
    ?individual a owl:NamedIndividual .
    OPTIONAL { ?individual a ?type . FILTER(?type != owl:NamedIndividual) }
    OPTIONAL { ?individual rdfs:label ?label }
}
ORDER BY ?individual
"""

print("\nNamed individuals:")
for row in g.query(query_individuals):
    ind_name = str(row.individual).split('#')[1]
    type_name = str(row.type).split('#')[1] if row.type else "Not typed"
    print(f"  - {ind_name} (type: {type_name})")

# Check imports
print("\n" + "="*80)
print("IMPORTS ANALYSIS")
print("="*80)

query_imports = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?import
WHERE {
    ?ontology a owl:Ontology .
    OPTIONAL { ?ontology owl:imports ?import }
}
"""

imports_found = False
for row in g.query(query_imports):
    import_uri = row['import'] if 'import' in row else None
    if import_uri:
        print(f"  Imports: {import_uri}")
        imports_found = True

if not imports_found:
    print("  No explicit owl:imports declarations found")
    print("  WARNING: Ontology references SAREF and SAREF4CITY but doesn't import them")

# Check for external references
print("\n" + "="*80)
print("EXTERNAL NAMESPACE REFERENCES")
print("="*80)

namespaces_used = set()
for s, p, o in g:
    for term in [s, p, o]:
        if hasattr(term, 'startswith'):
            if term.startswith('https://w3id.org/saref#'):
                namespaces_used.add('SAREF')
            elif term.startswith('https://w3id.org/def/saref4city#'):
                namespaces_used.add('SAREF4CITY')
            elif term.startswith('http://www.opengis.net/ont/geosparql#'):
                namespaces_used.add('GeoSPARQL')
            elif term.startswith('http://www.w3.org/2003/01/geo/wgs84_pos#'):
                namespaces_used.add('WGS84')
            elif term.startswith('http://www.w3.org/2006/time#'):
                namespaces_used.add('TIME')

print("External namespaces referenced:")
for ns in sorted(namespaces_used):
    print(f"  - {ns}")

print("\n" + "="*80)
print("LOADING WITH OWLREADY2 (for reasoning)")
print("="*80)

try:
    onto = get_ontology(f"file://{owl_path}").load()
    print(f"✓ Successfully loaded with owlready2")
    print(f"  Ontology IRI: {onto.base_iri}")
    print(f"  Classes: {len(list(onto.classes()))}")
    print(f"  Object Properties: {len(list(onto.object_properties()))}")
    print(f"  Data Properties: {len(list(onto.data_properties()))}")
    print(f"  Individuals: {len(list(onto.individuals()))}")
    print(f"  Imported ontologies: {onto.imported_ontologies}")
except Exception as e:
    print(f"✗ Failed to load with owlready2: {e}")

print("\n" + "="*80)
print("PHASE 1 COMPLETE")
print("="*80)
