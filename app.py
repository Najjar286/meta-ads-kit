"""Meta Ads Commander v4 — Main entry point."""
from __future__ import annotations

import streamlit as st

from core.state_manager import StateManager
from core.entity_cascade import EntityCascade
from core.demo_data import generate_insights, generate_entities
from engines import create_metric_engine, AnalyticsEngine, AlertEngine, ExportEngine
from ui.styles import inject_theme_css
from ui.components import PageFooter, Sidebar
from page_views import (
    render_dashboard, render_analytics, render_alerts,
    render_export, render_settings,
)

_PAGES = [
    ("Dashboard", "📊"),
    ("Analytics", "📈"),
    ("Alerts", "🔔"),
    ("Export", "📥"),
    ("Settings", "⚙️"),
]


def _init_session() -> None:
    state = StateManager()

    if "df_raw" not in st.session_state:
        st.session_state.df_raw = generate_insights(days=60, seed=42)

    if "entity_cascade" not in st.session_state:
        ec = EntityCascade()
        entities = generate_entities()
        ec.load_from_entities(**entities)
        st.session_state.entity_cascade = ec

    if "metric_engine" not in st.session_state:
        st.session_state.metric_engine = create_metric_engine()

    if "analytics_engine" not in st.session_state:
        st.session_state.analytics_engine = AnalyticsEngine()

    if "alert_engine" not in st.session_state:
        st.session_state.alert_engine = AlertEngine()

    if "export_engine" not in st.session_state:
        st.session_state.export_engine = ExportEngine()


def main() -> None:
    st.set_page_config(
        page_title="Meta Ads Commander v4",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _init_session()

    state = StateManager()
    theme = state.get("theme", "dark")
    inject_theme_css(theme)

    current_page = Sidebar("main_sidebar", pages=_PAGES)

    ec = st.session_state.entity_cascade
    df = st.session_state.df_raw
    me = st.session_state.metric_engine
    analytics = st.session_state.analytics_engine
    alert_eng = st.session_state.alert_engine
    export_eng = st.session_state.export_engine

    if current_page == "Dashboard":
        render_dashboard(state, ec, df, me)
    elif current_page == "Analytics":
        render_analytics(state, ec, df, analytics)
    elif current_page == "Alerts":
        render_alerts(state, ec, df, alert_eng)
    elif current_page == "Export":
        render_export(state, ec, df, export_eng)
    elif current_page == "Settings":
        render_settings(state, ec, df, me)

    PageFooter("main_footer")

    toast_msg = state.get("toast_message")
    if toast_msg:
        severity = state.get("toast_severity", "info")
        if severity == "success":
            st.toast(toast_msg, icon="✅")
        elif severity == "error":
            st.toast(toast_msg, icon="❌")
        elif severity == "warning":
            st.toast(toast_msg, icon="⚠️")
        else:
            st.toast(toast_msg, icon="ℹ️")
        state.set("toast_message", None)


if __name__ == "__main__":
    main()
