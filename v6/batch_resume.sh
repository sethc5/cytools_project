#!/bin/bash
set -e
cd /workspaces/cytools_project/v6
LOG=results/batch_resume.log
mkdir -p results

echo "=== RESUME BATCH START: $(date -u) ===" | tee $LOG
echo "Host: $(hostname) | Workers: 6" | tee -a $LOG
echo "Target: T1-backlog T2 sweep h20-h25 (~6799 polytopes)" | tee -a $LOG

# ── T2 sweep of T1 backlog ────────────────────────────────────────────────────
# These polytopes passed T1 (status='pass', tier_reached='T1') but never got
# T2 scoring. --resume queries tier_reached='T1' AND status='pass' per h11
# and feeds them directly to T2 — no T0/T1 re-run.
# Estimated wall time at 6 workers: ~118 min total.
for h in 20 21 22 23 24 25; do
    echo "[$(date -u)] Resuming T2 for h${h}..." | tee -a $LOG
    python3 pipeline_v6.py --resume --h11 $h --local-ks -w 6 --top 99999 2>&1 | tail -8 | tee -a $LOG
    echo "[$(date -u)] h${h} done." | tee -a $LOG
done

echo "=== DONE: $(date -u) ===" | tee -a $LOG
