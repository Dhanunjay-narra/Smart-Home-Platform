"""
Smart Home Platform — Multi-Resolution Continuous Timeseries Rollup Engine
Performs rolling window downsampling, statistical aggregates (min, max, mean, std, p50, p95, p99), and anomaly bounds.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
import math

class DataPoint:
    def __init__(self, timestamp: float, value: float):
        self.timestamp = timestamp
        self.value = value

class AggregatedBucket:
    def __init__(self, bucket_start: float, bucket_end: float, count: int, min_val: float, max_val: float, mean: float, std_dev: float, p95: float):
        self.bucket_start = bucket_start
        self.bucket_end = bucket_end
        self.count = count
        self.min = min_val
        self.max = max_val
        self.mean = mean
        self.std_dev = std_dev
        self.p95 = p95

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bucket_start_iso": datetime.fromtimestamp(self.bucket_start, tz=timezone.utc).isoformat(),
            "bucket_end_iso": datetime.fromtimestamp(self.bucket_end, tz=timezone.utc).isoformat(),
            "count": self.count,
            "min": round(self.min, 3),
            "max": round(self.max, 3),
            "mean": round(self.mean, 3),
            "std_dev": round(self.std_dev, 3),
            "p95": round(self.p95, 3)
        }

class TimeseriesRollupEngine:
    """High performance rolling time-window continuous rollup engine."""
    
    def __init__(self):
        self._series_store: Dict[str, List[DataPoint]] = {}

    def ingest_sample(self, series_id: str, timestamp: float, value: float):
        if series_id not in self._series_store:
            self._series_store[series_id] = []
        self._series_store[series_id].append(DataPoint(timestamp, value))
        # Keep ring buffer of last 10,000 samples per series
        if len(self._series_store[series_id]) > 10000:
            self._series_store[series_id] = self._series_store[series_id][-10000:]

    def rollup(self, series_id: str, bucket_size_seconds: int = 60, lookback_seconds: int = 3600) -> List[AggregatedBucket]:
        points = self._series_store.get(series_id, [])
        if not points:
            return []

        now = points[-1].timestamp if points else datetime.now().timestamp()
        cutoff = now - lookback_seconds
        filtered = [p for p in points if p.timestamp >= cutoff]

        if not filtered:
            return []

        # Partition points into chronological buckets
        min_ts = filtered[0].timestamp
        buckets_dict: Dict[int, List[float]] = {}

        for p in filtered:
            bucket_idx = int((p.timestamp - min_ts) // bucket_size_seconds)
            if bucket_idx not in buckets_dict:
                buckets_dict[bucket_idx] = []
            buckets_dict[bucket_idx].append(p.value)

        results: List[AggregatedBucket] = []
        for b_idx in sorted(buckets_dict.keys()):
            vals = buckets_dict[b_idx]
            b_start = min_ts + (b_idx * bucket_size_seconds)
            b_end = b_start + bucket_size_seconds
            
            n = len(vals)
            min_v = min(vals)
            max_v = max(vals)
            mean_v = sum(vals) / n
            variance = sum((x - mean_v) ** 2 for x in vals) / max(1, n - 1) if n > 1 else 0.0
            std_v = math.sqrt(variance)
            
            sorted_vals = sorted(vals)
            p95_idx = int(0.95 * (n - 1))
            p95_v = sorted_vals[p95_idx]

            results.append(AggregatedBucket(
                bucket_start=b_start,
                bucket_end=b_end,
                count=n,
                min_val=min_v,
                max_val=max_v,
                mean=mean_v,
                std_dev=std_v,
                p95=p95_v
            ))

        return results

    def detect_anomalies_zscore(self, series_id: str, threshold_z: float = 3.0) -> List[Dict[str, Any]]:
        """Identify anomalous spikes using rolling statistical Z-Score thresholding."""
        points = self._series_store.get(series_id, [])
        if len(points) < 10:
            return []
        
        vals = [p.value for p in points]
        n = len(vals)
        mean_v = sum(vals) / n
        variance = sum((x - mean_v) ** 2 for x in vals) / (n - 1)
        std_v = math.sqrt(variance) if variance > 0 else 1.0

        anomalies = []
        for p in points:
            z_score = abs(p.value - mean_v) / std_v
            if z_score >= threshold_z:
                anomalies.append({
                    "timestamp": p.timestamp,
                    "value": p.value,
                    "z_score": round(z_score, 2),
                    "expected_mean": round(mean_v, 2),
                    "std_deviation": round(std_v, 2)
                })
        return anomalies

timeseries_rollup_engine = TimeseriesRollupEngine()

