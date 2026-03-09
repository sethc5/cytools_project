#!/usr/bin/env bash
# b37_hetzner.sh — B-37 low-h¹¹ T2 completion on Hetzner
#
# Runs T2 resumption for h17-h19 (T1 backlog).
# Requires local KS files on Hetzner at v6/ks_raw/chi6/.
#
# Usage (on Hetzner, inside project dir):
#   bash b37_hetzner.sh 2>&1 | tee results/b37_hetzner_$(date +%Y%m%d_%H%M%S).log &
#
# Expected runtime: ~3-6h total on Hetzner (14-core i9)
# Expected new T2 entries: ~2000-4000 (most T1 will fail T2 bundle screen)

set -euo pipefail
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true

DB="v6/cy_landscape_v6.db"
PY="python3 v6/pipeline_v6.py"
WORKERS=12
LOCAL_KS="--local-ks"

echo "=== B-37 Low-h¹¹ T2 completion on Hetzner ==="
echo "Start: $(date)"
echo "DB: $DB"
echo "Workers: $WORKERS"
echo ""

# --- h17: 1069 T1 entries, max_idx=36591 ---
echo "--- h17: T2 resume (1069 T1 entries, max_idx=36591) ---"
$PY --scan --h11 17 --resume $LOCAL_KS -w $WORKERS --limit 37000 --db "$DB" \
    2>&1 | tail -20
echo "h17 done: $(date)"
echo ""

# --- h18: 8611 T1 entries, max_idx=98583 ---
echo "--- h18: T2 resume (8611 T1 entries, max_idx=98583) ---"
$PY --scan --h11 18 --resume $LOCAL_KS -w $WORKERS --limit 99000 --db "$DB" \
    2>&1 | tail -20
echo "h18 done: $(date)"
echo ""

# --- h19: 13077 T1 entries, max_idx=162537 ---
echo "--- h19: T2 resume (13077 T1 entries, max_idx=162537) ---"
$PY --scan --h11 19 --resume $LOCAL_KS -w $WORKERS --limit 163000 --db "$DB" \
    2>&1 | tail -20
echo "h19 done: $(date)"
echo ""

# --- Summary ---
echo "=== B-37 Hetzner run complete: $(date) ==="
sqlite3 "$DB" "
SELECT h11,
       COUNT(*) as n_t2,
       SUM(CASE WHEN sm_score >= 70 THEN 1 ELSE 0 END) as n_t3,
       MAX(sm_score) as max_score
FROM polytopes
WHERE h11 BETWEEN 17 AND 19 AND sm_score IS NOT NULL
GROUP BY h11;"
