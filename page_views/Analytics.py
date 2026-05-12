"""Analytics & Insights — 3 tabs: Trends & Distribution, Forecast, Anomalies & Cohorts."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core.entity_cascade import EntityCascade
from core.state_manager import StateManager
from engines.analytics_engine import AnalyticsEngine
from ui.components import (
    AnomalyChart, BarChart, ForecastChart, GaugeChart, Heatmap,
    LineChart, PageHeader, ScatterPlot, TabContainer,
)


def render(state: StateManager, entity_cascade: EntityCascade,
           df: pd.DataFrame, analytics: AnalyticsEngine | None = None):
    PageHeader("analytics_header", title="Analytics & Insights",
               subtitle="Deep dive into campaign analytics",
               breadcrumbs=["Home", "Analytics"])

    filtered = entity_cascade.apply(df)
    analytics = analytics or AnalyticsEngine()

    def _render_trends():
        daily = filtered.groupby("date_start").agg({
            "spend": "sum", "ctr": "mean", "cpc": "mean"
        }).reset_index()
        c1, c2 = st.columns(2)
        with c1:
            roas_col = ["spend"]
            if "roas" in filtered.columns:
                daily2 = filtered.groupby("date_start").agg({"spend": "sum", "roas": "mean"}).reset_index()
                LineChart("anal_spend_roas", daily2, y_cols=["spend", "roas"], title="Spend & ROAS")
            else:
                LineChart("anal_spend_roas", daily, y_cols=["spend"], title="Daily Spend")
        with c2:
            LineChart("anal_ctr_cpc", daily, y_cols=["ctr", "cpc"], title="CTR & CPC Trends")
        c3, c4 = st.columns(2)
        with c3:
            camp_spend = filtered.groupby("campaign_name")["spend"].sum().reset_index()
            BarChart("anal_camp_bar", camp_spend, x_col="campaign_name", y_cols=["spend"],
                     title="Campaign Spend Distribution")
        with c4:
            ScatterPlot("anal_cpc_ctr", filtered, x_col="cpc", y_col="ctr",
                        color_col="campaign_name", title="CPC vs CTR")

    def _render_forecast():
        daily = filtered.groupby("date_start").agg({"spend": "sum", "ctr": "mean"}).reset_index()
        spend_fc = analytics.compute_forecast(daily["spend"])
        ctr_fc = analytics.compute_forecast(daily["ctr"])
        c1, c2 = st.columns(2)
        with c1:
            ForecastChart("anal_fc_spend", daily, y_col="spend",
                          forecast=spend_fc["forecast"],
                          lower_bound=spend_fc["lower_bound"],
                          upper_bound=spend_fc["upper_bound"])
        with c2:
            ForecastChart("anal_fc_ctr", daily, y_col="ctr",
                          forecast=ctr_fc["forecast"],
                          lower_bound=ctr_fc["lower_bound"],
                          upper_bound=ctr_fc["upper_bound"])
        c3, c4 = st.columns(2)
        with c3:
            confidence = max(0, 100 - spend_fc["mape"])
            GaugeChart("anal_confidence", value=confidence, title="Forecast Confidence %")
        with c4:
            budget_eff = analytics.compute_budget_efficiency(filtered)
            st.markdown("#### Budget Efficiency")
            for k, v in budget_eff.items():
                label = k.replace("_", " ").title()
                st.markdown(f"**{label}:** {v:,.2f}" if isinstance(v, float) else f"**{label}:** {v}")

    def _render_anomalies():
        c1, c2 = st.columns(2)
        with c1:
            daily_spend = filtered.groupby("date_start")["spend"].sum().reset_index()
            anom_spend = analytics.detect_anomalies(daily_spend, "spend", method="zscore")
            AnomalyChart("anal_anom_spend", anom_spend, y_col="spend")
        with c2:
            daily_ctr = filtered.groupby("date_start")["ctr"].mean().reset_index()
            anom_ctr = analytics.detect_anomalies(daily_ctr, "ctr", method="iqr")
            AnomalyChart("anal_anom_ctr", anom_ctr, y_col="ctr")
        c3, c4 = st.columns(2)
        with c3:
            Heatmap("anal_heatmap", filtered, x_col="date_start", y_col="campaign_name",
                    z_col="spend", title="Spend Heatmap")
        with c4:
            cohort = analytics.compute_cohort_analysis(filtered)
            if not cohort.empty:
                st.markdown("#### Cohort Analysis")
                st.dataframe(cohort.head(10), use_container_width=True)
            else:
                st.info("Insufficient data for cohort analysis")

    TabContainer("analytics_tabs", [
        ("📈 Trends & Distribution", _render_trends),
        ("🔮 Forecast", _render_forecast),
        ("⚠️ Anomalies & Cohorts", _render_anomalies),
    ])
