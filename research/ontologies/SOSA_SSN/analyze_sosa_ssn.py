"""Analysis of SOSA/SSN ontology for water quality measurements."""

from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal
from rdflib.namespace import SKOS, XSD
from collections import defaultdict

# Define namespaces
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SSN = Namespace("http://www.w3.org/ns/ssn/")

def load_ontologies():
    """Load SOSA and SSN ontologies."""
    base_path = Path(__file__).parent

    g = Graph()

    # Load SOSA
    sosa_path = base_path / "sosa_updated.ttl"
    if sosa_path.exists():
        print(f"Loading SOSA from {sosa_path}")
        g.parse(sosa_path, format="turtle")
    else:
        print(f"SOSA file not found at {sosa_path}")

    # Load SSN
    ssn_path = base_path / "ssn.rdf"
    if ssn_path.exists():
        print(f"Loading SSN from {ssn_path}")
        g.parse(ssn_path, format="xml")
    else:
        print(f"SSN file not found at {ssn_path}")

    print(f"\nTotal triples loaded: {len(g)}")
    return g

def analyze_structure(g: Graph):
    """Analyze and report on ontology structure."""

    print("\n" + "="*80)
    print("ONTOLOGY STRUCTURE ANALYSIS")
    print("="*80)

    # Count classes
    classes = list(g.subjects(RDF.type, OWL.Class))
    rdfs_classes = list(g.subjects(RDF.type, RDFS.Class))
    all_classes = set(classes + rdfs_classes)

    print(f"\n📦 CLASSES ({len(all_classes)} total)")
    print("-" * 80)

    sosa_classes = [c for c in all_classes if str(c).startswith(str(SOSA))]
    ssn_classes = [c for c in all_classes if str(c).startswith(str(SSN))]

    print(f"\n  SOSA Classes ({len(sosa_classes)}):")
    for cls in sorted(sosa_classes):
        label = g.value(cls, RDFS.label)
        definition = g.value(cls, SKOS.definition)
        print(f"    • {cls.split('/')[-1]}")
        if label:
            print(f"      Label: {label}")
        if definition:
            def_str = str(definition)[:150] + "..." if len(str(definition)) > 150 else str(definition)
            print(f"      Definition: {def_str}")

    print(f"\n  SSN Classes ({len(ssn_classes)}):")
    for cls in sorted(ssn_classes):
        label = g.value(cls, RDFS.label)
        print(f"    • {cls.split('/')[-1]}: {label}")

    # Count properties
    obj_props = list(g.subjects(RDF.type, OWL.ObjectProperty))
    data_props = list(g.subjects(RDF.type, OWL.DatatypeProperty))

    print(f"\n🔗 OBJECT PROPERTIES ({len(obj_props)} total)")
    print("-" * 80)

    sosa_obj_props = [p for p in obj_props if str(p).startswith(str(SOSA))]
    ssn_obj_props = [p for p in obj_props if str(p).startswith(str(SSN))]

    print(f"\n  SOSA Object Properties ({len(sosa_obj_props)}):")
    for prop in sorted(sosa_obj_props):
        label = g.value(prop, RDFS.label)
        print(f"    • {prop.split('/')[-1]}: {label}")

    print(f"\n  SSN Object Properties ({len(ssn_obj_props)}):")
    for prop in sorted(ssn_obj_props):
        label = g.value(prop, RDFS.label)
        print(f"    • {prop.split('/')[-1]}: {label}")

    print(f"\n📊 DATA PROPERTIES ({len(data_props)} total)")
    print("-" * 80)
    for prop in sorted(data_props):
        if str(prop).startswith(str(SOSA)) or str(prop).startswith(str(SSN)):
            label = g.value(prop, RDFS.label)
            range_val = g.value(prop, RDFS.range)
            print(f"    • {prop.split('/')[-1]}: {label}")
            if range_val:
                print(f"      Range: {range_val.split('#')[-1]}")

def analyze_observation_pattern(g: Graph):
    """Analyze the observation pattern structure."""

    print("\n" + "="*80)
    print("OBSERVATION PATTERN ANALYSIS")
    print("="*80)

    # Find Observation class
    obs_class = SOSA.Observation

    # Find all properties that have Observation in their domain
    obs_properties = defaultdict(list)

    for prop in g.subjects(RDF.type, OWL.ObjectProperty):
        # Check schema:domainIncludes
        for domain in g.objects(prop, Namespace("http://schema.org/").domainIncludes):
            if domain == obs_class:
                obs_properties['domain'].append(prop)
        # Check rdfs:domain
        domain = g.value(prop, RDFS.domain)
        if domain == obs_class:
            obs_properties['domain'].append(prop)

    for prop in g.subjects(RDF.type, OWL.DatatypeProperty):
        for domain in g.objects(prop, Namespace("http://schema.org/").domainIncludes):
            if domain == obs_class:
                obs_properties['domain'].append(prop)
        domain = g.value(prop, RDFS.domain)
        if domain == obs_class:
            obs_properties['domain'].append(prop)

    print("\n📋 Properties with Observation as domain:")
    for prop in sorted(set(obs_properties['domain'])):
        label = g.value(prop, RDFS.label)
        comment = g.value(prop, RDFS.comment)
        print(f"\n  • {prop.split('/')[-1]}")
        if label:
            print(f"    Label: {label}")
        if comment:
            comment_str = str(comment)[:200] + "..." if len(str(comment)) > 200 else str(comment)
            print(f"    Comment: {comment_str}")

        # Check range
        range_val = g.value(prop, RDFS.range)
        if range_val:
            print(f"    Range: {range_val.split('/')[-1] if '/' in str(range_val) else range_val.split('#')[-1]}")

        # Check schema:rangeIncludes
        for range_inc in g.objects(prop, Namespace("http://schema.org/").rangeIncludes):
            print(f"    Range includes: {range_inc.split('/')[-1]}")

if __name__ == "__main__":
    g = load_ontologies()
    analyze_structure(g)
    analyze_observation_pattern(g)
