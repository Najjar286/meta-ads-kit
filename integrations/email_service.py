"""SMTP email notification dispatcher."""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

logger = logging.getLogger(__name__)


class EmailService:
    """Sends alert and report notifications via SMTP email."""

    def __init__(self, smtp_host: str = "", smtp_port: int = 587,
                 username: str = "", password: str = "",
                 from_addr: str = "") -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._username = username
        self._password = password
        self._from_addr = from_addr

    def _send(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        if not self._smtp_host:
            logger.warning("SMTP not configured")
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self._from_addr
            msg["To"] = to
            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type))
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.starttls()
                if self._username:
                    server.login(self._username, self._password)
                server.sendmail(self._from_addr, [to], msg.as_string())
            return True
        except Exception as exc:
            logger.error("Email send failed: %s", exc)
            return False

    def send_alert(self, alert: Any, to: str = "") -> bool:
        if not to:
            return False
        severity = getattr(alert, "severity", "info")
        subject = f"[{severity.upper()}] {getattr(alert, 'rule_name', 'Alert')}"
        body = (f"Alert: {getattr(alert, 'rule_name', 'Unknown')}\n"
                f"Message: {getattr(alert, 'message', '')}\n"
                f"Entity: {getattr(alert, 'entity_name', 'Unknown')}\n"
                f"Value: {getattr(alert, 'metric_value', 0):.2f}")
        return self._send(to, subject, body)

    def send_report(self, to: str, subject: str, html_body: str) -> bool:
        return self._send(to, subject, html_body, html=True)
