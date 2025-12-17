"""
Phase 1: Load and Inspect OntoCAPE Ontology
Following the protocol from agent_research.md
"""

from pathlib import Path
from rdflib import Graph, Namespace
from owlready2 import get_ontology
import sys

# Get the project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Path to OntoCAPE
ontocape_dir = Path(__file__).parent / "OntoCAPE"
main_owl = ontocape_dir / "OntoCAPE.owl"

print("=" * 80)
print("PHASE 1: LOAD AND INSPECT OntoCAPE")
print("=" * 80)

# First, let's understand the file structure
print("\n1. FILE STRUCTURE")
print("-" * 80)
print(f"Main OWL file: {main_owl}")
print(f"Exists: {main_owl.exists()}")

# Count all OWL files
owl_files = list(ontocape_dir.rglob("*.owl"))
print(f"\nTotal OWL files found: {len(owl_files)}")

# Organize by directory
from collections import defaultdict
by_category = defaultdict(list)
for f in owl_files:
    # Get the first subdirectory or "root"
    rel_path = f.relative_to(ontocape_dir)
    category = str(rel_path.parts[0]) if len(rel_path.parts) > 1 else "root"
    by_category[category].append(str(rel_path))

print("\nFiles by category:")
for category in sorted(by_category.keys()):
    print(f"  {category}: {len(by_category[category])} files")
    for file in sorted(by_category[category])[:3]:  # Show first 3
        print(f"    - {file}")
    if len(by_category[category]) > 3:
        print(f"    ... and {len(by_category[category]) - 3} more")

# Load with rdflib for basic inspection
print("\n2. LOADING WITH RDFLIB")
print("-" * 80)
try:
    g = Graph()
    print(f"Loading {main_owl}...")
    g.parse(str(main_owl), format="xml")
    print(f"✓ Successfully loaded {len(g)} triples")

    # Get namespaces
    print("\nNamespaces:")
    for prefix, ns in g.namespaces():
        print(f"  {prefix}: {ns}")

    # Basic counts using SPARQL
    print("\n3. BASIC STATISTICS (SPARQL)")
    print("-" * 80)

    # Count classes
    class_query = """
    SELECT (COUNT(DISTINCT ?class) as ?count)
    WHERE {
        ?class a owl:Class .
    }
    """
    result = list(g.query(class_query))
    print(f"Classes: {result[0][0]}")

    # Count object properties
    obj_prop_query = """
    SELECT (COUNT(DISTINCT ?prop) as ?count)
    WHERE {
        ?prop a owl:ObjectProperty .
    }
    """
    result = list(g.query(obj_prop_query))
    print(f"Object Properties: {result[0][0]}")

    # Count data properties
    data_prop_query = """
    SELECT (COUNT(DISTINCT ?prop) as ?count)
    WHERE {
        ?prop a owl:DatatypeProperty .
    }
    """
    result = list(g.query(data_prop_query))
    print(f"Data Properties: {result[0][0]}")

    # Count individuals
    ind_query = """
    SELECT (COUNT(DISTINCT ?ind) as ?count)
    WHERE {
        ?ind a ?class .
        ?class a owl:Class .
    }
    """
    result = list(g.query(ind_query))
    print(f"Individuals: {result[0][0]}")

    # List some top-level classes
    print("\n4. SAMPLE TOP-LEVEL CLASSES")
    print("-" * 80)
    top_classes_query = """
    SELECT DISTINCT ?class ?label
    WHERE {
        ?class a owl:Class .
        OPTIONAL { ?class rdfs:label ?label }
        FILTER(!isBlank(?class))
    }
    LIMIT 20
    """
    results = g.query(top_classes_query)
    for row in results:
        class_uri = row[0]
        label = row[1] if row[1] else "No label"
        # Get local name
        local_name = class_uri.split('#')[-1].split('/')[-1]
        print(f"  {local_name}: {label}")

    # Check for imports
    print("\n5. IMPORTS")
    print("-" * 80)
    imports_query = """
    SELECT DISTINCT ?import
    WHERE {
        ?ont owl:imports ?import .
    }
    """
    results = list(g.query(imports_query))
    if results:
        print(f"Found {len(results)} imports:")
        for row in results:
            print(f"  - {row[0]}")
    else:
        print("No owl:imports statements found in main file")
        print("(This is a modular ontology - modules may reference each other directly)")

except Exception as e:
    print(f"✗ Error loading with rdflib: {e}")
    import traceback
    traceback.print_exc()

# Try loading with owlready2
print("\n6. LOADING WITH OWLREADY2")
print("-" * 80)
try:
    # Convert file path to file:// URI
    onto_uri = main_owl.as_uri()
    print(f"Loading from: {onto_uri}")
    onto = get_ontology(onto_uri).load()

    print(f"✓ Successfully loaded ontology")
    print(f"Ontology IRI: {onto.base_iri}")

    # Basic counts
    classes = list(onto.classes())
    obj_props = list(onto.object_properties())
    data_props = list(onto.data_properties())
    individuals = list(onto.individuals())

    print(f"\nClasses: {len(classes)}")
    print(f"Object Properties: {len(obj_props)}")
    print(f"Data Properties: {len(data_props)}")
    print(f"Individuals: {len(individuals)}")

    # Show some example classes
    print("\nExample classes (first 10):")
    for cls in classes[:10]:
        print(f"  - {cls.name}")

    print("\nExample object properties (first 10):")
    for prop in obj_props[:10]:
        print(f"  - {prop.name}")

    # Check imports
    print(f"\nImported ontologies: {onto.imported_ontologies}")

except Exception as e:
    print(f"✗ Error loading with owlready2: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("PHASE 1 COMPLETE")
print("=" * 80)
