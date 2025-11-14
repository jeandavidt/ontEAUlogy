# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "networkx==3.5",
#     "numpy==2.3.4",
#     "plotly==6.4.0",
#     "rdflib==7.4.0",
# ]
# ///

import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import rdflib
    import sys
    from pathlib import Path
    import numpy as np
    from rdflib import Graph, URIRef
    from rdflib.namespace import DC, OWL, RDF, RDFS, SKOS
    import networkx as nx
    import plotly.graph_objects as go
    return OWL, Path, RDF, RDFS, go, mo, nx, rdflib


@app.cell
def _(Path, mo):
    # Input for ontology file path or URI
    ontology_input = mo.ui.text(
        label="Ontology Path or URI",
        full_width=True,
        value=str(Path(__file__).parent.parent / "data/ontology/onteaulogy.ttl"),
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
def _(OWL, RDF, RDFS, graph, nx):
    # Convert RDF graph to NetworkX with type information
    def rdf_to_networkx(rdf_graph):
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
            str(RDF.Statement), str(RDF.List), str(RDF.Seq), str(RDF.Bag), str(RDF.Alt),
            str(RDFS.Literal), str(RDFS.Container),
        }

        # Also check by namespace prefix for any RDF/RDFS/OWL/W3C vocabulary terms
        meta_namespaces = [
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'http://www.w3.org/2000/01/rdf-schema#',
            'http://www.w3.org/2002/07/owl#',
            'http://www.w3.org/ns/r2rml#',
            'http://www.w3.org/TR/',  # W3C Technical Reports
            'https://www.w3.org/TR/',
        ]

        # First pass: identify node types
        node_types = {}
        ontology_nodes = set()

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
            if '#' in s_uri and s_uri.split('#')[0] in [ns.rstrip('#') for ns in meta_namespaces]:
                _fragment = s_uri.split('#')[1].lower()
                if any(dt in _fragment for dt in ['json', 'html', 'xml', 'plainliteral', 'langstring']):
                    node_types[s_uri] = 'datatype'
            if '#' in o_uri and o_uri.split('#')[0] in [ns.rstrip('#') for ns in meta_namespaces]:
                _fragment = o_uri.split('#')[1].lower()
                if any(dt in _fragment for dt in ['json', 'html', 'xml', 'plainliteral', 'langstring']):
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

            s_label = s_uri.split('/')[-1].split('#')[-1]
            p_label = p_uri.split('/')[-1].split('#')[-1]
            o_label = o_uri.split('/')[-1].split('#')[-1]

            # Determine node types
            s_type = node_types.get(s_uri, 'unknown')

            # For objects, check if it's a literal (doesn't start with http)
            if o_uri.startswith('http'):
                o_type = node_types.get(o_uri, 'unknown')
            else:
                o_type = 'literal'

            # Add nodes with type information
            if s_uri not in G.nodes:
                G.add_node(s_uri, label=s_label, uri=s_uri, node_type=s_type)
            if o_uri not in G.nodes:
                G.add_node(o_uri, label=o_label, uri=o_uri, node_type=o_type)

            # Add edge with predicate info
            G.add_edge(s_uri, o_uri, predicate=p_label, predicate_uri=p_uri)

        return G

    nx_graph = rdf_to_networkx(graph)
    return (nx_graph,)


@app.cell
def _():
    return


