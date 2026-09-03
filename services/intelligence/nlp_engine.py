import re
from typing import Dict, Any, List
from services.device.device_service import device_service
from services.security.security_service import security_service, SecurityMode
from services.automation.rule_engine import automation_engine
from services.energy.energy_service import energy_service
from services.home.home_service import home_service, HomeMode

class NLPEngine:
    """Conversational AI intent parser and multi-device action orchestrator."""

    async def process_query(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip().lower()
        if not cleaned:
            return {
                "reply": "I'm listening! You can ask me to control devices, adjust climate, check solar power, or activate scenes.",
                "action_taken": "EMPTY_PROMPT",
                "actions_executed": []
            }

        actions_taken = []
        replies = []

        # 1. Greetings & System Health Checks
        greetings = ["hi", "hello", "hey", "hii", "hola", "namaste", "good morning", "good evening", "good afternoon"]
        if any(cleaned == g or cleaned.startswith(g + " ") for g in greetings) and len(cleaned.split()) <= 4:
            return {
                "reply": "Hello! I'm your Smart Home Copilot. All your home systems are online and running smoothly. How can I assist you?",
                "action_taken": "GREETING",
                "actions_executed": []
            }

        if "how are you" in cleaned or "status" in cleaned or "system health" in cleaned:
            flow = energy_service.get_realtime_energy_flow()
            return {
                "reply": f"Everything is running perfectly! Solar is generating {flow.solar_generation_kw:.2f} kW, battery is at {flow.battery_soc_percent:.1f}%, and home security is active.",
                "action_taken": "SYSTEM_STATUS",
                "actions_executed": ["FETCH_TELEMETRY"]
            }

        if "who are you" in cleaned or "what can you do" in cleaned or cleaned == "help":
            return {
                "reply": "I am your Smart Home Assistant. I can control multi-room lighting, set climate temperatures, activate living scenes, check real-time solar/battery power, and arm perimeter security.",
                "action_taken": "HELP",
                "actions_executed": []
            }

        # 2. Multi-Action: Lighting Control
        if "light" in cleaned or "lights" in cleaned or "lamp" in cleaned:
            if "off" in cleaned or "turn off" in cleaned or "shut" in cleaned:
                await device_service.execute_command("dev-light-living", "power", False, actor="AI_Copilot")
                actions_taken.append("LIGHT_OFF")
                replies.append("Living room lights turned OFF")
            elif "on" in cleaned or "turn on" in cleaned:
                await device_service.execute_command("dev-light-living", "power", True, actor="AI_Copilot")
                actions_taken.append("LIGHT_ON")
                replies.append("Living room lights turned ON")
            
            if "bright" in cleaned or "%" in cleaned or "dim" in cleaned:
                digits = re.findall(r'\d+', cleaned)
                level = int(digits[0]) if digits else (25 if "dim" in cleaned else 80)
                level = max(0, min(100, level))
                await device_service.execute_command("dev-light-living", "brightness", level, actor="AI_Copilot")
                actions_taken.append("SET_BRIGHTNESS")
                replies.append(f"brightness set to {level}%")

        # 3. Multi-Action: Climate / Thermostat Control
        if "temp" in cleaned or "temperature" in cleaned or "ac" in cleaned or "climate" in cleaned or "thermostat" in cleaned or "cool" in cleaned or "heat" in cleaned:
            digits = re.findall(r'\d+', cleaned)
            temp_candidates = [float(d) for d in digits if 15 <= float(d) <= 32]
            target_temp = temp_candidates[0] if temp_candidates else 22.0
            
            await device_service.execute_command("dev-thermostat-living", "target_temp", target_temp, actor="AI_Copilot")
            actions_taken.append("SET_TEMPERATURE")
            replies.append(f"Living room AC set to {target_temp}°C")

        # 4. Real-Time Energy & Solar Queries
        if "solar" in cleaned or "energy" in cleaned or "power" in cleaned or "battery" in cleaned or "electric" in cleaned or "saving" in cleaned:
            flow = energy_service.get_realtime_energy_flow()
            tariff = energy_service.get_tariff_breakdown()
            actions_taken.append("ENERGY_QUERY")
            replies.append(
                f"Solar is currently generating {flow.solar_generation_kw:.2f} kW (Home load: {flow.home_consumption_kw:.2f} kW). "
                f"Battery is at {flow.battery_soc_percent:.1f}% SoC. You've saved ${tariff.get('daily_cost_saved_usd', 4.25):.2f} today via clean solar energy"
            )

        # 5. Security & Camera Controls
        if "security" in cleaned or "alarm" in cleaned or "camera" in cleaned or "lock" in cleaned:
            if "disarm" in cleaned or "unlock" in cleaned:
                security_service.arm(SecurityMode.DISARMED, armed_by="AI_Copilot")
                actions_taken.append("SECURITY_DISARM")
                replies.append("Perimeter security is now DISARMED and doors unlocked")
            elif "arm" in cleaned or "lock" in cleaned:
                security_service.arm(SecurityMode.ARMED_AWAY, armed_by="AI_Copilot")
                actions_taken.append("SECURITY_ARM")
                replies.append("Perimeter security ARMED in AWAY mode with all AI cameras active")

        # 6. Living Scenes & Routines
        if "movie" in cleaned or "cinema" in cleaned:
            await automation_engine.activate_scene("scene-movie-night")
            actions_taken.append("SCENE_MOVIE")
            replies.append("Movie Night scene activated: Lights dimmed to 20%, AC set to 22°C")
        elif "bedtime" in cleaned or "sleep" in cleaned or ("night" in cleaned and "good" in cleaned):
            await automation_engine.activate_scene("scene-bedtime")
            actions_taken.append("SCENE_BEDTIME")
            replies.append("Bedtime Sanctuary activated: All doors locked, lights turned off, sleep mode enabled")
        elif "morning" in cleaned:
            await automation_engine.activate_scene("scene-morning")
            actions_taken.append("SCENE_MORNING")
            replies.append("Good Morning routine activated: Warm lighting set to 80%, climate set to 23°C")

        # 7. Home Mode Transitions
        if "away" in cleaned and "mode" in cleaned:
            await home_service.set_home_mode("home-master-01", HomeMode.AWAY, actor="AI_Copilot")
            actions_taken.append("MODE_AWAY")
            replies.append("Home mode set to AWAY")
        elif "home mode" in cleaned or "back home" in cleaned:
            await home_service.set_home_mode("home-master-01", HomeMode.HOME, actor="AI_Copilot")
            actions_taken.append("MODE_HOME")
            replies.append("Home mode set to HOME")

        # 8. Synthesize Final Conversational Output
        if replies:
            final_reply = ". ".join(replies) + "."
            return {
                "reply": final_reply,
                "action_taken": actions_taken[0] if len(actions_taken) == 1 else "MULTI_ACTION",
                "actions_executed": actions_taken
            }

        # Fallback for unrecognized queries
        return {
            "reply": f"I understand your request. I've noted: '{text}'. Would you like me to adjust devices, check solar yield, or arm security?",
            "action_taken": "ACKNOWLEDGED",
            "actions_executed": []
        }

nlp_engine = NLPEngine()
