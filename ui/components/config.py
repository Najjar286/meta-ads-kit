"""Component configuration defaults used across the UI layer."""
from __future__ import annotations

COMPONENT_CONFIG_DEFAULTS: dict = {
    "kpi_card": {
        "format": "num",
        "delta_direction": "up",
        "color": "default",
        "loading": False,
        "error": "",
    },
    "kpi_row": {
        "columns": 4,
    },
    "metric_table": {
        "page_size": 25,
        "max_rows": 1000,
        "sort_asc": False,
        "show_comparison": False,
    },
    "data_table": {
        "page_size": 50,
        "max_rows": 5000,
    },
    "top_performer_list": {
        "top_n": 5,
    },
    "charts": {
        "height": 400,
        "smooth": True,
        "barmode": "group",
        "max_slices": 10,
        "stacked": True,
        "max_value": 100,
        "threshold_good": 70,
        "threshold_warn": 40,
        "periods": 7,
    },
    "filters": {
        "date_presets": [
            ("Last 7 days", 7),
            ("Last 14 days", 14),
            ("Last 30 days", 30),
            ("Last 90 days", 90),
        ],
        "default_metrics": [
            "ctr", "cpc", "cpm", "cpa", "roas",
            "spend", "impressions", "clicks", "conversions", "frequency",
        ],
        "max_selections": 10,
    },
    "navigation": {
        "pages": [],
    },
    "actions": {
        "export_formats": ["csv", "xlsx", "json"],
        "refresh_interval": 0,
    },
    "feedback": {
        "empty_icon": "📭",
    },
}
