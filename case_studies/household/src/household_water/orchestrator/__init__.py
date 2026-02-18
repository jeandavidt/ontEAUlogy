"""Household orchestrator - Uses waterframe_core for orchestration.

This module creates a FastAPI orchestrator for the household case study
using the reusable waterframe_core components.
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


HOUSEHOLD_MODEL_PORTS = {
    "mbr": 8101,
    "ro": 8102,
    "infiltration": 8103,
}


async def discover_household_models():
    """Discover and register household model services."""
    import httpx

    from waterframe_core.orchestrator.services import registry

    registered_count = 0

    async with httpx.AsyncClient(timeout=5.0) as client:
        for model_id, port in HOUSEHOLD_MODEL_PORTS.items():
            endpoint = f"http://localhost:{port}"
            try:
                resp = await client.get(f"{endpoint}/describe")
                if resp.status_code == 200:
                    description = resp.json()
                    graph = description.get("@graph", [{}])
                    model_info = graph[0] if graph else {}

                    registry.register_model(
                        id=f"household_{model_id}",
                        name=model_info.get("rdfs:label", model_id.upper()),
                        endpoint=endpoint,
                        capabilities=[
                            "SteadyStateSimulation",
                            "DynamicSimulation",
                            "Calibration",
                        ],
                        entities=[f"housecase1:{model_id.capitalize()}"],
                        description=model_info.get("rdfs:comment", ""),
                    )
                    logger.info(f"Registered household model: {model_id} at {endpoint}")
                    registered_count += 1

            except httpx.ConnectError:
                logger.debug(f"Household model {model_id} not available at {endpoint}")
            except Exception as e:
                logger.warning(f"Error registering household model {model_id}: {e}")

    return registered_count


def create_household_orchestrator() -> FastAPI:
    """Create the household case study orchestrator."""
    from contextlib import asynccontextmanager
    from waterframe_core.orchestrator.main import OrchestratorConfig
    from waterframe_core.orchestrator.services import (
        execution_trace_service,
        ontology_store,
        sparql_engine,
    )
    from waterframe_core.orchestrator.routers import trace

    # Determine paths
    project_root = Path(__file__).parent.parent.parent.parent
    data_root = project_root / "data"
    household_data = project_root / "case_studies" / "household" / "data"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan handler."""
        logger.info("Starting Household Orchestrator")

        # Configure and load ontology
        ontology_store.configure(
            ontology_base_path=str(data_root),
            case_study_data_path=str(household_data),
        )
        await ontology_store.load_ontology()
        logger.info("Ontology loaded successfully")

        try:
            sparql_engine.set_graph(ontology_store.get_graph())
            logger.info("SPARQL engine configured")
        except Exception as e:
            logger.warning(f"Could not configure SPARQL engine: {e}")

        # Discover models
        logger.info("Discovering household models...")
        model_count = await discover_household_models()
        logger.info(f"Registered {model_count} household model(s)")

        yield

        logger.info("Shutting down Household Orchestrator")

    app = FastAPI(
        title="ontEAUlogy Household Backend",
        description="FastAPI orchestrator for Household water treatment system",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include trace router
    app.include_router(trace.router)

    # Health check
    @app.get("/health")
    async def health_check():
        from waterframe_core.orchestrator.services import registry

        components = {}

        try:
            if ontology_store.is_loaded():
                components["ontology"] = (
                    f"healthy ({ontology_store.get_triple_count()} triples)"
                )
            else:
                components["ontology"] = "not loaded"
        except Exception as e:
            components["ontology"] = f"error: {e}"

        try:
            model_count = len(registry.list_models())
            components["models"] = f"{model_count} registered"
        except Exception as e:
            components["models"] = f"error: {e}"

        healthy = all("error" not in str(v) for v in components.values())

        return {
            "status": "healthy" if healthy else "degraded",
            "version": "0.1.0",
            "components": components,
        }

    @app.get("/")
    async def root():
        return {
            "name": "ontEAUlogy Household Backend",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_household_orchestrator()
