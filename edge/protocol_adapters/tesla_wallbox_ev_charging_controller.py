"""
Smart Home Platform — Tesla Wallbox & EV Smart Charging Controller
Implements CAN Bus Frame Parsing, IEC 61851 Pilot Signaling, and Dynamic Current Throttling (6A to 32A).
"""

from typing import Dict, Any, Optional, Tuple
import struct
import math
from pydantic import BaseModel, Field
from enum import Enum

class PilotState(str, Enum):
    A_STANDBY = "A_STANDBY"            # +12V DC (Vehicle not connected)
    B_CONNECTED = "B_CONNECTED"        # +9V DC (Connected, ready to charge)
    C_CHARGING = "C_CHARGING"          # +6V DC (Charging active with ventilation)
    D_VENT_REQ = "D_VENT_REQ"          # +3V DC (Ventilation required)
    E_ERROR = "E_ERROR"                # 0V (Pilot short to ground / fault)
    F_NO_POWER = "F_NO_POWER"          # EVSE disconnect

class ChargingMode(str, Enum):
    SOLAR_SURPLUS_ONLY = "SOLAR_SURPLUS_ONLY"  # 100% Green Solar energy
    FAST_BOOST = "FAST_BOOST"                  # Maximum 32A charging
    TOU_SCHEDULED = "TOU_SCHEDULED"            # Lowest tariff charging window

class EVTelemetry(BaseModel):
    pack_voltage_v: float = 398.2
    pack_current_a: float = 0.0
    soc_percent: float = 68.5
    battery_temp_c: float = 24.5
    pilot_state: PilotState = PilotState.B_CONNECTED
    pwm_duty_cycle_percent: float = 0.0
    allowed_current_a: float = 0.0
    energy_delivered_kwh: float = 14.8
    fault_code: int = 0

