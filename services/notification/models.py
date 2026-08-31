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
