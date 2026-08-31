from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
from datetime import datetime, timezone
from services.device.capabilities import Capability, DeviceCategory

class ProtocolType(str, Enum):
    WIFI = "wifi"
    ZIGBEE = "zigbee"
    BLE = "ble"
    THREAD_MATTER = "matter"
    MQTT = "mqtt"
    MODBUS = "modbus"
    CAN = "can"

class DeviceStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"

class Device(BaseModel):
    device_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: DeviceCategory
    protocol: ProtocolType = ProtocolType.WIFI
    room_id: str
    home_id: str
    status: DeviceStatus = DeviceStatus.ONLINE
    firmware_version: str = "v2.4.0"
    capabilities: List[Capability] = Field(default_factory=list)
    state: Dict[str, Any] = Field(default_factory=dict)
    health_score: float = 98.5
    battery_level: Optional[int] = None
    rssi: int = -52
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
