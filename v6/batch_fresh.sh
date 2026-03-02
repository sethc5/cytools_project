#!/bin/bash
set -e
cd /workspaces/cytools_project/v6
LOG=results/batch_fresh.log
mkdir -p results

echo "=== FRESH SCAN START: $(date -u) ===" | tee $LOG

# Round 1: Sweet spot h11 levels — 50K each, priority order by candidate density
for h in 26 22 21 25 24 23; do
    echo "[$(date -u)] h${h} limit=50000..." | tee -a $LOG
    python3 pipeline_v6.py --scan --h11 $h --limit 50000 --local-ks -w 14 --top 99999 2>&1 | tail -8 | tee -a $LOG
done

# Round 2: Extended range — 30K each
for h in 20 27 28 29 30; do
    echo "[$(date -u)] h${h} limit=30000..." | tee -a $LOG
    python3 pipeline_v6.py --scan --h11 $h --limit 30000 --local-ks -w 14 --top 99999 2>&1 | tail -8 | tee -a $LOG
done

# Round 3: T2 backlog sweep — Yukawa retry on full T1 pool (now with fix)
echo "[$(date -u)] T2 backlog sweep h20-30..." | tee -a $LOG
python3 pipeline_v6.py --scan --h11 20 30 --resume --top 99999 --local-ks -w 14 2>&1 | tail -10 | tee -a $LOG

echo "=== DONE: $(date -u) ===" | tee -a $LOG
