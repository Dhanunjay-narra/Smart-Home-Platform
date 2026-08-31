from typing import Dict, Any, List
from services.notification.models import NotificationMessage, NotificationChannel, NotificationPriority
from libraries.common.events import global_event_bus, DomainEvent

NOTIFICATIONS_DB: List[NotificationMessage] = []

class NotificationDispatcher:
    def __init__(self):
        global_event_bus.subscribe("security.alarm_triggered", self._handle_security_alert)
        global_event_bus.subscribe("home.mode_changed", self._handle_mode_alert)

    async def _handle_security_alert(self, event: DomainEvent):
        msg = NotificationMessage(
            recipient_user_id="usr-admin-001",
            home_id=event.home_id,
            title="SECURITY ALERT",
            body=event.payload.get("description", "Security incident detected!"),
            priority=NotificationPriority.EMERGENCY,
            channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH, NotificationChannel.SMS]
        )
        NOTIFICATIONS_DB.append(msg)

    async def _handle_mode_alert(self, event: DomainEvent):
        msg = NotificationMessage(
            recipient_user_id="usr-admin-001",
            home_id=event.home_id,
            title="Home Mode Updated",
            body=f"Home mode changed to {event.payload.get('new_mode')} by {event.payload.get('actor')}",
            priority=NotificationPriority.NORMAL,
            channels=[NotificationChannel.IN_APP]
        )
        NOTIFICATIONS_DB.append(msg)

    def list_notifications(self, user_id: str, limit: int = 50) -> List[NotificationMessage]:
        return list(reversed(NOTIFICATIONS_DB[-limit:]))

notification_dispatcher = NotificationDispatcher()
