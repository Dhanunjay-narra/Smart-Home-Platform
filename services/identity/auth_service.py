from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
import secrets
from libraries.common.crypto import hash_password, verify_password
from libraries.common.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from services.identity.models import User, UserRole, Permission, Session, GuestPass, AuditEntry
from libraries.database.engine import db_save_user, db_save_audit_log

USERS_DB: Dict[str, User] = {}
SESSIONS_DB: Dict[str, Session] = {}
GUEST_PASSES_DB: Dict[str, GuestPass] = {}
AUDIT_LOG_DB: List[AuditEntry] = []

ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.PLATFORM_OWNER: list(Permission),
    UserRole.HOME_OWNER: list(Permission),
    UserRole.HOME_ADMINISTRATOR: [p for p in Permission if p != Permission.MANAGE_HOME],
    UserRole.FAMILY_MEMBER: [
        Permission.VIEW_HOME, Permission.CONTROL_DEVICES, Permission.VIEW_SECURITY,
        Permission.ARM_DISARM_SECURITY, Permission.VIEW_CAMERAS, Permission.VIEW_ENERGY
    ],
    UserRole.RESIDENT: [
        Permission.VIEW_HOME, Permission.CONTROL_DEVICES, Permission.VIEW_ENERGY
    ],
    UserRole.GUEST: [
        Permission.VIEW_HOME, Permission.CONTROL_DEVICES
    ],
    UserRole.CHILD_ACCOUNT: [
        Permission.VIEW_HOME, Permission.CONTROL_DEVICES
    ],
    UserRole.TECHNICIAN: [
        Permission.VIEW_HOME, Permission.MANAGE_DEVICES, Permission.VIEW_ENERGY
    ]
}

class AuthService:
    def __init__(self):
        self._seed_default_users()

    def _seed_default_users(self):
        if not USERS_DB:
            admin_user = User(
                user_id="usr-admin-001",
                email="admin@smarthome.local",
                full_name="Dhanunjay Narra (Platform Owner)",
                phone_number="+1-555-0199",
                role=UserRole.PLATFORM_OWNER,
                hashed_password=hash_password("HomeAdmin2026!"),
                is_active=True,
                home_ids=["home-master-01"]
            )
            USERS_DB[admin_user.email.lower()] = admin_user
            USERS_DB[admin_user.user_id] = admin_user
            try:
                db_save_user(admin_user)
            except Exception:
                pass

            dhanu_user = User(
                user_id="usr-dhanu-001",
                email="dhanu@123",
                full_name="Dhanunjay Narra (Platform Owner)",
                phone_number="+1-555-0199",
                role=UserRole.PLATFORM_OWNER,
                hashed_password=hash_password("bhanu"),
                is_active=True,
                home_ids=["home-master-01"]
            )
            USERS_DB[dhanu_user.email.lower()] = dhanu_user
            USERS_DB[dhanu_user.user_id] = dhanu_user
            try:
                db_save_user(dhanu_user)
            except Exception:
                pass

            guest_user = User(
                user_id="usr-guest-002",
                email="guest@smarthome.local",
                full_name="Visiting Guest",
                role=UserRole.GUEST,
                hashed_password=hash_password("GuestPass2026!"),
                is_active=True,
                home_ids=["home-master-01"]
            )
            USERS_DB[guest_user.email] = guest_user
            USERS_DB[guest_user.user_id] = guest_user
            try:
                db_save_user(guest_user)
            except Exception:
                pass

    async def authenticate(self, email: str, password: str, full_name: Optional[str] = None, ip: str = "127.0.0.1", user_agent: str = "Web/Browser") -> Dict[str, Any]:
        email_clean = email.strip()
        pwd_clean = password.strip()
        if not email_clean or not pwd_clean:
            self.log_audit("system", "Anonymous", "LOGIN_FAILED", "empty_credentials", ip_address=ip, result="FAILURE")
            raise AuthenticationError("Please enter both email and password.")

        user = USERS_DB.get(email_clean.lower())
        
        # Determine preferred display name
        if full_name and full_name.strip():
            display_name = full_name.strip()
        elif user:
            display_name = user.full_name
        else:
            name_part = email_clean.split('@')[0].replace('.', ' ').replace('_', ' ').replace('-', ' ').title()
            display_name = name_part if name_part else "Smart Home User"

        if not user or not verify_password(pwd_clean, user.hashed_password):
            self.log_audit("system", "Anonymous", "LOGIN_FAILED", f"email:{email_clean}", ip_address=ip, result="FAILURE")
            raise AuthenticationError("Invalid email or password.")

        if full_name and full_name.strip():
            user.full_name = full_name.strip()
            try:
                db_save_user(user)
            except Exception:
                pass

        if not user.is_active:
            raise AuthorizationError("Account is inactive or suspended.")

        access_token = f"tok_{secrets.token_urlsafe(32)}"
        refresh_token = f"ref_{secrets.token_urlsafe(48)}"
        
        session = Session(
            user_id=user.user_id,
            user_agent=user_agent,
            ip_address=ip,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        SESSIONS_DB[access_token] = session
        
        self.log_audit(user.user_id, user.full_name, "LOGIN_SUCCESS", f"user:{user.user_id}", ip_address=ip)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 86400,
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "home_ids": user.home_ids,
                "permissions": [p.value for p in self.get_effective_permissions(user)]
            }
        }

    def get_effective_permissions(self, user: User) -> List[Permission]:
        base_permissions = set(ROLE_PERMISSIONS.get(user.role, []))
        base_permissions.update(user.custom_permissions)
        return list(base_permissions)

    def verify_token(self, token: str) -> User:
        session = SESSIONS_DB.get(token)
        if not session or session.is_revoked or session.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("Session expired or token is invalid.")
        user = USERS_DB.get(session.user_id)
        if not user:
            raise NotFoundError("User", session.user_id)
        return user

    def check_permission(self, user: User, required_permission: Permission):
        effective = self.get_effective_permissions(user)
        if required_permission not in effective:
            raise AuthorizationError(f"Action requires permission '{required_permission.value}'")

    def create_guest_pass(self, home_id: str, guest_name: str, pin: str, allowed_rooms: List[str], duration_hours: int, creator_id: str) -> GuestPass:
        guest_pass = GuestPass(
            home_id=home_id,
            guest_name=guest_name,
            pin_code=pin,
            allowed_rooms=allowed_rooms,
            valid_from=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc) + timedelta(hours=duration_hours),
            created_by=creator_id
        )
        GUEST_PASSES_DB[guest_pass.pass_id] = guest_pass
        self.log_audit(creator_id, "HomeOwner", "CREATE_GUEST_PASS", f"guest_pass:{guest_pass.pass_id}", home_id=home_id)
        return guest_pass

    def log_audit(self, actor_id: str, actor_name: str, action: str, target: str, home_id: Optional[str] = None, device_id: Optional[str] = None, ip_address: Optional[str] = None, result: str = "SUCCESS", details: Dict[str, Any] = None):
        entry = AuditEntry(
            actor_id=actor_id,
            actor_name=actor_name,
            action=action,
            target_resource=target,
            home_id=home_id,
            device_id=device_id,
            ip_address=ip_address,
            result=result,
            details=details or {}
        )
        AUDIT_LOG_DB.append(entry)
        if len(AUDIT_LOG_DB) > 5000:
            AUDIT_LOG_DB.pop(0)
        try:
            db_save_audit_log(entry)
        except Exception:
            pass

auth_service = AuthService()
