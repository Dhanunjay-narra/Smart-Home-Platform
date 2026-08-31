from typing import Dict, Any, List, Optional
from services.home.models import Home, Building, Floor, Room, HomeMode, ZoneType
from libraries.common.events import global_event_bus, DomainEvent

HOMES_DB: Dict[str, Home] = {}

class HomeService:
    def __init__(self):
        self._seed_default_home()

    def _seed_default_home(self):
        if not HOMES_DB:
            home = Home(
                home_id="home-master-01",
                name="Smart Villa 2026",
                timezone="Asia/Kolkata",
                current_mode=HomeMode.HOME
            )
            main_building = Building(
                building_id="bld-main",
                name="Main Residence",
                home_id=home.home_id
            )
            
            ground_floor = Floor(floor_id="flr-0", name="Ground Floor", level=0, building_id="bld-main")
            ground_floor.rooms = [
                Room(room_id="rm-living", name="Living Room", floor_id="flr-0", zone_type=ZoneType.INDOOR, icon="couch"),
                Room(room_id="rm-kitchen", name="Smart Kitchen", floor_id="flr-0", zone_type=ZoneType.INDOOR, icon="utensils"),
                Room(room_id="rm-garage", name="Smart Garage", floor_id="flr-0", zone_type=ZoneType.GARAGE, icon="warehouse"),
                Room(room_id="rm-garden", name="Garden & Patio", floor_id="flr-0", zone_type=ZoneType.GARDEN, icon="tree")
            ]

            first_floor = Floor(floor_id="flr-1", name="First Floor", level=1, building_id="bld-main")
            first_floor.rooms = [
                Room(room_id="rm-master-bed", name="Master Bedroom", floor_id="flr-1", zone_type=ZoneType.INDOOR, icon="bed"),
                Room(room_id="rm-office", name="Home Office / Lab", floor_id="flr-1", zone_type=ZoneType.INDOOR, icon="laptop-code"),
                Room(room_id="rm-balcony", name="Sky Balcony", floor_id="flr-1", zone_type=ZoneType.OUTDOOR, icon="cloud-sun")
            ]

            main_building.floors = [ground_floor, first_floor]
            home.buildings = [main_building]
            HOMES_DB[home.home_id] = home

    def get_home(self, home_id: str) -> Optional[Home]:
        return HOMES_DB.get(home_id)

    def list_homes(self) -> List[Home]:
        return list(HOMES_DB.values())

    async def set_home_mode(self, home_id: str, new_mode: HomeMode, actor: str = "User") -> Home:
        home = HOMES_DB.get(home_id)
        if not home:
            raise ValueError(f"Home {home_id} not found")
        old_mode = home.current_mode
        home.current_mode = new_mode

        await global_event_bus.publish(DomainEvent(
            event_type="home.mode_changed",
            source_service="home-service",
            home_id=home_id,
            payload={"old_mode": old_mode.value, "new_mode": new_mode.value, "actor": actor}
        ))
        return home

home_service = HomeService()
