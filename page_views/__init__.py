"""Page view modules — pure component composition."""
from __future__ import annotations

from page_views.Dashboard import render as render_dashboard
from page_views.Analytics import render as render_analytics
from page_views.Alerts import render as render_alerts
from page_views.Export import render as render_export
from page_views.Settings import render as render_settings

__all__ = [
    "render_dashboard",
    "render_analytics",
    "render_alerts",
    "render_export",
    "render_settings",
]
