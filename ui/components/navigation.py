"""Navigation components: EntityTree, EntityBreadcrumb, EntitySelector, AccountSwitcher."""
from __future__ import annotations

import streamlit as st

from core.state_manager import StateManager
from core.entity_cascade import EntityCascade


def EntityTree(key: str, entity_cascade: EntityCascade | None = None):
    state = StateManager()
    html = '<div style="padding:8px 0;">'
    html += '<p style="font-size:11px;color:var(--text-tertiary);margin:0 0 8px 0;text-transform:uppercase;letter-spacing:1px;font-weight:600;">ENTITY TREE</p>'
    levels = [
        ("accounts", "account", "selected_account", "account_id", "account_name"),
        ("campaigns", "campaign", "selected_campaign", "campaign_id", "campaign_name"),
        ("adsets", "adset", "selected_adset", "adset_id", "adset_name"),
        ("ads", "ad", "selected_ad", "ad_id", "ad_name"),
    ]
    for store_key, label, state_key, id_key, name_key in levels:
        items = entity_cascade._entity_tree.get(store_key, []) if entity_cascade else []
        count = len(items)
        selected = state.get(state_key)
        color = "var(--accent-primary)" if selected else "var(--text-secondary)"
        icon = "▸" if not selected else "▾"
        html += (f'<p style="font-size:13px;margin:4px 0;color:{color};'
                 f'padding:4px 8px;border-radius:var(--radius-sm);'
                 f'transition:background var(--transition-fast);">'
                 f'{icon} {label.title()} <span style="color:var(--text-tertiary);">({count})</span></p>')
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
    return state.get("_current_page")


def EntityBreadcrumb(key: str, entity_cascade: EntityCascade | None = None):
    state = StateManager()
    crumbs = []
    for state_key, label in [("selected_account", "Account"), ("selected_campaign", "Campaign"),
                               ("selected_adset", "AdSet"), ("selected_ad", "Ad")]:
        val = state.get(state_key)
        if val and val != "All":
            name = entity_cascade.get_entity_name(val, label.lower()) if entity_cascade else val
            crumbs.append(name)
    if crumbs:
        trail = ' <span style="color:var(--text-tertiary);margin:0 6px;">›</span> '.join(
            f'<span style="color:var(--text-secondary);">{c}</span>' for c in crumbs
        )
        st.markdown(
            f'<p style="font-size:12px;color:var(--text-tertiary);margin:0 0 8px 0;">{trail}</p>',
            unsafe_allow_html=True,
        )


def EntitySelector(key: str, entity_cascade: EntityCascade | None = None, level: str = "account"):
    state = StateManager()
    store_key = f"{level}s"
    state_key = f"selected_{level}"
    current = state.get(state_key, "All")
    items = entity_cascade._entity_tree.get(store_key, []) if entity_cascade else []
    id_key = f"{level}_id"
    name_key = f"{level}_name"
    options = ["All"] + [item.get(name_key, item.get(id_key, "?")) for item in items]
    selected = st.selectbox(
        f"Select {level.title()}",
        options=options,
        index=options.index(current) if current in options else 0,
        key=f"{key}_{state_key}",
    )
    if selected != current:
        new_val = None if selected == "All" else next(
            (item.get(id_key) for item in items if item.get(name_key) == selected), selected
        )
        state.set(state_key, new_val, source="entity_selector")


def AccountSwitcher(key: str, entity_cascade: EntityCascade | None = None):
    state = StateManager()
    items = entity_cascade._entity_tree.get("accounts", []) if entity_cascade else []
    current = state.get("selected_account", "All")
    options = ["All Accounts"] + [a.get("account_name", a.get("account_id", "?")) for a in items]
    idx = 0
    if current:
        display = next((a.get("account_name") for a in items if a.get("account_id") == current), current)
        if display in options:
            idx = options.index(display)
    selected = st.selectbox("Account", options=options, index=idx, key=f"{key}_acct_switch",
                            label_visibility="collapsed")
    if selected == "All Accounts":
        if current is not None:
            state.set("selected_account", None, source="account_switcher")
    elif selected != current:
        new_id = next((a["account_id"] for a in items if a.get("account_name") == selected), None)
        if new_id:
            state.set("selected_account", new_id, source="account_switcher")
