"""Layout components: AppShell, Sidebar, PageHeader, ContentCard, GridLayout, TabContainer, PageFooter."""
from __future__ import annotations

from typing import Callable

import streamlit as st

from core.state_manager import StateManager


def AppShell(key: str, title: str = "Meta Ads Commander v4", sidebar_content: Callable | None = None):
    st.set_page_config(
        page_title=title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def Sidebar(
    key: str,
    pages: list[tuple[str, str]] | None = None,
    sections: dict[str, list[tuple[str, str]]] | None = None,
) -> str | None:
    """Sidebar navigation. Supports flat ``pages`` list or sectioned ``sections`` dict.

    When *sections* is provided the sidebar renders collapsible section headers
    with page buttons underneath.  Only one page is active at a time.
    """
    state = StateManager()
    with st.sidebar:
        st.markdown(
            '<div style="padding:16px 0;">'
            '<h2 style="margin:0;font-size:22px;font-weight:700;'
            'background:linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
            'Meta Ads Commander</h2>'
            '<p style="color:var(--text-tertiary);font-size:12px;margin:4px 0 0 0;'
            'letter-spacing:1px;">v4.0 GENIUS — Unified</p></div>',
            unsafe_allow_html=True,
        )
        st.divider()

        current_page = state.get("_current_page", "Dashboard")

        if sections:
            # Build flat list for icon lookup
            icons: dict[str, str] = {}
            for sec_pages in sections.values():
                for name, icon in sec_pages:
                    icons[name] = icon

            for section_name, sec_pages in sections.items():
                page_names = [p[0] for p in sec_pages]
                is_active = current_page in page_names
                with st.expander(f"**{section_name}**", expanded=is_active):
                    for pname in page_names:
                        icon = icons.get(pname, "")
                        active = pname == current_page
                        btn_type = "primary" if active else "secondary"
                        if st.button(
                            f"{icon}  {pname}",
                            key=f"{key}_{pname}",
                            use_container_width=True,
                            type=btn_type,
                        ):
                            if not active:
                                state.set("_current_page", pname)
                                st.rerun()

        elif pages:
            icons = {p[0]: p[1] for p in pages}
            page_names = [p[0] for p in pages]
            selected = st.radio(
                "Navigation",
                page_names,
                index=page_names.index(current_page) if current_page in page_names else 0,
                key=f"{key}_nav",
                label_visibility="collapsed",
                format_func=lambda x: f"{icons.get(x, '')} {x}" if icons.get(x) else x,
            )
            if selected != current_page:
                state.set("_current_page", selected)

        st.divider()
        theme = state.get("theme", "dark")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("☀️ Light" if theme == "dark" else "🌙 Dark",
                         key=f"{key}_theme", use_container_width=True):
                state.set("theme", "light" if theme == "dark" else "dark")
                st.rerun()
        with col2:
            lang = state.get("language", "en")
            if st.button("عربي" if lang == "en" else "EN",
                         key=f"{key}_lang", use_container_width=True):
                state.set("language", "ar" if lang == "en" else "en")
                st.rerun()
        return state.get("_current_page", "Dashboard")
    return None


def PageHeader(key: str, title: str, subtitle: str = "", breadcrumbs: list[str] | None = None):
    html = '<div style="margin-bottom:20px;">'
    if breadcrumbs:
        crumbs = ' <span style="color:var(--text-tertiary);margin:0 4px;">›</span> '.join(
            f'<span style="color:var(--text-secondary);">{c}</span>' for c in breadcrumbs
        )
        html += f'<p style="font-size:12px;color:var(--text-tertiary);margin:0 0 6px 0;">{crumbs}</p>'
    html += f'<h1 style="margin:0;font-size:28px;font-weight:700;color:var(--text-primary);">{title}</h1>'
    if subtitle:
        html += f'<p style="margin:6px 0 0 0;color:var(--text-secondary);font-size:14px;">{subtitle}</p>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def ContentCard(key: str, title: str | None = None, children: Callable | None = None, height: int | None = None):
    style = f"min-height:{height}px;" if height else ""
    with st.container(border=True):
        if title:
            st.markdown(
                f'<p style="font-size:14px;font-weight:600;color:var(--text-secondary);'
                f'margin:0 0 12px 0;text-transform:uppercase;letter-spacing:0.5px;">{title}</p>',
                unsafe_allow_html=True,
            )
        if children:
            children()


def GridLayout(key: str, columns: int = 2, gap: str = "16px"):
    return st.columns(columns, gap=gap)


def TabContainer(key: str, tabs: list[tuple[str, Callable]], default_index: int = 0):
    tab_labels = [t[0] for t in tabs]
    tab_funcs = [t[1] for t in tabs]
    selected_tabs = st.tabs(tab_labels)
    for i, tab in enumerate(selected_tabs):
        with tab:
            if i < len(tab_funcs):
                tab_funcs[i]()


def PageFooter(key: str, version: str = "4.0.0"):
    st.divider()
    st.markdown(
        f'<div style="text-align:center;padding:16px 0;color:var(--text-tertiary);font-size:12px;">'
        f'Meta Ads Commander v{version} — Genius Edition &bull; '
        f'Built with Streamlit &bull; '
        f'<a href="https://github.com/amrelnagar286/meta-ads-kit" '
        f'style="color:var(--text-tertiary);text-decoration:none;">GitHub</a>'
        f'</div>',
        unsafe_allow_html=True,
    )
