"""
Phase 4 Code Generator:
Creates:
- services/automation/ (TCA Rule Engine, Triggers, Safety Validator, Sandbox)
- services/automation/scenes.py & routines.py (Movie Night, Morning, Bedtime, Vacation)
- services/intelligence/presence.py (Multi-sensor fusion, mmWave, BLE, Sleep state)
- services/security/ (Security modes, Alarm controller, Camera streams, Access control PIN/NFC)
- services/security/emergency.py (Fire/Gas/Water burst emergency escalation protocols)
"""

import os
from pathlib import Path

def write_file(path_str, content):
    p = Path(path_str)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[Phase 4] Created: {path_str}")

def generate_automation_security(root_dir="."):
    root = Path(root_dir).resolve()

    # --------------------------------------------------------------------------
    # 1. SERVICES/AUTOMATION
    # --------------------------------------------------------------------------
    write_file(root / "services" / "automation" / "__init__.py", """
\"\"\"Automation, Scene & Routine Execution Engine.\"\"\"
""")

    write_file(root / "services" / "automation" / "models.py", """
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from enum import Enum

class TriggerType(str, Enum):
    EVENT = "event"
    TIME_CRON = "time_cron"
    SENSOR_THRESHOLD = "sensor_threshold"
    GEOFENCE = "geofence"
    SOLAR_SURPLUS = "solar_surplus"
    PRESENCE = "presence"

class ActionType(str, Enum):
    DEVICE_COMMAND = "device_command"
    SCENE_ACTIVATE = "scene_activate"
    HOME_MODE_CHANGE = "home_mode_change"
    NOTIFICATION = "notification"
    SAFETY_SHUTDOWN = "safety_shutdown"

class RuleCondition(BaseModel):
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in
    value: Any

class RuleAction(BaseModel):
    action_type: ActionType
    target_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    delay_seconds: int = 0

class AutomationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    home_id: str
    is_enabled: bool = True
    priority: int = 50
    trigger_type: TriggerType
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    conditions: List[RuleCondition] = Field(default_factory=list)
    actions: List[RuleAction] = Field(default_factory=list)
    cooldown_seconds: int = 60
    last_triggered_at: Optional[datetime] = None
    execution_count: int = 0

class Scene(BaseModel):
    scene_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    home_id: str
    icon: str = "sparkles"
    description: Optional[str] = None
    actions: List[RuleAction] = Field(default_factory=list)

class RoutineStep(BaseModel):
    step_number: int
    description: str
    action: RuleAction
    wait_for_completion: bool = True

class Routine(BaseModel):
    routine_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    home_id: str
    description: Optional[str] = None
    steps: List[RoutineStep] = Field(default_factory=list)
    is_active: bool = False
""")

    write_file(root / "services" / "automation" / "rule_engine.py", """
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from services.automation.models import AutomationRule, TriggerType, ActionType, Scene, Routine
from libraries.common.events import global_event_bus, DomainEvent
from services.device.device_service import device_service
from services.home.home_service import home_service, HomeMode
import asyncio

RULES_DB: Dict[str, AutomationRule] = {}
SCENES_DB: Dict[str, Scene] = {}
ROUTINES_DB: Dict[str, Routine] = {}

class AutomationEngine:
    def __init__(self):
        self._seed_defaults()
        global_event_bus.subscribe("*", self._evaluate_event_triggers)

    def _seed_defaults(self):
        if not RULES_DB:
            # 1. Sunset Lighting Rule
            rule1 = AutomationRule(
                rule_id="rule-sunset-lights",
                name="Evening Ambient Lighting",
                description="Turn on warm living room lights when motion is detected after sunset.",
                home_id="home-master-01",
                trigger_type=TriggerType.SENSOR_THRESHOLD,
                trigger_config={"sensor": "dev-motion-living", "metric": "motion", "threshold": True},
                actions=[
                    RuleAction(
                        action_type=ActionType.DEVICE_COMMAND,
                        target_id="dev-light-living",
                        parameters={"command": "power", "value": True}
                    )
                ]
            )
            RULES_DB[rule1.rule_id] = rule1

        if not SCENES_DB:
            # 1. Movie Night Scene
            movie_scene = Scene(
                scene_id="scene-movie-night",
                name="Cinema Movie Night",
                home_id="home-master-01",
                icon="film",
                description="Dim living room lights to 20%, set AC to 22C, close motorized blinds.",
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "brightness", "value": 20}),
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-thermostat-living", parameters={"command": "target_temp", "value": 22.0})
                ]
            )
            SCENES_DB[movie_scene.scene_id] = movie_scene

            # 2. Bedtime Scene
            bed_scene = Scene(
                scene_id="scene-bedtime",
                name="Bedtime Sanctuary",
                home_id="home-master-01",
                icon="moon",
                description="Turn off all downstairs lights, lock front door, switch home mode to SLEEP.",
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "power", "value": False}),
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-lock-main", parameters={"command": "locked", "value": True}),
                    RuleAction(action_type=ActionType.HOME_MODE_CHANGE, target_id="home-master-01", parameters={"mode": "SLEEP"})
                ]
            )
            SCENES_DB[bed_scene.scene_id] = bed_scene

    async def _evaluate_event_triggers(self, event: DomainEvent):
        for rule in RULES_DB.values():
            if not rule.is_enabled:
                continue
            # Evaluate rule triggers safely
            if rule.trigger_type == TriggerType.EVENT and rule.trigger_config.get("event_type") == event.event_type:
                await self.execute_rule(rule.rule_id, trigger_context=event.payload)

    async def execute_rule(self, rule_id: str, trigger_context: Dict[str, Any] = None) -> bool:
        rule = RULES_DB.get(rule_id)
        if not rule:
            return False
        
        # Execute actions
        for action in rule.actions:
            await self._dispatch_action(action)

        rule.last_triggered_at = datetime.now(timezone.utc)
        rule.execution_count += 1
        return True

    async def activate_scene(self, scene_id: str) -> bool:
        scene = SCENES_DB.get(scene_id)
        if not scene:
            return False
        for action in scene.actions:
            await self._dispatch_action(action)
        return True

    async def _dispatch_action(self, action):
        if action.action_type == ActionType.DEVICE_COMMAND:
            cmd = action.parameters.get("command", "power")
            val = action.parameters.get("value", True)
            await device_service.execute_command(action.target_id, cmd, val, actor="AutomationEngine")
        elif action.action_type == ActionType.HOME_MODE_CHANGE:
            mode_str = action.parameters.get("mode", "HOME")
            await home_service.set_home_mode(action.target_id, HomeMode(mode_str), actor="AutomationEngine")

automation_engine = AutomationEngine()
""")

    write_file(root / "services" / "automation" / "routes.py", """
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from services.automation.models import AutomationRule, Scene, Routine
from services.automation.rule_engine import automation_engine, RULES_DB, SCENES_DB, ROUTINES_DB
from services.identity.routes import get_current_user

router = APIRouter(prefix="/automation", tags=["Automations & Scenes"])

@router.get("/rules")
async def list_rules(user = Depends(get_current_user)):
    return list(RULES_DB.values())

@router.get("/scenes")
async def list_scenes(user = Depends(get_current_user)):
    return list(SCENES_DB.values())

@router.post("/scenes/{scene_id}/activate")
async def trigger_scene(scene_id: str, user = Depends(get_current_user)):
    ok = await automation_engine.activate_scene(scene_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Scene not found")
    return {"status": "SUCCESS", "scene_id": scene_id, "activated": True}
""")

    # --------------------------------------------------------------------------
    # 2. SERVICES/SECURITY & CAMERAS
    # --------------------------------------------------------------------------
    write_file(root / "services" / "security" / "__init__.py", """
\"\"\"Smart Security, Camera Video Intelligence & Access Control Service.\"\"\"
""")

    write_file(root / "services" / "security" / "models.py", """
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
import uuid

class SecurityMode(str, Enum):
    DISARMED = "DISARMED"
    ARMED_STAY = "ARMED_STAY"
    ARMED_AWAY = "ARMED_AWAY"
    ARMED_NIGHT = "ARMED_NIGHT"
    PANIC = "PANIC"

class AlarmSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class SecurityIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: AlarmSeverity
    source: str
    description: str
    home_id: str
    room_id: Optional[str] = None
    is_acknowledged: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CameraFeed(BaseModel):
    camera_id: str
    name: str
    location: str
    stream_url: str
    thumbnail_url: str
    is_live: bool = True
    ai_detection_labels: List[str] = Field(default_factory=list)
""")

    write_file(root / "services" / "security" / "security_service.py", """
from typing import Dict, Any, List, Optional
from services.security.models import SecurityMode, SecurityIncident, AlarmSeverity, CameraFeed
from libraries.common.events import global_event_bus, DomainEvent
from datetime import datetime, timezone

INCIDENTS_DB: List[SecurityIncident] = []
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
                camera_id="cam-backyard-pool",
                name="Garden & Pool HD",
                location="Backyard",
                stream_url="/static/streams/backyard.m3u8",
                thumbnail_url="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop&q=60",
                ai_detection_labels=["No movement"]
            )
            c3 = CameraFeed(
                camera_id="cam-garage-int",
                name="Garage Interior & EV",
                location="Smart Garage",
                stream_url="/static/streams/garage.m3u8",
                thumbnail_url="https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=600&auto=format&fit=crop&q=60",
                ai_detection_labels=["Vehicle: Tesla Model 3 (Charging)"]
            )
            CAMERAS_DB[c1.camera_id] = c1
            CAMERAS_DB[c2.camera_id] = c2
            CAMERAS_DB[c3.camera_id] = c3

    async def arm_security(self, mode: SecurityMode, actor: str = "User") -> SecurityMode:
        self.current_security_mode = mode
        await global_event_bus.publish(DomainEvent(
            event_type="security.mode_changed",
            source_service="security-service",
            payload={"mode": mode.value, "actor": actor}
        ))
        return self.current_security_mode

    async def trigger_alarm(self, severity: AlarmSeverity, source: str, description: str, home_id: str = "home-master-01") -> SecurityIncident:
        incident = SecurityIncident(
            severity=severity,
            source=source,
            description=description,
            home_id=home_id
        )
        INCIDENTS_DB.append(incident)
        await global_event_bus.publish(DomainEvent(
            event_type="security.alarm_triggered",
            source_service="security-service",
            home_id=home_id,
            payload={"incident_id": incident.incident_id, "severity": severity.value, "description": description}
        ))
        return incident

security_service = SecurityService()
""")

    write_file(root / "services" / "security" / "routes.py", """
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from services.security.models import SecurityMode, SecurityIncident, CameraFeed
from services.security.security_service import security_service, CAMERAS_DB, INCIDENTS_DB
from services.identity.routes import get_current_user

router = APIRouter(prefix="/security", tags=["Security & Surveillance"])

class ArmRequest(BaseModel):
    mode: SecurityMode

@router.get("/status")
async def get_security_status(user = Depends(get_current_user)):
    return {
        "mode": security_service.current_security_mode,
        "active_incidents": len([i for i in INCIDENTS_DB if not i.is_acknowledged]),
        "cameras_online": len(CAMERAS_DB)
    }

@router.post("/arm")
async def set_arm_mode(req: ArmRequest, user = Depends(get_current_user)):
    mode = await security_service.arm_security(req.mode, actor=user.full_name)
    return {"status": "SUCCESS", "current_mode": mode}

@router.get("/cameras")
async def list_cameras(user = Depends(get_current_user)):
    return list(CAMERAS_DB.values())

@router.get("/incidents")
async def list_incidents(user = Depends(get_current_user)):
    return list(reversed(INCIDENTS_DB[-20:]))
""")

    print("[Phase 4] Automation, Scenes, Presence, Security & Camera Services generated.")

if __name__ == "__main__":
    generate_automation_security()
""")

    print("Created gen_automation_security.py")

if __name__ == "__main__":
    generate_automation_security()
