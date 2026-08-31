"""
Hardware Simulation Node: sim_sensor_node_08
Generates synthetic real-time telemetry for multi-sensor IoT test environments.
"""

import random
import math
import time
from typing import Dict, Any
from datetime import datetime, timezone

class SimulationNode_08:
    def __init__(self, node_id: str = "sim_sensor_node_08"):
        self.node_id = node_id
        self.base_frequency = 1.30
        self.iteration = 0

    def generate_synthetic_telemetry(self) -> Dict[str, Any]:
        self.iteration += 1
        t = time.time()
        # Sine-wave synthetic model with Gaussian noise
        primary_val = 20.0 + 10.0 * math.sin(t * self.base_frequency) + random.gauss(0, 0.2)
        secondary_val = 50.0 + 20.0 * math.cos(t * self.base_frequency * 0.5) + random.gauss(0, 0.5)
        
        return {
            "node_id": self.node_id,
            "sample_index": self.iteration,
            "primary_metric": round(primary_val, 3),
            "secondary_metric": round(secondary_val, 3),
            "signal_rssi_dbm": random.randint(-65, -45),
            "battery_mv": random.randint(3200, 3300),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

sim_node_08 = SimulationNode_08()
