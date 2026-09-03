from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.security.models import SecurityMode
from services.security.security_service import security_service, CAMERAS_DB
from services.security.webrtc_signaling_manager import webrtc_signaling_manager
from services.identity.routes import get_current_user

router = APIRouter(prefix="/security", tags=["Security & Surveillance"])

class ArmRequest(BaseModel):
    mode: SecurityMode

class WebRTCOfferRequest(BaseModel):
    camera_id: str = "cam-front-door"
    sdp_offer: str
    session_id: Optional[str] = None

class WebRTCICERequest(BaseModel):
    session_id: str
    candidate: str
    sdp_mid: str = "0"
    sdp_mline_index: int = 0

class EmergencySmokeRequest(BaseModel):
    zone: str = "Living Area"
    smoke_ppm: float = 240.0

class EmergencyWaterLeakRequest(BaseModel):
    sensor_id: str = "sensor-water-kitchen"
    room_id: str = "kitchen"

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

@router.post("/webrtc/offer")
async def handle_webrtc_offer(req: WebRTCOfferRequest, user = Depends(get_current_user)):
    """Initiates WebRTC video streaming handshake and returns negotiated SDP answer."""
    session = webrtc_signaling_manager.create_session(req.camera_id)
    answer = webrtc_signaling_manager.process_sdp_offer(session.session_id, req.sdp_offer)
    return answer

@router.post("/webrtc/ice")
async def handle_webrtc_ice(req: WebRTCICERequest, user = Depends(get_current_user)):
    """Receives and enqueues trickle ICE candidate."""
    success = webrtc_signaling_manager.add_ice_candidate(
        session_id=req.session_id,
        candidate_str=req.candidate,
        sdp_mid=req.sdp_mid,
        sdp_mline_index=req.sdp_mline_index
    )
    return {"success": success}

@router.post("/emergency/smoke")
async def trigger_smoke_emergency(req: EmergencySmokeRequest, user = Depends(get_current_user)):
    """Triggers immediate HVAC shutdown and emergency door unlocks."""
    res = await security_service.trigger_emergency_smoke_fire_interlock(zone=req.zone, smoke_ppm=req.smoke_ppm)
    return res

@router.post("/emergency/water-leak")
async def trigger_water_leak_emergency(req: EmergencyWaterLeakRequest, user = Depends(get_current_user)):
    """Triggers rapid motorized main water solenoid shutoff."""
    res = await security_service.trigger_emergency_water_leak_interlock(sensor_id=req.sensor_id, room_id=req.room_id)
    return res
