from typing import Dict, Any, List, Optional
from services.device.models import Device, DeviceCategory, ProtocolType, DeviceStatus
from services.device.capabilities import Capability, CapabilityType
from libraries.common.events import global_event_bus, DomainEvent
from datetime import datetime, timezone

DEVICES_DB: Dict[str, Device] = {}

class DeviceService:
    def __init__(self):
        self._seed_default_devices()

    def _seed_default_devices(self):
        if not DEVICES_DB:
            light = Device(
                device_id="dev-light-living",
                name="Living Room Main Light",
                category=DeviceCategory.LIGHTING,
                protocol=ProtocolType.THREAD_MATTER,
                room_id="rm-living",
                home_id="home-master-01",
                capabilities=[
                    Capability(type=CapabilityType.POWER, name="Power Switch", current_value=True),
                    Capability(type=CapabilityType.BRIGHTNESS, name="Brightness", unit="%", min_value=0, max_value=100, current_value=85),
                    Capability(type=CapabilityType.COLOR_RGB, name="RGB Color", current_value="#FFB049")
                ],
                state={"power": True, "brightness": 85, "color_rgb": "#FFB049"}
            )
            DEVICES_DB[light.device_id] = light

            thermostat = Device(
                device_id="dev-thermostat-living",
                name="Living Room Climate HVAC",
                category=DeviceCategory.CLIMATE,
                protocol=ProtocolType.ZIGBEE,
                room_id="rm-living",
                home_id="home-master-01",
                capabilities=[
                    Capability(type=CapabilityType.TEMPERATURE_SETPOINT, name="Target Temperature", unit="°C", min_value=16, max_value=30, current_value=23.0),
                    Capability(type=CapabilityType.TEMPERATURE_SENSOR, name="Current Temperature", unit="°C", read_only=True, current_value=24.2)
                ],
                state={"target_temp": 23.0, "current_temp": 24.2, "mode": "COOL"}
            )
            DEVICES_DB[thermostat.device_id] = thermostat

            lock = Device(
                device_id="dev-lock-main",
                name="Front Door Smart Lock",
                category=DeviceCategory.ACCESS,
                protocol=ProtocolType.BLE,
                room_id="rm-living",
                home_id="home-master-01",
                capabilities=[
                    Capability(type=CapabilityType.DOOR_LOCK, name="Lock State", current_value=True)
                ],
                state={"locked": True, "battery": 92},
                battery_level=92
            )
            DEVICES_DB[lock.device_id] = lock

            solar = Device(
                device_id="dev-solar-inverter",
                name="Solar MPPT Inverter 8kW",
                category=DeviceCategory.ENERGY,
                protocol=ProtocolType.MODBUS,
                room_id="rm-garden",
                home_id="home-master-01",
                capabilities=[
                    Capability(type=CapabilityType.SOLAR_INVERTER, name="Solar Power Yield", unit="kW", read_only=True, current_value=4.82)
                ],
                state={"solar_kw": 4.82, "grid_export_kw": 1.25}
            )
            DEVICES_DB[solar.device_id] = solar

            garage = Device(
                device_id="dev-garage-door",
                name="Sectional Garage Door",
                category=DeviceCategory.ACCESS,
                protocol=ProtocolType.MQTT,
                room_id="rm-garage",
                home_id="home-master-01",
                capabilities=[
                    Capability(type=CapabilityType.GARAGE_DOOR, name="Door Position", current_value="CLOSED")
                ],
                state={"position": "CLOSED"}
            )
            DEVICES_DB[garage.device_id] = garage

    def list_devices(self, home_id: Optional[str] = None, room_id: Optional[str] = None) -> List[Device]:
        devices = list(DEVICES_DB.values())
        if home_id:
            devices = [d for d in devices if d.home_id == home_id]
        if room_id:
            devices = [d for d in devices if d.room_id == room_id]
        return devices

    def get_device(self, device_id: str) -> Optional[Device]:
        return DEVICES_DB.get(device_id)

    async def execute_command(self, device_id: str, command: str, value: Any, actor: str = "User") -> Device:
        device = DEVICES_DB.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        device.state[command] = value
        for cap in device.capabilities:
            if cap.type.value in command.lower() or command.lower() in cap.type.value:
                cap.current_value = value

        await global_event_bus.publish(DomainEvent(
            event_type="device.command_executed",
            source_service="device-service",
            home_id=device.home_id,
            device_id=device_id,
            payload={"command": command, "value": value, "actor": actor, "new_state": device.state}
        ))
        return device

device_service = DeviceService()
