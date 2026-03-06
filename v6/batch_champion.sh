#!/bin/bash
# batch_champion.sh — Full champion deep-physics run for h26/P11670 (score 89).
#
# Three stages (run sequentially inside the CYTools Docker container):
#   1. champion_kodaira.py   — Fibration Kodaira analysis + resolution attempt
#   2. figures.py            — Generate all 8 paper figures from v6 DB
#   3. champion_bundles.py   — SU(4) direct-sum bundle scan, χ=±3
#
# Usage (on hetzner, inside container):
#   cd /workspaces/cytools_project && bash v6/batch_champion.sh
#
# Or from local machine:
#   ssh hetzner 'docker exec funny_davinci bash -c \
#      "cd /workspaces/cytools_project && bash v6/batch_champion.sh" \
#      > /tmp/champion.log 2>&1 &'

set -e
cd "$(dirname "$0")"   # v6/

LOG=results/batch_champion.log
mkdir -p results results/figures

echo "=== CHAMPION BATCH START: $(date -u) ===" | tee "$LOG"
echo "Host: $(hostname) | Cores: $(nproc)" | tee -a "$LOG"
echo "DB: cy_landscape_v6.db ($(du -sh cy_landscape_v6.db 2>/dev/null | cut -f1 || echo '?'))" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# ── Stage 1: Kodaira analysis ─────────────────────────────────────────────────
echo "[$(date -u)] Stage 1: champion_kodaira.py" | tee -a "$LOG"
python3 champion_kodaira.py 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

# ── Stage 2: Figures (requires populated DB — local machine only) ─────────────
DB_SIZE=$(stat -c%s cy_landscape_v6.db 2>/dev/null || echo 0)
if [[ "$DB_SIZE" -gt 1000000 ]]; then
    echo "[$(date -u)] Stage 2: figures.py (all 8 figures)" | tee -a "$LOG"
    python3 figures.py --out-dir results/figures 2>&1 | tee -a "$LOG"
else
    echo "[$(date -u)] Stage 2: SKIPPED — DB is empty/missing ($DB_SIZE bytes). Run figures.py locally." | tee -a "$LOG"
fi
echo "" | tee -a "$LOG"

# ── Stage 3: SU(4) bundle scan ───────────────────────────────────────────────
echo "[$(date -u)] Stage 3: champion_bundles.py (SU(4), k_max=3, n=500K)" | tee -a "$LOG"
python3 champion_bundles.py \
    --rank 4 \
    --k-max 3 \
    --chi-target 3 \
    --n-sample 500000 \
    --max-hoppe 200 \
    2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

# ── Stage 4 (bonus): SU(5) if time allows ────────────────────────────────────
echo "[$(date -u)] Stage 4: champion_bundles.py (SU(5), k_max=3, n=300K)" | tee -a "$LOG"
python3 champion_bundles.py \
    --rank 5 \
    --k-max 3 \
    --chi-target 3 \
    --n-sample 300000 \
    --max-hoppe 100 \
    2>&1 | tee -a results/batch_champion_su5.log
echo "" | tee -a "$LOG"

# ── Stage 5: SU(4) monad scan (k_max=2, 1M samples) ─────────────────────────
echo "[$(date -u)] Stage 5: champion_monads.py (SU(4), k_max=2, n=1M)" | tee -a "$LOG"
python3 champion_monads.py \
    --rank 4 \
    --k-max 2 \
    --n-sample 1000000 \
    --j-tries 30 \
    2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

# ── Stage 6: SU(4) monad k_max=3 (larger space, log to separate file) ────────
echo "[$(date -u)] Stage 6: champion_monads.py (SU(4), k_max=3, n=2M)" | tee -a "$LOG"
python3 champion_monads.py \
    --rank 4 \
    --k-max 3 \
    --n-sample 2000000 \
    --j-tries 50 \
    2>&1 | tee -a results/batch_champion_monads3.log
echo "" | tee -a "$LOG"

echo "=== CHAMPION BATCH COMPLETE: $(date -u) ===" | tee -a "$LOG"
echo "Outputs:" | tee -a "$LOG"
echo "  results/champion_kodaira.json" | tee -a "$LOG"
echo "  results/figures/fig{1..8}*.png" | tee -a "$LOG"
echo "  results/champion_bundles.json" | tee -a "$LOG"
ls -lh results/champion_*.json results/figures/*.png 2>/dev/null | tee -a "$LOG"
