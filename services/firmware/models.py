from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class FirmwareRelease(BaseModel):
    release_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_hardware: str = "ESP32-S3"
    version_tag: str = "v2.4.0"
    file_size_bytes: int = 1428570
    sha256_checksum: str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    release_notes: str = "Enhanced Matter commissioning and low-power BLE mesh optimization."
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
