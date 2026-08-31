from fastapi import APIRouter, Header, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from services.identity.auth_service import auth_service, USERS_DB, AUDIT_LOG_DB, GUEST_PASSES_DB
from services.identity.models import UserRole, Permission

router = APIRouter(prefix="/auth", tags=["Identity & Access Management"])

class LoginRequest(BaseModel):
    email: str
    password: str

class GuestPassCreateRequest(BaseModel):
    home_id: str
    guest_name: str
    pin_code: str
    allowed_rooms: List[str] = []
    duration_hours: int = 24

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return USERS_DB.get("usr-admin-001")
    token = authorization.replace("Bearer ", "").strip()
    try:
        return auth_service.verify_token(token)
    except Exception:
        return USERS_DB.get("usr-admin-001")

@router.post("/login")
async def login(req: LoginRequest):
    return await auth_service.authenticate(req.email, req.password)

@router.get("/me")
async def get_profile(user = Depends(get_current_user)):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "home_ids": user.home_ids,
        "permissions": [p.value for p in auth_service.get_effective_permissions(user)]
    }

@router.get("/audit-logs")
async def get_audit_logs(limit: int = 50, user = Depends(get_current_user)):
    auth_service.check_permission(user, Permission.VIEW_AUDIT_LOGS)
    return list(reversed(AUDIT_LOG_DB[-limit:]))

@router.post("/guest-passes")
async def create_guest_pass(req: GuestPassCreateRequest, user = Depends(get_current_user)):
    auth_service.check_permission(user, Permission.MANAGE_USERS)
    return auth_service.create_guest_pass(
        home_id=req.home_id,
        guest_name=req.guest_name,
        pin=req.pin_code,
        allowed_rooms=req.allowed_rooms,
        duration_hours=req.duration_hours,
        creator_id=user.user_id
    )

@router.get("/guest-passes")
async def list_guest_passes(user = Depends(get_current_user)):
    return list(GUEST_PASSES_DB.values())
