# Pipeline Version History

> Each version lives in its own folder (`v2/`, `v3/`, `v4/`) with independent
> compute modules, DB schema, and results.  Code inherits upward:
> v4 imports from v3, v3 imports from v2.  Databases are **not** migrated.

---

## v2 — Binary Screening at Scale

**Folder**: `v2/`  
**Era**: Initial large-scale scans (h11 = 13–18)  
**Question**: *"Does this polytope have clean bundles?"*

### Architecture

| Tier   | Time     | Purpose                            | Kill rate |
|--------|----------|------------------------------------|-----------|
| T0     | 0.1s     | Geometry pre-filter (h11_eff, gap, Aut) | ~90%  |
| T0.25  | 0.5s     | Early-exit h⁰ ≥ 5 check           | ~70%      |
| T1     | 3–30s    | Full bundle census + divisors + fibrations | ranking |
| T2     | 1–5s     | Kodaira fiber classification + gauge algebra | top ~50 |

### Thresholds

```
EFF_MAX  = 15      # skip h11_eff > 15
GAP_MIN  = 2       # minimum gap for priority track
H0_MIN   = 5       # T0.25 screening signal
AUT_MAX  = 3       # skip |Aut| ≥ 4
```

### Scoring (26-point scale)

```python
SCORE_WEIGHTS = {
    'chi_neg6':       3,   'three_gen':     3,
    'h0_ge3_exists':  3,   'clean_bundles': 5,
    'max_h0':         2,   'swiss_cheese':  3,
    'k3_fibs':        2,   'ell_fibs':      2,
    'dp_divisors':    1,   'd3_diversity':  1,
    'h11_tractable':  1,
}
# Total: 26 pts
```

### Key Files

- `pipeline_v2.py` — orchestrator (T0 → T0.25 → T1 → T2)
- `cy_compute.py` — core math: lattice points, Koszul h⁰, χ search,
  fibrations, swiss cheese, coordinate conversions
- `db_utils.py` — `cy_landscape.db` schema + LandscapeDB class
- `fiber_analysis.py` — Kodaira classification, gauge algebra

### Limitations (found via DB analysis of 93K h18 rows)

- `screen_score` has **zero** predictive power for clean bundle count
- `has_swiss` doesn't predict clean bundles (17.8 avg vs 17.7 without)
- `n_dp` **anti-correlates** with clean count (fewer dP → more clean)
- Binary pass/fail scoring wastes effort on universal properties (χ = −6)
- `EFF_MAX = 15` too conservative: misses viable h11_eff = 16–20 polytopes
- T0.25 and T1 are separate tiers with redundant CYTools setup

---

## v3 — Physics-Driven Continuous Scoring

**Folder**: `v3/`  
**Era**: Physics-aware scans (h11 = 13–21, 6578 polytopes in DB)  
**Question**: *"How close is this geometry to the Standard Model?"*

### What changed from v2

1. **T05 intersection algebra** (NEW tier): extracts Yukawa rank, c₂ positivity,
   volume form structure, and tadpole bound from intersection numbers at ~0.05s
   marginal cost — subsequently merged into T0 after data showed 0% filter rate
2. **T0.25 + T1 merged** into single T1 with adaptive depth (find bundles,
   screen h⁰, count cleans in a 2s time budget)
3. **100-point SM score** replaces 26-point binary checklist
4. **New T2 physics**: LVS compatibility (τ/V^{2/3}), Yukawa texture analysis,
   Mori cone contractions
5. **T3 tier** (NEW): triangulation stability, flux landscape, orientifold checks
6. **EFF_MAX raised** from 15 → 20 (captures h11_eff 16–20 candidates)
7. **Fresh database** — `cy_landscape_v3.db`, not migrated from v2

### Architecture

| Tier | Time    | Purpose                          | Kill rate |
|------|---------|----------------------------------|-----------|
| T0   | 0.1s    | Geometry + intersection algebra  | ~85%      |
| T1   | 0.5s    | Bundle screening (adaptive)      | ~70%      |
| T2   | 3–30s   | Deep physics + SM scoring        | top ~1K   |
| T3   | 30s+    | Full phenomenology + fibers      | top ~50   |

### Thresholds

```
EFF_MAX  = 20      # raised from 15
GAP_MIN  = 2       # same
H0_MIN   = 5       # same
AUT_MAX  = 4       # relaxed from 3
```

