"""Alert Configuration for GLPI Dashboard."""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .connectivity_monitor import AlertSeverity


@dataclass
class AlertThreshold:
    """Alert threshold configuration."""
    metric: str
    warning_threshold: float
    critical_threshold: float
    comparison: str = "greater_than"  # greater_than, less_than, equals
    enabled: bool = True


@dataclass
class NotificationChannel:
    """Notification channel configuration."""
    name: str
    type: str  # email, webhook, log
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    severity_filter: List[AlertSeverity] = field(default_factory=list)


@dataclass
class AlertConfiguration:
    """Main alert configuration."""

    # Monitoring intervals
    connectivity_check_interval: int = 60  # seconds
    metrics_check_interval: int = 300  # seconds

    # Alert thresholds
    thresholds: List[AlertThreshold] = field(default_factory=list)

    # Notification channels
    notification_channels: List[NotificationChannel] = field(default_factory=list)

    # General settings
    max_alerts_per_hour: int = 100
    alert_retention_days: int = 30
    enable_alert_grouping: bool = True
    grouping_window_minutes: int = 5

    # Connectivity settings
    connectivity_timeout: int = 30  # seconds
    max_consecutive_failures: int = 3

    def __post_init__(self):
        """Initialize default configuration if not provided."""
        if not self.thresholds:
            self._setup_default_thresholds()

        if not self.notification_channels:
            self._setup_default_notification_channels()

    def _setup_default_thresholds(self):
        """Setup default alert thresholds."""
        self.thresholds = [
            AlertThreshold(
                metric="response_time",
                warning_threshold=2.0,  # seconds
                critical_threshold=5.0,
                comparison="greater_than"
            ),
            AlertThreshold(
                metric="error_rate",
                warning_threshold=0.05,  # 5%
                critical_threshold=0.10,  # 10%
                comparison="greater_than"
            ),
            AlertThreshold(
                metric="cpu_usage",
                warning_threshold=80.0,  # %
                critical_threshold=95.0,
                comparison="greater_than"
            ),
            AlertThreshold(
                metric="memory_usage",
                warning_threshold=85.0,  # %
                critical_threshold=95.0,
                comparison="greater_than"
            ),
            AlertThreshold(
                metric="disk_usage",
                warning_threshold=80.0,  # %
                critical_threshold=90.0,
                comparison="greater_than"
            )
        ]

    def _setup_default_notification_channels(self):
        """Setup default notification channels."""
        # Log channel (always enabled)
        self.notification_channels.append(
            NotificationChannel(
                name="log",
                type="log",
                config={"level": "INFO"},
                enabled=True,
                severity_filter=list(AlertSeverity)
            )
        )

        # Email channel (if configured)
        email_config = self._get_email_config()
        if email_config:
            self.notification_channels.append(
                NotificationChannel(
                    name="email",
                    type="email",
                    config=email_config,
                    enabled=True,
                    severity_filter=[AlertSeverity.HIGH, AlertSeverity.CRITICAL]
                )
            )

        # Webhook channel (if configured)
        webhook_config = self._get_webhook_config()
        if webhook_config:
            self.notification_channels.append(
                NotificationChannel(
                    name="webhook",
                    type="webhook",
                    config=webhook_config,
                    enabled=True,
                    severity_filter=[AlertSeverity.CRITICAL]
                )
            )

    def _get_email_config(self) -> Optional[Dict[str, Any]]:
        """Get email configuration from environment."""
        smtp_server = os.getenv('ALERT_SMTP_SERVER')
        smtp_port = os.getenv('ALERT_SMTP_PORT', '587')
        smtp_username = os.getenv('ALERT_SMTP_USERNAME')
        smtp_password = os.getenv('ALERT_SMTP_PASSWORD')
        from_email = os.getenv('ALERT_FROM_EMAIL')
        to_emails = os.getenv('ALERT_TO_EMAILS', '').split(',')

        if smtp_server and smtp_username and smtp_password and from_email:
            return {
                'smtp_server': smtp_server,
                'smtp_port': int(smtp_port),
                'username': smtp_username,
                'password': smtp_password,
                'from_email': from_email,
                'to_emails': [email.strip() for email in to_emails if email.strip()],
                'use_tls': os.getenv('ALERT_SMTP_TLS', 'true').lower() == 'true'
            }

        return None

    def _get_webhook_config(self) -> Optional[Dict[str, Any]]:
        """Get webhook configuration from environment."""
        webhook_url = os.getenv('ALERT_WEBHOOK_URL')
        webhook_token = os.getenv('ALERT_WEBHOOK_TOKEN')

        if webhook_url:
            config = {'url': webhook_url}
            if webhook_token:
                config['token'] = webhook_token
            return config

        return None

    def get_threshold(self, metric: str) -> Optional[AlertThreshold]:
        """Get threshold configuration for a metric."""
        for threshold in self.thresholds:
            if threshold.metric == metric and threshold.enabled:
                return threshold
        return None

    def get_notification_channels(self, severity: AlertSeverity) -> List[NotificationChannel]:
        """Get enabled notification channels for a severity level."""
        channels = []
        for channel in self.notification_channels:
            if (channel.enabled and
                (not channel.severity_filter or severity in channel.severity_filter)):
                channels.append(channel)
        return channels

    def update_threshold(self, metric: str, **kwargs):
        """Update threshold configuration."""
        for threshold in self.thresholds:
            if threshold.metric == metric:
                for key, value in kwargs.items():
                    if hasattr(threshold, key):
                        setattr(threshold, key, value)
                return True
        return False

    def enable_channel(self, channel_name: str, enabled: bool = True):
        """Enable or disable a notification channel."""
        for channel in self.notification_channels:
            if channel.name == channel_name:
                channel.enabled = enabled
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'connectivity_check_interval': self.connectivity_check_interval,
            'metrics_check_interval': self.metrics_check_interval,
            'max_alerts_per_hour': self.max_alerts_per_hour,
            'alert_retention_days': self.alert_retention_days,
            'enable_alert_grouping': self.enable_alert_grouping,
            'grouping_window_minutes': self.grouping_window_minutes,
            'connectivity_timeout': self.connectivity_timeout,
            'max_consecutive_failures': self.max_consecutive_failures,
            'thresholds': [
                {
                    'metric': t.metric,
                    'warning_threshold': t.warning_threshold,
                    'critical_threshold': t.critical_threshold,
                    'comparison': t.comparison,
                    'enabled': t.enabled
                }
                for t in self.thresholds
            ],
            'notification_channels': [
                {
                    'name': c.name,
                    'type': c.type,
                    'enabled': c.enabled,
                    'severity_filter': [s.value for s in c.severity_filter]
                }
                for c in self.notification_channels
            ]
        }


# Global configuration instance
_config_instance: Optional[AlertConfiguration] = None


def get_alert_config() -> AlertConfiguration:
    """Get global alert configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AlertConfiguration()
    return _config_instance


def set_alert_config(config: AlertConfiguration):
    """Set global alert configuration instance."""
    global _config_instance
    _config_instance = config
