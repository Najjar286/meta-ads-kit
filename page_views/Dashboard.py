"""Executive Dashboard — 8 KPIs, charts, health gauge, top performers, metric table."""
from __future__ import annotations

import pandas as pd

from core.entity_cascade import EntityCascade
from core.state_manager import StateManager
from engines.analytics_engine import AnalyticsEngine
from engines.metric_engine import MetricEngine
from ui.components import (
    CostAnalysisWidget, DateRangeFilter, HealthScoreGauge,
    KpiRow, LineChart, MetricSelector, MetricTable, PageHeader,
    PieChart, TopPerformerList, TrendIndicator,
)


def render(state: StateManager, entity_cascade: EntityCascade,
           df_raw: pd.DataFrame, metric_engine: MetricEngine | None = None):
    PageHeader("dash_header", title="Executive Dashboard",
               subtitle="Real-time campaign performance overview",
               breadcrumbs=["Home", "Dashboard"])

    DateRangeFilter("dash_date")

    filtered = entity_cascade.apply(df_raw)
    if metric_engine:
        filtered = metric_engine.compute(filtered)

    total_spend = float(filtered["spend"].sum()) if "spend" in filtered.columns else 0
    total_imp = int(filtered["impressions"].sum()) if "impressions" in filtered.columns else 0
    total_clicks = int(filtered["clicks"].sum()) if "clicks" in filtered.columns else 0
    total_conv = int(filtered["conversions"].sum()) if "conversions" in filtered.columns else 0
    avg_ctr = float(filtered["ctr"].mean()) if "ctr" in filtered.columns else 0
    avg_cpc = float(filtered["cpc"].mean()) if "cpc" in filtered.columns else 0
    avg_cpm = float(filtered["cpm"].mean()) if "cpm" in filtered.columns else 0
    avg_roas = float(filtered["roas"].mean()) if "roas" in filtered.columns else 0

    KpiRow("dash_kpis", [
        {"label": "Total Spend", "value": total_spend, "format": "cur", "color": "info"},
        {"label": "Impressions", "value": total_imp, "format": "num"},
        {"label": "Clicks", "value": total_clicks, "format": "num"},
        {"label": "Conversions", "value": total_conv, "format": "num", "color": "success"},
        {"label": "Avg CTR", "value": avg_ctr, "format": "pct"},
        {"label": "Avg CPC", "value": avg_cpc, "format": "cur"},
        {"label": "Avg CPM", "value": avg_cpm, "format": "cur"},
        {"label": "Avg ROAS", "value": avg_roas, "format": "dec", "color": "success"},
    ], columns=4)

    c1, c2 = __import__("streamlit").columns(2)
    with c1:
        daily = filtered.groupby("date_start").agg({"spend": "sum", "impressions": "sum"}).reset_index()
        LineChart("dash_spend_line", daily, y_cols=["spend", "impressions"],
                  title="Spend & Impressions Over Time")
    with c2:
        PieChart("dash_spend_pie", filtered, values_col="spend", title="Spend by Campaign")

    c3, c4, c5 = __import__("streamlit").columns(3)
    with c3:
        ad_health = 65.0
        if "ad_health_score" in filtered.columns:
            ad_health = float(filtered["ad_health_score"].mean())
        HealthScoreGauge("dash_health", score=ad_health, label="Ad Health")
    with c4:
        trend = AnalyticsEngine.compute_trend(filtered.groupby("date_start")["ctr"].mean())
        TrendIndicator("dash_trend", value=trend["pct_change"], label="CTR Trend")
    with c5:
        CostAnalysisWidget("dash_cost",
                            total_spend=total_spend,
                            total_budget=float(filtered["daily_budget"].sum()) if "daily_budget" in filtered.columns else 0,
                            avg_cpc=avg_cpc, avg_cpm=avg_cpm)

    c6, c7 = __import__("streamlit").columns(2)
    with c6:
        TopPerformerList("dash_top", filtered, metric="conversions", entity_col="ad_name")
    with c7:
        MetricTable("dash_table", filtered,
                    metrics=["campaign_name", "spend", "impressions", "clicks", "conversions", "ctr", "cpc"],
                    group_by="campaign_name", sort_by="spend")
