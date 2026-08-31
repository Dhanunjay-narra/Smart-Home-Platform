from fastapi import APIRouter, Depends
from services.energy.energy_service import energy_service
from services.identity.routes import get_current_user

router = APIRouter(prefix="/energy", tags=["Energy & Solar"])

@router.get("/flow")
async def get_energy_flow(user = Depends(get_current_user)):
    return energy_service.get_realtime_energy_flow()
