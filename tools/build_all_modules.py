import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def write_f(rel_path, content):
    p = ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {rel_path}")

def build_phase1_files():
    # .gitignore
    write_f(".gitignore", "\n".join([
        "__pycache__/",
        "*.py[cod]",
        "*.so",
        ".env",
        ".env.local",
        "node_modules/",
        "dist/",
        "build/",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        "*.o",
        "*.elf",
        "*.bin"
    ]))

    # .env.example
    write_f(".env.example", "\n".join([
        "# SMART HOME PLATFORM ENVIRONMENT TEMPLATE",
        "ENVIRONMENT=development",
        "PORT=8000",
        "HOST=0.0.0.0",
        "SECRET_KEY=smart-home-platform-secret-key-2026-prod-xyz",
        "API_PREFIX=/api/v1",
        "DATABASE_URL=sqlite+aiosqlite:///./data/smarthome.db",
        "REDIS_URL=redis://localhost:6379/0",
        "MQTT_BROKER_HOST=localhost",
        "MQTT_BROKER_PORT=1883",
        "EDGE_GATEWAY_ID=edge-hub-master-01",
        "OFFLINE_MODE_ENABLED=true"
    ]))

    # pyproject.toml
    write_f("pyproject.toml", "\n".join([
        '[build-system]',
        'requires = ["setuptools>=61.0", "wheel"]',
        'build-backend = "setuptools.build_meta"',
        '',
        '[project]',
        'name = "smart-home-platform"',
        'version = "2.4.0"',
        'description = "Unified Edge-First, Energy-Aware, Context-Aware Smart Home Platform"',
        'readme = "README.md"',
        'requires-python = ">=3.10"',
        'license = {text = "Proprietary. All Rights Reserved."}',
        'authors = [',
        '    {name = "Dhanunjay Narra", email = "dhanunjaynarra11@gmail.com"}',
        ']',
        'dependencies = [',
        '    "fastapi>=0.110.0",',
        '    "uvicorn[standard]>=0.28.0",',
        '    "pydantic>=2.6.0",',
        '    "pydantic-settings>=2.2.0",',
        '    "websockets>=12.0",',
        '    "python-jose[cryptography]>=3.3.0",',
        '    "passlib[bcrypt]>=1.7.4",',
        '    "cryptography>=42.0.5"',
        ']',
        '',
        '[project.optional-dependencies]',
        'dev = [',
        '    "pytest>=8.0.0",',
        '    "pytest-asyncio>=0.23.5"',
        ']'
    ]))

    # package.json
    write_f("package.json", "\n".join([
        '{',
        '  "name": "smart-home-platform-monorepo",',
        '  "version": "2.4.0",',
        '  "private": true,',
        '  "description": "Unified Edge-First, Energy-Aware Smart Home Ecosystem",',
        '  "scripts": {',
        '    "start": "python run_server.py",',
        '    "test": "pytest tests/ -v",',
        '    "measure": "python tools/measure_loc.py"',
        '  },',
        '  "author": "Dhanunjay Narra <dhanunjaynarra11@gmail.com>",',
        '  "license": "UNLICENSED"',
        '}'
    ]))

    # libraries/common
    write_f("libraries/common/__init__.py", "__version__ = '2.4.0'")

    write_f("libraries/common/config.py", "\n".join([
        'from pydantic_settings import BaseSettings, SettingsConfigDict',
        'from pydantic import Field',
        'from typing import Optional',
        '',
        'class PlatformSettings(BaseSettings):',
        '    ENVIRONMENT: str = Field(default="development")',
        '    DEBUG: bool = Field(default=True)',
        '    HOST: str = Field(default="0.0.0.0")',
        '    PORT: int = Field(default=8000)',
        '    SECRET_KEY: str = Field(default="smart-home-platform-dev-secret-key-2026")',
        '    API_PREFIX: str = Field(default="/api/v1")',
        '    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./data/smarthome.db")',
        '    REDIS_URL: str = Field(default="redis://localhost:6379/0")',
        '    MQTT_BROKER_HOST: str = Field(default="localhost")',
        '    MQTT_BROKER_PORT: int = Field(default=1883)',
        '    EDGE_GATEWAY_ID: str = Field(default="edge-hub-master-01")',
        '    OFFLINE_MODE_ENABLED: bool = Field(default=True)',
        '    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")',
        '',
        'settings = PlatformSettings()'
    ]))

    write_f("libraries/common/exceptions.py", "\n".join([
        'class SmartHomeException(Exception):',
        '    def __init__(self, message: str, error_code: str = "GENERIC_ERROR", status_code: int = 400):',
        '        super().__init__(message)',
        '        self.message = message',
        '        self.error_code = error_code',
        '        self.status_code = status_code',
        '',
        'class AuthenticationError(SmartHomeException):',
        '    def __init__(self, message: str = "Authentication failed"):',
        '        super().__init__(message, error_code="AUTH_FAILED", status_code=401)',
        '',
        'class AuthorizationError(SmartHomeException):',
        '    def __init__(self, message: str = "Insufficient permissions"):',
        '        super().__init__(message, error_code="FORBIDDEN", status_code=403)',
        '',
        'class NotFoundError(SmartHomeException):',
        '    def __init__(self, resource: str, identifier: str):',
        '        super().__init__(f"{resource} \'{identifier}\' not found", error_code="NOT_FOUND", status_code=404)',
        '',
        'class SafetyPolicyViolationError(SmartHomeException):',
        '    def __init__(self, rule_name: str, reason: str):',
        '        super().__init__(f"Action blocked by safety policy \'{rule_name}\': {reason}", error_code="SAFETY_VIOLATION", status_code=422)'
    ]))

    write_f("libraries/common/events.py", "\n".join([
        'from pydantic import BaseModel, Field',
        'from typing import Dict, Any, Optional, List, Callable, Awaitable',
        'from datetime import datetime, timezone',
        'import uuid',
        'import asyncio',
        '',
        'class DomainEvent(BaseModel):',
        '    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))',
        '    event_type: str',
        '    source_service: str',
        '    home_id: Optional[str] = None',
        '    device_id: Optional[str] = None',
        '    payload: Dict[str, Any] = Field(default_factory=dict)',
        '    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))',
        '',
        'class EventBus:',
        '    def __init__(self):',
        '        self._subscribers: Dict[str, List[Callable[[DomainEvent], Awaitable[None]]]] = {}',
        '        self._wildcard_subscribers: List[Callable[[DomainEvent], Awaitable[None]]] = []',
        '        self._event_history: List[DomainEvent] = []',
        '        self._max_history = 1000',
        '',
        '    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]):',
        '        if event_type == "*":',
        '            self._wildcard_subscribers.append(handler)',
        '        else:',
        '            if event_type not in self._subscribers:',
        '                self._subscribers[event_type] = []',
        '            self._subscribers[event_type].append(handler)',
        '',
        '    async def publish(self, event: DomainEvent):',
        '        self._event_history.append(event)',
        '        if len(self._event_history) > self._max_history:',
        '            self._event_history.pop(0)',
        '        handlers = list(self._subscribers.get(event.event_type, [])) + self._wildcard_subscribers',
        '        tasks = [asyncio.create_task(self._safe_execute(h, event)) for h in handlers]',
        '        if tasks:',
        '            await asyncio.gather(*tasks, return_exceptions=True)',
        '',
        '    async def _safe_execute(self, handler, event: DomainEvent):',
        '        try:',
        '            await handler(event)',
        '        except Exception as e:',
        '            print(f"[EventBus] Error in {event.event_type}: {e}")',
        '',
        '    def get_recent_events(self, limit: int = 50) -> List[DomainEvent]:',
        '        return list(reversed(self._event_history[-limit:]))',
        '',
        'global_event_bus = EventBus()'
    ]))

    write_f("libraries/common/crypto.py", "\n".join([
        'import hashlib',
        'import hmac',
        'import secrets',
        'from typing import Optional',
        '',
        'def hash_password(password: str, salt: Optional[str] = None) -> str:',
        '    if not salt:',
        '        salt = secrets.token_hex(16)',
        '    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()',
        '    return f"{salt}${hashed}"',
        '',
        'def verify_password(password: str, stored_hash: str) -> bool:',
        '    if not stored_hash or "$" not in stored_hash:',
        '        return False',
        '    salt, original_hash = stored_hash.split("$", 1)',
        '    test_hash = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()',
        '    return hmac.compare_digest(test_hash, original_hash)'
    ]))

    print("Phase 1 scaffolding files generated.")

if __name__ == "__main__":
    build_phase1_files()
