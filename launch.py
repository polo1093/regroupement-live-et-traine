"""Top-level launcher for the live decision bot AND the v3_slim training pipeline.

This file lives at the repo root so the project has a single, obvious
entry point. It is a *thin* wrapper around :

* ``aide_decission/launch.py`` : the live decision bot (Tkinter UI).
* ``Traine_aide_decission/experiments/v3_slim_mass_synthetic_pipeline.py`` :
  mass synthetic V3-rich corpus generation, V3 slim training and bundle
  export.

The launcher dispatches based on the first CLI argument :

```bash
# Mode 1 : lancer le bot live (par défaut, ou `python launch.py live ...`)
python launch.py
python launch.py live --game PMU --interval 250

# Mode 2 : générer ~1M lignes sur preflop/flop/turn/river et entraîner V3 slim
python launch.py train-slim --force
```

When imported as a module (``from launch import App, ...``) it
re-exports the public API of ``aide_decission/launch.py``,
``aide_decission/launch_support.py`` and
``aide_decission/launcher/cli.py`` so tests and tooling can
``import launch`` regardless of whether the CWD is the repo root or
``aide_decission/``.

Any cli flag accepted by the inner launcher (``--game``,
``--decision-mode``, ``--snapshot``, ``--list-games``, etc.) is
forwarded as-is.
"""

from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIVE_DIR = ROOT / "aide_decission"
TRAIN_DIR = ROOT / "Traine_aide_decission"
LIVE_LAUNCH = LIVE_DIR / "launch.py"
LIVE_LAUNCH_SUPPORT = LIVE_DIR / "launch_support.py"
LIVE_LAUNCHER_CLI = LIVE_DIR / "launcher" / "cli.py"
V3_SLIM_MASS_EXPERIMENT = (
    TRAIN_DIR / "experiments" / "v3_slim_mass_synthetic_pipeline.py"
)

# Subcommandes connues. ``live`` est implicite (par défaut) pour rétro-
# compatibilité avec l'ancien comportement de launch.py.
KNOWN_SUBCOMMANDS = {
    "live",
    "train-slim",
    "train_slim",
    "v3-slim",
    "v3_slim",
}


