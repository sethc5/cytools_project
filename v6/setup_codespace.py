#!/usr/bin/env python3
"""Post-create setup: copy seed DB and verify CYTools + DB are ready."""
import sys, os, sqlite3

# Verify CYTools
try:
    import cytools
    from cytools import Polytope
    print("CYTools ready")
except ImportError as e:
    print(f"ERROR: CYTools not available: {e}")
    sys.exit(1)

# Bootstrap working DB from seed
seed = "v6/t3_seed.db"
db   = "v6/cy_landscape_t3.db"

if not os.path.exists(db):
    import shutil
    shutil.copy(seed, db)
    print(f"Copied {seed} -> {db}")
else:
    print(f"DB already exists: {db}")

con = sqlite3.connect(db)
scored, ge80 = con.execute(
    "SELECT COUNT(*), SUM(CASE WHEN sm_score>=80 THEN 1 ELSE 0 END) "
    "FROM polytopes WHERE sm_score IS NOT NULL"
).fetchone()
t2_pending = con.execute(
    "SELECT COUNT(*) FROM polytopes WHERE sm_score>=80 AND tier_reached='T2' AND has_SM IS NULL"
).fetchone()[0]
t3_done = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T3'").fetchone()[0]
con.close()
print(f"Seed DB ready: {scored} scored rows, {ge80} score>=80 ({t2_pending} T2-pending T3, {t3_done} T3-done)")

import subprocess
cores = subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip()
print(f"Cores: {cores} | Run:  bash v6/batch_t3.sh")
