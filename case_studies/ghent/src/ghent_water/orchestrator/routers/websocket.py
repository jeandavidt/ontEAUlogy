"""WebSocket router for real-time sensor data and simulation status broadcasting."""

import json
import logging
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

active_connections: Set[WebSocket] = set()
simulation_connections: Set[WebSocket] = set()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            f"WebSocket connection established. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(
            f"WebSocket connection closed. Total connections: {len(self.active_connections)}"
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all active connections."""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/sensor-data")
async def sensor_data_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time sensor data updates.

    Clients connecting to this endpoint will receive real-time sensor data
    broadcasts as JSON messages.
    """
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                logger.debug(f"Received message from client: {message}")
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from client")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_sensor_data(sensor_data: dict):
    """Broadcast sensor data to all connected WebSocket clients.

    Args:
        sensor_data: Dictionary containing sensor reading information
    """
    await manager.broadcast(sensor_data)


async def broadcast_sensor_readings(readings: list):
    """Broadcast multiple sensor readings to all connected clients.

    Args:
        readings: List of sensor reading dictionaries
    """
    message = {
        "type": "sensor_batch",
        "count": len(readings),
        "readings": readings,
    }
    await manager.broadcast(message)


def get_connection_count() -> int:
    """Get the current number of active WebSocket connections.

    Returns:
        Number of active connections
    """
    return len(manager.active_connections)


class SimulationConnectionManager:
    """Manages active WebSocket connections for simulation status updates."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection for simulation status."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            f"Simulation WebSocket connection established. Total: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(
            f"Simulation WebSocket connection closed. Total: {len(self.active_connections)}"
        )

    async def broadcast(self, message: dict):
        """Broadcast a simulation status message to all connected clients."""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting simulation status: {e}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)


simulation_manager = SimulationConnectionManager()


@router.websocket("/simulation-status")
async def simulation_status_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time simulation status updates.

    Clients connecting to this endpoint will receive real-time simulation
    job status broadcasts as JSON messages.
    """
    await simulation_manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                logger.debug(f"Received simulation status request: {message}")
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from simulation client")

    except WebSocketDisconnect:
        simulation_manager.disconnect(websocket)
        logger.info("Client disconnected from simulation WebSocket")
    except Exception as e:
        logger.error(f"Simulation WebSocket error: {e}")
        simulation_manager.disconnect(websocket)


async def broadcast_simulation_status(status_data: dict):
    """Broadcast simulation status update to all connected WebSocket clients.

    Args:
        status_data: Dictionary containing simulation job status information
    """
    await simulation_manager.broadcast(status_data)


def get_simulation_connection_count() -> int:
    """Get the current number of active simulation WebSocket connections.

    Returns:
        Number of active connections
    """
    return len(simulation_manager.active_connections)
