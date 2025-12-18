# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "networkx==3.5",
#     "numpy==2.3.4",
#     "rdflib==7.4.0",
#     "marimo",
#     "anywidget",
#     "traitlets",
# ]
# ///

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import rdflib
    from pathlib import Path
    from rdflib import Graph, URIRef
    from rdflib.namespace import DC, OWL, RDF, RDFS, SKOS
    import networkx as nx
    import json
    import anywidget
    return OWL, Path, RDF, RDFS, anywidget, json, mo, nx, rdflib


@app.cell
def _(mo):
    import sys
    import argparse

    # Parse command-line arguments in script mode
    if mo.app_meta().mode == "script":
        parser = argparse.ArgumentParser(description="Explore RDF ontology")
        parser.add_argument(
            "--ontology",
            "-o",
            default="data/ontology/waterframe.ttl",
            help="Path or URI to the ontology file (default: data/ontology/waterframe.ttl)"
        )
        args = parser.parse_args()
        _initial_value = args.ontology
    else:
        _initial_value = "data/ontology/waterframe.ttl"

    # Input for ontology file path or URI
    ontology_input = mo.ui.text(
        label="Ontology Path or URI",
        full_width=True,
        value=_initial_value,
        placeholder="Enter file path or URI (e.g., data/ontology/waterframe.ttl or http://example.org/ontology.ttl)"
    )
    ontology_input
    return (ontology_input,)


@app.cell
def _(Path, mo, ontology_input, rdflib):
    import urllib.request
    import urllib.error

    graph = rdflib.Graph()

    def _load_from_uri(_uri):
        """Helper to load content from URI"""
        with urllib.request.urlopen(_uri) as response:
            return response.read().decode('utf-8')

    def _try_load_module_from_uri(_base_uri, _module_path):
        """Try to construct and load a module URI"""
        # Remove the filename from base URI to get directory
        _dir_uri = _base_uri.rsplit('/', 1)[0]
        # Construct module URI
        _module_uri = f"{_dir_uri}/{_module_path}"
        try:
            _content = _load_from_uri(_module_uri)
            graph.parse(data=_content, format="turtle")
            return True, _module_uri
        except Exception:
            return False, _module_uri

    _input_value = ontology_input.value.strip()
    _out = []
    if _input_value:
        # Check if it's a URI or file path
        if _input_value.startswith(('http://', 'https://')):
            # Load from URI
            try:
                # Fetch and parse main ontology
                _content = _load_from_uri(_input_value)
                graph.parse(data=_content, format="turtle")
                _out.append(mo.md(f"✓ Loaded main ontology from URI: `{_input_value}`"))

                # Try to load common module paths
                _module_paths = [
                    "modules/core/material_entities.ttl",
                    "modules/core/properties.ttl",
                    "modules/core/qualities.ttl",
                    "modules/core/processes.ttl",
                    "modules/core/roles.ttl",
                    "modules/core/information.ttl",
                ]

                _loaded_modules = []
                _failed_modules = []

                for _module_path in _module_paths:
                    _success, _module_uri = _try_load_module_from_uri(_input_value, _module_path)
                    if _success:
                        _loaded_modules.append(_module_path)
                    else:
                        _failed_modules.append(_module_path)

                if _loaded_modules:
                    _out.append(mo.md(f"✓ Loaded {len(_loaded_modules)} module(s): {', '.join([p.split('/')[-1] for p in _loaded_modules])}"))

                # Try to load bridge modules
                _bridge_paths = [
                    "bridges/sosa_alignment.ttl",
                    "bridges/prov_alignment.ttl",
                    "bridges/qudt_alignment.ttl",
                ]

                _loaded_bridges = []
                for _bridge_path in _bridge_paths:
                    _success, _bridge_uri = _try_load_module_from_uri(_input_value, _bridge_path)
                    if _success:
                        _loaded_bridges.append(_bridge_path)

                if _loaded_bridges:
                    _out.append(mo.md(f"✓ Loaded {len(_loaded_bridges)} bridge(s): {', '.join([p.split('/')[-1] for p in _loaded_bridges])}"))

                _total_triples = len(graph)
                _out.append(mo.md(f"**Total triples loaded:** {_total_triples}"))

            except Exception as e:
                _out.append(mo.md(f"❌ Error loading from URI: {e}"))
        else:
            # Load from file path
            _ontology_path = Path(_input_value)
            if _ontology_path.exists():
                try:
                    # Load main ontology file
                    graph.parse(_ontology_path, format="turtle")
                    _out.append(mo.md(f"✓ Loaded main ontology: `{_ontology_path}`"))

                    # Load all module files from modules/ directory
                    _modules_dir = _ontology_path.parent / "modules"
                    _module_count = 0
                    if _modules_dir.exists():
                        for _module_file in _modules_dir.rglob("*.ttl"):
                            try:
                                graph.parse(_module_file, format="turtle")
                                _module_count += 1
                            except Exception as e:
                                _out.append(mo.md(f"⚠ Warning: Could not load module `{_module_file.name}`: {e}"))

                        if _module_count > 0:
                            _out.append(mo.md(f"✓ Loaded {_module_count} module(s) from `{_modules_dir.relative_to(_ontology_path.parent.parent)}`"))

                    # Load all bridge files from bridges/ directory
                    _bridges_dir = _ontology_path.parent / "bridges"
                    _bridge_count = 0
                    if _bridges_dir.exists():
                        for _bridge_file in _bridges_dir.rglob("*.ttl"):
                            try:
                                graph.parse(_bridge_file, format="turtle")
                                _bridge_count += 1
                            except Exception as e:
                                _out.append(mo.md(f"⚠ Warning: Could not load bridge `{_bridge_file.name}`: {e}"))

                        if _bridge_count > 0:
                            _out.append(mo.md(f"✓ Loaded {_bridge_count} bridge(s) from `{_bridges_dir.relative_to(_ontology_path.parent.parent)}`"))

                    _total_triples = len(graph)
                    _out.append(mo.md(f"**Total triples loaded:** {_total_triples}"))

                except Exception as e:
                    _out.append(mo.md(f"❌ Error loading ontology: {e}"))
            else:
                _out.append(mo.md(f"❌ File not found: `{_ontology_path}`"))
    else:
        _out.append(mo.md("⚠ Please enter an ontology path or URI"))
    mo.vstack(_out)
    return (graph,)


