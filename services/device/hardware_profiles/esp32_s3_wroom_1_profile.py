"""
Hardware Architecture Profile: Esp32S3Wroom1Profile
Target: Espressif Dual-Core Xtensa LX7 with 8MB Flash & 8MB PSRAM for Matter/Wi-Fi/BLE
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import math

class Esp32S3Wroom1ProfileMemoryMap(BaseModel):
    flash_size_bytes: int = 8388608
    sram_size_bytes: int = 524288
    psram_size_bytes: int = 8388608
    bootloader_offset: str = "0x00000000"
    partition_table_offset: str = "0x00008000"
    nvs_storage_offset: str = "0x00009000"
    ota_0_app_offset: str = "0x00020000"
    ota_1_app_offset: str = "0x00200000"
    spiffs_storage_offset: str = "0x00400000"

class Esp32S3Wroom1ProfilePowerProfile(BaseModel):
    supply_voltage_nominal_mv: int = 3300
    active_tx_current_ma: float = 240.0
    active_rx_current_ma: float = 95.0
    modem_sleep_current_ma: float = 25.0
    light_sleep_current_ma: float = 0.8
    deep_sleep_current_ua: float = 10.0
    rtc_hibernation_current_ua: float = 2.5

class Esp32S3Wroom1Profile:
    """Hardware board diagnostics, power budgeting, and register abstraction."""
    def __init__(self, board_id: str = "brd-esp32_s3_wroom_1-01"):
        self.board_id = board_id
        self.memory_map = Esp32S3Wroom1ProfileMemoryMap()
        self.power_profile = Esp32S3Wroom1ProfilePowerProfile()
        self.runtime_hours = 0.0
        self.deep_sleep_cycles = 0

    def compute_battery_runtime_days(self, battery_capacity_mah: float, active_duty_cycle_pct: float) -> float:
        """Calculates theoretical battery operating lifetime given operational duty cycle."""
        active_ratio = active_duty_cycle_pct / 100.0
        sleep_ratio = 1.0 - active_ratio
        
        avg_current_ma = (self.power_profile.active_tx_current_ma * active_ratio) + \
                         (self.power_profile.deep_sleep_current_ua / 1000.0 * sleep_ratio)
        
        total_hours = battery_capacity_mah / max(0.001, avg_current_ma)
        return round(total_hours / 24.0, 2)

    def validate_firmware_binary_bounds(self, binary_size_bytes: int) -> bool:
        """Ensures compiled binary fits within allocated OTA partition boundaries."""
        max_partition_size = 0x00200000 - 0x00020000 # ~1.9MB
        return binary_size_bytes <= max_partition_size

    def generate_board_telemetry_snapshot(self) -> Dict[str, Any]:
        """Returns board diagnostic snapshot including memory utilization."""
        return {
            "board_id": self.board_id,
            "target_mcu": "esp32_s3_wroom_1",
            "flash_total_kb": self.memory_map.flash_size_bytes // 1024,
            "sram_total_kb": self.memory_map.sram_size_bytes // 1024,
            "psram_total_kb": self.memory_map.psram_size_bytes // 1024,
            "nominal_voltage_v": self.power_profile.supply_voltage_nominal_mv / 1000.0,
            "runtime_hours": self.runtime_hours,
            "deep_sleep_count": self.deep_sleep_cycles,
            "status": "ONLINE_HEALTHY"
        }
