"""Pure-contract tests for ``shared_decision_features``.

These tests are independent of the train pipeline and the live engine.
They lock the slim feature contract so any silent regression (extra
column, renamed column, leaked rich column) is caught here.
"""
from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

from shared_decision_features import (
    BUNDLE_SCHEMA,
    CRITICAL_FEATURES,
    EXPECTED_SCHEMA,
    FEATURES_BY_STAGE,
    FLOP_FEATURES,
    FORBIDDEN_MODEL_COLUMNS,
    LABELS,
    POSTFLOP_FEATURES,
    PREFLOP_FEATURES,
    RICH_FORBIDDEN_FEATURES,
    RIVER_FEATURES,
    STAGES,
    TURN_FEATURES,
    SlimContractError,
    SlimLiveBuildError,
    build_slim_features_from_decision_input,
    build_slim_frame_from_rich_dataset,
    live_features_for_stage,
    load_bundle_feature_contract,
    validate_bundle_feature_contract,
    validate_no_rich_leak,
    validate_stage_features,
    validate_stage_features_columns,
)


# ---- contract shape ----


def test_preflop_features_count_is_14() -> None:
    assert len(PREFLOP_FEATURES) == 11


def test_street_features_count_is_12() -> None:
    assert len(FLOP_FEATURES) == 12
    assert len(TURN_FEATURES) == 12
    assert len(RIVER_FEATURES) == 12


def test_street_features_extend_preflop_with_bet_size_only() -> None:
    preflop_set = set(PREFLOP_FEATURES)
    street_set = set(FLOP_FEATURES)
    assert preflop_set.issubset(street_set)
    assert street_set - preflop_set == {"features.bet_size_bb"}
    assert FLOP_FEATURES == TURN_FEATURES == RIVER_FEATURES == POSTFLOP_FEATURES


def test_schemas_are_stable() -> None:
    assert EXPECTED_SCHEMA == "merged_oracle_3intent_v3_slim"
    assert BUNDLE_SCHEMA == "v3_slim_model_export_bundle"
    assert STAGES == ("PREFLOP", "FLOP", "TURN", "RIVER")
    assert LABELS == ("NO_INVEST", "CALL", "RAISE")


def test_critical_features_are_in_all_stage_contracts() -> None:
    for stage, features in FEATURES_BY_STAGE.items():
        for feature in CRITICAL_FEATURES:
            assert feature in features, (stage, feature)
    assert "features.source_ev_bb" not in set().union(*FEATURES_BY_STAGE.values())
    assert "features.call_margin_bb" in PREFLOP_FEATURES


def test_no_rich_column_in_slim_lists() -> None:
    slim = set(PREFLOP_FEATURES) | set(POSTFLOP_FEATURES)
    leaks = slim & RICH_FORBIDDEN_FEATURES
    assert leaks == set(), f"rich columns leaked into slim: {leaks}"


def test_forbidden_model_columns_dont_contain_slim() -> None:
    slim = set(PREFLOP_FEATURES) | set(POSTFLOP_FEATURES)
    forbidden_in_slim = slim & FORBIDDEN_MODEL_COLUMNS
    assert forbidden_in_slim == set()


def test_validate_stage_features_columns_accepts_correct_lists() -> None:
    validate_stage_features_columns(list(PREFLOP_FEATURES), stage="preflop")
    validate_stage_features_columns(list(FLOP_FEATURES), stage="flop")
    validate_stage_features_columns(list(TURN_FEATURES), stage="turn")
    validate_stage_features_columns(list(RIVER_FEATURES), stage="river")


def test_validate_stage_features_columns_rejects_wrong_order() -> None:
    with pytest.raises(SlimContractError):
        validate_stage_features_columns(list(reversed(PREFLOP_FEATURES)), stage="preflop")


def test_validate_stage_features_columns_rejects_missing_column() -> None:
    bad = list(PREFLOP_FEATURES) + ["features.extra_column"]
    with pytest.raises(SlimContractError):
        validate_stage_features_columns(bad, stage="preflop")


def test_validate_stage_features_columns_rejects_unknown_stage() -> None:
    with pytest.raises(SlimContractError):
        validate_stage_features_columns(list(PREFLOP_FEATURES), stage="postflop")


def test_validate_no_rich_leak_raises_on_rich_columns() -> None:
    with pytest.raises(SlimContractError):
        validate_no_rich_leak(["features.equity_1v1", "features.has_check"])


def test_validate_no_rich_leak_passes_on_clean_columns() -> None:
    validate_no_rich_leak(list(PREFLOP_FEATURES))


