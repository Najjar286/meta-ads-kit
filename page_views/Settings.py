"""Settings & Configuration — Theme, entity selection, data management, metric info."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core.entity_cascade import EntityCascade
from core.state_manager import StateManager
from engines.metric_engine import MetricEngine
from ui.components import (
    AccountSwitcher, ActionButton, EntityBreadcrumb, EntitySelector,
    PageHeader, SuccessMessage, ToggleGroup,
)


def render(state: StateManager, entity_cascade: EntityCascade,
           df: pd.DataFrame, metric_engine: MetricEngine | None = None):
    PageHeader("settings_header", title="Settings & Configuration",
               subtitle="Customize your experience",
               breadcrumbs=["Home", "Settings"])

    st.markdown("#### Theme")
    current_theme = state.get("theme", "dark")
    theme = ToggleGroup("theme_toggle", "Theme", options=["Dark", "Light"],
                        default=current_theme.capitalize())
    if theme and theme.lower() != current_theme:
        state.set("theme", theme.lower())
        st.rerun()

    st.divider()
    st.markdown("#### Entity Selection")
    AccountSwitcher("settings_acct", entity_cascade)
    EntitySelector("settings_campaign", entity_cascade, level="campaign")
    EntitySelector("settings_adset", entity_cascade, level="adset")
    EntitySelector("settings_ad", entity_cascade, level="ad")
    EntityBreadcrumb("settings_bread", entity_cascade)

    st.divider()
    st.markdown("#### Data Management")
    c1, c2 = st.columns(2)
    with c1:
        if ActionButton("regen_data", "Regenerate Demo Data", icon="🔄"):
            del st.session_state["df_raw"]
            if metric_engine:
                metric_engine.clear_cache()
            SuccessMessage("regen_ok", "Demo data regenerated")
            st.rerun()
    with c2:
        if ActionButton("clear_cache", "Clear Metric Cache", icon="🗑️"):
            if metric_engine:
                metric_engine.clear_cache()
            SuccessMessage("cache_ok", "Metric cache cleared")

    if metric_engine:
        st.divider()
        st.markdown("#### Metric System")
        counts = metric_engine.metric_count_by_tier()
        total = sum(counts.values())
        tier_labels = {1: "Standard KPIs", 2: "AXIOM", 3: "ARCHON", 4: "Composite"}
        cols = st.columns(len(counts) + 1)
        with cols[0]:
            st.metric("Total Metrics", total)
        for i, (tier, count) in enumerate(sorted(counts.items()), 1):
            with cols[i]:
                st.metric(tier_labels.get(tier, f"Tier {tier}"), count)

    st.divider()
    st.markdown("#### System Info")
    info_data = {
        "Python": __import__("sys").version.split()[0],
        "Streamlit": st.__version__,
        "Pandas": pd.__version__,
        "Data rows": f"{len(df):,}" if df is not None else "0",
    }
    for label, val in info_data.items():
        st.markdown(f"**{label}:** {val}")
