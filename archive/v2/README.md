# v2 — Hetzner Batch Scan (UNFINISHED)

Killed 2026-02-26. Ran on Hetzner 16-core (95.216.246.55) from Feb 23-26.

## What it was
- **v2 architecture**: T0.25 (fast h⁰ scan) → T1 (del Pezzo + swiss cheese + symmetry) → T2 (deep)
- **h11=18 only**, scanning all ~100K polytopes at χ=-6
- 14 workers, ~600s/polytope at T1

## Status when killed
- **T0.25**: Complete — 93,302 polytopes scanned (87,491 + 5,812 offset batch)
- **T1**: 20,599 of ~93K processed (**~22% done**, ~12 more days needed)
- **T2**: 87 polytopes deep-analyzed

## Why killed
1. Only 22% done after 3 days — would need ~12 more days
2. v2 scoring lacks Yukawa hierarchy (the #1 discriminator in v4)
3. h18 already has 144 T2-scored polytopes in v3 DB with full physics
4. Data format incompatible with v3/v4 DB (CSV, different columns)
5. Hetzner 16-core better used for v4 scans

## Files
```
results/
  tier025_h18.csv              3.8M  87,491 rows  T0.25 results (main batch)
  tier025_h18_off100000.csv    266K   5,812 rows  T0.25 results (offset batch)
  tier025_h18_log.txt           72K                T0.25 scan log
  tier025_h18_off100000_log.txt 6.7K               offset batch log
  tier1_h18.csv                2.4M  20,600 rows  T1 results (incomplete)
  tier2_h18.csv                6.0K      88 rows  T2 deep results
  batch_t1_h18_log.txt         1.6M                T1 batch log
  batch_t2_h18_log.txt         8.7K                T2 batch log
```

## Column schemas

### tier025_h18.csv
h11, h21, poly_idx, favorable, h11_eff, max_h0_025, n_chi3_025, ...

### tier1_h18.csv
h11, h21, poly_idx, favorable, h11_eff, gap, n_chi3, n_dp, dp_types,
n_k3_div, n_rigid, has_swiss, n_swiss, best_swiss_tau, best_swiss_ratio,
sym_order, screen_score, elapsed, status, error
