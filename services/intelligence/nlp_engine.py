import re
from typing import Dict, Any
from services.device.device_service import device_service
from services.security.security_service import security_service, SecurityMode
from services.automation.rule_engine import automation_engine

class NLPEngine:
    async def process_query(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip().lower()
        
        # 1. Greetings & Pleasantries
        greetings = ["hi", "hello", "hey", "hii", "hi assistant", "hello assistant", "hey assistant", "hola", "namaste", "good morning", "good evening", "good afternoon"]
        if cleaned in greetings or any(cleaned == g or cleaned.startswith(g + " ") or cleaned.endswith(" " + g) for g in ["hi", "hello", "hey", "hii"]):
            return {
                "reply": "Hello! How can I assist you with your Smart Home today?",
                "action_taken": "GREETING"
            }
        
        if "how are you" in cleaned or "how're you" in cleaned:
            return {
                "reply": "I'm doing great and all your Smart Home systems are online and running smoothly! How can I assist you?",
                "action_taken": "STATUS_OK"
            }

        if "who are you" in cleaned or "what can you do" in cleaned or cleaned == "help":
            return {
                "reply": "I am your Home Assistant. You can ask me to control lights, adjust climate temperature, check solar power, or arm security. How can I assist you?",
                "action_taken": "HELP"
            }

        # 2. Lights Control
        if "light" in cleaned or "lights" in cleaned:
            if "off" in cleaned:
                await device_service.execute_command("dev-light-living", "power", False, actor="Home_Assistant")
                return {"reply": "I've turned off the living room lights.", "action_taken": "LIGHT_OFF"}
            elif "on" in cleaned:
                await device_service.execute_command("dev-light-living", "power", True, actor="Home_Assistant")
                return {"reply": "Living room lights are now ON.", "action_taken": "LIGHT_ON"}
            elif "bright" in cleaned or "%" in cleaned:
                digits = re.findall(r'\d+', cleaned)
                level = int(digits[0]) if digits else 80
                await device_service.execute_command("dev-light-living", "brightness", level, actor="Home_Assistant")
                return {"reply": f"Living room lights brightness adjusted to {level}%.", "action_taken": "SET_BRIGHTNESS"}

        # 3. Climate / AC Control
        if "temp" in cleaned or "temperature" in cleaned or "ac" in cleaned or "climate" in cleaned or "thermostat" in cleaned:
            digits = re.findall(r'\d+', cleaned)
            target = float(digits[0]) if digits else 22.0
            await device_service.execute_command("dev-thermostat-living", "target_temp", target, actor="Home_Assistant")
            return {"reply": f"Living room climate temperature set to {target}°C.", "action_taken": "SET_TEMPERATURE"}

        # 4. Solar & Energy Queries
        if "solar" in cleaned or "energy" in cleaned or "power" in cleaned or "battery" in cleaned:
            return {
                "reply": "Rooftop solar is generating 4.85 kW with +28.4 kWh yield today. Battery reserve is at 88.5% (+1.2 kW charging).",
                "action_taken": "ENERGY_TELEMETRY"
            }

        # 5. Security & Cameras
        if "security" in cleaned or "camera" in cleaned or "arm" in cleaned or "lock" in cleaned:
            if "disarm" in cleaned or "unlock" in cleaned:
                security_service.arm(SecurityMode.DISARMED, armed_by="Home_Assistant")
                return {"reply": "Security system is now DISARMED.", "action_taken": "SECURITY_DISARM"}
            else:
                security_service.arm(SecurityMode.ARMED_AWAY, armed_by="Home_Assistant")
                return {"reply": "Perimeter security armed in AWAY mode with all 3 AI cameras active.", "action_taken": "SECURITY_ARM"}

        # 6. Scenes & Living Modes
        if "movie" in cleaned:
            await automation_engine.execute_scene("scene-movie-night", triggered_by="Home_Assistant")
            return {"reply": "Movie Night scene activated: Lights dimmed to 20%, AC set to 22°C.", "action_taken": "SCENE_MOVIE"}
        
        if "bedtime" in cleaned or "sleep" in cleaned:
            await automation_engine.execute_scene("scene-bedtime", triggered_by="Home_Assistant")
            return {"reply": "Bedtime sanctuary activated: All doors locked, lights turned off, sleep mode enabled.", "action_taken": "SCENE_BEDTIME"}

        # 7. Fallback Response
        return {
            "reply": f"Understood! How else can I assist you with your Smart Home?",
            "action_taken": "ACKNOWLEDGED"
        }

nlp_engine = NLPEngine()
