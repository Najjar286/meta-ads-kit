"""Meta Ads Commander v4 — Unified Product.

Single entry point that integrates ALL functionality:
- V4 Genius Core: Dashboard, Analytics, Alerts, Export, Settings (5 pages)
- Ultimate Dashboard: Campaign Manager, Ad Sets, Ads, Audiences, Budget Center,
  Performance Monitor, Rules Engine, A/B Testing, Funnel & Attribution,
  Report Builder, Activity Log, Data Studio, Meta Settings, Profile Manager (14 pages)
- Monster Analyst: Data Hub (Import/Link/KPI/Explorer/Metric Lab/Export),
  Financial Analysis, Funnel Analysis, Creative Audit, Algorithm Health,
  Multi Source Report, Messaging Analysis, Video Analysis, Deep Analysis,
  Analysis Dashboard, Analysis Settings (11 pages)
Total: 30 pages in one unified product.
"""
from __future__ import annotations

import streamlit as st

from core.state_manager import StateManager
from core.entity_cascade import EntityCascade
from core.demo_data import generate_insights, generate_entities
from engines import create_metric_engine, AnalyticsEngine, AlertEngine, ExportEngine
from ui.styles import inject_theme_css
from ui.components import PageFooter, Sidebar

# V4 Genius Core page views (take state, ec, df, engine args)
from page_views import (
    render_dashboard, render_analytics, render_alerts,
    render_export, render_settings,
)

# ─── Page imports: Ultimate Dashboard (src/pages) ────────────────────────────
from src.pages import (
    _01_Campaign_Manager as pg_campaign,
    _02_Ad_Sets as pg_adsets,
    _03_Ads as pg_ads,
    _04_Audiences as pg_audiences,
    _05_Budget_Center as pg_budget,
    _06_Performance as pg_performance,
    _07_Rules_Engine as pg_rules,
    _08_AB_Testing as pg_ab_testing,
    _09_Funnel_Attribution as pg_funnel_attr,
    _10_Report_Builder as pg_report_builder,
    _11_Activity_Log as pg_activity_log,
    _12_Data_Studio as pg_data_studio,
    _13_Settings as pg_meta_settings,
    _14_Profile_Manager as pg_profile_mgr,
)

# ─── Page imports: Monster Analyst ───────────────────────────────────────────
from monster_analyst import app as pg_data_hub
from monster_analyst.pages import (
    _1_Financial_Analysis as pg_financial,
    _2_Funnel_Analysis as pg_funnel,
    _3_Creative_Audit as pg_creative,
    _4_Algorithm_Health as pg_algo,
    _5_Multi_Source_Report as pg_multisource,
    _6_Messaging_Analysis as pg_messaging,
    _7_Dashboard as pg_analysis_dash,
    _7_Settings as pg_analysis_settings,
    _8_Video_Analysis as pg_video,
    _9_Deep_Analysis as pg_deep,
)

# ─── Navigation Sections ────────────────────────────────────────────────────
_SECTIONS = {
    "Core": [
        ("Dashboard", "📊"),
        ("Analytics", "📈"),
        ("Alerts", "🔔"),
        ("Export", "📥"),
    ],
    "Campaign Management": [
        ("Campaign Manager", "📋"),
        ("Ad Sets", "🎯"),
        ("Ads", "📱"),
        ("Audiences", "👥"),
        ("Budget Center", "💰"),
    ],
    "Performance & Optimization": [
        ("Performance Monitor", "⚡"),
        ("Rules Engine", "🔧"),
        ("A/B Testing", "🧪"),
        ("Funnel & Attribution", "🔀"),
    ],
    "Reports & Tools": [
        ("Report Builder", "📄"),
        ("Activity Log", "📝"),
        ("Data Studio", "🔬"),
        ("Profile Manager", "👤"),
    ],
    "Data & Analysis": [
        ("Data Hub", "📂"),
        ("Financial Analysis", "💲"),
        ("Funnel Analysis", "🔻"),
        ("Creative Audit", "🎨"),
        ("Algorithm Health", "🤖"),
    ],
    "Advanced Analysis": [
        ("Multi Source Report", "📊"),
        ("Messaging Analysis", "💬"),
        ("Video Analysis", "🎬"),
        ("Deep Analysis", "🔍"),
        ("Analysis Dashboard", "📈"),
    ],
    "Settings": [
        ("App Settings", "⚙️"),
        ("Meta Settings", "🔧"),
        ("Analysis Settings", "📐"),
    ],
}

# ─── Routing table ───────────────────────────────────────────────────────────
# Maps page name → (renderer_type, renderer)
#   "v4"   → calls renderer(state, ec, df, engine)
#   "page" → calls renderer.render()  (no args, reads from session_state)

