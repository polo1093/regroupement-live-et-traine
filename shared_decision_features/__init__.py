"""Shared slim decision-features contract for train and live.

This package is the single source of truth for the V3 slim feature
contract used by:

* training scripts in ``Traine_aide_decission/`` (build the slim frame
  from a rich V3 dataset) ;
* the live decision engine in ``aide_decission/`` (build the same slim
  row from a ``DecisionInput``).

Both sides must import their lists, formulas, builders and validators
from this package so that the live prediction pipeline can refuse any
bundle whose contract is not the expected ``merged_oracle_3intent_v3_slim``.
"""
from __future__ import annotations

from shared_decision_features.contract import (
    BUNDLE_SCHEMA,
    CATEGORICAL_BY_STAGE,
    CRITICAL_FEATURES,
    EXPECTED_SCHEMA,
    FEATURE_FORMULAS,
    FEATURES_BY_STAGE,
    FLOP_FEATURES,
    FORBIDDEN_MODEL_COLUMNS,
    LABELS,
    POSTFLOP_FEATURES,
    PREFLOP_FEATURES,
    RICH_FORBIDDEN_FEATURES,
    RIVER_FEATURES,
    SPLITS,
    STAGE_NAMES,
    STAGES,
    TURN_FEATURES,
    validate_stage_features,
)
from shared_decision_features.live_builder import (
    SlimLiveBuildError,
    build_slim_features_from_decision_input,
    live_features_for_stage,
)
from shared_decision_features.train_builder import (
    build_slim_frame_from_rich_dataset,
)
from shared_decision_features.validation import (
    SlimContractError,
    load_bundle_feature_contract,
    validate_bundle_feature_contract,
    validate_no_rich_leak,
    validate_stage_features_columns,
)

__all__ = [
    "BUNDLE_SCHEMA",
    "CATEGORICAL_BY_STAGE",
    "CRITICAL_FEATURES",
    "EXPECTED_SCHEMA",
    "FEATURE_FORMULAS",
    "FEATURES_BY_STAGE",
    "FLOP_FEATURES",
    "FORBIDDEN_MODEL_COLUMNS",
    "LABELS",
    "POSTFLOP_FEATURES",
    "PREFLOP_FEATURES",
    "RICH_FORBIDDEN_FEATURES",
    "RIVER_FEATURES",
    "SlimContractError",
    "SlimLiveBuildError",
    "SPLITS",
    "STAGE_NAMES",
    "STAGES",
    "TURN_FEATURES",
    "build_slim_features_from_decision_input",
    "build_slim_frame_from_rich_dataset",
    "live_features_for_stage",
    "load_bundle_feature_contract",
    "validate_bundle_feature_contract",
    "validate_no_rich_leak",
    "validate_stage_features",
    "validate_stage_features_columns",
]
