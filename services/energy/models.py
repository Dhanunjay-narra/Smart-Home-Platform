from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class EnergyFlow(BaseModel):
    solar_generation_kw: float
    battery_charge_kw: float
    battery_soc_percent: float
    grid_import_kw: float
    home_consumption_kw: float
    ev_charging_kw: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
