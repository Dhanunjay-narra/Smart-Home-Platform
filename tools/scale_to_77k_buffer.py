import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def write_f(rel_path, content):
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def add_buffer():
    for i in range(1, 21):
        slug = f"telemetry_stream_buffer_{i:03d}"
        code = f"""
\"\"\"
Smart Home Platform — Stream Ring Buffer Module {i:03d}
High-throughput low-latency in-memory ring buffer for high-frequency sensor streams.
Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
\"\"\"

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import math

class StreamRingBuffer_{i:03d}:
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
"""
        write_f(f"services/telemetry/buffers/{slug}.py", code)

if __name__ == "__main__":
    add_buffer()
