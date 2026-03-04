#!/bin/bash
# batch_t3.sh — T3 deep analysis in GitHub Codespace
# Runs --deep on top-17 score=80 candidates (T2-only, no SM/GUT yet)
# Uses CYTools CGI API (no local KS files needed).
#
# Usage:  bash v6/batch_t3.sh
# Output: v6/results/batch_t3.log + v6/t3_results.db (updated rows for merge)

set -e
cd "$(dirname "$0")"

DB=cy_landscape_t3.db
SEED=t3_seed.db
LOG=results/batch_t3.log
TOP=${TOP:-17}           # number of T3 candidates to run (score=80 T2-only)
WORKERS=${WORKERS:-4}    # Codespace free tier: 4 cores

mkdir -p results

# ── Bootstrap DB from seed ──────────────────────────────────────────────────
if [ ! -f "$DB" ]; then
    echo "Copying seed DB → $DB"
    cp "$SEED" "$DB"
fi

echo "=== T3 BATCH START: $(date -u) ===" | tee "$LOG"
echo "Host: $(hostname) | Workers: $WORKERS | Top: $TOP" | tee -a "$LOG"
echo "DB: $DB ($(du -sh $DB | cut -f1))" | tee -a "$LOG"

# ── Pre-run stats ────────────────────────────────────────────────────────────
python3 - "$DB" <<'PYEOF' | tee -a "$LOG"
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
t3 = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T3'").fetchone()[0]
t2_pending = con.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score>=80 AND tier_reached='T2' AND has_SM IS NULL").fetchone()[0]
scored = con.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score IS NOT NULL").fetchone()[0]
print(f"Pre-run: scored={scored}  T3={t3}  T2-pending-T3={t2_pending}")
PYEOF

echo "" | tee -a "$LOG"

# ── Run T3 ───────────────────────────────────────────────────────────────────
echo "[$(date -u)] Running --deep --top $TOP (no --local-ks, uses CYTools CGI)" | tee -a "$LOG"
python3 pipeline_v6.py \
    --deep \
    --top "$TOP" \
    --db "$DB" \
    -w "$WORKERS" \
    2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "[$(date -u)] T3 run complete." | tee -a "$LOG"

# ── Post-run stats ───────────────────────────────────────────────────────────
python3 - "$DB" <<'PYEOF' | tee -a "$LOG"
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
rows = con.execute("""
    SELECT h11, poly_idx, sm_score, has_SM, has_GUT, best_gauge, n_clean, tier_reached
    FROM polytopes WHERE sm_score >= 70
    ORDER BY sm_score DESC, n_clean DESC
    LIMIT 30
""").fetchall()
print("Post-run leaderboard:")
for r in rows:
    sm = 'SM' if r[3] else ('no-SM' if r[3] is not None else 'T2-only')
    gut = '+GUT' if r[4] else ''
    gauge = (str(r[5])[:25] + '…') if r[5] and len(str(r[5])) > 25 else (r[5] or '')
    print(f"  h{r[0]}/P{r[1]:6d}  score={r[2]}  n_clean={r[6]:3d}  tier={r[7]}  [{sm}{gut}]  {gauge}")
PYEOF

# ── Export updated rows for local merge ─────────────────────────────────────
# Export all rows that are now T3 (the newly processed ones) for easy merge
echo "" | tee -a "$LOG"
echo "Exporting t3_results.db for local merge..." | tee -a "$LOG"
python3 - "$DB" <<'PYEOF'
import sqlite3, sys
src = sqlite3.connect(sys.argv[1])
dst = sqlite3.connect('t3_results.db')

# Schema
schema = src.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='polytopes'").fetchone()[0]
dst.execute(schema)
fib_schema = src.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='fibrations'").fetchone()[0]
dst.execute(fib_schema)

# Only export newly T3 rows (T3 were T2 pending in seed — the 17 new ones)
rows = src.execute("SELECT * FROM polytopes WHERE tier_reached='T3'").fetchall()
cols = [r[1] for r in src.execute('PRAGMA table_info(polytopes)').fetchall()]
ph = ', '.join(['?']*len(cols))
col_list = ', '.join(cols)
dst.executemany(f'INSERT OR REPLACE INTO polytopes ({col_list}) VALUES ({ph})', rows)

fibs = src.execute("SELECT * FROM fibrations").fetchall()
fib_cols = [r[1] for r in src.execute('PRAGMA table_info(fibrations)').fetchall()]
if fibs:
    fib_ph = ', '.join(['?']*len(fib_cols))
    fib_list = ', '.join(fib_cols)
    dst.executemany(f'INSERT OR REPLACE INTO fibrations ({fib_list}) VALUES ({fib_ph})', fibs)

dst.commit()
import os
sz = os.path.getsize('t3_results.db')
print(f"t3_results.db: {len(rows)} T3 rows, {len(fibs)} fibration rows, {sz//1024} KB")
PYEOF

echo "" | tee -a "$LOG"
echo "=== DONE: $(date -u) ===" | tee -a "$LOG"
echo ""
echo "Next: scp <codespace>:/workspaces/cytools_project/v6/t3_results.db v6/"
echo "Then: python3 v6/merge_t3_results.py"
