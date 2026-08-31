from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class CapabilityType(str, Enum):
    POWER = "power"
    BRIGHTNESS = "brightness"
    COLOR_RGB = "color_rgb"
    COLOR_TEMP = "color_temp"
    TEMPERATURE_SETPOINT = "temperature_setpoint"
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    MOTION_DETECTOR = "motion_detector"
    PRESENCE_DETECTOR = "presence_detector"
    DOOR_LOCK = "door_lock"
    GARAGE_DOOR = "garage_door"
    VALVE_CONTROL = "valve_control"
    ENERGY_MONITOR = "energy_monitor"
    SOLAR_INVERTER = "solar_inverter"
    BATTERY_STORAGE = "battery_storage"
    EV_CHARGER = "ev_charger"

class Capability(BaseModel):
    type: CapabilityType
    name: str
    unit: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    read_only: bool = False
    current_value: Any = None

class DeviceCategory(str, Enum):
    LIGHTING = "lighting"
    CLIMATE = "climate"
    SECURITY = "security"
    ENERGY = "energy"
    APPLIANCE = "appliance"
    SENSOR = "sensor"
    ACCESS = "access"
    ROBOTICS = "robotics"
