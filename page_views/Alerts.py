"""Alerts & Monitoring — 2 tabs: Rules (browse/toggle 25 rules), Triggers (run evaluation, view alerts)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core.entity_cascade import EntityCascade
from core.state_manager import StateManager
from engines.alert_engine import AlertEngine
from ui.components import (
    ActionButton, EmptyState, PageHeader, SuccessMessage, TabContainer,
)


def render(state: StateManager, entity_cascade: EntityCascade,
           df: pd.DataFrame, alert_engine: AlertEngine | None = None):
    PageHeader("alerts_header", title="Alerts & Monitoring",
               subtitle="Manage alert rules and view triggered alerts",
               breadcrumbs=["Home", "Alerts"])

    alert_engine = alert_engine or AlertEngine()

    def _render_rules():
        rules = alert_engine.get_rules()
        if not rules:
            EmptyState("no_rules", "No alert rules configured")
            return
        categories = sorted(set(r["category"] for r in rules))
        for cat in categories:
            st.markdown(
                f'<p style="font-size:14px;font-weight:600;color:var(--accent-primary);'
                f'margin:16px 0 8px 0;text-transform:uppercase;letter-spacing:1px;">{cat}</p>',
                unsafe_allow_html=True,
            )
            cat_rules = [r for r in rules if r["category"] == cat]
            for rule in cat_rules:
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                with c1:
                    st.markdown(
                        f'<span style="font-weight:500;">{rule["name"]}</span>'
                        f'<br><span style="font-size:12px;color:var(--text-tertiary);">{rule["description"]}</span>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    sev_colors = {"critical": "w11-badge-bad", "warning": "w11-badge-warn", "info": "w11-badge-info"}
                    cls = sev_colors.get(rule["severity"], "w11-badge-info")
                    st.markdown(f'<span class="w11-badge {cls}">{rule["severity"]}</span>', unsafe_allow_html=True)
                with c3:
                    st.markdown(
                        f'<span style="font-size:13px;color:var(--text-secondary);">'
                        f'{rule["metric"]} {rule["operator"]} {rule["threshold"]}</span>',
                        unsafe_allow_html=True,
                    )
                with c4:
                    enabled = st.toggle("", value=rule["enabled"],
                                         key=f"rule_{rule['rule_id']}",
                                         label_visibility="collapsed")
                    if enabled != rule["enabled"]:
                        alert_engine.toggle_rule(rule["rule_id"], enabled)

    def _render_triggers():
        filtered = entity_cascade.apply(df)

        if ActionButton("run_eval", "Run Evaluation", icon="🔍", variant="primary"):
            with st.spinner("Evaluating alert rules..."):
                results = alert_engine.evaluate(filtered)
            if results:
                st.warning(f"⚠️ {len(results)} alerts triggered!")
            else:
                SuccessMessage("no_alerts", "No alerts triggered — all metrics within thresholds")

        active = alert_engine.get_active_alerts()
        if not active:
            EmptyState("no_active", "No active alerts", icon="🎉")
            return
        st.markdown(
            f'<p style="font-size:14px;font-weight:600;color:var(--text-primary);margin:16px 0 8px 0;">'
            f'Active Alerts ({len(active)})</p>',
            unsafe_allow_html=True,
        )
        for alert in active:
            sev_colors = {"critical": "w11-badge-bad", "warning": "w11-badge-warn", "info": "w11-badge-info"}
            cls = sev_colors.get(alert.severity, "w11-badge-info")
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.markdown(
                        f'<span class="w11-badge {cls}">{alert.severity}</span> '
                        f'<strong>{alert.rule_name}</strong>'
                        f'<br><span style="font-size:13px;color:var(--text-secondary);">'
                        f'{alert.message}</span>'
                        f'<br><span style="font-size:12px;color:var(--text-tertiary);">'
                        f'Entity: {alert.entity_name}</span>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f'<span style="font-size:13px;color:var(--text-secondary);">'
                        f'Value: {alert.metric_value:.2f}</span>',
                        unsafe_allow_html=True,
                    )
                with c3:
                    if st.button("Acknowledge", key=f"ack_{alert.alert_id}", type="secondary"):
                        alert_engine.acknowledge(alert.alert_id)
                        SuccessMessage(f"acked_{alert.alert_id}", "Alert acknowledged")
                        st.rerun()

    TabContainer("alerts_tabs", [
        ("📋 Rules", _render_rules),
        ("🔔 Triggers", _render_triggers),
    ])
