from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
import uuid

class SecurityMode(str, Enum):
    DISARMED = "DISARMED"
    ARMED_STAY = "ARMED_STAY"
    ARMED_AWAY = "ARMED_AWAY"

class CameraFeed(BaseModel):
    camera_id: str
    name: str
    location: str
    stream_url: str
    thumbnail_url: str
    ai_detection_labels: List[str] = Field(default_factory=list)
