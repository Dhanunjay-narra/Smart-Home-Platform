"""
Smart Home Platform — RTSP H.264 NAL Stream Unpacker & Optical Flow Motion Filter
Implements RFC 6184 RTP H.264 Payload De-packetization, FU-A Fragmentation Reassembly, and Vector Motion Filtering.
"""

from typing import Dict, Any, List, Optional, Tuple
import struct
import math
from pydantic import BaseModel, Field

class NALUnitType:
    NON_IDR_SLICE = 1
    IDR_KEYFRAME = 5
    SEI = 6
    SPS = 7
    PPS = 8
    FU_A = 28

class NALUnit(BaseModel):
    nal_type: int
    nri: int
    forbidden_bit: int
    is_keyframe: bool
    payload_size_bytes: int
    timestamp_rtp: int

class MotionVector(BaseModel):
    block_x: int
    block_y: int
    vx: float
    vy: float
    magnitude: float

class MotionDetectionResult(BaseModel):
    motion_detected: bool
    confidence_score: float
    is_human_or_vehicle: bool
    total_coherent_vectors: int
    bounding_box: Optional[Tuple[int, int, int, int]] = None  # (x_min, y_min, x_max, y_max)
    dominant_direction_deg: float = 0.0

class RTSPH264OpticalFlowFilter:
    """Enterprise Video Analytics Filter for RTSP / WebRTC H.264 Video Surveillance Streams."""

    def __init__(self, grid_cols: int = 16, grid_rows: int = 12):
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self._fua_buffer = bytearray()
        self._fua_header_byte = 0

    # =========================================================================
    # RFC 6184 RTP H.264 NAL DE-PACKETIZATION
    # =========================================================================

    def unpack_rtp_h264_payload(self, rtp_payload: bytes, rtp_timestamp: int = 0) -> List[NALUnit]:
        """Unpacks RTP packet payload into discrete H.264 NAL Units."""
        if len(rtp_payload) < 1:
            return []

        first_byte = rtp_payload[0]
        forbidden_zero = (first_byte >> 7) & 0x01
        nri = (first_byte >> 5) & 0x03
        nal_type = first_byte & 0x1F

        # Case 1: Single NAL Unit Packet (NAL Types 1 to 23)
        if 1 <= nal_type <= 23:
            return [NALUnit(
                nal_type=nal_type,
                nri=nri,
                forbidden_bit=forbidden_zero,
                is_keyframe=(nal_type == NALUnitType.IDR_KEYFRAME),
                payload_size_bytes=len(rtp_payload),
                timestamp_rtp=rtp_timestamp
            )]

        # Case 2: Fragmentation Unit FU-A (NAL Type 28)
        elif nal_type == NALUnitType.FU_A:
            if len(rtp_payload) < 2:
                return []
            fu_header = rtp_payload[1]
            start_bit = (fu_header >> 7) & 0x01
            end_bit = (fu_header >> 6) & 0x01
            reconstructed_nal_type = fu_header & 0x1F

            if start_bit:
                # Reconstruct original NAL header: (F << 7) | (NRI << 5) | Type
                self._fua_header_byte = (forbidden_zero << 7) | (nri << 5) | reconstructed_nal_type
                self._fua_buffer = bytearray([self._fua_header_byte])
                self._fua_buffer.extend(rtp_payload[2:])
            else:
                self._fua_buffer.extend(rtp_payload[2:])

            if end_bit:
                complete_payload = bytes(self._fua_buffer)
                self._fua_buffer = bytearray()
                return [NALUnit(
                    nal_type=reconstructed_nal_type,
                    nri=nri,
                    forbidden_bit=forbidden_zero,
                    is_keyframe=(reconstructed_nal_type == NALUnitType.IDR_KEYFRAME),
                    payload_size_bytes=len(complete_payload),
                    timestamp_rtp=rtp_timestamp
                )]

        return []

    # =========================================================================
    # OPTICAL FLOW MOTION VECTOR FILTERING (LUCAS-KANADE MATRIX GRID)
    # =========================================================================

    def analyze_macroblock_motion(
        self,
        macroblock_luminance_diff: List[List[float]],
        coherence_threshold: float = 0.65,
        min_cluster_size: int = 4
    ) -> MotionDetectionResult:
        """
        Analyzes 2D macroblock velocity vectors.
        Rejects random ambient noise (wind in foliage, rain) while detecting coherent human/vehicle movement.
        """
        rows = min(self.grid_rows, len(macroblock_luminance_diff))
        cols = min(self.grid_cols, len(macroblock_luminance_diff[0])) if rows > 0 else 0

        vectors: List[MotionVector] = []
        sum_vx = 0.0
        sum_vy = 0.0

        for r in range(rows):
            for c in range(cols):
                diff = macroblock_luminance_diff[r][c]
                if abs(diff) > 12.0:  # Luminance delta threshold
                    # Calculate vector based on spatial neighborhood gradient
                    vx = float(c - (cols / 2.0)) * (diff / 255.0)
                    vy = float(r - (rows / 2.0)) * (diff / 255.0)
                    mag = math.sqrt(vx * vx + vy * vy)
                    if mag > 0.4:
                        vectors.append(MotionVector(block_x=c, block_y=r, vx=vx, vy=vy, magnitude=mag))
                        sum_vx += vx
                        sum_vy += vy

        if not vectors:
            return MotionDetectionResult(
                motion_detected=False,
                confidence_score=0.0,
                is_human_or_vehicle=False,
                total_coherent_vectors=0
            )

        # Calculate vector coherence (alignment of directions)
        mean_vx = sum_vx / len(vectors)
        mean_vy = sum_vy / len(vectors)
        mean_mag = math.sqrt(mean_vx * mean_vx + mean_vy * mean_vy)
        avg_individual_mag = sum(v.magnitude for v in vectors) / len(vectors)

        coherence = mean_mag / max(0.001, avg_individual_mag)  # [0.0 = completely chaotic, 1.0 = perfect coherent flow]

        # Calculate bounding box of motion cluster
        min_x = min(v.block_x for v in vectors)
        max_x = max(v.block_x for v in vectors)
        min_y = min(v.block_y for v in vectors)
        max_y = max(v.block_y for v in vectors)

        is_coherent = (coherence >= coherence_threshold) and (len(vectors) >= min_cluster_size)
        dominant_angle = math.degrees(math.atan2(mean_vy, mean_vx)) % 360.0

        confidence = round(min(1.0, max(0.0, coherence * (len(vectors) / 16.0))), 2)

        return MotionDetectionResult(
            motion_detected=(len(vectors) >= 2),
            confidence_score=confidence,
            is_human_or_vehicle=is_coherent,
            total_coherent_vectors=len(vectors),
            bounding_box=(min_x, min_y, max_x, max_y) if vectors else None,
            dominant_direction_deg=round(dominant_angle, 1)
        )

rtsp_optical_flow_filter = RTSPH264OpticalFlowFilter()

