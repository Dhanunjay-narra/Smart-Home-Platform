"""
Smart Home Platform — Protocol Codec: BacnetIpAnalogValueCodec
Standard: BACnet/IP Annex J Analog Value (AV) and Binary Value (BV) object handler
"""

from typing import Dict, Any, Optional, List, Tuple
import struct
import binascii
from datetime import datetime, timezone

class BacnetIpAnalogValueCodec:
    """High-performance binary & text protocol serializer/deserializer for BACnet/IP Annex J Analog Value (AV) and Binary Value (BV) object handler."""
    def __init__(self, port_identifier: str = "port-0"):
        self.port_id = port_identifier
        self.rx_frames = 0
        self.tx_frames = 0
        self.crc_errors = 0

    def compute_crc16_modbus(self, data: bytes) -> int:
        """Standard CRC-16 polynomial 0xA001 calculation."""
        crc = 0xFFFF
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        return crc

    def serialize_request_frame(self, unit_id: int, func_code: int, register_addr: int, count: int) -> bytes:
        """Packs standard request frame with address header and checksum."""
        pdu = struct.pack('>BBHH', unit_id, func_code, register_addr, count)
        crc = self.compute_crc16_modbus(pdu)
        frame = pdu + struct.pack('<H', crc)
        self.tx_frames += 1
        return frame

    def parse_response_frame(self, raw_bytes: bytes) -> Tuple[bool, Dict[str, Any]]:
        """Validates CRC and decodes response register values into numeric arrays."""
        if len(raw_bytes) < 5:
            self.crc_errors += 1
            return False, {"error": "FRAME_INCOMPLETE"}

        pdu = raw_bytes[:-2]
        received_crc = struct.unpack('<H', raw_bytes[-2:])[0]
        expected_crc = self.compute_crc16_modbus(pdu)
        if received_crc != expected_crc:
            self.crc_errors += 1
            return False, {"error": "CRC_VERIFICATION_FAILED", "expected": expected_crc, "got": received_crc}

        unit_id, func_code, byte_count = struct.unpack('>BBB', pdu[:3])
        data_payload = pdu[3:]
        self.rx_frames += 1

        return True, {
            "unit_id": unit_id,
            "function_code": func_code,
            "byte_count": byte_count,
            "payload_hex": binascii.hexlify(data_payload).decode('ascii'),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "VALID"
        }
