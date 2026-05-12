"""Data display components: KpiCard, KpiRow, MetricTable, DataTable, StatCard, ComparisonTable,
TopPerformerList, WorstPerformerList, HealthScoreGauge, CostAnalysisWidget, ExportPreview."""
from __future__ import annotations

from typing import Any, Callable

import pandas as pd
import streamlit as st

from ui.components.feedback import EmptyState


def KpiCard(key: str, label: str, value: str | float | int, delta: float | None = None,
            delta_direction: str = "up", format: str = "num", tooltip: str = "",
            color: str = "default", loading: bool = False, error: str = ""):
    if loading:
        st.markdown(
            f'<div class="genius-kpi">'
            f'<div class="w11-card-header">{label}</div>'
            f'<div class="w11-skeleton" style="height:32px;width:60%;margin-top:8px;"></div></div>',
            unsafe_allow_html=True,
        )
        return
    if error:
        st.markdown(f'<div class="w11-error-boundary">{error}</div>', unsafe_allow_html=True)
        return
    formatted = value
    if format == "cur":
        formatted = f"${value:,.2f}" if isinstance(value, (int, float)) else value
    elif format == "pct":
        formatted = f"{value:.2f}%" if isinstance(value, (int, float)) else value
    elif format == "dec":
        formatted = f"{value:.2f}" if isinstance(value, (int, float)) else value
    elif format == "num" and isinstance(value, (int, float)):
        formatted = f"{value:,.0f}" if value >= 1000 else f"{value}"
    delta_html = ""
    if delta is not None:
        cls = "w11-card-delta-positive" if delta > 0 else "w11-card-delta-negative" if delta < 0 else "w11-card-delta-neutral"
        arrow = "▲" if delta > 0 else "▼" if delta < 0 else "◆"
        delta_html = f'<div style="margin-top:6px;"><span class="{cls}">{arrow} {abs(delta):.1f}%</span></div>'
    accent_colors = {
        "success": "var(--success)", "danger": "var(--danger)",
        "warning": "var(--warning)", "info": "var(--info)",
    }
    accent = accent_colors.get(color, "var(--accent-primary)")
    st.markdown(
        f'<div class="genius-kpi" title="{tooltip}" style="border-top:3px solid {accent};">'
        f'<div class="w11-card-header">{label}</div>'
        f'<div class="w11-card-value">{formatted}</div>'
        f'{delta_html}</div>',
        unsafe_allow_html=True,
    )


def KpiRow(key: str, metrics: list[dict[str, Any]], columns: int = 4):
    cols = st.columns(min(columns, max(len(metrics), 1)))
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            KpiCard(f"{key}_{i}", **metric)


def MetricTable(key: str, df: pd.DataFrame, metrics: list[str] | None = None,
                group_by: str | None = None, sort_by: str | None = None,
                sort_asc: bool = False, page_size: int = 25, max_rows: int = 1000,
                show_comparison: bool = False, column_config: dict | None = None):
    if df is None or df.empty:
        EmptyState(key, "No data available for table")
        return
    display = df.head(max_rows).copy()
    if group_by and group_by in display.columns:
        agg = {}
        if metrics:
            for m in metrics:
                if m in display.columns:
                    agg[m] = "mean" if display[m].dtype in ("float64", "int64") else "first"
        if agg:
            display = display.groupby(group_by).agg(agg).reset_index()
    if sort_by and sort_by in display.columns:
        display = display.sort_values(sort_by, ascending=sort_asc)
    if metrics:
        cols = list(set([group_by] + metrics) if group_by else metrics)
        cols = [c for c in cols if c in display.columns]
        if cols:
            display = display[cols]
    st.dataframe(display, use_container_width=True, height=min(400, 35 * page_size),
                 column_config=column_config)


