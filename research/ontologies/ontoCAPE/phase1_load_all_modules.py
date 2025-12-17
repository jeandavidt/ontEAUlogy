"""
Phase 1: Load and Inspect ALL OntoCAPE Modules
Loads all OWL files individually since they have hardcoded Windows paths
"""

from pathlib import Path
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from collections import defaultdict
import sys

# Get the project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Path to OntoCAPE
ontocape_dir = Path(__file__).parent / "OntoCAPE"

print("=" * 80)
print("PHASE 1: LOAD AND INSPECT ALL OntoCAPE MODULES")
print("=" * 80)

# Load all OWL files into a single graph
print("\n1. LOADING ALL MODULES")
print("-" * 80)

combined_graph = Graph()
owl_files = list(ontocape_dir.rglob("*.owl"))

# Exclude test and example files
owl_files = [f for f in owl_files if "test" not in f.name.lower()
             and "example" not in f.name.lower()
             and f.name != "OntoCAPE.owl"]  # Skip the main wrapper

print(f"Found {len(owl_files)} OWL module files (excluding tests/examples)")

loaded_files = []
failed_files = []

for owl_file in owl_files:
    try:
        g = Graph()
        g.parse(str(owl_file), format="xml")
        # Merge into combined graph
        combined_graph += g
        loaded_files.append(owl_file)
        rel_path = owl_file.relative_to(ontocape_dir)
        print(f"  ✓ {rel_path} ({len(g)} triples)")
    except Exception as e:
        failed_files.append((owl_file, str(e)))
        rel_path = owl_file.relative_to(ontocape_dir)
        print(f"  ✗ {rel_path}: {e}")

print(f"\n✓ Successfully loaded {len(loaded_files)} modules")
if failed_files:
    print(f"✗ Failed to load {len(failed_files)} modules")
print(f"Total combined triples: {len(combined_graph)}")

# Get all namespaces from combined graph
print("\n2. NAMESPACES IN COMBINED GRAPH")
print("-" * 80)
namespaces = {}
for prefix, ns in combined_graph.namespaces():
    if prefix and not prefix.startswith('ns'):  # Skip auto-generated ns1, ns2, etc.
        namespaces[prefix] = str(ns)

print(f"Found {len(namespaces)} distinct namespaces")
# Show OntoCAPE-specific ones
ontocape_ns = {k: v for k, v in namespaces.items() if 'ontocape' in v.lower() or 'C:/OntoCAPE' in v}
print("\nOntoCAPE namespaces:")
for prefix, ns in sorted(ontocape_ns.items())[:15]:
    print(f"  {prefix}: {ns}")
if len(ontocape_ns) > 15:
    print(f"  ... and {len(ontocape_ns) - 15} more")

# Basic statistics
print("\n3. BASIC STATISTICS")
print("-" * 80)

# Count classes
classes = set(combined_graph.subjects(RDF.type, OWL.Class))
classes = [c for c in classes if not isinstance(c, type(None)) and not str(c).startswith('_')]
print(f"Classes: {len(classes)}")

# Count object properties
obj_props = set(combined_graph.subjects(RDF.type, OWL.ObjectProperty))
print(f"Object Properties: {len(obj_props)}")

# Count data properties
data_props = set(combined_graph.subjects(RDF.type, OWL.DatatypeProperty))
print(f"Data Properties: {len(data_props)}")

# Count annotation properties
ann_props = set(combined_graph.subjects(RDF.type, OWL.AnnotationProperty))
print(f"Annotation Properties: {len(ann_props)}")

# Count individuals
individuals_query = """
SELECT (COUNT(DISTINCT ?ind) as ?count)
WHERE {
    ?ind a ?class .
    ?class a owl:Class .
    FILTER(!isBlank(?ind))
}
"""
result = list(combined_graph.query(individuals_query))
if result and result[0]:
    print(f"Individuals: {result[0][0]}")

# Analyze class hierarchy
print("\n4. CLASS HIERARCHY ANALYSIS")
print("-" * 80)

# Find top-level classes (no superclass or only owl:Thing)
top_classes = []
for cls in classes:
    superclasses = list(combined_graph.objects(cls, RDFS.subClassOf))
    # Filter out blank nodes and owl:Thing
    superclasses = [s for s in superclasses if not isinstance(s, type(None))
                    and str(s) != str(OWL.Thing)]
    if not superclasses:
        # Get label if available
        labels = list(combined_graph.objects(cls, RDFS.label))
        label = str(labels[0]) if labels else None
        top_classes.append((cls, label))

