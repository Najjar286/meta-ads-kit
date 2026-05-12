"""Data Export — Format selection, scope, anonymization, column filter, preview, download."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core.entity_cascade import EntityCascade
from core.state_manager import StateManager
from engines.export_engine import ExportEngine
from ui.components import (
    ExportPreview, MultiSelectFilter, PageHeader, ToggleGroup,
)


def render(state: StateManager, entity_cascade: EntityCascade,
           df: pd.DataFrame, export_engine: ExportEngine | None = None):
    PageHeader("export_header", title="Data Export",
               subtitle="Export campaign data in multiple formats",
               breadcrumbs=["Home", "Export"])

    export_engine = export_engine or ExportEngine()

    formats = export_engine.get_formats()
    fmt = ToggleGroup("export_format", "Export Format",
                      options=[f.upper() for f in formats])
    if fmt:
        fmt = fmt.lower()
    else:
        fmt = "csv"

    c1, c2 = st.columns(2)
    with c1:
        scope = ToggleGroup("export_scope", "Scope", options=["Filtered", "All"])
    with c2:
        anonymize = st.checkbox("Anonymize data", value=False, key="export_anonymize")

    if scope == "Filtered":
        export_df = entity_cascade.apply(df)
    else:
        export_df = df.copy()

    all_cols = export_df.columns.tolist()
    selected_cols = MultiSelectFilter("export_cols", "Select Columns", all_cols, default=all_cols)
    if selected_cols:
        export_df = export_df[selected_cols]

    if anonymize:
        export_df = ExportEngine.anonymize(export_df)

    ExportPreview("export_preview", export_df, format=fmt)

    data = export_engine.export(export_df, fmt)
    ext = ExportEngine.get_extension(fmt)
    mime = ExportEngine.get_mime_type(fmt)
    st.download_button(
        label=f"📥 Download {fmt.upper()} ({len(export_df):,} rows)",
        data=data,
        file_name=f"meta_ads_export{ext}",
        mime=mime,
        key="download_btn",
        type="primary",
        use_container_width=True,
    )
