"""
Smart Home Platform — Multi-Property Facility Management Zone 023
Handles air handler unit (AHU) modulation, chilled water loops, and shared building amenities.
Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import math

class BuildingFacilityZone023ZoneSpecs(BaseModel):
    zone_id: str = "building_facility_zone_023"
    index: int = 23
    floor_area_m2: float = 120.5
    ceiling_height_m: float = 3.2
    max_occupancy_limit: int = 15
    current_occupant_count: int = 0
    target_cfm_airflow: float = 450.0
    chilled_water_valve_pct: float = 40.0
    air_quality_index_target: int = 30

class BuildingFacilityZone023:
    """Commercial & Multi-Property HVAC and Access Zone Controller."""
    def __init__(self):
        self.specs = BuildingFacilityZone023ZoneSpecs()
        self.supply_air_temp_c = 14.5
        self.return_air_temp_c = 23.8
        self.static_pressure_pa = 245.0

    def compute_ventilation_demand(self, co2_ppm: float, voc_ppb: float) -> Dict[str, Any]:
        """Modulates Variable Air Volume (VAV) dampers based on dynamic indoor air quality."""
        damper_open_pct = 20.0
        if co2_ppm > 1000.0:
            damper_open_pct = min(100.0, 20.0 + (co2_ppm - 1000.0) * 0.1)
        elif voc_ppb > 250.0:
            damper_open_pct = min(100.0, damper_open_pct + 30.0)

        self.specs.target_cfm_airflow = damper_open_pct * 10.0
        return {
            "zone_id": self.specs.zone_id,
            "co2_ppm": co2_ppm,
            "voc_ppb": voc_ppb,
            "vav_damper_position_pct": round(damper_open_pct, 1),
            "calculated_airflow_cfm": round(self.specs.target_cfm_airflow, 1),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
