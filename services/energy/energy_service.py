from datetime import datetime, timezone
from services.energy.models import EnergyFlow
from typing import Dict, Any
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
        self.peak_rate_kwh = 0.28
        self.off_peak_rate_kwh = 0.11
        self.feed_in_tariff_kwh = 0.08
        self.daily_solar_kwh_produced = 28.4

    def get_realtime_energy_flow(self) -> EnergyFlow:
        drift = (random.random() - 0.5) * 0.12
        self._current_flow.solar_generation_kw = max(0.0, round(self._current_flow.solar_generation_kw + drift, 2))
        load_drift = (random.random() - 0.5) * 0.08
        self._current_flow.home_consumption_kw = max(1.2, round(self._current_flow.home_consumption_kw + load_drift, 2))
        return self._current_flow

    def get_tariff_breakdown(self) -> Dict[str, Any]:
        """Calculates Time-of-Use (ToU) financial metrics, daily savings, and grid arbitrage."""
        now = datetime.now()
        is_peak = 14 <= now.hour <= 20  # Peak window 2:00 PM - 8:00 PM
        current_rate = self.peak_rate_kwh if is_peak else self.off_peak_rate_kwh
        
        # Calculate daily cost saved by solar & battery vs grid retail price
        daily_saved = round(self.daily_solar_kwh_produced * self.peak_rate_kwh * 0.85, 2)
        grid_export_usd = round(max(0.0, -self._current_flow.grid_import_kw) * 4.0 * self.feed_in_tariff_kwh, 2)
        
        return {
            "current_rate_usd_kwh": current_rate,
            "tariff_period": "PEAK (ToU)" if is_peak else "OFF-PEAK (ToU)",
            "daily_cost_saved_usd": daily_saved,
            "grid_export_earned_usd": grid_export_usd,
            "self_consumption_ratio_pct": 94.5,
            "carbon_offset_kg_today": round(self.daily_solar_kwh_produced * 0.42, 1),
            "ev_charging_recommendation": "SMART_SURPLUS" if self._current_flow.solar_generation_kw > 3.5 else "DELAY_TO_OFFPEAK"
        }

energy_service = EnergyService()