@app.cell
def _(graph, mo):
    # Extract all namespaces from the graph
    def extract_namespaces(rdf_graph):
        """Extract unique namespace prefixes from all URIs in the graph"""
        _namespaces = {}

        for s, p, o in rdf_graph:
            for _uri in [str(s), str(p), str(o)]:
                if _uri.startswith('http://') or _uri.startswith('https://'):
                    # Split on # or the last / to get the actual namespace
                    if '#' in _uri:
                        # For URIs with #, the namespace includes the #
                        _ns = _uri.rsplit('#', 1)[0] + '#'
                    elif _uri.count('/') > 2:  # More than just http://domain
                        # For URIs with /, take everything up to and including the last /
                        # But only if there's actual path content
                        _ns = _uri.rsplit('/', 1)[0] + '/'
                    else:
                        # Just the base domain
                        continue  # Skip base domains without paths

                    # Try to get a nice prefix name
                    if _ns not in _namespaces:
                        # Check if it's a known namespace from rdflib
                        _prefix = None
                        for _p, _n in rdf_graph.namespaces():
                            if str(_n) == _ns:
                                _prefix = _p
                                break

                        # If no prefix found, create one from the URI
                        if not _prefix:
                            if 'w3.org' in _ns:
                                if 'XMLSchema' in _ns:
                                    _prefix = 'xsd'
                                elif 'rdf-schema' in _ns:
                                    _prefix = 'rdfs'
                                elif '1999/02/22' in _ns:
                                    _prefix = 'rdf'
                                elif 'owl' in _ns:
                                    _prefix = 'owl'
                                elif 'skos' in _ns:
                                    _prefix = 'skos'
                                else:
                                    _prefix = 'w3'
                            else:
                                # Extract a meaningful name from the URI
                                # For http://example.org/onteaulogy#, use 'onteaulogy'
                                _uri_parts = _ns.replace('http://', '').replace('https://', '').rstrip('/#').split('/')
                                if len(_uri_parts) > 1:
                                    _prefix = _uri_parts[-1]  # Last meaningful part
                                else:
                                    _prefix = _uri_parts[0].split('.')[0]  # Domain

                        _namespaces[_ns] = _prefix if _prefix else 'unknown'

        return _namespaces

    _namespaces_extracted = extract_namespaces(graph)

    # Create a dictionary UI element that groups all checkboxes
    namespace_filter = mo.ui.dictionary({
        _ns: mo.ui.checkbox(
            label=f"{_prefix} ({_ns[:50]}...)" if len(_ns) > 50 else f"{_prefix} ({_ns})",
            value=True
        )
        for _ns, _prefix in sorted(_namespaces_extracted.items(), key=lambda x: x[1])
    })

    # Display namespace filters
    _ns_items = list(namespace_filter.items())
    _ns_display = [mo.md("**Filter by namespace:**")]
    for _i in range(0, len(_ns_items), 2):
        _row = [_ns_items[_i][1]]
        if _i + 1 < len(_ns_items):
            _row.append(_ns_items[_i + 1][1])
        _ns_display.append(mo.hstack(_row))

    mo.vstack(_ns_display)
    return (namespace_filter,)


@app.cell
def _(mo):
    # Search box for filtering nodes
    search_box = mo.ui.text(
        label="Search nodes (filter by label or URI)",
        placeholder="Type to filter nodes..."
    )

    # Create checkboxes for filtering node types
    show_ontology = mo.ui.checkbox(label="Show Ontology", value=True)
    show_meta = mo.ui.checkbox(label="Show Meta-level Terms", value=True)
    show_datatypes = mo.ui.checkbox(label="Show Datatypes (XSD)", value=True)
    show_classes = mo.ui.checkbox(label="Show Classes", value=True)
    show_object_properties = mo.ui.checkbox(label="Show Object Properties", value=True)
    show_datatype_properties = mo.ui.checkbox(label="Show Datatype Properties", value=True)
    show_individuals = mo.ui.checkbox(label="Show Individuals", value=True)
    show_literals = mo.ui.checkbox(label="Show Literals", value=True)
    show_unknown = mo.ui.checkbox(label="Show Unknown", value=True)
    k_slider = mo.ui.slider(start=0.1, step=0.05, stop=3,label="Neighbour distance")
    mo.vstack([
        search_box,
        mo.md("**Filter by node type:**"),
        mo.hstack([show_ontology, show_meta, show_datatypes]),
        mo.hstack([show_classes, show_object_properties, show_datatype_properties]),
        mo.hstack([show_individuals, show_literals, show_unknown]),
        k_slider
    ])
    return (
        k_slider,
        search_box,
        show_classes,
        show_datatype_properties,
        show_datatypes,
        show_individuals,
        show_literals,
        show_meta,
        show_object_properties,
        show_ontology,
        show_unknown,
    )


