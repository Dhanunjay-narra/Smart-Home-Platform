"""
Enterprise Test Suite — Hardened Features, Hardware Adapters & Mathematical Models
Validates:
1. Philips Hue CIE-1931 Gamut Math & REST API
2. Shelly/Sonoff CoAP Framing & Switch Relay
3. Tesla Wallbox CAN Bus & 6A-32A Dynamic Throttling
4. SolarEdge SunSpec Modbus & Sandia Inverter Efficiency
5. Battery Extended Kalman Filter (EKF) SoC & SoH
6. Time-of-Use (TOU) Dynamic Appliance Cost Optimizer
7. Solar Irradiance Geometry & Cloud Yield Predictor
8. WebRTC SDP Signaling & Trickle ICE
9. RTSP H.264 NAL De-packetizer & Optical Flow Filter
10. Emergency Safety Interlocks (Smoke HVAC Cutoff & Water Leak Solenoid)
"""

import pytest
import asyncio
import math
import struct

from edge.protocol_adapters.philips_hue_cie1931_adapter import philips_hue_adapter, PhilipsHueCIE1931Adapter
from edge.protocol_adapters.shelly_sonoff_switch_adapter import shelly_sonoff_adapter, CoAPCodec, CoAPMessage, CoAPType, CoAPCode
from edge.protocol_adapters.tesla_wallbox_ev_charging_controller import tesla_ev_controller, TeslaWallboxEVController, PilotState, ChargingMode
from edge.protocol_adapters.solaredge_enphase_inverter_adapter import solaredge_inverter_adapter, SolarEdgeEnphaseInverterAdapter
from services.energy.battery_kalman_filter_soc_soh import battery_kalman_estimator, BatteryKalmanFilterEstimator
from services.energy.tou_tariff_appliance_optimizer import tou_optimizer, TOUTariffApplianceOptimizer
from services.energy.solar_irradiance_forecast_predictor import solar_predictor, SolarIrradianceForecastPredictor
from services.security.webrtc_signaling_manager import webrtc_signaling_manager, PeerState
from services.security.rtsp_h264_optical_flow_filter import rtsp_optical_flow_filter, NALUnitType
from services.security.security_service import security_service
from services.analytics.reporting.report_generator import report_generator
from services.analytics.timeseries_models.rollup_engine import timeseries_rollup_engine

# =============================================================================
# 1. PHILIPS HUE CIE-1931 TESTS
# =============================================================================

def test_philips_hue_rgb_to_xy_and_back():
    # Pure Red in sRGB
    x, y, bri = PhilipsHueCIE1931Adapter.rgb_to_xy_brightness(255, 0, 0, "C")
    assert x > 0.6
    assert y > 0.28
    assert bri > 50

    # Convert back to RGB
    r, g, b = PhilipsHueCIE1931Adapter.xy_brightness_to_rgb(x, y, bri, "C")
    assert r > 200
    assert g < 50
    assert b < 50

def test_philips_hue_gamut_clamping():
    # Point outside triangle should be projected onto closest boundary
    x, y = PhilipsHueCIE1931Adapter._clamp_to_gamut(0.9, 0.9, "C")
    assert x <= 0.75
    assert y <= 0.75

def test_philips_hue_rest_api_state():
    res = philips_hue_adapter.set_light_state("1", {"on": True, "bri": 180, "xy": [0.4, 0.4]})
    assert "success" in res
    st = philips_hue_adapter.get_light_state("1")
    assert st.on is True
    assert st.bri == 180

# =============================================================================
# 2. SHELLY & SONOFF COAP & SWITCH TESTS
# =============================================================================

def test_coap_codec_roundtrip():
    msg = CoAPMessage(
        version=1,
        mtype=CoAPType.CON,
        code=CoAPCode.POST,
        message_id=0x1234,
        token=b"abc",
        options={11: b"relay", 12: b"application/json"},
        payload=b'{"turn":"on"}'
    )
    encoded = CoAPCodec.encode(msg)
    assert len(encoded) > 10

    decoded = CoAPCodec.decode(encoded)
    assert decoded.version == 1
    assert decoded.mtype == CoAPType.CON
    assert decoded.message_id == 0x1234
    assert decoded.token == b"abc"
    assert decoded.options[11] == b"relay"
    assert decoded.payload == b'{"turn":"on"}'

