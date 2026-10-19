"""Orchestration : Bronze -> Silver -> Gold (dbt) -> Qualite. Arret au premier echec."""
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
DBT = shutil.which("dbt") or "dbt"

STEPS = [
    ("bronze", [PY, "lakehouse/pipelines/bronze.py", "--next", "30"], ROOT),
    ("silver", [PY, "lakehouse/pipelines/silver.py"], ROOT),
    ("gold (dbt)", [DBT, "build", "--profiles-dir", "."], ROOT / "lakehouse" / "dbt_gold"),
    ("qualite", [PY, "lakehouse/pipelines/quality_checks.py"], ROOT),
]

for name, cmd, cwd in STEPS:
    t0 = time.time()
    print(f"\n=== {name} ===")
    r = subprocess.run(cmd, cwd=cwd)
    dt = time.time() - t0
    if r.returncode != 0:
        print(f"ECHEC a l'etape '{name}' apres {dt:.0f}s")
        sys.exit(r.returncode)
    print(f"OK {name} ({dt:.0f}s)")

print("\nPipeline termine avec succes")