"""Engine modules: metric computation, analytics, alerts, export, scheduling."""
from __future__ import annotations

from engines.metric_engine import MetricEngine, MetricDef
from engines.analytics_engine import AnalyticsEngine
from engines.alert_engine import AlertEngine, AlertResult, RuleDef
from engines.export_engine import ExportEngine
from engines.scheduler import Scheduler
from engines.metrics_registry import register_standard_metrics
from engines.metrics_axiom import register_axiom_metrics
from engines.metrics_archon import register_archon_metrics
from engines.metrics_composite import register_composite_metrics


def create_metric_engine() -> MetricEngine:
    """Create and configure a MetricEngine with all 220+ registered metrics."""
    engine = MetricEngine()
    register_standard_metrics(engine)
    register_axiom_metrics(engine)
    register_archon_metrics(engine)
    register_composite_metrics(engine)
    return engine


__all__ = [
    "MetricEngine", "MetricDef",
    "AnalyticsEngine",
    "AlertEngine", "AlertResult", "RuleDef",
    "ExportEngine",
    "Scheduler",
    "create_metric_engine",
]
