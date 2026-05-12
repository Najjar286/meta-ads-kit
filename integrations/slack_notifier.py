"""Slack webhook notification dispatcher."""
from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Sends alert and message notifications via Slack webhook."""

    def __init__(self, webhook_url: str = "") -> None:
        self._webhook_url = webhook_url

    def _post(self, payload: dict) -> bool:
        if not self._webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self._webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as exc:
            logger.error("Slack notification failed: %s", exc)
            return False

    def send_alert(self, alert: Any) -> bool:
        severity = getattr(alert, "severity", "info")
        emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "ℹ️")
        payload = {
            "text": f"{emoji} *{getattr(alert, 'rule_name', 'Alert')}*\n"
                    f"{getattr(alert, 'message', '')}\n"
                    f"Entity: {getattr(alert, 'entity_name', 'Unknown')}",
        }
        return self._post(payload)

    def send_message(self, message: str, channel: str = "") -> bool:
        payload = {"text": message}
        if channel:
            payload["channel"] = channel
        return self._post(payload)
