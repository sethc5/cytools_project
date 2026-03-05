#!/bin/bash
# batch_t3_sweep2.sh — §27 T3 deep sweep on score=70-73 T2-only candidates
# 628 remaining candidates (score 74-79 all completed in §26b).
# Uses CYTools CGI API (no --local-ks needed).
#
# Usage: bash v6/batch_t3_sweep2.sh
# Env:   WORKERS=14 TOP=628 bash v6/batch_t3_sweep2.sh
# Output: v6/t3_sweep2_results.db (new T3 rows for merge)

set -e
cd "$(dirname "$0")"

DB=cy_landscape_t3_sweep2.db
SEED=t3_sweep2_seed.db
LOG=results/batch_t3_sweep2.log
TOP=${TOP:-628}           # all 628 remaining: score=73(46) + 72(147) + 71(67) + 70(368) ≈ 11.5h
WORKERS=${WORKERS:-14}    # Hetzner i9: 14 workers leave 2 cores for OS

mkdir -p results

# ── Bootstrap DB from seed ──────────────────────────────────────────────────
if [ ! -f "$DB" ]; then
    echo "Copying sweep seed DB → $DB"
    cp "$SEED" "$DB"
fi

echo "=== T3 SWEEP2 START: $(date -u) ===" | tee "$LOG"
echo "Host: $(hostname) | Workers: $WORKERS | Top: $TOP" | tee -a "$LOG"
echo "DB: $DB ($(du -sh $DB | cut -f1))" | tee -a "$LOG"

# ── Pre-run stats ─────────────────────────────────────────────────────────
python3 - "$DB" <<'PYEOF' | tee -a "$LOG"
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
t3  = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T3'").fetchone()[0]
t2  = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T2'").fetchone()[0]
total = con.execute("SELECT COUNT(*) FROM polytopes").fetchone()[0]
print(f"Pre-run: total={total}  T2-pending={t2}  T3-done={t3}")
dist = con.execute("SELECT sm_score, COUNT(*) FROM polytopes WHERE tier_reached='T2' GROUP BY sm_score ORDER BY sm_score DESC").fetchall()
print("Score distribution (T2-only):")
for score, n in dist[:12]:
    print(f"  score={score}: {n}")
PYEOF

echo "" | tee -a "$LOG"

# ── Run T3 sweep ─────────────────────────────────────────────────────────────
echo "[$(date -u)] Running --deep --top $TOP (CGI API, no --local-ks)" | tee -a "$LOG"
python3 pipeline_v6.py \
    --deep \
    --top "$TOP" \
    --db "$DB" \
    -w "$WORKERS" \
    2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "[$(date -u)] T3 sweep complete." | tee -a "$LOG"

# ── Post-run stats ───────────────────────────────────────────────────────
python3 - "$DB" <<'PYEOF' | tee -a "$LOG"
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
t3  = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T3'").fetchone()[0]
t2  = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T2'").fetchone()[0]
print(f"Post-run: T3={t3}  T2-remaining={t2}")
rows = con.execute("""
    SELECT h11, poly_idx, sm_score, has_SM, has_GUT, best_gauge, n_clean, tier_reached
    FROM polytopes WHERE tier_reached='T3'
    ORDER BY sm_score DESC, n_clean DESC LIMIT 40
""").fetchall()
print("All T3-verified (sweep2):")
for r in rows:
    sm = 'SM+GUT' if r[3] and r[4] else ('SM' if r[3] else ('no-SM' if r[3] is not None else '?'))
    gauge = (str(r[5])[:30] + '…') if r[5] and len(str(r[5])) > 30 else (r[5] or '')
    print(f"  h{r[0]}/P{r[1]:6d}  score={r[2]}  n_clean={r[6]:3d}  [{sm}]  {gauge}")
PYEOF

# ── Export results for local merge ─────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "Exporting t3_sweep2_results.db for local merge..." | tee -a "$LOG"
python3 - "$DB" <<'PYEOF'
import sqlite3, sys, os

src = sqlite3.connect(sys.argv[1])
if os.path.exists('t3_sweep2_results.db'):
    os.remove('t3_sweep2_results.db')
dst = sqlite3.connect('t3_sweep2_results.db')

schema = src.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='polytopes'").fetchone()[0]
dst.execute(schema)
fib_schema = src.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='fibrations'").fetchone()[0]
dst.execute(fib_schema)

# Export all T3 rows
rows = src.execute("SELECT * FROM polytopes WHERE tier_reached='T3'").fetchall()
cols = [r[1] for r in src.execute('PRAGMA table_info(polytopes)').fetchall()]
ph = ', '.join(['?']*len(cols))
col_list = ', '.join(cols)
dst.executemany(f'INSERT OR REPLACE INTO polytopes ({col_list}) VALUES ({ph})', rows)

# Export fibrations (without id — let AUTOINCREMENT assign fresh ids at merge)
fibs = src.execute("SELECT * FROM fibrations").fetchall()
fib_all_cols = [r[1] for r in src.execute('PRAGMA table_info(fibrations)').fetchall()]
if fibs:
    fib_ph = ', '.join(['?']*len(fib_all_cols))
    fib_list = ', '.join(fib_all_cols)
    dst.executemany(f'INSERT OR REPLACE INTO fibrations ({fib_list}) VALUES ({fib_ph})', fibs)

dst.commit()
sz = os.path.getsize('t3_sweep2_results.db')
print(f"t3_sweep2_results.db: {len(rows)} T3 rows, {len(fibs)} fib rows, {sz//1024} KB")
PYEOF

echo "" | tee -a "$LOG"
echo "=== DONE: $(date -u) ===" | tee -a "$LOG"
echo ""
echo "Next steps:"
echo "  scp root@95.216.246.55:/tmp/t3_sweep2_results.db v6/"
echo "  OR: docker cp funny_davinci:/workspaces/cytools_project/v6/t3_sweep2_results.db /tmp/ && scp root@95.216.246.55:/tmp/t3_sweep2_results.db v6/"
echo "  python3 v6/merge_t3_results.py --results v6/t3_sweep2_results.db"
