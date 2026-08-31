from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

class UserRole(str, Enum):
    PLATFORM_OWNER = "platform_owner"
    HOME_OWNER = "home_owner"
    HOME_ADMINISTRATOR = "home_administrator"
    FAMILY_MEMBER = "family_member"
    RESIDENT = "resident"
    GUEST = "guest"
    CHILD_ACCOUNT = "child_account"
    TECHNICIAN = "technician"

class Permission(str, Enum):
    VIEW_HOME = "home:view"
    MANAGE_HOME = "home:manage"
    CONTROL_DEVICES = "device:control"
    MANAGE_DEVICES = "device:manage"
    VIEW_SECURITY = "security:view"
    ARM_DISARM_SECURITY = "security:arm_disarm"
    VIEW_CAMERAS = "camera:view"
    MANAGE_AUTOMATIONS = "automation:manage"
    MANAGE_USERS = "user:manage"
    VIEW_ENERGY = "energy:view"
    VIEW_AUDIT_LOGS = "audit:view"

class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    phone_number: Optional[str] = None
    role: UserRole = UserRole.RESIDENT
    hashed_password: str
    is_active: bool = True
    home_ids: List[str] = Field(default_factory=list)
    custom_permissions: List[Permission] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_agent: str
    ip_address: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    is_revoked: bool = False

class GuestPass(BaseModel):
    pass_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    home_id: str
    guest_name: str
    pin_code: str
    allowed_rooms: List[str] = Field(default_factory=list)
    valid_from: datetime
    valid_until: datetime
    is_revoked: bool = False
    created_by: str

class AuditEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: str
    actor_name: str
    action: str
    target_resource: str
    home_id: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    result: str = "SUCCESS"
    details: Dict[str, Any] = Field(default_factory=dict)