class TeslaWallboxEVController:
    """Enterprise EV Smart Charging Controller with Dynamic Grid/Solar Load Throttling."""

    MIN_CURRENT_AMPS = 6.0    # IEC 61851 standard minimum pilot current
    MAX_CURRENT_AMPS = 32.0   # 7.4 kW Single Phase / 22 kW 3-Phase standard limit
    GRID_VOLTAGE_V = 230.0    # RMS AC Phase Voltage
    PHASES = 1                # 1 for Single Phase, 3 for 3-Phase

    def __init__(self, wallbox_id: str = "ev-wallbox-garage-01"):
        self.wallbox_id = wallbox_id
        self.telemetry = EVTelemetry()
        self.charging_mode = ChargingMode.SOLAR_SURPLUS_ONLY
        self.target_departure_soc = 85.0
        self.current_setpoint_a = 0.0

    # =========================================================================
    # CAN BUS FRAME PARSING (0x102, 0x212, 0x318)
    # =========================================================================

    def parse_can_frame(self, can_id: int, payload: bytes) -> Dict[str, Any]:
        """Decode raw 8-byte CAN Bus payloads from EV BMS and Wallbox."""
        if len(payload) < 8:
            return {"error": "Invalid CAN frame length"}

        # 0x102: BMS High-Voltage Pack Voltage & Current
        if can_id == 0x102:
            raw_v, raw_i = struct.unpack("!Hh4x", payload)  # uint16 (0.1V), int16 (0.1A)
            self.telemetry.pack_voltage_v = round(raw_v * 0.1, 1)
            self.telemetry.pack_current_a = round(raw_i * 0.1, 1)
            return {
                "can_id": "0x102",
                "voltage_v": self.telemetry.pack_voltage_v,
                "current_a": self.telemetry.pack_current_a
            }

        # 0x212: BMS State-of-Charge and Battery Temperature
        elif can_id == 0x212:
            raw_soc, raw_temp, raw_fault = struct.unpack("!BBH4x", payload)
            self.telemetry.soc_percent = round(raw_soc * 0.5, 1)  # 0.5% resolution
            self.telemetry.battery_temp_c = raw_temp - 40.0       # -40C offset
            self.telemetry.fault_code = raw_fault
            return {
                "can_id": "0x212",
                "soc_percent": self.telemetry.soc_percent,
                "battery_temp_c": self.telemetry.battery_temp_c,
                "fault_code": raw_fault
            }

        # 0x318: EVSE Pilot Control & PWM Duty Cycle
        elif can_id == 0x318:
            raw_pilot, raw_duty, raw_kwh = struct.unpack("!BBH4x", payload)
            state_map = {
                12: PilotState.A_STANDBY,
                9: PilotState.B_CONNECTED,
                6: PilotState.C_CHARGING,
                3: PilotState.D_VENT_REQ,
                0: PilotState.E_ERROR
            }
            self.telemetry.pilot_state = state_map.get(raw_pilot, PilotState.E_ERROR)
            self.telemetry.pwm_duty_cycle_percent = raw_duty * 0.5
            self.telemetry.allowed_current_a = self.pwm_duty_to_amps(self.telemetry.pwm_duty_cycle_percent)
            self.telemetry.energy_delivered_kwh = round(raw_kwh * 0.01, 2)
            return {
                "can_id": "0x318",
                "pilot_state": self.telemetry.pilot_state,
                "allowed_current_a": self.telemetry.allowed_current_a,
                "energy_kwh": self.telemetry.energy_delivered_kwh
            }

        return {"can_id": hex(can_id), "status": "UNKNOWN_ID"}

    # =========================================================================
    # IEC 61851 PILOT DUTY CYCLE MATH
    # =========================================================================

    @staticmethod
    def amps_to_pwm_duty(amps: float) -> float:
        """Convert current in Amperes to IEC 61851 PWM duty cycle percentage."""
        if amps < 6.0:
            return 0.0  # 0% duty = charging disabled
        elif 6.0 <= amps <= 51.0:
            return amps / 0.6  # Duty = Amps / 0.6 (e.g. 16A = 26.66% duty, 32A = 53.33% duty)
        elif 51.0 < amps <= 80.0:
            return (amps / 2.5) + 64.0
        else:
            return 100.0

    @staticmethod
    def pwm_duty_to_amps(duty: float) -> float:
        """Convert IEC 61851 PWM duty cycle percentage to allowable Amperes."""
        if duty < 10.0:
            return 0.0
        elif 10.0 <= duty <= 85.0:
            return duty * 0.6
        elif 85.0 < duty <= 96.0:
            return (duty - 64.0) * 2.5
        else:
            return 0.0

    # =========================================================================
    # DYNAMIC LOAD BALANCING & CURRENT THROTTLING
    # =========================================================================

    def calculate_optimal_charging_current(
        self,
        solar_generation_kw: float,
        home_base_load_kw: float,
        grid_import_limit_kw: float = 7.0,
        electricity_tariff_per_kwh: float = 0.15
    ) -> float:
        """Dynamically computes the safe, cost-optimized EVSE current limit (6A to 32A)."""
        if self.telemetry.soc_percent >= self.target_departure_soc:
            self.current_setpoint_a = 0.0
            return 0.0

        if self.charging_mode == ChargingMode.FAST_BOOST:
            self.current_setpoint_a = self.MAX_CURRENT_AMPS
            return self.MAX_CURRENT_AMPS

        # 1. Available power calculation
        solar_surplus_kw = max(0.0, solar_generation_kw - home_base_load_kw)

        if self.charging_mode == ChargingMode.SOLAR_SURPLUS_ONLY:
            # Only charge from solar surplus
            power_available_kw = solar_surplus_kw
        else:
            # TOU Scheduled mode: Use solar surplus + grid allowance
            grid_allowance_kw = max(0.0, grid_import_limit_kw - home_base_load_kw)
            power_available_kw = solar_surplus_kw + grid_allowance_kw

        # 2. Convert power (kW) to Amps: P = V * I * sqrt(phases)
        raw_amps = (power_available_kw * 1000.0) / (self.GRID_VOLTAGE_V * math.sqrt(self.PHASES))

        # 3. Apply IEC 61851 6A threshold
        if raw_amps < self.MIN_CURRENT_AMPS:
            target_amps = 0.0  # Pause charging if surplus < 6A (1.38 kW)
        else:
            target_amps = min(self.MAX_CURRENT_AMPS, raw_amps)

        # 4. Slew rate limit to prevent contactor hunting
        slew_limit = 2.0  # Max 2A step change per control cycle
        if self.current_setpoint_a == 0.0 and target_amps >= self.MIN_CURRENT_AMPS:
            self.current_setpoint_a = target_amps
        else:
            if target_amps > self.current_setpoint_a:
                self.current_setpoint_a = min(target_amps, self.current_setpoint_a + slew_limit)
            else:
                self.current_setpoint_a = max(target_amps, self.current_setpoint_a - slew_limit)

        return round(self.current_setpoint_a, 1)

tesla_ev_controller = TeslaWallboxEVController()
