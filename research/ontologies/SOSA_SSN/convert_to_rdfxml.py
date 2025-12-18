"""Convert SOSA Turtle to RDF/XML for owlready2 compatibility."""

from pathlib import Path
from rdflib import Graph

base_path = Path(__file__).parent

# Load Turtle file
print("Loading SOSA from Turtle...")
g = Graph()
g.parse(base_path / "sosa_updated.ttl", format="turtle")
print(f"Loaded {len(g)} triples")

# Save as RDF/XML
output_path = base_path / "sosa_updated.rdf"
print(f"Saving to RDF/XML: {output_path}")
g.serialize(destination=output_path, format="xml")
print("Done!")
