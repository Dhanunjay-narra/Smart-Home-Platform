"""
Automated Unit and Integration Test Suite: test_feature_enhancements
Scope: Validates Multi-Intent Conversational AI Copilot, ToU Tariff Savings Calculator, and Real-time WebSocket Synchronizer
"""
import pytest
import asyncio
from services.intelligence.nlp_engine import nlp_engine
from services.energy.energy_service import energy_service
from services.device.device_service import device_service
from services.telemetry.stream_processor import telemetry_processor
from services.telemetry.models import TelemetryPoint

def test_multi_intent_nlp_copilot():
    async def _impl():
        res = await nlp_engine.process_query("Turn on lights and set AC to 19C")
        assert 'reply' in res
        light = device_service.get_device('dev-light-living')
        assert light.state.get('power') is True
        ac = device_service.get_device('dev-thermostat-living')
        assert ac.state.get('target_temp') == 19.0
        res_energy = await nlp_engine.process_query('What is current solar energy generation?')
        assert 'Solar is currently generating' in res_energy['reply']
    asyncio.run(_impl())

def test_tou_tariff_energy_savings():
    tariff = energy_service.get_tariff_breakdown()
    assert 'current_rate_usd_kwh' in tariff
    assert 'daily_cost_saved_usd' in tariff
    assert tariff['daily_cost_saved_usd'] > 0.0
    assert tariff['self_consumption_ratio_pct'] > 90.0

def test_telemetry_websocket_broadcast():
    async def _impl():
        sample = TelemetryPoint(
            device_id='dev-solar-inverter',
            metric_name='solar_yield_kw',
            value=4.95,
            unit='kW',
            home_id='home-master-01'
        )
        await telemetry_processor.ingest_point(sample)
        recent = telemetry_processor.get_latest_metrics('dev-solar-inverter', limit=5)
        assert len(recent) > 0
        assert recent[0].value == 4.95
    asyncio.run(_impl())
