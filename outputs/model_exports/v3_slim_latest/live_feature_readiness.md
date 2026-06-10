# Live Feature Readiness

Le contrat slim expose des features equity-core critiques. Chacune doit etre disponible live, normalisee en BB quand monetaire, et calculee comme au train.

| Feature | Disponible live ? | Meme calcul que train ? | Bloquant ? | Note |
| --- | --- | --- | --- | --- |
| equity_win | oui | oui | oui | DecisionInput.equity (probabilite 0..1). |
| call_max_bb | oui | oui | oui | DecisionInput.call_max / big_blind (BB). |
| call_margin_bb | oui | oui | oui | call_max_bb - to_call_bb. |
| players_active | oui | oui | oui | player_count si present, sinon active_opponents + 1. |

Decision actuelle: prediction live bloquee tant que toutes les lignes bloquantes ne sont pas `oui / oui / oui`.
