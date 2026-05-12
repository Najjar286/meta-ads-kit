"""Filter components: DateRangeFilter, ComparisonPeriodToggle, MetricSelector, SearchBar, MultiSelectFilter, ToggleGroup, SliderFilter."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import streamlit as st

from core.state_manager import StateManager


def DateRangeFilter(key: str, presets: list[tuple[str, int]] | None = None):
    state = StateManager()
    presets = presets or [("Last 7 days", 7), ("Last 14 days", 14), ("Last 30 days", 30),
                          ("Last 90 days", 90)]
    current = state.get("date_range", (7, 0))
    labels = [p[0] for p in presets]
    current_label = next((p[0] for p in presets if p[1] == current[0]), "Custom")
    col1, col2 = st.columns([1, 2])
    with col1:
        selected = st.selectbox("Range", labels,
                                index=labels.index(current_label) if current_label in labels else 0,
                                key=f"{key}_preset")
        days = next((p[1] for p in presets if p[0] == selected), 7)
        if days != current[0]:
            state.set("date_range", (days, 0), source="date_filter")
    with col2:
        end = datetime.now()
        start = end - timedelta(days=days)
        date_range = st.date_input("Custom", [start.date(), end.date()], key=f"{key}_custom")
        if len(date_range) == 2:
            custom_days = (date_range[1] - date_range[0]).days
            if custom_days != current[0]:
                state.set("date_range", (custom_days, 0), source="date_filter")


def ComparisonPeriodToggle(key: str):
    state = StateManager()
    enabled = state.get("comparison_period", False)
    toggled = st.toggle("Compare to previous period", value=enabled, key=key)
    if toggled != enabled:
        state.set("comparison_period", toggled, source="comparison_toggle")


def MetricSelector(key: str, available_metrics: list[str] | None = None,
                   selected_metrics: list[str] | None = None,
                   label: str = "Metrics", max_selections: int = 10):
    if not available_metrics:
        available_metrics = ["ctr", "cpc", "cpm", "cpa", "roas", "spend", "impressions",
                             "clicks", "conversions", "frequency"]
    default = selected_metrics or available_metrics[:5]
    selected = st.multiselect(label, available_metrics, default=default,
                              max_selections=max_selections, key=key)
    return selected


def SearchBar(key: str, placeholder: str = "Search entities...", on_search: Any = None):
    query = st.text_input("", placeholder=placeholder, key=key, label_visibility="collapsed")
    return query.strip() if query else ""


def MultiSelectFilter(key: str, label: str, options: list[str], default: list[str] | None = None):
    return st.multiselect(label, options, default=default or options, key=key)


def ToggleGroup(key: str, label: str, options: list[str], default: str | None = None):
    return st.segmented_control(label, options, default=default or options[0], key=key,
                                selection_mode="single")


def SliderFilter(key: str, label: str, min_value: float = 0.0, max_value: float = 100.0,
                 value: tuple[float, float] = (0.0, 100.0), step: float = 1.0):
    return st.slider(label, min_value=min_value, max_value=max_value, value=value,
                     step=step, key=key)