def test_shelly_sonoff_relay_actuation():
    res = shelly_sonoff_adapter.set_relay("shelly-plug-living", True)
    assert res["success"] is True
    assert res["is_on"] is True
    assert res["power_watts"] > 0

    res_off = shelly_sonoff_adapter.set_relay("shelly-plug-living", False)
    assert res_off["is_on"] is False
    assert res_off["power_watts"] == 0.0

# =============================================================================
# 3. TESLA WALLBOX & EV CONTROLLER TESTS
# =============================================================================

def test_tesla_can_bus_decoding():
    ctrl = TeslaWallboxEVController()
    
    # 0x102 Pack Voltage (4000 = 400.0V), Current (320 = 32.0A)
    p_102 = struct.pack("!Hh4x", 4000, 320)
    res_102 = ctrl.parse_can_frame(0x102, p_102)
    assert res_102["voltage_v"] == 400.0
    assert res_102["current_a"] == 32.0

    # 0x212 SoC% (160 * 0.5 = 80.0%), Temp (65 - 40 = 25.0C), Fault=0
    p_212 = struct.pack("!BBH4x", 160, 65, 0)
    res_212 = ctrl.parse_can_frame(0x212, p_212)
    assert res_212["soc_percent"] == 80.0
    assert res_212["battery_temp_c"] == 25.0

def test_tesla_dynamic_current_throttling():
    ctrl = TeslaWallboxEVController()
    ctrl.telemetry.soc_percent = 50.0
    ctrl.charging_mode = ChargingMode.SOLAR_SURPLUS_ONLY

    # High solar surplus (6.0 kW solar, 1.0 kW home -> 5.0 kW surplus)
    current = ctrl.calculate_optimal_charging_current(solar_generation_kw=6.0, home_base_load_kw=1.0)
    assert current >= 6.0  # Safe minimum threshold met

    # Low solar surplus (< 1.38 kW threshold for 6A @ 230V)
    current_low = ctrl.calculate_optimal_charging_current(solar_generation_kw=0.5, home_base_load_kw=1.0)
    assert current_low < current

# =============================================================================
# 4. SOLAREDGE SUNSPEC & EFFICIENCY TESTS
# =============================================================================

def test_sunspec_scale_factors():
    # 4850 with scale factor -2 -> 48.50
    v = SolarEdgeEnphaseInverterAdapter.apply_sunspec_scale(4850, -2)
    assert v == 48.50

    # 240 with scale factor 0 -> 240.0
    v2 = SolarEdgeEnphaseInverterAdapter.apply_sunspec_scale(240, 0)
    assert v2 == 240.0

def test_sandia_inverter_efficiency():
    p_ac, eff = SolarEdgeEnphaseInverterAdapter.calculate_sandia_efficiency(
        p_dc_watts=5000.0,
        v_dc_volts=380.0,
        p_ac0_max_watts=7600.0
    )
    assert p_ac > 4500.0
    assert 94.0 <= eff <= 99.0

# =============================================================================
# 5. BATTERY KALMAN FILTER (EKF) TESTS
# =============================================================================

def test_battery_kalman_filter_step():
    ekf = BatteryKalmanFilterEstimator(nominal_capacity_ah=100.0)
    # Discharge step at 20A for 1 second
    state = ekf.step(current_amps=20.0, measured_terminal_voltage=51.2, dt_seconds=1.0)
    assert 0.0 <= state.soc <= 1.0
    assert state.terminal_voltage_v > 45.0
    assert state.soh_capacity_percent >= 90.0
    assert state.soh_resistance_percent >= 90.0

# =============================================================================
# 6. TIME-OF-USE (TOU) COST OPTIMIZER TESTS
# =============================================================================

