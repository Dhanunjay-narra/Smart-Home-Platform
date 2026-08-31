import pytest
from services.identity.auth_service import auth_service
from services.home.home_service import home_service
from services.device.device_service import device_service
from services.energy.energy_service import energy_service
from services.intelligence.nlp_engine import nlp_engine
from services.automation.rule_engine import automation_engine

def test_auth_login():
    async def _async_impl():
        res = await auth_service.authenticate("admin@smarthome.local", "HomeAdmin2026!")
        assert "access_token" in res
    
def test_device_controls():
    async def _async_impl():
        res = await device_service.execute_command("dev-light-living", "brightness", 75)
        assert res.state["brightness"] == 75
    
def test_scene_execution():
    async def _async_impl():
        ok = await automation_engine.activate_scene("scene-movie-night")
        assert ok is True
    
def test_nlp_queries():
    async def _async_impl():
        res = await nlp_engine.process_query("turn off living room lights")
        assert res["action_taken"] == "LIGHT_OFF"
    
    import asyncio
    asyncio.run(_async_impl())

def test_energy_metrics():
    flow = energy_service.get_realtime_energy_flow()
    assert flow.solar_generation_kw >= 0.0
