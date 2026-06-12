# Regle d'or du projet

Ce document est la reference racine pour les garde-fous ML du projet.

## Regle d'or equity

```text
L'equite est obligatoire dans tout dataset modele.
Elle doit etre lue si elle existe, sinon recalculee, sinon le run doit echouer explicitement.
Elle ne doit jamais disparaitre silencieusement ni etre seulement imputee.
```

Champs minimums attendus quand la source les expose :

```text
equity_global ou equity_table
equity_1v1
equity_required
equity_gap
```

## Regle d'or features

Tout changement de feature d'entree modele doit passer par le notebook racine
`features.ipynb` avant d'etre ajoute ailleurs.

Le notebook doit documenter, pour chaque feature :

```text
nom exact
description francaise
type et unite
normalisation
valeurs attendues
statut obligatoire / optionnel / candidat
source train
source live
risques de fuite ou de mauvaise interpretation
correlations avec les autres features
```

Les modeles doivent utiliser uniquement les features promues dans le contrat
partage `shared_decision_features`. Les features optionnelles ou candidates
peuvent etre explorees dans le notebook, mais elles ne doivent pas entrer dans
un entrainement officiel tant qu'elles ne sont pas promues dans ce contrat.

## Regle d'or normalisation

Les montants d'argent utilises en entree modele sont exprimes en big blinds.

```text
montant_bb = montant_brut / big_blind
```

Une feature de montant sans suffixe clair, sans unite connue, ou melangeant
euros/jetons/big blinds ne doit pas entrer dans un modele.

## Regle d'or position

La position brute (`SB`, `BB`, `BTN`, `CO`, `MP`, `UTG`) ne doit pas etre le seul
signal pour expliquer l'ordre de parole. La direction cible est de remplacer ou
reduire cette feature brute par des features numeriques plus lisibles pour les
modeles :

```text
features.pot_certain_bb
features.pot_probable_bb
features.pot_probable_margin_bb
features.equity_win_present
```

Ces features doivent capturer ce qui compte vraiment : combien le pot represente
deja avec hero et les joueurs engages, combien de joueurs ont deja parle, et
combien peuvent encore rejoindre le pot.

`features.actors_before_hero` et `features.actors_after_hero` peuvent servir au
calcul interne ou au diagnostic, mais ne sont pas des entrees modele.
