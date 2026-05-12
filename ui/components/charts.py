"""Chart components — Plotly-based: Line, Bar, Pie, Area, Scatter, Heatmap, Funnel, Gauge, Sparkline, Trend, Forecast, Anomaly."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.components.feedback import EmptyState


_THEME_OVERRIDES = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Segoe UI, sans-serif"},
}

_COLORS = ["#60CDFF", "#6CCB5F", "#C08AFF", "#FF8C42", "#FCE100",
           "#FF6F6F", "#4FC1E8", "#A0D568", "#ED5564", "#AC92EB"]


def _apply_theme(fig: go.Figure, height: int = 400) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=40, r=20, t=30, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Segoe UI, sans-serif", "size": 12, "color": "#A0A0A0"},
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.08)", zeroline=False,
                   linecolor="rgba(128,128,128,0.15)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.08)", zeroline=False,
                   linecolor="rgba(128,128,128,0.15)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11)),
        colorway=_COLORS,
    )
    return fig


def LineChart(key: str, df: pd.DataFrame, x_col: str = "date_start", y_cols: list[str] | None = None,
              group_by: str | None = None, title: str = "", height: int = 400,
              show_trend: bool = True, smooth: bool = True):
    if df is None or df.empty:
        EmptyState(key, "No data for chart"); return
    y_cols = y_cols or [c for c in ["spend", "impressions", "clicks", "ctr", "cpa"] if c in df.columns]
    if not y_cols:
        EmptyState(key, "No numeric columns"); return
    fig = go.Figure()
    for ci, y in enumerate(y_cols):
        if y not in df.columns:
            continue
        color = _COLORS[ci % len(_COLORS)]
        if group_by and group_by in df.columns:
            for gi, grp in enumerate(df[group_by].unique()):
                subset = df[df[group_by] == grp]
                fig.add_trace(go.Scatter(
                    x=subset[x_col] if x_col in subset.columns else subset.index,
                    y=subset[y], mode="lines",
                    name=f"{y} - {grp}",
                    line=dict(width=2.5, shape="spline" if smooth else "linear",
                              color=_COLORS[(ci + gi) % len(_COLORS)]),
                    hovertemplate=f"{y}: %{{y:.2f}}<br>%{{x}}<extra>{grp}</extra>",
                ))
        else:
            fig.add_trace(go.Scatter(
                x=df[x_col] if x_col in df.columns else df.index,
                y=df[y], mode="lines",
                name=y, line=dict(width=2.5, shape="spline" if smooth else "linear", color=color),
                hovertemplate=f"{y}: %{{y:.2f}}<br>%{{x}}<extra></extra>",
                fill="tonexty" if ci > 0 else None,
            ))
    fig = _apply_theme(fig, height)
    if title:
        fig.update_layout(title=dict(text=title, x=0.5, xanchor="center", font=dict(size=15)))
    st.plotly_chart(fig, use_container_width=True, key=key)


def BarChart(key: str, df: pd.DataFrame, x_col: str | None = None, y_cols: list[str] | None = None,
             group_by: str | None = None, title: str = "", height: int = 400, barmode: str = "group"):
    if df is None or df.empty:
        EmptyState(key, "No data for chart"); return
    x_col = x_col or next((c for c in ["campaign_name", "adset_name", "ad_name", "date_start"] if c in df.columns), None)
    y_cols = y_cols or [c for c in ["spend", "impressions", "clicks", "conversions"] if c in df.columns]
    if not y_cols or x_col is None:
        EmptyState(key, "Missing required columns"); return
    fig = px.bar(df, x=x_col, y=y_cols, color=group_by, barmode=barmode, title=title,
                 color_discrete_sequence=_COLORS)
    fig = _apply_theme(fig, height)
    fig.update_traces(marker_line_width=0, opacity=0.9)
    st.plotly_chart(fig, use_container_width=True, key=key)


def PieChart(key: str, df: pd.DataFrame, names_col: str | None = None, values_col: str = "spend",
             title: str = "", height: int = 400, max_slices: int = 10):
    if df is None or df.empty:
        EmptyState(key, "No data for chart"); return
    names_col = names_col or next((c for c in ["campaign_name", "adset_name", "objective"] if c in df.columns), None)
    if names_col is None or values_col not in df.columns:
        EmptyState(key, "Missing required columns"); return
    grouped = df.groupby(names_col)[values_col].sum().nlargest(max_slices).reset_index()
    fig = px.pie(grouped, names=names_col, values=values_col, title=title,
                 color_discrete_sequence=_COLORS, hole=0.4)
    fig.update_traces(textposition="inside", textinfo="percent+label",
                      marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=1)))
    fig = _apply_theme(fig, height)
    st.plotly_chart(fig, use_container_width=True, key=key)


def AreaChart(key: str, df: pd.DataFrame, x_col: str = "date_start", y_cols: list[str] | None = None,
              title: str = "", height: int = 400, stacked: bool = True):
    if df is None or df.empty:
        EmptyState(key, "No data for chart"); return
    y_cols = y_cols or [c for c in ["spend", "impressions", "clicks"] if c in df.columns]
    fig = px.area(df, x=x_col if x_col in df.columns else None, y=y_cols,
                  title=title, groupnorm="percent" if stacked else None,
                  color_discrete_sequence=_COLORS)
    fig = _apply_theme(fig, height)
    fig.update_traces(line=dict(width=1.5))
    st.plotly_chart(fig, use_container_width=True, key=key)


def ScatterPlot(key: str, df: pd.DataFrame, x_col: str = "spend", y_col: str = "conversions",
                color_col: str | None = None, size_col: str | None = None,
                title: str = "", height: int = 400):
    if df is None or df.empty:
        EmptyState(key, "No data for chart"); return
    if x_col not in df.columns or y_col not in df.columns:
        EmptyState(key, "Missing required columns"); return
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col,
                     title=title, trendline="ols",
                     trendline_color_override="rgba(255,111,111,0.4)",
                     color_discrete_sequence=_COLORS)
    fig = _apply_theme(fig, height)
    st.plotly_chart(fig, use_container_width=True, key=key)


def Heatmap(key: str, df: pd.DataFrame, x_col: str | None = None, y_col: str | None = None,
            z_col: str = "spend", title: str = "", height: int = 400):
    if df is None or df.empty:
        EmptyState(key, "No data for chart"); return
    x_col = x_col or "date_start"
    y_col = y_col or "campaign_name"
    if x_col not in df.columns or y_col not in df.columns or z_col not in df.columns:
        EmptyState(key, "Missing required columns"); return
    pivot = df.pivot_table(index=y_col, columns=x_col, values=z_col, aggfunc="sum").fillna(0)
    fig = px.imshow(pivot, title=title, color_continuous_scale="Blues", aspect="auto")
    fig = _apply_theme(fig, height)
    st.plotly_chart(fig, use_container_width=True, key=key)


def FunnelChart(key: str, stages: list[str] | None = None, values: list[float] | None = None,
                title: str = "", height: int = 400):
    stages = stages or ["Impressions", "Clicks", "Conversions"]
    values = values or [10000, 500, 50]
    fig = go.Figure(go.Funnel(
        y=stages, x=values,
        textposition="inside", textinfo="value+percent initial",
        marker=dict(color=_COLORS[:len(stages)]),
        connector=dict(line=dict(color="rgba(128,128,128,0.2)", width=1)),
    ))
    fig = _apply_theme(fig, height)
    if title:
        fig.update_layout(title=dict(text=title, x=0.5, xanchor="center"))
    st.plotly_chart(fig, use_container_width=True, key=key)


def GaugeChart(key: str, value: float, title: str = "", max_value: float = 100,
               height: int = 300, threshold_good: float = 70, threshold_warn: float = 40):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14}},
        gauge=dict(
            axis=dict(range=[0, max_value], tickwidth=1, tickcolor="rgba(128,128,128,0.3)"),
            bar=dict(color="#60CDFF"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0, threshold_warn], color="rgba(255,111,111,0.15)"),
                dict(range=[threshold_warn, threshold_good], color="rgba(252,225,0,0.15)"),
                dict(range=[threshold_good, max_value], color="rgba(108,203,95,0.15)"),
            ],
            threshold=dict(line=dict(color="#FF6F6F", width=2), thickness=0.75, value=value),
        ),
    ))
    fig = _apply_theme(fig, height)
    st.plotly_chart(fig, use_container_width=True, key=key)


def Sparkline(key: str, data: list | pd.Series, height: int = 50, color: str = "#60CDFF"):
    if data is None or (hasattr(data, '__len__') and len(data) == 0):
        return
    values = list(data) if not isinstance(data, list) else data
    fig = go.Figure(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=1.5, shape="spline"),
        fill="tozeroy", fillcolor=f"rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},0.1)",
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False, hovermode=False,
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def TrendIndicator(key: str, value: float, label: str = "", format: str = "pct"):
    if format == "pct":
        display = f"{value:.1f}%"
    elif format == "cur":
        display = f"${value:,.2f}"
    else:
        display = f"{value:.2f}"
    if value > 0:
        cls = "w11-badge-good"
        arrow = "▲"
    elif value < 0:
        cls = "w11-badge-bad"
        arrow = "▼"
    else:
        cls = "w11-badge-info"
        arrow = "◆"
    html = f'<span class="w11-badge {cls}">{arrow} {display}</span>'
    if label:
        html = f'<span style="color:var(--text-secondary);font-size:13px;margin-right:8px;">{label}</span>{html}'
    st.markdown(html, unsafe_allow_html=True)


def ForecastChart(key: str, df: pd.DataFrame, x_col: str = "date_start", y_col: str = "spend",
                  forecast: list | None = None, lower_bound: list | None = None,
                  upper_bound: list | None = None, periods: int = 7, height: int = 400):
    if df is None or df.empty:
        EmptyState(key, "No data for forecast"); return
    fig = go.Figure()
    if x_col in df.columns and y_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df[x_col], y=df[y_col], mode="lines",
            name="Actual", line=dict(color="#60CDFF", width=2.5),
        ))
    if forecast:
        last_date = pd.to_datetime(df[x_col].max()) if x_col in df.columns else pd.Timestamp.now()
        future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=len(forecast))
        fig.add_trace(go.Scatter(
            x=future_dates, y=forecast, mode="lines",
            name="Forecast", line=dict(color="#C08AFF", width=2, dash="dash"),
        ))
        if upper_bound and lower_bound:
            fig.add_trace(go.Scatter(
                x=list(future_dates) + list(future_dates[::-1]),
                y=list(upper_bound) + list(lower_bound[::-1]),
                fill="toself", fillcolor="rgba(192,138,255,0.1)",
                line=dict(color="rgba(0,0,0,0)"), name="Confidence",
                showlegend=False,
            ))
    fig = _apply_theme(fig, height)
    fig.update_layout(title=dict(text=f"Forecast: {y_col}", x=0.5, xanchor="center"))
    st.plotly_chart(fig, use_container_width=True, key=key)


def AnomalyChart(key: str, df: pd.DataFrame, x_col: str = "date_start", y_col: str = "ctr",
                 anomaly_col: str = "is_anomaly", height: int = 400):
    if df is None or df.empty:
        EmptyState(key, "No data for anomaly chart"); return
    if y_col not in df.columns:
        EmptyState(key, f"Column {y_col} not found"); return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col] if x_col in df.columns else df.index,
        y=df[y_col], mode="lines",
        name=y_col, line=dict(color="#60CDFF", width=2),
    ))
    if anomaly_col in df.columns:
        anomalies = df[df[anomaly_col]]
        if not anomalies.empty:
            fig.add_trace(go.Scatter(
                x=anomalies[x_col] if x_col in anomalies.columns else anomalies.index,
                y=anomalies[y_col], mode="markers",
                name="Anomaly", marker=dict(color="#FF6F6F", size=12, symbol="x"),
            ))
    fig = _apply_theme(fig, height)
    fig.update_layout(title=dict(text=f"Anomaly Detection: {y_col}", x=0.5, xanchor="center"))
    st.plotly_chart(fig, use_container_width=True, key=key)
