# Merged Oracle V3 Slim Final Report

## Feature Counts

```json
{
  "flop": 12,
  "preflop": 11,
  "river": 12,
  "turn": 12
}
```

## Feature Contract

```json
{
  "flop": [
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
  "preflop": [
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
    "features.call_margin_bb"
  ],
  "river": [
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
  "turn": [
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
  ]
}
```

## Model Metrics

| model | rows_train | rows_validation | rows_test | selected_model | accuracy | macro_f1 | recall_NO_INVEST | recall_CALL | recall_RAISE |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| preflop | 53070 | 7581 | 15163 | lightgbm | 0.868364 | 0.86304 | 0.809402 | 0.916492 | 0.909707 |
| flop | 7896 | 1174 | 2189 | extra_trees | 0.835998 | 0.845369 | 0.781938 | 0.914683 | 0.941176 |
| turn | 20443 | 2885 | 5881 | random_forest | 0.877402 | 0.87946 | 0.879974 | 0.861993 | 0.897877 |
| river | 62893 | 8974 | 17996 | lightgbm | 0.840854 | 0.856665 | 0.800188 | 0.827687 | 0.978313 |

## Feature Formulas

| feature | calcul |
| --- | --- |
| `features.hero_position` | Normalized hero position: SB, BB, BTN, CO, MP, UTG, else UNKNOWN. |
| `features.pot_bb` | pot / big_blind. |
| `features.to_call_bb` | to_call / big_blind; 0.0 for a free check. |
| `features.effective_stack_bb` | min(hero_stack, max(active_villain_stacks)) / big_blind; folded players excluded. |
| `features.can_check` | 1 if check is currently legal, else 0. |
| `features.can_call` | 1 if call is legal and to_call_bb > 0, else 0. |
| `features.can_raise` | 1 if bet/raise/all-in is legal, else 0. |
| `features.players_active` | current players still in pot, hero included; live = active_opponents + 1 (fallback). |
| `features.bet_size_bb` | Available/source bet size in BB. In live, derived from to_call or raise buttons; in train, mapped from features.bet_size_bb. |
| `features.equity_win` | Single model equity against active opponents; in live = DecisionInput.equity. |
| `features.call_max_bb` | Maximum profitable call in big blinds. In live = call_max / big_blind. |
| `features.call_margin_bb` | call_max_bb - to_call_bb. |

## Removed Redundant Features

- `metadata.street`
- `features.source_ev_bb`
- `features.equity_1v1`
- `features.equity_required`
- `features.equity_gap`
- `features.has_fold`
- `features.num_bets`
- `features.call_ev_bb`
- `features.stack_to_pot_ratio`
- `features.to_call_pot_ratio`
- `features.players_folded`
- `features.prior_bet_raise_count`
- `features.prior_call_count`
- `features.prior_check_count`
- `features.action_count`
- `features.board_card_count`
