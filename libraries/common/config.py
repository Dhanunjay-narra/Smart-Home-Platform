from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class PlatformSettings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    SECRET_KEY: str = Field(default="smart-home-platform-dev-secret-key-2026")
    API_PREFIX: str = Field(default="/api/v1")
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./data/smarthome.db")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    MQTT_BROKER_HOST: str = Field(default="localhost")
    MQTT_BROKER_PORT: int = Field(default=1883)
    EDGE_GATEWAY_ID: str = Field(default="edge-hub-master-01")
    OFFLINE_MODE_ENABLED: bool = Field(default=True)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = PlatformSettings()
