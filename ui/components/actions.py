"""Action components: ActionButton, BulkActionBar, ConfirmDialog, ExportButton, RefreshButton."""
from __future__ import annotations

from typing import Any, Callable

import streamlit as st

from core.state_manager import StateManager


def ActionButton(key: str, label: str, on_click: Callable | None = None,
                 icon: str = "", variant: str = "primary", disabled: bool = False,
                 tooltip: str = ""):
    full_label = f"{icon} {label}" if icon else label
    kwargs = dict(key=key, disabled=disabled, help=tooltip)
    if variant == "primary":
        clicked = st.button(full_label, type="primary", **kwargs)
    else:
        clicked = st.button(full_label, **kwargs)
    if clicked and on_click:
        on_click()
    return clicked


def BulkActionBar(key: str, actions: list[dict[str, Any]], selected_count: int = 0):
    if selected_count == 0:
        return
    container = st.container(border=True)
    with container:
        cols = st.columns([1] + [1] * len(actions))
        with cols[0]:
            st.markdown(
                f'<span style="font-size:13px;color:var(--text-secondary);font-weight:500;">'
                f'{selected_count} selected</span>',
                unsafe_allow_html=True,
            )
        for i, action in enumerate(actions):
            with cols[i + 1]:
                if st.button(action.get("label", f"Action {i}"),
                             key=f"{key}_bulk_{i}",
                             type=action.get("variant", "secondary"),
                             disabled=action.get("disabled", False)):
                    cb = action.get("on_click")
                    if cb:
                        cb()


def ConfirmDialog(key: str, title: str = "Confirm", message: str = "Are you sure?",
                  on_confirm: Callable | None = None, on_cancel: Callable | None = None):
    dialog_key = f"{key}_open"
    if dialog_key not in st.session_state:
        st.session_state[dialog_key] = False
    if not st.session_state[dialog_key]:
        return
    with st.popover(title, use_container_width=True):
        st.markdown(f'<p style="margin:0 0 12px 0;">{message}</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Cancel", key=f"{key}_cancel", type="secondary"):
                st.session_state[dialog_key] = False
                if on_cancel:
                    on_cancel()
                st.rerun()
        with c2:
            if st.button("Confirm", key=f"{key}_confirm", type="primary"):
                st.session_state[dialog_key] = False
                if on_confirm:
                    on_confirm()
                st.rerun()


def ExportButton(key: str, on_export: Callable | None = None,
                 formats: list[str] | None = None):
    formats = formats or ["csv", "xlsx", "json"]
    state = StateManager()
    current = state.get("export_format", "xlsx")
    col1, col2 = st.columns([2, 1])
    with col1:
        fmt = st.selectbox("Format", formats,
                           index=formats.index(current) if current in formats else 0,
                           key=f"{key}_format", label_visibility="collapsed")
        if fmt != current:
            state.set("export_format", fmt, source="export_button")
    with col2:
        if st.button("📥 Export", key=key, type="primary"):
            if on_export:
                on_export(fmt)


def RefreshButton(key: str, on_refresh: Callable | None = None, interval: int = 0,
                  label: str = "Refresh"):
    if st.button(f"🔄 {label}", key=key):
        if on_refresh:
            on_refresh()
