"""FastAPI factory for creating case-study-specific orchestrators.

This module provides a factory function to create configured FastAPI applications
for different case studies (Ghent, Household, etc.) using shared core services.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .services import (
    execution_trace_service,
    ontology_store,
    sparql_engine,
    registry,
)
from .routers import trace

logger = logging.getLogger(__name__)


class OrchestratorConfig:
    """Configuration for an orchestrator instance."""

    def __init__(
        self,
        app_name: str,
        app_version: str = "0.1.0",
        app_description: str = "",
        model_ports: Optional[Dict[str, int]] = None,
        ontology_base_path: Optional[str] = None,
        case_study_data_path: Optional[str] = None,
        enable_llm: bool = False,
        enable_sensors: bool = False,
    ):
        self.app_name = app_name
        self.app_version = app_version
        self.app_description = app_description
        self.model_ports = model_ports or {}
        self.ontology_base_path = ontology_base_path
        self.case_study_data_path = case_study_data_path
        self.enable_llm = enable_llm
        self.enable_sensors = enable_sensors


async def discover_models(config: OrchestratorConfig) -> int:
    """Discover and register models based on config."""
    import httpx

    registered_count = 0

    async with httpx.AsyncClient(timeout=5.0) as client:
        for model_id, port in config.model_ports.items():
            endpoint = f"http://localhost:{port}"
            try:
                resp = await client.get(f"{endpoint}/describe")
                if resp.status_code == 200:
                    description = resp.json()
                    graph = description.get("@graph", [{}])
                    model_info = graph[0] if graph else {}

                    registry.register_model(
                        id=model_id,
                        name=model_info.get("rdfs:label", model_id.upper()),
                        endpoint=endpoint,
                        capabilities=["SteadyStateSimulation", "MassBalance"],
                        entities=[],
                        description=model_info.get("rdfs:comment", ""),
                    )
                    logger.info(f"Registered model: {model_id} at {endpoint}")
                    registered_count += 1

            except httpx.ConnectError:
                logger.debug(f"Model {model_id} not available at {endpoint}")
            except Exception as e:
                logger.warning(f"Error registering model {model_id}: {e}")

    return registered_count


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    config: OrchestratorConfig = app.state.config

    logger.info(f"Starting {config.app_name} v{config.app_version}")

    # Configure and load ontology
    if config.ontology_base_path:
        ontology_store.configure(
            ontology_base_path=config.ontology_base_path,
            case_study_data_path=config.case_study_data_path,
        )
        await ontology_store.load_ontology()
        logger.info("Ontology loaded successfully")

        # Configure SPARQL engine
        try:
            sparql_engine.set_graph(ontology_store.get_graph())
            logger.info("SPARQL engine configured")
        except Exception as e:
            logger.warning(f"Could not configure SPARQL engine: {e}")

    # Discover models
    if config.model_ports:
        logger.info("Discovering and registering models...")
        model_count = await discover_models(config)
        logger.info(f"Registered {model_count} model(s)")

    yield

    logger.info(f"Shutting down {config.app_name}")


def create_orchestrator(config: OrchestratorConfig) -> FastAPI:
    """Create a configured FastAPI orchestrator.

    Args:
        config: Configuration for the orchestrator.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title=config.app_name,
        description=config.app_description,
        version=config.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.state.config = config

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include trace router
    app.include_router(trace.router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
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
            "version": config.app_version,
            "components": components,
        }

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": config.app_name,
            "version": config.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


def create_ghent_orchestrator() -> FastAPI:
    """Create the Ghent case study orchestrator."""
    config = OrchestratorConfig(
        app_name="ontEAUlogy Ghent Backend",
        app_description="FastAPI orchestrator for Ghent water system ontology management",
        app_version="0.1.0",
        model_ports={
            "dwp1": 8001,
            "dwp2": 8002,
            "wwtp1": 8003,
            "wwtp2": 8004,
        },
        ontology_base_path=str(Path(__file__).parent.parent.parent.parent / "data"),
        case_study_data_path=str(
            Path(__file__).parent.parent.parent.parent
            / "case_studies"
            / "ghent"
            / "data"
        ),
        enable_llm=True,
        enable_sensors=True,
    )
    return create_orchestrator(config)
