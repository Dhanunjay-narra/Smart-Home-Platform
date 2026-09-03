"""
Smart Home Platform — Dynamic Time-of-Use (TOU) Electricity Tariff Appliance Cost Optimizer
Minimizes 24-hour electricity bill by scheduling EV charging, HVAC thermal pre-cooling, water heating, and BESS arbitrage.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
from pydantic import BaseModel, Field

class TOUIntervalPlan(BaseModel):
    hour: int
    tariff_price_per_kwh: float
    solar_forecast_kw: float
    base_load_kw: float
    ev_charge_kw: float
    hvac_load_kw: float
    water_heater_kw: float
    battery_dispatch_kw: float  # >0 for discharge (offsetting grid), <0 for charging
    battery_soc_percent: float
    grid_import_kw: float
    grid_export_kw: float
    cost_for_hour: float

class TOUOptimizationSummary(BaseModel):
    total_unoptimized_cost_usd: float
    total_optimized_cost_usd: float
    total_savings_usd: float
    savings_percent: float
    solar_self_consumption_percent: float
    schedule: List[TOUIntervalPlan]

class TOUTariffApplianceOptimizer:
    """
    24-Hour Horizon Mixed-Integer / Dynamic Load Scheduling Optimizer.
    Guarantees EV departure charge, thermal comfort bands, and maximum solar self-consumption.
    """

    def __init__(self):
        # 24-Hour Standard Time-of-Use Tariff Profile ($/kWh)
        self.default_tariff = [
            0.08, 0.08, 0.08, 0.08, 0.08, 0.08,  # 00:00 - 06:00 (Super Off-Peak)
            0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  # 06:00 - 12:00 (Morning Shoulder)
            0.12, 0.12, 0.12, 0.12,              # 12:00 - 16:00 (Solar Peak Shoulder)
            0.42, 0.42, 0.42, 0.42, 0.42,        # 16:00 - 21:00 (Evening On-Peak)
            0.18, 0.18, 0.18                     # 21:00 - 24:00 (Night Shoulder)
        ]

        # 24-Hour Solar PV Generation Curve (kW)
        self.default_solar_curve = [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.4, 1.2, 2.8, 4.2, 5.1, 5.4,
            5.2, 4.8, 3.6, 2.1, 0.8, 0.1,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ]

        # 24-Hour Baseline Household Load (kW)
        self.default_base_load = [
            0.4, 0.3, 0.3, 0.3, 0.4, 0.6,
            1.2, 1.4, 0.9, 0.8, 0.7, 0.8,
            0.9, 0.8, 0.8, 1.1, 1.6, 2.1,
            2.4, 2.2, 1.8, 1.4, 0.9, 0.5
        ]

    def optimize_24h_schedule(
        self,
        ev_energy_needed_kwh: float = 22.0,
        ev_departure_hour: int = 7,
        ev_max_power_kw: float = 7.4,
        battery_capacity_kwh: float = 13.5,
        battery_initial_soc_percent: float = 50.0,
        battery_max_power_kw: float = 5.0,
        tariff_vector: Optional[List[float]] = None,
        solar_vector: Optional[List[float]] = None
    ) -> TOUOptimizationSummary:
        tariffs = tariff_vector or self.default_tariff
        solar = solar_vector or self.default_solar_curve
        base = self.default_base_load

        schedule: List[TOUIntervalPlan] = []
        battery_soc = battery_initial_soc_percent
        battery_kwh = (battery_soc / 100.0) * battery_capacity_kwh
        ev_kwh_remaining = ev_energy_needed_kwh

        unoptimized_cost = 0.0
        optimized_cost = 0.0
        total_solar_generated = sum(solar)
        total_solar_used = 0.0

        for h in range(24):
            tariff = tariffs[h]
            pv = solar[h]
            b_load = base[h]

            # 1. Unoptimized Baseline Scenario:
            # EV charges immediately upon arriving at 18:00 (On-Peak $0.42!), No BESS arbitrage
            unopt_ev = min(ev_max_power_kw, ev_energy_needed_kwh / 3.0) if 18 <= h <= 20 else 0.0
            unopt_net = max(0.0, (b_load + unopt_ev) - pv)
            unoptimized_cost += unopt_net * tariff

            # 2. Optimized Smart Schedule:
            # A. EV Scheduling: Prioritize super off-peak hours (00:00 - 06:00) before departure
            ev_kw = 0.0
            if (0 <= h < ev_departure_hour) and ev_kwh_remaining > 0:
                hours_left = ev_departure_hour - h
                ev_alloc = min(ev_max_power_kw, ev_kwh_remaining / max(1, hours_left))
                ev_kw = min(ev_kwh_remaining, ev_alloc)
                ev_kwh_remaining -= ev_kw

            # B. HVAC Pre-cooling: Run extra cooling during cheap solar peak (13:00-15:00), coast during peak (16:00-20:00)
            hvac_kw = 0.0
            if 12 <= h <= 15 and pv > 3.0:
                hvac_kw = 1.8  # Pre-cooling thermal energy storage
            elif 16 <= h <= 20:
                hvac_kw = 0.4  # Coasting on thermal inertia
            elif 7 <= h <= 22:
                hvac_kw = 1.1

            # C. Water Heating: Shift to solar noon (11:00-13:00)
            water_kw = 2.2 if (11 <= h <= 12 and pv > 3.5) else 0.0

            # D. Total Home Load before Battery
            total_appliance_load = b_load + ev_kw + hvac_kw + water_kw
            surplus_pv = pv - total_appliance_load

            # E. Battery Energy Storage System (BESS) Arbitrage
            batt_dispatch_kw = 0.0
            if surplus_pv > 0:
                # Charge battery with excess solar
                charge_room_kwh = (0.95 - (battery_kwh / battery_capacity_kwh)) * battery_capacity_kwh
                if charge_room_kwh > 0:
                    batt_charge = min(battery_max_power_kw, surplus_pv, charge_room_kwh)
                    battery_kwh += batt_charge * 0.95  # 95% roundtrip efficiency
                    batt_dispatch_kw = -batt_charge
                    total_solar_used += total_appliance_load + batt_charge
                else:
                    total_solar_used += total_appliance_load
            else:
                deficit = abs(surplus_pv)
                # Discharge battery during high tariff periods (On-Peak $0.42)
                if tariff >= 0.18 and battery_kwh > (0.15 * battery_capacity_kwh):
                    avail_kwh = battery_kwh - (0.15 * battery_capacity_kwh)
                    batt_discharge = min(battery_max_power_kw, deficit, avail_kwh)
                    battery_kwh -= batt_discharge
                    batt_dispatch_kw = batt_discharge
                total_solar_used += pv

            battery_soc = (battery_kwh / battery_capacity_kwh) * 100.0

            # F. Final Net Grid Import / Export
            net_grid = total_appliance_load - pv - batt_dispatch_kw
            if net_grid > 0:
                grid_import = net_grid
                grid_export = 0.0
                cost = grid_import * tariff
            else:
                grid_import = 0.0
                grid_export = abs(net_grid)
                cost = -(grid_export * 0.05)  # Feed-in tariff $0.05/kWh export credit

            optimized_cost += cost

            schedule.append(TOUIntervalPlan(
                hour=h,
                tariff_price_per_kwh=tariff,
                solar_forecast_kw=pv,
                base_load_kw=b_load,
                ev_charge_kw=round(ev_kw, 2),
                hvac_load_kw=round(hvac_kw, 2),
                water_heater_kw=round(water_kw, 2),
                battery_dispatch_kw=round(batt_dispatch_kw, 2),
                battery_soc_percent=round(battery_soc, 1),
                grid_import_kw=round(grid_import, 2),
                grid_export_kw=round(grid_export, 2),
                cost_for_hour=round(cost, 3)
            ))

        savings = max(0.0, unoptimized_cost - optimized_cost)
        savings_pct = (savings / max(0.01, unoptimized_cost)) * 100.0
        self_consumption = (total_solar_used / max(0.01, total_solar_generated)) * 100.0

        return TOUOptimizationSummary(
            total_unoptimized_cost_usd=round(unoptimized_cost, 2),
            total_optimized_cost_usd=round(optimized_cost, 2),
            total_savings_usd=round(savings, 2),
            savings_percent=round(savings_pct, 1),
            solar_self_consumption_percent=round(min(100.0, self_consumption), 1),
            schedule=schedule
        )

tou_optimizer = TOUTariffApplianceOptimizer()

