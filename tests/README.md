# Tests hub

Ce dossier sert de point d'entree racine pour les IDE qui veulent un seul
dossier de tests.

Les tests restent dans leurs sous-projets d'origine :

- `shared_decision_features/tests`
- `aide_decission/tests`
- `Traine_aide_decission/tests`

Depuis la racine du repo :

```bash
python -m pytest
```

lance les suites directement via `pytest.ini`.

Si ton IDE demande explicitement un dossier de tests, pointe-le vers ce dossier
`tests/` : `tests/test_all_suites.py` relaiera l'execution vers les trois suites
ci-dessus.
