"""Analytics engine: trend analysis, anomaly detection, forecasting, cohort analysis, budget efficiency."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

_SAFE_DIV = 1e-10


class AnalyticsEngine:
    """Provides analytical computations: trend, anomaly, forecast, cohort, budget."""

    @staticmethod
    def compute_trend(series: pd.Series) -> dict[str, Any]:
        clean = series.dropna()
        if len(clean) < 2:
            return {"direction": "neutral", "slope": 0.0, "r_squared": 0.0,
                    "last_value": float(clean.iloc[-1]) if len(clean) else 0.0,
                    "first_value": float(clean.iloc[0]) if len(clean) else 0.0,
                    "pct_change": 0.0}
        x = np.arange(len(clean), dtype=float)
        y = clean.values.astype(float)
        x_mean, y_mean = x.mean(), y.mean()
        ss_xy = np.sum((x - x_mean) * (y - y_mean))
        ss_xx = np.sum((x - x_mean) ** 2)
        slope = ss_xy / max(ss_xx, _SAFE_DIV)
        intercept = y_mean - slope * x_mean
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y_mean) ** 2)
        r_squared = 1 - ss_res / max(ss_tot, _SAFE_DIV)
        first_val = float(y[0])
        last_val = float(y[-1])
        pct_change = (last_val - first_val) / max(abs(first_val), _SAFE_DIV) * 100
        direction = "up" if slope > 0.01 else "down" if slope < -0.01 else "neutral"
        return {
            "direction": direction,
            "slope": round(slope, 6),
            "r_squared": round(max(0, r_squared), 4),
            "last_value": round(last_val, 2),
            "first_value": round(first_val, 2),
            "pct_change": round(pct_change, 2),
        }

    @staticmethod
    def detect_anomalies(df: pd.DataFrame, metric: str, method: str = "zscore") -> pd.DataFrame:
        result = df.copy()
        if metric not in result.columns:
            result["anomaly_score"] = 0.0
            result["is_anomaly"] = False
            return result
        values = result[metric].astype(float)
        if method == "zscore":
            mean_val = values.mean()
            std_val = values.std()
            if std_val < _SAFE_DIV:
                result["anomaly_score"] = 0.0
                result["is_anomaly"] = False
            else:
                z_scores = (values - mean_val) / std_val
                result["anomaly_score"] = z_scores.abs()
                result["is_anomaly"] = z_scores.abs() > 3
        elif method == "iqr":
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            result["anomaly_score"] = np.where(
                values < lower, (lower - values) / max(iqr, _SAFE_DIV),
                np.where(values > upper, (values - upper) / max(iqr, _SAFE_DIV), 0.0),
            )
            result["is_anomaly"] = (values < lower) | (values > upper)
        else:
            result["anomaly_score"] = 0.0
            result["is_anomaly"] = False
        return result

    @staticmethod
    def compute_forecast(series: pd.Series, periods: int = 7) -> dict[str, Any]:
        clean = series.dropna().astype(float)
        if len(clean) < 3:
            return {"forecast": [], "lower_bound": [], "upper_bound": [], "mape": 0.0}
        alpha, beta = 0.3, 0.1
        level = float(clean.iloc[0])
        trend = float(clean.iloc[1] - clean.iloc[0])
        for val in clean:
            prev_level = level
            level = alpha * val + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend
        forecast = []
        for h in range(1, periods + 1):
            forecast.append(round(level + h * trend, 2))
        std = float(clean.std())
        lower = [round(f - 1.96 * std, 2) for f in forecast]
        upper = [round(f + 1.96 * std, 2) for f in forecast]
        fitted = []
        l2 = float(clean.iloc[0])
        t2 = float(clean.iloc[1] - clean.iloc[0])
        for val in clean:
            prev_l = l2
            l2 = alpha * val + (1 - alpha) * (l2 + t2)
            t2 = beta * (l2 - prev_l) + (1 - beta) * t2
            fitted.append(l2 + t2)
        errors = np.abs(clean.values - np.array(fitted))
        mape = float(np.mean(errors / np.maximum(np.abs(clean.values), _SAFE_DIV)) * 100)
        return {
            "forecast": forecast,
            "lower_bound": lower,
            "upper_bound": upper,
            "mape": round(mape, 2),
        }

    @staticmethod
    def compute_budget_efficiency(df: pd.DataFrame) -> dict[str, Any]:
        if df is None or df.empty:
            return {"total_spend": 0, "daily_avg_spend": 0, "budget_utilization_pct": 0,
                    "active_days": 0, "runway_days": 0}
        total_spend = float(df["spend"].sum()) if "spend" in df.columns else 0
        active_days = int(df["date_start"].nunique()) if "date_start" in df.columns else 1
        daily_avg = total_spend / max(active_days, 1)
        total_budget = float(df["daily_budget"].sum()) if "daily_budget" in df.columns else total_spend
        util_pct = (total_spend / max(total_budget, _SAFE_DIV)) * 100
        runway = int((total_budget - total_spend) / max(daily_avg, _SAFE_DIV)) if daily_avg > 0 else 0
        return {
            "total_spend": round(total_spend, 2),
            "daily_avg_spend": round(daily_avg, 2),
            "budget_utilization_pct": round(util_pct, 1),
            "active_days": active_days,
            "runway_days": max(0, runway),
        }

    @staticmethod
    def compute_cohort_analysis(df: pd.DataFrame, date_col: str = "date_start",
                                metric_col: str = "spend",
                                group_col: str = "campaign_id") -> pd.DataFrame:
        if df is None or df.empty or date_col not in df.columns or metric_col not in df.columns:
            return pd.DataFrame()
        data = df.copy()
        data[date_col] = pd.to_datetime(data[date_col])
        data["period_week"] = data[date_col].dt.isocalendar().week.astype(int)
        if group_col in data.columns:
            first_appearance = data.groupby(group_col)[date_col].min().reset_index()
            first_appearance["cohort_week"] = pd.to_datetime(
                first_appearance[date_col]
            ).dt.isocalendar().week.astype(int)
            first_appearance = first_appearance[[group_col, "cohort_week"]]
            data = data.merge(first_appearance, on=group_col, how="left")
        else:
            data["cohort_week"] = data["period_week"]
        pivot = data.groupby(["cohort_week", "period_week"])[metric_col].sum().reset_index()
        cohort_table = pivot.pivot(index="cohort_week", columns="period_week", values=metric_col)
        first_week_values = cohort_table.iloc[:, 0] if not cohort_table.empty else pd.Series()
        if not first_week_values.empty:
            retention = cohort_table.div(first_week_values.replace(0, _SAFE_DIV), axis=0) * 100
            return retention.round(1)
        return cohort_table
