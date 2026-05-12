"""Feedback components: EmptyState, LoadingSpinner, ErrorBoundary, SuccessMessage, WarningBanner."""
from __future__ import annotations

import streamlit as st


def EmptyState(key: str, message: str = "No data available", icon: str = "📭"):
    st.markdown(
        f'<div class="w11-empty-state">'
        f'<div class="w11-empty-state-icon">{icon}</div>'
        f'<div class="w11-empty-state-text">{message}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def LoadingSpinner(key: str, message: str = "Loading..."):
    with st.spinner(message):
        placeholder = st.empty()
        placeholder.markdown(
            f'<div style="text-align:center;padding:24px;">'
            f'<p style="color:var(--text-tertiary);font-size:14px;">{message}</p></div>',
            unsafe_allow_html=True,
        )
        return placeholder


def ErrorBoundary(key: str, message: str = "An error occurred", details: str = ""):
    html = '<div class="w11-error-boundary">'
    html += f'<p style="margin:0 0 4px 0;font-weight:600;color:var(--danger);">{message}</p>'
    if details:
        html += f'<p style="margin:0;font-size:13px;color:var(--text-secondary);">{details}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def SuccessMessage(key: str, message: str):
    st.markdown(
        f'<div style="padding:12px 16px;border-radius:var(--radius);'
        f'background:rgba(108,203,95,0.1);border:1px solid rgba(108,203,95,0.3);">'
        f'<p style="margin:0;color:var(--success);font-weight:500;">{message}</p></div>',
        unsafe_allow_html=True,
    )


def WarningBanner(key: str, message: str):
    st.markdown(
        f'<div style="padding:12px 16px;border-radius:var(--radius);'
        f'background:rgba(252,225,0,0.1);border:1px solid rgba(252,225,0,0.3);">'
        f'<p style="margin:0;color:var(--warning);font-weight:500;">{message}</p></div>',
        unsafe_allow_html=True,
    )
