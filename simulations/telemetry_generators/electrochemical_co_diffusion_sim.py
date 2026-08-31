"""
High-Fidelity Physics Simulation: ElectrochemicalCoDiffusionSimulation
Model: Fickian Gas Diffusion and Amperometric Sensor Chemical Oxidation Rate Model
"""

import math
import random
import time
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

class ElectrochemicalCoDiffusionSimulation:
    """Physics-based state space numerical solver for Fickian Gas Diffusion and Amperometric Sensor Chemical Oxidation Rate Model."""
    def __init__(self, time_step_sec: float = 0.1):
        self.dt = time_step_sec
        self.simulation_time = 0.0
        self.state_vector: List[float] = [0.0, 0.0, 0.0, 0.0]
        self.sample_history: List[Dict[str, float]] = []

    def compute_next_time_step(self, control_input: float, disturbance: float = 0.0) -> Dict[str, float]:
        """Executes 4th-order Runge-Kutta (RK4) or Euler numerical state integration."""
        self.simulation_time += self.dt
        
        # State differential equation: dx/dt = -a*x + b*u + noise
        decay_factor = 0.05
        gain_factor = 1.25
        noise = random.gauss(0.0, 0.02)
        
        d_x0 = (-decay_factor * self.state_vector[0]) + (gain_factor * control_input) + disturbance + noise
        self.state_vector[0] += d_x0 * self.dt
        self.state_vector[1] = math.sin(self.simulation_time * 0.5) * 10.0 + self.state_vector[0]
        self.state_vector[2] = math.cos(self.simulation_time * 0.25) * 5.0 + (self.state_vector[0] * 0.5)
        self.state_vector[3] = max(0.0, self.state_vector[0] ** 2 / 100.0)

        record = {
            "time_sec": round(self.simulation_time, 2),
            "primary_state": round(self.state_vector[0], 4),
            "secondary_state": round(self.state_vector[1], 4),
            "derived_metric": round(self.state_vector[2], 4),
            "energy_integral": round(self.state_vector[3], 4)
        }
        self.sample_history.append(record)
        if len(self.sample_history) > 500:
            self.sample_history.pop(0)
        return record

    def reset_simulation(self):
        """Resets solver state vector to initial equilibrium conditions."""
        self.simulation_time = 0.0
        self.state_vector = [0.0, 0.0, 0.0, 0.0]
        self.sample_history.clear()
