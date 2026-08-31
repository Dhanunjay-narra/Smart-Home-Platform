"""
Smart Home Platform — Advanced Protocol Frame Encoder 017
Handles binary message serialization, CRC checksum validation, and stream packet framing.
Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
"""

from typing import Dict, Any, List, Optional, Tuple
import struct
import binascii
from datetime import datetime, timezone

class ProtocolFrameEncoder017:
    """Protocol frame encoder with bitwise parity and packet sequence serialization."""
    def __init__(self):
        self.encoder_id = "protocol_frame_encoder_017"
        self.tx_packet_count = 0
        self.rx_packet_count = 0

    def pack_binary_telemetry(self, node_id: int, channel: int, value: float) -> bytes:
        """Packs floating point telemetry into network byte order binary frame."""
        payload = struct.pack('>BBf', node_id, channel, value)
        checksum = 0
        for b in payload:
            checksum ^= b
        frame = payload + bytes([checksum])
        self.tx_packet_count += 1
        return frame

    def unpack_binary_telemetry(self, frame_bytes: bytes) -> Tuple[bool, Dict[str, Any]]:
        """Validates checksum and extracts node, channel, and value fields."""
        if len(frame_bytes) < 7:
            return False, {"error": "FRAME_UNDERFLOW"}
        
        payload = frame_bytes[:-1]
        received_cs = frame_bytes[-1]
        expected_cs = 0
        for b in payload:
            expected_cs ^= b

        if received_cs != expected_cs:
            return False, {"error": "CHECKSUM_ERROR"}

        node_id, channel, val = struct.unpack('>BBf', payload)
        self.rx_packet_count += 1
        return True, {
            "node_id": node_id,
            "channel": channel,
            "value": round(val, 4),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
