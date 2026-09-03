"""
Smart Home Platform — Battery State-of-Charge (SoC) & State-of-Health (SoH) Estimator
Implements Coulomb Counting with Discrete-Time Extended Kalman Filter (EKF) and Capacity Degradation Modeling.
"""

from typing import Dict, Any, List, Tuple
import math
from pydantic import BaseModel, Field

class BatteryEKFState(BaseModel):
    soc: float = Field(default=0.85, ge=0.0, le=1.0)          # State of Charge [0.0 to 1.0]
    v_polarization: float = 0.0                                 # Voltage across RC polarization branch (V)
    terminal_voltage_v: float = 51.8                            # Estimated terminal voltage (V)
    internal_resistance_r0: float = 0.015                       # Ohmic internal resistance (Ohms)
    soh_capacity_percent: float = 98.4                          # State of Health capacity fade (%)
    soh_resistance_percent: float = 96.8                        # State of Health resistance growth (%)
    cumulative_throughput_ah: float = 4850.0                    # Total charge throughput (Ah)
    equivalent_full_cycles: float = 242.5                       # Total full discharge cycles

class BatteryKalmanFilterEstimator:
    """
    Extended Kalman Filter (EKF) on 1-RC Thevenin Equivalent Circuit Model (ECM) for LiFePO4 / NMC Battery Packs.
    Combines high-frequency Coulomb Counting with low-drift Open-Circuit Voltage (OCV) correction.
    """

    def __init__(self, nominal_capacity_ah: float = 200.0, nominal_voltage_v: float = 48.0):
        self.q_nom_ah = nominal_capacity_ah   # Nominal pack capacity in Ampere-hours (e.g., 200 Ah = 9.6 kWh @ 48V)
        self.v_nom = nominal_voltage_v
        self.coulombic_efficiency = 0.995     # Charge/discharge efficiency
        
        # Equivalent Circuit Parameters (1-RC Thevenin Model)
        self.r0 = 0.012                       # Ohmic internal resistance (Ohms)
        self.r1 = 0.008                       # Polarization resistance (Ohms)
        self.c1 = 2500.0                      # Polarization capacitance (Farads) -> tau = R1*C1 = 20s
        self.tau = self.r1 * self.c1

        # EKF State Vector x = [SoC, V1]^T
        self.x = [0.85, 0.0]

        # EKF Covariance Matrices
        # State covariance P
        self.P = [
            [1e-4, 0.0],
            [0.0,  1e-4]
        ]
        # Process noise covariance Q (trust in current integration vs polarization model)
        self.Q = [
            [1e-6, 0.0],
            [0.0,  1e-5]
        ]
        # Measurement noise covariance R (voltage sensor accuracy ~10mV)
        self.R = 1e-3

        # SoH Tracking
        self.cumulative_ah = 4850.0
        self.initial_r0 = 0.012

    # =========================================================================
    # OPEN-CIRCUIT VOLTAGE (OCV-SOC) POLYNOMIAL MODEL FOR LiFePO4 / NMC
    # =========================================================================

    def calculate_ocv(self, soc: float) -> float:
        """
        Evaluates Open-Circuit Voltage as a function of SoC (16S 48V nominal LiFePO4 pack).
        V_ocv(SoC) = a0 + a1*SoC + a2*SoC^2 + a3*SoC^3 + a4*ln(SoC) + a5*ln(1-SoC)
        """
        s = max(0.001, min(0.999, soc))
        
        # 16-cell LiFePO4 characteristic curve coefficients (per pack)
        v_cell = 3.15 + (0.35 * s) + (0.12 * (s ** 2)) - (0.08 * (s ** 3)) + (0.018 * math.log(s)) - (0.015 * math.log(1.0 - s))
        pack_ocv = v_cell * 16.0  # 16 cells in series
        return round(pack_ocv, 3)

    def calculate_docv_dsoc(self, soc: float) -> float:
        """Derivative of OCV with respect to SoC (Jacobian element C[0])."""
        s = max(0.001, min(0.999, soc))
        dv_cell_dsoc = 0.35 + (0.24 * s) - (0.24 * (s ** 2)) + (0.018 / s) + (0.015 / (1.0 - s))
        return dv_cell_dsoc * 16.0

    # =========================================================================
    # EXTENDED KALMAN FILTER PREDICTION & CORRECTION STEP
    # =========================================================================

    def step(self, current_amps: float, measured_terminal_voltage: float, dt_seconds: float = 1.0) -> BatteryEKFState:
        """
        Executes one EKF recursion cycle:
        - current_amps > 0 for discharge, < 0 for charge
        - dt_seconds: sampling period in seconds (typically 1.0s)
        """
        # 1. State Prediction (A priori state estimation)
        soc_prev, v1_prev = self.x[0], self.x[1]

        # Coulomb counting integration
        eta = self.coulombic_efficiency if current_amps < 0 else 1.0
        delta_soc = -(current_amps * eta * (dt_seconds / 3600.0)) / self.q_nom_ah
        soc_pred = max(0.0, min(1.0, soc_prev + delta_soc))

        # RC polarization voltage transition
        exp_decay = math.exp(-dt_seconds / self.tau)
        v1_pred = (exp_decay * v1_prev) + (self.r1 * (1.0 - exp_decay) * current_amps)

        # State transition matrix A
        A = [
            [1.0, 0.0],
            [0.0, exp_decay]
        ]

        # Predicted covariance P_pred = A * P * A^T + Q
        P_pred = [
            [A[0][0]*self.P[0][0]*A[0][0] + self.Q[0][0], A[0][0]*self.P[0][1]*A[1][1]],
            [A[1][1]*self.P[1][0]*A[0][0], A[1][1]*self.P[1][1]*A[1][1] + self.Q[1][1]]
        ]

        # 2. Measurement Update (A posteriori correction)
        ocv_pred = self.calculate_ocv(soc_pred)
        v_term_pred = ocv_pred - v1_pred - (current_amps * self.r0)

        # Measurement Jacobian matrix C = [dOCV/dSoC, -1]
        c0 = self.calculate_docv_dsoc(soc_pred)
        c1 = -1.0

        # Innovation (Residual)
        residual = measured_terminal_voltage - v_term_pred

        # Innovation covariance S = C * P_pred * C^T + R
        S = (c0 * P_pred[0][0] * c0) + (c0 * P_pred[0][1] * c1) + (c1 * P_pred[1][0] * c0) + (c1 * P_pred[1][1] * c1) + self.R

        # Kalman Gain K = P_pred * C^T * S^(-1)
        K0 = ((P_pred[0][0] * c0) + (P_pred[0][1] * c1)) / S
        K1 = ((P_pred[1][0] * c0) + (P_pred[1][1] * c1)) / S

        # Corrected state x_post = x_pred + K * residual
        soc_post = max(0.0, min(1.0, soc_pred + K0 * residual))
        v1_post = v1_pred + K1 * residual
        self.x = [soc_post, v1_post]

        # Corrected covariance P_post = (I - K * C) * P_pred
        self.P = [
            [(1.0 - K0 * c0) * P_pred[0][0], (1.0 - K0 * c0) * P_pred[0][1]],
            [-K1 * c0 * P_pred[1][0] + (1.0 - K1 * c1) * P_pred[1][0], (1.0 - K1 * c1) * P_pred[1][1]]
        ]

        # 3. State-of-Health (SoH) Throughput & Capacity Fade Degradation
        self.cumulative_ah += abs(current_amps) * (dt_seconds / 3600.0)
        efc = self.cumulative_ah / (2.0 * self.q_nom_ah)  # Equivalent full cycles

        # LiFePO4 semi-empirical degradation: Capacity fade = 1 - 0.00045 * sqrt(EFC)
        soh_cap = max(70.0, 100.0 - (0.00045 * math.sqrt(efc) * 100.0))
        
        # Internal resistance growth: R0(t) = R0_initial * (1 + 0.0006 * EFC)
        self.r0 = self.initial_r0 * (1.0 + 0.0006 * efc)
        soh_res = max(60.0, 100.0 - (0.0006 * efc * 50.0))

        return BatteryEKFState(
            soc=round(soc_post, 4),
            v_polarization=round(v1_post, 4),
            terminal_voltage_v=round(ocv_pred - v1_post - (current_amps * self.r0), 2),
            internal_resistance_r0=round(self.r0, 5),
            soh_capacity_percent=round(soh_cap, 2),
            soh_resistance_percent=round(soh_res, 2),
            cumulative_throughput_ah=round(self.cumulative_ah, 1),
            equivalent_full_cycles=round(efc, 1)
        )

battery_kalman_estimator = BatteryKalmanFilterEstimator()

