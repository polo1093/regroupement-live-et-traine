# Solver Soft Policy Training

Status: `ok`

## Dataset

```json
{
  "rows": 100,
  "split_distribution": {
    "test": 15,
    "train": 70,
    "validation": 15
  },
  "street_distribution": {
    "RIVER": 100
  },
  "label_distribution": {
    "NO_INVEST": 54,
    "RAISE": 46
  },
  "target_means": {
    "target_freq_no_invest": 0.553494,
    "target_freq_call": 0.002364,
    "target_freq_raise": 0.444142
  }
}
```

## Stages

### river

```json
{
  "status": "ok",
  "stage": "river",
  "selected_model": "extra_trees_regressor",
  "rows": 100,
  "rows_train": 70,
  "rows_validation": 15,
  "rows_test": 15,
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
    "features.bet_size_bb"
  ],
  "target_means": {
    "target_freq_no_invest": 0.553494,
    "target_freq_call": 0.002364,
    "target_freq_raise": 0.444142
  },
  "mae": 0.283757,
  "rmse": 0.420789,
  "per_target_mae": {
    "target_freq_no_invest": 0.424334,
    "target_freq_call": 0.001301,
    "target_freq_raise": 0.425635
  },
  "prediction_target_means": {
    "target_freq_no_invest": 0.520193,
    "target_freq_call": 0.001648,
    "target_freq_raise": 0.478159
  }
}
```
