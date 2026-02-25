#!/bin/bash
# Batch pipeline deep-dive on star candidates from h15/h16/h17 auto_scan
# Launch on Codespace: tmux new-session -d -s pipeline 'bash run_pipeline_stars.sh 2>&1 | tee pipeline_stars.log'

set -e
cd "$(dirname "$0")"
source activate.sh

echo "=== Pipeline Star Deep-Dives ==="
echo "Started: $(date)"
echo ""

CANDIDATES=(
    "15 147"   # h15 #1: 45 clean, su(2)⁴×su(3)²
    "15 256"   # h15 #2: 38 clean, τ=2025, su(7)×su(5)
    "15 387"   # h15 #9: 33 clean, τ=11,400!, su(5)×su(4)
    "16 212"   # h16 #1: 42 clean, su(8)/e7×su(4)
    "16 278"   # h16 max clean: 50 clean, score 23/26
    "16 329"   # h16 #3: 34 clean, 7 ell, su(5)×su(4)×su(3)
    "17 767"   # h17 #1: 59 clean!, su(2)×su(4)×su(2)×su(3)×su(6)
    "17 1033"  # h17 #4: 35 clean, 11 ell, su(2)×su(4)²×su(2)×su(3)
    "17 251"   # h17 #3: 38 clean, τ=539, su(4)×su(9)/e8
)

TOTAL=${#CANDIDATES[@]}
for i in "${!CANDIDATES[@]}"; do
    read -r H11 POLY <<< "${CANDIDATES[$i]}"
    N=$((i+1))
    echo "============================================"
    echo "[$N/$TOTAL] h${H11}/P${POLY}"
    echo "Started: $(date)"
    echo "============================================"
    python pipeline.py --h11 "$H11" --poly "$POLY"
    echo ""
    echo "[$N/$TOTAL] h${H11}/P${POLY} — DONE ($(date))"
    echo ""
done

echo "=== All $TOTAL pipeline runs complete ==="
echo "Finished: $(date)"
