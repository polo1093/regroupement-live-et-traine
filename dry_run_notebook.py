"""Dry-run every code cell of launch.ipynb in a Jupyter-like env.

This stub-spies subprocess.run and IPython.display, then executes each
cell in a *cumulative* namespace (cells after §1 see the variables that
§1 defined). Any exception is reported with its cell number and first
line so we can pinpoint the bug.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent
NB = REPO / "launch.ipynb"
nb = json.loads(NB.read_text(encoding="utf-8"))

# Stub IPython.display
ipython = types.ModuleType("IPython")
display_mod = types.ModuleType("IPython.display")
class _Stub:
    def __init__(self, *a, **k): pass
    def __getattr__(self, _k): return _Stub()
    def __call__(self, *a, **k): return None
for name in ("display", "Markdown", "SVG"):
    setattr(display_mod, name, _Stub())
ipython.display = display_mod
sys.modules["IPython"] = ipython
sys.modules["IPython.display"] = display_mod

# Make all subprojects + shared package importable
for p in (str(REPO), str(REPO / "Traine_aide_decission"), str(REPO / "aide_decission")):
    if p not in sys.path:
        sys.path.insert(0, p)

# Spy subprocess.run to a no-op (but expose the cmd to the dry-run log)
import subprocess as _sp
def _spy_run(cmd, *a, **kw):
    cwd = kw.get("cwd")
    print(f"  [DRY] cwd={cwd} cmd={' '.join(str(c) for c in cmd)}")
    class _R:
        returncode = 0
        stdout = ""
        stderr = ""
    return _R()
_sp.run = _spy_run
_sp.CalledProcessError = type("CalledProcessError", (Exception,), {})

# Build a single global namespace that all cells share
ns: dict = {"__name__": "__main__", "__file__": str(NB)}

# Sanity: the REPO used by §1's resolver is the actual repo, not cwd
ns["__REPO__"] = str(REPO)

# Track failures
failures: list[tuple[int, str, str]] = []
for idx, cell in enumerate(nb["cells"]):
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
    if not src.strip():
        continue
    # The very first cell uses Path.cwd() / __file__ to find ROOT. Make
    # sure __file__ points at this dry-run script so the resolver finds
    # the real repo.
    label = src.splitlines()[0][:60]
    try:
        exec(compile(src, f"<cell-{idx+1}>", "exec"), ns)
        print(f"[OK] cell {idx+1:2d}: {label!r}")
    except Exception as exc:
        import traceback
        print(f"[FAIL] cell {idx+1:2d}: {label!r}")
        print(f"        {type(exc).__name__}: {exc}")
        traceback.print_exc()
        failures.append((idx + 1, label, repr(exc)))
        break  # stop at the first failure

if not failures:
    print("\nAll code cells ran OK in dry-run.")
else:
    print(f"\nFirst failure at cell {failures[0][0]}: {failures[0][1]!r}")
    print(f"  {failures[0][2]}")
