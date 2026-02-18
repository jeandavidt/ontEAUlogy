"""FastAPI application entry point."""

import asyncio
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Tuple

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging FIRST so we can log during startup
# Log to project root directory (where .env and scripts are)
# main.py -> orchestrator -> ghent_water -> src -> ghent (project root)
project_root = Path(__file__).parent.parent.parent.parent
log_path = project_root / "orchestrator.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file at startup
# This ensures env vars are available before settings are loaded
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment from {env_path}")
else:
    # Also try current directory
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env)
        logger.info(f"Loaded environment from {cwd_env}")

# Log environment variable status for debugging
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key:
    logger.info(f"OPENROUTER_API_KEY is set (length: {len(api_key)} chars)")
else:
    logger.warning("OPENROUTER_API_KEY not found in environment!")

from .config import get_settings
from .schemas.models import HealthResponse, ModelRegistrationRequest
from .services.model_registry import registry
from .services.ontology_store import ontology_store
from .services.sparql_engine import sparql_engine
from .services.llm_sparql import get_llm_sparql_translator
from ..models.config import MODEL_PORTS

# Household model ports for discovery
HOUSEHOLD_MODEL_PORTS = {
    "mbr": ("http://household-mbr", 8101),
    "ro": ("http://household-ro", 8102),
    "infiltration": ("http://household-infiltration", 8103),
}


async def discover_and_register_models() -> int:
    """Discover running model services and register them with the orchestrator.

    Returns:
        Number of models successfully registered.
    """
    registered_count = 0

    async with httpx.AsyncClient(timeout=5.0) as client:
        for model_id, port in MODEL_PORTS.items():
            # Use container names for Docker networking instead of localhost
            endpoint = f"http://ghent-{model_id.replace('_', '-')}:{port}"
            try:
                # Try to fetch model's self-description
                resp = await client.get(f"{endpoint}/describe")
                if resp.status_code == 200:
                    description = resp.json()

                    # Extract info from JSON-LD description
                    graph = description.get("@graph", [{}])
                    model_info = graph[0] if graph else {}

                    registry.register_model(
                        ModelRegistrationRequest(
                            id=model_id,
                            name=model_info.get("rdfs:label", model_id.upper()),
                            description=model_info.get("rdfs:comment", ""),
                            endpoint=endpoint,
                            capabilities=["SteadyStateSimulation", "MassBalance"],
                            entities=[f"ghent:{model_id.upper()}"],
                        )
                    )
                    logger.info(f"Registered model: {model_id} at {endpoint}")
                    registered_count += 1

            except httpx.ConnectError:
                logger.debug(f"Model {model_id} not available at {endpoint}")
            except Exception as e:
                logger.warning(f"Error registering model {model_id}: {e}")

        # Discover household models
        for model_id, (host, port) in HOUSEHOLD_MODEL_PORTS.items():
            endpoint = f"{host}:{port}"
            try:
                resp = await client.get(f"{endpoint}/describe")
                if resp.status_code == 200:
                    description = resp.json()
                    graph = description.get("@graph", [{}])
                    model_info = graph[0] if graph else {}
                    registry.register_model(
                        ModelRegistrationRequest(
                            id=f"household_{model_id}",
                            name=model_info.get("rdfs:label", model_id.upper()),
                            description=model_info.get("rdfs:comment", ""),
                            endpoint=endpoint,
                            capabilities=["SteadyStateSimulation", "MassBalance"],
                            entities=[f"housecase1:{model_id.capitalize()}"],
                        )
                    )
                    logger.info(f"Registered household model: {model_id} at {endpoint}")
                    registered_count += 1
            except httpx.ConnectError:
                logger.debug(f"Household model {model_id} not available at {endpoint}")
            except Exception as e:
                logger.warning(f"Error registering household model {model_id}: {e}")

    return registered_count


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    settings = get_settings()

    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    try:
        # Load ontology on startup
        await ontology_store.load_ontology()
        logger.info("Ontology loaded successfully")

        # Set graph for SPARQL engine
        sparql_engine.set_graph(ontology_store.get_graph())
        logger.info("SPARQL engine configured")

        # Initialize LLM translator at startup (for OpenRouter connection)
        logger.info("Initializing LLM translator...")
        translator = get_llm_sparql_translator()
        llm_initialized = await translator.initialize()
        if llm_initialized:
            logger.info(
                f"LLM translator ready: provider={translator.provider}, model={translator.current_model}"
            )
        else:
            logger.warning(
                "LLM translator failed to initialize - natural language queries will fail"
            )

    except Exception as e:
        logger.warning(f"Failed to load ontology on startup: {e}")

    # Discover and register running models
    logger.info("Discovering and registering models...")
    model_count = await discover_and_register_models()
    logger.info(f"Registered {model_count} model(s)")

    # Start background sensor data generation
    logger.info("Starting background sensor data generation...")
    asyncio.create_task(start_sensor_broadcast_loop())

    yield

    # Shutdown
    logger.info("Shutting down ontEAUlogy backend")


