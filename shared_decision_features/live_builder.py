"""Build the slim live features from a ``DecisionInput``.

This module converts a ``DecisionInput`` (the live poker state) into the
slim V3 feature dict. The keys and units must match
``shared_decision_features.train_builder.build_slim_frame_from_rich_dataset``
exactly, otherwise the live bundle will predict on the wrong schema.
"""
from __future__ import annotations

from typing import Any, Optional

from shared_decision_features.contract import (
    FEATURES_BY_STAGE,
)


class SlimLiveBuildError(ValueError):
    """Raised when a critical slim feature cannot be computed live."""


def build_slim_features_from_decision_input(state: Any) -> dict[str, Any]:
    """Return a flat dict with all equity-core slim live features.

    The returned dict always contains the union of all street keys. The caller must
    pick the stage-specific feature list according to the
    street, and a missing critical feature raises ``SlimLiveBuildError``
    so the live engine can fall back to the legacy decision path.
    """
    bb = _positive_float(state.big_blind) or _infer_big_blind(state)
    pot = _positive_or_zero(state.pot)
    to_call = _positive_or_zero(state.to_call)
    call_max = _positive_or_zero(state.call_max)
    equity_global = _probability(state.equity)

    pot_bb = _amount_bb(pot, bb)
    to_call_bb = _amount_bb(to_call, bb)
    call_max_bb = _amount_bb(call_max, bb)
    call_margin_bb = None if call_max_bb is None or to_call_bb is None else call_max_bb - to_call_bb
    bet_size = _bet_size(state, to_call=to_call)
    bet_size_bb = _amount_bb(bet_size, bb)
    effective_stack_bb = _amount_bb(_positive_float(state.effective_stack), bb)

    # players_active from DecisionInput
    players_active = _players_active(state)
    players_present = _players_present(state, players_active)
    equity_present = _equity_win_present(equity_global, players_active, players_present)
    pot_certainty = _pot_certainty_features(
        pot_bb=pot_bb,
        to_call_bb=to_call_bb,
        players_active=players_active,
        equity_win=equity_global,
    )
    # Refuse to build a slim row missing any critical feature
    critical = {
        "features.equity_win": equity_global,
        "features.equity_win_present": equity_present,
        "features.call_max_bb": call_max_bb,
        "features.call_margin_bb": call_margin_bb,
        "features.players_active": players_active,
        "features.pot_certain_bb": pot_certainty["features.pot_certain_bb"],
        "features.pot_probable_bb": pot_certainty["features.pot_probable_bb"],
        "features.pot_probable_margin_bb": pot_certainty["features.pot_probable_margin_bb"],
        "features.ev_certain_bb": pot_certainty["features.ev_certain_bb"],
        "features.ev_probable_bb": pot_certainty["features.ev_probable_bb"],
    }
    missing = [name for name, value in critical.items() if value is None]
    if missing:
        raise SlimLiveBuildError(f"slim_live_critical_missing:{','.join(missing)}")

    return {
        "features.to_call_bb": to_call_bb,
        "features.effective_stack_bb": effective_stack_bb,
        "features.players_active": players_active,
        "features.bet_size_bb": bet_size_bb,
        "features.equity_win": equity_global,
        "features.equity_win_present": equity_present,
        "features.call_max_bb": call_max_bb,
        "features.call_margin_bb": call_margin_bb,
        **pot_certainty,
    }


def live_features_for_stage(features: dict[str, Any], stage: str) -> dict[str, Any]:
    """Pick the slim columns expected for the given stage."""
    if stage not in FEATURES_BY_STAGE:
        raise SlimLiveBuildError(f"unknown_stage:{stage}")
    wanted = FEATURES_BY_STAGE[stage]
    return {name: features.get(name) for name in wanted}


# ---- helpers ----


def _street(state: Any) -> str:
    return str(state.street or "").upper()


def _infer_big_blind(state: Any) -> Optional[float]:
    to_call = _positive_float(state.to_call)
    if _street(state) == "PREFLOP" and to_call is not None:
        return to_call
    positive_button_values = [
        value
        for button in state.buttons
        for value in [_positive_float(button.value)]
        if value is not None
    ]
    if _street(state) == "PREFLOP" and positive_button_values:
        return min(positive_button_values)
    return None


def _bet_size(state: Any, *, to_call: Optional[float]) -> Optional[float]:
    if to_call is not None and to_call > 0:
        return to_call
    values = [
        value
        for button in state.buttons
        if str(button.state or "").lower() in {"mise", "relance", "raise", "all-in"}
        for value in [_positive_float(button.value)]
        if value is not None
    ]
    return min(values) if values else 0.0


def _players_active(state: Any) -> Optional[int]:
    if state.active_opponents is not None:
        return max(1, int(state.active_opponents) + 1)
    if state.player_count is not None:
        return int(state.player_count)
    return None


def _players_present(state: Any, players_active: Optional[int]) -> Optional[int]:
    if state.player_count is not None:
        return int(state.player_count)
    return players_active


def _equity_win_present(
    equity: Optional[float],
    players_active: Optional[int],
    players_present: Optional[int],
) -> Optional[float]:
    if equity is None:
        return None
    active_opponents = max((players_active or 1) - 1, 1)
    present_opponents = max((players_present or players_active or 1) - 1, active_opponents)
    ratio = present_opponents / active_opponents
    return max(0.0, min(1.0, equity)) ** ratio


def _pot_certainty_features(
    *,
    pot_bb: Optional[float],
    to_call_bb: Optional[float],
    players_active: Optional[int],
    equity_win: Optional[float],
) -> dict[str, Optional[float]]:
    if pot_bb is None or to_call_bb is None or equity_win is None:
        return {
            "features.pot_certain_bb": None,
            "features.pot_probable_bb": None,
            "features.pot_probable_margin_bb": None,
            "features.ev_certain_bb": None,
            "features.ev_probable_bb": None,
        }
    players_after = max((players_active or 1) - 1, 0)
    pot_certain_bb = pot_bb + max(to_call_bb, 0.0)
    pot_probable_bb = pot_certain_bb + players_after * max(to_call_bb, 0.0)
    equity = max(0.0, min(1.0, equity_win))
    return {
        "features.pot_certain_bb": pot_certain_bb,
        "features.pot_probable_bb": pot_probable_bb,
        "features.pot_probable_margin_bb": pot_probable_bb - max(to_call_bb, 0.0),
        "features.ev_certain_bb": equity * pot_certain_bb - max(to_call_bb, 0.0),
        "features.ev_probable_bb": equity * pot_probable_bb - max(to_call_bb, 0.0),
    }


def _amount_bb(value: Optional[float], bb: Optional[float]) -> Optional[float]:
    if value is None or bb is None or bb <= 0:
        return None
    return value / bb


def _positive_or_zero(value: Any) -> Optional[float]:
    number = _positive_or_negative(value)
    if number is None or number < 0:
        return None
    return number


def _positive_float(value: Any) -> Optional[float]:
    number = _positive_or_negative(value)
    if number is None or number <= 0:
        return None
    return number


def _positive_or_negative(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _probability(value: Any) -> Optional[float]:
    number = _positive_or_negative(value)
    if number is None or number < 0.0 or number > 1.0:
        return None
    return number
