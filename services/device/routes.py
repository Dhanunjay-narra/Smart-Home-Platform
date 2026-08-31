from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
from services.device.device_service import device_service, DEVICES_DB
from services.identity.routes import get_current_user

router = APIRouter(prefix="/devices", tags=["Device Platform & Capabilities"])

class CommandRequest(BaseModel):
    command: str
    value: Any

@router.get("")
async def get_devices(home_id: Optional[str] = None, room_id: Optional[str] = None, user = Depends(get_current_user)):
    return device_service.list_devices(home_id=home_id, room_id=room_id)

@router.get("/{device_id}")
async def get_device(device_id: str, user = Depends(get_current_user)):
    dev = device_service.get_device(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return dev

@router.post("/{device_id}/command")
async def send_command(device_id: str, req: CommandRequest, user = Depends(get_current_user)):
    try:
        updated = await device_service.execute_command(device_id, req.command, req.value, actor=user.full_name)
        return {"status": "SUCCESS", "device_id": device_id, "state": updated.state}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
