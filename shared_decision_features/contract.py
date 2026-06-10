"""Slim feature contract shared between training and live.

Locked contract (do not edit without retraining):

* 11 preflop features, 12 street features for flop/turn/river.
* One model per street: preflop, flop, turn, river.
* No EV/source features and no action-history counters in the model input.
"""
from __future__ import annotations

# ---- Target labels and stages ----

LABELS = ("NO_INVEST", "CALL", "RAISE")
SPLITS = ("train", "validation", "test")
STAGES = ("PREFLOP", "FLOP", "TURN", "RIVER")
STAGE_NAMES = ("preflop", "flop", "turn", "river")

# ---- Slim feature lists (locked) ----

PREFLOP_FEATURES = (
    "features.hero_position",
    "features.pot_bb",
    "features.to_call_bb",
    "features.effective_stack_bb",
    "features.can_check",
    "features.can_call",
    "features.can_raise",
    "features.players_active",
    "features.equity_win",
    "features.call_max_bb",
    "features.call_margin_bb",
)

STREET_FEATURES = (
    "features.hero_position",
    "features.pot_bb",
    "features.to_call_bb",
    "features.effective_stack_bb",
    "features.can_check",
    "features.can_call",
    "features.can_raise",
    "features.players_active",
    "features.equity_win",
    "features.call_max_bb",
    "features.call_margin_bb",
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
    "preflop": ("features.hero_position",),
    "flop": ("features.hero_position",),
    "turn": ("features.hero_position",),
    "river": ("features.hero_position",),
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
    "features.call_max_bb",
    "features.call_margin_bb",
    "features.players_active",
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
        "features.has_check",
        "features.has_fold",
        "features.has_call",
        "features.has_raise",
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
    "features.hero_position": "Normalized hero position: SB, BB, BTN, CO, MP, UTG, else UNKNOWN.",
    "features.pot_bb": "pot / big_blind.",
    "features.to_call_bb": "to_call / big_blind; 0.0 for a free check.",
    "features.effective_stack_bb": "min(hero_stack, max(active_villain_stacks)) / big_blind; folded players excluded.",
    "features.can_check": "1 if check is currently legal, else 0.",
    "features.can_call": "1 if call is legal and to_call_bb > 0, else 0.",
    "features.can_raise": "1 if bet/raise/all-in is legal, else 0.",
    "features.players_active": "current players still in pot, hero included; live = active_opponents + 1 (fallback).",
    "features.bet_size_bb": "Available/source bet size in BB. In live, derived from to_call or raise buttons; in train, mapped from features.bet_size_bb.",
    "features.equity_win": "Single model equity against active opponents; in live = DecisionInput.equity.",
    "features.call_max_bb": "Maximum profitable call in big blinds. In live = call_max / big_blind.",
    "features.call_margin_bb": "call_max_bb - to_call_bb.",
}


def validate_stage_features(stage: str) -> tuple[str, ...]:
    """Return the slim feature tuple for ``stage`` (raises on unknown stage)."""
    if stage not in FEATURES_BY_STAGE:
        raise ValueError(f"unknown_stage:{stage}")
    return FEATURES_BY_STAGE[stage]
