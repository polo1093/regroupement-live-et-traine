# V3 Slim Model Export

Bundle exporte depuis `merged_oracle_preflop_postflop_v3_slim` (contrat equity-core per-street). Partage avec le live via `shared_decision_features/`.

## Modeles

- preflop: `models/preflop_model.joblib` - lightgbm - macro_f1 0.738026
- flop: `models/flop_model.joblib` - extra_trees - macro_f1 0.842916
- turn: `models/turn_model.joblib` - random_forest - macro_f1 0.851654
- river: `models/river_model.joblib` - lightgbm - macro_f1 0.833687

## Important

- Contrat slim verrouille: 11 features preflop, 12 features flop/turn/river.
- 4 modeles separes: preflop, flop, turn, river.
- Les features critiques (equity_win, call_max_bb, call_margin_bb, players_active) doivent etre disponibles live.
- Le live refuse la prediction si une feature critique manque (fallback legacy).
- Toutes les valeurs monetaires sont normalisees en big blinds.
- Les colonnes `source_dataset`, labels, raw text et audit ne sont pas des entrees modele.

## Fichiers

```json
{
  "feature_contract": "contracts/feature_contract.json",
  "final_report": "reports/final_report.md",
  "flop_model": "models/flop_model.joblib",
  "flop_training_report": "reports/flop_training_report.json",
  "inputs_outputs": "inputs_outputs.txt",
  "live_feature_readiness": "live_feature_readiness.md",
  "merge_report": "reports/merge_report.json",
  "preflop_model": "models/preflop_model.joblib",
  "preflop_training_report": "reports/preflop_training_report.json",
  "river_model": "models/river_model.joblib",
  "river_training_report": "reports/river_training_report.json",
  "turn_model": "models/turn_model.joblib",
  "turn_training_report": "reports/turn_training_report.json"
}
```
