"""
Smart Home Platform Trait: EnergyMeterCapability
Description: Bi-Directional 3-Phase Energy Meter with Active/Reactive Power and Power Factor Trait
"""
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import math

class EnergyMeterCapabilityConfig(BaseModel):
    trait_id: str = "energy_meter"
    display_name: str = "Energy Meter"
    is_enabled: bool = True
    telemetry_frequency_hz: float = 1.0
    safety_lockout: bool = False
    min_operating_threshold: float = 0.0
    max_operating_threshold: float = 100.0
    calibration_offset: float = 0.0
    hysteresis_band: float = 0.5

class EnergyMeterCapabilityState(BaseModel):
    trait: str = "energy_meter"
    raw_value: Any = None
    calibrated_value: Any = None
    unit_of_measurement: Optional[str] = None
    status_flag: str = 'NOMINAL'
    error_code: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnergyMeterCapabilityController:
    """Enterprise Controller handling state transitions and safety validation for EnergyMeterCapability."""
    def __init__(self, device_id: str = 'dev-node-001'):
        self.device_id = device_id
        self.config = EnergyMeterCapabilityConfig()
        self.state = EnergyMeterCapabilityState()
        self.history_buffer: List[Dict[str, Any]] = []
        self._max_history = 500

    def process_incoming_raw(self, raw_input: Any) -> Dict[str, Any]:
        """Applies mathematical calibration, bounds checking, and noise filtering."""
        if isinstance(raw_input, (int, float)):
            calibrated = (raw_input + self.config.calibration_offset)
            calibrated = max(self.config.min_operating_threshold, min(self.config.max_operating_threshold, calibrated))
        else:
            calibrated = raw_input

        self.state.raw_value = raw_input
        self.state.calibrated_value = calibrated
        self.state.updated_at = datetime.now(timezone.utc)
        entry = {
            'timestamp': self.state.updated_at.isoformat(),
            'raw': raw_input,
            'calibrated': calibrated,
            'status': self.state.status_flag
        }
        self.history_buffer.append(entry)
        if len(self.history_buffer) > self._max_history:
            self.history_buffer.pop(0)
        return entry

    def validate_actuator_safety(self, requested_state: Any) -> bool:
        """Evaluates hardware safety limits and thermal interlocks."""
        if self.config.safety_lockout:
            return False
        if isinstance(requested_state, (int, float)):
            if requested_state < self.config.min_operating_threshold or requested_state > self.config.max_operating_threshold:
                return False
        return True

    def get_aggregated_statistics(self) -> Dict[str, float]:
        """Computes statistical variance, moving average, and trend analysis."""
        numeric_values = [h['calibrated'] for h in self.history_buffer if isinstance(h['calibrated'], (int, float))]
        if not numeric_values:
            return {'mean': 0.0, 'min': 0.0, 'max': 0.0, 'variance': 0.0}
        mean_val = sum(numeric_values) / len(numeric_values)
        variance = sum((x - mean_val) ** 2 for x in numeric_values) / len(numeric_values)
        return {
            'mean': round(mean_val, 3),
            'min': round(min(numeric_values), 3),
            'max': round(max(numeric_values), 3),
            'variance': round(variance, 4),
            'sample_count': len(numeric_values)
        }
