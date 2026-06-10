"""Repository-wide pytest configuration.

The project is a monorepo composed of three siblings:

* ``aide_decission/``         — the live decision bot (Tk + scanner)
* ``Traine_aide_decission/``  — the training pipelines
* ``shared_decision_features/`` — the slim feature contract shared by both

When ``pytest`` is launched from the repo root, none of these three
folders is automatically on ``sys.path``. This conftest makes sure the
shared package and the two sub-projects are importable, mirroring the
behaviour of the per-project ``conftest.py`` files that already exist in
``aide_decission/tests`` and ``shared_decision_features/tests``.

It also exposes a couple of helpers (root path, project paths) so tests
and fixtures can rely on absolute, repo-relative locations.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
LIVE_DIR = REPO_ROOT / "aide_decission"
TRAIN_DIR = REPO_ROOT / "Traine_aide_decission"
SHARED_DIR = REPO_ROOT / "shared_decision_features"

# Les sous-projets ``Traine_aide_decission`` étalent leurs modules
# (datasets, experiments, models, solvers, solver_jobs, pokerth,
# synthetic) au même niveau que ``tests/``. Comme les tests font
# ``from experiments import ...`` ou ``from solver_jobs import ...``,
# il faut ajouter ``Traine_aide_decission/`` lui-même sur ``sys.path``.
TRAIN_SUBPROJECTS = (
    TRAIN_DIR,
    TRAIN_DIR / "datasets",
    TRAIN_DIR / "experiments",
    TRAIN_DIR / "models",
    TRAIN_DIR / "pokerth",
    TRAIN_DIR / "solvers",
    TRAIN_DIR / "solver_jobs",
    TRAIN_DIR / "synthetic",
)

for path in (REPO_ROOT, LIVE_DIR, TRAIN_DIR, SHARED_DIR, *TRAIN_SUBPROJECTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Absolute path to the repository root."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def live_dir() -> Path:
    """Absolute path to the ``aide_decission/`` sub-project."""
    return LIVE_DIR


@pytest.fixture(scope="session")
def train_dir() -> Path:
    """Absolute path to the ``Traine_aide_decission/`` sub-project."""
    return TRAIN_DIR


@pytest.fixture(scope="session")
def shared_dir() -> Path:
    """Absolute path to the ``shared_decision_features/`` package."""
    return SHARED_DIR
