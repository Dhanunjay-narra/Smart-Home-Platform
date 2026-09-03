"""
Smart Home Platform — Master API Gateway & Web Application Server
Unified Edge-First, Energy-Aware & Context-Aware Ecosystem
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

from services.identity.routes import router as identity_router
from services.home.routes import router as home_router
from services.device.routes import router as device_router
from services.telemetry.routes import router as telemetry_router
from services.automation.routes import router as automation_router
from services.security.routes import router as security_router
from services.energy.routes import router as energy_router
from services.intelligence.routes import router as ai_router
from services.analytics.routes import router as analytics_router

app = FastAPI(
    title="Smart Home Platform API",
    description="Unified Edge-First, Energy-Aware, Context-Aware Smart Home Platform",
    version="2.4.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
from libraries.common.exceptions import SmartHomeException

@app.exception_handler(SmartHomeException)
async def smart_home_exception_handler(request: Request, exc: SmartHomeException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "status_code": exc.status_code
        }
    )

# Mount Service API Routers
app.include_router(identity_router, prefix="/api/v1")
app.include_router(home_router, prefix="/api/v1")
app.include_router(device_router, prefix="/api/v1")
app.include_router(telemetry_router, prefix="/api/v1")
app.include_router(automation_router, prefix="/api/v1")
app.include_router(security_router, prefix="/api/v1")
app.include_router(energy_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

from libraries.database.engine import init_db

# Initialize SQLite database on startup
@app.on_event("startup")
async def on_startup():
    init_db()
    print(" [DATABASE] Connected to SQLite database: ./data/smarthome.db")
    print(" [DATABASE] Tables initialized (users, devices, rules, scenes, audit_logs) -> SUCCESS")

# Web Dashboard Path
web_dir = Path(__file__).parent / "apps" / "web"

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_file = web_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Smart Home Platform API Server Running</h1><p>Visit <a href='/api/docs'>API Docs</a></p>"

@app.get("/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "version": "2.4.0",
        "database": "sqlite+aiosqlite:///./data/smarthome.db",
        "platform": "Smart Home Unified Architecture",
        "services": [
            "identity", "home", "device", "telemetry", "automation",
            "security", "energy", "intelligence", "edge-gateway"
        ]
    }

if __name__ == "__main__":
    init_db()
    print("=================================================================")
    print(" Smart Home Platform — Starting Production Server")
    print(" Dashboard URL: http://localhost:8000")
    print(" API Docs:     http://localhost:8000/api/docs")
    print(" Database:     Connected (SQLite: ./data/smarthome.db)")
    print(" 1-Click Login: admin@smarthome.local / HomeAdmin2026!")
    print("=================================================================")
    uvicorn.run("run_server:app", host="0.0.0.0", port=8000, reload=False)
