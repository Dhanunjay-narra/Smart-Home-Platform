from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
from datetime import datetime, timezone

class HomeMode(str, Enum):
    HOME = "HOME"
    AWAY = "AWAY"
    SLEEP = "SLEEP"
    VACATION = "VACATION"
    GUEST = "GUEST"
    EMERGENCY = "EMERGENCY"
    CUSTOM = "CUSTOM"

class ZoneType(str, Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    PERIMETER = "perimeter"
    GARAGE = "garage"
    GARDEN = "garden"
    POOL = "pool"
    UTILITY = "utility"

class Room(BaseModel):
    room_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    floor_id: str
    zone_type: ZoneType = ZoneType.INDOOR
    icon: str = "door-open"
    device_ids: List[str] = Field(default_factory=list)
    target_temperature_c: float = 22.0
    is_occupied: bool = False

class Floor(BaseModel):
    floor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    level: int = 0
    building_id: str
    rooms: List[Room] = Field(default_factory=list)

class Building(BaseModel):
    building_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    home_id: str
    floors: List[Floor] = Field(default_factory=list)

class Geofence(BaseModel):
    latitude: float
    longitude: float
    radius_meters: float = 250.0

class Home(BaseModel):
    home_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    timezone: str = "Asia/Kolkata"
    current_mode: HomeMode = HomeMode.HOME
    security_armed: bool = False
    geofence: Geofence = Field(default_factory=lambda: Geofence(latitude=17.385044, longitude=78.486671))
    buildings: List[Building] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
