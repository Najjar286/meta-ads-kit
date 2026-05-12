"""Statistical demo data generator — 2 accounts, 5 campaigns, 7 adsets, 12 ads, 60 days."""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

_ACCOUNTS = [
    {"account_id": "act_001", "account_name": "Hoot Pharma Global"},
    {"account_id": "act_002", "account_name": "Hoot Pharma EU"},
]

_CAMPAIGNS = [
    {"campaign_id": "camp_001", "campaign_name": "Brand Awareness", "account_id": "act_001", "objective": "BRAND_AWARENESS"},
    {"campaign_id": "camp_002", "campaign_name": "Retargeting", "account_id": "act_001", "objective": "CONVERSIONS"},
    {"campaign_id": "camp_003", "campaign_name": "Conversion", "account_id": "act_001", "objective": "CONVERSIONS"},
    {"campaign_id": "camp_004", "campaign_name": "Video Engagement", "account_id": "act_002", "objective": "VIDEO_VIEWS"},
    {"campaign_id": "camp_005", "campaign_name": "Lead Gen", "account_id": "act_002", "objective": "LEAD_GENERATION"},
]

_ADSETS = [
    {"adset_id": "as_001", "adset_name": "Broad Audience", "campaign_id": "camp_001"},
    {"adset_id": "as_002", "adset_name": "Lookalike 1%", "campaign_id": "camp_002"},
    {"adset_id": "as_003", "adset_name": "Retarget Visitors", "campaign_id": "camp_002"},
    {"adset_id": "as_004", "adset_name": "Prospecting", "campaign_id": "camp_003"},
    {"adset_id": "as_005", "adset_name": "Remarketing", "campaign_id": "camp_004"},
    {"adset_id": "as_006", "adset_name": "Mobile Users", "campaign_id": "camp_005"},
    {"adset_id": "as_007", "adset_name": "Desktop Users", "campaign_id": "camp_005"},
]

_ADS = [
    {"ad_id": "ad_001", "ad_name": "IMG_Hero_Banner_v1", "adset_id": "as_001"},
    {"ad_id": "ad_002", "ad_name": "VID_Product_Showcase", "adset_id": "as_001"},
    {"ad_id": "ad_003", "ad_name": "CAR_Feature_Carousel", "adset_id": "as_002"},
    {"ad_id": "ad_004", "ad_name": "IMG_Social_Proof", "adset_id": "as_003"},
    {"ad_id": "ad_005", "ad_name": "VID_Testimonial", "adset_id": "as_003"},
    {"ad_id": "ad_006", "ad_name": "IMG_NewProduct_Launch", "adset_id": "as_004"},
    {"ad_id": "ad_007", "ad_name": "CAR_Product_Compare", "adset_id": "as_004"},
    {"ad_id": "ad_008", "ad_name": "IMG_Retarget_Offer", "adset_id": "as_005"},
    {"ad_id": "ad_009", "ad_name": "VID_Brand_Story", "adset_id": "as_005"},
    {"ad_id": "ad_010", "ad_name": "VID_Quick_Demo", "adset_id": "as_006"},
    {"ad_id": "ad_011", "ad_name": "IMG_Static_Ad", "adset_id": "as_006"},
    {"ad_id": "ad_012", "ad_name": "CAR_Multi_Product", "adset_id": "as_007"},
]

_ADSET_TO_CAMPAIGN: dict[str, str] = {a["adset_id"]: a["campaign_id"] for a in _ADSETS}
_CAMPAIGN_TO_ACCOUNT: dict[str, str] = {c["campaign_id"]: c["account_id"] for c in _CAMPAIGNS}
_CAMPAIGN_NAMES: dict[str, str] = {c["campaign_id"]: c["campaign_name"] for c in _CAMPAIGNS}
_ADSET_NAMES: dict[str, str] = {a["adset_id"]: a["adset_name"] for a in _ADSETS}
_ACCOUNT_NAMES: dict[str, str] = {a["account_id"]: a["account_name"] for a in _ACCOUNTS}
_CAMPAIGN_OBJ: dict[str, str] = {c["campaign_id"]: c["objective"] for c in _CAMPAIGNS}
_QUALITY_RANKS = ["ABOVE_AVERAGE", "AVERAGE", "BELOW_AVERAGE"]


