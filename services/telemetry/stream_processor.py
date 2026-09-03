import json
import asyncio
from typing import Dict, List, Any, Set
from datetime import datetime, timezone
from services.telemetry.models import TelemetryPoint
from libraries.common.events import global_event_bus, DomainEvent

TELEMETRY_RING_BUFFER: List[TelemetryPoint] = []
LIVE_SOCKET_CLIENTS: Set[Any] = set()

class TelemetryStreamProcessor:
    def __init__(self):
        self._max_buffer = 10000
        self._subscribe_domain_events()

    def _subscribe_domain_events(self):
        global_event_bus.subscribe("device.command_executed", self._handle_device_event)
        global_event_bus.subscribe("home.mode_changed", self._handle_mode_event)
        global_event_bus.subscribe("security.mode_changed", self._handle_security_event)

    async def broadcast_ws(self, payload: Dict[str, Any]):
        """Broadcasts real-time events to all active WebSocket browser sessions."""
        if not LIVE_SOCKET_CLIENTS:
            return
        msg_text = json.dumps(payload)
        dead = []
        for ws in list(LIVE_SOCKET_CLIENTS):
            try:
                await ws.send_text(msg_text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            LIVE_SOCKET_CLIENTS.discard(ws)

    async def _handle_device_event(self, event: DomainEvent):
        await self.broadcast_ws({
            "type": "DEVICE_STATE_CHANGED",
            "device_id": event.device_id,
            "payload": event.payload,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def _handle_mode_event(self, event: DomainEvent):
        await self.broadcast_ws({
            "type": "HOME_MODE_CHANGED",
            "payload": event.payload,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def _handle_security_event(self, event: DomainEvent):
        await self.broadcast_ws({
            "type": "SECURITY_MODE_CHANGED",
            "payload": event.payload,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def ingest_point(self, point: TelemetryPoint):
        TELEMETRY_RING_BUFFER.append(point)
        if len(TELEMETRY_RING_BUFFER) > self._max_buffer:
            TELEMETRY_RING_BUFFER.pop(0)

        await self.broadcast_ws({
            "type": "TELEMETRY_SAMPLE",
            "device_id": point.device_id,
            "metric": point.metric_name,
            "value": point.value,
            "unit": point.unit
        })

        await global_event_bus.publish(DomainEvent(
            event_type="telemetry.point_ingested",
            source_service="telemetry-service",
            home_id=point.home_id,
            device_id=point.device_id,
            payload={"metric": point.metric_name, "value": point.value, "unit": point.unit}
        ))

    def get_latest_metrics(self, device_id: str, limit: int = 50) -> List[TelemetryPoint]:
        points = [p for p in TELEMETRY_RING_BUFFER if p.device_id == device_id]
        return list(reversed(points[-limit:]))

telemetry_processor = TelemetryStreamProcessor()
