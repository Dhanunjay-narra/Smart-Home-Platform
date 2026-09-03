"""
Smart Home Platform — SolarEdge & Enphase Solar Inverter Adapter
Implements SunSpec Modbus Register Mapping, Scale Factor Calculations, and Sandia DC-to-AC Inverter Efficiency Models.
"""

from typing import Dict, Any, Optional, List, Tuple
import struct
import math
from pydantic import BaseModel, Field

class InverterStatus:
    OFF = 1
    SLEEPING = 2
    STARTING = 3
    MPPT_TRACKING = 4
    THROTTLED = 5
    SHUTTING_DOWN = 6
    FAULT = 7
    STANDBY = 8

class SunSpecInverterTelemetry(BaseModel):
    inverter_id: str = "solaredge-se7600h-01"
    manufacturer: str = "SolarEdge Technologies"
    model: str = "SE7600H-US"
    firmware_version: str = "4.18.32"
    serial_number: str = "SF29048172"
    ac_power_w: float = 4850.0
    ac_voltage_v: float = 240.2
    ac_current_a: float = 20.19
    ac_frequency_hz: float = 60.01
    total_energy_wh: float = 14280500.0
    dc_power_w: float = 5020.0
    dc_voltage_v: float = 385.0
    dc_current_a: float = 13.04
    heatsink_temp_c: float = 44.5
    status: int = InverterStatus.MPPT_TRACKING
    efficiency_percent: float = 96.61
    mppt_strings: List[Dict[str, float]] = []

class SolarEdgeEnphaseInverterAdapter:
    """SunSpec Modbus protocol decoder and DC-to-AC conversion efficiency analyzer."""

    def __init__(self, inverter_id: str = "solaredge-se7600h-01"):
        self.inverter_id = inverter_id
        self.telemetry = SunSpecInverterTelemetry(
            inverter_id=inverter_id,
            mppt_strings=[
                {"string_id": 1, "voltage_v": 385.0, "current_a": 6.52, "power_w": 2510.2},
                {"string_id": 2, "voltage_v": 384.8, "current_a": 6.52, "power_w": 2508.8}
            ]
        )

    # =========================================================================
    # SUNSPEC MODBUS REGISTER MAPPING & SCALE FACTOR PARSING
    # =========================================================================

    @staticmethod
    def apply_sunspec_scale(raw_val: int, scale_factor: int) -> float:
        """SunSpec standard: Physical = RawValue * 10^(ScaleFactor), where scale_factor is signed int16."""
        # Convert unsigned 16-bit to signed if needed
        if scale_factor > 32767:
            scale_factor -= 65536
        if raw_val > 32767:
            raw_val -= 65536
        
        # 0x8000 (-32768) represents Not Implemented in SunSpec
        if raw_val == -32768 or scale_factor == -32768:
            return 0.0

        return round(float(raw_val) * (10.0 ** scale_factor), 3)

    def decode_sunspec_model_101_single_phase(self, registers: List[int]) -> SunSpecInverterTelemetry:
        """Decode SunSpec Model 101/103 (Inverter Single Phase / Three Phase) 50-register block."""
        if len(registers) < 50:
            return self.telemetry

        # Register map offsets according to SunSpec Inverter Model 101 Specification:
        # Offsets:
        # 2: AC Current (uint16), 6: Current Scale (int16)
        # 7: AC Voltage (uint16), 10: Voltage Scale (int16)
        # 11: AC Power (int16), 12: Power Scale (int16)
        # 13: AC Frequency (uint16), 14: Frequency Scale (int16)
        # 21: DC Current (uint16), 22: DC Current Scale (int16)
        # 23: DC Voltage (uint16), 24: DC Voltage Scale (int16)
        # 25: DC Power (int16), 26: DC Power Scale (int16)
        # 27: Heatsink Temp (int16), 30: Temp Scale (int16)
        # 31: Status (uint16)

        ac_curr = self.apply_sunspec_scale(registers[2], registers[6])
        ac_volt = self.apply_sunspec_scale(registers[7], registers[10])
        ac_power = self.apply_sunspec_scale(registers[11], registers[12])
        ac_freq = self.apply_sunspec_scale(registers[13], registers[14])
        
        dc_curr = self.apply_sunspec_scale(registers[21], registers[22])
        dc_volt = self.apply_sunspec_scale(registers[23], registers[24])
        dc_power = self.apply_sunspec_scale(registers[25], registers[26])
        temp_c = self.apply_sunspec_scale(registers[27], registers[30])
        status = registers[31]

        eff = (ac_power / max(0.1, dc_power)) * 100.0 if dc_power > 0 else 0.0

        self.telemetry.ac_current_a = ac_curr
        self.telemetry.ac_voltage_v = ac_volt
        self.telemetry.ac_power_w = ac_power
        self.telemetry.ac_frequency_hz = ac_freq
        self.telemetry.dc_current_a = dc_curr
        self.telemetry.dc_voltage_v = dc_volt
        self.telemetry.dc_power_w = dc_power
        self.telemetry.heatsink_temp_c = temp_c
        self.telemetry.status = status
        self.telemetry.efficiency_percent = round(min(100.0, max(0.0, eff)), 2)

        return self.telemetry

    # =========================================================================
    # SANDIA / CEC INVERTER EFFICIENCY MODEL
    # =========================================================================

    @staticmethod
    def calculate_sandia_efficiency(
        p_dc_watts: float,
        v_dc_volts: float,
        p_ac0_max_watts: float = 7600.0,
        p_nt_tare_loss_watts: float = 4.5,
        v_dc0_nominal_volts: float = 380.0
    ) -> Tuple[float, float]:
        """
        Calculates theoretical AC power output and CEC conversion efficiency using the Sandia Inverter Model.
        Returns: (ac_power_watts, efficiency_percent)
        """
        if p_dc_watts <= p_nt_tare_loss_watts:
            return 0.0, 0.0

        # Standard Sandia inverter conversion efficiency
        delta_v = (v_dc_volts - v_dc0_nominal_volts) / v_dc0_nominal_volts
        p_dc_eff = p_dc_watts - p_nt_tare_loss_watts

        # Power loss equation (tare loss + conduction loss + switching loss)
        loss = p_nt_tare_loss_watts + (0.022 + 0.002 * abs(delta_v)) * p_dc_eff + 0.006 * (p_dc_eff ** 2) / p_ac0_max_watts
        ac_power = max(0.0, min(p_ac0_max_watts, p_dc_eff - loss))

        efficiency = min(99.0, max(0.0, (ac_power / p_dc_watts) * 100.0))
        return round(ac_power, 1), round(efficiency, 2)

solaredge_inverter_adapter = SolarEdgeEnphaseInverterAdapter()
