# Pipeline v6 — Changelog

## v6.0 (2025-06-30)

**Base:** v5.2 (not v4). Inherits all v5 fixes + features.

### Inherited from v5

- **`first_clean_at` fix** (v5.2): T2 worker tracks bundle index of first
  clean hit. Previously always NULL → `clean_depth` scored 0.
- **MONOTONIC_MAX rescore** (v5.2): post-upsert rescore in `_run_t2_parallel`
  reads merged DB rows and recomputes scores, preventing drift when
  monotonic columns (n_clean, yukawa_rank) take MAX of old/new values
  but sm_score was overwritten with stale data.
- **`compute_tri_stability()`** (v5.0): c₂/κ hash stability across 20 random
  triangulations. Integrated into T3 deep pass.
- **`rank_sweet_spot`** (v5.0): 3 pts for Yukawa rank 140–159 sweet spot.
- **Graded `mori_blowdown`** (v5.0): fraction-based contraction scoring,
  replacing binary yes/no check.
- **DB migration** for tri_stability columns (v5.0).
- **`--limit`** CLI argument (v5.1): KS fetch limit with auto-adjust in deep mode.

### Bug Fix — Import Path

v5 imports from `v2/cy_compute.py` but the actual location is
`archive/v2/cy_compute.py`. v6 fixes this by adding `archive/v2/` to
`sys.path` before importing any v5 code. This makes v6 runnable standalone
without manual path hacks.

### Scoring Changes (Audit-Validated, 501K Polytopes)

| Component          | v5   | v6   | Change |
|--------------------|------|------|--------|
| `clean_bundles`    |  10  |  10  | —      |
| `yukawa_rank`      |  15  |  15  | —      |
| `yukawa_hierarchy` |  27  |  30  | +3, extended top brackets |
| `lvs_binary`       |   5  |   0  | Removed (96.1% pass) |
| `lvs_quality`      |  10  |  15  | +5, 7-tier grading |
| `rank_sweet_spot`  |   3  |   3  | —      |
| `vol_hierarchy`    |   5  |   7  | +2, better graded |
| `tadpole_ok`       |   5  |   0  | Removed (100% pass) |
| `mori_blowdown`    |   5  |   2  | −3, keeps fraction grading |
| `d3_diversity`     |   5  |   5  | —      |
| `clean_depth`      |   5  |   5  | —      |
| `clean_rate`       |   5  |   5  | —      |
| **`bundle_quality`** | — |   3  | NEW: conjunction of depth + rate |
| **Total**          | 100  | 100  | Zero-sum reallocation |

### Dead Component Removal Rationale

1. **`tadpole_ok`** (−5): `chi/24 = −6/24 = −0.25` for ALL χ=−6 polytopes.
   This is a topological constant, not the real D3-brane tadpole bound.
   100% pass rate → zero discrimination.

2. **`lvs_binary`** (−5): `has_swiss` passes 96.1% of T2-scored polytopes.
   Near-universal → near-zero discrimination. Points absorbed into
   expanded `lvs_quality` (7-tier grading of τ/V^{2/3} ratio).

3. **`mori_blowdown`** (−3): 99.7% pass even with v5's fraction grading.
   Reduced to 2 pts, keeps grading.

### New Component — `bundle_quality`

Conjunction signal rewarding BOTH depth AND rate:
- `n_clean ≥ 20` AND `clean_rate ≥ 0.03` → 3 pts
- `n_clean ≥ 10` AND `clean_rate ≥ 0.02` → 2 pts
- `n_clean ≥ 5`  AND `clean_rate ≥ 0.01` → 1 pt

This differs from the separate `clean_depth` and `clean_rate` components
which reward each dimension independently.

### Architecture

Unchanged from v5:
- `db_utils_v6.py` — Thin wrapper re-exporting v5's LandscapeDB
- `cy_compute_v6.py` — Imports v5 compute functions, overrides scoring only
- `pipeline_v6.py` — Full pipeline (v5 structure + v6 scoring + fixed imports)