def generate_entities() -> dict[str, list[dict]]:
    return {
        "accounts": list(_ACCOUNTS),
        "campaigns": list(_CAMPAIGNS),
        "adsets": list(_ADSETS),
        "ads": list(_ADS),
    }


def generate_insights(days: int = 60, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)
    rows: list[dict] = []

    for ad in _ADS:
        adset_id = ad["adset_id"]
        campaign_id = _ADSET_TO_CAMPAIGN[adset_id]
        account_id = _CAMPAIGN_TO_ACCOUNT[campaign_id]
        base_spend = rng.uniform(20, 200)
        base_impressions = rng.integers(1000, 50000)
        base_ctr = rng.uniform(0.5, 4.0)

        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            dow = date.weekday()
            day_factor = 1.0 + 0.3 * np.sin(2 * np.pi * dow / 7)
            noise = rng.normal(1.0, 0.15)
            factor = max(0.2, day_factor * noise)

            impressions = int(base_impressions * factor)
            clicks = max(1, int(impressions * base_ctr / 100 * rng.normal(1.0, 0.1)))
            spend = round(base_spend * factor * rng.normal(1.0, 0.1), 2)
            reach = int(impressions * rng.uniform(0.6, 0.95))
            frequency = round(impressions / max(reach, 1), 2)
            ctr = round(clicks / max(impressions, 1) * 100, 4)
            cpc = round(spend / max(clicks, 1), 2)
            cpm = round(spend / max(impressions, 1) * 1000, 2)
            conversions = max(0, int(clicks * rng.uniform(0.02, 0.15)))
            cost_per_conv = round(spend / max(conversions, 1), 2)
            total_engagement = clicks + int(rng.integers(0, 50))
            likes = int(rng.integers(0, 30))
            comments = int(rng.integers(0, 10))
            shares = int(rng.integers(0, 8))
            unique_clicks = max(1, int(clicks * rng.uniform(0.7, 0.95)))
            unique_ctr = round(unique_clicks / max(impressions, 1) * 100, 4)
            video_plays = int(rng.integers(0, impressions // 2)) if "VID" in ad["ad_name"] else 0
            video_thruplays = int(video_plays * rng.uniform(0.3, 0.7)) if video_plays else 0
            video_p25 = int(video_plays * rng.uniform(0.6, 0.9)) if video_plays else 0
            video_p50 = int(video_plays * rng.uniform(0.4, 0.7)) if video_plays else 0
            video_p75 = int(video_plays * rng.uniform(0.2, 0.5)) if video_plays else 0
            video_p95 = int(video_plays * rng.uniform(0.05, 0.2)) if video_plays else 0
            daily_budget = round(base_spend * 1.5, 2)

            rows.append({
                "account_id": account_id,
                "account_name": _ACCOUNT_NAMES[account_id],
                "campaign_id": campaign_id,
                "campaign_name": _CAMPAIGN_NAMES[campaign_id],
                "adset_id": adset_id,
                "adset_name": _ADSET_NAMES[adset_id],
                "ad_id": ad["ad_id"],
                "ad_name": ad["ad_name"],
                "status": "ACTIVE",
                "objective": _CAMPAIGN_OBJ[campaign_id],
                "daily_budget": daily_budget,
                "date_start": str(date),
                "date_stop": str(date),
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "reach": reach,
                "frequency": frequency,
                "ctr": ctr,
                "cpc": cpc,
                "cpm": cpm,
                "conversions": conversions,
                "cost_per_conv": cost_per_conv,
                "total_engagement": total_engagement,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "unique_clicks": unique_clicks,
                "unique_ctr": unique_ctr,
                "video_plays": video_plays,
                "video_thruplays": video_thruplays,
                "video_p25": video_p25,
                "video_p50": video_p50,
                "video_p75": video_p75,
                "video_p95": video_p95,
                "quality_rank": rng.choice(_QUALITY_RANKS),
                "conv_rate_rank": rng.choice(_QUALITY_RANKS),
            })

    df = pd.DataFrame(rows)
    df["date_start"] = pd.to_datetime(df["date_start"])
    df["date_stop"] = pd.to_datetime(df["date_stop"])
    return df
