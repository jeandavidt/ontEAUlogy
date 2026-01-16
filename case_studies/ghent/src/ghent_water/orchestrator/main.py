"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas.models import HealthResponse
from .services.ontology_store import ontology_store
from .services.sparql_engine import sparql_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
        
    except Exception as e:
        logger.warning(f"Failed to load ontology on startup: {e}")
    
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
    redoc_url="/redoc"
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
from .routers import discovery, query, simulation, ontology


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    
    # Check components
    components = {
        "ontology": "healthy" if ontology_store._loaded else "not loaded",
        "sparql_engine": "ready"
    }
    
    overall_status = "healthy" if all(
        v == "healthy" or v == "ready" 
        for v in components.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        components=components
    )


# Include routers
app.include_router(discovery.router)
app.include_router(query.router)
app.include_router(simulation.router)
app.include_router(ontology.router)


# Root redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return {
        "name": "ontEAUlogy Ghent Backend",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }
