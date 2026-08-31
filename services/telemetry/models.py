from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class TelemetryPoint(BaseModel):
    point_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    home_id: str
    metric_name: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
