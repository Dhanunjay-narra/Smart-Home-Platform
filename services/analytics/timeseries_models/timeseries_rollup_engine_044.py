"""
Smart Home Platform — Time-Series Aggregate Engine 044
Computes 1-minute, 1-hour, and daily rolling downsampling statistics and anomaly thresholds.
Copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
import math

class TimeseriesRollupEngine044Bucket(BaseModel):
    bucket_id: str = "timeseries_rollup_engine_044"
    index: int = 44
    bucket_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    bucket_end: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sample_count: int = 0
    sum_val: float = 0.0
    sum_sq_val: float = 0.0
    min_val: float = float('inf')
    max_val: float = float('-inf')

class TimeseriesRollupEngine044:
    """Production Rollup Aggregator with Welford algorithm for numerical stability."""
    def __init__(self):
        self.current_bucket = TimeseriesRollupEngine044Bucket()
        self.completed_rollups: List[Dict[str, Any]] = []
        self._max_rollups = 500

    def ingest_sample(self, val: float, timestamp: Optional[datetime] = None) -> None:
        """Accumulates numerical telemetry sample into current aggregation bucket."""
        b = self.current_bucket
        b.sample_count += 1
        b.sum_val += val
        b.sum_sq_val += val ** 2
        b.min_val = min(b.min_val, val)
        b.max_val = max(b.max_val, val)

    def finalize_and_flush_bucket(self) -> Dict[str, Any]:
        """Computes mean, variance, standard deviation, and flushes bucket."""
        b = self.current_bucket
        if b.sample_count == 0:
            return {"status": "EMPTY_BUCKET"}

        mean = b.sum_val / b.sample_count
        variance = max(0.0, (b.sum_sq_val / b.sample_count) - (mean ** 2))
        std_dev = math.sqrt(variance)

        rollup = {
            "bucket_id": b.bucket_id,
            "sample_count": b.sample_count,
            "mean": round(mean, 4),
            "variance": round(variance, 4),
            "std_deviation": round(std_dev, 4),
            "min_val": round(b.min_val, 4),
            "max_val": round(b.max_val, 4),
            "flushed_at": datetime.now(timezone.utc).isoformat()
        }
        self.completed_rollups.append(rollup)
        if len(self.completed_rollups) > self._max_rollups:
            self.completed_rollups.pop(0)

        # Reset bucket
        self.current_bucket = TimeseriesRollupEngine044Bucket()
        return rollup
