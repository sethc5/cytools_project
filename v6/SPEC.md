# Pipeline v6 — Specification

## Overview

v6 iterates on **v5** (not v4), inheriting all v5 fixes and features,
then applying audit-validated scoring changes from the 501K-polytope DB
analysis. It also fixes v5's broken import path (`v2/` → `archive/v2/`).

**Database compatibility:** Same schema as v4/v5 (same DB file).
Existing data is preserved; `--rescore` recomputes all SM scores in place.

---

## Inherited from v5

- **`first_clean_at` fix** (v5.2): T2 worker tracks first clean bundle index
- **MONOTONIC_MAX rescore** (v5.2): post-upsert rescore from merged DB row
  prevents score drift when rescanning existing polytopes
- **`compute_tri_stability()`** (v5.0): c₂/κ hash stability across random
  triangulations, integrated into T3 deep pass
- **`rank_sweet_spot`** (v5.0): 3 pts for Yukawa rank 140–159 sweet spot
- **Graded `mori_blowdown`** (v5.0): fraction-based contraction scoring
- **DB migration** for `tri_n_tested`, `tri_c2_stable_frac`, `tri_kappa_stable_frac`
- **`--limit`** CLI argument (v5.1) with auto-adjust in `run_deep`

## Bug Fix — v5 Import Path

**Problem:** v5's `cy_compute_v5.py` imports from `v2/cy_compute.py` but the
actual location is `archive/v2/cy_compute.py`. This causes `ModuleNotFoundError`
when running v5 standalone.

**Fix:** v6 imports from `archive/v2/` (same as v4's working path).

---

## Scoring Changes from v5 (Audit-Validated)

### 1. Remove Dead Component — `tadpole_ok` (5 pts → 0 pts)

`chi_over_24 = χ/24 = −6/24 = −0.25` always → 100% pass → zero discrimination.
This is topological χ/24, not the real D3-brane tadpole bound (which requires
flux data). 5 freed points redistributed to discriminating components.

### 2. Merge `lvs_binary` into `lvs_quality` (5+10 → 0+15 pts)

`lvs_binary` (has_swiss) passes 96.1% of scored polytopes → near-zero
discrimination. Absorbed into expanded `lvs_quality` with a richer 7-tier
grading ladder:
- `< 0.001` → 15 (superb)
- `< 0.002` → 13 (elite)
- `< 0.005` → 10 (excellent)
- `< 0.01`  →  8 (good)
- `< 0.03`  →  5 (decent)
- `< 0.05`  →  3 (marginal)
- `≥ 0.05`  →  0

### 3. Reduce `mori_blowdown` (5 pts → 2 pts)

99.7% pass (4,572/4,588) even with v5's graded scoring. The 3 freed points
go to better discriminators. v6 keeps v5's fraction-based grading but caps
the component at 2 pts.

### 4. Upweight `yukawa_hierarchy` (27 → 30 pts)

THE key discriminator (Pearson r=+0.31). Extended top brackets:
- `≥ 50000` → 30 pts (exceptional)
- `≥ 10000` → 27 pts (elite)
- `≥ 1000`  → 22 pts
- `≥ 500`   → 17 pts
- `≥ 100`   → 12 pts
- `≥ 10`    →  5 pts

### 5. Upweight `vol_hierarchy` (5 → 7 pts)

Independent signal, better graded:
- `≥ 10000` → 7 pts
- `≥ 1000`  → 5 pts
- `≥ 100`   → 3 pts
- `≥ 10`    → 1 pt

### 6. New Component — `bundle_quality` (3 pts)

Rewards polytopes strong on BOTH depth and rate (conjunction signal):
- `n_clean ≥ 20` AND `clean_rate ≥ 0.03` → 3 pts
- `n_clean ≥ 10` AND `clean_rate ≥ 0.02` → 2 pts
- `n_clean ≥ 5`  AND `clean_rate ≥ 0.01` → 1 pt

---

### Weight Summary (100 pts total)

| Component         | v5   | v6   | Δ   | Rationale |
|-------------------|------|------|-----|-----------|
| clean_bundles     | 10   | 10   | —   | log₂ scaled, still informative |
| yukawa_rank       | 15   | 15   | —   | Remains strong signal |
| yukawa_hierarchy  | 27   | 30   | +3  | THE key discriminator |
| lvs_binary        |  5   |  0   | −5  | Merged into lvs_quality |
| lvs_quality       | 10   | 15   | +5  | Expanded grading ladder |
| rank_sweet_spot   |  3   |  3   | —   | Yukawa rank sweet spot (from v5) |
| vol_hierarchy     |  5   |  7   | +2  | Better graded |
| tadpole_ok        |  5   |  0   | −5  | Dead (100% pass) — removed |
| mori_blowdown     |  5   |  2   | −3  | Near-dead — reduced, keeps fraction grading |
| d3_diversity      |  5   |  5   | —   | Decent discrimination |
| clean_depth       |  5   |  5   | —   | Properly populated (v5.2 fix) |
| clean_rate        |  5   |  5   | —   | Structural quality signal |
| **bundle_quality**|  —   |  3   | +3  | NEW: conjunction signal |
| **Total**         |**100**|**100**| 0  | Zero-sum reallocation |

---

## Architecture (Unchanged from v5)

```
T0  (0.1s/poly)   Geometry + intersection algebra      kills ~85%
T1  (0.5s/poly)   Bundle screening (capped)            kills ~70%
T2  (3-30s/poly)  Deep physics + scoring (v6 weights)  top ~1K
T3  (30s+/poly)   Full phenomenology + tri stability    top ~50
```

## Pipeline Modes

```
--ladder --h11 13 30                 T0 only, fast landscape mapping
--scan   --h11 19                    Full T0→T2 for one h¹¹
--scan   --h11 28 --limit 10000      Scan first 10K polytopes at h28
--deep   --top 50                    T3 on top candidates
--rescore                            Recompute SM scores (v6 weights)
```

## Files

| File | Description |
|------|-------------|
| `SPEC.md` | This document |
| `CHANGELOG.md` | Version history |
| `db_utils_v6.py` | Database layer (imports from v5, same schema + migration) |
| `cy_compute_v6.py` | Computation layer (imports v5 functions, overrides scoring) |
| `pipeline_v6.py` | Pipeline (inherits v5 structure, v6 scoring, fixed import) |

## Compatibility

- **DB:** Same schema as v4/v5. Points at `v4/cy_landscape_v4.db` directly.
  `--rescore` updates all T2/T3 rows with v6 scoring.
- **Imports:** v6 → `archive/v2/cy_compute.py` for base CYTools functions
  (fixes v5's broken `v2/` path).
- **Python:** 3.10+ with CYTools installed.