def DataTable(key: str, df: pd.DataFrame, page_size: int = 50, max_rows: int = 5000):
    if df is None or df.empty:
        EmptyState(key, "No data to display")
        return
    display = df.head(max_rows).reset_index(drop=True)
    total = len(df)
    total_pages = max(1, (total - 1) // page_size + 1)
    state_key = f"{key}_page"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0
    page = st.session_state[state_key]
    start = page * page_size
    end = min(start + page_size, total)
    st.dataframe(display.iloc[start:end], use_container_width=True)
    if total > page_size:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("◀ Prev", key=f"{key}_prev", disabled=page == 0):
                st.session_state[state_key] = max(0, page - 1)
                st.rerun()
        with c2:
            st.markdown(
                f'<p style="text-align:center;color:var(--text-tertiary);font-size:13px;">'
                f'Page {page + 1} of {total_pages} ({total:,} rows)</p>',
                unsafe_allow_html=True,
            )
        with c3:
            if st.button("Next ▶", key=f"{key}_next", disabled=page >= total_pages - 1):
                st.session_state[state_key] = min(total_pages - 1, page + 1)
                st.rerun()


def StatCard(key: str, label: str, value: str | float, tooltip: str = ""):
    st.markdown(
        f'<div class="w11-card" title="{tooltip}">'
        f'<div class="w11-card-header">{label}</div>'
        f'<div class="w11-card-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def ComparisonTable(key: str, df: pd.DataFrame, current_period_col: str = "current",
                    prev_period_col: str = "previous", metric_cols: list[str] | None = None):
    if df is None or df.empty:
        EmptyState(key, "No comparison data")
        return
    st.dataframe(df, use_container_width=True)


def TopPerformerList(key: str, df: pd.DataFrame, metric: str, top_n: int = 5,
                     entity_col: str = "ad_name", ascending: bool = False):
    if df is None or df.empty or metric not in df.columns or entity_col not in df.columns:
        EmptyState(key, "No performer data")
        return
    sorted_df = df.sort_values(metric, ascending=ascending).head(top_n)
    html = '<div style="padding:4px 0;">'
    for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
        val = row[metric]
        name = row[entity_col]
        badge_cls = "w11-badge-good" if not ascending and i <= 2 else "w11-badge-bad" if ascending and i <= 2 else "w11-badge-info"
        fmt_val = f"${val:,.2f}" if "spend" in metric or "cost" in metric or "cpc" in metric else f"{val:.2f}"
        html += (f'<div style="display:flex;align-items:center;justify-content:space-between;'
                 f'padding:8px 12px;margin:4px 0;border-radius:var(--radius-sm);'
                 f'background:var(--bg-glass);border:1px solid var(--glass-border);">'
                 f'<span style="color:var(--text-secondary);font-size:13px;">'
                 f'<strong style="color:var(--text-primary);margin-right:8px;">#{i}</strong>{name}</span>'
                 f'<span class="w11-badge {badge_cls}">{fmt_val}</span></div>')
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def WorstPerformerList(key: str, df: pd.DataFrame, metric: str, top_n: int = 5,
                       entity_col: str = "ad_name"):
    TopPerformerList(key, df, metric, top_n, entity_col, ascending=True)


def HealthScoreGauge(key: str, score: float, label: str = "Health Score", max_score: float = 100):
    pct = min(score / max_score * 100, 100)
    color = "var(--success)" if pct >= 70 else "var(--warning)" if pct >= 40 else "var(--danger)"
    circumference = 2 * 3.14159 * 45
    offset = circumference * (1 - pct / 100)
    svg = f'''<div style="text-align:center;padding:16px;">
    <svg width="140" height="140" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="var(--bg-tertiary)" stroke-width="8"/>
        <circle cx="50" cy="50" r="45" fill="none" stroke="{color}" stroke-width="8"
                stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                stroke-linecap="round" transform="rotate(-90 50 50)"
                style="transition: stroke-dashoffset 0.8s ease-out;"/>
        <text x="50" y="45" text-anchor="middle" font-size="22" font-weight="700"
              fill="var(--text-primary)">{score:.0f}</text>
        <text x="50" y="62" text-anchor="middle" font-size="10"
              fill="var(--text-tertiary)">{label}</text>
    </svg></div>'''
    st.markdown(svg, unsafe_allow_html=True)


def CostAnalysisWidget(key: str, total_spend: float, total_budget: float,
                        avg_cpc: float, avg_cpm: float):
    KpiRow(key, [
        {"label": "Total Spend", "value": total_spend, "format": "cur"},
        {"label": "Total Budget", "value": total_budget, "format": "cur"},
        {"label": "Avg CPC", "value": avg_cpc, "format": "cur"},
        {"label": "Avg CPM", "value": avg_cpm, "format": "cur"},
    ])


def ExportPreview(key: str, df: pd.DataFrame, format: str = "csv"):
    if df is None or df.empty:
        EmptyState(key, "No data to preview")
        return
    with st.expander(f"Preview ({format.upper()}) — {len(df):,} rows", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown(
            f'<p style="color:var(--text-tertiary);font-size:12px;margin-top:8px;">'
            f'Showing first 10 of {len(df):,} rows</p>',
            unsafe_allow_html=True,
        )
