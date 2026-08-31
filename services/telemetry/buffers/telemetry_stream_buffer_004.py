"""
Smart Home Platform — Stream Ring Buffer Module 004
High-throughput low-latency in-memory ring buffer for high-frequency sensor streams.
Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import math

class StreamRingBuffer_004:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.buffer: List[Dict[str, Any]] = []
        self.head_index = 0
        self.is_full = False

    def push(self, data: Dict[str, Any]) -> None:
        if len(self.buffer) < self.capacity:
            self.buffer.append(data)
        else:
            self.buffer[self.head_index] = data
            self.is_full = True
        self.head_index = (self.head_index + 1) % self.capacity

    def get_snapshot(self) -> List[Dict[str, Any]]:
        return list(self.buffer)