print(f"Top-level classes (no superclass): {len(top_classes)}")
print("\nSample top-level classes:")
for cls, label in sorted(top_classes, key=lambda x: str(x[0]))[:15]:
    local_name = str(cls).split('#')[-1].split('/')[-1]
    label_str = f" ({label})" if label else ""
    print(f"  - {local_name}{label_str}")
if len(top_classes) > 15:
    print(f"  ... and {len(top_classes) - 15} more")

# Analyze by module/category
print("\n5. CLASSES BY MODULE CATEGORY")
print("-" * 80)

module_classes = defaultdict(list)
for cls in classes:
    cls_str = str(cls)
    # Extract module from URI
    if '/OntoCAPE/' in cls_str:
        parts = cls_str.split('/OntoCAPE/')[1].split('/')
        if len(parts) > 1:
            module = parts[0]
        else:
            module = parts[0].split('#')[0].replace('.owl', '')
        module_classes[module].append(cls)

print("Class count by module category:")
for module in sorted(module_classes.keys()):
    print(f"  {module}: {len(module_classes[module])} classes")

# Sample properties
print("\n6. SAMPLE OBJECT PROPERTIES")
print("-" * 80)
for prop in list(obj_props)[:15]:
    local_name = str(prop).split('#')[-1].split('/')[-1]
    # Get label
    labels = list(combined_graph.objects(prop, RDFS.label))
    label = f" ({labels[0]})" if labels else ""
    # Get domain/range
    domains = list(combined_graph.objects(prop, RDFS.domain))
    ranges = list(combined_graph.objects(prop, RDFS.range))
    domain_str = f" [domain: {str(domains[0]).split('#')[-1].split('/')[-1]}]" if domains else ""
    range_str = f" [range: {str(ranges[0]).split('#')[-1].split('/')[-1]}]" if ranges else ""
    print(f"  - {local_name}{label}{domain_str}{range_str}")

print("\n7. SAMPLE DATA PROPERTIES")
print("-" * 80)
for prop in list(data_props)[:15]:
    local_name = str(prop).split('#')[-1].split('/')[-1]
    labels = list(combined_graph.objects(prop, RDFS.label))
    label = f" ({labels[0]})" if labels else ""
    domains = list(combined_graph.objects(prop, RDFS.domain))
    ranges = list(combined_graph.objects(prop, RDFS.range))
    domain_str = f" [domain: {str(domains[0]).split('#')[-1].split('/')[-1]}]" if domains else ""
    range_str = f" [range: {str(ranges[0]).split('#')[-1].split('/')[-1]}]" if ranges else ""
    print(f"  - {local_name}{label}{domain_str}{range_str}")

# Look for water/wastewater related concepts
print("\n8. WATER/WASTEWATER RELATED CONCEPTS")
print("-" * 80)

water_keywords = ['water', 'wastewater', 'aqueous', 'liquid', 'flow', 'treatment',
                  'reactor', 'tank', 'pump', 'pipe', 'stream']

relevant_classes = []
for cls in classes:
    cls_str = str(cls).lower()
    local_name = str(cls).split('#')[-1].split('/')[-1]

    if any(keyword in cls_str.lower() or keyword in local_name.lower() for keyword in water_keywords):
        labels = list(combined_graph.objects(cls, RDFS.label))
        label = str(labels[0]) if labels else None
        relevant_classes.append((local_name, label, cls))

if relevant_classes:
    print(f"Found {len(relevant_classes)} potentially relevant classes:")
    for name, label, uri in sorted(relevant_classes)[:20]:
        label_str = f" ({label})" if label else ""
        print(f"  - {name}{label_str}")
    if len(relevant_classes) > 20:
        print(f"  ... and {len(relevant_classes) - 20} more")
else:
    print("No classes found with water/wastewater keywords")
    print("(This is expected - OntoCAPE is a general process engineering ontology)")

# Save the combined graph for later use
print("\n9. SAVING COMBINED GRAPH")
print("-" * 80)
output_file = Path(__file__).parent / "ontocape_combined.ttl"
combined_graph.serialize(output_file, format="turtle")
print(f"✓ Saved combined graph to: {output_file}")
print(f"  ({len(combined_graph)} triples)")

print("\n" + "=" * 80)
print("PHASE 1 COMPLETE")
print("=" * 80)
print("\nKey Findings:")
print(f"  - {len(loaded_files)} modules successfully loaded")
print(f"  - {len(classes)} classes")
print(f"  - {len(obj_props)} object properties")
print(f"  - {len(data_props)} data properties")
print(f"  - {len(combined_graph)} total triples")
print(f"\nNext steps: Phase 2 (Create test instances) and Phase 3 (Query testing)")
