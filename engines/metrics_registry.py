"""Tier 1: Standard & Extended KPIs — 26 metrics."""
from __future__ import annotations

import numpy as np

from engines.metric_engine import MetricEngine

_SAFE_DIV = 1e-10


def register_standard_metrics(engine: MetricEngine) -> None:
    """Register all Tier 1 standard and extended KPIs."""

    @engine.register("engagement_rate", "Engagement Rate", "engagement", 1,
                     "total_engagement / impressions * 100", ["total_engagement", "impressions"],
                     description="Total engagement divided by impressions", fmt="pct")
    def _engagement_rate(df):
        return df["total_engagement"] / df["impressions"].replace(0, _SAFE_DIV) * 100

    @engine.register("conversion_rate", "Conversion Rate", "conversion", 1,
                     "conversions / clicks * 100", ["conversions", "clicks"],
                     description="Conversions divided by clicks", fmt="pct")
    def _conversion_rate(df):
        return df["conversions"] / df["clicks"].replace(0, _SAFE_DIV) * 100

    @engine.register("roas", "Return on Ad Spend", "efficiency", 1,
                     "conversions * avg_order_value / spend", ["conversions", "spend"],
                     description="Revenue generated per dollar spent", fmt="dec")
    def _roas(df):
        avg_order = 50.0
        return (df["conversions"] * avg_order) / df["spend"].replace(0, _SAFE_DIV)

    @engine.register("cpl", "Cost Per Lead", "cost", 1,
                     "spend / conversions", ["spend", "conversions"],
                     description="Cost per lead/conversion", fmt="cur")
    def _cpl(df):
        return df["spend"] / df["conversions"].replace(0, _SAFE_DIV)

    @engine.register("bounce_rate", "Bounce Rate", "engagement", 1,
                     "1 - (unique_clicks / clicks)", ["unique_clicks", "clicks"],
                     description="Percentage of non-unique clicks", fmt="pct")
    def _bounce_rate(df):
        return (1 - df["unique_clicks"] / df["clicks"].replace(0, _SAFE_DIV)) * 100

    @engine.register("video_avg_watch", "Avg Video Watch %", "video", 1,
                     "video_thruplays / video_plays * 100", ["video_thruplays", "video_plays"],
                     description="Average video watch percentage", fmt="pct")
    def _video_avg_watch(df):
        return df["video_thruplays"] / df["video_plays"].replace(0, _SAFE_DIV) * 100

    @engine.register("cost_per_thumb", "Cost Per Like", "cost", 1,
                     "spend / likes", ["spend", "likes"], fmt="cur")
    def _cost_per_thumb(df):
        return df["spend"] / df["likes"].replace(0, _SAFE_DIV)

    @engine.register("cost_per_comment", "Cost Per Comment", "cost", 1,
                     "spend / comments", ["spend", "comments"], fmt="cur")
    def _cost_per_comment(df):
        return df["spend"] / df["comments"].replace(0, _SAFE_DIV)

    @engine.register("cost_per_share", "Cost Per Share", "cost", 1,
                     "spend / shares", ["spend", "shares"], fmt="cur")
    def _cost_per_share(df):
        return df["spend"] / df["shares"].replace(0, _SAFE_DIV)

    @engine.register("impression_share", "Impression Share", "reach", 1,
                     "impressions / total_impressions * 100", ["impressions"],
                     description="Share of total impressions", fmt="pct")
    def _impression_share(df):
        total = df["impressions"].sum()
        return df["impressions"] / max(total, _SAFE_DIV) * 100

    @engine.register("reach_rate", "Reach Rate", "reach", 1,
                     "reach / impressions * 100", ["reach", "impressions"],
                     description="Unique reach as pct of impressions", fmt="pct")
    def _reach_rate(df):
        return df["reach"] / df["impressions"].replace(0, _SAFE_DIV) * 100

    @engine.register("click_share", "Click Share", "engagement", 1,
                     "clicks / total_clicks * 100", ["clicks"],
                     description="Share of total clicks", fmt="pct")
    def _click_share(df):
        total = df["clicks"].sum()
        return df["clicks"] / max(total, _SAFE_DIV) * 100

    @engine.register("conversion_value", "Conversion Value", "conversion", 1,
                     "conversions * avg_order_value", ["conversions"],
                     description="Estimated revenue from conversions", fmt="cur")
    def _conversion_value(df):
        return df["conversions"] * 50.0

    @engine.register("roas_d7", "7-Day ROAS", "efficiency", 1,
                     "rolling_7d_revenue / rolling_7d_spend", ["conversions", "spend"],
                     description="Rolling 7-day ROAS", fmt="dec")
    def _roas_d7(df):
        rev = (df["conversions"] * 50.0).rolling(7, min_periods=1).sum()
        sp = df["spend"].rolling(7, min_periods=1).sum()
        return rev / sp.replace(0, _SAFE_DIV)

    @engine.register("roas_d30", "30-Day ROAS", "efficiency", 1,
                     "rolling_30d_revenue / rolling_30d_spend", ["conversions", "spend"],
                     description="Rolling 30-day ROAS", fmt="dec")
    def _roas_d30(df):
        rev = (df["conversions"] * 50.0).rolling(30, min_periods=1).sum()
        sp = df["spend"].rolling(30, min_periods=1).sum()
        return rev / sp.replace(0, _SAFE_DIV)

    @engine.register("blended_roas", "Blended ROAS", "efficiency", 1,
                     "total_revenue / total_spend", ["conversions", "spend"],
                     description="Overall blended ROAS", fmt="dec")
    def _blended_roas(df):
        total_rev = (df["conversions"] * 50.0).sum()
        total_sp = df["spend"].sum()
        return np.full(len(df), total_rev / max(total_sp, _SAFE_DIV))

    @engine.register("cost_per_save", "Cost Per Save", "cost", 1,
                     "spend / (likes + shares)", ["spend", "likes", "shares"], fmt="cur")
    def _cost_per_save(df):
        saves = df["likes"] + df["shares"]
        return df["spend"] / saves.replace(0, _SAFE_DIV)
