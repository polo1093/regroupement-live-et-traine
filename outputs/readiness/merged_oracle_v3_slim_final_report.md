# Merged Oracle V3 Slim Final Report

## Feature Counts

```json
{
  "flop": 13,
  "preflop": 12,
  "river": 13,
  "turn": 13
}
```

## Feature Contract

```json
{
  "flop": [
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
    "features.bet_size_bb"
  ],
  "preflop": [
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
    "features.ev_probable_bb"
  ],
  "river": [
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
    "features.bet_size_bb"
  ],
  "turn": [
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
    "features.bet_size_bb"
  ]
}
```

## Model Metrics

| model | rows_train | rows_validation | rows_test | selected_model | accuracy | macro_f1 | recall_NO_INVEST | recall_CALL | recall_RAISE |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| preflop | 53070 | 7581 | 15163 | lightgbm | 0.862494 | 0.856544 | 0.805183 | 0.910552 | 0.900071 |
| flop | 7896 | 1174 | 2189 | lightgbm | 0.83143 | 0.841547 | 0.770191 | 0.918651 | 0.95356 |
| turn | 20443 | 2885 | 5881 | lightgbm | 0.864819 | 0.868126 | 0.859426 | 0.847755 | 0.913043 |
| river | 62893 | 8974 | 17996 | lightgbm | 0.838464 | 0.854537 | 0.80604 | 0.808498 | 0.978012 |

## Feature Formulas

| feature | calcul |
| --- | --- |
| `features.to_call_bb` | to_call / big_blind; 0.0 for a free check. |
| `features.effective_stack_bb` | min(hero_stack, max(active_villain_stacks)) / big_blind; folded players excluded. |
| `features.players_active` | current players still in pot, hero included; live = active_opponents + 1 (fallback). |
| `features.bet_size_bb` | Available/source bet size in BB. In live, derived from to_call or raise buttons; in train, mapped from features.bet_size_bb. |
| `features.equity_win` | Single model equity against active opponents; in live = DecisionInput.equity. |
| `features.equity_win_present` | Conservative win equity adjusted to players present at the table; equals equity_win when present count is unknown or equal to active count. |
| `features.call_max_bb` | Maximum profitable call in big blinds. In live = call_max / big_blind. |
| `features.call_margin_bb` | call_max_bb - to_call_bb. |
| `features.pot_certain_bb` | Guaranteed pot in BB if hero continues now: current pot_bb + to_call_bb. |
| `features.pot_probable_bb` | Probable pot in BB if hero continues and remaining active players match the same minimum contribution; actors are internal only, not model inputs. |
| `features.pot_probable_margin_bb` | pot_probable_bb - to_call_bb; probable reward remaining after the amount hero must add. |
| `features.ev_certain_bb` | Net equity value in BB on the guaranteed pot: equity_win * pot_certain_bb - to_call_bb. |
| `features.ev_probable_bb` | Net equity value in BB on the probable pot: equity_win * pot_probable_bb - to_call_bb. |

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
