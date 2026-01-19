# Coding Conventions

**Analysis Date:** 2026-01-19

## Naming Patterns

**Files:**
- snake_case for all Python files (e.g., `api_client.py`, `sensor_config.py`)
- Module directories use snake_case (e.g., `frontend/`, `orchestrator/`, `models/`)
- Package directories match import paths (e.g., `ghent_water/`)

**Functions:**
- snake_case for all functions (e.g., `get_entity_by_id()`, `create_job()`)
- Private/internal functions use underscore prefix (e.g., `_get_client()`, `_extract_entity_id()`)
- Async functions use `async def` prefix (e.g., `async def load_ontology()`, `async def execute_sparql_query()`)

**Variables:**
- snake_case for variables (e.g., `entity_id`, `job_count`, `query_time_ms`)
- Private/internal class attributes use underscore prefix (e.g., `_models`, `_jobs`, `_client`)
- Constants use UPPER_SNAKE_CASE (e.g., `MODEL_PORTS`, `VLAREM_II_LIMITS`, `WATERFRAME_BASE`)

**Types/Classes:**
- CamelCase for class names (e.g., `ModelRegistry`, `OrchestratorClient`, `BaseWaterModel`)
- Pydantic models use CamelCase with descriptive names (e.g., `SparqlQueryRequest`, `SimulationJobResponse`)
- Base classes use descriptive names with "Base" prefix (e.g., `BaseWaterModel`)

## Code Style

**Formatting:**
- No explicit formatting tool configured (no `.prettierrc`, `black`, or `ruff` configuration detected)
- Manual formatting with 4-space indentation (consistent across codebase)
- Blank lines between logical sections (functions, classes, imports)
- Maximum line length not enforced (some lines exceed 100 characters)

**Linting:**
- No linting tool configured (no `.flake8`, `.pylintrc`, or `.ruff.toml` detected)
- No CI/CD pipeline for linting checks

## Import Organization

**Order:**
1. Standard library imports (e.g., `import logging`, `from pathlib import Path`)
2. Third-party imports (e.g., `import httpx`, `from fastapi import FastAPI`)
3. Local application imports (e.g., `from ..services.model_registry import registry`)

**Grouping:**
```python
# Standard library
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Third-party
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Local
from ..services.ontology_store import ontology_store
from ..schemas.models import ModelRegistrationRequest
```

**Path Aliases:**
- Use relative imports within packages (e.g., `from ..services.model_registry import registry`)
- Absolute imports from package root (e.g., `from ghent_water.frontend.config import Config`)

## Error Handling

**Patterns:**

**For API endpoints (FastAPI):**
```python
try:
    result = sparql_engine.execute_query(request.query, request.format)
    return SparqlQueryResponse(...)
except Exception as e:
    logger.error(f"SPARQL query failed: {e}\n{traceback.format_exc()}")
    raise HTTPException(status_code=400, detail=str(e))
```

**For async operations:**
```python
try:
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{endpoint}/describe")
        resp.raise_for_status()
        return resp.json()
except httpx.ConnectError:
    logger.warning(f"Could not connect to model {model_id} at {endpoint}")
    return False
except Exception as e:
    logger.error(f"Error registering model {model_id}: {e}")
    return None
```

**For service methods:**
```python
def get_entity(self, entity_uri: str) -> Optional[Dict[str, Any]]:
    """Get entity details from the ontology."""
    if not self._loaded or self._graph is None:
        return None

    try:
        entity_ref = URIRef(entity_uri)
        # ... process entity ...
        return result
    except Exception as e:
        logger.error(f"Error getting entity {entity_uri}: {e}")
        return None
```

**Key patterns:**
- Always log errors with context
- Use specific exception types where possible (`httpx.ConnectError`, `httpx.HTTPStatusError`)
- Return `None` for non-critical failures (service methods)
- Raise `HTTPException` for API endpoint failures
- Include traceback for debugging in critical paths

## Logging

**Framework:** Python standard `logging` module

**Patterns:**
```python
# Module-level logger
logger = logging.getLogger(__name__)

# Use different log levels appropriately
logger.debug(f"Query: {request.query[:200]}...")  # Debug info
logger.info(f"Received SPARQL query request (format={request.format})")  # General info
logger.warning(f"OPENROUTER_API_KEY not found in environment!")  # Non-critical issue
logger.error(f"SPARQL query failed: {e}")  # Error with context
```

**Global logging setup (in `src/ghent_water/orchestrator/main.py`):**
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
)
```

**When to log:**
- Log at INFO level: API requests, significant state changes, successful operations
- Log at DEBUG level: Detailed execution flow, variable values, query snippets
- Log at WARNING level: Non-critical failures, missing optional features
- Log at ERROR level: Exceptions that prevent operation completion

## Comments

**When to Comment:**
- All modules have docstrings at the top explaining purpose
- All public functions have docstrings with Args/Returns sections
- Complex logic explained with inline comments
- TODO/FIXME comments: Not present in codebase (no markers found)

**JSDoc/TSDoc:**
- Python docstrings used (not JSDoc/TSDoc)
- Google-style docstrings with Args/Returns format

**Docstring format:**
```python
def register_model(self, request: ModelRegistrationRequest) -> ModelInfo:
    """Register a new model or update existing one."""
    # ... implementation ...

async def load_ontology(self) -> bool:
    """Load the ontology from TTL files.

    Loads from:
    1. Main ontology: ontEAUlogy/data/ontology/waterframe.ttl
    2. Ontology modules: ontEAUlogy/data/ontology/modules/*.ttl

    Returns:
        True if ontology loaded successfully, False otherwise.
    """
    # ... implementation ...

def _get_parameter_value(
    self, inputs: Dict[str, Any], param_name: str, default: Any = None
) -> Any:
    """Get parameter value from inputs, with fallback to default.

    Args:
        inputs: Input dictionary.
        param_name: Name of parameter to retrieve.
        default: Default value if parameter not found.

    Returns:
        Parameter value or default.
    """
    # ... implementation ...
```

## Function Design

**Size:**
- No strict size limit enforced
- Functions range from 10-80 lines
- Complex functions (e.g., `load_ontology()`) can exceed 80 lines

**Parameters:**
- Type hints for all parameters
- Default values for optional parameters (e.g., `timeout: int = 30.0`)
- Use `**kwargs` for extensibility in base classes
- Dictionaries for complex inputs (e.g., `parameters: Dict[str, Any]`)

**Return Values:**
- Type hints for all return values
- Return `None` for failures in non-critical methods
- Return `bool` for success/failure operations
- Return complex objects (dicts, Pydantic models) for API responses
- Use `Optional[Type]` for nullable returns (e.g., `Optional[Dict[str, Any]]`)

**Examples:**
```python
# Simple return
def get_model(self, model_id: str) -> Optional[ModelInfo]:
    """Get a model by ID."""
    return self._models.get(model_id)

# Dictionary return
def create_job(self, model_id: str, parameters: Dict[str, Any]) -> str:
    """Create a new simulation job."""
    job_id = str(uuid.uuid4())
    # ... set up job ...
    return job_id

# Pydantic model return
@router.post("/sparql", response_model=SparqlQueryResponse)
async def execute_sparql_query(request: SparqlQueryRequest):
    """Execute a SPARQL query against the unified graph."""
    result = sparql_engine.execute_query(request.query, request.format)
    return SparqlQueryResponse(...)
```

## Module Design

**Exports:**
- `__init__.py` files used sparingly
- Some packages use barrel exports (e.g., `src/ghent_water/frontend/components/__init__.py`)
- Many packages have minimal `__init__.py` (just docstring or empty)

**Barrel files:**
```python
# src/ghent_water/frontend/components/__init__.py
from .map_view import (
    create_map_view,
    get_entity_by_id,
    ENTITY_PORTS,
    # ...
)
from .query_panel import render_query_panel
from .entity_details import render_entity_details
```

**Global instances:**
- Services use global singleton pattern (e.g., `ontology_store = OntologyStore()`, `registry = ModelRegistry()`)
- Imported from service modules: `from ..services.model_registry import registry`

**Configuration:**
- Config classes use module-level constants (e.g., `src/ghent_water/frontend/config.py`)
- Environment variables loaded with `python-dotenv`
- Settings classes in `pydantic-settings` for orchestrator

---

*Convention analysis: 2026-01-19*
