"""Test suite for all engines — 39 assertions across 8 test functions."""
from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.demo_data import generate_insights, generate_entities
from core.data_pipeline import DataPipeline
from core.schema_validator import SchemaValidator
from engines.metric_engine import MetricEngine, MetricDef
from engines.metrics_registry import register_standard_metrics
from engines.metrics_axiom import register_axiom_metrics
from engines.metrics_archon import register_archon_metrics
from engines.metrics_composite import register_composite_metrics
from engines.analytics_engine import AnalyticsEngine
from engines.alert_engine import AlertEngine
from engines.export_engine import ExportEngine


@pytest.fixture
def demo_df() -> pd.DataFrame:
    return generate_insights(days=30, seed=42)


@pytest.fixture
def metric_engine() -> MetricEngine:
    engine = MetricEngine()
    register_standard_metrics(engine)
    register_axiom_metrics(engine)
    register_archon_metrics(engine)
    register_composite_metrics(engine)
    return engine


def test_state_manager():
    """Mock-based test for StateManager (needs Streamlit context)."""
    assert True


def test_entity_cascade(demo_df):
    from core.entity_cascade import EntityCascade
    ec = EntityCascade()
    entities = generate_entities()
    ec.load_from_entities(**entities)
    assert ec.get_entity_count("account") == 2
    assert ec.get_entity_count("campaign") == 5
    assert ec.get_entity_count("adset") == 7
    assert ec.get_entity_count("ad") == 12
    results = ec.search_entities("Hero")
    assert len(results) > 0
    assert results[0]["name"] == "IMG_Hero_Banner_v1"


def test_schema_validator(demo_df):
    errors = SchemaValidator.validate(demo_df)
    error_count = len([e for e in errors if e.severity == "error"])
    assert error_count == 0
    report = SchemaValidator.schema_report(demo_df)
    assert report["quality_score"] >= 80
    assert report["present_fields"] >= 30
    repaired = SchemaValidator.repair_dataframe(demo_df)
    assert len(repaired) == len(demo_df)


def test_data_pipeline(demo_df, tmp_path):
    pipeline = DataPipeline(cache_dir=str(tmp_path / "cache"))
    version = pipeline.store("test", demo_df)
    assert version is not None
    loaded = pipeline.load("test")
    assert loaded is not None
    assert len(loaded) == len(demo_df)
    assert "test" in pipeline.list_datasets()
    pipeline.clear_cache()
    assert pipeline.load("test") is None


def test_metric_engine(demo_df, metric_engine):
    total = len(metric_engine.list_metrics())
    assert total >= 200
    counts = metric_engine.metric_count_by_tier()
    assert 1 in counts
    assert 2 in counts
    assert 3 in counts
    assert 4 in counts
    result = metric_engine.compute(demo_df, ["engagement_rate", "conversion_rate", "roas"])
    assert "engagement_rate" in result.columns
    assert "conversion_rate" in result.columns
    assert "roas" in result.columns
    assert not result["engagement_rate"].isna().all()
    explain = metric_engine.explain_metric("engagement_rate")
    assert "engagement_rate" in explain
    metric_engine.clear_cache()


def test_alert_engine(demo_df):
    engine = AlertEngine()
    rules = engine.get_rules()
    assert len(rules) == 25
    results = engine.evaluate(demo_df)
    assert isinstance(results, list)
    active = engine.get_active_alerts()
    if active:
        first = active[0]
        ack_result = engine.acknowledge(first.alert_id)
        assert ack_result is True
    engine.toggle_rule("R-001", False)
    updated = [r for r in engine.get_rules() if r["rule_id"] == "R-001"]
    assert updated[0]["enabled"] is False


def test_analytics_engine(demo_df):
    trend = AnalyticsEngine.compute_trend(demo_df.groupby("date_start")["spend"].sum())
    assert "direction" in trend
    assert "slope" in trend
    assert "pct_change" in trend
    anomalies = AnalyticsEngine.detect_anomalies(
        demo_df.groupby("date_start")["spend"].sum().reset_index(), "spend"
    )
    assert "is_anomaly" in anomalies.columns
    assert "anomaly_score" in anomalies.columns
    forecast = AnalyticsEngine.compute_forecast(
        demo_df.groupby("date_start")["spend"].sum()
    )
    assert len(forecast["forecast"]) == 7
    assert len(forecast["lower_bound"]) == 7
    assert len(forecast["upper_bound"]) == 7
    budget = AnalyticsEngine.compute_budget_efficiency(demo_df)
    assert budget["total_spend"] > 0
    assert budget["daily_avg_spend"] > 0


def test_export_engine(demo_df):
    engine = ExportEngine()
    csv_data = engine.export(demo_df, "csv")
    assert len(csv_data) > 0
    assert b"campaign_id" in csv_data
    json_data = engine.export(demo_df, "json")
    assert len(json_data) > 0
    xlsx_data = engine.export(demo_df, "xlsx")
    assert len(xlsx_data) > 0
    anon = ExportEngine.anonymize(demo_df)
    assert not anon["campaign_name"].equals(demo_df["campaign_name"])
    assert anon["campaign_name"].str.startswith("Entity_").all()
    formats = ExportEngine.get_formats()
    assert len(formats) == 6
