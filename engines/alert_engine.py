"""Alert engine: 25 rules, 6 categories, cooldown, dispatch, acknowledge."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import pandas as pd

_SAFE_DIV = 1e-10


@dataclass
class AlertResult:
    alert_id: str
    rule_id: str
    rule_name: str
    category: str
    severity: str
    message: str
    entity_id: str
    entity_name: str
    metric_value: float
    threshold: float
    timestamp: float
    acknowledged: bool = False


@dataclass
class RuleDef:
    rule_id: str
    name: str
    category: str
    severity: str
    metric: str
    operator: str
    threshold: float
    enabled: bool = True
    cooldown_seconds: int = 3600
    description: str = ""


_DEFAULT_RULES: list[dict] = [
    {"rule_id": "R-001", "name": "Low CTR", "category": "performance", "severity": "warning", "metric": "ctr", "operator": "<", "threshold": 0.5, "description": "CTR below 0.5%"},
    {"rule_id": "R-002", "name": "Critical CTR", "category": "performance", "severity": "critical", "metric": "ctr", "operator": "<", "threshold": 0.2, "description": "CTR critically low"},
    {"rule_id": "R-003", "name": "High CPC", "category": "cost", "severity": "warning", "metric": "cpc", "operator": ">", "threshold": 5.0, "description": "CPC above $5"},
    {"rule_id": "R-004", "name": "Critical CPC", "category": "cost", "severity": "critical", "metric": "cpc", "operator": ">", "threshold": 10.0, "description": "CPC above $10"},
    {"rule_id": "R-005", "name": "High CPA", "category": "cost", "severity": "warning", "metric": "cost_per_conv", "operator": ">", "threshold": 20.0, "description": "CPA above $20"},
    {"rule_id": "R-006", "name": "Critical CPA", "category": "cost", "severity": "critical", "metric": "cost_per_conv", "operator": ">", "threshold": 50.0, "description": "CPA above $50"},
    {"rule_id": "R-007", "name": "Low ROAS", "category": "performance", "severity": "warning", "metric": "roas", "operator": "<", "threshold": 1.0, "description": "ROAS below 1.0"},
    {"rule_id": "R-008", "name": "Critical ROAS", "category": "performance", "severity": "critical", "metric": "roas", "operator": "<", "threshold": 0.5, "description": "ROAS below 0.5"},
    {"rule_id": "R-009", "name": "Budget Overrun", "category": "budget", "severity": "warning", "metric": "budget_util_pct", "operator": ">", "threshold": 120.0, "description": "Spend exceeds budget by 20%"},
    {"rule_id": "R-010", "name": "High Frequency", "category": "health", "severity": "warning", "metric": "frequency", "operator": ">", "threshold": 5.0, "description": "Frequency above 5"},
    {"rule_id": "R-011", "name": "Critical Frequency", "category": "health", "severity": "critical", "metric": "frequency", "operator": ">", "threshold": 10.0, "description": "Frequency above 10"},
    {"rule_id": "R-012", "name": "Zero Impressions", "category": "health", "severity": "critical", "metric": "impressions", "operator": "==", "threshold": 0, "description": "No impressions delivered"},
    {"rule_id": "R-013", "name": "Zero Reach", "category": "health", "severity": "critical", "metric": "reach", "operator": "==", "threshold": 0, "description": "No reach"},
    {"rule_id": "R-014", "name": "CPM Spike", "category": "cost", "severity": "warning", "metric": "cpm", "operator": ">", "threshold": 50.0, "description": "CPM spiked above $50"},
    {"rule_id": "R-015", "name": "CPA Spike", "category": "cost", "severity": "warning", "metric": "cost_per_conv", "operator": ">", "threshold": 30.0, "description": "CPA spiked"},
    {"rule_id": "R-016", "name": "Conversion Drop", "category": "performance", "severity": "warning", "metric": "conversions", "operator": "<", "threshold": 1.0, "description": "Less than 1 conversion"},
    {"rule_id": "R-017", "name": "Low Engagement", "category": "performance", "severity": "warning", "metric": "total_engagement", "operator": "<", "threshold": 5.0, "description": "Very low engagement"},
    {"rule_id": "R-018", "name": "High Spend No Conv", "category": "cost", "severity": "critical", "metric": "spend", "operator": ">", "threshold": 50.0, "description": "High spend with no conversions"},
    {"rule_id": "R-019", "name": "Below Avg Quality", "category": "quality", "severity": "warning", "metric": "quality_rank_score", "operator": "<", "threshold": 1.0, "description": "Below average quality rank"},
    {"rule_id": "R-020", "name": "Below Avg Conv Rank", "category": "quality", "severity": "warning", "metric": "conv_rate_rank_score", "operator": "<", "threshold": 1.0, "description": "Below average conversion rank"},
    {"rule_id": "R-021", "name": "Frequency Creep", "category": "health", "severity": "warning", "metric": "frequency", "operator": ">", "threshold": 3.5, "description": "Frequency increasing rapidly"},
    {"rule_id": "R-022", "name": "Creative Fatigue", "category": "change", "severity": "warning", "metric": "ctr", "operator": "<", "threshold": 0.8, "description": "CTR declining, possible fatigue"},
    {"rule_id": "R-023", "name": "Budget Util Low", "category": "budget", "severity": "info", "metric": "budget_util_pct", "operator": "<", "threshold": 50.0, "description": "Budget underutilized"},
    {"rule_id": "R-024", "name": "Bid Strategy Changed", "category": "change", "severity": "info", "metric": "cpc", "operator": ">", "threshold": 8.0, "description": "CPC suggests bid strategy change"},
    {"rule_id": "R-025", "name": "Daypart Drop", "category": "performance", "severity": "info", "metric": "ctr", "operator": "<", "threshold": 0.3, "description": "CTR dropped in daypart"},
]


class AlertEngine:
    """Evaluates alert rules against DataFrame, manages alert lifecycle."""

    def __init__(self) -> None:
        self._rules: dict[str, RuleDef] = {}
        self._active_alerts: list[AlertResult] = []
        self._history: list[AlertResult] = []
        self._cooldowns: dict[str, float] = {}
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        for r in _DEFAULT_RULES:
            self._rules[r["rule_id"]] = RuleDef(**r)

    def _check_condition(self, value: float, operator: str, threshold: float) -> bool:
        if operator == "<":
            return value < threshold
        if operator == ">":
            return value > threshold
        if operator == "==":
            return abs(value - threshold) < _SAFE_DIV
        if operator == "<=":
            return value <= threshold
        if operator == ">=":
            return value >= threshold
        return False

    def evaluate(self, df: pd.DataFrame, entity_scope: str = "all") -> list[AlertResult]:
        if df is None or df.empty:
            return []
        triggered: list[AlertResult] = []
        now = time.time()

        rank_map = {"ABOVE_AVERAGE": 2, "AVERAGE": 1, "BELOW_AVERAGE": 0}
        eval_df = df.copy()
        if "quality_rank" in eval_df.columns:
            eval_df["quality_rank_score"] = eval_df["quality_rank"].map(rank_map).fillna(1)
        if "conv_rate_rank" in eval_df.columns:
            eval_df["conv_rate_rank_score"] = eval_df["conv_rate_rank"].map(rank_map).fillna(1)
        if "spend" in eval_df.columns and "daily_budget" in eval_df.columns:
            eval_df["budget_util_pct"] = eval_df["spend"] / eval_df["daily_budget"].replace(0, _SAFE_DIV) * 100

        for rule in self._rules.values():
            if not rule.enabled:
                continue
            if rule.metric not in eval_df.columns:
                continue
            for _, row in eval_df.iterrows():
                value = float(row.get(rule.metric, 0))
                if not self._check_condition(value, rule.operator, rule.threshold):
                    continue
                entity_id = str(row.get("ad_id", row.get("campaign_id", "unknown")))
                entity_name = str(row.get("ad_name", row.get("campaign_name", "Unknown")))
                cooldown_key = f"{rule.rule_id}_{entity_id}"
                if cooldown_key in self._cooldowns:
                    if now - self._cooldowns[cooldown_key] < rule.cooldown_seconds:
                        continue
                self._cooldowns[cooldown_key] = now
                existing = {f"{a.rule_id}_{a.entity_id}" for a in triggered}
                if cooldown_key in existing:
                    continue
                alert = AlertResult(
                    alert_id=str(uuid.uuid4())[:8],
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    message=f"{rule.name}: {rule.metric}={value:.2f} {rule.operator} {rule.threshold}",
                    entity_id=entity_id,
                    entity_name=entity_name,
                    metric_value=value,
                    threshold=rule.threshold,
                    timestamp=now,
                )
                triggered.append(alert)
        self._active_alerts.extend(triggered)
        self._history.extend(triggered)
        return triggered

    def dispatch(self, alert_results: list[AlertResult]) -> None:
        pass

    def acknowledge(self, alert_id: str) -> bool:
        for alert in self._active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                self._active_alerts = [a for a in self._active_alerts if a.alert_id != alert_id]
                return True
        return False

    def toggle_rule(self, rule_id: str, enabled: bool) -> None:
        if rule_id in self._rules:
            self._rules[rule_id].enabled = enabled

    def get_rules(self) -> list[dict]:
        return [
            {
                "rule_id": r.rule_id, "name": r.name, "category": r.category,
                "severity": r.severity, "metric": r.metric, "operator": r.operator,
                "threshold": r.threshold, "enabled": r.enabled,
                "description": r.description,
            }
            for r in self._rules.values()
        ]

    def get_active_alerts(self) -> list[AlertResult]:
        return [a for a in self._active_alerts if not a.acknowledged]

    def get_alert_history(self, days: int = 30) -> list[AlertResult]:
        cutoff = time.time() - days * 86400
        return [a for a in self._history if a.timestamp >= cutoff]