def test_validate_stage_features_utility() -> None:
    assert validate_stage_features("preflop") == PREFLOP_FEATURES
    assert validate_stage_features("flop") == FLOP_FEATURES
    assert validate_stage_features("turn") == TURN_FEATURES
    assert validate_stage_features("river") == RIVER_FEATURES
    with pytest.raises(ValueError):
        validate_stage_features("unknown")


# ---- bundle contract I/O ----


def _write_bundle(bundle_dir, schema: str = EXPECTED_SCHEMA) -> None:
    (bundle_dir / "contracts").mkdir(parents=True, exist_ok=True)
    contract = {
        "schema": schema,
        "features_model_used_by_stage": {
            "preflop": list(PREFLOP_FEATURES),
            "flop": list(FLOP_FEATURES),
            "turn": list(TURN_FEATURES),
            "river": list(RIVER_FEATURES),
        },
        "feature_count_by_stage": {
            "preflop": len(PREFLOP_FEATURES),
            "flop": len(FLOP_FEATURES),
            "turn": len(TURN_FEATURES),
            "river": len(RIVER_FEATURES),
        },
    }
    (bundle_dir / "contracts" / "feature_contract.json").write_text(
        __import__("json").dumps(contract, indent=2), encoding="utf-8"
    )


def test_load_bundle_feature_contract_ok(tmp_path) -> None:
    _write_bundle(tmp_path)
    contract = load_bundle_feature_contract(tmp_path)
    assert contract["schema"] == EXPECTED_SCHEMA


def test_load_bundle_feature_contract_missing(tmp_path) -> None:
    with pytest.raises(SlimContractError):
        load_bundle_feature_contract(tmp_path)


def test_validate_bundle_feature_contract_rejects_wrong_schema(tmp_path) -> None:
    _write_bundle(tmp_path, schema="merged_oracle_3intent_v3_rich")
    with pytest.raises(SlimContractError) as excinfo:
        validate_bundle_feature_contract(tmp_path, stage="preflop")
    assert "slim_bundle_schema_mismatch" in str(excinfo.value)


def test_validate_bundle_feature_contract_rejects_wrong_features(tmp_path) -> None:
    bundle_dir = tmp_path
    (bundle_dir / "contracts").mkdir(parents=True, exist_ok=True)
    contract = {
        "schema": EXPECTED_SCHEMA,
        "features_model_used_by_stage": {
            "preflop": list(PREFLOP_FEATURES) + ["features.phantom"],
            "flop": list(FLOP_FEATURES),
            "turn": list(TURN_FEATURES),
            "river": list(RIVER_FEATURES),
        },
    }
    (bundle_dir / "contracts" / "feature_contract.json").write_text(
        __import__("json").dumps(contract, indent=2), encoding="utf-8"
    )
    with pytest.raises(SlimContractError) as excinfo:
        validate_bundle_feature_contract(bundle_dir, stage="preflop")
    assert "slim_stage_features_mismatch" in str(excinfo.value)


# ---- train builder ----


def test_build_slim_frame_from_rich_dataset_keeps_only_slim_columns() -> None:
    rich = pd.DataFrame(
        {
            "source_dataset": ["fixture"],
            "source_row_id": ["row-0"],
            "hand_id": ["h-0"],
            "stage_group": ["PREFLOP"],
            "split": ["train"],
            "label_3intent": ["call"],
            "metadata.street": ["PREFLOP"],
            "features.hero_position": ["bb"],
            "features.pot_bb": [3.0],
            "features.to_call_bb": [1.0],
            "features.effective_stack_bb": [40.0],
            "features.stack_to_pot_ratio": [13.3],
            "features.has_check": [1.0],
            "features.has_call": [1.0],
            "features.has_raise": [1.0],
            "features.num_players": [3.0],
            "features.prior_fold_count": [1.0],
            "features.action_count": [2.0],
            "features.prior_check_count": [0.0],
            "features.prior_bet_raise_count": [1.0],
            "features.prior_call_count": [1.0],
            "features.board_card_count": [0.0],
            "features.bet_size_bb": [1.0],
            "features.equity_global": [0.55],
            "features.ev": [4.0],
            "features.call_max_bb": [2.0],
            # Rich columns that MUST NOT appear in the slim frame
            "features.equity_1v1": [0.60],
            "features.equity_gap": [0.10],
            "features.has_fold": [1.0],
            "features.num_bets": [1.0],
        }
    )
    slim = build_slim_frame_from_rich_dataset(rich)
    slim_columns = set(slim.columns)
    assert "features.equity_1v1" not in slim_columns
    assert "features.equity_gap" not in slim_columns
    assert "features.has_fold" not in slim_columns
    assert "features.num_bets" not in slim_columns
    # slim keeps the slim columns (subset of preflop is enough for the assertion)
    for feature in PREFLOP_FEATURES:
        assert feature in slim_columns, feature
    # equity_win is populated from the rich source; EV is intentionally absent.
    assert slim.loc[0, "features.equity_win"] == 0.55
    assert "features.source_ev_bb" not in slim_columns
    assert slim.loc[0, "features.call_margin_bb"] == 1.0
    assert slim.loc[0, "features.can_check"] == 1.0
    assert slim.loc[0, "features.can_call"] == 1.0


