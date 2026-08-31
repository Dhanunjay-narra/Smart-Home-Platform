from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.security.models import SecurityMode
from services.security.security_service import security_service, CAMERAS_DB
from services.identity.routes import get_current_user

router = APIRouter(prefix="/security", tags=["Security & Surveillance"])

class ArmRequest(BaseModel):
    mode: SecurityMode

@router.get("/status")
async def get_security_status(user = Depends(get_current_user)):
    return {"mode": security_service.current_security_mode, "cameras_online": len(CAMERAS_DB)}

@router.post("/arm")
async def set_arm_mode(req: ArmRequest, user = Depends(get_current_user)):
    mode = await security_service.arm_security(req.mode, actor=user.full_name)
    return {"status": "SUCCESS", "current_mode": mode}

@router.get("/cameras")
async def list_cameras(user = Depends(get_current_user)):
    return list(CAMERAS_DB.values())
