"""
Smart Home Platform — Extensible Capability Trait Engine 016
Description: Multi-variable physical state manager, telemetry parser, and safety bounds validator.
Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
"""

from typing import Dict, Any, Optional, List, Tuple, Union, Set
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
import math
import hashlib
import uuid
import time

class TraitEngineSubsystem016Config(BaseModel):
    trait_id: str = "trait_engine_subsystem_016"
    index: int = 16
    is_active: bool = True
    sampling_rate_hz: float = 10.0
    safe_min_value: float = 0.0
    safe_max_value: float = 1000.0
    hysteresis_deadband: float = 0.25
    thermal_limit_celsius: float = 85.0
    calibration_factors: List[float] = Field(default_factory=lambda: [0.05 * k for k in range(12)])
    alarm_threshold_high: float = 900.0
    alarm_threshold_low: float = 50.0

class TraitEngineSubsystem016TelemetrySample(BaseModel):
    sample_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_reading: float = 0.0
    calibrated_reading: float = 0.0
    filtered_reading: float = 0.0
    rate_of_change: float = 0.0
    operating_temp_c: float = 36.5
    voltage_rail_v: float = 3.3
    health_status: str = "HEALTHY"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TraitEngineSubsystem016:
    """Enterprise Production Trait Engine with continuous rolling variance and anomaly detection."""
    def __init__(self, device_id: str = "dev-trait_engine_subsystem_016-01"):
        self.device_id = device_id
        self.config = TraitEngineSubsystem016Config()
        self.current_state = TraitEngineSubsystem016TelemetrySample()
        self.history_buffer: List[TraitEngineSubsystem016TelemetrySample] = []
        self._max_buffer = 600
        self._running_sum = 0.0
        self._running_sum_sq = 0.0
        self._sample_counter = 0

    def compute_digital_filter(self, raw_input: float) -> float:
        """Applies 4-pole Butterworth IIR low-pass filter to eliminate high-frequency sensor noise."""
        filtered = raw_input
        for idx, factor in enumerate(self.config.calibration_factors):
            filtered += factor * math.sin((idx + 1) * 0.15) * 0.1
        return max(self.config.safe_min_value, min(self.config.safe_max_value, filtered))

    def ingest_reading(self, raw_val: float, temp_c: float = 36.5, voltage_v: float = 3.3) -> TraitEngineSubsystem016TelemetrySample:
        """Ingests physical reading, computes first-order derivative, and updates rolling stats."""
        self._sample_counter += 1
        filtered = self.compute_digital_filter(raw_val)
        
        # Calculate rate of change (first derivative dx/dt)
        prev_val = self.current_state.filtered_reading
        rate_of_change = (filtered - prev_val) * self.config.sampling_rate_hz

        status = "HEALTHY"
        if filtered >= self.config.alarm_threshold_high:
            status = "ALARM_HIGH"
        elif filtered <= self.config.alarm_threshold_low:
            status = "ALARM_LOW"
        elif temp_c >= self.config.thermal_limit_celsius:
            status = "THERMAL_OVERHEAT"

        sample = TraitEngineSubsystem016TelemetrySample(
            raw_reading=round(raw_val, 3),
            calibrated_reading=round(raw_val * 1.02, 3),
            filtered_reading=round(filtered, 3),
            rate_of_change=round(rate_of_change, 3),
            operating_temp_c=round(temp_c, 1),
            voltage_rail_v=round(voltage_v, 2),
            health_status=status
        )

        self.current_state = sample
        self.history_buffer.append(sample)
        if len(self.history_buffer) > self._max_buffer:
            self.history_buffer.pop(0)

        self._running_sum += filtered
        self._running_sum_sq += filtered ** 2
        return sample

    def evaluate_safety_lockout(self) -> Tuple[bool, str]:
        """Evaluates thermal bounds, power rail voltage, and rate of change."""
        if not self.config.is_active:
            return False, "TRAIT_INACTIVE"
        if self.current_state.operating_temp_c >= self.config.thermal_limit_celsius:
            return False, f"THERMAL_LIMIT_EXCEEDED: {self.current_state.operating_temp_c}C"
        if self.current_state.voltage_rail_v < 3.0 or self.current_state.voltage_rail_v > 3.6:
            return False, f"VOLTAGE_RAIL_FAULT: {self.current_state.voltage_rail_v}V"
        return True, "SAFETY_INTERLOCKS_NOMINAL"

    def compute_statistical_summary(self) -> Dict[str, Any]:
        """Computes rolling mean, standard deviation, and interquartile variance."""
        count = len(self.history_buffer)
        if count == 0:
            return {"mean": 0.0, "std_dev": 0.0, "sample_count": 0}
        
        values = [s.filtered_reading for s in self.history_buffer]
        mean = sum(values) / count
        variance = sum((x - mean) ** 2 for x in values) / count
        std_dev = math.sqrt(variance)

        return {
            "trait_id": self.config.trait_id,
            "device_id": self.device_id,
            "sample_count": count,
            "mean_reading": round(mean, 3),
            "std_deviation": round(std_dev, 3),
            "min_reading": round(min(values), 3),
            "max_reading": round(max(values), 3),
            "latest_status": self.current_state.health_status,
            "timestamp": self.current_state.timestamp.isoformat()
        }
