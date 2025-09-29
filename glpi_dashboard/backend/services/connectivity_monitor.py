"""Connectivity Monitor for GLPI Dashboard."""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConnectivityStatus(Enum):
    """Connectivity status types."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ConnectivityEvent:
    """Connectivity event data."""
    timestamp: datetime
    status: ConnectivityStatus
    severity: AlertSeverity
    message: str
    details: Optional[Dict] = None


class ConnectivityMonitor:
    """Monitor connectivity and trigger alerts."""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.is_running = False
        self.current_status = ConnectivityStatus.UNKNOWN
        self.last_check = None
        self.event_handlers: List[Callable] = []
        self.events: List[ConnectivityEvent] = []

    def add_event_handler(self, handler: Callable):
        """Add event handler for connectivity events."""
        self.event_handlers.append(handler)

    async def start_monitoring(self):
        """Start connectivity monitoring."""
        self.is_running = True
        logger.info("Starting connectivity monitoring")

        while self.is_running:
            try:
                await self._check_connectivity()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in connectivity monitoring: {e}")
                await asyncio.sleep(self.check_interval)

    def stop_monitoring(self):
        """Stop connectivity monitoring."""
        self.is_running = False
        logger.info("Stopping connectivity monitoring")

    async def _check_connectivity(self):
        """Check connectivity status."""
        try:
            # Simulate connectivity check
            # In real implementation, this would check GLPI API
            import random

            # Simulate different connectivity states
            rand = random.random()
            if rand > 0.9:
                new_status = ConnectivityStatus.DISCONNECTED
                severity = AlertSeverity.CRITICAL
                message = "GLPI API is unreachable"
            elif rand > 0.8:
                new_status = ConnectivityStatus.DEGRADED
                severity = AlertSeverity.HIGH
                message = "GLPI API response time is degraded"
            else:
                new_status = ConnectivityStatus.CONNECTED
                severity = AlertSeverity.LOW
                message = "GLPI API is healthy"

            # Check if status changed
            if new_status != self.current_status:
                event = ConnectivityEvent(
                    timestamp=datetime.now(),
                    status=new_status,
                    severity=severity,
                    message=message,
                    details={"previous_status": self.current_status.value}
                )

                self.current_status = new_status
                self.last_check = datetime.now()
                self.events.append(event)

                # Notify handlers
                for handler in self.event_handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {e}")

            self.last_check = datetime.now()

        except Exception as e:
            logger.error(f"Connectivity check failed: {e}")

            # Create failure event
            event = ConnectivityEvent(
                timestamp=datetime.now(),
                status=ConnectivityStatus.UNKNOWN,
                severity=AlertSeverity.CRITICAL,
                message=f"Connectivity check failed: {str(e)}",
                details={"error": str(e)}
            )

            self.events.append(event)
            self.current_status = ConnectivityStatus.UNKNOWN

    def get_status(self) -> ConnectivityStatus:
        """Get current connectivity status."""
        return self.current_status

    def get_recent_events(self, hours: int = 24) -> List[ConnectivityEvent]:
        """Get recent connectivity events."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [event for event in self.events if event.timestamp >= cutoff]

    def get_health_summary(self) -> Dict:
        """Get health summary."""
        recent_events = self.get_recent_events()

        return {
            "current_status": self.current_status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "is_monitoring": self.is_running,
            "recent_events_count": len(recent_events),
            "events_by_severity": {
                severity.value: len([
                    e for e in recent_events
                    if e.severity == severity
                ]) for severity in AlertSeverity
            }
        }
