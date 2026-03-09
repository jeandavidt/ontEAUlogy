"""FastAPI application entry point for ontEAUlogy orchestrator."""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import OrchestratorConfig, load_config, get_config
from .schemas.models import HealthResponse, ModelRegistrationRequest
from .services.model_registry import registry
from .services.ontology_store import ontology_store
from .services.sparql_engine import sparql_engine
from .services.llm_sparql import get_llm_sparql_translator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def discover_and_register_models(config: OrchestratorConfig) -> int:
    """Discover running model services and register them.

    Args:
        config: Orchestrator configuration with model discovery settings

    Returns:
        Number of models successfully registered
    """
    registered_count = 0

    async with httpx.AsyncClient(timeout=5.0) as client:
        for model_config in config.models.discovery:
            try:
                # Try to fetch model's self-description
                resp = await client.get(f"{model_config.endpoint}/describe")
                if resp.status_code == 200:
                    description = resp.json()
                    graph = description.get("@graph", [{}])
                    model_info = graph[0] if graph else {}

                    registry.register_model(
                        ModelRegistrationRequest(
                            id=model_config.id,
                            name=model_config.name or model_info.get("rdfs:label", model_config.id),
                            description=model_config.description
                            or model_info.get("rdfs:comment", ""),
                            endpoint=model_config.endpoint,
                            capabilities=model_config.capabilities
                            or ["SteadyStateSimulation", "MassBalance"],
                            entities=[model_config.entity],
                        )
                    )
                    logger.info(f"Registered model: {model_config.id} at {model_config.endpoint}")
                    registered_count += 1

            except httpx.ConnectError:
                logger.debug(f"Model {model_config.id} not available at {model_config.endpoint}")
            except Exception as e:
                logger.warning(f"Error registering model {model_config.id}: {e}")

    return registered_count


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    config: OrchestratorConfig = app.state.config

    # Startup
    logger.info(f"Starting {config.app.name} v{config.app.version}")

    try:
        # Configure ontology store
        ontology_store.configure(
            base_path=config.ontology.base_path,
            case_study_path=config.ontology.case_study_path,
            files=config.ontology.files,
        )

        # Load ontology
        await ontology_store.load_ontology()
        logger.info("Ontology loaded successfully")

        # Set graph for SPARQL engine
        sparql_engine.set_graph(ontology_store.get_graph())
        logger.info("SPARQL engine configured")

        # Initialize LLM translator
        logger.info("Initializing LLM translator...")
        translator = get_llm_sparql_translator()
        llm_initialized = await translator.initialize()
        if llm_initialized:
            logger.info(f"LLM translator ready: provider={translator.provider}")
        else:
            logger.warning(
                "LLM translator failed to initialize - natural language queries will fail"
            )

    except Exception as e:
        logger.warning(f"Failed to initialize services on startup: {e}")

    # Discover and register models
    logger.info("Discovering and registering models...")
    model_count = await discover_and_register_models(config)
    logger.info(f"Registered {model_count} model(s)")

    yield

    # Shutdown
    logger.info(f"Shutting down {config.app.name}")


def create_app(config_path: Optional[Path] = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        config_path: Optional path to YAML configuration file

    Returns:
        Configured FastAPI application
    """
    # Load configuration
    config = load_config(config_path)

    # Create FastAPI application
    app = FastAPI(
        title=config.app.name,
        description=config.app.description,
        version=config.app.version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Store config in app state for access during lifespan
    app.state.config = config

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and include routers
    from .routers import discovery, query, simulation, ontology, websocket, sensors, trace

    app.include_router(discovery)
    app.include_router(query)
    app.include_router(simulation)
    app.include_router(ontology)
    app.include_router(websocket)
    app.include_router(sensors)
    app.include_router(trace)

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint with component validation."""
        components = {}

        # Check ontology store
        try:
            if ontology_store.is_loaded() and ontology_store.get_triple_count() > 0:
                components["ontology"] = "healthy"
            elif ontology_store.is_loaded():
                components["ontology"] = "degraded - empty graph"
            else:
                components["ontology"] = "not loaded"
        except Exception as e:
            components["ontology"] = f"error - {type(e).__name__}"

        # Check SPARQL engine
        try:
            test_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o } LIMIT 1"
            result = sparql_engine.execute_query(test_query)
            if "error" not in result:
                components["sparql_engine"] = "healthy"
            else:
                components["sparql_engine"] = f"error - {result.get('error', 'unknown')}"
        except Exception as e:
            components["sparql_engine"] = f"error - {type(e).__name__}"

        # Check LLM translator
        try:
            translator = get_llm_sparql_translator()
            if translator._initialized:
                components["llm_translator"] = f"healthy - {translator.provider}"
            else:
                components["llm_translator"] = "not initialized"
        except Exception as e:
            components["llm_translator"] = f"error - {type(e).__name__}"

        # Check model registry
        try:
            model_count = len(registry.list_models())
            components["model_registry"] = f"healthy - {model_count} models"
        except Exception as e:
            components["model_registry"] = f"error - {type(e).__name__}"

        # Determine overall status
        has_critical_error = any("error" in str(v) for v in components.values())
        all_healthy = all("healthy" in str(v) for v in components.values())

        if has_critical_error:
            overall_status = "unhealthy"
        elif all_healthy:
            overall_status = "healthy"
        else:
            overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            version=config.app.version,
            components=components,
        )

    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint with API info."""
        return {
            "name": config.app.name,
            "version": config.app.version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Default app instance (used by uvicorn)
app = create_app()


def run():
    """Run the orchestrator (entry point for CLI)."""
    import uvicorn
    import sys

    # Check for config path argument
    config_path = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    # Create app with config
    app = create_app(config_path)
    config = app.state.config

    # Run server
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    run()