@app.cell
def _(OWL, RDF, RDFS, graph, nx, rdflib):
    # Convert RDF graph to NetworkX with type information
    def rdf_to_networkx(rdf_graph, skip_blank_nodes=True):
        G = nx.DiGraph()

        # Define meta-level URIs (ontology vocabulary)
        meta_level_uris = {
            # OWL terms
            str(OWL.Class), str(RDFS.Class),
            str(OWL.ObjectProperty), str(OWL.DatatypeProperty),
            str(OWL.NamedIndividual), str(OWL.Ontology),
            str(OWL.FunctionalProperty), str(OWL.InverseFunctionalProperty),
            str(OWL.TransitiveProperty), str(OWL.SymmetricProperty),
            # RDF and RDFS terms
            str(RDF.Property), str(RDFS.Resource),
            str(RDF.Statement), str(RDF.List), str(RDF.Seq),
            str(RDF.Bag), str(RDF.Alt),
            str(RDFS.Literal), str(RDFS.Container),
        }

        # Also check by namespace prefix for any RDF/RDFS/OWL/W3C vocabulary
        meta_namespaces = [
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'http://www.w3.org/2000/01/rdf-schema#',
            'http://www.w3.org/2002/07/owl#',
            'http://www.w3.org/ns/r2rml#',
            'http://www.w3.org/TR/',  # W3C Technical Reports
            'https://www.w3.org/TR/',
        ]

        # First pass: identify node types and blank nodes
        node_types = {}
        ontology_nodes = set()
        blank_nodes = set()

        # Identify blank nodes
        for s, p, o in rdf_graph:
            if isinstance(s, rdflib.BNode):
                blank_nodes.add(str(s))
            if isinstance(o, rdflib.BNode):
                blank_nodes.add(str(o))

        for s, p, o in rdf_graph:
            s_uri = str(s)
            o_uri = str(o)
            p_uri = str(p)

            # Check if it's an ontology declaration
            if p_uri == str(RDF.type) and str(o) == str(OWL.Ontology):
                ontology_nodes.add(s_uri)
                node_types[s_uri] = 'ontology'

            # Check if it's referenced as an import (owl:imports)
            # This catches external ontologies that aren't loaded but are referenced
            if p_uri == str(OWL.imports):
                # The object of owl:imports is an ontology URI
                if o_uri not in node_types:
                    node_types[o_uri] = 'ontology'
                    ontology_nodes.add(o_uri)

            # Check if subject or object is a meta-level term
            if s_uri in meta_level_uris:
                node_types[s_uri] = 'meta'
            if o_uri in meta_level_uris:
                node_types[o_uri] = 'meta'

            # Check if it's in a meta namespace (RDF/RDFS/OWL vocabulary)
            for _meta_ns in meta_namespaces:
                if s_uri.startswith(_meta_ns):
                    node_types[s_uri] = 'meta'
                if o_uri.startswith(_meta_ns):
                    node_types[o_uri] = 'meta'

            # Check for XSD datatypes (primitive types)
            if s_uri.startswith('http://www.w3.org/2001/XMLSchema#'):
                node_types[s_uri] = 'datatype'
            if o_uri.startswith('http://www.w3.org/2001/XMLSchema#'):
                node_types[o_uri] = 'datatype'

            # Check for RDF datatypes (like rdf:JSON, rdf:HTML, etc.)
            if '#' in s_uri and s_uri.split('#')[0] in [
                ns.rstrip('#') for ns in meta_namespaces
            ]:
                _fragment = s_uri.split('#')[1].lower()
                if any(
                    dt in _fragment
                    for dt in ['json', 'html', 'xml', 'plainliteral', 'langstring']
                ):
                    node_types[s_uri] = 'datatype'
            if '#' in o_uri and o_uri.split('#')[0] in [
                ns.rstrip('#') for ns in meta_namespaces
            ]:
                _fragment = o_uri.split('#')[1].lower()
                if any(
                    dt in _fragment
                    for dt in ['json', 'html', 'xml', 'plainliteral', 'langstring']
                ):
                    node_types[o_uri] = 'datatype'

            # Check if subject is a class, property, or individual
            if p_uri == str(RDF.type):
                if str(o) == str(OWL.Class) or str(o) == str(RDFS.Class):
                    node_types[s_uri] = 'class'
                elif str(o) == str(OWL.ObjectProperty):
                    node_types[s_uri] = 'object_property'
                elif str(o) == str(OWL.DatatypeProperty):
                    node_types[s_uri] = 'datatype_property'
                elif str(o) == str(OWL.NamedIndividual):
                    node_types[s_uri] = 'individual'

            # Classes can also be defined via rdfs:subClassOf without explicit rdf:type
            if p_uri == str(RDFS.subClassOf):
                # Subject of subClassOf is a class
                if s_uri not in node_types or node_types[s_uri] == 'unknown':
                    node_types[s_uri] = 'class'
                # Object of subClassOf is also a class (superclass)
                if o_uri not in node_types or node_types[o_uri] == 'unknown':
                    # Don't override if it's already marked as meta or other specific type
                    if not any(o_uri.startswith(ns) for ns in meta_namespaces):
                        node_types[o_uri] = 'class'

        # Second pass: build graph
        for s, p, o in rdf_graph:
            s_uri = str(s)
            p_uri = str(p)
            o_uri = str(o)

            # Skip blank nodes if requested
            if skip_blank_nodes:
                if s_uri in blank_nodes or o_uri in blank_nodes:
                    continue

            s_label = s_uri.split('/')[-1].split('#')[-1]
            p_label = p_uri.split('/')[-1].split('#')[-1]
            o_label = o_uri.split('/')[-1].split('#')[-1]

            # Determine node types
            if s_uri in blank_nodes:
                s_type = 'blank'
            else:
                s_type = node_types.get(s_uri, 'unknown')

            # For objects, check if it's a literal (doesn't start with http)
            if o_uri.startswith('http') or o_uri.startswith('_:'):
                if o_uri in blank_nodes:
                    o_type = 'blank'
                else:
                    o_type = node_types.get(o_uri, 'unknown')
            else:
                o_type = 'literal'

            # Add nodes with type information
            if s_uri not in G.nodes:
                G.add_node(
                    s_uri,
                    label=s_label,
                    uri=s_uri,
                    node_type=s_type,
                    is_blank=s_uri in blank_nodes,
                )
            if o_uri not in G.nodes:
                G.add_node(
                    o_uri,
                    label=o_label,
                    uri=o_uri,
                    node_type=o_type,
                    is_blank=o_uri in blank_nodes,
                )

            # Add edge with predicate info
            G.add_edge(s_uri, o_uri, predicate=p_label, predicate_uri=p_uri)

        return G

    # Always include blank nodes in the graph structure
    # The UI filter will control visibility
    nx_graph = rdf_to_networkx(graph, skip_blank_nodes=False)
    return (nx_graph,)


