# Pipeline Version History

> Active code lives in `v4/` and `v5/`.  Legacy versions (`v2/`, `v3/`) are
> archived in `archive/v2/` and `archive/v3/`.  Code inherits upward:
> v5 imports from v4, v4 from v3, v3 from v2.  Databases are **not**
> migrated across major versions (v5 shares v4's DB by design).

---

## v2 — Binary Screening at Scale

**Folder**: `archive/v2/`  
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

**Folder**: `archive/v3/`  
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
**Era**: h22–30 scans (9K polytopes, 1,134 T2-scored)
**Question**: *"Same physics, sharper scoring, faster pipeline."*

### What changed from v3

#### v4.0 Scoring overhaul (evidence from 6,578 v3 polytopes)

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

## v4.1 — Evidence-Based Scoring Redistribution

**Folder**: `v4/` (same code, weights updated in-place)
**Era**: h22–40 scan complete (19K polytopes, 1,300 T2-scored)
**Trigger**: Analysis of 9,000 v4.0 polytopes revealed scoring waste

### What changed from v4.0

| Component | v4.0 | v4.1 | Rationale |
|-----------|------|------|-----------|
| dp_divisors | 5 | **0** | n_dp anti-correlates with score (r=−0.19); elite polytopes avg 5.0 vs pop 6.5 |
| fibration_sm | 5 | **3** | n_k3_fib anti-correlates (r=−0.22); keep SM gauge signal only |
| vol_hierarchy | — | **5 (NEW)** | vol_h > 1000 polytopes avg 6.5 pts higher (n=203 vs n=71); strong unscored predictor |
| yukawa_hierarchy | 25 | **27** | Absorbed 2 freed points; still the dominant discriminator (r=+0.31) |

### Thresholds

```
EFF_MAX  = 22      # raised from 20 — 46% of score-75+ were at the ceiling
```

EFF_MAX=22 impact: h26 T0 pass rate doubled (142→282), h27 +80%.

### Scan Results

Completed h26–40 with 14 workers (~16 min total). h37+ effectively barren.
New top score **84** at h28 and h30 (unlocked by EFF_MAX=22). Database grew
to 19K scored polytopes.

---

## v5 — Scoring Refinement + Triangulation Stability (current)

**Folder**: `v5/`
**Era**: h20–40 deep scans (70K polytopes, 1,787 T2-scored)
**Database**: shares `v4/cy_landscape_v4.db` — scoring upgrade, not schema break
**Question**: *"Which candidates survive triangulation variation?"*

### What changed from v4.1

#### v5.0 — Scoring changes (total remains 100)

| Component | v4.1 | v5 | Rationale |
|-----------|------|----|-----------|
| fibration_sm | 3 | **0 (REMOVED)** | Only 3 of 19K polytopes had SM gauge group via fibration. 3 pts permanently stranded for 99.98% of candidates. |
| rank_sweet_spot | — | **3 (NEW)** | Yukawa rank 140–159 is the SM sweet spot for h11_eff=18–22. Graded: 140-159→3, 130-139→2, 120-129→1. |
| mori_blowdown | 5 (binary) | **5 (graded)** | Now fraction-based (n_dp_contract / n_mori_rays): ≥0.9→5, ≥0.7→4, ≥0.5→3, ≥0.3→2, >0→1. |
| yukawa_rank | 15 | 15 | Bug fix: `texture_rank=0` (falsy) fell through `or` to κ triple count, inflating 194 polytopes by +10 to +18. Now uses `is None` check. |

#### v5.0 — New feature: triangulation stability (T3)

`compute_tri_stability(polytope, n_samples=20)`:
- Tests 20 random FRST triangulations vs default placing triangulation
- Compares c₂ vector hash and κ nonzero pattern hash
- Returns `tri_c2_stable_frac` and `tri_kappa_stable_frac`
- Three new DB columns: `tri_n_tested`, `tri_c2_stable_frac`, `tri_kappa_stable_frac`
- Auto-migrated via `_migrate()` in db_utils_v5.py

#### v5.1 — KS fetch limit fix

CYTools `fetch_polytopes()` has a hidden `limit=1000` default. All prior
scans retrieved only the first 1,000 of ~50,000+ polytopes per h¹¹ from
the KS web server. Added `--limit N` CLI argument to all pipeline modes.

#### v5.2 — MONOTONIC_MAX score drift fix

When rescanning existing polytopes, `MONOTONIC_MAX` columns (n_clean,
yukawa_rank, etc.) correctly preserve higher values, but `sm_score` was
computed from the T2 worker's stale local data and unconditionally
overwritten. Fix: post-upsert rescore reads merged DB row and recomputes
`compute_sm_score()`. Also added `first_clean_at` tracking in T2.

### Scoring (100-point scale, v5.2 current)

```python
SM_SCORE_WEIGHTS = {
    'clean_bundles':    10,   # log₂ scaled (saturates ~50)
    'yukawa_rank':      15,   # texture rank ≥ 3
    'yukawa_hierarchy': 27,   # eigenvalue spread — THE discriminator
    'lvs_binary':        5,   # has Swiss cheese structure
    'lvs_quality':      10,   # τ/V^{2/3} ratio grading
    'rank_sweet_spot':   3,   # Yukawa rank 140-159 sweet spot
    'vol_hierarchy':     5,   # volume hierarchy > 1000
    'tadpole_ok':        5,   # |χ/24| ≤ 20
    'mori_blowdown':     5,   # del Pezzo contraction fraction (graded)
    'd3_diversity':      5,   # distinct D³ values
    'clean_depth':       5,   # first clean bundle found early
    'clean_rate':        5,   # n_clean / n_bundles_checked
}
# Total: 100 pts.  Zero stranded points.
```

### Architecture

Same 4-tier structure as v4. T3 now includes triangulation stability.

| Tier | Time     | Purpose                              | Kill rate |
|------|----------|--------------------------------------|-----------|
| T0   | 0.1s     | Geometry + intersection algebra      | ~85%      |
| T1   | 0.5–120s | Bundle screening (capped, wall-timed)| ~55%      |
| T2   | 3–30s    | Deep physics + SM scoring + rescore  | top ~1K   |
| T3   | 30s+     | Tri stability + fibrations + phenome | top ~50   |

### Key Files

- `pipeline_v5.py` — orchestrator (adds `--limit`, post-upsert rescore,
  `first_clean_at` tracking)
- `cy_compute_v5.py` — imports v4 core + new `compute_sm_score()` with
  v5 weights, graded mori_blowdown, rank_sweet_spot, tri_stability
- `db_utils_v5.py` — v4 schema + 3 tri columns (auto-migrated)
- `CHANGELOG.md` — detailed v5.0/v5.1/v5.2 history

### Data Collected

- `v4/cy_landscape_v4.db`: 70,000 polytopes (h11=20–40), 1,787 T2-scored
- 50,000-polytope deep scan at h28 (full coverage of KS population)
- Top 20 candidates analyzed with T3 triangulation stability
- Scanned on Hetzner (16-core, 12 workers)

### Key Results

| Champions | Score | c₂ stab | Tier |
|-----------|-------|---------|------|
| h28/P874  | 87    | 50%     | A    |
| h28/P186  | 87    | 30%     | A    |
| h30/P289  | 86    | 0%      | C    |
| h28/P187  | 84    | 55%     | A    |

---

## v6 — KS Landscape Deep Scan + Monad Obstruction

**Folder**: `v6/`  
**Era**: h13–h40 full KS scan + priority cluster monad analysis (Feb–Mar 2026)  
**Question**: *"Does any χ=−6 polytope admit a heterotic SM via perturbative monads?"*

### What changed from v5

1. **Local KS index** (`--local-ks`): caches the full KS polytope set locally — eliminates web fetch bottleneck, enables reproducible offline scans
2. **T4 tier**: 37 polytopes (score≥80) fully verified via direct triangulation + deep physics; 5 priority entries confirmed
3. **Monad LP scanner** (`monad_scan_top37.py`): random-charge LP feasibility check for slope stability + D3 tadpole — `--rank`, `--k-max`, `--n-sample`, `--only-priority`, `--force` flags
4. **Champion deep physics**: h26/P11670 (sm=89) — Kodaira ✅, figures ✅, direct-sum ✅ (0 Hoppe-stable), monad LP ✅
5. **Paper** (`paper/paper.tex`): 31pp draft, JHEP target

### Scan Coverage

- **3.11M polytopes** scanned (h13–h40) — full KS landscape in range
- **938 T3-verified** (score≥70), **37 T4-verified** (score≥80)
- **Champion**: h26/P11670, sm=89
- **Landscape boundary**: h11≤28 productive; h29–h40 barren

### Monad Results (Findings §30–33)

| Scan | Rank | k_max | Entries | Slope-feasible | Tadpole-OK |
|------|------|-------|---------|----------------|-----------|
| B-45 | SU(4) | 3 | h26/P11670 | 612 | 0 |
| B-46 | SU(4) | 3 | 4 priority | 725 | 0 |
| B-47a | SU(4) | 1 | 4 priority | 80,293 | 0 |
| B-48 | SU(5) | 1 | 4 priority | 22,515 | 0 |
| **Total** | | | 5 | **104,145** | **0** |

**Finding**: Universal D3 tadpole obstruction for all perturbative SU(n≥4)
monads at integer charges on all five priority entries. The obstruction is
physical (not a sampling artefact) and strengthens monotonically with rank.

### Key Files

- `v6/monad_scan_top37.py` — monad LP scanner
- `v6/cy_compute_v6.py` — core physics (inherits v5)
- `v6/db_utils_v6.py` — DB schema (18 monad columns added)
- `v6/cy_landscape_v6.db` — 827MB, full landscape
- `paper/paper.tex` — 31pp draft (Theorem 1 + Corollary 1)

---

## v7 — Beyond the Standard Model Archetype

**Folder**: `v7/`  
**Era**: Mar 2026–  
**Question**: *"What does this geometry predict — and are we discarding better candidates because they don't fit the SM template?"*

### Motivation

v6 proved a universal tadpole obstruction for perturbative monads. Two paths forward:

1. **Track A — Non-perturbative completion**: H-flux tadpole cancellation, extension bundles, spectral covers. Relax perturbativity, allow flux quanta to cancel the D3 excess.
2. **Track B — Observable-first discovery**: Stop asking "does it look like the SM" and start asking "what does it predict?" Score candidates on dark matter mass, proton decay rate, and neutrino mass hierarchy.

### Key Shifts

| Dimension | v6 | v7 |
|-----------|----|----||
| Tadpole | Bundle alone | Bundle + H-flux: $n_{D3}^{\rm bundle} + n_{D3}^{\rm flux} \leq \chi/24$ |
| Gauge group | SU(4)/SU(5) required | Any stable bundle; gauge group is an output |
| Bundle class | Perturbative monads | Extension bundles, spectral covers |
| Scoring | Group-theoretic SM-match | Physical observables (DM mass, Γ_p, Δm²_ν) |

See `v7/README.md` for full architecture and scoring spec.

---

## Version Inheritance

```
archive/v2/cy_compute.py     ← core math (lattice points, Koszul, χ, fibrations)
  ↑ imports
archive/v3/cy_compute_v3.py  ← adds: Yukawa texture, LVS, Mori, divisor classify
  ↑ imports
v4/cy_compute_v4.py          ← adds: compute_sm_score() (v4.0 → v4.1 weights)
  ↑ imports
v5/cy_compute_v5.py          ← adds: graded mori, rank_sweet_spot, tri_stability,
                                 yukawa_rank fallback fix, post-upsert rescore

archive/v2/db_utils.py       ← original schema
archive/v3/db_utils_v3.py    ← expanded schema (Yukawa, LVS, Mori columns)
v4/db_utils_v4.py            ← same schema as v3
v5/db_utils_v5.py            ← v4 schema + tri columns (auto-migrated)

archive/v2/pipeline_v2.py    ← T0 → T0.25 → T1 → T2
archive/v3/pipeline_v3.py    ← T0 → T1 → T2 → T3 (merged T0.25 into T1)
v4/pipeline_v4.py            ← T0 → T1 → T2 → T3 (gap-priority, wall-time, bundle cap)
v5/pipeline_v5.py            ← T0 → T1 → T2 → T3 (--limit, rescore, first_clean_at)
```

---

## Compute Environments

| Environment | Specs           | Used for                                  |
|-------------|-----------------|-------------------------------------------|
| Hetzner     | 16-core, 128GB  | v2 h18, v4 h22-40, v5 h20-40 + 50K h28   |
| Codespace   | 4-core, 32GB    | v3 h13-24 scans, h17 full landscape       |
| Local       | Dev, analysis   | DB queries, scoring R&D, documentation    |
