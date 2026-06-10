"""Build the slim training frame from a rich V3 dataset.

This builder is the single source of truth used by the V3 slim training
pipeline. It maps the rich V3 columns onto the slim contract and must
stay in sync with ``live_builder.build_slim_features_from_decision_input``.
"""
from __future__ import annotations

import pandas as pd

from shared_decision_features.contract import FEATURES_BY_STAGE


def build_slim_frame_from_rich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Map a rich V3 DataFrame to the slim feature set.

    The returned frame contains the bookkeeping columns
    (``source_dataset``, ``source_row_id``, ``hand_id``, ``stage_group``,
    ``split``, ``label_3intent``) plus all equity-core slim features.
    Categorical columns are uppercased; numeric columns are coerced.
    """
    out = pd.DataFrame()
    out["source_dataset"] = df.get("source_dataset")
    out["source_row_id"] = df.get("source_row_id")
    out["hand_id"] = df.get("hand_id")
    out["stage_group"] = df.get("stage_group")
    out["split"] = df.get("split")
    out["label_3intent"] = df.get("label_3intent")
    out["metadata.street"] = df.get("metadata.street", "UNKNOWN")
    out["features.hero_position"] = df.get("features.hero_position", "UNKNOWN")
    out["features.pot_bb"] = _numeric(df, "features.pot_bb")
    out["features.to_call_bb"] = _numeric(df, "features.to_call_bb")
    out["features.effective_stack_bb"] = _numeric(df, "features.effective_stack_bb")
    out["features.can_check"] = _numeric(df, "features.has_check")
    out["features.can_call"] = (
        (_numeric(df, "features.has_call") > 0) & (_numeric(df, "features.to_call_bb") > 0)
    ).astype(float)
    out["features.can_raise"] = _numeric(df, "features.has_raise")
    out["features.players_active"] = _numeric(df, "features.num_players")
    out["features.bet_size_bb"] = _numeric(df, "features.bet_size_bb")
    out["features.equity_win"] = _numeric(df, "features.equity_global")
    out["features.call_max_bb"] = _numeric(df, "features.call_max_bb")
    out["features.call_margin_bb"] = out["features.call_max_bb"] - out["features.to_call_bb"]
    return _coerce_slim_frame(out)


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        return pd.Series([pd.NA] * len(frame), index=frame.index, dtype="Float64")
    return pd.to_numeric(frame[column], errors="coerce")


def _coerce_slim_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["metadata.street"] = out["metadata.street"].fillna("UNKNOWN").astype(str).str.upper()
    out["features.hero_position"] = out["features.hero_position"].fillna("UNKNOWN").astype(str).str.upper()
    out["label_3intent"] = out["label_3intent"].fillna("").astype(str).str.upper()
    numeric_features = set().union(*FEATURES_BY_STAGE.values()) - {"features.hero_position"}
    for feature in numeric_features:
        out[feature] = pd.to_numeric(out[feature], errors="coerce")
    return out
