# Live Feature Readiness

Le contrat slim expose des features equity-core critiques. Chacune doit etre disponible live, normalisee en BB quand monetaire, et calculee comme au train.

| Feature | Disponible live ? | Meme calcul que train ? | Bloquant ? | Note |
| --- | --- | --- | --- | --- |
| equity_win | oui | oui | oui | DecisionInput.equity (probabilite 0..1). |
| equity_win_present | oui | oui | oui | Equity conservative ajustee avec joueurs actifs vs joueurs presents. |
| call_max_bb | oui | oui | oui | DecisionInput.call_max / big_blind (BB). |
| call_margin_bb | oui | oui | oui | call_max_bb - to_call_bb. |
| players_active | oui | oui | oui | active_opponents + 1 si present, sinon player_count. |
| pot_certain_bb | oui | oui | oui | pot_bb + to_call_bb. |
| pot_probable_bb | oui | oui | oui | pot_certain_bb + contribution minimale plausible des joueurs actifs restants. |
| pot_probable_margin_bb | oui | oui | oui | pot_probable_bb - to_call_bb. |
| ev_certain_bb | oui | oui | oui | equity_win * pot_certain_bb - to_call_bb. |
| ev_probable_bb | oui | oui | oui | equity_win * pot_probable_bb - to_call_bb. |

Decision actuelle: prediction live bloquee tant que toutes les lignes bloquantes ne sont pas `oui / oui / oui`.
