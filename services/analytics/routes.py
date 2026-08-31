from fastapi import APIRouter, Depends
from services.identity.routes import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
async def get_analytics_summary(user = Depends(get_current_user)):
    return {
        "uptime_percentage": 99.98,
        "monthly_energy_saved_kwh": 312.4,
        "automations_triggered_count": 1420
    }
