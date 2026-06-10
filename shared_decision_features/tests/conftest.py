"""Pytest conftest that makes the shared_decision_features package importable.

The shared package lives at the repo root (one level above this
``tests/`` folder). When pytest is launched from a project subfolder
(``Traine_aide_decission/`` or ``aide_decission/``), the root is not on
``sys.path`` by default. This conftest makes both layouts work.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
