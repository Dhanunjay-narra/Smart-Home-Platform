from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from enum import Enum

class TriggerType(str, Enum):
    EVENT = "event"
    TIME_CRON = "time_cron"
    SENSOR_THRESHOLD = "sensor_threshold"

class ActionType(str, Enum):
    DEVICE_COMMAND = "device_command"
    SCENE_ACTIVATE = "scene_activate"
    HOME_MODE_CHANGE = "home_mode_change"

class RuleAction(BaseModel):
    action_type: ActionType
    target_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class AutomationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    home_id: str
    is_enabled: bool = True
    trigger_type: TriggerType
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    actions: List[RuleAction] = Field(default_factory=list)

class Scene(BaseModel):
    scene_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    home_id: str
    icon: str = "sparkles"
    description: Optional[str] = None
    actions: List[RuleAction] = Field(default_factory=list)
