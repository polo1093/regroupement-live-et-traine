"""Top-level launcher for the live decision bot.

This file lives at the repo root so the project has a single, obvious
entry point. It is a *thin* wrapper around ``aide_decission/launch.py``:

* When executed as a script (``python launch.py``) it delegates to the
  real entry point via :mod:`runpy` so error reporting and signal
  handling stay native.
* When imported as a module (``from launch import App, ...``) it
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
LIVE_LAUNCH = LIVE_DIR / "launch.py"
LIVE_LAUNCH_SUPPORT = LIVE_DIR / "launch_support.py"
LIVE_LAUNCHER_CLI = LIVE_DIR / "launcher" / "cli.py"

# Make the live package importable so that ``from launcher import ...``
# inside ``aide_decission/launch.py`` resolves to
# ``aide_decision/launcher/`` rather than failing with
# ``ModuleNotFoundError`` when ``runpy`` executes the script.
if str(LIVE_DIR) not in sys.path:
    sys.path.insert(0, str(LIVE_DIR))


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
del _ns, _name, _value


__all__ = sorted(
    name for name in globals()
    if not name.startswith("_") and name not in {"runpy", "sys", "Path", "importlib"}
)


if __name__ == "__main__":
    # Show the real entry point in help output and log lines.
    sys.argv[0] = str(LIVE_LAUNCH)
    runpy.run_path(str(LIVE_LAUNCH), run_name="__main__")
