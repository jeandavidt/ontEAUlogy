"""Sensor data ingestion router for receiving and processing sensor readings."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

from ..services.ontology_store import ontology_store
from ..services.sensor_config import (
    get_all_sensors,
    get_sensor_config,
    get_parameter_info,
)
from ..services.sensor_generator import get_generator
from ..routers.websocket import broadcast_sensor_data, broadcast_sensor_readings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sensors", tags=["Sensors"])


class SensorReading(BaseModel):
    """Individual sensor reading."""

    parameter: str = Field(..., description="Parameter name (e.g., BOD, pH)")
    value: float = Field(..., description="Sensor reading value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Reading timestamp (defaults to now)",
    )


class SensorDataRequest(BaseModel):
    """Request for submitting sensor data."""

    sensor_id: str = Field(..., description="Sensor identifier")
    readings: List[SensorReading] = Field(
        ...,
        description="List of sensor readings",
    )


class SensorListResponse(BaseModel):
    """Response with list of all configured sensors."""

    sensors: dict


class SensorGenerationRequest(BaseModel):
    """Request to generate synthetic sensor data."""

    sensor_type: Optional[str] = Field(
        None,
        description="Filter by sensor type (water_quality, flow, weather)",
    )


class SensorGenerationResponse(BaseModel):
    """Response with generated sensor data."""

    count: int
    readings: List[dict]


def _create_sosa_observation_triples(
    sensor_id: str,
    parameter: str,
    value: float,
    unit: str,
    timestamp: datetime,
    feature_of_interest: Optional[str],
) -> str:
    """Create SOSA-compliant RDF triples for an observation.

    Args:
        sensor_id: Sensor identifier
        parameter: Parameter name
        value: Observation value
        unit: Unit of measurement
        timestamp: Reading timestamp
        feature_of_interest: Feature of interest URI

    Returns:
        Turtle-formatted RDF triples
    """
    sensor_uri = f"ghent:{sensor_id}"
    obs_id = f"Reading_{sensor_id}_{parameter}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    obs_uri = f"ghent:{obs_id}"

    param_uri = f"wf:{parameter}"
    unit_uri = f"unit:{unit}" if unit.startswith("unit:") else None

    timestamp_iso = timestamp.strftime("%Y-%m-%dT%H:%M:%S")

    triples = f"""{obs_uri} a wf:WaterQualityObservation, sosa:Observation ;
    rdfs:label "{obs_id}" ;
    sosa:madeBySensor {sensor_uri} ;
    sosa:observedProperty {param_uri} ;
    sosa:hasResult "{value}"^^xsd:double ;
    sosa:resultTime "{timestamp_iso}"^^xsd:dateTime ."""

    if feature_of_interest:
        triples += f"\n{obs_uri} sosa:hasFeatureOfInterest {feature_of_interest} ."

    return triples


@router.get("/", response_model=SensorListResponse)
async def list_sensors():
    """Get list of all configured sensors."""
    sensors = get_all_sensors()
    return SensorListResponse(sensors=sensors)


@router.get("/types")
async def list_sensor_types():
    """Get list of available sensor types."""
    config = {
        "types": ["water_quality", "flow", "weather"],
        "descriptions": {
            "water_quality": "Multi-parameter water quality sensors",
            "flow": "Flow rate sensors",
            "weather": "Weather monitoring sensors",
        },
    }
    return config


@router.post("/data")
async def submit_sensor_data(
    request: SensorDataRequest, background_tasks: BackgroundTasks
):
    """Submit sensor data for processing and storage.

    This endpoint:
    1. Validates the sensor ID and parameters
    2. Creates SOSA-compliant RDF triples for each reading
    3. Adds the observations to the ontology store
    4. Broadcasts the data via WebSocket to connected clients
    """
    sensors = get_all_sensors()
    sensor_info = None

    for sensor_key, info in sensors.items():
        if info["sensor_id"] == request.sensor_id:
            sensor_info = info
            break

    if not sensor_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor not found: {request.sensor_id}",
        )

    processed_readings = []

    for reading in request.readings:
        sensor_config = get_sensor_config(sensor_info["sensor_type"])
        if not sensor_config or reading.parameter not in sensor_config.parameters:
            logger.warning(
                f"Parameter {reading.parameter} not found for sensor {request.sensor_id}"
            )
            continue

        param_info = get_parameter_info(sensor_info["sensor_type"], reading.parameter)
        if not param_info:
            continue

        feature_of_interest = None
        if sensor_info.get("port"):
            feature_of_interest = f"ghent:{sensor_info['port']}"

        triples = _create_sosa_observation_triples(
            sensor_id=request.sensor_id,
            parameter=reading.parameter,
            value=reading.value,
            unit=reading.unit,
            timestamp=reading.timestamp,
            feature_of_interest=feature_of_interest,
        )

        try:
            ontology_store.add_triples(triples)
            logger.info(
                f"Added observation triples for {request.sensor_id}/{reading.parameter}"
            )
        except Exception as e:
            logger.error(f"Error adding triples: {e}")

        reading_data = {
            "sensor_id": request.sensor_id,
            "sensor_type": sensor_info["sensor_type"],
            "parameter": reading.parameter,
            "value": reading.value,
            "unit": reading.unit,
            "timestamp": reading.timestamp.isoformat() + "Z",
            "location": {
                "lat": sensor_info.get("lat"),
                "lon": sensor_info.get("lon"),
            },
            "feature_of_interest": feature_of_interest,
        }
        processed_readings.append(reading_data)

    if processed_readings:
        background_tasks.add_task(broadcast_sensor_readings, processed_readings)

    return {
        "message": f"Processed {len(processed_readings)} reading(s)",
        "processed_count": len(processed_readings),
    }


@router.post("/generate", response_model=SensorGenerationResponse)
async def generate_sensor_data(request: SensorGenerationRequest):
    """Generate synthetic sensor data for testing.

    This endpoint generates realistic synthetic sensor data with variance
    and diurnal patterns for all sensors or filtered by type.
    """
    generator = get_generator()
    timestamp = datetime.utcnow()

    readings = generator.generate_all_readings(
        timestamp=timestamp,
        sensor_type_filter=request.sensor_type,
    )

    reading_dicts = [reading.to_dict() for reading in readings]

    return SensorGenerationResponse(
        count=len(reading_dicts),
        readings=reading_dicts,
    )


@router.post("/generate-and-broadcast")
async def generate_and_broadcast_data(
    request: SensorGenerationRequest,
    background_tasks: BackgroundTasks,
):
    """Generate and broadcast synthetic sensor data.

    This is a convenience endpoint that generates data and immediately
    broadcasts it to WebSocket clients.
    """
    generator = get_generator()
    timestamp = datetime.utcnow()

    readings = generator.generate_all_readings(
        timestamp=timestamp,
        sensor_type_filter=request.sensor_type,
    )

    reading_dicts = [reading.to_dict() for reading in readings]

    if reading_dicts:
        background_tasks.add_task(broadcast_sensor_readings, reading_dicts)

    return {
        "message": f"Generated and broadcast {len(reading_dicts)} reading(s)",
        "count": len(reading_dicts),
    }


class HistoricalDataResponse(BaseModel):
    """Response with historical sensor data."""
    
    sensor_data: Dict[str, Dict]
    count: int


@router.get("/historical", response_model=HistoricalDataResponse)
async def get_historical_sensor_data(
    num_points: int = 25,
):
    """Get pre-populated historical sensor data.
    
    This endpoint generates historical sensor data for all sensors,
    useful for pre-populating the frontend with initial data.
    
    Args:
        num_points: Number of historical data points to generate per sensor (default: 25)
    
    Returns:
        Dictionary mapping sensor_id to sensor data with history
    """
    from ..services.sensor_config import get_all_sensors
    
    generator = get_generator()
    now = datetime.utcnow()
    sensors = get_all_sensors()
    
    sensor_data: Dict[str, Dict] = {}
    
    for sensor_key in generator._sensor_values.keys():
        # Get the actual sensor type from the config
        sensor_full_info = sensors.get(sensor_key, {})
        sensor_type = sensor_full_info.get("sensor_type", "water_quality")
        
        sensor_info = {
            "sensor_id": sensor_key,
            "sensor_type": sensor_type,
            "parameters": {},
            "current_readings": {},
            "history": [],
        }
        
        # Generate historical readings
        for i in range(num_points):
            timestamp = now - timedelta(seconds=num_points - i)
            readings = generator.generate_sensor_readings(sensor_key, timestamp)
            
            for reading in readings:
                param = reading.parameter
                # Update parameter info
                if param not in sensor_info["parameters"]:
                    sensor_info["parameters"][param] = {"unit": reading.unit}
                
                # Add to history
                history_entry: Dict = {"timestamp": reading.timestamp.isoformat() + "Z"}
                history_entry[param] = reading.value
                
                # Merge with existing history entries that share the same timestamp
                timestamp_found = False
                for entry in sensor_info["history"]:
                    if entry.get("timestamp") == reading.timestamp.isoformat() + "Z":
                        entry[param] = reading.value
                        timestamp_found = True
                        break
                
                if not timestamp_found:
                    sensor_info["history"].append(history_entry)
                
                # Update current reading (will be the last one)
                sensor_info["current_readings"][param] = reading.value
        
        sensor_data[sensor_key] = sensor_info
    
    return HistoricalDataResponse(
        sensor_data=sensor_data,
        count=len(sensor_data),
    )
