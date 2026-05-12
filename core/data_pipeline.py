"""DataFrame management with versioning, caching, and field standardization."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

FIELD_MAP: dict[str, str] = {
    "campaign_id": "campaign_id",
    "campaign_name": "campaign_name",
    "adset_id": "adset_id",
    "adset_name": "adset_name",
    "ad_id": "ad_id",
    "ad_name": "ad_name",
    "date_start": "date_start",
    "date_stop": "date_stop",
    "impressions": "impressions",
    "clicks": "clicks",
    "spend": "spend",
    "reach": "reach",
    "frequency": "frequency",
    "actions": "conversions",
    "cost_per_action_type": "cost_per_conv",
    "ctr": "ctr",
    "cpc": "cpc",
    "cpm": "cpm",
}

_DEFAULT_CACHE_TTL = 900


class DataPipeline:
    """Manages DataFrame lifecycle: load, standardize, cache, version."""

    def __init__(self, cache_dir: str = "output/.cache") -> None:
        self._memory_cache: dict[str, tuple[pd.DataFrame, float]] = {}
        self._cache_ttl = _DEFAULT_CACHE_TTL
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._versions: dict[str, str] = {}

    def standardize_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {}
        for src, dst in FIELD_MAP.items():
            if src in df.columns and src != dst:
                rename_map[src] = dst
        if rename_map:
            df = df.rename(columns=rename_map)
        return df

    def _compute_version(self, df: pd.DataFrame) -> str:
        info = {
            "shape": list(df.shape),
            "cols": sorted(df.columns.tolist()),
            "dtypes": {c: str(d) for c, d in df.dtypes.items()},
        }
        return hashlib.md5(json.dumps(info, sort_keys=True).encode()).hexdigest()[:12]

    def store(self, name: str, df: pd.DataFrame) -> str:
        version = self._compute_version(df)
        self._memory_cache[name] = (df, time.time())
        self._versions[name] = version
        return version

    def load(self, name: str) -> pd.DataFrame | None:
        entry = self._memory_cache.get(name)
        if entry is None:
            return None
        df, ts = entry
        if time.time() - ts > self._cache_ttl:
            del self._memory_cache[name]
            return None
        return df

    def save_to_disk(self, name: str, df: pd.DataFrame, fmt: str = "parquet") -> Path:
        path = self._cache_dir / f"{name}.{fmt}"
        if fmt == "parquet":
            df.to_parquet(path, index=False)
        elif fmt == "csv":
            df.to_csv(path, index=False)
        return path

    def load_from_disk(self, name: str, fmt: str = "parquet") -> pd.DataFrame | None:
        path = self._cache_dir / f"{name}.{fmt}"
        if not path.exists():
            return None
        if fmt == "parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path)

    def get_version(self, name: str) -> str | None:
        return self._versions.get(name)

    def clear_cache(self) -> None:
        self._memory_cache.clear()
        self._versions.clear()

    def list_datasets(self) -> list[str]:
        return list(self._memory_cache.keys())
