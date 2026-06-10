"""Contract validation helpers shared by train and live.

These functions are the runtime gate that prevents the live engine from
predicting on the wrong schema. They are also used by the training
pipeline to assert the slim CSV columns and the exported bundle
contract.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shared_decision_features.contract import (
    EXPECTED_SCHEMA,
    FEATURES_BY_STAGE,
    RICH_FORBIDDEN_FEATURES,
)


class SlimContractError(ValueError):
    """Raised when a slim feature contract is violated."""


def validate_stage_features_columns(features: list[str], *, stage: str) -> None:
    """Validate that the given feature list matches the slim contract for the stage."""
    if stage not in FEATURES_BY_STAGE:
        raise SlimContractError(f"unknown_stage:{stage}")
    expected = list(FEATURES_BY_STAGE[stage])
    if list(features) != expected:
        raise SlimContractError(
            f"slim_stage_features_mismatch:{stage}:expected:{expected}:got:{list(features)}"
        )


def validate_no_rich_leak(columns: list[str]) -> None:
    """Raise if any rich-only feature would leak into the slim model."""
    leaks = sorted(set(columns) & set(RICH_FORBIDDEN_FEATURES))
    if leaks:
        raise SlimContractError(f"slim_rich_feature_leak:{leaks}")


def load_bundle_feature_contract(bundle_dir: Path) -> dict[str, Any]:
    """Load the ``contracts/feature_contract.json`` from a model bundle."""
    path = Path(bundle_dir) / "contracts" / "feature_contract.json"
    if not path.exists():
        raise SlimContractError(f"slim_bundle_contract_missing:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SlimContractError(f"slim_bundle_contract_invalid_json:{path}:{exc}") from exc


def validate_bundle_feature_contract(bundle_dir: Path, *, stage: str) -> dict[str, Any]:
    """Validate that the bundle's ``feature_contract.json`` matches the slim contract.

    Returns the loaded contract for downstream use.
    """
    contract = load_bundle_feature_contract(bundle_dir)
    schema = contract.get("schema")
    if schema != EXPECTED_SCHEMA:
        raise SlimContractError(
            f"slim_bundle_schema_mismatch:expected:{EXPECTED_SCHEMA}:got:{schema}"
        )
    features_by_stage = contract.get("features_model_used_by_stage") or {}
    stage_features = features_by_stage.get(stage)
    validate_stage_features_columns(list(stage_features or []), stage=stage)
    return contract
