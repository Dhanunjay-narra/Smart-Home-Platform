from datetime import datetime, timezone
from services.energy.models import EnergyFlow
import random

class EnergyService:
    def __init__(self):
        self._current_flow = EnergyFlow(
            solar_generation_kw=4.85,
            battery_charge_kw=1.20,
            battery_soc_percent=88.5,
            grid_import_kw=-0.45,
            home_consumption_kw=3.20,
            ev_charging_kw=7.40
        )

    def get_realtime_energy_flow(self) -> EnergyFlow:
        drift = (random.random() - 0.5) * 0.08
        self._current_flow.solar_generation_kw = max(0.0, round(self._current_flow.solar_generation_kw + drift, 2))
        return self._current_flow

energy_service = EnergyService()
