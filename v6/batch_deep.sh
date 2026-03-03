#!/bin/bash
set -e
cd /workspaces/cytools_project/v6
LOG=results/batch_deep.log
mkdir -p results

echo "=== DEEP BATCH START: $(date -u) ===" | tee $LOG
echo "Host: $(hostname) | Workers: 6" | tee -a $LOG

# ── Step 1: Recover h18/h19 stalls ───────────────────────────────────────────
# h19/P438 (prev 81), h18/P315 (prev 80), h19/P390 (prev 80) were overwritten
# by T1-stall rows from the ext mop-up run at 12 workers. Re-scan first 50K at
# 6 workers to avoid Yukawa timeouts. Existing rows upserted (MONOTONIC_MAX).
echo "[$(date -u)] Step 1a: h18 first 50K (recover h18/P315)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 18 --limit 50000 --local-ks -w 6 --top 99999 2>&1 | tail -8 | tee -a $LOG

echo "[$(date -u)] Step 1b: h19 first 50K (recover h19/P438, h19/P390)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 19 --limit 50000 --local-ks -w 6 --top 99999 2>&1 | tail -8 | tee -a $LOG

# ── Step 2: T0 wall mechanistic probe ─────────────────────────────────────────
# Test back-half polytopes at h24 (350K-360K) and h26 (250K-260K) under both
# standard EFF_MAX=22 and relaxed EFF_MAX=24 to characterize the wall.
echo "[$(date -u)] Step 2a: T0 wall probe h24 offset=350K limit=10K (EFF_MAX=22)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 24 --offset 350000 --limit 10000 --local-ks -w 6 --top 99999 2>&1 | tail -4 | tee -a $LOG

echo "[$(date -u)] Step 2b: T0 wall probe h26 offset=250000 limit=10K (EFF_MAX=22)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 26 --offset 250000 --limit 10000 --local-ks -w 6 --top 99999 2>&1 | tail -4 | tee -a $LOG

echo "[$(date -u)] Step 2c: T0 wall probe h26 offset=250000 limit=10K (EFF_MAX=24)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 26 --offset 250000 --limit 10000 --local-ks -w 6 --top 99999 --eff-max 24 2>&1 | tail -4 | tee -a $LOG

echo "[$(date -u)] Step 2d: T0 wall probe h23 offset=340K limit=10K (EFF_MAX=22)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 23 --offset 340000 --limit 10000 --local-ks -w 6 --top 99999 2>&1 | tail -4 | tee -a $LOG

# ── Step 3: EFF_MAX=24 expansion scan ─────────────────────────────────────────
# Re-scan first 50K at h22–h26 with EFF_MAX=24. Polytopes with h11_eff=23–24
# that were previously killed at T0 now get full T0→T2 treatment. Existing
# scored rows are preserved by MONOTONIC_MAX; only new geometry is added.
for h in 22 23 24 25 26; do
    echo "[$(date -u)] Step 3: EFF_MAX=24 h${h} limit=50000..." | tee -a $LOG
    python3 pipeline_v6.py --scan --h11 $h --limit 50000 --local-ks -w 6 --top 99999 --eff-max 24 2>&1 | tail -8 | tee -a $LOG
done

# ── Step 4: T3 deep analysis on top candidates ───────────────────────────────
# Full triangulation stability + fibration classification on top 20 by score.
# Writes tri_c2_stable_frac, tri_n_tested, fibration data back to DB.
echo "[$(date -u)] Step 4: T3 deep analysis top 20..." | tee -a $LOG
python3 pipeline_v6.py --deep --top 20 --local-ks -w 6 2>&1 | tail -20 | tee -a $LOG

echo "=== DONE: $(date -u) ===" | tee -a $LOG