@app.cell
def _(OWL, graph, mo, nx_graph):
    # Extract namespaces/modules from the graph
    def _extract_namespaces(rdf_graph, nx_g):
        """Extract unique namespaces from the graph with node counts"""
        namespace_info = {}

        # Get all unique namespaces from nodes
        for node_uri, node_data in nx_g.nodes(data=True):
            if node_uri.startswith('http'):
                # Extract namespace (everything before the last # or /)
                if '#' in node_uri:
                    namespace = node_uri.rsplit('#', 1)[0] + '#'
                elif '/' in node_uri:
                    # For slash-based URIs, take up to the last segment
                    parts = node_uri.rsplit('/', 1)
                    namespace = parts[0] + '/'
                else:
                    namespace = node_uri

                node_type = node_data.get('node_type', 'unknown')

                if namespace not in namespace_info:
                    namespace_info[namespace] = {
                        'count': 0,
                        'types': set(),
                        'label': namespace
                    }

                namespace_info[namespace]['count'] += 1
                namespace_info[namespace]['types'].add(node_type)

        # Try to get prettier labels from ontology declarations
        for ns_uri, ns_data in namespace_info.items():
            # Check if this namespace has an ontology declaration
            ontology_uri = ns_uri.rstrip('#/')
            for ont_uri in rdf_graph.subjects(predicate=None, object=OWL.Ontology):
                if str(ont_uri).startswith(ontology_uri):
                    # Try to get a label
                    for label in rdf_graph.objects(ont_uri, None):
                        label_str = str(label)
                        if len(label_str) < 100 and not label_str.startswith('http'):
                            ns_data['label'] = label_str
                            break

        # Sort by count (descending)
        sorted_ns = sorted(namespace_info.items(), key=lambda x: x[1]['count'], reverse=True)

        return sorted_ns

    _namespaces = _extract_namespaces(graph, nx_graph)

    # Format namespace options for dropdown
    _namespace_options = [("All namespaces", None)]

    for ns_uri, ns_data in _namespaces:
        # Determine indentation based on nesting
        _indent = ""
        _short_name = ns_uri

        # Shorten common long URIs
        if "www.w3.org" in ns_uri:
            # Extract the spec name (e.g., "owl", "rdf", "rdfs")
            if '#' in ns_uri:
                _short_name = ns_uri.rstrip('#').split('/')[-1]
            else:
                _short_name = ns_uri.rstrip('/').split('/')[-1]
            _indent = "  "  # Indent meta namespaces
        elif "purl.obolibrary.org" in ns_uri:
            # Extract ontology name (e.g., "BFO")
            if '/obo/' in ns_uri:
                _parts = ns_uri.split('/obo/')
                if len(_parts) > 1:
                    _short_name = _parts[1].rstrip('#/').split('/')[0]
                else:
                    _short_name = "OBO"
            else:
                _short_name = "OBO"
            _indent = "  "
        elif "github.com" in ns_uri or "ugentbiomath" in ns_uri or "waterframe" in ns_uri.lower():
            # Project namespaces - extract meaningful part
            if '/modules/core/' in ns_uri:
                # Extract module name
                _module = ns_uri.split('/modules/core/')[-1].rstrip('#/')
                _short_name = f"core/{_module}"
                _indent = "    "  # Double indent for nested modules
            elif '/modules/' in ns_uri:
                _module = ns_uri.split('/modules/')[-1].rstrip('#/')
                _short_name = f"modules/{_module}"
                _indent = "  "
            elif 'waterframe#' in ns_uri or ns_uri.endswith('waterframe/'):
                _short_name = "waterFRAME (main)"
            else:
                # Try to get the last meaningful segment
                _short_name = ns_uri.rstrip('#/').split('/')[-1]
        else:
            # For other namespaces, extract the last segment
            _short_name = ns_uri.rstrip('#/').split('/')[-1]
            if not _short_name:
                _short_name = ns_uri.rstrip('#/').split('/')[-2] if len(ns_uri.rstrip('#/').split('/')) > 1 else ns_uri

        _label = f"{_indent}{_short_name} ({ns_data['count']})"
        _namespace_options.append((_label, ns_uri))

    namespace_filter = mo.ui.dropdown(
        options=_namespace_options,
        value=None,
        label="Filter by Namespace/Module"
    )
    return (namespace_filter,)