### Scoring (100-point scale)

```python
SM_SCORE_WEIGHTS = {
    'chi_match':        10,   # χ = ±6
    'clean_bundles':    15,   # log₂-scaled
    'yukawa_rank':      15,   # texture rank ≥ 3
    'yukawa_hierarchy': 10,   # eigenvalue spread ≥ 10³
    'lvs_compatible':   15,   # τ/V^{2/3} < 0.01
    'fibration_sm':     10,   # SU(3)×SU(2)×U(1) or GUT
    'c2_positive':       5,   # DRS conjecture
    'dp_divisors':       5,   # del Pezzo divisors
    'tadpole_ok':        5,   # |χ/24| ≤ 20
    'mori_blowdown':     5,   # del Pezzo contracting curves
    'h0_diversity':      5,   # distinct h⁰ values
}
# Total: 100 pts
```

### Key Files

- `pipeline_v3.py` — orchestrator (T0 → T1 → T2 → T3)
- `cy_compute_v3.py` — imports v2 core + adds: LVS score, Yukawa texture,
  Mori analysis, divisor classification, SM scoring
- `db_utils_v3.py` — expanded schema (Yukawa, LVS, Mori columns)
- `PIPELINE_V3_SPEC.md` — full specification (331 lines)

### Data Collected

- `cy_landscape_v3.db`: 6,578 polytopes (h11 = 13–21), 1,100 T2-scored
- scanned on GitHub Codespace (4-core) + Hetzner (16-core)

### Scoring Waste Found (motivating v4)

Analysis of the 6,578-polytope v3 DB revealed:
- `chi_match` (10 pts): **universal** — χ = −6 for every candidate, zero discrimination
- `h0_diversity` (5 pts): **anti-correlates** with score (high diversity → lower SM quality)
- `yukawa_hierarchy` was the **dominant discriminator** but only got 10/100 pts
- `lvs_compatible` was all-or-nothing (15 pts) — no grading of LVS quality
- `clean_bundles` saturates above ~50 clean; 15 pts wasted past that

---

## v4 — Evidence-Based Weight Redistribution

**Folder**: `v4/`  
**Era**: Optimized scans (h11 = 22–30), currently running  
**Question**: *"Same physics, sharper scoring, faster pipeline."*

### What changed from v3

#### Scoring overhaul (evidence from 6,578 v3 polytopes)

| Component          | v3 pts | v4 pts | Rationale                                   |
|--------------------|--------|--------|---------------------------------------------|
| chi_match          | 10     | **0**  | Universal (χ = −6 for all), zero discrimination |
| h0_diversity       | 5      | **0**  | Anti-correlates with SM quality              |
| clean_bundles      | 15     | **10** | Saturates above ~50; log₂-scaled            |
| yukawa_rank        | 15     | 15     | Unchanged                                    |
| yukawa_hierarchy   | 10     | **25** | THE key discriminator (90-scorers have >1000×) |
| lvs_compatible     | 15     | —      | Split into two components ↓                  |
| → lvs_binary (NEW) | —      | **5**  | Has swiss cheese structure at all            |
| → lvs_quality (NEW)| —      | **10** | 5-tier τ/V^{2/3} grading                    |
| fibration_sm       | 10     | 5      | Quality not count                            |
| c2_positive        | 5      | **0**  | Merged into dp_divisors context              |
| dp_divisors        | 5      | 5      | Unchanged                                    |
| tadpole_ok         | 5      | 5      | Unchanged                                    |
| mori_blowdown      | 5      | 5      | Unchanged                                    |
| clean_depth (NEW)  | —      | **5**  | Deep clean bundles (high h⁰ + clean)        |
| clean_rate (NEW)   | —      | **5**  | n_clean/n_checked — structural SM-friendliness |
| d3_diversity (NEW) | —      | **5**  | Distinct D³ values in clean bundles          |
| **Total**          | **100**| **100**| Zero points wasted on universal properties   |

#### Yukawa hierarchy grading (25 pts, 6 tiers)

```
≥ 10⁴  → 25 pts     ≥ 10³ → 20 pts     ≥ 500 → 15 pts
≥ 10²  → 10 pts     ≥ 10  →  5 pts     < 10  →  0 pts
```

#### LVS quality grading (10 pts, 5 tiers)

