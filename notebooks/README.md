# Ontology Explorer Notebook

Interactive notebook for exploring and visualizing RDF ontologies using [marimo](https://marimo.io/).

## Features

- **Modular Ontology Loading**: Automatically loads main ontology file plus all modules and bridges
- **Local & Remote Support**: Works with both local file paths and HTTP(S) URIs
- **Interactive Visualization**: Graph-based visualization using Cytoscape.js with color-coded node types
- **Namespace/Module Filtering**: Filter graph by specific namespaces or ontology modules
- **Flexible Type Filtering**: Filter by node types (blank nodes, meta-level terms, datatypes, literals)
- **Visual Legend**: Color-coded legend showing all node types and their visual representation
- **Multiple Layouts**: Choose from various graph layout algorithms (fcose, cose, cola, etc.)
- **Enhanced Class Detection**: Automatically identifies classes defined via `rdfs:subClassOf`
- **Statistics**: View graph statistics and node type distributions

## Usage

### Interactive Mode (UI)

Run the notebook in interactive mode with marimo:

```bash
marimo edit notebooks/explore_ontology.py
```

This will open a web interface where you can:
- Enter an ontology path or URI
- Filter by namespace/module (with hierarchical display)
- Adjust visualization filters (show/hide different node types)
- Change layout algorithms
- Click nodes to view details
- View a color-coded legend for all node types

### Script Mode (CLI)

Run the notebook as a command-line script:

```bash
# Use default local path (data/ontology/waterframe.ttl)
uv run --with-requirements notebooks/explore_ontology.py notebooks/explore_ontology.py

# Or specify a custom path
uv run --with-requirements notebooks/explore_ontology.py notebooks/explore_ontology.py --ontology data/ontology/waterframe.ttl

# Or use a URI
uv run --with-requirements notebooks/explore_ontology.py notebooks/explore_ontology.py --ontology http://example.org/ontology.ttl
```
