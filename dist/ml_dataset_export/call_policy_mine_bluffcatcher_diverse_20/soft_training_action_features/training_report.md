# Solver Soft Policy Training

Status: `ok`

## Dataset

```json
{
  "rows": 20,
  "split_distribution": {
    "test": 3,
    "train": 14,
    "validation": 3
  },
  "street_distribution": {
    "RIVER": 20
  },
  "label_distribution": {
    "NO_INVEST": 19,
    "RAISE": 1
  },
  "target_means": {
    "target_freq_no_invest": 0.714613,
    "target_freq_call": 0.243629,
    "target_freq_raise": 0.041758
  }
}
```

## Stages

### river

```json
{
  "status": "ok",
  "stage": "river",
  "selected_model": "random_forest_regressor",
  "rows": 20,
  "rows_train": 14,
  "rows_validation": 3,
  "rows_test": 3,
  "feature_names": [
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
    "features.raise_option_max_bb",
    "features.raise_option_pot_ratio",
    "features.raise_option_to_call_ratio"
  ],
  "extended_soft_features": [
    "features.raise_option_max_bb",
    "features.raise_option_pot_ratio",
    "features.raise_option_to_call_ratio"
  ],
  "target_means": {
    "target_freq_no_invest": 0.714613,
    "target_freq_call": 0.243629,
    "target_freq_raise": 0.041758
  },
  "mae": 0.033131,
  "rmse": 0.053126,
  "per_target_mae": {
    "target_freq_no_invest": 0.049696,
    "target_freq_call": 0.013857,
    "target_freq_raise": 0.035839
  },
  "prediction_target_means": {
    "target_freq_no_invest": 0.747005,
    "target_freq_call": 0.216834,
    "target_freq_raise": 0.036161
  }
}
```