def test_tou_appliance_optimizer():
    opt = TOUTariffApplianceOptimizer()
    summary = opt.optimize_24h_schedule(
        ev_energy_needed_kwh=15.0,
        ev_departure_hour=7,
        battery_capacity_kwh=13.5,
        battery_initial_soc_percent=50.0
    )
    assert summary.total_optimized_cost_usd <= summary.total_unoptimized_cost_usd
    assert summary.savings_percent >= 0.0
    assert len(summary.schedule) == 24

# =============================================================================
# 7. SOLAR IRRADIANCE FORECAST PREDICTOR TESTS
# =============================================================================

def test_solar_forecast_predictor():
    pred = SolarIrradianceForecastPredictor(latitude_deg=37.77, longitude_deg=-122.41, system_dc_kw=6.0)
    forecast = pred.predict_forecast(horizon_hours=24)
    assert forecast.forecast_horizon_hours == 24
    assert forecast.total_predicted_yield_kwh >= 0.0
    assert len(forecast.hourly_forecast) == 24

# =============================================================================
# 8. WEBRTC SIGNALING TESTS
# =============================================================================

def test_webrtc_signaling_handshake():
    session = webrtc_signaling_manager.create_session("cam-front-door")
    assert session.state == PeerState.NEW

    dummy_offer = "v=0\r\no=- 123 2 IN IP4 127.0.0.1\r\na=ice-ufrag:client123\r\na=ice-pwd:secretpass123\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\n"
    res = webrtc_signaling_manager.process_sdp_offer(session.session_id, dummy_offer)
    assert res["type"] == "answer"
    assert "sdp_answer" in res

    cand_added = webrtc_signaling_manager.add_ice_candidate(session.session_id, "candidate:1 1 UDP 2130706431 192.168.1.100 50000 typ host")
    assert cand_added is True

# =============================================================================
# 9. RTSP H.264 NAL & OPTICAL FLOW TESTS
# =============================================================================

def test_rtsp_nal_unpacking():
    # Single NAL packet (Type 5 IDR Keyframe)
    single_nal_packet = bytes([0x65]) + b"\x00" * 20  # 0x65 = 0b01100101 -> forbidden=0, NRI=3, Type=5
    nals = rtsp_optical_flow_filter.unpack_rtp_h264_payload(single_nal_packet)
    assert len(nals) == 1
    assert nals[0].is_keyframe is True
    assert nals[0].nal_type == 5

def test_optical_flow_motion_filter():
    # Coherent directional motion across contiguous blocks
    diff_grid = [[0.0] * 16 for _ in range(12)]
    # Simulate a human walking in blocks (4,4) to (6,6)
    for r in range(4, 7):
        for c in range(4, 7):
            diff_grid[r][c] = 45.0  # Significant coherent luminance delta

    result = rtsp_optical_flow_filter.analyze_macroblock_motion(diff_grid)
    assert result.motion_detected is True
    assert result.confidence_score > 0.0

# =============================================================================
# 10. EMERGENCY SAFETY INTERLOCK TESTS
# =============================================================================

def test_emergency_interlocks():
    async def _async_test():
        # Smoke fire evacuation interlock
        res_smoke = await security_service.trigger_emergency_smoke_fire_interlock(zone="Kitchen", smoke_ppm=320.0)
        assert res_smoke["status"] == "EMERGENCY_INTERLOCK_EXECUTED"

        # Water leak rapid isolation interlock
        res_water = await security_service.trigger_emergency_water_leak_interlock(sensor_id="sensor-water-bath", room_id="bathroom")
        assert res_water["status"] == "WATER_LEAK_ISOLATED"
        assert res_water["response_time_ms"] < 500.0

    asyncio.run(_async_test())

# =============================================================================
# 11. ANALYTICS REPORT & ROLLUP TESTS
# =============================================================================

def test_analytics_report_and_rollup():
    rep = report_generator.generate_energy_report(days=1)
    assert rep.report_type == "energy_daily"
    assert rep.compliance_score >= 90.0

    # Ingest samples into rollup engine
    for i in range(20):
        timeseries_rollup_engine.ingest_sample("solar-test", 1000 + i * 10, 4.0 + 0.1 * i)
    buckets = timeseries_rollup_engine.rollup("solar-test", bucket_size_seconds=60, lookback_seconds=3600)
    assert len(buckets) >= 1

