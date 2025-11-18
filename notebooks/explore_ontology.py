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

__generated_with = "0.17.8"
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
def _(Path, mo):
    # Input for ontology file path or URI
    ontology_input = mo.ui.text(
        label="Ontology Path or URI",
        full_width=True,
        value="",
        placeholder="Enter file path or URI (e.g., http://example.org/ontology.ttl)"
    )
    ontology_input
    return (ontology_input,)


@app.cell
def _(Path, mo, ontology_input, rdflib):
    import urllib.request

    graph = rdflib.Graph()

    _input_value = ontology_input.value.strip()
    _out = []
    if _input_value:
        # Check if it's a URI or file path
        if _input_value.startswith(('http://', 'https://')):
            # Load from URI
            try:
                # Fetch content manually first (WASM-compatible approach)
                with urllib.request.urlopen(_input_value) as response:
                    _content = response.read().decode('utf-8')

                # Parse from string instead of URL
                graph.parse(data=_content, format="turtle")
                _out.append(mo.md(f"✓ Loaded ontology from URI: `{_input_value}`"))
            except Exception as e:
                _out.append(mo.md(f"❌ Error loading from URI: {e}"))
        else:
            # Load from file path
            _ontology_path = Path(_input_value)
            if _ontology_path.exists():
                graph.parse(_ontology_path, format="turtle")
                _out.append(mo.md(f"✓ Loaded ontology from file: `{_ontology_path}`"))
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
def _(mo):
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

        # Add nodes
        for node_id, node_data in G.nodes(data=True):
            node_type = node_data.get('node_type', 'unknown')

            # Skip filtered types
            if node_type in skip_types:
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
    _filters = {
        'show_blank': show_blank_nodes.value,
        'show_meta': show_meta.value,
        'show_datatypes': show_datatypes.value,
        'show_literals': show_literals.value,
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

    mo.vstack([
        mo.md(f"**Showing {len(_cyto_elements)} elements** (Layout: {_selected_layout})"),
        graph_viz
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


if __name__ == "__main__":
    app.run()
