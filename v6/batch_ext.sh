#!/bin/bash
set -e
cd /workspaces/cytools_project/v6
LOG=results/batch_ext.log
mkdir -p results

echo "=== EXT SCAN START: $(date -u) ===" | tee $LOG
echo "Host: $(hostname) | Workers: 12" | tee -a $LOG

# Step 0: Mop up unscored T2 residuals (~322 rows, ~15-20 min)
echo "[$(date -u)] T2 mop-up h13-40 --resume..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 13 40 --resume --top 99999 --local-ks -w 12 2>&1 | tail -10 | tee -a $LOG

# Step 1: h25 — finish the KS universe (362K→424K, ~62K new polytopes, ~3 hr)
echo "[$(date -u)] h25 offset=362000 limit=62000 (finish KS universe)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 25 --offset 362000 --limit 62000 --local-ks -w 12 --top 99999 2>&1 | tail -8 | tee -a $LOG

# Step 2: h24 — finish the KS universe (350K→438K, ~88K new polytopes, ~4 hr)
echo "[$(date -u)] h24 offset=350000 limit=88000 (finish KS universe)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 24 --offset 350000 --limit 88000 --local-ks -w 12 --top 99999 2>&1 | tail -8 | tee -a $LOG

# Step 3: h26 — fresh pipeline deep scan (50K→200K, ~150K polytopes, ~5 hr)
# Covers old-DB range 50K-200K with clean pipeline + new territory
echo "[$(date -u)] h26 offset=50000 limit=150000 (clean + extend)..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 26 --offset 50000 --limit 150000 --local-ks -w 12 --top 99999 2>&1 | tail -8 | tee -a $LOG

echo "=== DONE: $(date -u) ===" | tee -a $LOG
