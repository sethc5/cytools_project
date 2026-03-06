#!/usr/bin/env bash
# §29 scan extension: h29–h32, full slices from offset 0
# Estimated runtime: ~7.5h at 200 poly/s with 14 workers
# Started: 2026-03-06

set -euo pipefail

WORKERS=${WORKERS:-14}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULT_DB="${SCRIPT_DIR}/ext_h29_h32_results.db"
LOG_DIR="${SCRIPT_DIR}/results"
mkdir -p "$LOG_DIR"

echo "=== §29 h29-h32 full scan ===" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
echo "Started: $(date -u)" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
echo "Workers: $WORKERS" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
echo "" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"

# Remove stale scan DB if it exists
if [[ -f "${SCRIPT_DIR}/cy_landscape_ext_h29_h32.db" ]]; then
    echo "[WARN] Removing stale cy_landscape_ext_h29_h32.db" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
    rm -f "${SCRIPT_DIR}/cy_landscape_ext_h29_h32.db"
fi

cd "$SCRIPT_DIR"

# h29: 1,669,235 polytopes, offset=0 (never scanned)
echo "[$(date -u)] h29 offset=0 full slice" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
python3 pipeline_v6.py \
    --scan --h11 29 --offset 0 --limit 9999999 \
    --local-ks \
    --db cy_landscape_ext_h29_h32.db \
    -w "$WORKERS" --top 999999 \
    2>&1 | tee -a "$LOG_DIR/batch_ext_h29_h32.log"

# h30: 1,430,475 polytopes, offset=0
echo "[$(date -u)] h30 offset=0 full slice" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
python3 pipeline_v6.py \
    --scan --h11 30 --offset 0 --limit 9999999 \
    --local-ks \
    --db cy_landscape_ext_h29_h32.db \
    -w "$WORKERS" --top 999999 \
    2>&1 | tee -a "$LOG_DIR/batch_ext_h29_h32.log"

# h31: 1,261,342 polytopes, offset=0
echo "[$(date -u)] h31 offset=0 full slice" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
python3 pipeline_v6.py \
    --scan --h11 31 --offset 0 --limit 9999999 \
    --local-ks \
    --db cy_landscape_ext_h29_h32.db \
    -w "$WORKERS" --top 999999 \
    2>&1 | tee -a "$LOG_DIR/batch_ext_h29_h32.log"

# h32: 1,091,040 polytopes, offset=0
echo "[$(date -u)] h32 offset=0 full slice" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
python3 pipeline_v6.py \
    --scan --h11 32 --offset 0 --limit 9999999 \
    --local-ks \
    --db cy_landscape_ext_h29_h32.db \
    -w "$WORKERS" --top 999999 \
    2>&1 | tee -a "$LOG_DIR/batch_ext_h29_h32.log"

# Summarize results
echo "" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
echo "=== Summary ===" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
python3 - <<'PYEOF' 2>&1 | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
import sqlite3, os
db = "cy_landscape_ext_h29_h32.db"
if not os.path.exists(db):
    print("No DB found")
else:
    conn = sqlite3.connect(db)
    rows = conn.execute("""
        SELECT h11, COUNT(*), SUM(CASE WHEN lvs_score IS NOT NULL THEN 1 ELSE 0 END),
               MAX(poly_idx), MAX(lvs_score)
        FROM ks_polytopes GROUP BY h11 ORDER BY h11
    """).fetchall()
    for r in rows:
        print(f"  h{r[0]}: {r[1]} rows, max_idx={r[3]}, scored={r[2]}, max_score={r[4]}")
    top = conn.execute("""
        SELECT h11, poly_idx, lvs_score FROM ks_polytopes
        WHERE lvs_score >= 70 ORDER BY lvs_score DESC LIMIT 20
    """).fetchall()
    print(f"Top new candidates (score>=70): {len(top)}")
    for r in top:
        print(f"  h{r[0]}/P{r[1]}: score={r[2]}")
    conn.close()
PYEOF

# Export clean results DB for merge
echo "" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
echo "Exporting ${RESULT_DB}..." | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
python3 - <<'PYEOF' 2>&1 | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
import sqlite3, os, shutil
src = "cy_landscape_ext_h29_h32.db"
dst = "ext_h29_h32_results.db"
if not os.path.exists(src):
    print("Source DB not found, nothing to export")
    exit(0)
shutil.copy2(src, dst)
conn = sqlite3.connect(dst)
try:
    p_count = conn.execute("SELECT COUNT(*) FROM ks_polytopes").fetchone()[0]
    f_count = conn.execute("SELECT COUNT(*) FROM fibrations").fetchone()[0] if conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fibrations'").fetchone() else 0
    size = os.path.getsize(dst) // 1024
    print(f"{dst}: {p_count} polytope rows, {f_count} fib rows, {size} KB")
except Exception as e:
    print(f"Error reading export: {e}")
conn.close()
PYEOF

echo "" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
echo "=== DONE: $(date -u) ===" | tee -a "$LOG_DIR/batch_ext_h29_h32.log"
echo "Merge with:  python3 v6/merge_t3_results.py --results v6/ext_h29_h32_results.db"