```
τ/V^{2/3} < 0.002 → 10 pts (elite)    < 0.005 →  8 pts
            < 0.01 →  6 pts            < 0.05  →  3 pts
            ≥ 0.05 →  0 pts
```

#### Pipeline efficiency fixes

1. **Gap-priority scheduling at T1**: polytopes sorted by `gap` descending
   before bundle screening.  Data: gap = 2 avg 35s vs gap = 5 avg 4s;
   T1 pass rate 30% (gap = 2) → 79% (gap = 7).  High-gap polytopes
   processed first → faster time-to-first-result.

2. **`imap_unordered(chunksize=1)`**: replaces `pool.map(chunksize=10)` —
   results stream as completed instead of waiting for full batch.

3. **T1 bundle cap** (`T1_BUNDLE_CAP = 500`): uses `find_chi3_bundles_capped`
   instead of uncapped search.  T1 is a screen, not a census; T2 does
   exhaustive analysis.  Prevents O(hour) T1 on h11_eff = 17–20 polytopes.

4. **T1 wall-time limit** (`T1_WALL_SEC = 120`): hard per-polytope timeout.
   Checked every 10 bundles; returns `status='timeout'` with partial data.
   Timeout polytopes with clean hits are promoted to T2.

5. **T1 progress reporting**: prints status every 20 polytopes with
   pass / timeout counts, elapsed time, and ETA.

6. **T05 eliminated as separate tier**: merged into T0 (0% filter rate in
   h11 = 13–18 data; Yukawa density always ≥ 2.0).

### Architecture

| Tier | Time    | Purpose                          | Kill rate |
|------|---------|----------------------------------|-----------|
| T0   | 0.1s    | Geometry + intersection algebra  | ~85%      |
| T1   | 0.5–120s| Bundle screening (capped, wall-timed) | ~55% |
| T2   | 3–30s   | Deep physics + SM scoring        | top ~1K   |
| T3   | 30s+    | Full phenomenology + fibers      | top ~50   |

### Thresholds

```
EFF_MAX        = 20     # same as v3
GAP_MIN        = 2      # same
H0_MIN_T1      = 5      # same
AUT_MAX        = 4      # same
T1_BUDGET_SEC  = 2.0    # adaptive clean counting budget (after first clean hit)
T1_WALL_SEC    = 120    # hard per-polytope wall-time limit
T1_BUNDLE_CAP  = 500    # max bundles to find at T1
```

### Key Files

- `pipeline_v4.py` — orchestrator with gap-priority + wall-time limits
- `cy_compute_v4.py` — imports v3/v2 core + new `compute_sm_score()` with
  v4 weights, 6-tier yukawa grading, 5-tier LVS grading
- `db_utils_v4.py` — same schema as v3 (scoring logic changed, not columns)

### Performance

First h22 scan (632 T0-pass polytopes, 14 workers on Hetzner 16-core):
- T0: 6.7s (148 poly/s)
- T1: 180s (zero timeouts, 281 pass = 44.5%)
- T2: ~7 min (0.7 poly/s), clean bundles flowing

Compare: v4-without-fixes T1 hung indefinitely on h22 (same polytopes).

---

## Version Inheritance

```
v2/cy_compute.py          ← core math (lattice points, Koszul, χ, fibrations)
  ↑ imports
v3/cy_compute_v3.py       ← adds: Yukawa texture, LVS, Mori, divisor classify
  ↑ imports
v4/cy_compute_v4.py       ← adds: new compute_sm_score() with v4 weights

v2/db_utils.py            ← original schema
v3/db_utils_v3.py         ← expanded schema (Yukawa, LVS, Mori columns)
v4/db_utils_v4.py         ← same schema as v3

v2/pipeline_v2.py         ← T0 → T0.25 → T1 → T2
v3/pipeline_v3.py         ← T0 → T1 → T2 → T3 (merged T0.25 into T1)
v4/pipeline_v4.py         ← T0 → T1 → T2 → T3 (gap-priority, wall-time, bundle cap)
```

---

## Compute Environments

| Environment    | Specs          | Used for                      |
|----------------|----------------|-------------------------------|
| Hetzner        | 16-core, 128GB | v2 h18 batch, v4 h22–30 scan  |
| Codespace      | 4-core, 32GB   | v3 h13–24 scans               |
| Local (Dell5)  | Dev, analysis  | DB queries, scoring R&D       |
