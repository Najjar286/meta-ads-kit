"""Entity cascade: Account → Campaign → AdSet → Ad hierarchy with filtering."""
from __future__ import annotations

from typing import Any

import pandas as pd

from core.state_manager import StateManager

_STATE_KEY_MAP = {
    "account": "selected_account",
    "campaign": "selected_campaign",
    "adset": "selected_adset",
    "ad": "selected_ad",
}
_COLUMN_MAP = {
    "account": "account_id",
    "campaign": "campaign_id",
    "adset": "adset_id",
    "ad": "ad_id",
}


class EntityCascade:
    """Manages entity hierarchy and cascaded filtering."""

    def __init__(self) -> None:
        self._entity_tree: dict[str, list[dict]] = {
            "accounts": [],
            "campaigns": [],
            "adsets": [],
            "ads": [],
        }

    def load_from_entities(
        self,
        accounts: list[dict],
        campaigns: list[dict],
        adsets: list[dict],
        ads: list[dict],
    ) -> None:
        self._entity_tree["accounts"] = accounts
        self._entity_tree["campaigns"] = campaigns
        self._entity_tree["adsets"] = adsets
        self._entity_tree["ads"] = ads

    def load_from_dataframe(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return
        if "account_id" in df.columns:
            accts = df[["account_id", "account_name"]].drop_duplicates().to_dict("records")
            self._entity_tree["accounts"] = accts
        if "campaign_id" in df.columns:
            cols = [c for c in ["campaign_id", "campaign_name", "account_id", "objective"] if c in df.columns]
            self._entity_tree["campaigns"] = df[cols].drop_duplicates().to_dict("records")
        if "adset_id" in df.columns:
            cols = [c for c in ["adset_id", "adset_name", "campaign_id"] if c in df.columns]
            self._entity_tree["adsets"] = df[cols].drop_duplicates().to_dict("records")
        if "ad_id" in df.columns:
            cols = [c for c in ["ad_id", "ad_name", "adset_id"] if c in df.columns]
            self._entity_tree["ads"] = df[cols].drop_duplicates().to_dict("records")

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return df
        state = StateManager()
        result = df.copy()
        for level in ["account", "campaign", "adset", "ad"]:
            selected = state.get(_STATE_KEY_MAP[level])
            col = _COLUMN_MAP[level]
            if selected and col in result.columns:
                result = result[result[col] == selected]
        return result

    def apply_with_index(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return df
        state = StateManager()
        mask = pd.Series(True, index=df.index)
        for level in ["account", "campaign", "adset", "ad"]:
            selected = state.get(_STATE_KEY_MAP[level])
            col = _COLUMN_MAP[level]
            if selected and col in df.columns:
                mask &= df[col] == selected
        return df[mask]

    def search_entities(self, query: str, max_results: int = 20) -> list[dict]:
        if not query:
            return []
        query_lower = query.lower()
        results: list[dict] = []
        for level_key, items in self._entity_tree.items():
            level = level_key.rstrip("s")
            name_key = f"{level}_name"
            id_key = f"{level}_id"
            for item in items:
                name = item.get(name_key, "")
                eid = item.get(id_key, "")
                score = 0
                if query_lower in str(name).lower():
                    score = 10
                elif query_lower in str(eid).lower():
                    score = 5
                if score > 0:
                    results.append({"level": level, "id": eid, "name": name, "score": score})
                    if len(results) >= max_results:
                        return sorted(results, key=lambda x: -x["score"])
        return sorted(results, key=lambda x: -x["score"])

    def get_entity_path(self, entity_id: str) -> list[str]:
        path: list[str] = []
        for level_key in ["accounts", "campaigns", "adsets", "ads"]:
            level = level_key.rstrip("s")
            name_key = f"{level}_name"
            id_key = f"{level}_id"
            for item in self._entity_tree[level_key]:
                if item.get(id_key) == entity_id:
                    path.append(item.get(name_key, entity_id))
        return path

    def get_entity_name(self, entity_id: str, level: str) -> str:
        store_key = f"{level}s"
        name_key = f"{level}_name"
        id_key = f"{level}_id"
        for item in self._entity_tree.get(store_key, []):
            if item.get(id_key) == entity_id:
                return item.get(name_key, entity_id)
        return entity_id

    def get_entity_count(self, level: str) -> int:
        return len(self._entity_tree.get(f"{level}s", []))

    def reset_selection(self) -> None:
        state = StateManager()
        for key in _STATE_KEY_MAP.values():
            state.set(key, None, source="entity_cascade")

    @property
    def campaigns(self) -> list[dict]:
        state = StateManager()
        acct = state.get("selected_account")
        items = self._entity_tree.get("campaigns", [])
        if acct:
            return [c for c in items if c.get("account_id") == acct]
        return items

    @property
    def adsets(self) -> list[dict]:
        state = StateManager()
        camp = state.get("selected_campaign")
        items = self._entity_tree.get("adsets", [])
        if camp:
            return [a for a in items if a.get("campaign_id") == camp]
        return items

    @property
    def ads(self) -> list[dict]:
        state = StateManager()
        adset = state.get("selected_adset")
        items = self._entity_tree.get("ads", [])
        if adset:
            return [a for a in items if a.get("adset_id") == adset]
        return items
