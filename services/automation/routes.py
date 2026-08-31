from fastapi import APIRouter, HTTPException, Depends
from services.automation.rule_engine import automation_engine, SCENES_DB, RULES_DB
from services.identity.routes import get_current_user

router = APIRouter(prefix="/automation", tags=["Automations & Scenes"])

@router.get("/rules")
async def list_rules(user = Depends(get_current_user)):
    return list(RULES_DB.values())

@router.get("/scenes")
async def list_scenes(user = Depends(get_current_user)):
    return list(SCENES_DB.values())

@router.post("/scenes/{scene_id}/activate")
async def trigger_scene(scene_id: str, user = Depends(get_current_user)):
    ok = await automation_engine.activate_scene(scene_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Scene not found")
    return {"status": "SUCCESS", "scene_id": scene_id, "activated": True}
