#!/usr/bin/env bash
# §30 T4 deep triangulation on top 37 (sm_score >= 80)
# 500 tri samples (vs 50 at T3), 100 stability samples (vs 20 at T3)
# Est runtime: ~30-60 min with 14 workers (37 polytopes parallel)

set -euo pipefail

WORKERS=${WORKERS:-14}
TRI_SAMPLES=${TRI_SAMPLES:-500}
STAB_SAMPLES=${STAB_SAMPLES:-100}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="${SCRIPT_DIR}/results/batch_t4_nohup.log"
mkdir -p "${SCRIPT_DIR}/results"

echo "=== §30 T4 Deep Triangulation ===" | tee "$LOG"
echo "Started: $(date -u)" | tee -a "$LOG"
echo "Workers: $WORKERS  |  Tri samples: $TRI_SAMPLES  |  Stab samples: $STAB_SAMPLES" | tee -a "$LOG"
echo "" | tee -a "$LOG"

cd "$SCRIPT_DIR"

python3 t4_deep.py \
    --workers "$WORKERS" \
    --tri-samples "$TRI_SAMPLES" \
    --stab-samples "$STAB_SAMPLES" \
    --out-db t4_results.db \
    2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "=== DONE: $(date -u) ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Merge with:  python3 v6/merge_t4_results.py --results v6/t4_results.db" | tee -a "$LOG"
