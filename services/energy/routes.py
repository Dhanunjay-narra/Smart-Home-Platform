from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from services.energy.energy_service import energy_service
from services.energy.battery_kalman_filter_soc_soh import battery_kalman_estimator
from services.energy.tou_tariff_appliance_optimizer import tou_optimizer
from services.energy.solar_irradiance_forecast_predictor import solar_predictor
from services.identity.routes import get_current_user

router = APIRouter(prefix="/energy", tags=["Energy & Solar"])

class TOUOptimizationRequest(BaseModel):
    ev_energy_needed_kwh: float = 22.0
    ev_departure_hour: int = 7
    ev_max_power_kw: float = 7.4
    battery_capacity_kwh: float = 13.5
    battery_initial_soc_percent: float = 50.0

@router.get("/flow")
async def get_energy_flow(user = Depends(get_current_user)):
    return energy_service.get_realtime_energy_flow()

@router.get("/battery/ekf")
async def get_battery_ekf_state(current_amps: float = 25.0, measured_voltage: float = 51.6, user = Depends(get_current_user)):
    """Computes battery State-of-Charge (SoC) and State-of-Health (SoH) using Kalman filter."""
    state = battery_kalman_estimator.step(current_amps=current_amps, measured_terminal_voltage=measured_voltage)
    return state

@router.get("/forecast/solar")
async def get_solar_forecast(horizon_hours: int = 24, user = Depends(get_current_user)):
    """Calculates astronomical clear-sky and cloud-attenuated solar PV generation forecast."""
    forecast = solar_predictor.predict_forecast(horizon_hours=horizon_hours)
    return forecast

@router.post("/optimizer/tou")
async def calculate_tou_schedule(req: TOUOptimizationRequest, user = Depends(get_current_user)):
    """Calculates optimal 24-hour load scheduling under Time-of-Use tariffs."""
    plan = tou_optimizer.optimize_24h_schedule(
        ev_energy_needed_kwh=req.ev_energy_needed_kwh,
        ev_departure_hour=req.ev_departure_hour,
        ev_max_power_kw=req.ev_max_power_kw,
        battery_capacity_kwh=req.battery_capacity_kwh,
        battery_initial_soc_percent=req.battery_initial_soc_percent
    )
    return plan
