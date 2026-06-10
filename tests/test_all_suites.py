from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_SUITES = (
    "shared_decision_features/tests",
    "aide_decission/tests",
    "Traine_aide_decission/tests",
)


def test_all_project_suites() -> None:
    """Run every project test suite from one root-level IDE target."""

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(REPO_ROOT)
        if not existing_pythonpath
        else os.pathsep.join((str(REPO_ROOT), existing_pythonpath))
    )

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", *TEST_SUITES],
        cwd=REPO_ROOT,
        env=env,
        check=False,
    )
    assert completed.returncode == 0
