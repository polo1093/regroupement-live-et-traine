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
    pot_bb = _numeric(df, "features.pot_bb")
    to_call_bb = _numeric(df, "features.to_call_bb")
    players_active = _numeric(df, "features.num_players")
    players_present = _players_present(df, players_active)
    out["features.to_call_bb"] = _numeric(df, "features.to_call_bb")
    out["features.effective_stack_bb"] = _numeric(df, "features.effective_stack_bb")
    out["features.players_active"] = players_active
    out["features.bet_size_bb"] = _numeric(df, "features.bet_size_bb")
    out["features.equity_win"] = _equity_win(df)
    out["features.equity_win_present"] = _equity_win_present(out["features.equity_win"], players_active, players_present)
    out["features.call_max_bb"] = _numeric(df, "features.call_max_bb")
    out["features.call_margin_bb"] = out["features.call_max_bb"] - out["features.to_call_bb"]
    pot_features = _pot_certainty_features(
        pot_bb=pot_bb,
        to_call_bb=to_call_bb,
        players_active=players_active,
        actors_after_hero=_numeric(df, "features.actors_after_hero"),
    )
    out["features.pot_certain_bb"] = pot_features["features.pot_certain_bb"]
    out["features.pot_probable_bb"] = pot_features["features.pot_probable_bb"]
    out["features.pot_probable_margin_bb"] = pot_features["features.pot_probable_margin_bb"]
    out["features.ev_certain_bb"] = out["features.equity_win"] * out["features.pot_certain_bb"] - out["features.to_call_bb"]
    out["features.ev_probable_bb"] = out["features.equity_win"] * out["features.pot_probable_bb"] - out["features.to_call_bb"]
    return _coerce_slim_frame(out)


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        return pd.Series([pd.NA] * len(frame), index=frame.index, dtype="Float64")
    return pd.to_numeric(frame[column], errors="coerce")


def _equity_win(frame: pd.DataFrame) -> pd.Series:
    for column in ("features.equity_global", "features.equity_table", "features.equity_win"):
        if column in frame:
            values = _numeric(frame, column)
            if values.notna().any():
                return values
    return pd.Series([pd.NA] * len(frame), index=frame.index, dtype="Float64")


def _players_present(frame: pd.DataFrame, players_active: pd.Series) -> pd.Series:
    for column in (
        "features.players_present",
        "features.player_present",
        "features.player_start",
        "features.num_players_present",
        "features.num_players_start",
    ):
        if column in frame:
            values = _numeric(frame, column)
            if values.notna().any():
                return values
    return players_active


def _equity_win_present(equity: pd.Series, players_active: pd.Series, players_present: pd.Series) -> pd.Series:
    active_opponents = (pd.to_numeric(players_active, errors="coerce") - 1.0).clip(lower=1.0)
    present_opponents = (pd.to_numeric(players_present, errors="coerce") - 1.0).clip(lower=1.0)
    ratio = (present_opponents / active_opponents).clip(lower=1.0)
    values = pd.to_numeric(equity, errors="coerce").clip(lower=0.0, upper=1.0)
    return values.pow(ratio)


def _pot_certainty_features(
    *,
    pot_bb: pd.Series,
    to_call_bb: pd.Series,
    players_active: pd.Series,
    actors_after_hero: pd.Series,
) -> pd.DataFrame:
    pot = pd.to_numeric(pot_bb, errors="coerce")
    to_call = pd.to_numeric(to_call_bb, errors="coerce").clip(lower=0.0)
    players_after = pd.to_numeric(actors_after_hero, errors="coerce")
    fallback_after = (pd.to_numeric(players_active, errors="coerce") - 1.0).clip(lower=0.0)
    players_after = players_after.fillna(fallback_after).clip(lower=0.0)

    certain = pot + to_call
    probable = certain + players_after * to_call
    return pd.DataFrame(
        {
            "features.pot_certain_bb": certain,
            "features.pot_probable_bb": probable,
            "features.pot_probable_margin_bb": probable - to_call,
        },
        index=pot_bb.index,
    )


def _coerce_slim_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["metadata.street"] = out["metadata.street"].fillna("UNKNOWN").astype(str).str.upper()
    out["label_3intent"] = out["label_3intent"].fillna("").astype(str).str.upper()
    numeric_features = set().union(*FEATURES_BY_STAGE.values())
    for feature in numeric_features:
        out[feature] = pd.to_numeric(out[feature], errors="coerce")
    return out
