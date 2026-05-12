"""Singleton reactive state manager with cascade resets, pub/sub, and history."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from collections import deque
from typing import Any, Callable

import streamlit as st

_SCHEMA: dict[str, tuple[type, Any]] = {
    "_current_page": (str, "Dashboard"),
    "selected_account": ((str, type(None)), None),
    "selected_campaign": ((str, type(None)), None),
    "selected_adset": ((str, type(None)), None),
    "selected_ad": ((str, type(None)), None),
    "date_range": (tuple, (7, 0)),
    "comparison_period": (bool, False),
    "theme": (str, "dark"),
    "data_version": ((str, type(None)), None),
    "extraction_status": (str, "IDLE"),
    "active_df_name": ((str, type(None)), None),
    "alerts_enabled": (bool, True),
    "export_format": (str, "xlsx"),
    "last_refresh_ts": ((float, type(None)), None),
    "rate_limit_remaining": ((int, type(None)), None),
    "rate_limit_reset_at": ((float, type(None)), None),
    "alerts": (list, []),
    "toast_message": ((str, type(None)), None),
    "toast_severity": (str, "info"),
    "language": (str, "en"),
}

_CASCADE_RESETS: dict[str, list[str]] = {
    "selected_account": ["selected_campaign", "selected_adset", "selected_ad"],
    "selected_campaign": ["selected_adset", "selected_ad"],
    "selected_adset": ["selected_ad"],
}

_MAX_HISTORY = 50


class StateManager:
    """Singleton state manager backed by st.session_state."""

    _instance: StateManager | None = None

    def __new__(cls) -> StateManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _ensure_init(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._subscribers: dict[str, list[tuple[str, Callable]]] = {}
        self._history: deque[dict] = deque(maxlen=_MAX_HISTORY)
        for key, (_, default) in _SCHEMA.items():
            if key not in st.session_state:
                st.session_state[key] = default if not isinstance(default, list) else list(default)

    def get(self, key: str, default: Any = None) -> Any:
        self._ensure_init()
        if key in st.session_state:
            return st.session_state[key]
        schema_entry = _SCHEMA.get(key)
        if schema_entry:
            return schema_entry[1]
        return default

    def set(self, key: str, value: Any, source: str = "user") -> None:
        self._ensure_init()
        old = st.session_state.get(key)
        st.session_state[key] = value
        self._history.append({
            "key": key,
            "old": old,
            "new": value,
            "source": source,
            "ts": time.time(),
        })
        if key in _CASCADE_RESETS:
            for child in _CASCADE_RESETS[key]:
                schema_entry = _SCHEMA.get(child)
                child_default = schema_entry[1] if schema_entry else None
                st.session_state[child] = child_default
        for _, cb in self._subscribers.get(key, []):
            try:
                cb(key, value)
            except Exception:
                pass

    def subscribe(self, key: str, callback: Callable) -> str:
        self._ensure_init()
        sub_id = str(uuid.uuid4())
        self._subscribers.setdefault(key, []).append((sub_id, callback))
        return sub_id

    def unsubscribe(self, sub_id: str) -> None:
        self._ensure_init()
        for key in self._subscribers:
            self._subscribers[key] = [
                (sid, cb) for sid, cb in self._subscribers[key] if sid != sub_id
            ]

    def snapshot(self) -> dict[str, Any]:
        self._ensure_init()
        return {k: st.session_state.get(k, v[1]) for k, v in _SCHEMA.items()}

    def get_state_hash(self) -> str:
        snap = self.snapshot()
        return hashlib.md5(json.dumps(snap, sort_keys=True, default=str).encode()).hexdigest()

    def reset(self) -> None:
        self._ensure_init()
        for key, (_, default) in _SCHEMA.items():
            st.session_state[key] = default if not isinstance(default, list) else list(default)
        self._history.clear()

    def get_history(self) -> list[dict]:
        self._ensure_init()
        return list(self._history)
