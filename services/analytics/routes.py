from fastapi import APIRouter, Depends
from services.identity.routes import get_current_user
from services.analytics.reporting.report_generator import report_generator
from services.analytics.timeseries_models.rollup_engine import timeseries_rollup_engine
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
async def get_analytics_summary(user = Depends(get_current_user)):
    return {
        "uptime_percentage": 99.98,
        "monthly_energy_saved_kwh": 312.4,
        "automations_triggered_count": 1420
    }

@router.get("/reports/energy")
async def get_energy_analytics_report(days: int = 1, user = Depends(get_current_user)):
    """Generates comprehensive energy analytics report."""
    return report_generator.generate_energy_report(days=days)

@router.get("/reports/reliability")
async def get_reliability_analytics_report(user = Depends(get_current_user)):
    """Generates system reliability SLA and MTBF/MTTR report."""
    return report_generator.generate_reliability_report()

@router.get("/rollup")
async def get_timeseries_rollup(series_id: str = "home-solar-yield", bucket_seconds: int = 60, lookback_seconds: int = 3600, user = Depends(get_current_user)):
    """Returns multi-resolution timeseries aggregation buckets."""
    # Seed sample telemetry if empty
    if not timeseries_rollup_engine._series_store.get(series_id):
        now = datetime.now().timestamp()
        for i in range(60):
            ts = now - (60 - i) * 60
            val = 3.5 + 1.2 * (i / 60.0)
            timeseries_rollup_engine.ingest_sample(series_id, ts, val)

    buckets = timeseries_rollup_engine.rollup(series_id=series_id, bucket_size_seconds=bucket_seconds, lookback_seconds=lookback_seconds)
    return [b.to_dict() for b in buckets]