@app.cell
def _(mo, namespace_filter):
    # Filter controls
    show_blank_nodes = mo.ui.checkbox(label="Show Blank Nodes", value=False)
    show_meta = mo.ui.checkbox(label="Show Meta-level Terms", value=True)
    show_datatypes = mo.ui.checkbox(label="Show Datatypes (XSD)", value=True)
    show_literals = mo.ui.checkbox(label="Show Literals", value=True)

    # Layout selection - use list so value is the actual layout name
    layout_options = mo.ui.dropdown(
        options=["fcose", "cose", "cola", "breadthfirst", "circle", "concentric", "grid"],
        value="fcose",
        label="Layout Algorithm"
    )

    # Refresh button - forces re-render and fits to view
    refresh_button = mo.ui.button(
        value=0,
        on_click=lambda value: value + 1,
        label="🔄 Refresh & Fit to View"
    )

    mo.vstack([
        mo.md("**Filter Options:**"),
        namespace_filter,
        mo.hstack([show_blank_nodes, show_meta, show_datatypes, show_literals]),
        layout_options,
        refresh_button
    ])
    return (
        layout_options,
        refresh_button,
        show_blank_nodes,
        show_datatypes,
        show_literals,
        show_meta,
    )


@app.cell
def _(
    anywidget,
    json,
    layout_options,
    mo,
    namespace_filter,
    nx_graph,
    refresh_button,
    show_blank_nodes,
    show_datatypes,
    show_literals,
    show_meta,
):


    # Convert NetworkX graph to Cytoscape format
    def nx_to_cytoscape(G, filters):
        """Convert NetworkX graph to Cytoscape.js format with filters"""
        elements = []

        # Node type filters
        skip_types = set()
        if not filters['show_blank']:
            skip_types.add('blank')
        if not filters['show_meta']:
            skip_types.add('meta')
        if not filters['show_datatypes']:
            skip_types.add('datatype')
        if not filters['show_literals']:
            skip_types.add('literal')

        # Namespace filter
        selected_namespace = filters.get('namespace', None)

        # Add nodes
        for node_id, node_data in G.nodes(data=True):
            node_type = node_data.get('node_type', 'unknown')

            # Skip filtered types
            if node_type in skip_types:
                continue

            # Skip if namespace filter is active and node doesn't match
            if selected_namespace is not None:
                if not node_id.startswith(selected_namespace):
                    continue

            elements.append({
                'data': {
                    'id': node_id,
                    'label': node_data.get('label', node_id),
                    'type': node_type,
                    'uri': node_data.get('uri', node_id),
                }
            })

        # Get visible node IDs
        visible_nodes = {el['data']['id'] for el in elements}

        # Add edges (only if both nodes are visible)
        for source, target, edge_data in G.edges(data=True):
            if source in visible_nodes and target in visible_nodes:
                elements.append({
                    'data': {
                        'id': f"{source}-{target}",
                        'source': source,
                        'target': target,
                        'label': edge_data.get('predicate', ''),
                        'predicate': edge_data.get('predicate', ''),
                    }
                })

        return elements

    # Prepare filters from current UI values
    # Handle namespace filter value - could be None, a string, or a tuple
    _ns_value = namespace_filter.value
    if isinstance(_ns_value, tuple):
        # If it's a tuple, extract the second element (the actual value)
        _ns_filter = _ns_value[1] if len(_ns_value) > 1 else None
    else:
        _ns_filter = _ns_value

    _filters = {
        'show_blank': show_blank_nodes.value,
        'show_meta': show_meta.value,
        'show_datatypes': show_datatypes.value,
        'show_literals': show_literals.value,
        'namespace': _ns_filter,  # None means "All namespaces", otherwise it's a URI string
    }

    # Get elements with current filters
    _cyto_elements = nx_to_cytoscape(nx_graph, _filters)

    # Get the selected layout from the dropdown
    _selected_layout = layout_options.value

    # Note: refresh_button is included as a dependency (even though not accessed directly)
    # so clicking it re-runs this cell, recreating the widget with a fresh layout
    _ = refresh_button.value  # Acknowledge dependency

    # Create the widget HTML directly with JavaScript
    _esm_code = f"""
    async function render({{ model, el }}) {{
        try {{
            // Import Cytoscape and extensions from CDN
            const cytoscapeModule = await import('https://cdn.jsdelivr.net/npm/cytoscape@3.28.1/+esm');
            const cytoscape = cytoscapeModule.default;

        // Import layout extensions
        try {{
            const fcoseModule = await import('https://cdn.jsdelivr.net/npm/cytoscape-fcose@2.2.0/+esm');
            cytoscape.use(fcoseModule.default);
        }} catch (e) {{
            console.error('fcose layout not available:', e);
        }}

        try {{
            const colaModule = await import('https://cdn.jsdelivr.net/npm/cytoscape-cola@2.5.1/+esm');
            cytoscape.use(colaModule.default);
        }} catch (e) {{
            console.error('cola layout not available:', e);
        }}

        // Create container
        const container = document.createElement('div');
        container.style.cssText = 'position: relative; width: 100%; height: 750px;';

        const cyDiv = document.createElement('div');
        cyDiv.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 1px solid #ccc; background: #fafafa;';
        container.appendChild(cyDiv);

        const infoDiv = document.createElement('div');
        infoDiv.style.cssText = 'position: absolute; top: 10px; left: 10px; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-width: 300px; font-family: Arial, sans-serif; font-size: 12px; display: none;';
        container.appendChild(infoDiv);

        el.appendChild(container);

        // Color scheme for different node types
        const nodeColors = {{
            'ontology': '#8e44ad',
            'meta': '#34495e',
            'datatype': '#16a085',
            'class': '#3498db',
            'object_property': '#2ecc71',
            'datatype_property': '#f39c12',
            'individual': '#9b59b6',
            'literal': '#95a5a6',
            'blank': '#ff6b6b',
            'unknown': '#e74c3c'
        }};

        const nodeSizes = {{
            'ontology': 60,
            'meta': 45,
            'datatype': 35,
            'class': 50,
            'object_property': 40,
            'datatype_property': 40,
            'individual': 30,
            'literal': 25,
            'blank': 25,
            'unknown': 30
        }};

        const nodeShapes = {{
            'ontology': 'star',
            'meta': 'diamond',
            'datatype': 'hexagon',
            'class': 'ellipse',
            'object_property': 'round-diamond',
            'datatype_property': 'round-rectangle',
            'individual': 'round-octagon',
            'literal': 'round-tag',
            'blank': 'triangle',
            'unknown': 'vee'
        }};

        // Get layout and elements from Python
        const layoutName = '{_selected_layout}';
        const elements = {json.dumps(_cyto_elements)};

        console.log('DEBUG: JavaScript using layout =', layoutName);
        console.log('DEBUG: Elements count =', elements.length);

        const layoutConfig = {{
            name: layoutName,
            animate: true,
            animationDuration: 500,
            nodeDimensionsIncludeLabels: true,
        }};

        // Add layout-specific parameters
        if (layoutName === 'fcose' || layoutName === 'cose') {{
            Object.assign(layoutConfig, {{
                idealEdgeLength: 100,
                nodeRepulsion: 8000,
                edgeElasticity: 0.45,
                nestingFactor: 0.1,
                gravity: 0.25,
                numIter: 2500,
                tile: true,
                randomize: false
            }});
        }} else if (layoutName === 'cola') {{
            Object.assign(layoutConfig, {{
                edgeLength: 100,
                nodeSpacing: 50,
                animate: true,
                randomize: false,
                maxSimulationTime: 2000
            }});
        }}

        // Initialize Cytoscape with the layout from Python
        const cy = cytoscape({{
            container: cyDiv,
            elements: elements,
            layout: layoutConfig,
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'background-color': function(ele) {{
                            return nodeColors[ele.data('type')] || '#95a5a6';
                        }},
                        'label': 'data(label)',
                        'width': function(ele) {{
                            return nodeSizes[ele.data('type')] || 30;
                        }},
                        'height': function(ele) {{
                            return nodeSizes[ele.data('type')] || 30;
                        }},
                        'shape': function(ele) {{
                            return nodeShapes[ele.data('type')] || 'ellipse';
                        }},
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '10px',
                        'color': '#333',
                        'text-outline-color': '#fff',
                        'text-outline-width': 2,
                        'border-width': 2,
                        'border-color': function(ele) {{
                            const color = nodeColors[ele.data('type')] || '#95a5a6';
                            return color;
                        }},
                        'border-opacity': 0.7
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 2,
                        'line-color': '#999',
                        'target-arrow-color': '#999',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(predicate)',
                        'font-size': '8px',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -10,
                        'color': '#666',
                        'text-background-color': '#fff',
                        'text-background-opacity': 0.8,
                        'text-background-padding': '2px'
                    }}
                }},
                {{
                    selector: 'node:selected',
                    style: {{
                        'border-width': 4,
                        'border-color': '#000',
                        'background-color': function(ele) {{
                            const color = nodeColors[ele.data('type')] || '#95a5a6';
                            return color;
                        }}
                    }}
                }},
                {{
                    selector: 'edge:selected',
                    style: {{
                        'width': 4,
                        'line-color': '#000',
                        'target-arrow-color': '#000'
                    }}
                }},
                {{
                    selector: '.highlighted',
                    style: {{
                        'background-color': '#FFD700',
                        'line-color': '#FFD700',
                        'target-arrow-color': '#FFD700',
                        'transition-property': 'background-color, line-color, target-arrow-color',
                        'transition-duration': '0.5s'
                    }}
                }}
            ]
        }});

        // Node interaction
        cy.on('tap', 'node', function(evt) {{
            const node = evt.target;
            const data = node.data();

            const edges = node.connectedEdges();
            const incoming = edges.filter(e => e.target().id() === node.id());
            const outgoing = edges.filter(e => e.source().id() === node.id());

            let infoHTML = '<h3 style="margin: 0 0 10px 0;">' + data.label + '</h3>';
            infoHTML += '<div><strong>Type:</strong> ' + data.type + '</div>';
            infoHTML += '<div><strong>URI:</strong><br/><small>' + data.uri.substring(0, 60);
            if (data.uri.length > 60) infoHTML += '...';
            infoHTML += '</small></div>';
            infoHTML += '<div style="margin-top: 5px;"><strong>Incoming:</strong> ' + incoming.length + '</div>';
            infoHTML += '<div><strong>Outgoing:</strong> ' + outgoing.length + '</div>';

            infoDiv.innerHTML = infoHTML;
            infoDiv.style.display = 'block';

            cy.elements().removeClass('highlighted');
            node.addClass('highlighted');
            node.neighborhood().addClass('highlighted');
        }});

        cy.on('tap', function(evt) {{
            if (evt.target === cy) {{
                infoDiv.style.display = 'none';
                cy.elements().removeClass('highlighted');
            }}
        }});

        cy.on('dbltap', 'node', function(evt) {{
            const node = evt.target;
            cy.animate({{
                fit: {{
                    eles: node.neighborhood(),
                    padding: 50
                }},
                duration: 500
            }});
        }});
        }} catch (error) {{
            console.error('ERROR in Cytoscape widget:', error);
            el.innerHTML = '<div style="color: red; padding: 20px; font-family: monospace;">Error rendering graph:<br>' + error.message + '<br><br>Check console for details.</div>';
        }}
    }}
    export default {{ render }};
    """

    # Create simple widget class with the JavaScript code
    class CytoscapeWidget(anywidget.AnyWidget):
        _esm = _esm_code

    cyto_widget = CytoscapeWidget()
    graph_viz = mo.ui.anywidget(cyto_widget)

    # Create legend
    _legend_md = """
    ### Legend

    | Shape | Color | Type |
    |-------|-------|------|
    | ⭐ | Purple | Ontology |
    | ◆ | Dark Gray | Meta (OWL/RDFS/RDF) |
    | ⬡ | Teal | Datatype (XSD) |
    | ⚪ | Blue | Class |
    | ◇ | Green | Object Property |
    | ▭ | Orange | Datatype Property |
    | ⬢ | Light Purple | Individual |
    | ▼ | Light Gray | Literal |
    | ▲ | Red | Blank Node |
    | ▽ | Dark Red | Unknown |
    """

    mo.vstack([
        mo.md(f"**Showing {len(_cyto_elements)} elements** (Layout: {_selected_layout})"),
        graph_viz,
        mo.md(_legend_md)
    ])
    return


