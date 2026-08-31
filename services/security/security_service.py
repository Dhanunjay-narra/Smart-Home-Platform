from typing import Dict, Any, List
from services.security.models import SecurityMode, CameraFeed
from libraries.common.events import global_event_bus, DomainEvent

CAMERAS_DB: Dict[str, CameraFeed] = {}

class SecurityService:
    def __init__(self):
        self.current_security_mode = SecurityMode.DISARMED
        self._seed_cameras()

    def _seed_cameras(self):
        if not CAMERAS_DB:
            c1 = CameraFeed(
                camera_id="cam-front-door",
                name="Front Door 4K HDR",
                location="Front Porch",
                stream_url="/static/streams/front_door.m3u8",
                thumbnail_url="https://images.unsplash.com/photo-1558002038-1055907df827?w=600&auto=format&fit=crop&q=60",
                ai_detection_labels=["Person: Dhanunjay", "Package Delivered"]
            )
            c2 = CameraFeed(
                camera_id="cam-garage-int",
                name="Garage Interior & EV",
                location="Smart Garage",
                stream_url="/static/streams/garage.m3u8",
                thumbnail_url="https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=600&auto=format&fit=crop&q=60",
                ai_detection_labels=["Vehicle: Tesla Model 3"]
            )
            CAMERAS_DB[c1.camera_id] = c1
            CAMERAS_DB[c2.camera_id] = c2

    async def arm_security(self, mode: SecurityMode, actor: str = "User") -> SecurityMode:
        self.current_security_mode = mode
        await global_event_bus.publish(DomainEvent(
            event_type="security.mode_changed",
            source_service="security-service",
            payload={"mode": mode.value, "actor": actor}
        ))
        return self.current_security_mode

security_service = SecurityService()
