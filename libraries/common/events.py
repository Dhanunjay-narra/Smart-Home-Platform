from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime, timezone
import uuid
import asyncio

class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    source_service: str
    home_id: Optional[str] = None
    device_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[DomainEvent], Awaitable[None]]]] = {}
        self._wildcard_subscribers: List[Callable[[DomainEvent], Awaitable[None]]] = []
        self._event_history: List[DomainEvent] = []
        self._max_history = 1000

    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Awaitable[None]]):
        if event_type == "*":
            self._wildcard_subscribers.append(handler)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        handlers = list(self._subscribers.get(event.event_type, [])) + self._wildcard_subscribers
        tasks = [asyncio.create_task(self._safe_execute(h, event)) for h in handlers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, handler, event: DomainEvent):
        try:
            await handler(event)
        except Exception as e:
            print(f"[EventBus] Error in {event.event_type}: {e}")

    def get_recent_events(self, limit: int = 50) -> List[DomainEvent]:
        return list(reversed(self._event_history[-limit:]))

global_event_bus = EventBus()
