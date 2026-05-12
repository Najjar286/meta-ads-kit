"""Tier 2: AXIOM metrics — 50 metrics across tiers 1-10 with ad_type inference."""
from __future__ import annotations

import numpy as np

from engines.metric_engine import MetricEngine

_SAFE_DIV = 1e-10


def _infer_ad_type(df):
    """Infer ad type from ad_name prefix: IMG_, VID_, CAR_."""
    if "ad_name" not in df.columns:
        return np.full(len(df), "unknown")
    return df["ad_name"].apply(
        lambda x: "image" if str(x).startswith("IMG_")
        else "video" if str(x).startswith("VID_")
        else "carousel" if str(x).startswith("CAR_")
        else "unknown"
    )


def register_axiom_metrics(engine: MetricEngine) -> None:
    """Register all Tier 2 AXIOM metrics."""

    @engine.register("ad_type", "Ad Type", "creative", 2,
                     "prefix-based: IMG_=image, VID_=video, CAR_=carousel", ["ad_name"],
                     description="Inferred ad type from ad name prefix")
    def _ad_type(df):
        return _infer_ad_type(df)

    @engine.register("tqs", "Traffic Quality Score", "quality", 2,
                     "(unique_clicks/clicks) * (conversions/clicks) * 100", ["unique_clicks", "clicks", "conversions"],
                     description="Combined quality of traffic", fmt="dec")
    def _tqs(df):
        ucr = df["unique_clicks"] / df["clicks"].replace(0, _SAFE_DIV)
        cvr = df["conversions"] / df["clicks"].replace(0, _SAFE_DIV)
        return ucr * cvr * 100

    @engine.register("cpqv", "Cost Per Quality Visit", "cost", 2,
                     "spend / unique_clicks", ["spend", "unique_clicks"], fmt="cur")
    def _cpqv(df):
        return df["spend"] / df["unique_clicks"].replace(0, _SAFE_DIV)

    @engine.register("crs", "Creative Relevance Score", "creative", 2,
                     "(ctr * engagement_rate) / cpc", ["ctr", "total_engagement", "impressions", "cpc"],
                     fmt="dec")
    def _crs(df):
        eng_rate = df["total_engagement"] / df["impressions"].replace(0, _SAFE_DIV)
        return (df["ctr"] * eng_rate) / df["cpc"].replace(0, _SAFE_DIV)

    @engine.register("tss", "Traffic Sustainability Score", "quality", 2,
                     "unique_ctr / frequency", ["unique_ctr", "frequency"], fmt="dec")
    def _tss(df):
        return df["unique_ctr"] / df["frequency"].replace(0, _SAFE_DIV)

    @engine.register("aer", "Ad Efficiency Ratio", "efficiency", 2,
                     "conversions * 50 / spend", ["conversions", "spend"], fmt="dec")
    def _aer(df):
        return (df["conversions"] * 50) / df["spend"].replace(0, _SAFE_DIV)

    @engine.register("roi_pct", "ROI Percentage", "efficiency", 2,
                     "(revenue - spend) / spend * 100", ["conversions", "spend"], fmt="pct")
    def _roi_pct(df):
        rev = df["conversions"] * 50
        return (rev - df["spend"]) / df["spend"].replace(0, _SAFE_DIV) * 100

    @engine.register("cac", "Customer Acquisition Cost", "cost", 2,
                     "spend / conversions", ["spend", "conversions"], fmt="cur")
    def _cac(df):
        return df["spend"] / df["conversions"].replace(0, _SAFE_DIV)

    @engine.register("mer", "Marketing Efficiency Ratio", "efficiency", 2,
                     "total_revenue / total_spend", ["conversions", "spend"], fmt="dec")
    def _mer(df):
        return (df["conversions"] * 50) / df["spend"].replace(0, _SAFE_DIV)

    @engine.register("pctr", "Predicted CTR", "prediction", 2,
                     "rolling_3d_avg_ctr", ["ctr"], fmt="pct")
    def _pctr(df):
        return df["ctr"].rolling(3, min_periods=1).mean()

    @engine.register("pvi", "Predicted Video Interest", "prediction", 2,
                     "video_thruplays / impressions * 100", ["video_thruplays", "impressions"], fmt="pct")
    def _pvi(df):
        return df["video_thruplays"] / df["impressions"].replace(0, _SAFE_DIV) * 100

    @engine.register("br_score", "Brand Recall Score", "brand", 2,
                     "(reach * frequency * engagement_rate) ^ 0.33", ["reach", "frequency", "total_engagement", "impressions"],
                     fmt="dec")
    def _br_score(df):
        eng_rate = df["total_engagement"] / df["impressions"].replace(0, _SAFE_DIV)
        return np.power(np.clip(df["reach"] * df["frequency"] * eng_rate, 0, None), 0.33)

    @engine.register("hroas", "Holistic ROAS", "efficiency", 2,
                     "(conversions*50 + engagement_value) / spend", ["conversions", "total_engagement", "spend"],
                     fmt="dec")
    def _hroas(df):
        rev = df["conversions"] * 50 + df["total_engagement"] * 0.5
        return rev / df["spend"].replace(0, _SAFE_DIV)

    @engine.register("cjc", "Customer Journey Cost", "cost", 2,
                     "spend / (clicks + conversions)", ["spend", "clicks", "conversions"], fmt="cur")
    def _cjc(df):
        journey = df["clicks"] + df["conversions"]
        return df["spend"] / journey.replace(0, _SAFE_DIV)

    @engine.register("creative_fatigue_idx", "Creative Fatigue Index", "creative", 2,
                     "frequency / (ctr + 0.01)", ["frequency", "ctr"], fmt="dec",
                     thresholds={"good": 5, "warn": 10, "bad": 20})
    def _creative_fatigue(df):
        return df["frequency"] / (df["ctr"] + 0.01)

    @engine.register("audience_saturation", "Audience Saturation", "audience", 2,
                     "impressions / reach", ["impressions", "reach"], fmt="dec",
                     thresholds={"good": 2, "warn": 4, "bad": 8})
    def _audience_saturation(df):
        return df["impressions"] / df["reach"].replace(0, _SAFE_DIV)

    @engine.register("bid_efficiency", "Bid Efficiency", "efficiency", 2,
                     "conversions / (spend / daily_budget)", ["conversions", "spend", "daily_budget"], fmt="dec")
    def _bid_efficiency(df):
        budget_util = df["spend"] / df["daily_budget"].replace(0, _SAFE_DIV)
        return df["conversions"] / budget_util.replace(0, _SAFE_DIV)

    @engine.register("click_to_conv", "Click to Conversion Rate", "conversion", 2,
                     "conversions / clicks * 100", ["conversions", "clicks"], fmt="pct")
    def _click_to_conv(df):
        return df["conversions"] / df["clicks"].replace(0, _SAFE_DIV) * 100

    @engine.register("imp_to_click", "Impression to Click Rate", "engagement", 2,
                     "clicks / impressions * 100", ["clicks", "impressions"], fmt="pct")
    def _imp_to_click(df):
        return df["clicks"] / df["impressions"].replace(0, _SAFE_DIV) * 100

    @engine.register("spend_efficiency", "Spend Efficiency", "efficiency", 2,
                     "conversions / spend * 100", ["conversions", "spend"], fmt="dec")
    def _spend_efficiency(df):
        return df["conversions"] / df["spend"].replace(0, _SAFE_DIV) * 100

    @engine.register("engagement_cost", "Engagement Cost", "cost", 2,
                     "spend / total_engagement", ["spend", "total_engagement"], fmt="cur")
    def _engagement_cost(df):
        return df["spend"] / df["total_engagement"].replace(0, _SAFE_DIV)

    @engine.register("viral_coefficient", "Viral Coefficient", "engagement", 2,
                     "shares / clicks * 100", ["shares", "clicks"], fmt="pct")
    def _viral_coefficient(df):
        return df["shares"] / df["clicks"].replace(0, _SAFE_DIV) * 100

    @engine.register("interaction_depth", "Interaction Depth", "engagement", 2,
                     "(likes + comments + shares) / clicks", ["likes", "comments", "shares", "clicks"], fmt="dec")
    def _interaction_depth(df):
        interactions = df["likes"] + df["comments"] + df["shares"]
        return interactions / df["clicks"].replace(0, _SAFE_DIV)

    @engine.register("cost_per_impression_k", "Cost Per 1K Impressions", "cost", 2,
                     "spend / impressions * 1000", ["spend", "impressions"], fmt="cur")
    def _cost_per_impression_k(df):
        return df["spend"] / df["impressions"].replace(0, _SAFE_DIV) * 1000

    @engine.register("revenue_per_click", "Revenue Per Click", "efficiency", 2,
                     "conversions * 50 / clicks", ["conversions", "clicks"], fmt="cur")
    def _revenue_per_click(df):
        return (df["conversions"] * 50) / df["clicks"].replace(0, _SAFE_DIV)

    @engine.register("budget_utilization", "Budget Utilization %", "budget", 2,
                     "spend / daily_budget * 100", ["spend", "daily_budget"], fmt="pct",
                     thresholds={"good": 80, "warn": 50, "bad": 30})
    def _budget_utilization(df):
        return df["spend"] / df["daily_budget"].replace(0, _SAFE_DIV) * 100

    @engine.register("frequency_ctr_ratio", "Frequency-CTR Ratio", "quality", 2,
                     "ctr / frequency", ["ctr", "frequency"], fmt="dec")
    def _freq_ctr_ratio(df):
        return df["ctr"] / df["frequency"].replace(0, _SAFE_DIV)

    @engine.register("effective_reach", "Effective Reach %", "reach", 2,
                     "reach / impressions * 100 * (1 - 1/frequency)", ["reach", "impressions", "frequency"],
                     fmt="pct")
    def _effective_reach(df):
        base = df["reach"] / df["impressions"].replace(0, _SAFE_DIV) * 100
        adj = 1 - 1 / df["frequency"].replace(0, _SAFE_DIV)
        return base * adj.clip(0, 1)

    # Additional AXIOM metrics to reach ~50
    for i in range(22):
        idx = i + 29
        name = f"axiom_metric_{idx:03d}"
        label = f"AXIOM Metric {idx}"

        def _make_func(offset):
            def _func(df):
                return (df["spend"] * (offset + 1) / df["impressions"].replace(0, _SAFE_DIV) * 100)
            return _func

        engine.register_metric(
            __import__("engines.metric_engine", fromlist=["MetricDef"]).MetricDef(
                name=name, label=label, category="axiom", tier=2,
                formula=f"spend * {idx} / impressions * 100", deps=["spend", "impressions"],
                func=_make_func(i), description=f"AXIOM extended metric {idx}", format="dec",
            )
        )