@app.cell
def _(mo, nx, nx_graph):
    # Graph statistics
    _stats = f"""
    ## Graph Statistics

    - **Nodes**: {nx_graph.number_of_nodes()}
    - **Edges**: {nx_graph.number_of_edges()}
    - **Density**: {nx.density(nx_graph):.4f}

    ### Node Types Distribution
    """

    _node_types = {}
    for _, node_data in nx_graph.nodes(data=True):
        _type = node_data.get('node_type', 'unknown')
        _node_types[_type] = _node_types.get(_type, 0) + 1

    for _type, _count in sorted(_node_types.items(), key=lambda x: -x[1]):
        _stats += f"\n- **{_type}**: {_count}"

    mo.md(_stats)
    return


@app.cell
def _(graph, mo, nx_graph):
    # Script mode: print summary of loaded ontology
    if mo.app_meta().mode == "script":
        print("=" * 60)
        print("Ontology Explorer - Script Mode Test")
        print("=" * 60)
        print(f"\n✓ Ontology loaded successfully")
        print(f"  - Total RDF triples: {len(graph)}")
        print(f"  - Graph nodes: {nx_graph.number_of_nodes()}")
        print(f"  - Graph edges: {nx_graph.number_of_edges()}")
        print("\n✓ Script mode test completed successfully!")
        print("=" * 60)
    return


if __name__ == "__main__":
    app.run()