# ---- live builder ----


def _decision_input(**overrides) -> SimpleNamespace:
    base = dict(
        new_party_detected=False,
        street="FLOP",
        hero_cards=["AS", "KD"],
        board_cards=["AH", "8C", "4D"],
        strategy_hero_cards=["AS", "KD"],
        buttons=[],
        pot=200.0,
        to_call=20.0,
        equity=0.64,
        equity_1v1=0.70,
        equity_required=0.20,
        call_max=60.0,
        amount_to_play=20.0,
        active_opponents=1,
        player_count=2,
        hero_stack=1500.0,
        effective_stack=1000.0,
        big_blind=20.0,
        ev=120.0,
        hero_position=SimpleNamespace(position="BTN", reason="", confidence=None),
        pokercharts_provider=None,
        preflop_scenario=None,
        villain_position=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_build_slim_features_from_decision_input_returns_all_columns() -> None:
    features = build_slim_features_from_decision_input(_decision_input())
    expected = set(PREFLOP_FEATURES) | set(POSTFLOP_FEATURES)
    assert set(features) == expected


def test_build_slim_features_from_decision_input_maps_equity_win() -> None:
    features = build_slim_features_from_decision_input(_decision_input(equity=0.42))
    assert features["features.equity_win"] == 0.42


def test_build_slim_features_from_decision_input_computes_players_active() -> None:
    state = _decision_input(player_count=5, active_opponents=3)
    features = build_slim_features_from_decision_input(state)
    assert features["features.players_active"] == 5


def test_build_slim_features_from_decision_input_computes_call_max_bb() -> None:
    state = _decision_input(call_max=60.0, big_blind=20.0)
    features = build_slim_features_from_decision_input(state)
    assert features["features.call_max_bb"] == 3.0


def test_build_slim_features_from_decision_input_computes_call_margin_bb() -> None:
    state = _decision_input(call_max=60.0, to_call=20.0, big_blind=20.0)
    features = build_slim_features_from_decision_input(state)
    assert features["features.call_margin_bb"] == 2.0


def test_build_slim_features_from_decision_input_raises_on_missing_equity() -> None:
    state = _decision_input(equity=None, equity_1v1=None, equity_required=None)
    with pytest.raises(SlimLiveBuildError) as excinfo:
        build_slim_features_from_decision_input(state)
    assert "slim_live_critical_missing" in str(excinfo.value)
    assert "features.equity_win" in str(excinfo.value)


def test_build_slim_features_from_decision_input_raises_on_missing_call_max() -> None:
    state = _decision_input(call_max=0.0, big_blind=None)
    with pytest.raises(SlimLiveBuildError) as excinfo:
        build_slim_features_from_decision_input(state)
    assert "features.call_max_bb" in str(excinfo.value)


def test_live_features_for_stage_preflop_returns_preflop_columns() -> None:
    features = build_slim_features_from_decision_input(_decision_input())
    slim = live_features_for_stage(features, stage="preflop")
    assert list(slim) == list(PREFLOP_FEATURES)


def test_live_features_for_stage_flop_returns_flop_columns() -> None:
    features = build_slim_features_from_decision_input(_decision_input())
    slim = live_features_for_stage(features, stage="flop")
    assert list(slim) == list(FLOP_FEATURES)


def test_live_features_for_stage_unknown_raises() -> None:
    features = build_slim_features_from_decision_input(_decision_input())
    with pytest.raises(SlimLiveBuildError):
        live_features_for_stage(features, stage="postflop")


def test_features_by_stage_keys() -> None:
    assert set(FEATURES_BY_STAGE) == {"preflop", "flop", "turn", "river"}
    assert FEATURES_BY_STAGE["preflop"] == PREFLOP_FEATURES
    assert FEATURES_BY_STAGE["flop"] == FLOP_FEATURES
    assert FEATURES_BY_STAGE["turn"] == TURN_FEATURES
    assert FEATURES_BY_STAGE["river"] == RIVER_FEATURES
