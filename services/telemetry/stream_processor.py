from typing import Dict, List, Any
from datetime import datetime, timezone
from services.telemetry.models import TelemetryPoint
from libraries.common.events import global_event_bus, DomainEvent

TELEMETRY_RING_BUFFER: List[TelemetryPoint] = []
LIVE_SOCKET_CLIENTS = set()

class TelemetryStreamProcessor:
    def __init__(self):
        self._max_buffer = 10000

    async def ingest_point(self, point: TelemetryPoint):
        TELEMETRY_RING_BUFFER.append(point)
        if len(TELEMETRY_RING_BUFFER) > self._max_buffer:
            TELEMETRY_RING_BUFFER.pop(0)

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
