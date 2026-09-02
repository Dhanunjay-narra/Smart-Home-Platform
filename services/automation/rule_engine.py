from typing import Dict, Any, List, Optional
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
            morning_scene = Scene(
                scene_id="scene-morning",
                name="Good Morning Energize",
                home_id="home-master-01",
                icon="sun",
                description="Turn on warm lighting (80%), set AC to 23°C, HOME mode.",
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "power", "value": True}),
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "brightness", "value": 80}),
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-thermostat-living", parameters={"command": "target_temp", "value": 23.0}),
                    RuleAction(action_type=ActionType.HOME_MODE_CHANGE, target_id="home-master-01", parameters={"mode": "HOME"})
                ]
            )
            SCENES_DB[morning_scene.scene_id] = morning_scene

            away_scene = Scene(
                scene_id="scene-away-eco",
                name="Eco Away & Lock Guard",
                home_id="home-master-01",
                icon="person-walking-luggage",
                description="Turn off all lights, lock all doors, set AWAY mode.",
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "power", "value": False}),
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-lock-main", parameters={"command": "locked", "value": True}),
                    RuleAction(action_type=ActionType.HOME_MODE_CHANGE, target_id="home-master-01", parameters={"mode": "AWAY"})
                ]
            )
            SCENES_DB[away_scene.scene_id] = away_scene

        if not RULES_DB:
            r1 = AutomationRule(
                rule_id="rule-solar-ev-charge",
                name="Solar Surplus Smart EV Charging",
                description="When solar yield >= 4.0 kW, maximize home energy self-consumption",
                home_id="home-master-01",
                is_enabled=True,
                trigger_type=TriggerType.SENSOR_THRESHOLD,
                trigger_config={"sensor": "Solar Inverter", "condition": "Solar >= 4.0 kW"},
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-solar-inverter", parameters={"command": "grid_export_kw", "value": 0.5})
                ]
            )
            RULES_DB[r1.rule_id] = r1

            r2 = AutomationRule(
                rule_id="rule-motion-living-light",
                name="Occupancy Radar Ambient Lighting",
                description="When mmWave radar detects presence in Living Room, turn on ambient lights",
                home_id="home-master-01",
                is_enabled=True,
                trigger_type=TriggerType.EVENT,
                trigger_config={"event": "presence.detected", "zone": "Living Room"},
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-light-living", parameters={"command": "power", "value": True})
                ]
            )
            RULES_DB[r2.rule_id] = r2

            r3 = AutomationRule(
                rule_id="rule-night-lockdown",
                name="Night Schedule Perimeter Lockdown",
                description="At 23:00 daily, verify all perimeter doors locked & activate SLEEP mode",
                home_id="home-master-01",
                is_enabled=True,
                trigger_type=TriggerType.TIME_CRON,
                trigger_config={"cron": "0 23 * * *", "schedule": "Daily at 11:00 PM"},
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-lock-main", parameters={"command": "locked", "value": True}),
                    RuleAction(action_type=ActionType.HOME_MODE_CHANGE, target_id="home-master-01", parameters={"mode": "SLEEP"})
                ]
            )
            RULES_DB[r3.rule_id] = r3

            r4 = AutomationRule(
                rule_id="rule-water-leak-defense",
                name="Emergency Water Burst Isolation",
                description="If moisture sensor triggers, immediately isolate main motorized water shutoff valve",
                home_id="home-master-01",
                is_enabled=True,
                trigger_type=TriggerType.EVENT,
                trigger_config={"event": "leak.sensor_tripped", "severity": "CRITICAL"},
                actions=[
                    RuleAction(action_type=ActionType.DEVICE_COMMAND, target_id="dev-lock-main", parameters={"command": "locked", "value": True})
                ]
            )
            RULES_DB[r4.rule_id] = r4

    async def activate_scene(self, scene_id: str) -> bool:
        scene = SCENES_DB.get(scene_id)
        if not scene:
            return False
        for action in scene.actions:
            if action.action_type == ActionType.DEVICE_COMMAND:
                cmd = action.parameters.get("command", "power")
                val = action.parameters.get("value", True)
                await device_service.execute_command(action.target_id, cmd, val, actor="SceneActivation")
            elif action.action_type == ActionType.HOME_MODE_CHANGE:
                mode_str = action.parameters.get("mode", "HOME")
                await home_service.set_home_mode(action.target_id, HomeMode(mode_str), actor="SceneActivation")
        return True

    async def toggle_rule(self, rule_id: str) -> Optional[bool]:
        rule = RULES_DB.get(rule_id)
        if not rule:
            return None
        rule.is_enabled = not rule.is_enabled
        return rule.is_enabled

    async def execute_rule(self, rule_id: str) -> bool:
        rule = RULES_DB.get(rule_id)
        if not rule:
            return False
        for action in rule.actions:
            if action.action_type == ActionType.DEVICE_COMMAND:
                cmd = action.parameters.get("command", "power")
                val = action.parameters.get("value", True)
                await device_service.execute_command(action.target_id, cmd, val, actor="RuleExecution")
            elif action.action_type == ActionType.HOME_MODE_CHANGE:
                mode_str = action.parameters.get("mode", "HOME")
                await home_service.set_home_mode(action.target_id, HomeMode(mode_str), actor="RuleExecution")
        return True

automation_engine = AutomationEngine()
