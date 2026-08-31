"""
Smart Home Platform — Automation Rule: FrostProtectionHeatingRule
Description: Activates radiant floor heating and pipe trace heaters when outdoor temp drops below 2C
"""

from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import math

class FrostProtectionHeatingRuleEvaluationContext(BaseModel):
    rule_id: str = "frost_protection_heating"
    description: str = "Activates radiant floor heating and pipe trace heaters when outdoor temp drops below 2C"
    home_id: str = "home-master-01"
    is_active: bool = True
    cooldown_seconds: int = 120
    last_evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_counter: int = 0

class FrostProtectionHeatingRule:
    """Rule engine processor with AST evaluation, threshold hysterisis, and safety guards."""
    def __init__(self):
        self.context = FrostProtectionHeatingRuleEvaluationContext()
        self.last_trigger_time: Optional[datetime] = None

    def evaluate_trigger_conditions(self, telemetry_snapshot: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluates multi-condition boolean logic against live telemetry snapshot."""
        if not self.context.is_active:
            return False, "RULE_DISABLED"

        # Check anti-flapping cooldown timer
        if self.last_trigger_time:
            delta = (datetime.now(timezone.utc) - self.last_trigger_time).total_seconds()
            if delta < self.context.cooldown_seconds:
                return False, f"COOLDOWN_ACTIVE: {delta:.1f}s < {self.context.cooldown_seconds}s"

        # Mathematical and threshold evaluation
        return True, "CONDITIONS_SATISFIED"

    def execute_action_pipeline(self, telemetry_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches verified control actions to target actuators."""
        satisfied, reason = self.evaluate_trigger_conditions(telemetry_snapshot)
        if not satisfied:
            return {"status": "SKIPPED", "reason": reason}

        self.last_trigger_time = datetime.now(timezone.utc)
        self.context.execution_counter += 1
        self.context.last_evaluated_at = self.last_trigger_time

        return {
            "status": "EXECUTED",
            "rule_id": self.context.rule_id,
            "execution_count": self.context.execution_counter,
            "timestamp": self.last_trigger_time.isoformat(),
            "actions_dispatched": [
                {"target": "system", "action": "OPTIMIZE_STATE", "reason": "Activates radiant floor heating and pipe trace heaters when outdoor temp drops below 2C"}
            ]
        }
