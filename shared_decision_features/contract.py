"""Slim feature contract shared between training and live.

Locked contract (do not edit without retraining):

* 12 preflop features, 13 street features for flop/turn/river.
* One model per street: preflop, flop, turn, river.
* No position, raw pot, live action flags, EV/source features or action-history
  counters in the model input.
"""
from __future__ import annotations

# ---- Target labels and stages ----

LABELS = ("NO_INVEST", "CALL", "RAISE")
SPLITS = ("train", "validation", "test")
STAGES = ("PREFLOP", "FLOP", "TURN", "RIVER")
STAGE_NAMES = ("preflop", "flop", "turn", "river")

# ---- Slim feature lists (locked) ----

PREFLOP_FEATURES = (
    "features.to_call_bb",
    "features.effective_stack_bb",
    "features.players_active",
    "features.equity_win",
    "features.equity_win_present",
    "features.call_max_bb",
    "features.call_margin_bb",
    "features.pot_certain_bb",
    "features.pot_probable_bb",
    "features.pot_probable_margin_bb",
    "features.ev_certain_bb",
    "features.ev_probable_bb",
)

STREET_FEATURES = (
    "features.to_call_bb",
    "features.effective_stack_bb",
    "features.players_active",
    "features.equity_win",
    "features.equity_win_present",
    "features.call_max_bb",
    "features.call_margin_bb",
    "features.pot_certain_bb",
    "features.pot_probable_bb",
    "features.pot_probable_margin_bb",
    "features.ev_certain_bb",
    "features.ev_probable_bb",
    "features.bet_size_bb",
)

FLOP_FEATURES = STREET_FEATURES
TURN_FEATURES = STREET_FEATURES
RIVER_FEATURES = STREET_FEATURES
POSTFLOP_FEATURES = STREET_FEATURES

FEATURES_BY_STAGE = {
    "preflop": PREFLOP_FEATURES,
    "flop": FLOP_FEATURES,
    "turn": TURN_FEATURES,
    "river": RIVER_FEATURES,
}

CATEGORICAL_BY_STAGE = {
    "preflop": (),
    "flop": (),
    "turn": (),
    "river": (),
}

# ---- Forbidden columns in X (no leakage / no raw text / no labels) ----

FORBIDDEN_MODEL_COLUMNS = frozenset(
    {
        "source_dataset",
        "source_row_id",
        "hand_id",
        "split",
        "stage_group",
        "label_3intent",
        "bootstrap_label",
        "raw_action",
        "normalized_action_4class",
        "raw_prompt",
        "raw_response",
        "raw_instruction",
        "raw_output",
        "raw_chosen",
        "raw_rejected",
    }
)

# ---- Live / training critical features (must never be missing) ----

CRITICAL_FEATURES = (
    "features.equity_win",
    "features.equity_win_present",
    "features.call_max_bb",
    "features.call_margin_bb",
    "features.players_active",
    "features.pot_certain_bb",
    "features.pot_probable_bb",
    "features.pot_probable_margin_bb",
    "features.ev_certain_bb",
    "features.ev_probable_bb",
)

# ---- Schemas ----

EXPECTED_SCHEMA = "merged_oracle_3intent_v3_slim"
BUNDLE_SCHEMA = "v3_slim_model_export_bundle"

# ---- Rich columns that must NOT enter the slim model ----

RICH_FORBIDDEN_FEATURES = frozenset(
    {
        "features.equity_1v1",
        "features.equity_required",
        "features.equity_gap",
        "features.ev",
        "features.hero_position",
        "features.pot_bb",
        "features.has_check",
        "features.has_fold",
        "features.has_call",
        "features.has_raise",
        "features.can_check",
        "features.can_call",
        "features.can_raise",
        "features.actors_before_hero",
        "features.actors_after_hero",
        "features.num_players",
        "features.num_bets",
        "features.prior_bet_raise_count",
        "features.prior_fold_count",
        "features.hero_stack_bb",
        "features.call_ev_bb",
        "features.source_ev_bb",
        "features.stack_to_pot_ratio",
        "features.to_call_pot_ratio",
        "features.board_card_count",
        "features.action_count",
        "features.prior_check_count",
        "features.prior_call_count",
    }
)

# ---- Feature formulas (documentation + smoke test) ----

FEATURE_FORMULAS = {
    "features.to_call_bb": "to_call / big_blind; 0.0 for a free check.",
    "features.effective_stack_bb": "min(hero_stack, max(active_villain_stacks)) / big_blind; folded players excluded.",
    "features.players_active": "current players still in pot, hero included; live = active_opponents + 1 (fallback).",
    "features.bet_size_bb": "Available/source bet size in BB. In live, derived from to_call or raise buttons; in train, mapped from features.bet_size_bb.",
    "features.equity_win": "Single model equity against active opponents; in live = DecisionInput.equity.",
    "features.equity_win_present": "Conservative win equity adjusted to players present at the table; equals equity_win when present count is unknown or equal to active count.",
    "features.call_max_bb": "Maximum profitable call in big blinds. In live = call_max / big_blind.",
    "features.call_margin_bb": "call_max_bb - to_call_bb.",
    "features.pot_certain_bb": "Guaranteed pot in BB if hero continues now: current pot_bb + to_call_bb.",
    "features.pot_probable_bb": "Probable pot in BB if hero continues and remaining active players match the same minimum contribution; actors are internal only, not model inputs.",
    "features.pot_probable_margin_bb": "pot_probable_bb - to_call_bb; probable reward remaining after the amount hero must add.",
    "features.ev_certain_bb": "Net equity value in BB on the guaranteed pot: equity_win * pot_certain_bb - to_call_bb.",
    "features.ev_probable_bb": "Net equity value in BB on the probable pot: equity_win * pot_probable_bb - to_call_bb.",
}


def validate_stage_features(stage: str) -> tuple[str, ...]:
    """Return the slim feature tuple for ``stage`` (raises on unknown stage)."""
    if stage not in FEATURES_BY_STAGE:
        raise ValueError(f"unknown_stage:{stage}")
    return FEATURES_BY_STAGE[stage]
