# ontEAUlogy Shared

Shared utilities for ontEAUlogy case studies.

## Components

- `OntologyLoader`: Load RDF/TTL ontology files
- `OntologyManager`: Manage ontology state with caching
- `NamespaceManager`: Handle CURIE resolution and namespace prefixes

## Usage

```python
from ontEAUlogy_shared import OntologyManager, get_namespace_manager

# Load ontology
manager = OntologyManager()
manager.configure(
    ontology_base_path="/path/to/ontology",
    case_study_data_path="/path/to/case/data"
)
await manager.load_ontology()

# Query
results = manager.loader.query("SELECT * WHERE { ?s ?p ?o }")
```

## Installation

```bash
pip install -e .
```
