from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Optional
from services.telemetry.stream_processor import telemetry_processor, TELEMETRY_RING_BUFFER, LIVE_SOCKET_CLIENTS
from services.identity.routes import get_current_user
import json

router = APIRouter(prefix="/telemetry", tags=["Telemetry Stream"])

@router.get("/latest")
async def get_latest_points(device_id: Optional[str] = None, limit: int = 50, user = Depends(get_current_user)):
    if device_id:
        return telemetry_processor.get_latest_metrics(device_id, limit=limit)
    return list(reversed(TELEMETRY_RING_BUFFER[-limit:]))

@router.websocket("/ws")
async def telemetry_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    LIVE_SOCKET_CLIENTS.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        LIVE_SOCKET_CLIENTS.remove(websocket)
