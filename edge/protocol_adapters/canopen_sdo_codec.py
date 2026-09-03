"""
Protocol Adapter: CanopenSdoCodec
Standard: CANOpen Service Data Object (SDO) and PDO Frame Codec
"""
from typing import Dict, Any, Optional, List, Tuple
import struct
import binascii
from datetime import datetime, timezone

class CanopenSdoCodec:
    """Industrial & IoT Protocol implementation for CANOpen Service Data Object (SDO) and PDO Frame Codec."""
    def __init__(self, interface_name: str = 'com0'):
        self.interface = interface_name
        self.packet_counter = 0
        self.error_counter = 0
        self.is_connected = True

    def calculate_checksum(self, payload: bytes) -> int:
        """Computes standard CRC16 / ITU-T polynomial checksum."""
        crc = 0xFFFF
        for b in payload:
            crc ^= b
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def encode_frame(self, address: int, function_code: int, data: bytes) -> bytes:
        """Packs structured data into a validated binary protocol frame."""
        header = struct.pack('>BB', address, function_code)
        body = header + data
        crc = self.calculate_checksum(body)
        frame = body + struct.pack('<H', crc)
        self.packet_counter += 1
        return frame

    def decode_frame(self, frame_bytes: bytes) -> Tuple[bool, Dict[str, Any]]:
        """Unpacks binary frame, verifies CRC, and extracts payload fields."""
        if len(frame_bytes) < 4:
            self.error_counter += 1
            return False, {'error': 'FRAME_TOO_SHORT'}

        body = frame_bytes[:-2]
        received_crc = struct.unpack('<H', frame_bytes[-2:])[0]
        expected_crc = self.calculate_checksum(body)
        if received_crc != expected_crc:
            self.error_counter += 1
            return False, {'error': 'CRC_MISMATCH', 'expected': expected_crc, 'got': received_crc}

        addr, func = struct.unpack('>BB', body[:2])
        payload_data = body[2:]
        return True, {
            'address': addr,
            'function_code': func,
            'payload_hex': binascii.hexlify(payload_data).decode('ascii'),
            'length': len(payload_data),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
