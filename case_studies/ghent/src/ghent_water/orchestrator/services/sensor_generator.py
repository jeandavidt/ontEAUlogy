"""Sensor data generation service for creating realistic synthetic sensor readings.

This module generates synthetic sensor data with configurable variance,
diurnal cycles, and optional anomaly injection.
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

np = None
NUMPY_AVAILABLE = False
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    pass

from .sensor_config import (
    get_all_sensors,
    get_sensor_config,
    get_parameter_info,
)

logger = logging.getLogger(__name__)


class SensorReading:
    """Represents a single sensor reading."""

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        parameter: str,
        value: float,
        unit: str,
        timestamp: datetime,
        location: Dict[str, Optional[float]],
        feature_of_interest: Optional[str] = None,
    ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.parameter = parameter
        self.value = value
        self.unit = unit
        self.timestamp = timestamp
        self.location = location
        self.feature_of_interest = feature_of_interest

    def to_dict(self) -> Dict:
        """Convert reading to dictionary format."""
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "parameter": self.parameter,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat() + "Z",
            "location": self.location,
            "feature_of_interest": self.feature_of_interest,
        }


class SensorDataGenerator:
    """Generates realistic synthetic sensor data."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize the sensor data generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
            if NUMPY_AVAILABLE and np is not None:
                np.random.seed(seed)

        self._sensor_values = {}
        self._initialize_sensor_states()

    def _initialize_sensor_states(self):
        """Initialize internal state for all sensors."""
        sensors = get_all_sensors()

        for sensor_key, sensor_info in sensors.items():
            sensor_config = get_sensor_config(sensor_info["sensor_type"])
            if not sensor_config:
                continue

            self._sensor_values[sensor_key] = {}
            for param in sensor_info["parameters"]:
                param_info = get_parameter_info(sensor_info["sensor_type"], param)
                if param_info:
                    self._sensor_values[sensor_key][param] = param_info.base_value

    def _add_variance(self, base_value: float, variance_pct: float) -> float:
        """Add random variance to a base value.

        Args:
            base_value: Base value
            variance_pct: Percentage variance (e.g., 0.1 for 10%)

        Returns:
            Value with variance applied
        """
        if NUMPY_AVAILABLE and np is not None:
            variance = base_value * variance_pct * np.random.randn()
        else:
            variance = base_value * variance_pct * random.gauss(0, 1)

        return base_value + variance

    def _add_diurnal_trend(
        self, value: float, hour: int, amplitude: float = 0.1
    ) -> float:
        """Add diurnal (24-hour) cycle trend to value.

        Args:
            value: Base value
            hour: Hour of day (0-23)
            amplitude: Amplitude of diurnal cycle as percentage

        Returns:
            Value with diurnal trend applied
        """
        diurnal_factor = math.sin((hour - 6) * math.pi / 12)
        return value * (1 + amplitude * diurnal_factor)

    def _clamp_value(
        self, value: float, min_value: Optional[float], max_value: Optional[float]
    ) -> float:
        """Clamp value within specified bounds.

        Args:
            value: Value to clamp
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            Clamped value
        """
        if min_value is not None:
            value = max(min_value, value)
        if max_value is not None:
            value = min(max_value, value)
        return value

    def _generate_parameter_value(
        self,
        sensor_key: str,
        parameter: str,
        timestamp: datetime,
    ) -> float:
        """Generate a realistic value for a specific sensor parameter.

        Args:
            sensor_key: Unique sensor identifier
            parameter: Parameter name
            timestamp: Timestamp for the reading

        Returns:
            Generated sensor value
        """
        # Get sensor info to get the correct sensor type
        sensors = get_all_sensors()
        sensor_info = sensors.get(sensor_key)
        
        if not sensor_info:
            logger.warning(f"Sensor not found: {sensor_key}")
            return 0.0
        
        sensor_type = sensor_info.get("sensor_type", "water_quality")
        param_info = get_parameter_info(sensor_type, parameter)

        if not param_info:
            logger.warning(f"Parameter info not found: {sensor_type}/{parameter}")
            return 0.0

        previous_value = self._sensor_values.get(sensor_key, {}).get(
            parameter, param_info.base_value
        )

        generated_value = self._add_variance(param_info.base_value, param_info.variance)

        generated_value = self._add_diurnal_trend(
            generated_value, timestamp.hour, amplitude=0.05
        )

        generated_value = self._clamp_value(
            generated_value, param_info.min_value, param_info.max_value
        )

        self._sensor_values.setdefault(sensor_key, {})[parameter] = generated_value

        return generated_value

    def generate_reading(
        self,
        sensor_key: str,
        parameter: str,
        timestamp: Optional[datetime] = None,
    ) -> Optional[SensorReading]:
        """Generate a single sensor reading.

        Args:
            sensor_key: Unique sensor identifier (e.g., "dwp1_outlet_water_quality")
            parameter: Parameter to generate reading for
            timestamp: Optional timestamp (defaults to now)

        Returns:
            SensorReading or None if sensor not found
        """
        sensors = get_all_sensors()
        sensor_info = sensors.get(sensor_key)

        if not sensor_info:
            logger.warning(f"Sensor not found: {sensor_key}")
            return None

        if timestamp is None:
            timestamp = datetime.utcnow()

        sensor_type = sensor_info["sensor_type"]
        param_info = get_parameter_info(sensor_type, parameter)

        if not param_info:
            logger.warning(f"Parameter not found: {sensor_type}/{parameter}")
            return None

        value = self._generate_parameter_value(sensor_key, parameter, timestamp)

        location = {
            "lat": sensor_info.get("lat"),
            "lon": sensor_info.get("lon"),
        }

        feature_of_interest = None
        if sensor_info.get("port"):
            feature_of_interest = f"ghent:{sensor_info['port']}"

        return SensorReading(
            sensor_id=sensor_info["sensor_id"],
            sensor_type=sensor_type,
            parameter=parameter,
            value=round(value, 3),
            unit=param_info.unit,
            timestamp=timestamp,
            location=location,
            feature_of_interest=feature_of_interest,
        )

    def generate_sensor_readings(
        self,
        sensor_key: str,
        timestamp: Optional[datetime] = None,
    ) -> List[SensorReading]:
        """Generate readings for all parameters of a specific sensor.

        Args:
            sensor_key: Unique sensor identifier
            timestamp: Optional timestamp (defaults to now)

        Returns:
            List of SensorReading objects
        """
        sensors = get_all_sensors()
        sensor_info = sensors.get(sensor_key)

        if not sensor_info:
            logger.warning(f"Sensor not found: {sensor_key}")
            return []

        readings = []
        for parameter in sensor_info["parameters"]:
            reading = self.generate_reading(sensor_key, parameter, timestamp)
            if reading:
                readings.append(reading)

        return readings

    def generate_all_readings(
        self,
        timestamp: Optional[datetime] = None,
        sensor_type_filter: Optional[str] = None,
    ) -> List[SensorReading]:
        """Generate readings for all sensors or filtered by type.

        Args:
            timestamp: Optional timestamp (defaults to now)
            sensor_type_filter: Optional filter by sensor type (water_quality, flow, weather)

        Returns:
            List of all generated SensorReading objects
        """
        sensors = get_all_sensors()
        all_readings = []

        for sensor_key, sensor_info in sensors.items():
            if sensor_type_filter and sensor_info["sensor_type"] != sensor_type_filter:
                continue

            sensor_readings = self.generate_sensor_readings(sensor_key, timestamp)
            all_readings.extend(sensor_readings)

        return all_readings


import math


_global_generator: Optional[SensorDataGenerator] = None


def get_generator() -> SensorDataGenerator:
    """Get or create the global sensor data generator.

    Returns:
        SensorDataGenerator instance
    """
    global _global_generator
    if _global_generator is None:
        _global_generator = SensorDataGenerator()
        logger.info("Sensor data generator initialized")
    return _global_generator
