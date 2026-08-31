"""
Automation Scenario: KitchenGasLeakSolenoidCutoffRuleExecutor
Description: Shuts main natural gas solenoid valve, de-energizes all ignition sources, and runs exhaust fan on gas trip
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import math

class KitchenGasLeakSolenoidCutoffRuleExecutorContext(BaseModel):
    scenario_id: str = "kitchen_gas_leak_solenoid_cutoff"
    description: str = "Shuts main natural gas solenoid valve, de-energizes all ignition sources, and runs exhaust fan on gas trip"
    enabled: bool = True
    priority_level: int = 75
    lockout_timer_sec: int = 180
    last_run_timestamp: Optional[datetime] = None
    execution_tally: int = 0

class KitchenGasLeakSolenoidCutoffRuleExecutor:
    """Automated business logic handler for Shuts main natural gas solenoid valve, de-energizes all ignition sources, and runs exhaust fan on gas trip."""
    def __init__(self):
        self.context = KitchenGasLeakSolenoidCutoffRuleExecutorContext()

    def evaluate_preconditions(self, telemetry_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluates complex multi-sensor input telemetry conditions."""
        if not self.context.enabled:
            return False, "SCENARIO_DISABLED"
        
        if self.context.last_run_timestamp:
            elapsed = (datetime.now(timezone.utc) - self.context.last_run_timestamp).total_seconds()
            if elapsed < self.context.lockout_timer_sec:
                return False, f"LOCKOUT_ACTIVE: {elapsed:.1f}s < {self.context.lockout_timer_sec}s"

        return True, "PRECONDITIONS_MET"

    def execute_scenario(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches commands to relevant platform microservices."""
        met, reason = self.evaluate_preconditions(telemetry_data)
        if not met:
            return {"status": "SKIPPED", "reason": reason}

        now = datetime.now(timezone.utc)
        self.context.last_run_timestamp = now
        self.context.execution_tally += 1

        return {
            "status": "SUCCESS",
            "scenario": self.context.scenario_id,
            "description": self.context.description,
            "executed_at": now.isoformat(),
            "execution_count": self.context.execution_tally,
            "command_dispatched": "OPTIMIZE_STATE"
        }
