"""Alert Handlers for GLPI Dashboard Alert System."""

import asyncio
import smtplib
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import aiohttp
import os
from dataclasses import dataclass


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    title: str
    message: str
    severity: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False


class AlertHandler(ABC):
    """Abstract base class for alert handlers."""

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"alert_handler.{name}")
        self.enabled = self.config.get('enabled', True)

    @abstractmethod
    async def handle_alert(self, alert: Alert) -> bool:
        """Handle an alert. Return True if successful, False otherwise."""
        pass

    def is_enabled(self) -> bool:
        """Check if handler is enabled."""
        return self.enabled

    def should_handle_severity(self, severity: str) -> bool:
        """Check if handler should handle alerts of given severity."""
        min_severity = self.config.get('min_severity', 'low')
        severity_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

        return severity_levels.get(severity, 1) >= severity_levels.get(min_severity, 1)


class LogAlertHandler(AlertHandler):
    """Handler that logs alerts to the application log."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("log", config)

        # Configure log level based on alert severity
        self.severity_log_levels = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }

    async def handle_alert(self, alert: Alert) -> bool:
        """Log the alert."""
        try:
            if not self.should_handle_severity(alert.severity):
                return True

            log_level = self.severity_log_levels.get(alert.severity, logging.INFO)

            log_message = (
                f"ALERT [{alert.severity.upper()}] {alert.title}: {alert.message} "
                f"(Source: {alert.source}, ID: {alert.id})"
            )

            if alert.metadata:
                log_message += f" Metadata: {json.dumps(alert.metadata, default=str)}"

            self.logger.log(log_level, log_message)

            # Also log to structured format for audit
            structured_data = {
                'alert_id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'source': alert.source,
                'timestamp': alert.timestamp.isoformat(),
                'metadata': alert.metadata,
                'acknowledged': alert.acknowledged,
                'resolved': alert.resolved
            }

            self.logger.info(
                f"Alert processed by LogHandler",
                extra={'alert_data': structured_data}
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to log alert {alert.id}: {str(e)}")
            return False


class EmailAlertHandler(AlertHandler):
    """Handler that sends alerts via email."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("email", config)

        # Email configuration
        self.smtp_server = self.config.get('smtp_server', os.getenv('SMTP_SERVER', 'localhost'))
        self.smtp_port = self.config.get('smtp_port', int(os.getenv('SMTP_PORT', '587')))
        self.smtp_username = self.config.get('smtp_username', os.getenv('SMTP_USERNAME'))
        self.smtp_password = self.config.get('smtp_password', os.getenv('SMTP_PASSWORD'))
        self.use_tls = self.config.get('use_tls', os.getenv('SMTP_USE_TLS', 'true').lower() == 'true')

        self.from_email = self.config.get('from_email', os.getenv('ALERT_FROM_EMAIL', 'alerts@glpi.local'))
        self.to_emails = self.config.get('to_emails', [])

        # Add default recipients from environment
        env_recipients = os.getenv('ALERT_RECIPIENTS', '')
        if env_recipients:
            self.to_emails.extend([email.strip() for email in env_recipients.split(',')])

        # Email templates
        self.subject_template = self.config.get(
            'subject_template',
            "[GLPI Alert - {severity}] {title}"
        )

        self.body_template = self.config.get(
            'body_template',
            """
GLPI Dashboard Alert

Title: {title}
Severity: {severity}
Source: {source}
Timestamp: {timestamp}

Message:
{message}

Metadata:
{metadata}

Alert ID: {id}

---
This is an automated alert from GLPI Dashboard.
"""
        )

    async def handle_alert(self, alert: Alert) -> bool:
        """Send alert via email."""
        try:
            if not self.should_handle_severity(alert.severity):
                return True

            if not self.to_emails:
                self.logger.warning("No email recipients configured for alerts")
                return False

            if not self.smtp_username or not self.smtp_password:
                self.logger.warning("SMTP credentials not configured")
                return False

            # Format email content
            subject = self.subject_template.format(
                severity=alert.severity.upper(),
                title=alert.title,
                id=alert.id
            )

            metadata_str = json.dumps(alert.metadata, indent=2, default=str) if alert.metadata else "None"

            body = self.body_template.format(
                title=alert.title,
                severity=alert.severity.upper(),
                source=alert.source,
                timestamp=alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                message=alert.message,
                metadata=metadata_str,
                id=alert.id
            )

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Send email (run in thread to avoid blocking)
            await asyncio.get_event_loop().run_in_executor(
                None, self._send_email_sync, msg
            )

            self.logger.info(
                f"Alert {alert.id} sent via email to {len(self.to_emails)} recipients"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to send email alert {alert.id}: {str(e)}")
            return False

    def _send_email_sync(self, msg: MIMEMultipart):
        """Send email synchronously (to be run in executor)."""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()

            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            server.send_message(msg)


class WebhookAlertHandler(AlertHandler):
    """Handler that sends alerts to webhook endpoints."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("webhook", config)

        self.webhook_urls = self.config.get('webhook_urls', [])
        self.timeout = self.config.get('timeout', 30)
        self.retry_count = self.config.get('retry_count', 3)
        self.retry_delay = self.config.get('retry_delay', 1)

        # Add webhook URLs from environment
        env_webhooks = os.getenv('ALERT_WEBHOOK_URLS', '')
        if env_webhooks:
            self.webhook_urls.extend([url.strip() for url in env_webhooks.split(',')])

    async def handle_alert(self, alert: Alert) -> bool:
        """Send alert to webhook endpoints."""
        try:
            if not self.should_handle_severity(alert.severity):
                return True

            if not self.webhook_urls:
                self.logger.warning("No webhook URLs configured for alerts")
                return False

            # Prepare webhook payload
            payload = {
                'alert_id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'source': alert.source,
                'timestamp': alert.timestamp.isoformat(),
                'metadata': alert.metadata,
                'acknowledged': alert.acknowledged,
                'resolved': alert.resolved
            }

            success_count = 0

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                for webhook_url in self.webhook_urls:
                    if await self._send_webhook(session, webhook_url, payload, alert.id):
                        success_count += 1

            # Consider successful if at least one webhook succeeded
            success = success_count > 0

            if success:
                self.logger.info(
                    f"Alert {alert.id} sent to {success_count}/{len(self.webhook_urls)} webhooks"
                )
            else:
                self.logger.error(f"Failed to send alert {alert.id} to any webhook")

            return success

        except Exception as e:
            self.logger.error(f"Failed to send webhook alert {alert.id}: {str(e)}")
            return False

    async def _send_webhook(self, session: aiohttp.ClientSession, url: str, payload: Dict[str, Any], alert_id: str) -> bool:
        """Send webhook with retry logic."""
        for attempt in range(self.retry_count):
            try:
                async with session.post(url, json=payload) as response:
                    if response.status < 400:
                        self.logger.debug(f"Webhook sent successfully to {url} for alert {alert_id}")
                        return True
                    else:
                        self.logger.warning(
                            f"Webhook to {url} returned status {response.status} for alert {alert_id}"
                        )

            except Exception as e:
                self.logger.warning(
                    f"Webhook attempt {attempt + 1}/{self.retry_count} to {url} failed for alert {alert_id}: {str(e)}"
                )

                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        return False


class SlackAlertHandler(AlertHandler):
    """Handler that sends alerts to Slack channels."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("slack", config)

        self.webhook_url = self.config.get('webhook_url', os.getenv('SLACK_WEBHOOK_URL'))
        self.channel = self.config.get('channel', '#alerts')
        self.username = self.config.get('username', 'GLPI Dashboard')
        self.timeout = self.config.get('timeout', 30)

        # Severity to color mapping
        self.severity_colors = {
            'low': '#36a64f',      # Green
            'medium': '#ff9500',   # Orange
            'high': '#ff0000',     # Red
            'critical': '#8b0000'  # Dark Red
        }

    async def handle_alert(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        try:
            if not self.should_handle_severity(alert.severity):
                return True

            if not self.webhook_url:
                self.logger.warning("Slack webhook URL not configured")
                return False

            # Create Slack message
            color = self.severity_colors.get(alert.severity, '#808080')

            attachment = {
                'color': color,
                'title': f"🚨 {alert.title}",
                'text': alert.message,
                'fields': [
                    {
                        'title': 'Severity',
                        'value': alert.severity.upper(),
                        'short': True
                    },
                    {
                        'title': 'Source',
                        'value': alert.source,
                        'short': True
                    },
                    {
                        'title': 'Timestamp',
                        'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                        'short': True
                    },
                    {
                        'title': 'Alert ID',
                        'value': alert.id,
                        'short': True
                    }
                ],
                'footer': 'GLPI Dashboard',
                'ts': int(alert.timestamp.timestamp())
            }

            # Add metadata if present
            if alert.metadata:
                metadata_text = '\n'.join([f"• {k}: {v}" for k, v in alert.metadata.items()])
                attachment['fields'].append({
                    'title': 'Metadata',
                    'value': metadata_text,
                    'short': False
                })

            payload = {
                'channel': self.channel,
                'username': self.username,
                'attachments': [attachment]
            }

            # Send to Slack
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status < 400:
                        self.logger.info(f"Alert {alert.id} sent to Slack successfully")
                        return True
                    else:
                        self.logger.error(
                            f"Slack webhook returned status {response.status} for alert {alert.id}"
                        )
                        return False

        except Exception as e:
            self.logger.error(f"Failed to send Slack alert {alert.id}: {str(e)}")
            return False


class CompositeAlertHandler(AlertHandler):
    """Handler that delegates to multiple other handlers."""

    def __init__(self, handlers: List[AlertHandler], config: Dict[str, Any] = None):
        super().__init__("composite", config)
        self.handlers = handlers
        self.require_all_success = self.config.get('require_all_success', False)

    async def handle_alert(self, alert: Alert) -> bool:
        """Handle alert with all configured handlers."""
        try:
            results = []

            # Execute all handlers concurrently
            tasks = [
                handler.handle_alert(alert)
                for handler in self.handlers
                if handler.is_enabled()
            ]

            if not tasks:
                self.logger.warning("No enabled handlers available")
                return False

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            success_count = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(
                        f"Handler {self.handlers[i].name} failed with exception: {str(result)}"
                    )
                elif result:
                    success_count += 1

            # Determine overall success
            if self.require_all_success:
                success = success_count == len(tasks)
            else:
                success = success_count > 0

            self.logger.info(
                f"Alert {alert.id} handled by {success_count}/{len(tasks)} handlers "
                f"(success: {success})"
            )

            return success

        except Exception as e:
            self.logger.error(f"Failed to handle alert {alert.id} with composite handler: {str(e)}")
            return False


# Factory function to create handlers from configuration
def create_alert_handler(handler_type: str, config: Dict[str, Any] = None) -> AlertHandler:
    """Create an alert handler of the specified type."""
    handlers = {
        'log': LogAlertHandler,
        'email': EmailAlertHandler,
        'webhook': WebhookAlertHandler,
        'slack': SlackAlertHandler
    }

    handler_class = handlers.get(handler_type.lower())
    if not handler_class:
        raise ValueError(f"Unknown handler type: {handler_type}")

    return handler_class(config)


def create_handlers_from_config(config: Dict[str, Any]) -> List[AlertHandler]:
    """Create multiple handlers from configuration."""
    handlers = []

    for handler_config in config.get('handlers', []):
        handler_type = handler_config.get('type')
        handler_settings = handler_config.get('config', {})

        if handler_type:
            try:
                handler = create_alert_handler(handler_type, handler_settings)
                handlers.append(handler)
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to create handler {handler_type}: {str(e)}"
                )

    return handlers
