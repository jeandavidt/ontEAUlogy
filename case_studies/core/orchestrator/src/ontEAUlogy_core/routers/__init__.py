"""Router exports."""

from .discovery import router as discovery
from .query import router as query
from .simulation import router as simulation
from .ontology import router as ontology
from .websocket import router as websocket
from .sensors import router as sensors
from .trace import router as trace

__all__ = [
    "discovery",
    "query",
    "simulation",
    "ontology",
    "websocket",
    "sensors",
    "trace",
]
