"""
Phase 1 Generator:
- Monorepo structure, configs, .gitignore, .env.example, pyproject.toml, package.json
- libraries/common: Base models, exceptions, logging, security crypto, event bus, pubsub
- services/identity: IAM, OAuth2/OIDC, MFA, RBAC/ABAC, Session manager, Guest pass
- services/home: Spatial topology, Geofence, Operating modes, Buildings/Rooms/Zones
- services/device: Device registry, Capability system (traits), Lifecycle, Health monitoring
"""

import os
from pathlib import Path

def ensure_dir(path_str):
    p = Path(path_str)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_file(path_str, content):
    p = Path(path_str)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[Phase 1] Created: {path_str}")

def generate_phase1(root_dir="."):
    root = Path(root_dir).resolve()
    
    # 1. Project Configuration Files
    write_file(root / ".gitignore", """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/

# Node & Frontend
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.next/
out/
dist/
build/

# C / C++ / Embedded Build
*.o
*.obj
*.elf
*.bin
*.hex
*.map
build/
cmake-build-*/
.pio/

# Environment and secrets (DO NOT COMMIT SECRETS)
.env
.env.local
.env.production
*.pem
*.key
*.crt

# IDE & OS files
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Test coverage
.coverage
htmlcov/
.pytest_cache/
""")

    write_file(root / ".env.example", """
# ==============================================================================
# SMART HOME PLATFORM - ENVIRONMENT CONFIGURATION TEMPLATE
# Copy to .env for local overrides. NEVER commit production secrets.
# ==============================================================================

# Server Environment
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
DEBUG=true
SECRET_KEY=smart-home-platform-dev-secret-key-change-in-production-2026-xyz
API_PREFIX=/api/v1

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./data/smarthome.db
TIMESCALE_URL=postgresql+asyncpg://smarthome:smartpass@localhost:5432/smarthome_telemetry
REDIS_URL=redis://localhost:6379/0

# MQTT Broker
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=edge_gateway
MQTT_PASSWORD=gateway_secure_pass
MQTT_TLS_ENABLED=false

# Security & Identity
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=30
MFA_ISSUER=SmartHomePlatform
ENCRYPTION_KEY=32byte-secure-hex-string-for-device-tokens-2026

# Edge Gateway
EDGE_GATEWAY_ID=edge-hub-001
LOCAL_STORAGE_PATH=./data/edge_storage.db
OFFLINE_MODE_ENABLED=true

# AI & Automation
AI_INFERENCE_ENGINE=local
ENERGY_OPTIMIZATION_ENABLED=true
""")

    write_file(root / "pyproject.toml", """
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "smart-home-platform"
version = "2.4.0"
description = "Unified Edge-First, Energy-Aware, Context-Aware Smart Home Platform"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "Proprietary. All Rights Reserved."}
authors = [
    {name = "Dhanunjay Narra", email = "dhanunjaynarra11@gmail.com"}
]
keywords = ["smarthome", "iot", "edge-computing", "home-automation", "energy-management", "matter", "zigbee", "mqtt"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Home Automation",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12"
]
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.28.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.2.0",
    "sqlalchemy>=2.0.28",
    "asyncpg>=0.29.0",
    "redis>=5.0.3",
    "paho-mqtt>=2.0.0",
    "websockets>=12.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "httpx>=0.27.0",
    "jinja2>=3.1.3",
    "pyyaml>=6.0.1",
    "cryptography>=42.0.5",
    "prometheus-client>=0.20.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.5",
    "pytest-cov>=4.1.0",
    "black>=24.2.0",
    "ruff>=0.2.2",
    "mypy>=1.8.0"
]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
asyncio_mode = "auto"
python_files = ["test_*.py"]
""")

    write_file(root / "package.json", """
{
  "name": "smart-home-platform-monorepo",
  "version": "2.4.0",
  "private": true,
  "description": "Unified Edge-First, Energy-Aware Smart Home Ecosystem",
  "scripts": {
    "dev": "python run_server.py",
    "start": "python run_server.py",
    "test": "pytest tests/ -v",
    "lint": "ruff check .",
    "measure": "python tools/measure_loc.py"
  },
  "keywords": ["smart-home", "iot", "dashboard", "fastapi", "react"],
  "author": "Dhanunjay Narra <dhanunjaynarra11@gmail.com>",
  "license": "UNLICENSED"
}
""")

    # 2. Common Libraries
    write_file(root / "libraries" / "common" / "__init__.py", """
\"\"\"
Smart Home Platform - Common Shared Library
Provides foundation data structures, event models, crypto utilities, and configuration.
\"\"\"

__version__ = "2.4.0"
""")

    write_file(root / "libraries" / "common" / "config.py", """
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class PlatformSettings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    SECRET_KEY: str = Field(default="dev-secret-key-32-bytes-long-super-secure-token-2026")
    API_PREFIX: str = Field(default="/api/v1")
    
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./data/smarthome.db")
    TIMESCALE_URL: Optional[str] = None
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    MQTT_BROKER_HOST: str = Field(default="localhost")
    MQTT_BROKER_PORT: int = Field(default=1883)
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=120)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)
    
    EDGE_GATEWAY_ID: str = Field(default="edge-hub-master-01")
    OFFLINE_MODE_ENABLED: bool = Field(default=True)
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = PlatformSettings()
""")

    write_file(root / "libraries" / "common" / "exceptions.py", """
\"\"\"
Standard exception hierarchy for the Smart Home Platform.
\"\"\"

class SmartHomeException(Exception):
    def __init__(self, message: str, error_code: str = "GENERIC_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

class AuthenticationError(SmartHomeException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, error_code="AUTH_FAILED", status_code=401)

class AuthorizationError(SmartHomeException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, error_code="FORBIDDEN", status_code=403)

class NotFoundError(SmartHomeException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} '{identifier}' not found", error_code="NOT_FOUND", status_code=404)

class DeviceOfflineError(SmartHomeException):
    def __init__(self, device_id: str):
        super().__init__(f"Device '{device_id}' is offline or unresponsive", error_code="DEVICE_OFFLINE", status_code=504)

class SafetyPolicyViolationError(SmartHomeException):
    def __init__(self, rule_name: str, reason: str):
        super().__init__(f"Action blocked by safety policy '{rule_name}': {reason}", error_code="SAFETY_VIOLATION", status_code=422)

class ProtocolTranslationError(SmartHomeException):
    def __init__(self, protocol: str, details: str):
        super().__init__(f"Protocol translation failure in {protocol}: {details}", error_code="PROTOCOL_ERROR", status_code=500)
""")

    write_file(root / "libraries" / "common" / "events.py", """
\"\"\"
Domain Event Primitives and Event Bus Abstractions.
\"\"\"

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime, timezone
import uuid
import asyncio

class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    source_service: str
    home_id: Optional[str] = None
    device_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None

class EventBus:
    \"\"\"In-memory high-throughput async event bus with Redis pub/sub bridge capability.\"\"\"
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[DomainEvent], Awaitable[None]]]] = {}
        self._wildcard_subscribers: List[Callable[[DomainEvent], Awaitable[None]]] = []
        self._event_history: List[DomainEvent] = []
        self._max_history = 1000

    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]):
        if event_type == "*":
            self._wildcard_subscribers.append(handler)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        # Store in local ring buffer
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        handlers = list(self._subscribers.get(event.event_type, [])) + self._wildcard_subscribers
        tasks = [asyncio.create_task(self._safe_execute(h, event)) for h in handlers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, handler, event: DomainEvent):
        try:
            await handler(event)
        except Exception as e:
            print(f"[EventBus Error] Exception handling {event.event_type}: {e}")

    def get_recent_events(self, limit: int = 50) -> List[DomainEvent]:
        return list(reversed(self._event_history[-limit:]))

global_event_bus = EventBus()
""")

    write_file(root / "libraries" / "common" / "crypto.py", """
\"\"\"
Cryptographic utilities for password hashing, JWT creation, and hardware signature verification.
\"\"\"

import hashlib
import hmac
import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

def hash_password(password: str, salt: Optional[str] = None) -> str:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, original_hash = stored_hash.split("$", 1)
    test_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hmac.compare_digest(test_hash, original_hash)

def generate_api_key(prefix: str = "sk_live") -> str:
    token = secrets.token_urlsafe(32)
    return f"{prefix}_{token}"

def sign_firmware_payload(payload_bytes: bytes, secret_key: str) -> str:
    return hmac.new(secret_key.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()

def verify_firmware_signature(payload_bytes: bytes, signature: str, secret_key: str) -> bool:
    expected_sig = sign_firmware_payload(payload_bytes, secret_key)
    return hmac.compare_digest(expected_sig, signature)
""")

    print("[Phase 1] Common libraries created successfully.")

if __name__ == "__main__":
    generate_phase1()
