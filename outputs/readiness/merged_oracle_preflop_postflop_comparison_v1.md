# Merged Oracle Preflop/Postflop Comparison

| model | rows | accuracy | macro F1 | recall NO_INVEST | recall CALL | recall RAISE |
|---|---:|---:|---:|---:|---:|---:|
| merged_preflop_model_v1 | 90 | 0.055556 | 0.047619 | 0.0 | 0.0 | 0.125 |
| merged_postflop_model_v1 | 90 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |

## Warnings

- Source/domain shift is expected: PokerBench structured rows and GTO-style HF rows do not share the same distribution.
- Source dataset is used only for grouped evaluation, not as a model feature.
- PHH/ACPC remains excluded from supervised oracle training.

## Recommendation

Use these models for offline comparison only. Treat improvement as coverage evidence only after source-level and street-level performance are stable.
