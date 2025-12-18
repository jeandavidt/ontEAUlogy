#!/usr/bin/env python3
"""
Ontology Documentation Generator

This script parses the waterFRAME ontology file and generates
a single markdown documentation file (entities.md) containing
all entities as sections with internal anchor links.
"""

import sys
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import DC, OWL, RDF, RDFS, SKOS

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from helpers import get_ontology_path


class OntologyDocGenerator:
    """Generates documentation from ontology entities."""

    def __init__(self, ontology_path=None, output_dir=None):
        """Initialize the documentation generator.

        Args:
            ontology_path: Path to the ontology file
            output_dir: Directory to write generated documentation
        """
        self.ontology_path = ontology_path or get_ontology_path()
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "docs" / "entities"
        self.graph = Graph()
        self.namespaces = {}

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize namespace attributes with defaults
        self.ontology_base = "http://example.org/waterFRAME"
        self.ontology_namespace = f"{self.ontology_base}#"

        # Load the ontology (may override namespace if found)
        self._load_ontology()

    def _load_ontology(self):
        """Load and parse the ontology file and all imported modules."""
        if not self.ontology_path.exists():
            print(f"Warning: Ontology file not found at {self.ontology_path}")
            return

        try:
            # Load main ontology
            self.graph.parse(self.ontology_path, format="turtle")
            print(f"Loaded ontology from {self.ontology_path}")

            # Load all module files from the modules directory
            modules_dir = self.ontology_path.parent / "modules"
            if modules_dir.exists():
                for module_file in modules_dir.rglob("*.ttl"):
                    try:
                        self.graph.parse(module_file, format="turtle")
                        print(f"Loaded module from {module_file}")
                    except Exception as e:
                        print(f"Warning: Could not load module {module_file}: {e}")

            # Load all bridge files from the bridges directory
            bridges_dir = self.ontology_path.parent / "bridges"
            if bridges_dir.exists():
                for bridge_file in bridges_dir.rglob("*.ttl"):
                    try:
                        self.graph.parse(bridge_file, format="turtle")
                        print(f"Loaded bridge from {bridge_file}")
                    except Exception as e:
                        print(f"Warning: Could not load bridge {bridge_file}: {e}")

            # Extract the ontology namespace from the graph
            self._extract_ontology_namespace()
        except Exception as e:
            print(f"Error loading ontology: {e}")
            return

    def _extract_ontology_namespace(self):
        """
        Extract the ontology namespace URI from the loaded graph.

        Uses the default prefix (empty prefix) which is what entities
        actually use, rather than the ontology declaration URI which
        might be different.
        """
        # First try: use the default prefix (what entities actually use)
        for prefix, namespace in self.graph.namespaces():
            if prefix == '' or prefix is None:  # Default prefix
                self.ontology_namespace = str(namespace)
                self.ontology_base = self.ontology_namespace.rstrip('#')
                print(f"Using namespace from default prefix: {self.ontology_namespace}")
                return

        # Fallback: try to find the ontology declaration
        for ontology_uri in self.graph.subjects(RDF.type, OWL.Ontology):
            # Convert to string and ensure it doesn't end with #
            self.ontology_base = str(ontology_uri).rstrip('#')
            self.ontology_namespace = f"{self.ontology_base}#"
            print(f"Using namespace from ontology declaration: {self.ontology_namespace}")
            return

        # Last resort fallback
        self.ontology_base = "http://example.org/waterFRAME"
        self.ontology_namespace = f"{self.ontology_base}#"
        print(
            f"Warning: Could not detect ontology namespace, "
            f"using fallback: {self.ontology_namespace}"
        )

    def _get_entity_info(self, uri):
        """Extract information about a specific entity.

        Args:
            uri: The URI of the entity

        Returns:
            Dictionary containing entity information
        """
        entity_uri = URIRef(uri)
        info = {
            'uri': str(uri),
            'local_name': self._get_local_name(entity_uri),
            'labels': [],
            'descriptions': [],
            'types': [],
            'subclasses': [],
            'superclasses': [],
            'domains': [],
            'ranges': [],
            'properties': {},
            'related_entities': set()
        }

        # Get labels
        for label in self.graph.objects(entity_uri, RDFS.label):
            info['labels'].append(str(label))

        # Get alternative labels
        for alt_label in self.graph.objects(entity_uri, SKOS.altLabel):
            info['labels'].append(str(alt_label))

        # Get descriptions/comments
        for desc in self.graph.objects(entity_uri, RDFS.comment):
            info['descriptions'].append(str(desc))

        for desc in self.graph.objects(entity_uri, SKOS.definition):
            info['descriptions'].append(str(desc))

        for desc in self.graph.objects(entity_uri, DC.description):
            info['descriptions'].append(str(desc))

        # Get types
        for type_uri in self.graph.objects(entity_uri, RDF.type):
            type_name = self._get_local_name(type_uri)
            info['types'].append(type_name)

            # Handle different entity types
            if type_uri == OWL.Class:
                info = self._get_class_info(entity_uri, info)
            elif type_uri == OWL.ObjectProperty:
                info = self._get_property_info(entity_uri, info, object_property=True)
            elif type_uri == OWL.DatatypeProperty:
                info = self._get_property_info(entity_uri, info, object_property=False)
            elif type_uri == OWL.NamedIndividual:
                info = self._get_individual_info(entity_uri, info)

        # Implicit class detection: if it has rdfs:subClassOf, it's a class
        # (even if not explicitly declared with rdf:type owl:Class)
        if (entity_uri, RDFS.subClassOf, None) in self.graph:
            if 'Class' not in info['types']:
                info['types'].append('Class')
            info = self._get_class_info(entity_uri, info)

        return info

    def _get_class_info(self, entity_uri, info):
        """Get class-specific information."""
        # Get subclasses
        for subclass in self.graph.subjects(RDFS.subClassOf, entity_uri):
            subclass_name = self._get_local_name(subclass)
            info['subclasses'].append(subclass_name)
            info['related_entities'].add(str(subclass))

        # Get superclasses
        for superclass in self.graph.objects(entity_uri, RDFS.subClassOf):
            superclass_name = self._get_local_name(superclass)
            info['superclasses'].append(superclass_name)
            info['related_entities'].add(str(superclass))

        # Get individuals that are instances of this class
        for individual in self.graph.subjects(RDF.type, entity_uri):
            if individual != entity_uri:  # Avoid self-reference
                individual_name = self._get_local_name(individual)
                if 'instances' not in info:
                    info['instances'] = []
                info['instances'].append(individual_name)
                info['related_entities'].add(str(individual))

        return info

    def _get_property_info(self, entity_uri, info, object_property=True):
        """Get property-specific information."""
        # Get domains
        for domain in self.graph.objects(entity_uri, RDFS.domain):
            domain_name = self._get_local_name(domain)
            info['domains'].append(domain_name)
            info['related_entities'].add(str(domain))

        # Get ranges
        for range_obj in self.graph.objects(entity_uri, RDFS.range):
            range_name = self._get_local_name(range_obj)
            info['ranges'].append(range_name)
            info['related_entities'].add(str(range_obj))

        # Get property characteristics
        characteristics = []
        if (entity_uri, RDF.type, OWL.FunctionalProperty) in self.graph:
            characteristics.append("Functional")
        if (entity_uri, RDF.type, OWL.InverseFunctionalProperty) in self.graph:
            characteristics.append("Inverse Functional")
        if (entity_uri, RDF.type, OWL.TransitiveProperty) in self.graph:
            characteristics.append("Transitive")
        if (entity_uri, RDF.type, OWL.SymmetricProperty) in self.graph:
            characteristics.append("Symmetric")
        if (entity_uri, RDF.type, OWL.AsymmetricProperty) in self.graph:
            characteristics.append("Asymmetric")
        if (entity_uri, RDF.type, OWL.ReflexiveProperty) in self.graph:
            characteristics.append("Reflexive")
        if (entity_uri, RDF.type, OWL.IrreflexiveProperty) in self.graph:
            characteristics.append("Irreflexive")
            

        info['characteristics'] = characteristics

        # Get inverse properties
        for inverse in self.graph.objects(entity_uri, OWL.inverseOf):
            inverse_name = self._get_local_name(inverse)
            info['inverse_properties'] = info.get('inverse_properties', []) + [inverse_name]
            info['related_entities'].add(str(inverse))

        # Get subproperties
        for subproperty in self.graph.subjects(RDFS.subPropertyOf, entity_uri):
            subproperty_name = self._get_local_name(subproperty)
            info['subproperties'] = info.get('subproperties', []) + [subproperty_name]
            info['related_entities'].add(str(subproperty))

        # Get superproperties
        for superproperty in self.graph.objects(entity_uri, RDFS.subPropertyOf):
            superproperty_name = self._get_local_name(superproperty)
            info['superproperties'] = info.get('superproperties', []) + [superproperty_name]
            info['related_entities'].add(str(superproperty))

        return info

    def _get_individual_info(self, entity_uri, info):
        """Get individual-specific information."""
        # Get classes this individual is an instance of
        for class_uri in self.graph.objects(entity_uri, RDF.type):
            if class_uri != OWL.NamedIndividual:  # Avoid the type declaration itself
                class_name = self._get_local_name(class_uri)
                info['instance_of'] = info.get('instance_of', []) + [class_name]
                info['related_entities'].add(str(class_uri))

        # Get property values for this individual
        for predicate in self.graph.predicates(entity_uri, None):
            for obj in self.graph.objects(entity_uri, predicate):
                predicate_name = self._get_local_name(predicate)

                # Check if obj is a URI or a literal value
                if isinstance(obj, URIRef):
                    obj_name = self._get_local_name(obj)
                    # Only add URIRefs to related entities
                    info['related_entities'].add(str(obj))
                else:
                    # It's a literal value, use it as-is
                    obj_name = str(obj)

                if 'property_values' not in info:
                    info['property_values'] = []

                info['property_values'].append({
                    'property': predicate_name,
                    'value': obj_name,
                    'is_uri': isinstance(obj, URIRef)
                })

        return info

    def _get_local_name(self, uri):
        """Get the local name from a URI."""
        if isinstance(uri, URIRef):
            uri_str = str(uri)
            # Handle common namespaces
            if uri_str.startswith('http://www.w3.org/'):
                return uri_str.split('#')[-1] if '#' in uri_str else uri_str.split('/')[-1]
            elif '#' in uri_str:
                return uri_str.split('#')[-1]
            elif '/' in uri_str:
                return uri_str.split('/')[-1]
            else:
                return uri_str
        return str(uri)

    def _get_safe_filename(self, uri):
        """Get a safe filename from a URI."""
        local_name = self._get_local_name(uri)
        # Replace any remaining special characters that aren't safe for filenames
        safe_name = local_name.replace(':', '_').replace('#', '_').replace('/', '_')
        return safe_name

    def _get_anchor_id(self, uri):
        """Get a safe anchor ID from a URI for use in markdown links."""
        safe_name = self._get_safe_filename(uri)
        # Convert to lowercase for consistency
        return safe_name.lower()

    def _generate_entity_section(self, entity_info):
        """Generate a markdown section for a single entity.

        Returns:
            String containing the markdown content for this entity
        """
        entity_name = entity_info['local_name']
        anchor_id = self._get_anchor_id(entity_info['uri'])

        # Determine entity type for display
        entity_type = "Entity"
        if 'Class' in entity_info['types']:
            entity_type = "Class"
        elif 'ObjectProperty' in entity_info['types']:
            entity_type = "Object Property"
        elif 'DatatypeProperty' in entity_info['types']:
            entity_type = "Datatype Property"
        elif 'NamedIndividual' in entity_info['types']:
            entity_type = "Individual"

        # Generate markdown content using h2 for sections
        content = f"""## {entity_name} {{#{anchor_id}}}

**Type:** {entity_type}

**URI:** `{entity_info['uri']}`

"""

        # Add labels
        if entity_info['labels']:
            content += "### Labels\n\n"
            for label in entity_info['labels']:
                content += f"- {label}\n"
            content += "\n"

        # Add descriptions
        if entity_info['descriptions']:
            content += "### Description\n\n"
            for desc in entity_info['descriptions']:
                content += f"{desc}\n\n"

        # Add class-specific information
        if 'Class' in entity_info['types']:
            if entity_info['superclasses']:
                content += "### Superclasses\n\n"
                for superclass in entity_info['superclasses']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{superclass}"
                    )
                    content += f"- [{superclass}](#{anchor})\n"
                content += "\n"

            if entity_info['subclasses']:
                content += "### Subclasses\n\n"
                for subclass in entity_info['subclasses']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{subclass}"
                    )
                    content += f"- [{subclass}](#{anchor})\n"
                content += "\n"

            if 'instances' in entity_info and entity_info['instances']:
                content += "### Instances\n\n"
                for instance in entity_info['instances']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{instance}"
                    )
                    content += f"- [{instance}](#{anchor})\n"
                content += "\n"

        # Add property-specific information
        if 'Property' in entity_type:
            if entity_info['domains']:
                content += "### Domains\n\n"
                for domain in entity_info['domains']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{domain}"
                    )
                    content += f"- [{domain}](#{anchor})\n"
                content += "\n"

            if entity_info['ranges']:
                content += "### Ranges\n\n"
                for range_obj in entity_info['ranges']:
                    content += f"- {range_obj}\n"
                content += "\n"

            if 'characteristics' in entity_info and entity_info['characteristics']:
                content += "### Characteristics\n\n"
                for char in entity_info['characteristics']:
                    content += f"- {char}\n"
                content += "\n"

            if 'inverse_properties' in entity_info and entity_info['inverse_properties']:
                content += "### Inverse Properties\n\n"
                for inv_prop in entity_info['inverse_properties']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{inv_prop}"
                    )
                    content += f"- [{inv_prop}](#{anchor})\n"
                content += "\n"

            if 'subproperties' in entity_info and entity_info['subproperties']:
                content += "### Subproperties\n\n"
                for subprop in entity_info['subproperties']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{subprop}"
                    )
                    content += f"- [{subprop}](#{anchor})\n"
                content += "\n"

            if 'superproperties' in entity_info and entity_info['superproperties']:
                content += "### Superproperties\n\n"
                for superprop in entity_info['superproperties']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{superprop}"
                    )
                    content += f"- [{superprop}](#{anchor})\n"
                content += "\n"

        # Add individual-specific information
        if entity_type == "Individual":
            if 'instance_of' in entity_info and entity_info['instance_of']:
                content += "### Instance Of\n\n"
                for class_name in entity_info['instance_of']:
                    anchor = self._get_anchor_id(
                        f"{self.ontology_namespace}{class_name}"
                    )
                    content += f"- [{class_name}](#{anchor})\n"
                content += "\n"

            if 'property_values' in entity_info and entity_info['property_values']:
                content += "### Property Values\n\n"
                for prop_value in entity_info['property_values']:
                    prop_name = prop_value['property']
                    value = prop_value['value']
                    # Only create link if it's a URI reference to another entity
                    if prop_value.get('is_uri', False):
                        # Check if it's from our ontology namespace
                        if self.ontology_base.lower() in str(value).lower():
                            anchor = self._get_anchor_id(
                                f"{self.ontology_namespace}{value}"
                            )
                            content += f"- **{prop_name}**: [{value}](#{anchor})\n"
                        else:
                            # External URI, show as plain text
                            content += f"- **{prop_name}**: `{value}`\n"
                    else:
                        # Literal value, show as plain text
                        content += f"- **{prop_name}**: {value}\n"
                content += "\n"

        # Add related entities section (only for entities in our ontology)
        ontology_entities = [
            r for r in entity_info['related_entities']
            if self.ontology_base.lower() in r.lower()
        ]
        if ontology_entities:
            content += "### Related Entities\n\n"
            for related in sorted(ontology_entities):
                related_name = self._get_local_name(URIRef(related))
                anchor = self._get_anchor_id(related)
                content += f"- [{related_name}](#{anchor})\n"
            content += "\n"

        return content

    def _get_ontology_metadata(self):
        """Extract metadata about the ontology itself."""
        metadata = {
            'title': 'Ontology Documentation',
            'description': '',
            'version': '',
            'definition': '',
            'creator': '',
            'contributors': [],
            'license': '',
            'uri': ''
        }

        # Find the ontology declaration
        for ontology_uri in self.graph.subjects(RDF.type, OWL.Ontology):
            metadata['uri'] = str(ontology_uri)

            # Get title/label
            for label in self.graph.objects(ontology_uri, RDFS.label):
                metadata['title'] = str(label)
                break

            # Get description/comment
            for comment in self.graph.objects(ontology_uri, RDFS.comment):
                metadata['description'] = str(comment)
                break

            # Get version
            for version in self.graph.objects(ontology_uri, OWL.versionInfo):
                metadata['version'] = str(version)
                break

            # Get definition
            for definition in self.graph.objects(ontology_uri, SKOS.definition):
                metadata['definition'] = str(definition)
                break

            # Get creator
            for creator in self.graph.objects(ontology_uri, DC.creator):
                metadata['creator'] = str(creator)
                break

            # Get contributors
            for contributor in self.graph.objects(ontology_uri, DC.contributor):
                metadata['contributors'].append(str(contributor))

            # Get license
            for license_info in self.graph.objects(ontology_uri, DC.rights):
                metadata['license'] = str(license_info)
                break

            break  # Only process first ontology declaration

        return metadata

    def generate_index(self):
        """Generate the index.md file with ontology overview."""
        metadata = self._get_ontology_metadata()

        # Count entities by type
        classes = len(list(self.graph.subjects(RDF.type, OWL.Class)))
        object_properties = len(
            list(self.graph.subjects(RDF.type, OWL.ObjectProperty))
        )
        datatype_properties = len(
            list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))
        )
        individuals = len(
            list(self.graph.subjects(RDF.type, OWL.NamedIndividual))
        )

        # Generate index content
        content = f"# {metadata['title']}\n\n"

        if metadata['version']:
            content += f"**Version:** {metadata['version']}\n\n"

        if metadata['description']:
            content += f"{metadata['description']}\n\n"

        if metadata['definition']:
            content += f"## Overview\n\n{metadata['definition']}\n\n"

        content += "## Statistics\n\n"
        content += f"- **Classes:** {classes}\n"
        content += f"- **Object Properties:** {object_properties}\n"
        content += f"- **Datatype Properties:** {datatype_properties}\n"
        content += f"- **Named Individuals:** {individuals}\n"
        content += f"- **Total Entities:** {classes + object_properties + datatype_properties + individuals}\n\n"

        content += "## Navigation\n\n"
        content += "- **[Browse All Entities](entities.md)** - "
        content += "Complete documentation of all classes, properties, and individuals\n\n"

        if metadata['uri']:
            content += "## Ontology Information\n\n"
            content += f"**Ontology URI:** `{metadata['uri']}`\n\n"
            content += f"**Namespace:** `{self.ontology_namespace}`\n\n"

        if metadata['creator'] or metadata['contributors']:
            content += "## Authors\n\n"
            if metadata['creator']:
                content += f"**Creator:** {metadata['creator']}\n\n"
            if metadata['contributors']:
                content += "**Contributors:**\n\n"
                for contributor in metadata['contributors']:
                    content += f"- {contributor}\n"
                content += "\n"

        if metadata['license']:
            content += f"## License\n\n{metadata['license']}\n\n"

        # Write to index.md
        index_file = self.output_dir.parent / "index.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Generated index at {index_file}")
        return index_file

    def _get_module_info(self, module_path):
        """Extract metadata from a module file."""
        module_graph = Graph()
        try:
            module_graph.parse(module_path, format="turtle")

            # Find ontology declaration
            for ontology_uri in module_graph.subjects(RDF.type, OWL.Ontology):
                metadata = {
                    'title': None,
                    'description': None,
                    'uri': str(ontology_uri)
                }

                for label in module_graph.objects(ontology_uri, DC.title):
                    metadata['title'] = str(label)
                    break

                for comment in module_graph.objects(ontology_uri, RDFS.comment):
                    metadata['description'] = str(comment)
                    break

                return metadata
        except Exception as e:
            print(f"Warning: Could not extract metadata from {module_path}: {e}")

        return {'title': None, 'description': None, 'uri': None}

    def _is_blank_node(self, entity_uri):
        """Check if entity is a blank node or RDF/OWL internal construct."""
        # Blank nodes and internal RDF/OWL/RDFS constructs
        return (
            entity_uri.startswith('_:')
            or entity_uri.startswith('http://www.w3.org/2002/07/owl#')
            or entity_uri.startswith('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
            or entity_uri.startswith('http://www.w3.org/2000/01/rdf-schema#')
        )

    def _add_placeholder_content(self, entity_info):
        """Add placeholder content for entities without labels or descriptions."""
        if not entity_info['labels']:
            entity_info['labels'] = ['[Undefined label]']

        if not entity_info['descriptions']:
            entity_info['descriptions'] = ['Yet to be defined...']

        return entity_info

    def _categorize_entities_by_type(self, entity_uris):
        """Categorize entities by their OWL type."""
        categories = {
            'classes': [],
            'object_properties': [],
            'datatype_properties': [],
            'individuals': [],
            'other': []
        }

        for entity_uri in entity_uris:
            # Skip blank nodes and RDF/OWL internal constructs
            if self._is_blank_node(entity_uri):
                continue

            try:
                entity_info = self._get_entity_info(entity_uri)
                if not entity_info:
                    continue

                # Skip if it has no types (likely not a real entity)
                if not entity_info['types']:
                    continue

                # Add placeholder content if missing labels/descriptions
                entity_info = self._add_placeholder_content(entity_info)

                # Categorize based on types
                if 'Class' in entity_info['types']:
                    categories['classes'].append(entity_info)
                elif 'ObjectProperty' in entity_info['types']:
                    categories['object_properties'].append(entity_info)
                elif 'DatatypeProperty' in entity_info['types']:
                    categories['datatype_properties'].append(entity_info)
                elif 'NamedIndividual' in entity_info['types']:
                    categories['individuals'].append(entity_info)
                else:
                    categories['other'].append(entity_info)
            except Exception as e:
                print(f"Error categorizing {entity_uri}: {e}")

        # Sort each category alphabetically
        for category in categories.values():
            category.sort(key=lambda x: x['local_name'].lower())

        return categories

    def _generate_module_page(self, module_name, module_path, entities_by_type):
        """Generate a documentation page for a single module."""
        module_info = self._get_module_info(module_path)

        # Build page content
        title = module_info['title'] or f"Module: {module_name}"
        content = f"# {title}\n\n"

        if module_info['description']:
            content += f"{module_info['description']}\n\n"

        content += f"**Module URI:** `{module_info['uri'] or 'N/A'}`\n\n"
        content += f"**Source:** `{module_path.relative_to(self.ontology_path.parent.parent)}`\n\n"

        # Count entities
        total = sum(len(entities) for entities in entities_by_type.values())
        content += f"**Total Entities:** {total}\n\n"

        # Table of contents
        content += "## Contents\n\n"
        if entities_by_type['classes']:
            content += f"- [Classes](#classes) ({len(entities_by_type['classes'])})\n"
        if entities_by_type['object_properties']:
            obj_props_count = len(entities_by_type['object_properties'])
            content += (
                f"- [Object Properties](#object-properties) ({obj_props_count})\n"
            )
        if entities_by_type['datatype_properties']:
            dt_props_count = len(entities_by_type['datatype_properties'])
            content += (
                f"- [Datatype Properties](#datatype-properties) ({dt_props_count})\n"
            )
        if entities_by_type['individuals']:
            ind_count = len(entities_by_type['individuals'])
            content += f"- [Individuals](#individuals) ({ind_count})\n"
        content += "\n---\n\n"

        # Generate sections for each type
        if entities_by_type['classes']:
            content += "## Classes\n\n"
            for entity_info in entities_by_type['classes']:
                content += self._generate_entity_section(entity_info)
                content += "\n---\n\n"

        if entities_by_type['object_properties']:
            content += "## Object Properties\n\n"
            for entity_info in entities_by_type['object_properties']:
                content += self._generate_entity_section(entity_info)
                content += "\n---\n\n"

        if entities_by_type['datatype_properties']:
            content += "## Datatype Properties\n\n"
            for entity_info in entities_by_type['datatype_properties']:
                content += self._generate_entity_section(entity_info)
                content += "\n---\n\n"

        if entities_by_type['individuals']:
            content += "## Individuals\n\n"
            for entity_info in entities_by_type['individuals']:
                content += self._generate_entity_section(entity_info)
                content += "\n---\n\n"

        return content

    def generate_modular_docs(self):
        """Generate documentation organized by module structure."""
        if not self.graph:
            print("No ontology loaded. Cannot generate documentation.")
            return []

        # Create modules directory in docs
        modules_doc_dir = self.output_dir.parent / "modules"
        modules_doc_dir.mkdir(parents=True, exist_ok=True)

        # Get the ontology directory structure
        ontology_dir = self.ontology_path.parent
        modules_dir = ontology_dir / "modules"
        bridges_dir = ontology_dir / "bridges"

        generated_files = []

        # Process modules directory
        if modules_dir.exists():
            for module_file in sorted(modules_dir.rglob("*.ttl")):
                # Get relative path from modules directory
                rel_path = module_file.relative_to(modules_dir)
                module_name = rel_path.stem

                # Parse the module to find its entities
                module_graph = Graph()
                try:
                    module_graph.parse(module_file, format="turtle")
                except Exception as e:
                    print(f"Warning: Could not parse {module_file}: {e}")
                    continue

                # Collect entities from this module
                # Look for all classes, properties, and individuals defined here
                entity_uris = set()

                # Get all classes
                for class_uri in module_graph.subjects(RDF.type, OWL.Class):
                    if self.ontology_base.lower() in str(class_uri).lower():
                        entity_uris.add(str(class_uri))

                # Also get classes defined via rdfs:subClassOf
                for class_uri in module_graph.subjects(RDFS.subClassOf, None):
                    if self.ontology_base.lower() in str(class_uri).lower():
                        entity_uris.add(str(class_uri))

                # Get all properties
                for prop_uri in module_graph.subjects(RDF.type, OWL.ObjectProperty):
                    if self.ontology_base.lower() in str(prop_uri).lower():
                        entity_uris.add(str(prop_uri))

                for prop_uri in module_graph.subjects(RDF.type, OWL.DatatypeProperty):
                    if self.ontology_base.lower() in str(prop_uri).lower():
                        entity_uris.add(str(prop_uri))

                # Get all individuals
                for ind_uri in module_graph.subjects(RDF.type, OWL.NamedIndividual):
                    if self.ontology_base.lower() in str(ind_uri).lower():
                        entity_uris.add(str(ind_uri))

                # Categorize entities
                entities_by_type = self._categorize_entities_by_type(entity_uris)

                # Generate page content
                content = self._generate_module_page(
                    module_name, module_file, entities_by_type
                )

                # Create output directory structure
                output_subdir = modules_doc_dir / rel_path.parent
                output_subdir.mkdir(parents=True, exist_ok=True)

                # Write file
                output_file = output_subdir / f"{module_name}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"Generated module page: {output_file}")
                generated_files.append(output_file)

        # Process bridges directory
        if bridges_dir.exists():
            bridges_doc_dir = self.output_dir.parent / "bridges"
            bridges_doc_dir.mkdir(parents=True, exist_ok=True)

            for bridge_file in sorted(bridges_dir.rglob("*.ttl")):
                rel_path = bridge_file.relative_to(bridges_dir)
                bridge_name = rel_path.stem

                # Parse the bridge file
                bridge_graph = Graph()
                try:
                    bridge_graph.parse(bridge_file, format="turtle")
                except Exception as e:
                    print(f"Warning: Could not parse {bridge_file}: {e}")
                    continue

                # Collect entities from this bridge
                # Look for all classes, properties, and individuals defined here
                entity_uris = set()

                # Get all classes
                for class_uri in bridge_graph.subjects(RDF.type, OWL.Class):
                    if self.ontology_base.lower() in str(class_uri).lower():
                        entity_uris.add(str(class_uri))

                # Also get classes defined via rdfs:subClassOf
                for class_uri in bridge_graph.subjects(RDFS.subClassOf, None):
                    if self.ontology_base.lower() in str(class_uri).lower():
                        entity_uris.add(str(class_uri))

                # Get all properties
                for prop_uri in bridge_graph.subjects(RDF.type, OWL.ObjectProperty):
                    if self.ontology_base.lower() in str(prop_uri).lower():
                        entity_uris.add(str(prop_uri))

                for prop_uri in bridge_graph.subjects(RDF.type, OWL.DatatypeProperty):
                    if self.ontology_base.lower() in str(prop_uri).lower():
                        entity_uris.add(str(prop_uri))

                # Get all individuals
                for ind_uri in bridge_graph.subjects(RDF.type, OWL.NamedIndividual):
                    if self.ontology_base.lower() in str(ind_uri).lower():
                        entity_uris.add(str(ind_uri))

                # Categorize entities
                entities_by_type = self._categorize_entities_by_type(entity_uris)

                # Generate page content
                content = self._generate_module_page(
                    bridge_name, bridge_file, entities_by_type
                )

                # Write file
                output_file = bridges_doc_dir / f"{bridge_name}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"Generated bridge page: {output_file}")
                generated_files.append(output_file)

        return generated_files

def main():
    """Main function to run the documentation generator."""
    generator = OntologyDocGenerator()

    # Generate index page
    index_file = generator.generate_index()

    # Generate modular documentation
    module_files = generator.generate_modular_docs()

    if module_files:
        print("\nSuccessfully generated documentation:")
        print(f"  - Index: {index_file}")
        print(f"  - Module pages: {len(module_files)}")
        for file in module_files:
            print(f"    - {file}")

if __name__ == "__main__":
    main()
