from typing import Dict, Any, List
from services.automation.models import AutomationRule, TriggerType, ActionType, Scene, RuleAction
from libraries.common.events import global_event_bus, DomainEvent
from services.device.device_service import device_service
from services.home.home_service import home_service, HomeMode

RULES_DB: Dict[str, AutomationRule] = {}
SCENES_DB: Dict[str, Scene] = {}

class AutomationEngine:
    def __init__(self):
        self._seed_defaults()

    def _seed_defaults(self):
        if not SCENES_DB:
            movie_scene = Scene(
                scene_id="scene-movie-night",
                name="Cinema Movie Night",
                home_id="home-master-01",
                icon="film",
                description="Dim lights to 20%, AC to 22C.",
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "brightness", "value": 20}),
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-thermostat-living", parameters={"command": "target_temp", "value": 22.0})
                ]
            )
            SCENES_DB[movie_scene.scene_id] = movie_scene

            bed_scene = Scene(
                scene_id="scene-bedtime",
                name="Bedtime Sanctuary",
                home_id="home-master-01",
                icon="moon",
                description="Turn off lights, lock doors, SLEEP mode.",
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "power", "value": False}),
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-lock-main", parameters={"command": "locked", "value": True}),
                    RuleAction(action_type=ActionType.HOME_MODE_CHANGE, target_id="home-master-01", parameters={"mode": "SLEEP"})
                ]
            )
            SCENES_DB[bed_scene.scene_id] = bed_scene

    async def activate_scene(self, scene_id: str) -> bool:
        scene = SCENES_DB.get(scene_id)
        if not scene:
            return False
        for action in scene.actions:
            if action.action_type == ActionType.DEVICE_COMMAND:
                cmd = action.parameters.get("command", "power")
                val = action.parameters.get("value", True)
                await device_service.execute_command(action.target_id, cmd, val, actor="AutomationEngine")
            elif action.action_type == ActionType.HOME_MODE_CHANGE:
                mode_str = action.parameters.get("mode", "HOME")
                await home_service.set_home_mode(action.target_id, HomeMode(mode_str), actor="AutomationEngine")
        return True

automation_engine = AutomationEngine()