@app.cell
def _(
    go,
    k_slider,
    mo,
    namespace_filter,
    nx,
    nx_graph,
    search_box,
    show_classes,
    show_datatype_properties,
    show_datatypes,
    show_individuals,
    show_literals,
    show_meta,
    show_object_properties,
    show_ontology,
    show_unknown,
):
    # Define colors and sizes for different node types
    node_styles = {
        'ontology': {'color': '#8e44ad', 'size': 18, 'symbol': 'star'},
        'meta': {'color': '#34495e', 'size': 14, 'symbol': 'diamond'},
        'datatype': {'color': '#16a085', 'size': 12, 'symbol': 'hexagon'},
        'class': {'color': '#3498db', 'size': 15, 'symbol': 'circle'},
        'object_property': {'color': '#2ecc71', 'size': 12, 'symbol': 'diamond'},
        'datatype_property': {'color': '#f39c12', 'size': 12, 'symbol': 'square'},
        'individual': {'color': '#9b59b6', 'size': 10, 'symbol': 'circle'},
        'literal': {'color': '#95a5a6', 'size': 8, 'symbol': 'circle'},
        'unknown': {'color': '#e74c3c', 'size': 10, 'symbol': 'x'}
    }

    # Map checkboxes to node types
    node_type_filters = {
        'ontology': show_ontology.value,
        'meta': show_meta.value,
        'datatype': show_datatypes.value,
        'class': show_classes.value,
        'object_property': show_object_properties.value,
        'datatype_property': show_datatype_properties.value,
        'individual': show_individuals.value,
        'literal': show_literals.value,
        'unknown': show_unknown.value
    }

    # Define edge styles for different predicates
    edge_styles = {
        'type': {'color': '#34495e', 'width': 2, 'dash': 'solid'},
        'subClassOf': {'color': '#3498db', 'width': 2, 'dash': 'solid'},
        'domain': {'color': '#27ae60', 'width': 1.5, 'dash': 'dot'},
        'range': {'color': '#e67e22', 'width': 1.5, 'dash': 'dot'},
        'label': {'color': '#bdc3c7', 'width': 0.5, 'dash': 'dash'},
        'comment': {'color': '#bdc3c7', 'width': 0.5, 'dash': 'dash'},
        'default': {'color': '#888', 'width': 1, 'dash': 'solid'}
    }
    # Store edge_styles for use in legend
    current_edge_styles = edge_styles
    # Create layout
    pos = nx.spring_layout(nx_graph, k=k_slider.value, iterations=50, seed=64)

    # Start with all nodes
    all_nodes = list(nx_graph.nodes())

    # Apply node type filter first
    type_filtered_nodes = [n for n in all_nodes 
                           if node_type_filters.get(nx_graph.nodes[n]['node_type'], True)]

    # Apply namespace filter
    _selected_namespaces = {_ns for _ns, _checked in namespace_filter.value.items() if _checked}

    if _selected_namespaces:
        namespace_filtered_nodes = []
        for _n in type_filtered_nodes:
            _node_uri = _n
            # Keep literals (non-URIs)
            if not _node_uri.startswith('http'):
                namespace_filtered_nodes.append(_n)
                continue

            # Check if node belongs to a selected namespace
            for _ns in _selected_namespaces:
                if _node_uri.startswith(_ns):
                    namespace_filtered_nodes.append(_n)
                    break

        visible_nodes = namespace_filtered_nodes
    else:
        visible_nodes = type_filtered_nodes

    # Apply search filter (should be last to include neighbors)
    _search_query = search_box.value.lower().strip()
    if _search_query:
        # Find nodes that match the search
        _matching_nodes = {
            n for n in visible_nodes
            if _search_query in nx_graph.nodes[n]['label'].lower() 
            or _search_query in nx_graph.nodes[n]['uri'].lower()
        }

        # Include direct neighbors of matching nodes
        _nodes_with_neighbors = set(_matching_nodes)
        for _node in _matching_nodes:
            _nodes_with_neighbors.update(nx_graph.successors(_node))
            _nodes_with_neighbors.update(nx_graph.predecessors(_node))

        # Keep only neighbors that pass the other filters
        visible_nodes = [n for n in _nodes_with_neighbors if n in visible_nodes or n in _matching_nodes]

    # Group nodes by type for separate traces
    node_traces = []
    for _node_type, _style in node_styles.items():
        if not node_type_filters.get(_node_type, True):
            continue

        _nodes_of_type = [n for n in visible_nodes if nx_graph.nodes[n]['node_type'] == _node_type]
        if not _nodes_of_type:
            continue

        _node_x = [pos[n][0] for n in _nodes_of_type]
        _node_y = [pos[n][1] for n in _nodes_of_type]
        _node_labels = [nx_graph.nodes[n]['label'] for n in _nodes_of_type]

        _hover_text = [f"<b>{nx_graph.nodes[n]['label']}</b><br>Type: {_node_type}<br>URI: {n}" 
                      for n in _nodes_of_type]

        _trace = go.Scatter(
            x=_node_x, y=_node_y,
            mode='markers+text',
            text=_node_labels,
            textposition="top center",
            hovertext=_hover_text,
            hoverinfo='text',
            marker=dict(
                size=_style['size'],
                color=_style['color'],
                symbol=_style['symbol'],
                line_width=2),
            name=_node_type.replace('_', ' ').title(),
            showlegend=True
        )
        node_traces.append(_trace)

    # Filter edges - only show edges where both nodes are visible
    edge_traces = []
    edges_by_predicate = {}
    for _s, _t in nx_graph.edges():
        if _s in visible_nodes and _t in visible_nodes:
            _pred = nx_graph.edges[_s, _t]['predicate']
            if _pred not in edges_by_predicate:
                edges_by_predicate[_pred] = []
            edges_by_predicate[_pred].append((_s, _t))

    for _pred, _edges in edges_by_predicate.items():
        _edge_x = []
        _edge_y = []
        for _s, _t in _edges:
            _x0, _y0 = pos[_s]
            _x1, _y1 = pos[_t]
            _edge_x.extend([_x0, _x1, None])
            _edge_y.extend([_y0, _y1, None])

        _style = edge_styles.get(_pred, edge_styles['default'])

        _trace = go.Scatter(
            x=_edge_x, y=_edge_y,
            mode='lines',
            line=dict(width=_style['width'], color=_style['color'], dash=_style['dash']),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(_trace)

    # Create figure
    fig = go.Figure(data=edge_traces + node_traces,
                 layout=go.Layout(
                    showlegend=True,
                    hovermode='closest',
                    clickmode='event+select',
                    margin=dict(b=0,l=0,r=0,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600,
                    legend=dict(x=0, y=1, bgcolor='rgba(255,255,255,0.8)')
                    ))

    graph_plot = mo.ui.plotly(fig)
    graph_plot
    return current_edge_styles, graph_plot, pos


@app.cell
def _(current_edge_styles, mo, nx_graph):
    # Create edge style legend from the actual edge_styles used in the plot
    _edge_legend_md = """
    ## Edge Styles Legend

    The edges (connections) in the graph are styled based on the predicate (relationship type):

    | Predicate | Color | Width | Dash Style |
    |-----------|-------|-------|------------|
    """

    # Add rows for each defined edge style
    for _pred, _style in current_edge_styles.items():
        if _pred == 'default':
            _pred_display = "**other predicates**"
        else:
            _pred_display = f"**{_pred}**"

        _edge_legend_md += f"| {_pred_display} | {_style['color']} | {_style['width']} | {_style['dash']} |\n"

    _edge_legend_md += "\n### Predicates present in this graph:\n\n"

    # List all unique predicates in the current graph
    _predicates_in_graph = set()
    for _s, _t in nx_graph.edges():
        _predicates_in_graph.add(nx_graph.edges[_s, _t]['predicate'])

    _edge_legend_md += "\n".join([f"- `{_pred}`" for _pred in sorted(_predicates_in_graph)])

    mo.md(_edge_legend_md)
    return


@app.cell
def _(graph_plot, mo, nx_graph, pos):
    # Handle range-based selection
    selected_node_uris = []
    if graph_plot.ranges:
        x_range = graph_plot.ranges.get('x', [])
        y_range = graph_plot.ranges.get('y', [])

        if x_range and y_range:
            for _node_uri in nx_graph.nodes():
                node_pos = pos[_node_uri]
                if (x_range[0] <= node_pos[0] <= x_range[1] and 
                    y_range[0] <= node_pos[1] <= y_range[1]):
                    selected_node_uris.append(_node_uri)

    if selected_node_uris:
        _t = f"## Selected {len(selected_node_uris)} node(s)\n"

        for _node_uri in selected_node_uris:
            _node_data = nx_graph.nodes[_node_uri]
            _node_label = _node_data['label']
            _node_type = _node_data['node_type']

            # Get relationships
            _outgoing = [(nx_graph.nodes[_node_uri]['label'], 
                        nx_graph.edges[_node_uri, target]['predicate'], 
                        nx_graph.nodes[target]['label']) 
                        for target in nx_graph.successors(_node_uri)]
            _incoming = [(nx_graph.nodes[source]['label'],
                        nx_graph.edges[source, _node_uri]['predicate'], 
                        nx_graph.nodes[_node_uri]['label'])
                        for source in nx_graph.predecessors(_node_uri)]

            _t += f"\n---\n\n### {_node_label}\n\n"
            _t += f"**Type:** `{_node_type}`\n\n"
            _t += f"**URI:** `{_node_data['uri']}`\n\n"

            _t += "**Incoming:**\n\n"
            if _incoming:
                for _subj_label, _pred, _ in _incoming:
                    _t += f"- {_subj_label} → **{_pred}**\n"
            else:
                _t += "_None_\n"

            _t += "\n**Outgoing:**\n\n"
            if _outgoing:
                for _, _pred, _obj_label in _outgoing:
                    _t += f"- **{_pred}** → {_obj_label}\n"
            else:
                _t += "_None_\n"

    else:
        _t = "_Use box select or lasso select to choose nodes and see their details_"
    mo.md(_t)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
