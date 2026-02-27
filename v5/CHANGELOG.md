# v5 Pipeline Changelog

## v5.2 — 2026-02-27: MONOTONIC_MAX Score Drift Fix

### Bug: Score regression after rescanning existing polytopes

When the pipeline rescans polytopes already in the DB, `MONOTONIC_MAX`
columns (`n_clean`, `yukawa_rank`, `n_bundles_checked`, etc.) correctly
preserve the higher of old vs new values. But `sm_score` was computed
from the T2 worker's local data (which might have lower values if the
fresh CYTools run found fewer clean bundles, e.g. different triangulation
ordering), then unconditionally overwritten in the DB.

**Example:** P874 previously had `n_clean=14 → score=87`. A fresh T2 run
found `n_clean=6 → score=84`. The DB kept `n_clean=14` (MONOTONIC_MAX)
but stored `sm_score=84` from the latest T2 worker. The score became
inconsistent with the preserved metrics.

### Fix

1. **Post-upsert rescore:** After all T2 results are upserted, the
   pipeline reads each polytope's merged DB row and recomputes
   `compute_sm_score()` from the MAX-preserved values. This ensures
   the score always reflects the best-known metrics.

2. **T2 tracks `first_clean_at`:** The T2 worker now records the index
   of the first clean bundle found in its full census, matching the T1
   field. This feeds the `clean_depth` scoring component (5 pts).

### Impact

Champions P874/P186 restored from 84→87. All polytopes with prior T2
data that were rescanned will have consistent scores.

---

## v5.1 — 2026-02-27: KS Fetch Limit + Coverage Fix

### Critical Bug: 1000-polytope cap

`cytools.fetch_polytopes()` defaults to `limit=1000`, silently capping
queries to the first 1,000 polytopes per (h11, h21) pair from the KS web
server. The actual populations at chi=−6 are **10,000–50,000+** per h11
level. Our entire 21K-polytope database was the first ~2% of each bucket,
returned in a fixed deterministic order (by lattice point count).

### Fix: --limit CLI argument

Added `--limit N` to all pipeline modes (scan, ladder, deep):
- `--scan --h11 28 --limit 10000` scans the first 10K polytopes at h28
- `--deep --top 20 --limit 10000` ensures deep mode can access polytopes
  with `poly_idx ≥ 1000` (auto-adjusts limit to `max(limit, idx+1)`)
- Default remains 1000 for backward compatibility

### Impact

The KS server returns polytopes sorted by combinatorial complexity (number
of lattice points, then vertices). First-1000 polytopes have a slight bias
toward fewer points (mean 32.9 vs 34.2 for batch 2 at h28). The scoring
distribution may differ at higher indices. Deeper scans will reveal
whether our h28 champions are robust or artifacts of positional bias.

---

## v5.0 — 2026-02-27: Scoring Refinement + Triangulation Stability

Based on comprehensive analysis of 19,000 polytopes (1,300 T2-scored) across
h11=22–40. All changes driven by Pearson correlations, distributional evidence,
and the h40-50 dead-zone finding (gap=0, 0% T0 pass beyond h≈37).

### Scoring Weight Changes (total remains 100)

| Component | v4.1 | v5.0 | Rationale |
|-----------|------|------|-----------|
| fibration_sm | 3 | **0 (REMOVED)** | Only 3 polytopes out of 19K had SM gauge group via fibration. n_k3_fib anti-correlates (r=−0.22). 3 points permanently stranded → removed entirely. |
| rank_sweet_spot | — | **3 (NEW)** | Yukawa rank 140-159 is the SM sweet spot for h11_eff=18-22. Graded: 140-159→3, 130-139→2, 120-129→1. |
| mori_blowdown | 5 (binary) | **5 (graded)** | Now uses n_dp_contract/n_mori_rays fraction instead of binary yes/no. ≥0.9→5, ≥0.7→4, ≥0.5→3, ≥0.3→2, else→1. Better discrimination. |

### Unchanged Components

- clean_bundles: 10 (log₂ scaled)
- yukawa_rank: 15
- yukawa_hierarchy: 27
- lvs_binary: 5
- lvs_quality: 10
- vol_hierarchy: 5
- tadpole_ok: 5
- d3_diversity: 5
- clean_depth: 5
- clean_rate: 5

### New Feature: compute_tri_stability()

Added `compute_tri_stability(polytope, n_samples=20)` to cy_compute_v5.py:
- Tests 20 random triangulations vs default placing triangulation
- Compares c₂ vector (round to 8 decimals) and κ nonzero pattern (frozenset hash)
- Returns: `tri_n_tested`, `tri_c2_stable_frac`, `tri_kappa_stable_frac`
- Integrated into T3 deep pass (`run_deep`)
- Lightweight complement to the existing property-level `check_triangulation_stability()`

### DB Schema: v5 Migration

Three new columns added to polytopes table (ALTER TABLE migration for existing DBs):
- `tri_n_tested INTEGER` — number of random tris tested
- `tri_c2_stable_frac REAL` — fraction matching default c₂
- `tri_kappa_stable_frac REAL` — fraction matching default κ nonzero pattern

The `_migrate()` method in `db_utils_v5.py` handles this automatically when
opening an existing v4 database. Safe to call multiple times.

### Architecture

v5 shares the same database as v4 (`v4/cy_landscape_v4.db`) — this is a
scoring and analysis upgrade, not a schema break. The v4/ folder is preserved
unchanged as a reference implementation.

### Impact

- 0 stranded points (was 3 for fibration_sm in v4.1)
- Mori blowdown now provides 5-level discrimination instead of binary
- rank_sweet_spot captures the Yukawa rank distribution peak
- tri_stability gives quantitative stability data for paper candidates

---

## Prior versions

See `v4/CHANGELOG.md` for v4.0 and v4.1 history.
