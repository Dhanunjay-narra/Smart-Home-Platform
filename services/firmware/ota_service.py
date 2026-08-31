from typing import Dict, Any, List, Optional
from services.firmware.models import FirmwareRelease

FIRMWARE_RELEASES_DB: Dict[str, FirmwareRelease] = {}

class OTAService:
    def __init__(self):
        self._seed_default_release()

    def _seed_default_release(self):
        if not FIRMWARE_RELEASES_DB:
            rel = FirmwareRelease(
                release_id="rel-v240-esp32",
                target_hardware="ESP32-S3",
                version_tag="v2.4.0",
                file_size_bytes=1048576,
                sha256_checksum="4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
            )
            FIRMWARE_RELEASES_DB[rel.release_id] = rel

    def get_latest_release(self, hardware_model: str) -> Optional[FirmwareRelease]:
        matches = [r for r in FIRMWARE_RELEASES_DB.values() if r.target_hardware.lower() in hardware_model.lower()]
        return matches[-1] if matches else None

ota_service = OTAService()
