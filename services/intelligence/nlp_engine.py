import re
from typing import Dict, Any
from services.device.device_service import device_service
from services.security.security_service import security_service, SecurityMode

class NLPEngine:
    async def process_query(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip().lower()
        if "light" in cleaned or "lights" in cleaned:
            if "off" in cleaned:
                await device_service.execute_command("dev-light-living", "power", False, actor="NLP_Assistant")
                return {"reply": "I've turned off the living room lights.", "action_taken": "LIGHT_OFF"}
            elif "on" in cleaned:
                await device_service.execute_command("dev-light-living", "power", True, actor="NLP_Assistant")
                return {"reply": "Living room lights are now ON.", "action_taken": "LIGHT_ON"}
        
        if "temp" in cleaned or "temperature" in cleaned or "ac" in cleaned:
            digits = re.findall(r'\d+', cleaned)
            target = float(digits[0]) if digits else 22.0
            await device_service.execute_command("dev-thermostat-living", "target_temp", target, actor="NLP_Assistant")
            return {"reply": f"Living room climate set to {target}°C.", "action_taken": "SET_TEMPERATURE"}

        return {"reply": f"Understood: '{text}'. All systems operational.", "action_taken": "ACKNOWLEDGED"}

nlp_engine = NLPEngine()
