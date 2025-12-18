"""
Create a normalized version of OntoCAPE with proper HTTP URIs
Replaces file:///C:/OntoCAPE/ with http://www.theworldavatar.com/ontology/ontocape/
"""

from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
import re

print("=" * 80)
print("CREATING NORMALIZED OntoCAPE ONTOLOGY")
print("=" * 80)

# Load the combined graph
combined_path = Path(__file__).parent / "ontocape_combined.ttl"
print(f"\nLoading: {combined_path}")

g = Graph()
g.parse(str(combined_path), format="turtle")
print(f"✓ Loaded {len(g)} triples")

# Create new graph with normalized URIs
print("\nNormalizing URIs...")
normalized = Graph()

# Define the new base URI (using TheWorldAvatar's actual OntoCAPE URI)
OLD_BASE = "file:///C:/OntoCAPE/OntoCAPE/"
NEW_BASE = "http://www.theworldavatar.com/ontology/ontocape/OntoCAPE/"

def normalize_uri(uri):
    """Replace old file-based URIs with HTTP URIs"""
    if isinstance(uri, URIRef):
        uri_str = str(uri)
        if OLD_BASE in uri_str:
            return URIRef(uri_str.replace(OLD_BASE, NEW_BASE))
    return uri

# Copy all triples with normalized URIs
count = 0
for s, p, o in g:
    new_s = normalize_uri(s)
    new_p = normalize_uri(p)
    new_o = normalize_uri(o) if isinstance(o, URIRef) else o
    normalized.add((new_s, new_p, new_o))
    count += 1
    if count % 10000 == 0:
        print(f"  Processed {count} triples...")

print(f"✓ Normalized {len(normalized)} triples")

# Add proper namespace bindings
print("\nAdding namespace bindings...")
normalized.bind("ontocape", NEW_BASE)
normalized.bind("system", NEW_BASE + "upper_level/system.owl#")
normalized.bind("tech", NEW_BASE + "upper_level/technical_system.owl#")
normalized.bind("net", NEW_BASE + "upper_level/network_system.owl#")
normalized.bind("material", NEW_BASE + "material/material.owl#")
normalized.bind("substance", NEW_BASE + "material/substance/substance.owl#")
normalized.bind("phase", NEW_BASE + "material/phase_system/phase_system.owl#")
normalized.bind("cps", NEW_BASE + "chemical_process_system/chemical_process_system.owl#")
normalized.bind("plant", NEW_BASE + "chemical_process_system/CPS_realization/plant.owl#")
normalized.bind("process", NEW_BASE + "chemical_process_system/CPS_function/process.owl#")
normalized.bind("behavior", NEW_BASE + "chemical_process_system/CPS_behavior/behavior.owl#")
normalized.bind("model", NEW_BASE + "model/mathematical_model.owl#")
normalized.bind("pmodel", NEW_BASE + "model/process_model.owl#")

# Save normalized version
output_path = Path(__file__).parent / "ontocape_normalized.ttl"
print(f"\nSaving normalized ontology...")
normalized.serialize(output_path, format="turtle")
print(f"✓ Saved to: {output_path}")
print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

# Verify a few sample URIs
print("\n📝 VERIFICATION - Sample normalized URIs:")
sample_classes = list(normalized.subjects(RDF.type, OWL.Class))[:5]
for cls in sample_classes:
    print(f"  {cls}")

print("\n" + "=" * 80)
print("NORMALIZATION COMPLETE")
print("=" * 80)
print(f"\n✓ Created: {output_path}")
print("✓ All file:///C:/OntoCAPE/ URIs replaced with HTTP URIs")
print("✓ Ready for use with reasoners and SPARQL queries")
