from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.home.home_service import home_service, HOMES_DB
from services.home.models import Home, HomeMode
from services.identity.routes import get_current_user

router = APIRouter(prefix="/homes", tags=["Home & Property Management"])

class ModeChangeRequest(BaseModel):
    mode: HomeMode

@router.get("")
async def get_homes(user = Depends(get_current_user)):
    return home_service.list_homes()

@router.get("/{home_id}")
async def get_home_details(home_id: str, user = Depends(get_current_user)):
    home = home_service.get_home(home_id)
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    return home

@router.post("/{home_id}/mode")
async def change_home_mode(home_id: str, req: ModeChangeRequest, user = Depends(get_current_user)):
    try:
        updated = await home_service.set_home_mode(home_id, req.mode, actor=user.full_name)
        return {"status": "SUCCESS", "current_mode": updated.current_mode}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
