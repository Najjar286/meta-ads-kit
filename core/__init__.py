"""Core modules: state management, entity cascade, demo data, data pipeline, schema validation."""
from __future__ import annotations

from core.state_manager import StateManager
from core.entity_cascade import EntityCascade
from core.demo_data import generate_insights, generate_entities
from core.data_pipeline import DataPipeline
from core.schema_validator import SchemaValidator

__all__ = [
    "StateManager",
    "EntityCascade",
    "generate_insights",
    "generate_entities",
    "DataPipeline",
    "SchemaValidator",
]
