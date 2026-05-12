"""Schema validation for ad insights DataFrames — INSIGHT_V1 contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

INSIGHT_V1: list[dict[str, Any]] = [
    {"name": "account_id", "type": "str", "required": True, "nullable": False},
    {"name": "account_name", "type": "str", "required": True, "nullable": False},
    {"name": "campaign_id", "type": "str", "required": True, "nullable": False},
    {"name": "campaign_name", "type": "str", "required": True, "nullable": False},
    {"name": "adset_id", "type": "str", "required": True, "nullable": False},
    {"name": "adset_name", "type": "str", "required": True, "nullable": False},
    {"name": "ad_id", "type": "str", "required": True, "nullable": False},
    {"name": "ad_name", "type": "str", "required": True, "nullable": False},
    {"name": "status", "type": "str", "required": True, "nullable": False},
    {"name": "objective", "type": "str", "required": True, "nullable": False},
    {"name": "daily_budget", "type": "float", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "date_start", "type": "datetime", "required": True, "nullable": False},
    {"name": "date_stop", "type": "datetime", "required": True, "nullable": False},
    {"name": "impressions", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "clicks", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "spend", "type": "float", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "reach", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "frequency", "type": "float", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "ctr", "type": "float", "required": True, "nullable": False},
    {"name": "cpc", "type": "float", "required": True, "nullable": False},
    {"name": "cpm", "type": "float", "required": True, "nullable": False},
    {"name": "conversions", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "cost_per_conv", "type": "float", "required": True, "nullable": False},
    {"name": "total_engagement", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "likes", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "comments", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "shares", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "unique_clicks", "type": "int", "required": True, "nullable": False, "valid_range": (0, None)},
    {"name": "unique_ctr", "type": "float", "required": True, "nullable": False},
    {"name": "video_plays", "type": "int", "required": False, "nullable": True, "valid_range": (0, None)},
    {"name": "video_thruplays", "type": "int", "required": False, "nullable": True, "valid_range": (0, None)},
    {"name": "video_p25", "type": "int", "required": False, "nullable": True, "valid_range": (0, None)},
    {"name": "video_p50", "type": "int", "required": False, "nullable": True, "valid_range": (0, None)},
    {"name": "video_p75", "type": "int", "required": False, "nullable": True, "valid_range": (0, None)},
    {"name": "video_p95", "type": "int", "required": False, "nullable": True, "valid_range": (0, None)},
    {"name": "quality_rank", "type": "str", "required": False, "nullable": True},
    {"name": "conv_rate_rank", "type": "str", "required": False, "nullable": True},
]

_SCHEMA_MAP = {"INSIGHT_V1": INSIGHT_V1}


@dataclass
class ValidationError:
    column: str
    error_type: str
    message: str
    severity: str = "error"


class SchemaValidator:
    """Validates DataFrames against INSIGHT_V1 schema."""

    @staticmethod
    def validate(df: pd.DataFrame, schema_name: str = "INSIGHT_V1") -> list[ValidationError]:
        schema = _SCHEMA_MAP.get(schema_name, INSIGHT_V1)
        errors: list[ValidationError] = []
        for field_def in schema:
            name = field_def["name"]
            if field_def["required"] and name not in df.columns:
                errors.append(ValidationError(name, "missing_column", f"Required column '{name}' is missing"))
                continue
            if name not in df.columns:
                continue
            if not field_def.get("nullable", True) and df[name].isna().any():
                count = int(df[name].isna().sum())
                errors.append(ValidationError(name, "null_values", f"Column '{name}' has {count} null values", "warning"))
            vr = field_def.get("valid_range")
            if vr and name in df.columns:
                lo, hi = vr
                if lo is not None:
                    below = (df[name] < lo).sum()
                    if below > 0:
                        errors.append(ValidationError(name, "range_violation", f"{below} values below {lo}", "warning"))
                if hi is not None:
                    above = (df[name] > hi).sum()
                    if above > 0:
                        errors.append(ValidationError(name, "range_violation", f"{above} values above {hi}", "warning"))
        return errors

    @staticmethod
    def repair_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for field_def in INSIGHT_V1:
            name = field_def["name"]
            if name not in df.columns:
                continue
            ftype = field_def["type"]
            if ftype in ("int", "float"):
                df[name] = pd.to_numeric(df[name], errors="coerce")
                if not field_def.get("nullable", True):
                    df[name] = df[name].fillna(0)
            elif ftype == "datetime":
                df[name] = pd.to_datetime(df[name], errors="coerce")
            vr = field_def.get("valid_range")
            if vr and ftype in ("int", "float"):
                lo, hi = vr
                if lo is not None:
                    df[name] = df[name].clip(lower=lo)
                if hi is not None:
                    df[name] = df[name].clip(upper=hi)
        return df

    @staticmethod
    def schema_report(df: pd.DataFrame) -> dict:
        errors = SchemaValidator.validate(df)
        total_fields = len(INSIGHT_V1)
        present = sum(1 for f in INSIGHT_V1 if f["name"] in df.columns)
        error_count = len([e for e in errors if e.severity == "error"])
        warn_count = len([e for e in errors if e.severity == "warning"])
        quality = max(0, 100 - error_count * 10 - warn_count * 2)
        return {
            "total_fields": total_fields,
            "present_fields": present,
            "missing_fields": total_fields - present,
            "errors": error_count,
            "warnings": warn_count,
            "quality_score": quality,
            "details": [{"column": e.column, "type": e.error_type, "message": e.message, "severity": e.severity} for e in errors],
        }
