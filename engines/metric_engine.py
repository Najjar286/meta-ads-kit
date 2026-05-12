"""DAG-based MetricEngine with topological sort, LRU cache, and metric registry."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable

import numpy as np
import pandas as pd


@dataclass
class MetricDef:
    name: str
    label: str
    category: str
    tier: int
    formula: str
    deps: list[str]
    func: Callable
    description: str = ""
    format: str = "num"
    thresholds: dict | None = None
    source: str = "standard"


class MetricEngine:
    """DAG-based metric computation engine with topological sort and caching."""

    def __init__(self) -> None:
        self._metrics: dict[str, MetricDef] = {}
        self._cache: dict[str, pd.DataFrame] = {}
        self._max_cache = 10

    def register(self, name: str, label: str, category: str, tier: int, formula: str,
                 deps: list[str], description: str = "", fmt: str = "num",
                 thresholds: dict | None = None, source: str = "standard") -> Callable:
        def decorator(func: Callable) -> Callable:
            self._metrics[name] = MetricDef(
                name=name, label=label, category=category, tier=tier,
                formula=formula, deps=deps, func=func,
                description=description, format=fmt,
                thresholds=thresholds, source=source,
            )
            return func
        return decorator

    def register_metric(self, metric_def: MetricDef) -> None:
        self._metrics[metric_def.name] = metric_def

    def _cache_key(self, df: pd.DataFrame, metric_names: list[str]) -> str:
        data_hash = hashlib.md5(
            pd.util.hash_pandas_object(df, index=True).values.tobytes()
        ).hexdigest()
        info = {
            "shape": list(df.shape),
            "data_hash": data_hash,
            "metrics": sorted(metric_names),
        }
        return hashlib.md5(json.dumps(info, sort_keys=True).encode()).hexdigest()

    def _topological_sort(self, metric_names: list[str]) -> list[str]:
        in_degree: dict[str, int] = defaultdict(int)
        graph: dict[str, list[str]] = defaultdict(list)
        relevant = set(metric_names)
        for name in metric_names:
            m = self._metrics.get(name)
            if not m:
                continue
            for dep in m.deps:
                if dep in self._metrics:
                    relevant.add(dep)
        for name in relevant:
            m = self._metrics.get(name)
            if not m:
                continue
            for dep in m.deps:
                if dep in self._metrics and dep in relevant:
                    graph[dep].append(name)
                    in_degree[name] += 1
            if name not in in_degree:
                in_degree[name] = 0
        queue: deque[str] = deque(n for n in relevant if in_degree.get(n, 0) == 0)
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return order

    def compute(self, df: pd.DataFrame, metric_names: list[str] | None = None,
                group_by: str | None = None) -> pd.DataFrame:
        if df is None or df.empty:
            return df
        if metric_names is None:
            metric_names = list(self._metrics.keys())
        available = [m for m in metric_names if m in self._metrics]
        if not available:
            return df

        cache_key = self._cache_key(df, available)
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = df.copy()
        order = self._topological_sort(available)
        for name in order:
            m = self._metrics.get(name)
            if not m:
                continue
            deps_available = all(d in result.columns for d in m.deps if d not in self._metrics)
            if not deps_available:
                continue
            try:
                result[name] = m.func(result)
            except Exception:
                result[name] = np.nan

        if len(self._cache) >= self._max_cache:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[cache_key] = result
        return result

    def get_available_metrics(self, df: pd.DataFrame) -> list[MetricDef]:
        return [m for m in self._metrics.values()
                if all(d in df.columns for d in m.deps if d not in self._metrics)]

    def get_metric_groups(self) -> dict[str, list[MetricDef]]:
        groups: dict[str, list[MetricDef]] = defaultdict(list)
        for m in self._metrics.values():
            groups[m.category].append(m)
        return dict(groups)

    def validate_metric(self, name: str, df: pd.DataFrame) -> bool:
        m = self._metrics.get(name)
        if not m:
            return False
        return all(d in df.columns for d in m.deps if d not in self._metrics)

    def explain_metric(self, name: str) -> str:
        m = self._metrics.get(name)
        if not m:
            return f"Metric '{name}' not found."
        lines = [
            f"Name: {m.name}",
            f"Label: {m.label}",
            f"Category: {m.category}",
            f"Tier: {m.tier}",
            f"Formula: {m.formula}",
            f"Dependencies: {', '.join(m.deps) if m.deps else 'None'}",
            f"Format: {m.format}",
            f"Description: {m.description}",
        ]
        return "\n".join(lines)

    def clear_cache(self) -> None:
        self._cache.clear()

    def list_metrics(self) -> list[MetricDef]:
        return list(self._metrics.values())

    def metric_count_by_tier(self) -> dict[int, int]:
        counts: dict[int, int] = defaultdict(int)
        for m in self._metrics.values():
            counts[m.tier] += 1
        return dict(counts)