# Create FastAPI application
app = FastAPI(
    title="ontEAUlogy Ghent Backend",
    description="FastAPI orchestrator for Ghent water system ontology management",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import and include routers
from .routers import discovery, query, simulation, ontology, websocket, sensors, trace


# Background task to generate and broadcast sensor data every second
async def start_sensor_broadcast_loop():
    """Background task that generates and broadcasts sensor data every second."""
    from .services.sensor_generator import get_generator
    from .routers.websocket import broadcast_sensor_readings

    logger.info("Sensor broadcast loop started")

    try:
        generator = get_generator()

        while True:
            try:
                # Generate readings for all sensors
                readings = generator.generate_all_readings()

                if readings:
                    reading_dicts = [reading.to_dict() for reading in readings]
                    await broadcast_sensor_readings(reading_dicts)
                    logger.debug(f"Broadcast {len(readings)} sensor readings")
                else:
                    logger.warning("No readings generated!")

                # Wait 1 second before next iteration
                await asyncio.sleep(1.0)

            except Exception as e:
                logger.error(f"Error in sensor broadcast loop: {e}", exc_info=True)
                await asyncio.sleep(1.0)

    except asyncio.CancelledError:
        logger.info("Sensor broadcast loop cancelled")
        raise


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint with actual functionality validation."""
    settings = get_settings()
    components = {}

    # 1. Check ontology store
    try:
        if ontology_store._loaded and ontology_store.get_triple_count() > 0:
            components["ontology"] = "healthy"
        elif ontology_store._loaded:
            components["ontology"] = "degraded - empty graph"
        else:
            components["ontology"] = "not loaded"
    except Exception as e:
        components["ontology"] = f"error - {type(e).__name__}"

    # 2. Check SPARQL engine with actual query
    try:
        test_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o } LIMIT 1"
        result = sparql_engine.execute_query(test_query)
        if "error" not in result:
            components["sparql_engine"] = "healthy"
        else:
            components["sparql_engine"] = f"error - {result['error']}"
    except Exception as e:
        components["sparql_engine"] = f"error - {type(e).__name__}"

    # 3. Check LLM translator
    try:
        translator = get_llm_sparql_translator()
        if translator._initialized:
            components["llm_translator"] = f"healthy - {translator.provider}"
        else:
            components["llm_translator"] = "not initialized"
    except Exception as e:
        components["llm_translator"] = f"error - {type(e).__name__}"

    # 4. Check model registry
    try:
        model_count = len(registry.list_models())
        components["model_registry"] = f"healthy - {model_count} models"
    except Exception as e:
        components["model_registry"] = f"error - {type(e).__name__}"

    # Determine overall status
    healthy_states = ["healthy"]
    degraded_states = ["degraded", "not loaded", "not initialized"]

    has_critical_error = any("error" in str(v) for v in components.values())
    all_healthy = all(
        any(state in str(v) for state in healthy_states) for v in components.values()
    )

    if has_critical_error:
        overall_status = "unhealthy"
    elif all_healthy:
        overall_status = "healthy"
    else:
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status, version=settings.app_version, components=components
    )


# Include routers
app.include_router(discovery.router)
app.include_router(query.router)
app.include_router(simulation.router)
app.include_router(ontology.router)
app.include_router(websocket.router)
app.include_router(sensors.router)
app.include_router(trace.router)


# Root redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return {
        "name": "ontEAUlogy Ghent Backend",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
