"""Integration modules: Slack and Email notification dispatchers."""
from __future__ import annotations

from integrations.slack_notifier import SlackNotifier
from integrations.email_service import EmailService

__all__ = ["SlackNotifier", "EmailService"]
