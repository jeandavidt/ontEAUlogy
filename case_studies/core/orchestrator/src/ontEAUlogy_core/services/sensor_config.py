"""Sensor configuration system for Ghent water system.

This module defines sensor types, parameters, and locations for the
synthetic sensor data generation system.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SensorLocation:
    """Represents a sensor location with entity and port information."""

    sensor_id: str
    entity: str
    port: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class SensorParameter:
    """Represents a measurable sensor parameter with base values and units."""

    parameter_name: str
    base_value: float
    unit: str
    variance: float = 0.1
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    regulatory_limit: Optional[float] = None


@dataclass
class SensorType:
    """Represents a sensor type with its parameters and locations."""

    sensor_type: str
    sensor_class: str
    parameters: Dict[str, SensorParameter]
    locations: Dict[str, SensorLocation]
    sampling_rate: float = 1.0


# Water Quality Sensor Configuration
WATER_QUALITY_PARAMETERS = {
    "Turbidity": SensorParameter(
        parameter_name="Turbidity",
        base_value=0.5,
        unit="NTU",
        variance=0.2,
        min_value=0.0,
        max_value=5.0,
        regulatory_limit=1.0,
    ),
    "Chlorine": SensorParameter(
        parameter_name="Chlorine",
        base_value=0.4,
        unit="mg/L",
        variance=0.1,
        min_value=0.1,
        max_value=1.0,
        regulatory_limit=0.5,
    ),
    "pH": SensorParameter(
        parameter_name="pH",
        base_value=7.2,
        unit="pH",
        variance=0.2,
        min_value=6.5,
        max_value=8.5,
        regulatory_limit=None,
    ),
    "BOD": SensorParameter(
        parameter_name="BOD",
        base_value=15.0,
        unit="mg/L",
        variance=5.0,
        min_value=0.0,
        max_value=50.0,
        regulatory_limit=25.0,
    ),
    "COD": SensorParameter(
        parameter_name="COD",
        base_value=75.0,
        unit="mg/L",
        variance=15.0,
        min_value=0.0,
        max_value=250.0,
        regulatory_limit=125.0,
    ),
    "TSS": SensorParameter(
        parameter_name="TSS",
        base_value=20.0,
        unit="mg/L",
        variance=5.0,
        min_value=0.0,
        max_value=100.0,
        regulatory_limit=35.0,
    ),
    "NH4": SensorParameter(
        parameter_name="NH4",
        base_value=8.0,
        unit="mg/L",
        variance=2.0,
        min_value=0.0,
        max_value=30.0,
        regulatory_limit=10.0,
    ),
    "DO": SensorParameter(
        parameter_name="DO",
        base_value=6.5,
        unit="mg/L",
        variance=1.0,
        min_value=0.0,
        max_value=12.0,
        regulatory_limit=5.0,
    ),
    "Temperature": SensorParameter(
        parameter_name="Temperature",
        base_value=20.0,
        unit="°C",
        variance=2.0,
        min_value=5.0,
        max_value=35.0,
        regulatory_limit=None,
    ),
}

# Flow Sensor Configuration
FLOW_PARAMETERS = {
    "FlowRate": SensorParameter(
        parameter_name="FlowRate",
        base_value=100.0,
        unit="m3/h",
        variance=10.0,
        min_value=0.0,
        max_value=500.0,
        regulatory_limit=None,
    ),
}

# Weather Sensor Configuration
WEATHER_PARAMETERS = {
    "AirTemperature": SensorParameter(
        parameter_name="AirTemperature",
        base_value=15.0,
        unit="°C",
        variance=3.0,
        min_value=-10.0,
        max_value=40.0,
        regulatory_limit=None,
    ),
    "Precipitation": SensorParameter(
        parameter_name="Precipitation",
        base_value=0.0,
        unit="mm",
        variance=1.0,
        min_value=0.0,
        max_value=50.0,
        regulatory_limit=None,
    ),
}

# Water Quality Sensor Locations
WATER_QUALITY_LOCATIONS = {
    "DWP1_Outlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="DWP1_Outlet_WaterQuality_Sensor",
        entity="dwp1",
        port="DWP1_PotableWater_Out",
        lat=51.064,
        lon=3.695,
    ),
    "DWP1_Inlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="DWP1_Inlet_WaterQuality_Sensor",
        entity="dwp1",
        port="DWP1_RawWater_In",
        lat=51.064,
        lon=3.693,
    ),
    "DWP2_Outlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="DWP2_Outlet_WaterQuality_Sensor",
        entity="dwp2",
        port="DWP2_PotableWater_Out",
        lat=51.049,
        lon=3.725,
    ),
    "DWP2_Inlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="DWP2_Inlet_WaterQuality_Sensor",
        entity="dwp2",
        port="DWP2_RawWater_In",
        lat=51.049,
        lon=3.723,
    ),
    "WWTP1_Outlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="WWTP1_Outlet_WaterQuality_Sensor",
        entity="wwtp1",
        port="WWTP1_Effluent_Out",
        lat=51.062,
        lon=3.700,
    ),
    "WWTP1_Inlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="WWTP1_Inlet_WaterQuality_Sensor",
        entity="wwtp1",
        port="WWTP1_Influent_In",
        lat=51.061,
        lon=3.699,
    ),
    "WWTP2_Outlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="WWTP2_Outlet_WaterQuality_Sensor",
        entity="wwtp2",
        port="WWTP2_Effluent_Out",
        lat=51.047,
        lon=3.730,
    ),
    "WWTP2_Inlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="WWTP2_Inlet_WaterQuality_Sensor",
        entity="wwtp2",
        port="WWTP2_Influent_In",
        lat=51.046,
        lon=3.729,
    ),
    "Texfin_Outlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="Texfin_Outlet_WaterQuality_Sensor",
        entity="texfin",
        port="Texfin_Wastewater_Out",
        lat=51.066,
        lon=3.692,
    ),
    "FoodPro_Outlet_WaterQuality_Sensor": SensorLocation(
        sensor_id="FoodPro_Outlet_WaterQuality_Sensor",
        entity="foodpro",
        port="FoodPro_Wastewater_Out",
        lat=51.062,
        lon=3.698,
    ),
    "LieveSegment1_In_Flow_Sensor": SensorLocation(
        sensor_id="LieveSegment1_In_Flow_Sensor",
        entity="lieve",
        port="LieveSegment1_In",
        lat=51.068,
        lon=3.688,
    ),
    "LieveSegment1_WaterQuality_Sensor": SensorLocation(
        sensor_id="LieveSegment1_WaterQuality_Sensor",
        entity="lieve",
        port="LieveSegment1",
        lat=51.068,
        lon=3.688,
    ),
    "LieveSegment2_WaterQuality_Sensor": SensorLocation(
        sensor_id="LieveSegment2_WaterQuality_Sensor",
        entity="lieve",
        port="LieveSegment2",
        lat=51.055,
        lon=3.710,
    ),
    "LieveSegment3_WaterQuality_Sensor": SensorLocation(
        sensor_id="LieveSegment3_WaterQuality_Sensor",
        entity="lieve",
        port="LieveSegment3",
        lat=51.042,
        lon=3.732,
    ),
}

# Flow Sensor Locations
FLOW_LOCATIONS = {
    "DWP1_Inlet_Flow_Sensor": SensorLocation(
        sensor_id="DWP1_Inlet_Flow_Sensor",
        entity="dwp1",
        port="DWP1_RawWater_In",
        lat=51.064,
        lon=3.693,
    ),
    "DWP2_Inlet_Flow_Sensor": SensorLocation(
        sensor_id="DWP2_Inlet_Flow_Sensor",
        entity="dwp2",
        port="DWP2_RawWater_In",
        lat=51.049,
        lon=3.723,
    ),
    "WWTP1_Inlet_Flow_Sensor": SensorLocation(
        sensor_id="WWTP1_Inlet_Flow_Sensor",
        entity="wwtp1",
        port="WWTP1_Influent_In",
        lat=51.061,
        lon=3.699,
    ),
    "WWTP2_Inlet_Flow_Sensor": SensorLocation(
        sensor_id="WWTP2_Inlet_Flow_Sensor",
        entity="wwtp2",
        port="WWTP2_Influent_In",
        lat=51.046,
        lon=3.729,
    ),
}

# Weather Sensor Locations
WEATHER_LOCATIONS = {
    "Ghent_Weather_Station_Sensor": SensorLocation(
        sensor_id="Ghent_Weather_Station_Sensor", entity="weather", port=None, lat=51.057, lon=3.713
    ),
}

# Complete sensor configuration
SENSOR_CONFIGS = {
    "water_quality": SensorType(
        sensor_type="water_quality",
        sensor_class="WaterQualitySensor",
        parameters=WATER_QUALITY_PARAMETERS,
        locations=WATER_QUALITY_LOCATIONS,
        sampling_rate=1.0,
    ),
    "flow": SensorType(
        sensor_type="flow",
        sensor_class="FlowSensor",
        parameters=FLOW_PARAMETERS,
        locations=FLOW_LOCATIONS,
        sampling_rate=1.0,
    ),
    "weather": SensorType(
        sensor_type="weather",
        sensor_class="WeatherSensor",
        parameters=WEATHER_PARAMETERS,
        locations=WEATHER_LOCATIONS,
        sampling_rate=1.0,
    ),
}


def get_sensor_config(sensor_type: str) -> Optional[SensorType]:
    """Get sensor configuration by type."""
    return SENSOR_CONFIGS.get(sensor_type)


def get_all_sensors() -> Dict[str, Dict]:
    """Get all sensors with their configured parameters."""
    all_sensors = {}

    for sensor_type, sensor_config in SENSOR_CONFIGS.items():
        for sensor_id, location in sensor_config.locations.items():
            all_sensors[sensor_id] = {
                "sensor_type": sensor_type,
                "sensor_class": sensor_config.sensor_class,
                "sensor_id": sensor_id,
                "entity": location.entity,
                "port": location.port,
                "lat": location.lat,
                "lon": location.lon,
                "parameters": list(sensor_config.parameters.keys()),
                "sampling_rate": sensor_config.sampling_rate,
            }

    return all_sensors


def get_sensor_parameters(sensor_type: str, location_id: str) -> List[str]:
    """Get parameters for a specific sensor.

    Args:
        sensor_type: Type of sensor (water_quality, flow, weather)
        location_id: Location identifier

    Returns:
        List of parameter names
    """
    config = get_sensor_config(sensor_type)
    if config and location_id in config.locations:
        return list(config.parameters.keys())
    return []


def get_parameter_info(
    sensor_type: str, parameter_name: str
) -> Optional[SensorParameter]:
    """Get parameter information.

    Args:
        sensor_type: Type of sensor
        parameter_name: Name of parameter

    Returns:
        SensorParameter or None if not found
    """
    config = get_sensor_config(sensor_type)
    if config:
        return config.parameters.get(parameter_name)
    return None
