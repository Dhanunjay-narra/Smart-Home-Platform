import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def write_f(rel_path, content):
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def generate_rich_domain_ecosystem():
    print("Generating simulations, notifications, firmware OTA, and rich domain schemas...")

    # 1. Services/Notification
    write_f("services/notification/__init__.py", '"""Multi-Channel Notification Dispatcher"""')
    write_f("services/notification/models.py", """
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
import uuid

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"

class NotificationPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"

class NotificationMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_user_id: str
    home_id: Optional[str] = None
    title: str
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.IN_APP])
    data_payload: Dict[str, Any] = Field(default_factory=dict)
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
""")

    write_f("services/notification/dispatcher.py", """
from typing import Dict, Any, List
from services.notification.models import NotificationMessage, NotificationChannel, NotificationPriority
from libraries.common.events import global_event_bus, DomainEvent

NOTIFICATIONS_DB: List[NotificationMessage] = []

class NotificationDispatcher:
    def __init__(self):
        global_event_bus.subscribe("security.alarm_triggered", self._handle_security_alert)
        global_event_bus.subscribe("home.mode_changed", self._handle_mode_alert)

    async def _handle_security_alert(self, event: DomainEvent):
        msg = NotificationMessage(
            recipient_user_id="usr-admin-001",
            home_id=event.home_id,
            title="SECURITY ALERT",
            body=event.payload.get("description", "Security incident detected!"),
            priority=NotificationPriority.EMERGENCY,
            channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH, NotificationChannel.SMS]
        )
        NOTIFICATIONS_DB.append(msg)

    async def _handle_mode_alert(self, event: DomainEvent):
        msg = NotificationMessage(
            recipient_user_id="usr-admin-001",
            home_id=event.home_id,
            title="Home Mode Updated",
            body=f"Home mode changed to {event.payload.get('new_mode')} by {event.payload.get('actor')}",
            priority=NotificationPriority.NORMAL,
            channels=[NotificationChannel.IN_APP]
        )
        NOTIFICATIONS_DB.append(msg)

    def list_notifications(self, user_id: str, limit: int = 50) -> List[NotificationMessage]:
        return list(reversed(NOTIFICATIONS_DB[-limit:]))

notification_dispatcher = NotificationDispatcher()
""")

    # 2. Services/Firmware OTA
    write_f("services/firmware/__init__.py", '"""OTA Firmware Management & Staged Deployment"""')
    write_f("services/firmware/models.py", """
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class FirmwareRelease(BaseModel):
    release_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_hardware: str = "ESP32-S3"
    version_tag: str = "v2.4.0"
    file_size_bytes: int = 1428570
    sha256_checksum: str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    release_notes: str = "Enhanced Matter commissioning and low-power BLE mesh optimization."
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
""")

    write_f("services/firmware/ota_service.py", """
from typing import Dict, Any, List, Optional
from services.firmware.models import FirmwareRelease

FIRMWARE_RELEASES_DB: Dict[str, FirmwareRelease] = {}

class OTAService:
    def __init__(self):
        self._seed_default_release()

    def _seed_default_release(self):
        if not FIRMWARE_RELEASES_DB:
            rel = FirmwareRelease(
                release_id="rel-v240-esp32",
                target_hardware="ESP32-S3",
                version_tag="v2.4.0",
                file_size_bytes=1048576,
                sha256_checksum="4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
            )
            FIRMWARE_RELEASES_DB[rel.release_id] = rel

    def get_latest_release(self, hardware_model: str) -> Optional[FirmwareRelease]:
        matches = [r for r in FIRMWARE_RELEASES_DB.values() if r.target_hardware.lower() in hardware_model.lower()]
        return matches[-1] if matches else None

ota_service = OTAService()
""")

    # 3. Simulations / Hardware-in-the-Loop Testbed (30 Simulated Sensor Data Feeds)
    for sim_idx in range(1, 31):
        sim_name = f"sim_sensor_node_{sim_idx:02d}"
        write_f(f"simulations/{sim_name}.py", f"""
\"\"\"
Hardware Simulation Node: {sim_name}
Generates synthetic real-time telemetry for multi-sensor IoT test environments.
\"\"\"

import random
import math
import time
from typing import Dict, Any
from datetime import datetime, timezone

class SimulationNode_{sim_idx:02d}:
    def __init__(self, node_id: str = "{sim_name}"):
        self.node_id = node_id
        self.base_frequency = {0.5 + (sim_idx * 0.1):.2f}
        self.iteration = 0

    def generate_synthetic_telemetry(self) -> Dict[str, Any]:
        self.iteration += 1
        t = time.time()
        # Sine-wave synthetic model with Gaussian noise
        primary_val = 20.0 + 10.0 * math.sin(t * self.base_frequency) + random.gauss(0, 0.2)
        secondary_val = 50.0 + 20.0 * math.cos(t * self.base_frequency * 0.5) + random.gauss(0, 0.5)
        
        return {{
            "node_id": self.node_id,
            "sample_index": self.iteration,
            "primary_metric": round(primary_val, 3),
            "secondary_metric": round(secondary_val, 3),
            "signal_rssi_dbm": random.randint(-65, -45),
            "battery_mv": random.randint(3200, 3300),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }}

sim_node_{sim_idx:02d} = SimulationNode_{sim_idx:02d}()
""")

    print("Simulations and extended domain services generated.")

if __name__ == "__main__":
    generate_rich_domain_ecosystem()
