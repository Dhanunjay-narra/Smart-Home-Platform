"""
Smart Home Platform — Device Model: RobotLawnMowerDeviceModel
Enterprise-grade device lifecycle, state machine, safety interlock, and telemetry codec.
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import math
import hashlib
import uuid

class RobotLawnMowerDeviceModelConfiguration(BaseModel):
    device_type: str = "robot_lawn_mower"
    hardware_revision: str = "REV_2.4"
    firmware_target: str = "FW_UNIVERSAL_V24"
    telemetry_interval_sec: int = 5
    safe_operating_min: float = 0.0
    safe_operating_max: float = 100.0
    nominal_operating_point: float = 50.0
    thermal_limit_c: float = 85.0
    emergency_lockout_enabled: bool = True
    calibration_polynomial: List[float] = Field(default_factory=lambda: [0.0, 1.0, 0.0])

class RobotLawnMowerDeviceModelTelemetry(BaseModel):
    reading_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_signal: float = 0.0
    calibrated_value: float = 0.0
    thermal_temp_c: float = 35.0
    supply_voltage_v: float = 230.0
    current_amperes: float = 0.5
    power_watts: float = 115.0
    power_factor: float = 0.98
    status_flags: int = 0
    error_counter: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RobotLawnMowerDeviceModelDriver:
    """Enterprise device driver handling communication, telemetry processing, and safety loops."""
    def __init__(self, device_id: str = "dev-robot_lawn_mower-01"):
        self.device_id = device_id
        self.config = RobotLawnMowerDeviceModelConfiguration()
        self.telemetry = RobotLawnMowerDeviceModelTelemetry()
        self.state_history: List[RobotLawnMowerDeviceModelTelemetry] = []
        self.is_interlocked: bool = False
        self.total_energy_consumed_kwh: float = 0.0

    def compute_polynomial_calibration(self, raw_val: float) -> float:
        """Applies quadratic polynomial calibration curve: y = a0 + a1*x + a2*x^2"""
        p = self.config.calibration_polynomial
        a0 = p[0] if len(p) > 0 else 0.0
        a1 = p[1] if len(p) > 1 else 1.0
        a2 = p[2] if len(p) > 2 else 0.0
        calibrated = a0 + (a1 * raw_val) + (a2 * (raw_val ** 2))
        return max(self.config.safe_operating_min, min(self.config.safe_operating_max, calibrated))

    def ingest_sensor_frame(self, raw_input: float, temp_c: float = 35.0, voltage_v: float = 230.0) -> RobotLawnMowerDeviceModelTelemetry:
        """Ingests raw physical ADC reading and updates calibrated telemetry state."""
        if temp_c > self.config.thermal_limit_c:
            self.is_interlocked = True
            print(f"[Safety Warning] Thermal limit exceeded on {self.device_id}: {temp_c}C > {self.config.thermal_limit_c}C")

        cal_val = self.compute_polynomial_calibration(raw_input)
        power_w = (voltage_v * 0.5 * 0.98) if cal_val > 0 else 0.0
        self.total_energy_consumed_kwh += (power_w * (self.config.telemetry_interval_sec / 3600.0)) / 1000.0

        t = RobotLawnMowerDeviceModelTelemetry(
            raw_signal=raw_input,
            calibrated_value=round(cal_val, 3),
            thermal_temp_c=round(temp_c, 2),
            supply_voltage_v=round(voltage_v, 1),
            current_amperes=0.5 if cal_val > 0 else 0.0,
            power_watts=round(power_w, 2),
            power_factor=0.98,
            status_flags=1 if self.is_interlocked else 0
        )
        self.telemetry = t
        self.state_history.append(t)
        if len(self.state_history) > 300:
            self.state_history.pop(0)
        return t

    def execute_command_validated(self, command: str, parameter: Any) -> Tuple[bool, str]:
        """Executes control command with safety verification and bounds enforcement."""
        if self.is_interlocked and self.config.emergency_lockout_enabled:
            return False, "DEVICE_THERMALLY_INTERLOCKED"

        if command == "set_level":
            if not isinstance(parameter, (int, float)):
                return False, "INVALID_PARAMETER_TYPE"
            if parameter < self.config.safe_operating_min or parameter > self.config.safe_operating_max:
                return False, f"VALUE_OUT_OF_BOUNDS: [{self.config.safe_operating_min}, {self.config.safe_operating_max}]"
            self.telemetry.calibrated_value = float(parameter)
            return True, "COMMAND_EXECUTED"

        elif command == "reset_interlock":
            self.is_interlocked = False
            return True, "INTERLOCK_CLEARED"

        return False, f"UNKNOWN_COMMAND: {command}"

    def export_diagnostic_report(self) -> Dict[str, Any]:
        """Exports comprehensive hardware diagnostics and health score."""
        sample_count = len(self.state_history)
        mean_power = sum(s.power_watts for s in self.state_history) / max(1, sample_count)
        return {
            "device_id": self.device_id,
            "device_type": self.config.device_type,
            "is_interlocked": self.is_interlocked,
            "total_samples": sample_count,
            "mean_power_watts": round(mean_power, 2),
            "total_kwh": round(self.total_energy_consumed_kwh, 4),
            "latest_reading": self.telemetry.model_dump(mode="json"),
            "health_score_percent": 99.0 if not self.is_interlocked else 65.0
        }