_PAGE_ROUTER: dict[str, tuple[str, object]] = {
    # Core (V4 genius)
    "Dashboard": ("v4", render_dashboard),
    "Analytics": ("v4", render_analytics),
    "Alerts": ("v4", render_alerts),
    "Export": ("v4", render_export),
    "App Settings": ("v4", render_settings),
    # Campaign Management (ultimate-dashboard)
    "Campaign Manager": ("page", pg_campaign),
    "Ad Sets": ("page", pg_adsets),
    "Ads": ("page", pg_ads),
    "Audiences": ("page", pg_audiences),
    "Budget Center": ("page", pg_budget),
    # Performance & Optimization (ultimate-dashboard)
    "Performance Monitor": ("page", pg_performance),
    "Rules Engine": ("page", pg_rules),
    "A/B Testing": ("page", pg_ab_testing),
    "Funnel & Attribution": ("page", pg_funnel_attr),
    # Reports & Tools (ultimate-dashboard)
    "Report Builder": ("page", pg_report_builder),
    "Activity Log": ("page", pg_activity_log),
    "Data Studio": ("page", pg_data_studio),
    "Profile Manager": ("page", pg_profile_mgr),
    # Meta Settings (ultimate-dashboard)
    "Meta Settings": ("page", pg_meta_settings),
    # Data & Analysis (monster-analyst)
    "Data Hub": ("page", pg_data_hub),
    "Financial Analysis": ("page", pg_financial),
    "Funnel Analysis": ("page", pg_funnel),
    "Creative Audit": ("page", pg_creative),
    "Algorithm Health": ("page", pg_algo),
    # Advanced Analysis (monster-analyst)
    "Multi Source Report": ("page", pg_multisource),
    "Messaging Analysis": ("page", pg_messaging),
    "Video Analysis": ("page", pg_video),
    "Deep Analysis": ("page", pg_deep),
    "Analysis Dashboard": ("page", pg_analysis_dash),
    # Analysis Settings (monster-analyst)
    "Analysis Settings": ("page", pg_analysis_settings),
}


def _init_session() -> None:
    """Initialize all session state for every module."""
    StateManager()

    # V4 Core data
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

    # Monster Analyst data hub session state
    if "datasets" not in st.session_state:
        st.session_state.datasets = {}
    if "dataset_sources" not in st.session_state:
        st.session_state.dataset_sources = {}
    if "merged_data" not in st.session_state:
        st.session_state.merged_data = None
    if "custom_metrics" not in st.session_state:
        try:
            from monster_analyst.src.helpers import load_custom_metrics
            st.session_state.custom_metrics = load_custom_metrics()
        except Exception:
            st.session_state.custom_metrics = []
    if "active_dataset" not in st.session_state:
        st.session_state.active_dataset = None
    if "computed_metrics_df" not in st.session_state:
        st.session_state.computed_metrics_df = None

    # Meta API session state (for ultimate-dashboard pages)
    if "access_token" not in st.session_state:
        st.session_state.access_token = ""
    if "ad_account_id" not in st.session_state:
        st.session_state.ad_account_id = ""


def _get_v4_engine(page_name: str):
    """Return the appropriate engine for a V4 core page."""
    if page_name == "Dashboard":
        return st.session_state.metric_engine
    elif page_name == "Analytics":
        return st.session_state.analytics_engine
    elif page_name == "Alerts":
        return st.session_state.alert_engine
    elif page_name == "Export":
        return st.session_state.export_engine
    elif page_name == "App Settings":
        return st.session_state.metric_engine
    return None


def main() -> None:
    st.set_page_config(
        page_title="Meta Ads Commander v4 — Unified",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _init_session()

    state = StateManager()
    theme = state.get("theme", "dark")
    inject_theme_css(theme)

    current_page = Sidebar("main_sidebar", sections=_SECTIONS)

    # Route to the correct page
    route = _PAGE_ROUTER.get(current_page)
    if route is None:
        st.error(f"Page '{current_page}' not found in router.")
        return

    route_type, renderer = route

    if route_type == "v4":
        ec = st.session_state.entity_cascade
        df = st.session_state.df_raw
        engine = _get_v4_engine(current_page)
        renderer(state, ec, df, engine)
    elif route_type == "page":
        renderer.render()

    PageFooter("main_footer")

    # Toast messages
    toast_msg = state.get("toast_message")
    if toast_msg:
        severity = state.get("toast_severity", "info")
        icons = {"success": "✅", "error": "❌", "warning": "⚠️"}
        st.toast(toast_msg, icon=icons.get(severity, "ℹ️"))
        state.set("toast_message", None)


if __name__ == "__main__":
    main()