def _load_module_from_path(module_name: str, file_path: Path) -> dict:
    """Charge un module Python depuis un chemin arbitraire.

    On utilise :func:`importlib.util.spec_from_file_location` pour
    charger le module dans un spec dédié, ce qui évite d'éventuels
    effets de bord (création de fenêtre Tk, etc.) à l'import. Seul le
    bloc de définitions au top-level est exécuté.

    Le module est enregistré dans :data:`sys.modules` sous le nom
    ``module_name`` (et son ``__file__`` original). C'est indispensable
    pour que les décorateurs qui s'appuient sur ``sys.modules[...]``
    (par exemple :func:`dataclasses.dataclass`) puissent retrouver
    leur propre module lors de la décoration.
    """
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError(f"Impossible de charger {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return vars(module)


def _route_subcommand(argv: list[str]) -> str | None:
    """Détermine le sous-mode demandé par argv[1] (live, river-solver, ...)."""

    if not argv:
        return None
    first = argv[0].strip().lower()
    if first in KNOWN_SUBCOMMANDS:
        return first
    # Sous-commande non reconnue : on bascule sur le mode live par
    # défaut (rétro-compatibilité avec les anciens appels type
    # `python launch.py --game PMU ...`).
    if first.startswith("-"):
        return None
    return None


def _run_v3_slim_mass_training(argv: list[str]) -> int:
    """Délègue au pipeline massif de génération/entraînement V3 slim."""

    if not V3_SLIM_MASS_EXPERIMENT.exists():
        print(
            f"ERREUR : script introuvable : {V3_SLIM_MASS_EXPERIMENT}",
            file=sys.stderr,
        )
        return 1
    if str(TRAIN_DIR) not in sys.path:
        sys.path.insert(0, str(TRAIN_DIR))
    forwarded_argv = list(argv[1:])
    sys.argv = [str(V3_SLIM_MASS_EXPERIMENT), *forwarded_argv]
    runpy.run_path(str(V3_SLIM_MASS_EXPERIMENT), run_name="__main__")
    return 0


_INITIAL_SUBCOMMAND = _route_subcommand(sys.argv[1:]) if __name__ == "__main__" else None
_OFFLINE_SUBCOMMANDS = {
    "train-slim",
    "train_slim",
    "v3-slim",
    "v3_slim",
}
_HELP_REQUESTED = (
    __name__ == "__main__"
    and bool(sys.argv[1:])
    and sys.argv[1].strip().lower() in {"help", "--help", "-h"}
)
_SKIP_LIVE_BOOTSTRAP = _HELP_REQUESTED or _INITIAL_SUBCOMMAND in _OFFLINE_SUBCOMMANDS


if _SKIP_LIVE_BOOTSTRAP:
    _LIVE_NS = {}
    _SUPPORT_NS = {}
    _CLI_NS = {}
else:
    # Make the live package importable so that ``from launcher import ...``
    # inside ``aide_decission/launch.py`` resolves to
    # ``aide_decision/launcher/`` rather than failing with
    # ``ModuleNotFoundError`` when ``runpy`` executes the script.
    if str(LIVE_DIR) not in sys.path:
        sys.path.insert(0, str(LIVE_DIR))

    _LIVE_NS = _load_module_from_path("_aide_decission_launch", LIVE_LAUNCH)
    _SUPPORT_NS = _load_module_from_path(
        "_aide_decission_launch_support", LIVE_LAUNCH_SUPPORT
    )
    _CLI_NS = _load_module_from_path(
        "_aide_decission_launcher_cli", LIVE_LAUNCHER_CLI
    )

import types

# Réexporte la même API publique que ``aide_decission/launch.py``,
# ``launch_support.py`` et ``launcher/cli.py`` pour que
# ``from launch import App, CONFIG_ROOT, parse_args, ...`` fonctionne
# aussi bien depuis la racine du repo que depuis ``aide_decission/``.
# On évite les noms privés (préfixés par ``_``) pour ne pas polluer
# l'API publique.
for _ns in (_LIVE_NS, _SUPPORT_NS, _CLI_NS):
    for _name, _value in _ns.items():
        if _name.startswith("_"):
            continue
        # On exclut uniquement les sous-modules (ex: ``PokerTH`` qui
        # est un sous-package du namespace ``launcher.cli``). On garde
        # les fonctions, classes, dataclasses, constantes, etc.
        if isinstance(_value, types.ModuleType):
            continue
        globals().setdefault(_name, _value)
del _ns
if "_name" in globals():
    del _name
if "_value" in globals():
    del _value


__all__ = sorted(
    name for name in globals()
    if not name.startswith("_") and name not in {"runpy", "sys", "Path", "importlib"}
)


def _print_help() -> None:
    print(
        "Usage :\n"
        "  python launch.py [live] [options live ...]\n"
        "      -> lance le bot live (mode par défaut).\n"
        "\n"
        "  python launch.py train-slim [options train ...]\n"
        "      -> génère un corpus synthétique V3 riche (~1M lignes par défaut),\n"
        "         entraîne les 4 modèles slim et exporte le bundle.\n"
        "\n"
        "Pour les options live :\n"
        "  python launch.py live --help\n"
        "\n"
        "Pour les options train-slim :\n"
        "  python launch.py train-slim --help\n"
        "\n"
        "Exemples :\n"
        "  python launch.py --game PMU --interval 250\n"
        "  python launch.py train-slim --force\n",
        file=sys.stderr,
    )


if __name__ == "__main__":
    subcmd = _route_subcommand(sys.argv[1:])
    if subcmd in {"train-slim", "train_slim", "v3-slim", "v3_slim"}:
        raise SystemExit(_run_v3_slim_mass_training(sys.argv[1:]))
    if subcmd is None and sys.argv[1:] and sys.argv[1].strip().lower() in {"help", "--help", "-h"}:
        _print_help()
        raise SystemExit(0)
    # Mode live (par défaut, rétro-compatible)
    sys.argv[0] = str(LIVE_LAUNCH)
    runpy.run_path(str(LIVE_LAUNCH), run_name="__main__")
