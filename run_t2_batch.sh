#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  run_t2_batch.sh — Run Tier 2 deep screening in parallel batches
#
#  Designed for GitHub Codespace (4-core, 16GB).
#  Splits 157 T2-worthy candidates (≥3 clean in T1.5 probe) into
#  4 parallel pipes, each writing its own CSV shard.
#
#  Usage:
#    ./run_t2_batch.sh          # launch all 4 pipes
#    ./run_t2_batch.sh merge    # merge shards after all complete
#    ./run_t2_batch.sh status   # check running pipes
#
#  Estimated time: ~40 minutes (4 parallel pipes on 4 cores)
# ═══════════════════════════════════════════════════════════════════

set -e

CSV15="results/tier15_screen_results.csv"
TOTAL=157   # T2-worthy candidates from T1.5 (≥3 clean in probe)
PIPES=4
BATCH_SIZE=$(( (TOTAL + PIPES - 1) / PIPES ))  # ceiling division = 40

if [[ "$1" == "status" ]]; then
    echo "=== T2 batch pipe status ==="
    for i in 1 2 3 4; do
        log="results/tier2_batch_${i}.log"
        csv="results/tier2_batch_${i}.csv"
        if [[ -f "$log" ]]; then
            done_count=$(grep -c "screen_polytope_deep" "$log" 2>/dev/null || echo 0)
            last=$(tail -1 "$log" 2>/dev/null)
            printf "  Pipe %d: %s  (last: %s)\n" "$i" \
                "$(wc -l < "$csv" 2>/dev/null || echo '0') rows in CSV" \
                "$(echo "$last" | head -c 60)"
        else
            echo "  Pipe $i: not started"
        fi
    done
    # Check if any python3 tier2 processes running
    echo ""
    echo "=== Running processes ==="
    ps aux | grep "tier2_screen" | grep -v grep || echo "  (none)"
    exit 0
fi

if [[ "$1" == "merge" ]]; then
    echo "=== Merging T2 batch shards ==="
    OUT="results/tier2_full_results.csv"
    
    # Take header from first shard
    head -1 results/tier2_batch_1.csv > "$OUT"
    
    # Append data rows from all shards, re-sort by tier2_score
    for i in 1 2 3 4; do
        csv="results/tier2_batch_${i}.csv"
        if [[ -f "$csv" ]]; then
            tail -n +2 "$csv" >> "$OUT.tmp"
            echo "  Added $(( $(wc -l < "$csv") - 1 )) rows from batch $i"
        fi
    done
    
    # Sort by tier2_score (column 6) descending, then by clean_h0_3 (col 7) descending
    head -1 "$OUT" > "$OUT.sorted"
    sort -t',' -k6,6rn -k7,7rn "$OUT.tmp" >> "$OUT.sorted"
    mv "$OUT.sorted" "$OUT"
    rm -f "$OUT.tmp"
    
    # Re-number ranks
    python3 -c "
import csv
rows = list(csv.DictReader(open('$OUT')))
with open('$OUT', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    for i, r in enumerate(rows, 1):
        r['rank'] = i
        w.writerow(r)
print(f'  Merged {len(rows)} results into $OUT')
"
    
    # Also append the original T2 top-20 results
    if [[ -f "results/tier2_screen_results.csv" ]]; then
        echo ""
        echo "  Original T2 (top 20 from T1): results/tier2_screen_results.csv"
        echo "  New T2 (157 from T1.5):       $OUT"
        echo ""
        echo "  To combine both into one master file:"
        echo "    head -1 $OUT > results/tier2_master.csv"
        echo "    tail -n +2 results/tier2_screen_results.csv >> results/tier2_master.csv"  
        echo "    tail -n +2 $OUT >> results/tier2_master.csv"
    fi
    exit 0
fi

# ═══════════════════════════════════════════════════════════════════
#  Launch 4 parallel pipes
# ═══════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════"
echo "  Launching $PIPES parallel T2 pipes  ($BATCH_SIZE candidates each)"
echo "  Source: $CSV15 (T2-worthy: ≥3 clean in 300-bundle probe)"
echo "  Estimated time: ~40 minutes"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Activate venv if present
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

for i in $(seq 1 $PIPES); do
    offset=$(( (i - 1) * BATCH_SIZE ))
    out_csv="results/tier2_batch_${i}.csv"
    log_file="results/tier2_batch_${i}.log"
    
    echo "  Pipe $i: offset=$offset, batch=$BATCH_SIZE → $out_csv"
    
    python3 -u tier2_screen.py \
        --csv15 "$CSV15" \
        --top $TOTAL \
        --min-clean 3 \
        --offset $offset \
        --batch $BATCH_SIZE \
        --out "$out_csv" \
        2>&1 | tee "$log_file" &
    
    # Small delay to stagger CYTools database access
    sleep 2
done

echo ""
echo "  All $PIPES pipes launched. Monitor with:"
echo "    ./run_t2_batch.sh status"
echo "    tail -f results/tier2_batch_1.log"
echo ""
echo "  When all finish:"
echo "    ./run_t2_batch.sh merge"
echo ""

wait
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  All pipes completed!  Run: ./run_t2_batch.sh merge"
echo "═══════════════════════════════════════════════════════════════"
