"""Tier 4: Composite Scores — 24 multi-signal health scores."""
from __future__ import annotations

import numpy as np

from engines.metric_engine import MetricDef, MetricEngine

_SAFE_DIV = 1e-10


def _normalize(series, invert=False):
    """Min-max normalize a series to 0-100."""
    mn, mx = series.min(), series.max()
    if mx - mn < _SAFE_DIV:
        return np.full(len(series), 50.0)
    norm = (series - mn) / (mx - mn) * 100
    return 100 - norm if invert else norm


def register_composite_metrics(engine: MetricEngine) -> None:
    """Register all Tier 4 Composite Score metrics."""

    @engine.register("ad_health_score", "Ad Health Score", "composite", 4,
                     "weighted(ctr, cpc, frequency, conv_rate)", ["ctr", "cpc", "frequency", "conversions", "clicks"],
                     description="Overall ad health composite", fmt="dec",
                     thresholds={"good": 70, "warn": 40, "bad": 20})
    def _ad_health(df):
        ctr_n = _normalize(df["ctr"])
        cpc_n = _normalize(df["cpc"], invert=True)
        freq_n = _normalize(df["frequency"], invert=True)
        conv_n = _normalize(df["conversions"] / df["clicks"].replace(0, _SAFE_DIV))
        return ctr_n * 0.3 + cpc_n * 0.25 + freq_n * 0.2 + conv_n * 0.25

    @engine.register("campaign_efficiency_score", "Campaign Efficiency", "composite", 4,
                     "weighted(roas, cpa, conv_rate, budget_util)", ["conversions", "spend", "clicks", "daily_budget"],
                     description="Campaign efficiency composite", fmt="dec")
    def _campaign_eff(df):
        roas_n = _normalize(df["conversions"] * 50 / df["spend"].replace(0, _SAFE_DIV))
        cpa_n = _normalize(df["spend"] / df["conversions"].replace(0, _SAFE_DIV), invert=True)
        cvr_n = _normalize(df["conversions"] / df["clicks"].replace(0, _SAFE_DIV))
        bu_n = _normalize(df["spend"] / df["daily_budget"].replace(0, _SAFE_DIV))
        return roas_n * 0.3 + cpa_n * 0.25 + cvr_n * 0.25 + bu_n * 0.2

    @engine.register("creative_vitality_score", "Creative Vitality", "composite", 4,
                     "weighted(ctr_trend, freq_impact, engagement)", ["ctr", "frequency", "total_engagement", "impressions"],
                     description="Creative freshness and impact", fmt="dec")
    def _creative_vitality(df):
        ctr_n = _normalize(df["ctr"])
        freq_impact = _normalize(df["frequency"], invert=True)
        eng_n = _normalize(df["total_engagement"] / df["impressions"].replace(0, _SAFE_DIV))
        return ctr_n * 0.4 + freq_impact * 0.3 + eng_n * 0.3

    @engine.register("audience_engagement_score", "Audience Engagement", "composite", 4,
                     "weighted(eng_rate, unique_ctr, interaction_depth)", ["total_engagement", "impressions", "unique_ctr", "likes", "comments", "shares", "clicks"],
                     description="Audience engagement quality", fmt="dec")
    def _audience_eng(df):
        eng_rate = _normalize(df["total_engagement"] / df["impressions"].replace(0, _SAFE_DIV))
        uctr = _normalize(df["unique_ctr"])
        interact = _normalize((df["likes"] + df["comments"] + df["shares"]) / df["clicks"].replace(0, _SAFE_DIV))
        return eng_rate * 0.35 + uctr * 0.35 + interact * 0.3

    @engine.register("roas_optimization_score", "ROAS Optimization", "composite", 4,
                     "weighted(roas, cpc_eff, conv_value)", ["conversions", "spend", "cpc", "clicks"],
                     description="ROAS optimization potential", fmt="dec")
    def _roas_opt(df):
        roas_n = _normalize(df["conversions"] * 50 / df["spend"].replace(0, _SAFE_DIV))
        cpc_eff = _normalize(df["cpc"], invert=True)
        cv_n = _normalize(df["conversions"] / df["clicks"].replace(0, _SAFE_DIV))
        return roas_n * 0.4 + cpc_eff * 0.3 + cv_n * 0.3

    @engine.register("budget_utilization_score", "Budget Utilization", "composite", 4,
                     "weighted(util_pct, spend_eff, runway)", ["spend", "daily_budget", "conversions"],
                     description="How well budget is being used", fmt="dec")
    def _budget_util(df):
        util = _normalize(df["spend"] / df["daily_budget"].replace(0, _SAFE_DIV))
        eff = _normalize(df["conversions"] / df["spend"].replace(0, _SAFE_DIV))
        return util * 0.5 + eff * 0.5

    @engine.register("risk_score", "Risk Score", "composite", 4,
                     "weighted(frequency, cpa_spike, ctr_decline)", ["frequency", "spend", "conversions", "ctr"],
                     description="Risk of ad fatigue or budget waste", fmt="dec")
    def _risk_score(df):
        freq_risk = _normalize(df["frequency"])
        cpa_risk = _normalize(df["spend"] / df["conversions"].replace(0, _SAFE_DIV))
        ctr_inv = _normalize(df["ctr"], invert=True)
        return freq_risk * 0.35 + cpa_risk * 0.35 + ctr_inv * 0.3

    @engine.register("quality_index", "Quality Index", "composite", 4,
                     "weighted(reach_rate, unique_ctr, engagement)", ["reach", "impressions", "unique_ctr", "total_engagement"],
                     description="Overall quality index", fmt="dec")
    def _quality_idx(df):
        rr = _normalize(df["reach"] / df["impressions"].replace(0, _SAFE_DIV))
        uctr = _normalize(df["unique_ctr"])
        eng = _normalize(df["total_engagement"] / df["impressions"].replace(0, _SAFE_DIV))
        return rr * 0.33 + uctr * 0.34 + eng * 0.33

    # Additional composite scores
    composite_defs = [
        ("funnel_health", "Funnel Health", ["impressions", "clicks", "conversions"]),
        ("video_engagement_score", "Video Engagement", ["video_plays", "video_thruplays", "impressions"]),
        ("cost_efficiency_index", "Cost Efficiency Index", ["spend", "clicks", "conversions"]),
        ("growth_potential", "Growth Potential", ["ctr", "conversions", "spend", "impressions"]),
        ("audience_quality_score", "Audience Quality", ["unique_clicks", "clicks", "reach", "impressions"]),
        ("placement_score", "Placement Score", ["impressions", "clicks", "spend", "ctr"]),
        ("time_decay_score", "Time Decay Score", ["ctr", "frequency", "spend"]),
        ("competitive_index", "Competitive Index", ["impressions", "spend", "ctr", "cpc"]),
        ("conversion_velocity", "Conversion Velocity", ["conversions", "clicks", "spend"]),
        ("media_mix_score", "Media Mix Score", ["spend", "impressions", "conversions", "ctr"]),
        ("brand_safety_score", "Brand Safety Score", ["impressions", "reach", "frequency"]),
        ("creative_diversity", "Creative Diversity", ["impressions", "clicks", "ctr"]),
        ("engagement_velocity", "Engagement Velocity", ["total_engagement", "impressions", "spend"]),
        ("retention_score", "Retention Score", ["frequency", "unique_clicks", "clicks"]),
        ("saturation_risk", "Saturation Risk", ["frequency", "reach", "impressions"]),
        ("delivery_score", "Delivery Score", ["impressions", "spend", "daily_budget"]),
    ]

    for name, label, deps in composite_defs:
        def _make_func(dep_list):
            def _func(df):
                scores = []
                for d in dep_list:
                    if d in df.columns and df[d].dtype in ("int64", "float64"):
                        scores.append(_normalize(df[d].astype(float)))
                if scores:
                    return sum(scores) / len(scores)
                return np.full(len(df), 50.0)
            return _func

        engine.register_metric(MetricDef(
            name=name, label=label, category="composite", tier=4,
            formula=f"weighted_composite({', '.join(deps)})",
            deps=deps, func=_make_func(deps),
            description=f"Composite score: {label}", format="dec",
            source="composite",
        ))
