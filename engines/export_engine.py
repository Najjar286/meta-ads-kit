"""Export engine: Strategy pattern with 6 formats, anonymization, templates."""
from __future__ import annotations

import hashlib
import io
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class ExportStrategy(ABC):
    @abstractmethod
    def export(self, df: pd.DataFrame, options: dict | None = None) -> bytes:
        ...


class CsvStrategy(ExportStrategy):
    def export(self, df: pd.DataFrame, options: dict | None = None) -> bytes:
        opts = options or {}
        encoding = opts.get("encoding", "utf-8")
        sep = opts.get("separator", ",")
        return df.to_csv(index=False, encoding=encoding, sep=sep).encode(encoding)


class XlsxStrategy(ExportStrategy):
    def export(self, df: pd.DataFrame, options: dict | None = None) -> bytes:
        opts = options or {}
        sheet_name = opts.get("sheet_name", "Data")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]
            for col_idx, col in enumerate(df.columns, 1):
                max_len = max(len(str(col)), df[col].astype(str).str.len().max())
                ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_len + 2, 50)
        return buf.getvalue()


class JsonStrategy(ExportStrategy):
    def export(self, df: pd.DataFrame, options: dict | None = None) -> bytes:
        opts = options or {}
        orient = opts.get("orient", "records")
        date_format = opts.get("date_format", "iso")
        return df.to_json(orient=orient, date_format=date_format, indent=2).encode("utf-8")


class PowerBiAdStrategy(ExportStrategy):
    def export(self, df: pd.DataFrame, options: dict | None = None) -> bytes:
        cols = [c for c in ["ad_id", "ad_name", "campaign_name", "adset_name",
                            "spend", "impressions", "clicks", "conversions",
                            "ctr", "cpc", "cpm", "cost_per_conv", "date_start"] if c in df.columns]
        return df[cols].to_csv(index=False).encode("utf-8") if cols else b""


class PowerBiAdsetStrategy(ExportStrategy):
    def export(self, df: pd.DataFrame, options: dict | None = None) -> bytes:
        group_cols = [c for c in ["adset_id", "adset_name", "campaign_name"] if c in df.columns]
        agg_cols = {"spend": "sum", "impressions": "sum", "clicks": "sum", "conversions": "sum"}
        agg_cols = {k: v for k, v in agg_cols.items() if k in df.columns}
        if group_cols and agg_cols:
            result = df.groupby(group_cols).agg(agg_cols).reset_index()
            return result.to_csv(index=False).encode("utf-8")
        return b""


class PowerBiCampaignStrategy(ExportStrategy):
    def export(self, df: pd.DataFrame, options: dict | None = None) -> bytes:
        group_cols = [c for c in ["campaign_id", "campaign_name"] if c in df.columns]
        agg_cols = {"spend": "sum", "impressions": "sum", "clicks": "sum", "conversions": "sum"}
        agg_cols = {k: v for k, v in agg_cols.items() if k in df.columns}
        if group_cols and agg_cols:
            result = df.groupby(group_cols).agg(agg_cols).reset_index()
            return result.to_csv(index=False).encode("utf-8")
        return b""


_STRATEGIES: dict[str, ExportStrategy] = {
    "csv": CsvStrategy(),
    "xlsx": XlsxStrategy(),
    "json": JsonStrategy(),
    "powerbi_ad": PowerBiAdStrategy(),
    "powerbi_adset": PowerBiAdsetStrategy(),
    "powerbi_campaign": PowerBiCampaignStrategy(),
}


class ExportEngine:
    """Dispatches export to appropriate strategy, supports anonymization."""

    def __init__(self, template_dir: str = "config/templates") -> None:
        self._template_dir = Path(template_dir)

    def export(self, df: pd.DataFrame, fmt: str = "xlsx", options: dict | None = None) -> bytes:
        strategy = _STRATEGIES.get(fmt)
        if not strategy:
            strategy = _STRATEGIES["csv"]
        return strategy.export(df, options)

    @staticmethod
    def anonymize(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
        result = df.copy()
        target_cols = columns or [c for c in result.columns if c.endswith("_name") or c.endswith("_id")]
        for col in target_cols:
            if col not in result.columns:
                continue
            if col.endswith("_name"):
                result[col] = result[col].apply(
                    lambda x: f"Entity_{hashlib.md5(str(x).encode()).hexdigest()[:8]}")
            elif col.endswith("_id"):
                result[col] = result[col].apply(
                    lambda x: f"xxx_{hashlib.md5(str(x).encode()).hexdigest()[:8]}")
        return result

    def export_with_template(self, df: pd.DataFrame, template_name: str,
                             fmt: str = "xlsx") -> bytes:
        template_path = self._template_dir / f"{template_name}.json"
        if template_path.exists():
            with open(template_path) as f:
                config = json.load(f)
            cols = config.get("columns", [])
            if cols:
                available = [c for c in cols if c in df.columns]
                df = df[available]
        return self.export(df, fmt)

    @staticmethod
    def get_formats() -> list[str]:
        return list(_STRATEGIES.keys())

    @staticmethod
    def get_mime_type(fmt: str) -> str:
        mime_map = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json",
            "powerbi_ad": "text/csv",
            "powerbi_adset": "text/csv",
            "powerbi_campaign": "text/csv",
        }
        return mime_map.get(fmt, "application/octet-stream")

    @staticmethod
    def get_extension(fmt: str) -> str:
        ext_map = {
            "csv": ".csv", "xlsx": ".xlsx", "json": ".json",
            "powerbi_ad": ".csv", "powerbi_adset": ".csv", "powerbi_campaign": ".csv",
        }
        return ext_map.get(fmt, ".dat")
