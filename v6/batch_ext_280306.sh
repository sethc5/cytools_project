#!/bin/bash
# batch_ext_280306.sh — §28 scan extension: h26-h28 next 50K each
# Resumes from current high-water marks (post §25):
#   h26: max_idx=334729 → offset=334730
#   h27: max_idx=233595 → offset=233596
#   h28: max_idx=136407 → offset=136408
#
# Usage: bash v6/batch_ext_280306.sh
# Env:   WORKERS=14 bash v6/batch_ext_280306.sh
# Output: v6/ext_280306_results.db (new rows for merge)

set -e
cd "$(dirname "$0")"

DB=cy_landscape_ext_280306.db
LOG=results/batch_ext_280306.log
WORKERS=${WORKERS:-14}
LIMIT=${LIMIT:-50000}

mkdir -p results

# Bootstrap: let pipeline_v6.py initialize the DB with the correct full schema
# on first run. Just ensure a clean start.
if [ -f "$DB" ]; then
    echo "Removing stale $DB for clean start"
    rm -f "$DB"
fi
echo "DB will be created by pipeline on first run: $DB"

echo "=== EXT SCAN §28 START: $(date -u) ===" | tee "$LOG"
echo "Host: $(hostname) | Workers: $WORKERS | Limit per h11: $LIMIT" | tee -a "$LOG"

# ── h26: offset 334730 ──────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "[$(date -u)] h26 offset=334730 limit=$LIMIT --local-ks" | tee -a "$LOG"
python3 pipeline_v6.py \
    --scan --h11 26 \
    --offset 334730 --limit $LIMIT \
    --local-ks --db "$DB" -w $WORKERS --top 999999 \
    2>&1 | tail -12 | tee -a "$LOG"

# ── h27: offset 233596 ──────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "[$(date -u)] h27 offset=233596 limit=$LIMIT --local-ks" | tee -a "$LOG"
python3 pipeline_v6.py \
    --scan --h11 27 \
    --offset 233596 --limit $LIMIT \
    --local-ks --db "$DB" -w $WORKERS --top 999999 \
    2>&1 | tail -12 | tee -a "$LOG"

# ── h28: offset 136408 ──────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "[$(date -u)] h28 offset=136408 limit=$LIMIT --local-ks" | tee -a "$LOG"
python3 pipeline_v6.py \
    --scan --h11 28 \
    --offset 136408 --limit $LIMIT \
    --local-ks --db "$DB" -w $WORKERS --top 999999 \
    2>&1 | tail -12 | tee -a "$LOG"

# ── Post-run stats ──────────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
python3 - "$DB" <<'PYEOF' | tee -a "$LOG"
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
for h in [26, 27, 28]:
    r = con.execute("""SELECT COUNT(*), MAX(poly_idx), SUM(CASE WHEN sm_score IS NOT NULL THEN 1 ELSE 0 END),
                              MAX(sm_score) FROM polytopes WHERE h11=?""", (h,)).fetchone()
    print(f"  h{h}: {r[0]} rows, max_idx={r[1]}, scored={r[2]}, max_score={r[3]}")
top = con.execute("""SELECT h11, poly_idx, sm_score, has_SM, has_GUT, n_clean
    FROM polytopes WHERE sm_score IS NOT NULL ORDER BY sm_score DESC LIMIT 20""").fetchall()
print("Top new candidates:")
for r in top:
    sm = 'SM+GUT' if r[3] and r[4] else ('SM' if r[3] else 'no-SM')
    print(f"  h{r[0]}/P{r[1]:6d}  score={r[2]}  n_clean={r[5]}  [{sm}]")
PYEOF

# ── Export results ──────────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "Exporting ext_280306_results.db..." | tee -a "$LOG"
python3 - "$DB" <<'PYEOF'
import sqlite3, sys, os
src = sqlite3.connect(sys.argv[1])
out = 'ext_280306_results.db'
if os.path.exists(out): os.remove(out)
dst = sqlite3.connect(out)
for tbl in ['polytopes', 'fibrations', 'scan_log']:
    schema = src.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{tbl}'").fetchone()
    if schema: dst.execute(schema[0])
rows = src.execute("SELECT * FROM polytopes").fetchall()
cols = [r[1] for r in src.execute('PRAGMA table_info(polytopes)').fetchall()]
ph = ','.join(['?']*len(cols)); cl = ','.join(cols)
dst.executemany(f'INSERT OR REPLACE INTO polytopes ({cl}) VALUES ({ph})', rows)
fibs = src.execute("SELECT * FROM fibrations").fetchall()
if fibs:
    fc = [r[1] for r in src.execute('PRAGMA table_info(fibrations)').fetchall()]
    fp = ','.join(['?']*len(fc)); fl = ','.join(fc)
    dst.executemany(f'INSERT OR REPLACE INTO fibrations ({fl}) VALUES ({fp})', fibs)
dst.commit()
sz = os.path.getsize(out)
print(f"ext_280306_results.db: {len(rows)} polytope rows, {len(fibs)} fib rows, {sz//1024} KB")
PYEOF

echo "" | tee -a "$LOG"
echo "=== DONE: $(date -u) ===" | tee -a "$LOG"
echo ""
echo "Merge with:  python3 v6/merge_hetzner_scan.py --results v6/ext_280306_results.db"
echo "Or use:      python3 v6/merge_t3_results.py --results v6/ext_280306_results.db"
