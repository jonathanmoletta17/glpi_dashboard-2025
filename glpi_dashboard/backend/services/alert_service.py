"""Alert Service for GLPI Dashboard."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .connectivity_monitor import ConnectivityEvent, AlertSeverity

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    title: str
    message: str
    source: str
    details: Optional[Dict] = None
    acknowledged: bool = False
    resolved: bool = False


class GLPIAlertService:
    """GLPI Alert Service for managing alerts."""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Any] = []
        self.alert_counter = 0

    def add_alert_handler(self, handler: Any):
        """Add alert handler."""
        self.alert_handlers.append(handler)
        logger.info(f"Added alert handler: {handler.__class__.__name__}")

    async def process_connectivity_event(self, event: ConnectivityEvent):
        """Process connectivity event and create alert if needed."""
        try:
            # Create alert for significant events
            if event.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                alert = self._create_alert_from_event(event)
                await self._send_alert(alert)

            logger.info(f"Processed connectivity event: {event.message}")

        except Exception as e:
            logger.error(f"Error processing connectivity event: {e}")

    def _create_alert_from_event(self, event: ConnectivityEvent) -> Alert:
        """Create alert from connectivity event."""
        self.alert_counter += 1

        alert = Alert(
            id=f"alert_{self.alert_counter}_{int(event.timestamp.timestamp())}",
            timestamp=event.timestamp,
            severity=event.severity,
            title=f"Connectivity Alert - {event.status.value.title()}",
            message=event.message,
            source="connectivity_monitor",
            details=event.details or {}
        )

        self.alerts.append(alert)
        return alert

    async def _send_alert(self, alert: Alert):
        """Send alert to all handlers."""
        for handler in self.alert_handlers:
            try:
                if hasattr(handler, 'send_alert'):
                    if hasattr(handler.send_alert, '__call__'):
                        if hasattr(handler.send_alert, '__code__') and \
                           handler.send_alert.__code__.co_flags & 0x80:  # CO_COROUTINE
                            await handler.send_alert(alert)
                        else:
                            handler.send_alert(alert)
                    else:
                        logger.warning(f"Handler {handler} does not have callable send_alert method")
                else:
                    logger.warning(f"Handler {handler} does not have send_alert method")
            except Exception as e:
                logger.error(f"Error sending alert via handler {handler}: {e}")

    def create_manual_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        source: str = "manual",
        details: Optional[Dict] = None
    ) -> Alert:
        """Create manual alert."""
        self.alert_counter += 1

        alert = Alert(
            id=f"manual_{self.alert_counter}_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(),
            severity=severity,
            title=title,
            message=message,
            source=source,
            details=details or {}
        )

        self.alerts.append(alert)
        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged")
                return True

        logger.warning(f"Alert {alert_id} not found")
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} resolved")
                return True

        logger.warning(f"Alert {alert_id} not found")
        return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity."""
        return [alert for alert in self.alerts if alert.severity == severity]

    def get_alert_summary(self) -> Dict:
        """Get alert summary statistics."""
        active_alerts = self.get_active_alerts()

        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "acknowledged_alerts": len([a for a in active_alerts if a.acknowledged]),
            "unacknowledged_alerts": len([a for a in active_alerts if not a.acknowledged]),
            "alerts_by_severity": {
                severity.value: len(self.get_alerts_by_severity(severity))
                for severity in AlertSeverity
            },
            "recent_alerts": [
                {
                    "id": alert.id,
                    "timestamp": alert.timestamp.isoformat(),
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "acknowledged": alert.acknowledged,
                    "resolved": alert.resolved
                }
                for alert in sorted(self.alerts, key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }
