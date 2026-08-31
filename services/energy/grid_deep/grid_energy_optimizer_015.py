"""
Smart Home Platform — Grid Energy Optimization Subsystem 015
Handles PV power forecasting, battery storage lifecycle, and dynamic tariff dispatch.
Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
import math

class GridEnergyOptimizer015Parameters(BaseModel):
    optimizer_id: str = "grid_energy_optimizer_015"
    index: int = 15
    solar_pv_capacity_kwp: float = 8.5
    battery_capacity_kwh: float = 15.0
    max_inverter_charge_rate_kw: float = 5.0
    grid_export_limit_kw: float = 6.0
    offpeak_tariff_rate: float = 4.50
    peak_tariff_rate: float = 12.80
    co2_intensity_g_per_kwh: float = 650.0

class GridEnergyOptimizer015:
    """Real-time economic energy dispatch and battery longevity optimizer."""
    def __init__(self):
        self.params = GridEnergyOptimizer015Parameters()
        self.cumulative_savings_currency: float = 0.0
        self.cumulative_co2_abated_kg: float = 0.0

    def optimize_dispatch(self, current_solar_kw: float, home_load_kw: float, battery_soc_pct: float) -> Dict[str, Any]:
        """Computes optimal split between self-consumption, battery storage, and grid interaction."""
        net_power = current_solar_kw - home_load_kw
        battery_action = "IDLE"
        battery_power_kw = 0.0
        grid_power_kw = 0.0

        if net_power > 0:
            # Surplus solar generation
            if battery_soc_pct < 98.0:
                battery_power_kw = min(net_power, self.params.max_inverter_charge_rate_kw)
                battery_action = "CHARGING"
                grid_power_kw = -(net_power - battery_power_kw) # Export remainder
            else:
                grid_power_kw = -net_power # Full export
        else:
            # Deficit load requirement
            deficit = abs(net_power)
            if battery_soc_pct > 20.0:
                battery_power_kw = min(deficit, self.params.max_inverter_charge_rate_kw)
                battery_action = "DISCHARGING"
                grid_power_kw = deficit - battery_power_kw # Import remainder
            else:
                grid_power_kw = deficit # Full grid import

        # Compute cost and carbon metrics
        avoided_cost = (current_solar_kw * self.params.peak_tariff_rate) * 0.01
        self.cumulative_savings_currency += avoided_cost
        co2_saved = (current_solar_kw * self.params.co2_intensity_g_per_kwh) / 1000.0 * 0.01
        self.cumulative_co2_abated_kg += co2_saved

        return {
            "optimizer_id": self.params.optimizer_id,
            "solar_generation_kw": round(current_solar_kw, 2),
            "home_load_kw": round(home_load_kw, 2),
            "battery_action": battery_action,
            "battery_power_kw": round(battery_power_kw, 2),
            "grid_power_kw": round(grid_power_kw, 2),
            "tariff_savings": round(self.cumulative_savings_currency, 2),
            "co2_abated_kg": round(self.cumulative_co2_abated_kg, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
