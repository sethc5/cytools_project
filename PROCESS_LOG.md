# PROCESS LOG — CYTools Project

> Chronological record of investigations, decisions, and issues encountered.
> New entries go at the top. Reference BACKLOG.md items by ID.

---

## 2026-02-27 — h30 50K Scan + T3 Deep Analysis

**Work done**: Expanded h30 from 1K → 50K polytopes on Hetzner (v5.2,
14 workers). Total DB now at 119,000 polytopes, 1,805 T2-scored. Ran T3
deep analysis (`--deep --top 5`) on the five highest-scoring candidates.

**Key results**:
- **h30/P289 rescored 86 → 89** — new global champion. The 50K scan provided
  deeper bundle census data that elevated the score.
- T3 revealed P289 has **3 K3 fibrations, 1 elliptic fibration, SM+GUT gauge
  groups** (su(3) × su(17) × U(1)^10). Only top-5 candidate with this property.
- P289 Yukawa hierarchy = 34,318 — 30× higher than the h28 cluster.
- **Triangulation instability**: P289 has c₂ stab = 0%, κ stab = 0%.
  Geometry changes across all 20 sampled FRSTs. This is a known caveat.
- h30/P1398 (score 82) emerged as a strong alternative: 3 K3 + 3 elliptic
  fibrations, SM+GUT, 100% κ-stability.
- h28 cluster (P874/P186/P187) has best c₂ stability (40–60%) but no SM/GUT
  fibrations.

**Updated docs**: FINDINGS.md, CATALOGUE.md, PROCESS_LOG.md, README.md.

**Database snapshot**: 119K polytopes across h20–h40. h28 and h30 at 50K each,
all others at 1K.

---

## 2026-02-26 — FINDINGS.md Restructure

**Work done**: Full clarity review of FINDINGS.md (2,176 lines). Identified
structural problems: three overlapping leaderboard tables (§0, §0.1, §0.3)
at different pipeline versions, "§0.x" numbering, stale score references,
wrong "Theoretical Ceiling: Score=84" claim (champions hit 87), no executive
summary.

**Approach**: Preserved original as `archive/FINDINGS_v1.md`. Built fresh
version with:
- Executive summary at top with current leaderboard and tier assignments
- Single authoritative landscape trends section (consolidated from three)
- Sequential §1–§15 numbering
- All score references updated to post-rescore values
- Earlier pipeline results (h13–h19) grouped under one heading with
  scoring-system context note

**Net effect**: 2,176 → ~450 lines. ~75% reduction, zero information loss.

---

## 2026-02-26 — v5.2 MONOTONIC_MAX Score Drift Fix (commit `b1c9555`)

**Work done**: Diagnosed and fixed score regression bug discovered after 50K
h28 scan. Champions P874/P186 had dropped from 87 → 84.

**Root cause**: T2 worker computes `sm_score` from its local result dict
(where e.g. n_clean=6 from a fresh triangulation). The DB preserves
`MAX(old, new)` for MONOTONIC_MAX columns (n_clean, yukawa_rank, etc.),
so the DB correctly keeps n_clean=14. But `sm_score` is NOT in
MONOTONIC_MAX — computed from the worker's stale n_clean=6, it overwrites
the stored 87 with 84.

**Manual trace** (P874):
- Worker data: n_clean=6 → clean_bundles=7, total=84
- DB merged data: n_clean=14 → clean_bundles=9, total=87
- Score was being computed BEFORE upsert, from local data

**Fix (three parts)**:
1. Post-upsert rescore in `_run_t2_parallel()` — reads merged DB row after
   upsert and recomputes `compute_sm_score()` from the merged values
2. T2 worker now tracks `first_clean_at` (index of first clean bundle found)
3. Added `first_clean_at` to T2 upsert function

**Verification**: Deployed to Hetzner, ran `--rescore` which updated 358 of
1,787 scores. P874/P186 restored to 87. P187 correctly at 84. Full
leaderboard verified.

**Files modified**: v5/pipeline_v5.py, v5/CHANGELOG.md

---

## 2026-02-26 — Deep Coverage Scan: h28 at 50K (v5.1)

**Work done**: Ran `--scan --h11 28 --limit 50000 -w 12` on Hetzner.
13.5 min runtime. Tests whether the first-1K (2% of h28 population)
contains the true champions.

**Results**:
- 50,000 fetched → 484 T0 pass (1.0%) → 164 T2 scored
- 95 from first 1K, 69 from new 49K
- Best new: h28/P1040 (score=80, n_clean=50, hier=3,859)
- Champions P874/P186 (score=87) not displaced
- P1105 has 100 clean bundles (record) but only scores 70

**Conclusion**: First-1K bias is mild. Champion selection robust.

---

## 2026-02-26 — v5.1: KS `limit` Bug Discovery (commit `0e1287b`)

**Work done**: Discovered CYTools `fetch_polytopes()` has a hidden
`limit=1000` default. All prior scans retrieved only the first 1,000 of
~50,000+ polytopes per h¹¹ from the KS web server.

**Fix**: Added `--limit N` CLI argument to pipeline_v5.py. Threads through
`run_scan`, `run_ladder`, `run_deep`.

---

## 2026-02-26 — T3 Deep Analysis: Top 20 Candidates

**Work done**: Ran `--deep --top 20` on Hetzner. For each candidate, generate
up to 50 random FRST triangulations. Compute c₂ hash and κ hash. Report
stability fraction.

**Key findings**:
1. No SM or GUT fibrations in any of the 20 candidates
2. Stability is bimodal: robust (≥50%) vs fragile (0%)
3. Score and stability weakly correlated — different quality axes
4. High hierarchy (e.g. h21/P496 at 49K×) can be triangulation-dependent

**Tier assignments**:
- **A (paper-ready)**: h28/P874 (87, 50%), h28/P187 (84, 55%), h28/P186 (87, 30%)
- **B (strong)**: h32/P94 (80, 100%), h32/P42 (79, 100%), h27/P219 (79, 55%)
- **C (score-driven)**: h30/P289 (86, 0%), h25/P934 (81, 25%), h20/P903 (81, 0%)

**Commit**: `3e46bc4`

---

## 2026-02-26 — v5 Scoring Overhaul + h20-40 Scan (21K polytopes)

**Work done**: Created v5 pipeline with revised 100-point scoring based on
v4.1 landscape analysis. Deployed to Hetzner, scanned h20-40 at 1K/bucket.

**Scoring changes from v4.1**:
- `fibration_sm` (3 pts) → **removed**. Only 3 of 19K polytopes had SM gauge
  group fibrations — 3 pts permanently stranded for 99.98% of candidates.
- `rank_sweet_spot` (3 pts) → **new**. Yukawa rank 140–159 is the SM sweet
  spot for h11_eff=18–22.
- `mori_blowdown` → **graded**. Was binary 5/0. Now fraction-based:
  ≥0.9→5, ≥0.7→4, ≥0.5→3, ≥0.3→2, >0→1.
- `yukawa_rank` fallback → **bug fix**. `texture_rank=0` (falsy) was falling
  through to κ triple count via `or` operator, inflating 194 polytopes by
  +10 to +18 points.

**Scan results**: 21K polytopes, 1,718 T2-scored. New champions at h28
(score=87) displacing old h30/P289 (82→86 under v5). Fertile window:
h20–35, barren at h37+.

**Files**: v5/pipeline_v5.py, v5/cy_compute_v5.py, v5/db_utils_v5.py,
v5/CHANGELOG.md

---

## 2026-02-26 — v4.1 Tuning: EFF_MAX=22, Scoring Redistribution, h26-40 Launch

**Work done**: Applied evidence-based tuning from h22-30 analysis. Killed
running h31-40 scan, updated thresholds and scoring, redeployed, relaunched
h26-40 with 14 workers.

### Changes Applied

1. **EFF_MAX 20 → 22**: 46% of score-75+ polytopes were at the eff=20
   ceiling. At h30, 535 polytopes were blocked solely by eff>20 (gap OK).
   Immediate impact: h26 T0 pass rate **doubled** from 142 → 282.

2. **dp_divisors removed (5 → 0 pts)**: n_dp anti-correlates with score
   (r=−0.19). Elite polytopes average n_dp=5.0 vs population 6.5. The
   weight was actively rewarding the wrong thing.

3. **fibration_sm reduced (5 → 3 pts)**: n_k3_fib anti-correlates with
   score (r=−0.22). Keep SM/GUT gauge group signal but reduce weight.
   Fibration count doesn't predict SM quality.

4. **vol_hierarchy added (5 pts, new)**: Volume hierarchy > 1000 averages
   6.5 pts higher than < 100 (n=203 vs n=71). Previously unscored.
   Graded: ≥1000→5, ≥100→3, ≥10→1.

5. **yukawa_hierarchy boosted (25 → 27 pts)**: Absorbed 2 freed points.
   Still the dominant discriminator (r=+0.31, elite polytopes have 11.6×
   population average).

### Validation

- Weights sum to 100 ✓
- Champion h30/P289 rescores: 82 → 92
- h26 T0 pass rate: 142 → 282 (2× from EFF_MAX change)
- Zero T1 timeouts in first h26 batch
- Full changelog: v4/CHANGELOG.md

### Scan Results (completed 2026-02-26, ~16 min total)

`--scan --h11 26 40 --workers 14` on Hetzner (16-core).
Re-scanned h26-30 with EFF_MAX=22 (added eff=21-22 polytopes + rescored),
then extended through h31-40. Zero T1 timeouts across all 15 h-values.

| h11 | T0 pass | T1 pass (%) | Top | Time | vs v4.0 |
|-----|---------|-------------|-----|------|----------|
| 26  | 282     | 113 (40.1%) | 76  | 5.1m | T0 2× (was 142) |
| 27  | 192     | 63 (32.8%)  | 79  | 3.3m | T0 +80% (was 106) |
| 28  | 182     | 95 (52.2%)  | **84** | 2.9m | **New champion** (was 75) |
| 29  | 91      | 39 (42.9%)  | 73  | 1.5m | +5 vs v4.0 |
| 30  | 128     | 56 (43.8%)  | **84** | 1.7m | Tied champion (was 82) |
| 31  | 52      | 27 (51.9%)  | 70  | 49s  | |
| 32  | 54      | 41 (75.9%)  | 77  | 48s  | Surprise: high T1 pass |
| 33  | 31      | 7 (22.6%)   | 65  | 14s  | |
| 34  | 17      | 15 (88.2%)  | 70  | 14s  | Very high T1 pass |
| 35  | 11      | 3 (27.3%)   | 62  | 11s  | |
| 36  | 6       | 2 (33.3%)   | 30  | 11s  | Sparse |
| 37  | 3       | 0 (0%)      | —   | —    | Empty |
| 38  | 0       | —           | —   | —    | Zero T0 pass |
| 39  | 1       | 1 (100%)    | 49  | 10s  | Single survivor |
| 40  | 0       | —           | —   | —    | Zero T0 pass |

**Key observations:**
- New top score **84** at both h28 and h30 (EFF_MAX=22 unlocked these)
- EFF_MAX=22 impact massive: h26 T0 doubled (142→282), h27 +80% (106→192),
  h28 nearly doubled (92→182)
- **h37+ is effectively barren** — CY landscape exhausted at EFF_MAX=22
- h32 surprise: 76% T1 pass rate and top=77, outperforming h31 and h33
- h34 has 88% T1 pass (15/17) — tiny but high-quality sample

---

## 2026-02-26 — v4 Full h22-30 Scan Analysis (9,000 polytopes, 1,134 T2-scored)

**Work done**: Completed v4 scan across h11=22–30 (9,000 polytopes, 1,134
T2-scored). Pulled DB (3.1MB) and performed comprehensive trend analysis
across score components, correlations, hidden predictors, and ceiling effects.

### Summary Statistics

| h11 | T0 pass | T1 pass (%) | Top score | Avg score | Total time |
|-----|---------|-------------|-----------|-----------|------------|
| 22  | 632     | 281 (44.5%) | 75        | 60.4      | 17.3m      |
| 23  | 453     | 235 (51.9%) | 79        | 59.1      | 13.1m      |
| 24  | 380     | 184 (48.4%) | 79        | 58.6      | 8.8m       |
| 25  | 242     | 138 (57.0%) | 79        | 56.6      | 3.9m       |
| 26  | 142     | 89 (62.7%)  | 76        | 52.7      | 3.1m       |
| 27  | 106     | 54 (50.9%)  | 76        | 51.8      | 2.3m       |
| 28  | 92      | 70 (76.1%)  | 75        | 56.2      | 1.3m       |
| 29  | 49      | 35 (71.4%)  | 68        | 50.7      | 56s        |
| 30  | 91      | 48 (52.7%)  | 82        | 51.6      | 1.1m       |

Zero T1 timeouts across all h-values — T1 efficiency fix validated at scale.

### Key Findings

**1. Yukawa hierarchy and LVS quality are orthogonal (r = −0.027)**

The two heaviest-weighted score components are *statistically independent*.
This means high scores require excelling on both—not just one:

- yuk>500 + lvs<0.005: avg 71.4, top 82 (n=29)
- yuk>500 + lvs≥0.005: avg 68.4, top 79 (n=111)
- yuk≤500 + lvs<0.005: avg 64.9, top 75 (n=188)
- yuk≤500 + lvs≥0.005: avg 60.1, top 71 (n=658)

This validates v4's decision to weight both heavily and independently.

**2. EFF_MAX=20 ceiling — detectable but not critical**

- 46% of score-75+ polytopes sit at eff=20 (the ceiling)
- At h30, 535 polytopes blocked by eff>20 alone (gap OK)
- Raising EFF_MAX to 22 would unlock ~200 additional polytopes/h-value at h26+
- Recommendation: test EFF_MAX=22 in v5, but T1 wall-time may need adjustment

**3. Elite polytope profile (score ≥ 75, n=24)**

Compared to population averages:
- h11_eff: 19.3 (pop: 18.1) — higher effective rank
- yukawa_hierarchy: 3,594 (pop: 311) — **11.6× population average**
- lvs_score: 0.011 (pop: 0.017) — 1.6× better
- n_clean: 31.3 (pop: 25.3) — slightly more clean bundles
- n_dp: 5.0 (pop: 6.5) — **fewer del Pezzo** (anti-intuitive)
- n_k3_fib: 2.5 (pop: 2.9) — fewer fibrations
- volume_hierarchy: 1,962 (pop: 920) — **2.1× population average**

**4. Volume hierarchy > 1000 is a strong (unstudied) predictor**

avg score 59.9 (n=203) vs 53.4 for vol_hierarchy < 100 (n=71).
Not currently in the scoring formula. Candidate for v5 addition.

**5. yukawa_rank 140-159 is the sweet spot**

Not "more = better". The 140-159 bucket has both the highest avg
yukawa_hierarchy (444) and the best max (34K). Above 160, hierarchy
drops to 223. The intersection ring has an optimal complexity.

**6. n_dp anti-correlates with score (confirmed at 9K scale)**

n_dp=0-1: avg 63-64. n_dp=8+: avg 55. Fewer del Pezzo divisors
correlate with higher SM scores. This is anti-intuitive re: instanton
contributions but consistent with simpler divisor structure favoring
clean bundle topology.

**7. Non-discriminating properties at h22+**

These columns carry zero information above h22 and can be dropped:
- `volume_form_type`: 100% swiss_cheese
- `has_swiss`: 99.6% = 1
- `c2_all_positive`: 100% = 0
- `yukawa_zeros`: 100% have ≥ 5 (or null for unscored)

**8. Score achievability collapses at h29**

Only 2.9% of h29 polytopes have both clean≥10 and yuk_h≥100
(vs 31.7% at h22). The landscape becomes genuinely sparse.

### Pearson Correlations with SM Score (n_clean > 0 subset)

| Variable          | r     | Direction |
|-------------------|-------|-----------|
| n_clean           | +0.39 | moderate  |
| h11_eff           | +0.35 | moderate  |
| lvs_score         | −0.34 | moderate (lower = better) |
| yukawa_hierarchy  | +0.31 | moderate  |
| yukawa_rank       | +0.26 | weak-mod  |
| n_k3_fib          | −0.22 | weak (fewer = better!) |
| n_dp              | −0.19 | weak (fewer = better!) |
| gap               | −0.19 | weak      |
| n_ell_fib         | −0.13 | weak      |
| chi_over_24       | 0.00  | none      |

---

## 2026-02-26 — v4 Pipeline: Evidence-Based Scoring + T1 Efficiency Fix

**Work done**: Created v4 pipeline with scoring weight redistribution based on
analysis of 6,578 v3 polytopes (h11=13–21). Deployed to Hetzner 16-core.
Diagnosed and fixed critical T1 efficiency bug. Launched h22–30 scan.

### v4 Scoring Rationale

Comprehensive trend analysis of the v3 database revealed scoring waste:

**Removed — zero discrimination:**
- `chi_match` (was 10 pts): χ = −6 for every candidate by construction.
  100% of T0-passing polytopes have |χ| = 6. Allocating 10/100 points to a
  universal property is pure noise.
- `h0_diversity` (was 5 pts): anti-correlates with SM quality. Polytopes
  with h⁰ diversity 5–9 average score 76.6; diversity ≥20 averages 70.6.
  High diversity means many marginal bundles, not physics quality.

**Promoted — dominant discriminator:**
- `yukawa_hierarchy` (10 → 25 pts): THE key signal. Every score-90 polytope
  has hierarchy > 1000×. Score-86 polytopes average ~200×. A 6-tier grading
  (10, 100, 500, 1000, 10000) replaces the binary ≥10³ check.

**Split — graded instead of binary:**
- `lvs_compatible` (15 → split): was all-or-nothing. Now:
  - `lvs_binary` (5 pts): has swiss cheese structure at all
  - `lvs_quality` (10 pts): 5-tier τ/V^{2/3} ratio grading
    (elite < 0.002, excellent < 0.005, good < 0.01, fair < 0.05)

**Reduced — diminishing returns:**
- `clean_bundles` (15 → 10 pts): log₂-scaled, saturates above ~50 clean.
  Going from 50 → 200 clean adds zero physics information.

**Added — structural quality:**
- `clean_rate` (5 pts): n_clean/n_checked rewards structural SM-friendliness.
- `clean_depth` (5 pts): depth of first clean hit in bundle search.
- `d3_diversity` (5 pts): distinct D³ values among clean bundles.

**Net effect**: 0 points on universal properties (was 15), 25 points on the
proven key discriminator (was 10). Total still 100.

### v2 Hetzner Data Analysis

Pulled 93K T0 rows, 20.6K T1 rows, and 87 T2 rows from the old v2 batch
(h18, 14-worker, 22% complete after 3 days). Loaded into `v2/v2_hetzner.db`.

Key findings that validate v4 design:
- `has_swiss` does NOT predict clean bundles: avg 17.8 with vs 17.7 without
- `n_dp` anti-correlates: fewer del Pezzo → more clean bundles
- `screen_score` (v2's 26-pt) has zero predictive power for clean count
- This confirms removing binary swiss/dP/chi gates from scoring

### T1 Efficiency Bug (diagnosed + fixed)

**Symptom**: v4 deployed to Hetzner, h22 scan launched with 14 workers. T0
completed in 6.7s (632/1000 pass, 148 poly/s). T1 hung indefinitely — 12+
minutes with zero output, all 14 workers at 99% CPU.

**Root cause**: `find_chi3_bundles()` (uncapped) at h11_eff=17–20 returns
thousands of bundles. Each `compute_h0_koszul()` call takes 0.5–2s at this
h11_eff scale. The `T1_BUDGET_SEC = 2.0` timer only starts after the first
clean hit — polytopes with no clean bundles iterate all ~2000 bundles with
no escape, taking 15+ minutes each per worker.

**Three-part fix**:
1. `T1_BUNDLE_CAP = 500` — use `find_chi3_bundles_capped()` at T1 (screen,
   not census; T2 does exhaustive analysis)
2. `T1_WALL_SEC = 120` — hard per-polytope wall-time limit, checked every
   10 bundles. Returns `status='timeout'` with partial data.
3. Progress reporting — prints status every 20 polytopes with pass/timeout
   counts, elapsed, ETA.

**Result**: T1 h22 went from ∞ (hung) → **180s** (3 min). 281/632 pass
(44.5%), zero timeouts. Gap-priority scheduling confirmed: first 300
polytopes (high gap) processed in ~20s; remaining 332 (low gap) took 160s.

### h22 Scan Results (in progress)

```
T0: 632/1000 pass (63.2%), 6.7s
T1: 281/632 pass (44.5%), 0 timeout, 180s
T2: ~200/281 done, 189 with clean (running at 0.3-0.4 poly/s, ETA ~3 min)
```

Scan continuing through h23–30 on Hetzner (14 workers).

### Gap-Priority Scheduling (v4 pipeline change)

Polytopes sorted by `gap = h11 - h11_eff` descending before T1 dispatch.
Combined with `imap_unordered(chunksize=1)`, this ensures:
- High-gap polytopes (fast, high pass rate) process first
- Time-to-first-result drops from minutes to seconds
- Workers stay busy — fast polytopes fill gaps while slow ones grind

Data from v3 DB: gap=2 avg 35s, 30% pass. gap=5 avg 4s, 52% pass.
gap=7 avg 2s, 79% pass.

### has_swiss Anomaly Investigated

56 polytopes in v3 DB have has_swiss=0 but volume_form_type='swiss_cheese'.
Investigation showed these are NOT bugs — they genuinely fail the swiss cheese
test (check_swiss_cheese returns False) but the volume Hessian has swiss cheese
eigenvalue signature. Average lvs_score 3× worse than true swiss cheese.
v4 scoring correctly uses the binary check (lvs_binary) and ratio quality
(lvs_quality) independently.

### Files Created/Modified
- `v4/pipeline_v4.py` — orchestrator with gap-priority, wall-time, bundle cap
- `v4/cy_compute_v4.py` — new `compute_sm_score()` with v4 weights
- `v4/db_utils_v4.py` — DB layer (same schema as v3)
- `VERSIONS.md` — full v2/v3/v4 lineage documentation

---

## 2026-02-25 — v3 Pipeline Infrastructure & Workspace Reorganization

**Work done**: Built the complete v3 pipeline infrastructure and reorganized the
workspace for clarity.

### Workspace Reorganization
- Moved all v2 code to `v2/`: pipeline_v2.py, cy_compute.py, db_utils.py,
  merge_receipts.py, fiber_analysis.py, mori_pf.py, picard_fuchs.py,
  cy_landscape.db, checkpoints, receipts/
- Moved old results to `archive/results_v1v2/`
- Root now contains only docs, LICENSE, activate.sh, requirements.txt
- Cleaned `__pycache__`

### v3 Pipeline (new `v3/` folder)
5-tier physics-driven architecture replacing v2's 4 tiers:

| Tier | Time   | Purpose                    | Kill rate |
|------|--------|----------------------------|-----------|
| T0   | 0.05s  | Geometry fingerprint       | ~85%      |
| T05  | 0.1s   | Intersection algebra (NEW) | ~50%      |
| T1   | 0.5s   | Bundle screening           | ~70%      |
| T2   | 3-30s  | Deep physics + scoring     | top ~1K   |
| T3   | 30s+   | Full phenomenology (NEW)   | top ~50   |

Key improvements over v2:
- **100-point continuous SM_SCORE** replacing 26-point binary score
- **Yukawa texture analysis**: rank, hierarchy, zeros of κ_{ijk}D^k
- **Volume form classification** via Hessian eigenvalues (swiss_cheese/fibered/generic)
- **LVS compatibility score**: τ/V^{2/3} at multiple Kähler scales
- **c₂ positivity check** (DRS conjecture gate)
- **Mori cone analysis**: del Pezzo contraction identification
- **Triangulation stability** (T3): property persistence across random triangulations
- **Instanton divisor check** (T3): rigid dP surfaces for E3 instantons
- Chi computed from actual h²¹ (v2 hardcoded χ=−6)

### Files created
- `v3/PIPELINE_V3_SPEC.md` — complete spec document
- `v3/db_utils_v3.py` — fresh SQLite database layer with new schema
- `v3/cy_compute_v3.py` — physics computation (imports v2 functions, adds T05/T2/T3)
- `v3/pipeline_v3.py` — main orchestrator with --ladder/--scan/--deep/--rescore modes

### Execution modes
- `--ladder --h11 13 30` — T0+T05 fast landscape mapping
- `--scan --h11 19` — Full T0→T2 for one h¹¹
- `--deep --top 50` — T3 on best candidates
- `--rescore` — Recompute SM scores from existing data

---

## 2026-02-28 — h17 Full Scan (pipeline_v2), Receipt System, Circularity Audit

**Work done**: Built `pipeline_v2.py` (gap-aware 4-tier pipeline with optional DB),
`merge_receipts.py` (receipt-based remote data transport), and ran h17 full scan on
GitHub Codespace (4-core, 15GB). Then audited whether findings hold honestly.

### Pipeline v2 + Receipt System
- `pipeline_v2.py`: T0→T0.25→T1→T2, optional DB via `HAS_DB` flag. Always writes
  self-contained JSON receipts to `receipts/` for remote runs.
- `merge_receipts.py`: CLI tool ingests receipt JSONs into local `cy_landscape.db`.
  Supports `--dry-run`, `--list`, `--force`. Tracks merged status in `receipts/.merged`.
- Workflow: run on Codespace → download receipt via SSH → merge locally → commit.

### h17 Full Scan Results
- **38,735 polytopes** scanned in **25.1 minutes** on 4-core Codespace
- T0: 38,735 → 1,803 pass (4.7%), 83 poly/s
- T0.25: 1,803 → 519 pass
- T1: **519/519 had clean bundles** (100% hit rate)
- T2: 509 with SM gauge groups, 2,770 fibrations
- Receipt: 12.8 MB JSON, merged into DB. Committed as `4d8e3fc`.

### Circularity Audit (IMPORTANT)
Realized h17 data **cannot independently validate** Finding 14's gap prediction
because pipeline_v2 filters on gap≥2 before T1. The 100% hit rate is circular.

**Honest unbiased evidence** (only pre-pipeline_v2 data, N=496, excl h17):
- gap<2: **97.2% hit rate** (317/326), avg clean when hit: 13.7
- gap≥2: **100.0% hit rate** (170/170), avg clean when hit: 23.8
- Difference: 2.8 percentage points

**Verdict**: Gap is a **weak quality filter** (97.2% vs 100%) but a **meaningful
yield predictor** (13.7 vs 23.8 avg clean — 1.7× multiplier). It's an efficiency
knob, not a quality gate. For h17 specifically, gap<2 polytopes were all killed
by eff/aut constraints at T0 anyway — the gap filter was redundant.

### Loser Analysis (9 polytopes with n_clean=0 at T1+)
Profile of the 9 failures (all from unbiased pre-pipeline_v2 data):
- **7/9 gap=0, 2/9 gap=1** (0/9 gap≥2)
- **7/9 favorable** (vs 22% of winners — 3.5× overrepresentation)
- **7/9 max_h⁰=4** (borderline lowest qualifying h⁰)
- **8/9 lack deep analysis data** (NULL bundles_checked, d3, rigid)
- Losers: avg h⁰=4.7 vs winners avg 8.3
- Losers: 78% favorable vs winners 22%
- Losers: avg gap=0.2 vs winners 1.8
- Loser rate by h¹¹: h14 14.3%, h15 3.5%, h16 0.5%, h18–h19 0%

**Pattern**: Losers are favorable, gap=0, barely-qualifying polytopes. They're
marginal by every metric — the pipeline's early gates just aren't tight enough
to catch them. At higher h¹¹ the loser rate drops toward zero.

### Updated Leaderboard
Top 5 by n_clean:
1. h18/P34: 189 clean, gap=5, eff=13
2. h19/P7: 114 clean, gap=6, eff=13
3. h16/P52: 94 clean, gap=4, eff=12
4. h13/P0: 86 clean, gap=0, eff=13 (the only favorable in top 10)
5. h16/P40: 69 clean, gap=3, eff=13

Best h17 entry: P767 at #9 (59 clean, 26/26, SM, 10 fibrations).
Database: 74,823 polytopes, 1,284 deep-analyzed, 4,387 fibrations.

**Committed**: pipeline_v2.py, merge_receipts.py, receipts/, .gitignore update.

---

## 2026-02-27 — Database Landscape Analysis: 30 Queries, Pipeline Redesign

**Work done**: Built SQLite database layer (`db_utils.py`, `consolidate_db.py`),
ingested 15 result files into `cy_landscape.db` (74,819 polytopes, 35 fibrations,
13.7 MB). Ran 30 exploratory queries across the full dataset.

**Major discovery**: The variable `gap = h¹¹ − h¹¹_eff` is a near-perfect predictor
of clean bundle count. Every polytope with gap ≥ 2 that reaches T2 has at least
one clean bundle (100% hit rate). Average clean count rises from 12.4 (gap=0) to
47.7 (gap=6). The all-time champion (h18/P34, 189 clean) has gap=5.

**Pipeline redesign**: Based on all 30 queries, designed a new T0 pre-filter that
computes h¹¹_eff in ~0.1s per polytope. Rejects eff ≥ 16, gap < 2 with h⁰ < 5,
and |Aut| ≥ 4. Expected to cut ~90% of compute at h19/h20. Also raised h⁰ gate
from ≥3 to ≥5, removed Swiss cheese from triage gates.

**Other findings**: Non-favorable systematically better than favorable (189 vs 86
best clean). Swiss cheese is noise (89% vs 86%). Del Pezzo non-monotonic. Symmetry
kills (|Aut|=8 → 0 clean). n_chi3 ≥ 10K → avg 92.4 clean (phase transition).
At fixed eff=13, clean increases with h¹¹ — the landscape gets better as we scale.

**Committed**: `468b4ae` (db_utils.py, consolidate_db.py, .gitignore).
See Finding 14 in FINDINGS.md for full details and all 30 query results.

---

## 2026-02-26 — B-21: Automorphism group scan (592 candidates + full h15/h16/h17)

**Work done**: Created `scan_automorphisms.py` to compute `p.automorphisms()` for all 592 top-200 candidates and all polytopes with nontrivial symmetry at each h-value. Cross-referenced with scan CSVs for max_h0 and h0_3_count.

**GL=12 falsification**: h17/P37 (GL=12, |Aut|=12, D₆ symmetry) has max_h⁰=1 across all 1,720 χ=−6 bundles. Zero h⁰=3 bundles. D₆ Yukawa texture program via line bundles is dead.

**Key findings**:
- 53/592 candidates (9%) have nontrivial |Aut|>1. Max is |Aut|=4.
- 532 polytopes across all h15-h17 have BOTH |Aut|>1 AND h⁰≥3
- Symmetry-vs-h⁰ tension confirmed: higher |Aut| → fewer h⁰=3 bundles
- |Aut|=8 exists (h16/P0, h17/P2997) but only 2-4 h⁰=3 bundles each
- Best combination: **h16/P329** — |Aut|=2, 26/26 score, 228 clean, 164 h⁰=3 bundles, 7 ell

**Committed**: `scan_automorphisms.py` as `14ee18b`. Results in `results/aut_scan.log`.

---

## 2026-02-25 — B-19/B-28: h15 auto_scan complete (553 → 200 → 192)

**Work done**: Ran `auto_scan.py --h11 15 --skip-t025 --top 200 -w 3` on Codespace.
Loaded existing scan_h15.csv (553 polytopes, 333 T0.25 passes).
Deep-analyzed 200, fiber-classified 192. Total time: **1.9 minutes**.

### Results summary

| Metric | Value |
|--------|-------|
| Polytopes (T0.25) | 553 |
| T0.25 passes | 333 (60%) |
| Deep-analyzed | 200 |
| Fiber-analyzed | 192 |
| Score 26/26 | **28** |
| Score 25/26 | 67 |
| SM gauge group | **191/192 (99%)** |
| SU(5) GUT | **120/192 (62%)** |
| Max clean | 45 (P147) |
| Max elliptic | 13 (P215) |
| Max τ | 14,436 (P41) |

### Top 10 candidates

| Rank | Poly | Score | Clean | Ell | K3 | τ | Gauge |
|------|------|-------|-------|-----|-----|---|-------|
| 1 | P147 | 26/26 | 45 | 1 | 2 | 15 | su(2)⁴×su(3)² |
| 2 | P256 | 26/26 | 38 | 1 | 3 | 2,025 | su(7)×su(5) |
| 3 | P183 | 26/26 | 37 | 1 | 2 | 1,154 | su(6)×su(5) |
| 4 | P94 | 26/26 | 36 | 4 | 4 | 241 | su(6)² |
| 5 | P249 | 26/26 | 36 | 1 | 2 | 735 | su(3)² |
| 6 | P101 | 26/26 | 35 | 1 | 2 | 130 | su(3)² |
| 7 | P500 | 26/26 | 34 | 1 | 2 | 124 | su(6)×su(5) |
| 8 | P214 | 26/26 | 34 | 1 | 3 | 252 | su(6)×su(5) |
| 9 | P387 | 26/26 | 33 | 3 | 3 | 11,400 | su(5)×su(4) |
| 10 | P67 | 26/26 | 31 | 4 | 4 | 128 | su(4)×su(5) |

### Notable findings

- **28 perfect-score polytopes** at h11=15 — 9 new discoveries beyond existing pipeline coverage
- **99% SM rate** (191/192), **62% GUT** (120/192)
- **P387**: τ = 11,400 — second highest LVS parameter after P61 (τ=14,300)
- **P147**: 45 clean bundles, richest at h15, but no SU(5) GUT
- **P256**: 38 clean + τ=2,025, strong GUT candidate with su(7)×su(5)
- Known cross-refs: P94 rank=4 (was 380 clean in old pipeline), P61 rank=29 (was 110 clean, τ=14,300)

---

## 2026-02-25 — B-19/B-28: h16 auto_scan complete (5,180 → 200 → 190)

**Work done**: Ran `auto_scan.py --h11 16 --skip-t025 --top 200 -w 3` on Codespace.
Loaded existing scan_h16.csv (5,180 polytopes, 1,811 T0.25 passes).
Deep-analyzed 200, fiber-classified 190. Total time: **1.7 minutes**.

### Results summary

| Metric | Value |
|--------|-------|
| Polytopes (T0.25) | 5,180 |
| T0.25 passes | 1,811 (35%) |
| Deep-analyzed | 200 |
| Fiber-analyzed | 190 |
| Score 26/26 | **58** |
| Score 25/26 | 39 |
| SM gauge group | **190/190 (100%)** |
| SU(5) GUT | **169/190 (89%)** |
| Max clean | 50 (P278) |
| Max elliptic | 15 (P1245) |
| Max τ | 6,468 (P425) |

### Top 10 candidates

| Rank | Poly | Score | Clean | Ell | K3 | τ | Gauge |
|------|------|-------|-------|-----|-----|---|-------|
| 1 | P212 | 26/26 | 42 | 3 | 3 | 50 | su(8)/e7×su(4) |
| 2 | P239 | 26/26 | 38 | 1 | 3 | 0 | su(7)×su(5) |
| 3 | P329 | 26/26 | 34 | 7 | 6 | 109 | su(5)×su(4)×su(3) |
| 4 | P313 | 26/26 | 33 | 3 | 3 | 689 | su(4)²×su(3)² |
| 5 | P169 | 26/26 | 31 | 4 | 4 | 110 | su(4)²×su(3)² |
| 6 | P83 | 26/26 | 31 | 1 | 3 | 1,640 | su(8)/e7×su(5) |
| 7 | P1998 | 26/26 | 30 | 7 | 6 | 2 | su(6)² |
| 8 | P376 | 26/26 | 30 | 4 | 4 | 162 | su(5)²×su(3) |
| 9 | P125 | 26/26 | 29 | 4 | 4 | 564 | su(8)/e7×su(4) |
| 10 | P800 | 26/26 | 28 | 6 | 5 | 359 | su(8)/e7×su(5) |

### Notable findings

- **58 perfect-score polytopes** at h16 — dramatic jump from h15's 28
- **100% SM rate** (190/190), **89% GUT** (169/190) — GUT rate up from 62% at h15
- **P278**: 50 clean bundles but only 23/26 (no Swiss cheese → score penalty)
- **P1245**: 15 elliptic fibrations — highest ell count observed so far
- **P425**: τ=6,468 — 3rd highest LVS parameter (behind P41/h15 and P61/h15)
- **P212**: Overall best — 42 clean, score 26/26, su(8)/e7 gauge, SM+GUT
- Known: P86 rank=16 (score 26, 24 clean, τ=1536), P11 rank=39, P53 rank=113

---

## 2026-02-25 — B-19/B-28: h17 auto_scan complete (38,735 → 200 → 193)

**Work done**: Ran `auto_scan.py --h11 17 --skip-t025 --top 200 -w 3` on Codespace
(4 CPUs, 15GB RAM). Loaded existing scan_h17.csv (38,735 polytopes, 10,624 T0.25 passes).
Selected top 200 by max_h0 (cutoff: h0≥10). Deep-analyzed 200, fiber-classified 193.
Total time: **3.0 minutes**.

### Results summary

| Metric | Value |
|--------|-------|
| Polytopes scanned (T0.25) | 38,735 |
| T0.25 passes | 10,624 (27.4%) |
| Deep-analyzed (Stage 1) | 200 |
| Fiber-analyzed (Stage 2) | 193 |
| Score 26/26 (perfect) | **87** |
| Score 25/26 | 26 |
| SM gauge group (SU3×SU2×U1) | **193/193 (100%)** |
| SU(5) GUT candidates | **166/193 (86%)** |
| Max clean bundles | 59 (P767) |
| Max elliptic fibrations | 15 (P695) |
| Max Swiss cheese τ | 8,608 (P860) |

### Top 10 candidates

| Rank | Poly | Score | Clean | h0 | dP | SC | τ | K3 | Ell | Gauge |
|------|------|-------|-------|----|----|----|---|-----|-----|-------|
| 1 | P767 | 26/26 | 59 | 17 | 3 | ✓ | 1 | 5 | 10 | su(2)×su(4)×su(2)×su(3) |
| 2 | P389 | 26/26 | 41 | 10 | 3 | ✓ | 185 | 2 | 1 | su(2)×su(3)×su(4)×su(2) |
| 3 | P251 | 26/26 | 38 | 10 | 6 | ✓ | 539 | 4 | 4 | su(4)×su(9)/e8 |
| 4 | P1033 | 26/26 | 35 | 15 | 5 | ✓ | 64 | 6 | 11 | su(2)×su(4)×su(4)×su(2) |
| 5 | P1096 | 26/26 | 35 | 12 | 6 | ✓ | 344 | 4 | 4 | su(4)×su(8)/e7 |
| 6 | P996 | 26/26 | 35 | 32 | 3 | ✓ | 30 | 3 | 3 | su(4)×su(4)×su(2)×su(4) |
| 7 | P4126 | 26/26 | 35 | 11 | 5 | ✓ | 74 | 3 | 3 | su(6)×su(6)×su(3) |
| 8 | P1180 | 26/26 | 34 | 10 | 6 | ✓ | 564 | 5 | 6 | su(5)×su(8)/e7 |
| 9 | P2297 | 26/26 | 33 | 23 | 6 | ✓ | 28 | 5 | 8 | su(2)×su(6)×su(6) |
| 10 | P894 | 26/26 | 33 | 10 | 5 | ✓ | 110 | 4 | 6 | su(2)×su(2)×su(4)×su(5) |

### Notable findings

- **87 perfect-score polytopes** at h11=17 vs. 19 at h11≤16 combined — dramatic scaling
- **100% SM rate** across all 193 fiber-analyzed polytopes (every single one has SU3×SU2×U1)
- **86% GUT rate** (166/193 have SU(5) subgroup) — up from 67% at h15
- **P767** has 59 clean bundles and 10 elliptic fibrations — richest structure seen
- **P860** has τ=8,608 (LVS candidate, though h15/poly61 still holds record at τ=14,300)
- **P1033** has 11 elliptic fibrations (second only to h16/poly74's 10 in old pipeline)
- **P996** has max_h0=32 (highest h⁰ value among top-ranked)

---

## 2026-02-25 — B-28: Automated scan pipeline (`auto_scan.py`)

**Work done**: Built `auto_scan.py` (925 lines) — a single-command pipeline that
replaces the 6-script manual workflow (scan_fast → tier1_screen → tier15_screen →
tier2_screen → pipeline → fiber_analysis) with one automated run.

### Architecture

Three pipeline stages per polytope:

| Stage | Name | Per-poly time | What it does |
|-------|------|---------------|--------------|
| 0 (T0.25) | Pre-filter | ~0.08s | Early-termination h⁰≥3 check. Parallel. |
| 1 (deep)  | Full analysis | ~2-30s | Bundle count + clean bundles + dP/K3 divisors + Swiss cheese + K3/elliptic fibrations. Parallel. 26-point scoring. |
| 2 (fiber) | Kodaira | ~1-5s | Fiber polygon classification + gauge algebra + SM/GUT detection. Sequential. |

### Validation

**h14 test** (22 polytopes, 23s):
- P2 ranked #1 at 26/26 with τ=58, SM★, GUT★ — matches pipeline.py exactly
- 14/14 fiber-analyzed polytopes have SM gauge factors
- 10/14 have SU(5) GUT

**h15 scale test** (553 polytopes, 8 minutes):
- T0.25: 333/553 pass (60.2%) in 6.8m — matches known figure exactly
- Stage 1: top 50 deep-analyzed in 1.1m
- Stage 2: 48/50 fiber-classified (48 have elliptic fibrations)
- **6× 26/26 perfect**, 12× 25/26, 6× 23/26
- **47/48 contain SM gauge factors** (98%) — only P7 is U(1)^10
- **32/48 have SU(5) GUT** (67%)
- Max τ = 11,400 (P387, new h15 LVS champion)
- Max clean = 38 (P256)

**Resume test**: Checkpoint loads all completed polytopes, skips to results in 1s.

### Swiss cheese bug fix

`cy_compute.check_swiss_cheese()` uses `cyobj.compute_divisor_volumes()` which can
return negative volumess (not physical). The pipeline.py approach — manual intersection
tensor contraction with `tau2 > 0` guard and `V2 > 100` check — gives correct results.

Before fix: P2 τ=-8789 (wrong). After fix: P2 τ=58 (matches pipeline's 58.5).

### Usage
```bash
python auto_scan.py --h11 19 --workers 8 --top 100
python auto_scan.py --h11 15 --top 0 -w 3          # all passes
python auto_scan.py --h11 18 --resume               # resume from checkpoint
```

---

## 2026-02-25 — B-21 complete: F-theory Kodaira fiber classification

**Work done**: Built `fiber_analysis.py` (890 lines) — a comprehensive F-theory
elliptic fibration analysis tool. Classifies toric fiber polygons via GL₂(ℤ)
invariants, computes Kodaira singular fiber types from toric tops, assembles
gauge algebras, and detects SU(3)×SU(2)×U(1) (SM) and SU(5) (GUT) candidates.

### Key finding

**39/39 fibrations** across all 8 top-scoring candidates contain the Standard Model
gauge group SU(3) × SU(2) × U(1) as factors. **17/39 are SU(5) GUT candidates**.

| Candidate | Fibs | SM | SU(5) GUT | Max Rank | Distinct Algebras |
|-----------|------|----|-----------|----------|-------------------|
| h14/poly2 | 1 | 1 | 1 | 10 | 1 |
| h15/poly61 | 3 | 3 | 0 | 9 | 3 |
| h15/poly94 | 4 | 4 | 2 | 10 | 4 |
| h16/poly63 | 4 | 4 | 2 | 10 | 4 |
| h16/poly74 | 10 | 10 | 2 | 10 | 9 |
| h17/poly25 | 8 | 8 | 6 | 10 | 5 |
| h17/poly53 | 3 | 3 | 0 | 8 | 3 |
| h17/poly63 | 6 | 6 | 6 | 10 | 6 |
| **Total** | **39** | **39** | **17** | — | — |

### Notable gauge algebras

- **h17/poly25 fib 3–7**: su(2) × su(3) × su(5) × su(4) — contains SM + SU(5) GUT
- **h17/poly63 fib 1–4**: su(2) × su(3) × su(5), su(3) × su(3) × su(5) — GUT candidates
- **h14/poly2**: su(6) × su(6) × U(1)² — largest single-fibration rank
- **h16/poly74**: 10 distinct fibrations (9 distinct algebras) — richest structure

### Technical fixes during implementation

1. **Reflexive 2D polygon database**: Rebuilt from exhaustive enumeration — 15/16 
   GL₂(ℤ)-classified polygons with precomputed invariants (n_pts, n_hull, edge_gcds, 2×area).
2. **Lattice point enumerator**: Rewrote `_lattice_pts_of_polygon()` — compute convex 
   hull first, use proper inward normals for CCW-ordered hull vertices.
3. **2D fiber projection**: Fixed half-integer coordinate bug — K3 directions don't 
   always form a lattice basis. Added fallback to find proper integer basis from actual 
   subspace lattice points.
4. **Pipeline fibration dedup** (`pipeline.py`): Added `frozenset(subspace_pts)` 
   deduplication — was counting 15 generator pairs vs 8 actual unique fibrations.

### Confidence assessment

- Fiber polygon classification: **high** (invariant-based, 15/16 known)
- Kodaira type from excess: **medium** (heuristic — excess n → I_{n+1}, no D/E branching)
- Gauge algebra: **medium** (correct for A-type singularities, may mis-identify D/E)
- SM/GUT detection: **high** (conservative substring matching)

---

## 2026-02-23 — B-24 complete: full pipeline on all 37 T2=45 candidates

**Work done**: Ran `pipeline.py` on the remaining 24 T2=45 candidates (all h¹¹ = 15–19). Combined with the 13 prior runs, this completes the full pipeline analysis across all top-scoring T2 polytopes.

### Summary

| Metric | Value |
|--------|-------|
| Total pipeline runs | **37** |
| Perfect 26/26 | **19** |
| Score 25/26 | 5 |
| Score 23/26 | 10 |
| Score 22/26 | 2 |
| Score 18/20 (old fmt) | 1 (h13/poly1) |
| Max clean bundles | **418** (h17/poly53) |
| Max τ (Swiss cheese) | **14,300** (h15/poly61) |
| Max elliptic fibs | **15** (h17/poly25, h17/poly45) |
| Max K3 fibs | **6** (h17/poly25, h17/poly45) |
| Total wall-clock | ~7 min (sequential, local) |

### Complete results (sorted by score, then clean count)

| Candidate | Score | Clean | K3 | Ell | τ_SC |
|-----------|-------|-------|----|-----|------|
| h15/poly94 | **26/26** | 380 | 4 | 6 | 241 |
| h14/poly2 | **26/26** | 320 | 3 | 3 | 58 |
| h16/poly11 | **26/26** | 298 | 3 | 3 | 150 |
| h16/poly86 | **26/26** | 224 | 4 | 6 | 1,536 |
| h17/poly63 | **26/26** | 218 | 5 | 10 | 84 |
| h17/poly89 | **26/26** | 184 | 3 | 3 | 2,598 |
| h18/poly34 | **26/26** | 184 | 4 | 6 | — |
| h17/poly8 | **26/26** | 180 | 3 | 3 | 2,208 |
| h17/poly90 | **26/26** | 176 | 3 | 3 | 1,168 |
| h17/poly25 | **26/26** | 170 | 6 | 15 | 56 |
| h16/poly74 | **26/26** | 158 | 5 | 10 | 114 |
| h17/poly21 | **26/26** | 142 | 4 | 6 | 243 |
| h18/poly31 | **26/26** | 134 | 4 | 6 | — |
| h16/poly40 | **26/26** | 112 | 5 | 10 | 102 |
| h15/poly25 | **26/26** | 106 | 3 | 3 | 5,255 |
| h15/poly67 | **26/26** | 82 | 4 | 6 | 128 |
| h16/poly73 | **26/26** | 82 | 3 | 3 | 108 |
| h16/poly63 | **26/26** | 78 | 4 | 6 | 836 |
| h18/poly6 | **26/26** | 74 | 3 | 3 | 588 |
| h17/poly53 | 25/26 | 418 | 3 | 3 | 1,016 |
| h17/poly51 | 25/26 | 340 | 3 | 3 | 210 |
| h19/poly67 | 25/26 | 312 | 3 | 3 | 24 |
| h17/poly96 | 25/26 | 252 | 2 | 1 | 252 |
| h15/poly61 | 25/26 | 110 | 3 | 3 | 14,300 |
| h16/poly53 | 23/26 | 300 | 5 | 10 | — |
| h17/poly9 | 23/26 | 192 | 1 | 0 | 72 |
| h15/poly23 | 23/26 | 134 | 4 | 6 | — |
| h16/poly22 | 23/26 | 112 | 4 | 6 | — |
| h17/poly58 | 23/26 | 112 | 3 | 3 | — |
| h17/poly32 | 23/26 | 104 | 3 | 3 | — |
| h16/poly3 | 23/26 | 100 | 4 | 6 | — |
| h15/poly86 | 23/26 | 86 | 5 | 10 | — |
| h16/poly55 | 23/26 | 78 | 5 | 10 | — |
| h17/poly45 | 23/26 | 68 | 6 | 15 | — |
| h18/poly32 | 22/26 | 308 | 4 | 6 | — |
| h19/poly16 | 22/26 | 86 | 5 | 10 | — |

### Key new discoveries

1. **h15/poly94** — new clean-bundle champion at 26/26 (380 clean, τ=241). Surpasses h14/poly2 (320) as the polytope with most clean h⁰=3 bundles among perfect scorers.
2. **h17/poly53** — most clean bundles overall (418), but scores 25/26 (no Swiss cheese checkpoint reported). τ=1,016 from Swiss cheese analysis.
3. **h17/poly51** — 340 clean, 25/26, τ=210.
4. **h16/poly86** — 224 clean, 26/26, τ=1,536 (strong LVS).
5. **h17/poly89** — 184 clean, 26/26, τ=2,598 (second-best τ among 26/26 scorers after h15/poly25's 5,255).
6. **h16/poly74** — 158 clean, 26/26, 10 elliptic fibs. F-theory candidate.
7. **h17/poly45** — 68 clean, K3=6, **15 elliptic fibs** (ties h17/poly25 record), but 23/26 (no Swiss cheese).

### Score = 23/26 pattern

All 10 polytopes scoring 23/26 fail the same 3 checkpoints: Swiss cheese (no τ found), and the two LVS-derived checks. These are geometrically viable candidates where the Kähler cone simply doesn't admit the large 4-cycle / small 4-cycle hierarchy needed for LVS moduli stabilization.

---

## 2026-02-23 — h18 T2 complete (81/87 PASS); T1 batch launched on 21K pool

**Work done**: Full T2 screening of top 87 h18 candidates (max_h0≥5, favorable). T1 batch launched on remaining 21K T0.25 passes.

### Pipeline state
- h18 T0.25 scan: **complete** — 105,811 polytopes, 30,293 passes (commits `02f4c3a`)
- h18 T2 (high-h0): **complete** — 87 screened, **81 PASS**, 6 NONE (commits `e6977c9`)
- h18 T1 (21K pool): **running** on Hetzner (`batch_t1_h18.py`, 14 workers, ~2hr ETA)

### h18 T2 results — 81/87 PASS

**n_clean distribution** (87 screened, min_h0≥5, favorable only):

| n_clean range | count |
|---|---|
| 30+ | 21 |
| 20–29 | 11 |
| 10–19 | 16 |
| 5–9 | 27 |
| 1–4 | 6 |

**Top candidates by n_clean:**

| poly_idx | max_h0 | n_clean | K3 | elliptic |
|----------|--------|---------|----|----------|
| 3105 | 6 | **40** | 2 | 1 |
| 37037 | 6 | **40** | 4 | 4 |
| 34670 | 7 | **38** | 2 | 1 |
| 18005 | 6 | **38** | 2 | 1 |
| 25921 | 6 | **38** | 3 | 3 |
| 57305 | 6 | **38** | 4 | 4 |
| 178 | 10 | 32 | 1 | 0 |

**Top by elliptic fibrations:**

| poly_idx | elliptic | K3 | n_clean |
|----------|----------|----|---------|
| 30303 | **13** | 6 | 9 |
| 91896 | **13** | 6 | 17 |
| 8607 | 9 | **7** | 15 |
| 17309 | 9 | **7** | 1 |
| 32432 | 9 | **7** | 3 |
| 35953 | 9 | **7** | 2 |

**New records (pending T1/Swiss cheese verification):**
- K3 fibrations: 4 polys with k3=7 — exceeds current all-time record of 6 (h17/poly25)
- Elliptic: 13 — below h17/poly25 record of 15
- n_clean: 40 — below h14/poly2 record of 320 (but search was restricted at h18 due to h11_eff=18 coefficient limits)

**6 NONE polys** (max_h0≥5 but zero clean bundles — h³≠0 on everything):
- poly 2476 (max_h0=7, 1548 bundles checked)
- poly 16290 (max_h0=7, 1632 bundles checked)
- poly 29123, 7122, 25462, 39779 (max_h0=5–6)

### T1 batch (21K pool) — running
- Script: `batch_t1_h18.py` (committed `81b584d`)
- Input: 21,115 favorable polys with max_h0≥3 from combined T0.25 CSVs
- Checks: dP classification + Swiss cheese + GL symmetry order
- Workers: 14, ETA ~2hrs
- Output: `results/tier1_h18.csv`
- Next step: join T1 results with T2 results → full scoring → identify h18 champions

### Decision log
- Skipped T1.5 for top-87 pool (appropriate: max_h0≥5 is stronger than T1.5 gate)
- T1 on full 21K instead of T1.5 first: Hetzner idle, T1 is faster per-poly (~2-5s vs 5-30s), produces richer output (dP types, Swiss τ, sym order) directly useful for scoring
- After T1: candidates with n_dp≥3 + has_swiss → send to T2 (will be manageable subset)

---

## 2026-02-24 — Hetzner dedicated server provisioned

**Work done**: Provisioned Hetzner dedicated server as primary compute node.

- **Hardware**: i9-9900K (8c/16t), 128 GB RAM, 2× 1TB NVMe RAID-1
- **OS**: Ubuntu 24.04.3 LTS, installed via Hetzner `installimage`
- **Partitions**: LVM on RAID-1 — 100G root, 200G /home, 200G /var/lib/docker, 50G /tmp (~400G unallocated)
- **Stack**: Docker 29.2.1, devcontainer CLI 0.83.3, tmux, git
- **Dev container**: Built from `.devcontainer/Dockerfile` — Python 3.12, CYTools 1.4.5, pplpy, python-flint
- **User**: `seth` with Docker group + passwordless sudo + SSH key auth
- **Benchmark**: `scan_fast.py` at 12.7 poly/s (8 workers) — **5.3× faster than Dell5**
- **Docs**: See [HETZNER.md](HETZNER.md) for connection details, scan commands, rebuild instructions.

---

## 2026-02-24 — Tier 0.25 fast pre-filter (`scan_fast.py`)

**Work done (B-25)**: Built and validated a fast pre-filter for χ=-6 polytope screening.

### Problem
Full scans (`scan_parallel.py`) run at ~1 poly/s. At h18 (195K polytopes), that's 50+ hours. For h19-h21, it's infeasible. We needed a faster screening tool.

### Approach tried and rejected: Probe-based pre-filter
- Idea: Rank bundles by a cheap proxy (|D³| descending, then ‖D‖₁ ascending), probe only top-N.
- Probe v1 (|D³| desc, N=50): 10.2% recall — terrible.
- Probe v2 (‖D‖₁ asc, N=200): 29.4% recall — still terrible.
- **Root cause**: h⁰≥3 bundles are ~1% of χ=3 bundles per polytope. No cheap proxy predicts which bundles have h⁰(X,D)≥3. The Koszul difference h⁰(V,D) − h⁰(V,D+K_V) is fundamentally unpredictable without computing both lattice-point counts.

### Solution: Early termination + ambient h⁰ bound
Two synergistic optimizations:
1. **`min_h0=3` ambient bound** (in `compute_h0_koszul`): If h⁰(V,D) < 3, then h⁰(X,D) ≤ h⁰(V,D) < 3 → skip the second lattice-point count entirely. Saves ~40% of second-count computations.
2. **Early termination**: For pass/fail classification, stop scanning bundles as soon as the first h⁰≥3 is found. On hit polytopes, this scans only 13% of bundles on average.

### Validation (h15, 553 polytopes)
- **Recall: 100%** (333/333 actual hits caught)
- **Precision: 100%** (0 false positives)
- **Speed: 2.4 poly/s** (~2.4× faster than full scan's ~1.0 poly/s)
- Early termination saves 696K bundle evaluations
- Average first hit at bundle #316 / 2408 (13.1% of bundle set)

### Key insight
For Tier 0.25 screening, we only need to know IF a polytope has any h⁰≥3 bundle, not HOW MANY. This asymmetry is the entire speedup: hit polytopes stop early (huge savings), while non-hit polytopes must scan all bundles (no shortcut possible). The `min_h0=3` bound adds modest savings on non-hit polytopes by avoiding the second lattice-point count when the ambient Koszul h⁰ is already too small.

---

## 2026-02-23 04:00 — 4 new pipeline runs (2× 26/26) + h17 scan launched on Codespace

**Work done (B-22, B-19)**: Full pipeline on 4 new candidates. h17 scan launched on Codespace in tmux with keepalive.

### New pipeline results

| Polytope | Score | Clean | h⁰≥3 | max h⁰ | K3 | Ell | dP | Swiss τ | Notes |
|----------|-------|-------|-------|--------|----|-----|----|---------|-------|
| **h17/poly25** | **26/26** | 170 | 490 | 8 | 6 | **15** | 2 | 56 | **NEW F-theory + triple-threat champion** |
| **h16/poly63** | **26/26** | 78 | 584 | 37 | 4 | 6 | 5 | 836 | Triple-threat #2 |
| h16/poly53 | 23/26 | **300** | 1100 | 16 | 5 | 10 | 6 | — | 2nd-most clean ever, no Swiss cheese |
| h19/poly16 | 22/26 | 86 | 564 | 27 | 5 | 10 | 5 | — | h¹¹=19 (loses tractability point) |

**h17/poly25** is the new F-theory champion: **15 elliptic fibrations** (previous record: 10, h17/poly63). Also scores 26/26 with Swiss cheese τ=56, making it a "triple-threat" — viable for heterotic, F-theory, AND LVS simultaneously.

**h16/poly53** has 300 clean bundles — second only to h14/poly2 (320) — but no Swiss cheese structure, so scores 23/26.

### Updated full pipeline leaderboard (12 runs, 7× 26/26)

| Polytope | Score | Clean | K3 | Ell | dP | Swiss τ | Title |
|----------|-------|-------|----|-----|----|---------|-------|
| h14/poly2 | 26/26 | **320** | 3 | 3 | 3 | 58.5 | Heterotic champion |
| h16/poly53 | 23/26 | **300** | 5 | 10 | 6 | — | 2nd most clean, no LVS |
| h16/poly11 | 26/26 | **298** | 3 | 3 | 5 | 150 | |
| h17/poly96 | 25/26 | **252** | 2 | 1 | 0 | 252 | max h⁰=65 |
| h17/poly63 | 26/26 | **218** | 5 | 10 | 6 | 84 | Former F-theory champion |
| h17/poly9 | 23/26 | **192** | 1 | 0 | 0 | 72 | |
| h18/poly34 | 26/26 | **184** | 4 | 6 | 5 | 0 | |
| h17/poly8 | 26/26 | **180** | 3 | 3 | 4 | 2,208 | |
| **h17/poly25** | **26/26** | **170** | **6** | **15** | 2 | 56 | **F-theory + triple-threat champ** |
| h15/poly61 | 25/26 | **110** | 3 | 3 | 0 | **14,300** | LVS champion |
| h19/poly16 | 22/26 | 86 | 5 | 10 | 5 | — | |
| h16/poly63 | 26/26 | 78 | 4 | 6 | 5 | 836 | Triple-threat #2 |

### Triple-threat rankings (Heterotic + F-theory + LVS)

Candidates that score well across all three compactification approaches:

1. **h17/poly25**: 26/26, 170 clean, 15 ell (record!), τ=56, 2 dP
2. **h16/poly63**: 26/26, 78 clean, 6 ell, τ=836, 5 dP
3. **h17/poly8**: 26/26, 180 clean, 3 ell, τ=2,208, 4 dP
4. **h16/poly11**: 26/26, 298 clean, 3 ell, τ=150, 5 dP

### h17 scan launched on Codespace

- Codespace: bookish-sniffle-g46r9xgj9vprh9pp4 (4 cores)
- Running in tmux session `h17scan` with keepalive (SSHs every 29 min)
- 38,735 polytopes, 4 workers, ~5.8 hrs ETA
- At last check: 100/38,735 (0.26%), 1.8 poly/s, 72 hits

---

## 2026-02-23 00:30 — h15/poly61 full pipeline (25/26, τ=14,300) + h16 complete

**Work done (B-23, B-19)**: Full pipeline on h15/poly61. h16 scan complete (5180/5180). h16 screened through T1→T1.5→T2.

### h15/poly61 full pipeline → 25/26, LVS champion

`python pipeline.py --h11 15 --poly 61` → 13s runtime.

| Metric | T2 (probe) | Full Pipeline | Δ |
|--------|-----------|---------------|---|
| Clean h⁰=3 | 103 | **110** | +7% |
| h⁰≥3 | (probe) | **338** | — |
| Max h⁰ | 4 | **4** | same |
| χ=±3 bundles | — | **13,256** | — |

Key result: **Swiss cheese τ = 14,300.0** — 6.5× the previous best (h17/poly8 at τ=2,208). Only loses the dP point (0 del Pezzo divisors → 0/1). Score: **25/26**.

### Updated full pipeline leaderboard

| Polytope | Score | Clean | K3 | Ell | dP | Swiss τ | Title |
|----------|-------|-------|----|-----|----|---------|-------|
| h14/poly2 | 26/26 | **320** | 3 | 3 | 3 | 58.5 | Heterotic champion |
| h16/poly11 | 26/26 | **298** | 3 | 3 | 5 | 150.0 | |
| h17/poly96 | 25/26 | **252** | 2 | 1 | 0 | 252.0 | |
| h17/poly63 | 26/26 | **218** | 5 | 10 | 6 | 84.0 | F-theory champion |
| h17/poly9 | 23/26 | **192** | 1 | 0 | 0 | 72.0 | |
| h18/poly34 | 26/26 | **184** | 4 | 6 | 5 | 0.0 | |
| h17/poly8 | 26/26 | **180** | 3 | 3 | 4 | 2,208 | |
| **h15/poly61** | **25/26** | **110** | 3 | 3 | 0 | **14,300** | **LVS champion** |

### h16 full scan → 5,180/5,180 complete ✅

| Metric | Value |
|--------|-------|
| Polytopes scanned | 5,180 (100%) |
| Hits (h⁰≥3) | 1,811 (35%) |
| Runtime | 52.9 min |
| Throughput | 1.6 poly/s |

### h16 T1 → T1.5 → T2 screening

- **T1**: 30 screened, 17/30 Swiss cheese. Best: h16/poly329 (score=41, max h⁰=15). 374 total T1 entries.
- **T1.5**: 20 screened, 19/20 T2-worthy (17s). 338 total T1.5 entries.
- **T2**: 20 screened, all 20 ★★★ (56s). 36 total T2 entries.

T2 top new performers:
- h19/poly16: T2=45, 69 clean, max h⁰=27, 5 K3 + 6 ell
- h18/poly32: T2=45, 49 clean, max h⁰=30
- h17/poly53: T2=45, 45 clean
- h15/poly94: T2=45, 36 clean, 4 K3 + 4 ell

### Scan coverage

| h11 | Polytopes | Scanned | Coverage |
|-----|-----------|---------|----------|
| 13 | 3 | 3 | 100% |
| 14 | 22 | 22 | 100% |
| 15 | 553 | 553 | 100% |
| 16 | 5,180 | 5,180 | 100% |
| 17 | 38,735 | 100 | 0.26% |

h13–h16 fully covered. h17 (38,735 polytopes, ~3.7 hrs) deferred to Codespace.

---

## 2026-02-22 23:30 — Expanded scan: h15 complete, h16 running, new T2 discovery

**Work done (B-19)**: Built `scan_parallel.py` multiprocessing scanner and expanded the scan beyond the original `limit=100` cap.

### scan_parallel.py — 4× speedup

New multiprocessing scanner using `mp.Pool` with configurable workers. Key design decisions:
- Worker function `_scan_one()` takes serialized vertex lists (CYTools `Polytope` objects aren't picklable)
- `imap_unordered` with `chunksize=4` for load balancing across polytopes of varying complexity
- Resume support via `--resume CSV_PATH` (skips already-scanned `(h11, poly_idx)` pairs)
- Dual output: `.log` (tier1_screen.py compatible) + `.csv` (machine-readable)
- Progress reporting every 50 polytopes with rate and ETA

Performance: **1.0–1.4 poly/s** with 4 workers on a 4-core machine (vs ~0.3 poly/s serial).

### h15 full scan — 553/553 complete ✅

| Metric | Original (limit=100) | Expanded (all 553) |
|--------|---------------------|--------------------|
| Polytopes scanned | 100 | **553** |
| Hits (h⁰≥3) | ~60 | **333** (60%) |
| Runtime | ~2 min | **9.2 min** |

### h16 scan — in progress 🔶

5,180 polytopes at 1.4 poly/s. At 1800/5180 (35%) with 913 hits (51% rate). ETA ~40 min.

### T1 → T1.5 → T2 screening on new h15 candidates

Ran the full screening pipeline on new h15 hits while h16 scan runs:

- **T1**: Top 30 screened → 16/30 have Swiss cheese structure. **h15/poly 127** scores 40 (max h⁰=17, 8 dP divisors)
- **T1.5**: 20 screened → 19/20 T2-worthy (≥3 clean in 300-bundle probe)
- **T2**: 20 screened → **h15/poly 61 has 103 clean bundles** (new #5 overall)

### New discovery: h15/poly 61

Previously invisible (poly index 61 > original limit of 100). Now ranks #5 in the entire T2 leaderboard:

| Rank | Polytope | Clean h⁰=3 | Source |
|------|----------|-----------|--------|
| 1 | h16/poly11 | 255 | Pipeline |
| 2 | h17/poly63 | 198 | Pipeline |
| 3 | h18/poly34 | 189 | Pipeline |
| 4 | h17/poly90 | 148 | T2 |
| **5** | **h15/poly61** | **103** | **NEW — expanded scan** |
| 6 | h14/poly5 | 74 | T2 |

h15/poly 61 has 3 K3 + 3 elliptic fibrations and max h⁰ = 4 (modest). Needs full pipeline run.

**Also notable**: h15/poly 94 (36 clean, 4 K3+4 ell), h15/poly 33 (16 clean, 9 dP — highest dP count).

### Infrastructure
- `.gitignore`: Added `!results/*.log` exception so scan logs are tracked
- Committed `d45fbd8`: scanner + h15 results
- Total scanned: 1,025 → **1,478** polytopes (h15 expanded from 100 to 553)

---

## 2026-02-22 22:00 — Full pipeline on all top 7 candidates: 5× perfect 26/26

**Work done**: Ran `pipeline.py` on the remaining 5 top T2 candidates (h16/poly11, h17/poly96, h18/poly34, h17/poly9, h17/poly8). Combined with the earlier h14/poly2 and h17/poly63 runs, all 7 top candidates are now fully analyzed.

**Full leaderboard** (sorted by clean bundles):

| Polytope | Score | Clean | T2→Pipe Δ | K3 | Ell | dP | Swiss τ |
|----------|-------|-------|-----------|-----|-----|-----|---------|
| h14/poly2 | 26/26 | **320** | +52 | 3 | 3 | 3 | 58.5 |
| h16/poly11 | 26/26 | **298** | +43 | 3 | 3 | 5 | 150.0 |
| h17/poly96 | 25/26 | **252** | +25 | 2 | 1 | 0 | 252.0 |
| h17/poly63 | 26/26 | **218** | +20 | 5 | **10** | **6** | 84.0 |
| h17/poly9 | 23/26 | **192** | +11 | 1 | 0 | 0 | 72.0 |
| h18/poly34 | 26/26 | **184** | −5 | 4 | 6 | 5 | 0.0 |
| h17/poly8 | 26/26 | **180** | +21 | 3 | 3 | 4 | **2208** |

**Key findings**:
- **5 of 7 score 26/26** (perfect). h17/poly96 loses 1 point (no dP). h17/poly9 loses 3 (no ell, no dP).
- **Full pipeline consistently finds more clean bundles** than T2 screen (avg +24, range −5 to +52). The more thorough h³ verification via Serre duality catches bundles the T2 heuristic misses.
- **h16/poly11 is the new #2** — 298 clean, 5 dP, 3 ell. Previously had only 1 ell fibration in T2.
- **h17/poly8 has best LVS structure**: τ=2208 is 37× larger than any other candidate. Extremely strong volume hierarchy.
- **h18/poly34 has τ=0.0** — a degenerate Swiss cheese direction. The flag passes but the LVS hierarchy is absent. May need investigation.
- **h17/poly9 scores lowest (23/26)** despite 192 clean bundles — zero elliptic fibrations and zero dP divisors limit its physics utility.

**Runtime**: 16-18s per candidate (total batch ~85s). All output saved to `results/pipeline_h{h11}_P{poly}_output.txt`.

---

## 2026-02-22 21:00 — Generic pipeline.py + h17/poly63 Full Pipeline: 26/26, 218 clean

**Work done**: Refactored all pipeline code into a single generic `pipeline.py` that takes `--h11` and `--poly` arguments. No more per-candidate custom scripts. All heavy computation imported from `cy_compute.py`. Ran full Stages 1-4 on h17/poly63.

**Architecture change**: `cy_compute.py` is the shared computational core (vectorized lattice points, batch χ, precomputed vertex data). `pipeline.py` is the single entry point:
```
python pipeline.py --h11 14 --poly 2    # champion
python pipeline.py --h11 17 --poly 63   # F-theory champion
python pipeline.py --h11 18 --poly 34   # next candidate
```
Old per-candidate scripts (`pipeline_h14_P2.py`, `pipeline_h13_P1.py`) still work but are superseded.

**h17/poly63 Full Pipeline Results**:
- **26/26 score** — perfect (same as h14/poly2)
- **218 clean bundles**: h⁰=3, h¹=h²=h³=0 (up from 198 in T2 screen)
- 14,458 total χ=±3 bundles searched (max_nonzero=4, max_coeff=3)
- 922 bundles with h⁰≥3 (6.4% of total)
- Max h⁰ = 40
- 1 nef bundle out of 14,458
- 61 distinct D³ values among clean bundles (range [-59, 59])
- Non-favorable: h11=17, h11_eff=13
- SHA-256 fingerprint: 3cc2448f341e6e9a
- Runtime: 25s

**Divisor structure**:
- 6 del Pezzo candidates (e2: dP₄, e5: dP₈, e7: dP₄, e8: dP₆, e9: dP₇, e10: dP₇)
- 1 K3-like divisor (e0: D³=0, c₂·D=36)
- 6 rigid divisors

**Swiss cheese structure**: 1 direction
- e12: τ=84.0, V=853536, τ/V^(2/3)=0.00934

**Fibrations**: 5 K3 + 10 elliptic (up from 6 elliptic in T2 — full pipeline methodology finds more)

**Comparison of the two champions**:

| Metric | h14/poly2 | h17/poly63 | Winner |
|--------|-----------|------------|--------|
| Score | 26/26 | 26/26 | Tie |
| Clean bundles | **320** | 218 | h14/poly2 |
| Max h⁰ | 13 | **40** | h17/poly63 |
| K3 fibrations | 3 | **5** | h17/poly63 |
| Elliptic fibrations | 3 | **10** | h17/poly63 |
| dP divisors | 3 | **6** | h17/poly63 |
| Swiss cheese dirs | **3** | 1 | h14/poly2 |
| h¹¹ (lower=simpler) | **14** | 17 | h14/poly2 |

h14/poly2 = **heterotic champion** (most clean bundles, simplest moduli). h17/poly63 = **F-theory champion** (most fibrations, richest divisor structure).

**Performance**: All screening scripts + pipeline now import from `cy_compute.py`. Speedups:
- pipeline: 271s → 25-30s (10-19×)
- tier2 per polytope: 87s → 7.4s (12×)
- scan per polytope: 8s → 0.6s (13×)
- ~700 lines of duplicated code removed across 5 scripts

**Commits**: `9bc4145` (pipeline_h14_P2 refactor), `6e3da48` (generic pipeline.py + h17/poly63)

---

## 2026-02-22 20:15 — cy_compute refactoring: all scripts accelerated

**Work done**: Created `cy_compute.py` shared computational module. Refactored all 4 screening scripts (`scan_chi6_h0.py`, `tier1_screen.py`, `tier15_screen.py`, `tier2_screen.py`) and `pipeline_h14_P2.py` to import from it.

**Bug found and fixed**: `build_intnum_tensor()` was symmetrizing intersection numbers to all 6 permutations of (i,j,k). CYTools stores sorted-index entries only (i≤j≤k), so the scalar `compute_chi()` sums correctly, but the symmetrized tensor caused 3-6× D³ overcounting. Fixed by removing symmetrization. Verified: all test bundles match scalar vs batch.

**Commits**: `d37e1e1` (cy_compute creation), `761fd34` (screening refactoring + tensor fix)

---

## 2026-02-22 19:30 — h14/poly2 Full Pipeline: 26/26, 320 clean bundles — new champion

**Work done**: Built `pipeline_h14_P2.py`. Full Stages 1-4 of FRAMEWORK.md on h11=14, polytope 2 — the #1 ranked candidate from 177 T2-screened polytopes.

**Bug fixed during development**: `IndexError: index 13 is out of bounds for axis 0 with size 13`. Root cause: non-favorable polytope (h11=14 but h11_eff=13). All 5 instances of `range(h11)` replaced with `range(h11_eff)` where `h11_eff = len(div_basis)`. Same class as Bug #11 (B-11).

**Key results**:
- **26/26 score** — perfect on the expanded 26-point scorecard
- **320 clean bundles**: h⁰=3, h¹=h²=h³=0 (no higher cohomology)
- 14,608 total χ=±3 bundles searched (max_nonzero=4, max_coeff=3)
- 828 bundles with h⁰≥3 (5.7% of total)
- Max h⁰ = 13 (6 bundles, e.g. D = 3·e0 + 3·e4 + 1·e8 + 1·e11)
- 1 nef bundle out of 14,608
- 61 distinct D³ values among clean bundles (range [-63, 63])
- Non-favorable: h11=14, h11_eff=13
- SHA-256 fingerprint: f6c14152f6f3b812
- Runtime: 271s (4.5 min)

**Divisor structure**:
- 3 del Pezzo candidates (e5: dP₄, e9: dP₄, e10: dP₇)
- 2 K3-like divisors (e0: D³=0, c₂·D=36; e2: D³=0, c₂·D=12)
- 6 rigid divisors

**Swiss cheese structure**: 3 directions found
- e9: τ=58.5, τ/V^(2/3)=0.00113 — best LVS candidate
- e8: τ=723.0, τ/V^(2/3)=0.01395
- e6: τ=1487.5, τ/V^(2/3)=0.02835

**Fibrations**: 3 K3 + 3 elliptic (matches T2 for K3; T2 only found 1 elliptic — full pipeline methodology is more thorough)

**Cohomology breakdown** (h⁰≥3 bundles):
- 320 clean (h⁰=3, h³=0) — of which 160 have h¹-h²=0 (truly pristine), 207+89 have h¹-h²=6 (vector-like pairs)
- 74 with h⁰=6, 53 with h⁰=10, 6 with h⁰=11, 3 with h⁰=13

**Comparison with previous champions**:

| Polytope | Score | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell | Swiss |
|----------|-------|------------|-------|--------|-----|-----|-------|
| **h14/poly2** | **26/26** | **320** | **828** | **13** | 3 | 3 | 3 dirs |
| h13/poly1 | 18/20 | 25 | 76 | 6 | 3 | 3 | 1 dir |
| Polytope 40 | 10/20 | 0 | 0 | 2 | 3 | 3 | 1 dir |

h14/poly2 has **12.8× more clean bundles** than h13/poly1 and **2.2× higher max h⁰**. This is the strongest 3-generation Calabi-Yau manifold identified in the project.

**Representative simplest clean bundles**: L = O(±e0), with D³=0 and all higher cohomology vanishing — a single-divisor 3-generation model.

**Next**: Full pipeline on h17/poly63 (#2 priority candidate: T2=45, 198 clean, 5 K3 + 6 elliptic fibrations).

---

## 2026-02-22 18:36 — Merge fix: early T2 (20) + batch T2 (157) → 177 total

**Issue discovered**: The 20 polytopes screened in the early T2 run (15:15) were stored in `tier2_screen_results.csv` but never merged into `tier2_full_results.csv` when the 157-polytope batch ran. This caused 20 real results — including several top candidates — to be missing from the "full" CSV and all downstream documentation. Zero overlap between the two sets.

**Fix**: Merged both CSVs. Reran all 7 top early-T2 candidates to confirm reproducibility — all matched exactly. Backup of early results: `tier2_screen_results_early20_backup.csv`.

**New total**: 177 T2-screened polytopes.

---

## 2026-02-22 17:24 — T2 batch complete: 157/157, new leaders discovered

**Work done**: All 4 Codespace T2 pipes finished (33–41 min each). Pulled results locally, saved to `results/tier2_full_results.csv`. Updated CATALOGUE.md, README.md, FINDINGS.md.

**Key discoveries from the combined 177-polytope T2 results** (157 batch + 20 early):

| Polytope | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell | Note |
|----------|-----|------------|-------|--------|-----|-----|------|
| **h14/poly2** | 41 | **268** | 828 | 13 | 3 | 1 | Most clean bundles. Lowest h¹¹ among top candidates. |
| **h16/poly11** | 41 | **255** | 840 | 13 | 3 | 1 | #2 clean count. From early T2 batch. |
| **h17/poly96** | 39 | 227 | 930 | **65** | 2 | 1 | Highest max h⁰ ever recorded. |
| **h17/poly63** | 45 | **198** | 922 | 40 | 5 | 6 | Top T2=45 by clean count + best fibrations. |
| **h18/poly34** | 45 | 189 | 730 | 16 | 4 | 4 | From early T2 batch. |
| h16/poly74 | 45 | 24 | 80 | 4 | 5 | **10** | Most elliptic fibrations → F-theory target. |
| h17/poly45 | 45 | 61 | 404 | 16 | **6** | **8** | Most K3 fibrations. |

**Score distribution**: 30 at T2=45 (max), 80 at T2≥41, 177 total. The T2 scoring saturates — clean bundle count is the better discriminator.

**Decision**: h14/poly2 and h17/poly63 are the two priority candidates for full pipeline runs. h14/poly2 has the most clean bundles at lowest h¹¹; h17/poly63 is the top T2=45 scorer (198 clean, 5 K3 + 6 elliptic).

**Commits**: tier2_full_results.csv (merged), updated CATALOGUE/README/FINDINGS/BACKLOG

---

## 2026-02-22 17:16 — Repo restructured for open-source

**Work done**: Rewrote README.md, created CATALOGUE.md and CONTRIBUTING.md, updated FINDINGS.md and BACKLOG.md. Archived old README and FINDINGS. Pushed to GitHub.

**Strategic direction**: Open-source pipeline + catalogue. Build the sieve, record what passes, make it contributor-friendly. "Nothing big unless we find the big one."

**Commits**: 8dc9d63

---

## 2026-02-22 15:46 — Tier 1.5 sweep complete: 157 T2-worthy candidates

**Work done**: Ran `tier15_screen.py` on all 317 remaining Tier 1 candidates (excluding 20 already T2-screened). Phase A (fibrations) + Phase B (300-bundle capped probe). Total runtime: 26.8 min locally.

**Results**:
- 244/317 (77%) have clean h⁰=3 bundles in the 300-bundle probe
- **157/317 have ≥3 clean → T2-worthy** (promotion threshold)
- 1,584 total clean bundles found from probing alone
- ALL 317 have K3/elliptic fibrations (universal for χ=-6)

**Top T1.5 candidates** (not yet T2-screened):

| Rank | Polytope | T1.5 | Probe clean | Probe h⁰≥3 | max h⁰ | K3 | Ell |
|------|----------|------|-------------|-------------|--------|-----|-----|
| 1 | h18/poly32 [NF] | 40 | 21 | 89 | 30 | 4 | 4 |
| 2 | h17/poly53 [NF] | 40 | 20 | 74 | 10 | 3 | 3 |
| 3 | h18/poly31 [NF] | 40 | 18 | 90 | 20 | 4 | 4 |
| 4 | h15/poly61 [NF] | 40 | 15 | 40 | 4 | 3 | 3 |
| 5 | h16/poly53 [NF] | 40 | 14 | 70 | 12 | 5 | 6 |

**Early T2 validation** of top T1.5 candidates:
- h18/poly32: T2=45/55, **49 clean bundles** (21 found in 300-probe → full search found 49)
- h18/poly31: T2=45/55, **29 clean bundles**

**Next step**: Full T2 on all 157 T2-worthy candidates via 4-pipe parallel batch on Codespace (`run_t2_batch.sh`). Estimated ~40 min with 4 cores.

**Commits**: tier15_screen_results.csv, tier2_screen.py (--csv15/--offset/--batch), run_t2_batch.sh

---

## 2026-02-22 15:15 — Tier 2 deep screening: top 20 from Tier 1

**Work done**: Built `tier2_screen.py`. Four expensive checks per polytope: (1) exact h⁰=3 bundle count with full Koszul computation, (2) h³=h⁰(-D)=0 verification for all h⁰≥3 bundles, (3) D³ intersection statistics, (4) K3/elliptic fibration count from dual-polytope geometry.

**Validated**: Tested on h13-P1 benchmark — found 25 clean bundles, 3 K3, 3 elliptic, matching `pipeline_h13_P1.py` exactly. T2 score 45/55.

**Top results from early T2 run** (20 candidates from Tier 1, 29 min total):

| Rank | Polytope | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell |
|------|----------|-----|------------|-------|--------|-----|-----|
| 1 | h17/poly63 [NF] | 45 | **198** | 922 | 40 | 5 | 6 |
| 2 | h18/poly34 [NF] | 45 | **189** | 730 | 16 | 4 | 4 |
| 3 | h17/poly90 [NF] | 45 | **148** | 542 | 16 | 3 | 3 |
| 4 | h16/poly63 [NF] | 45 | 72 | 584 | 37 | 4 | 4 |
| 5 | h18/poly6 [NF] | 45 | 56 | 514 | 24 | 3 | 3 |
| 6 | h15/poly94 [NF] | 45 | 36 | 126 | 10 | 4 | 4 |
| 12 | h16/poly11 [NF] | 41 | **255** | 840 | 13 | 3 | 1 |
| — | h13-P1 (bench) | 45 | 25 | 76 | 6 | 3 | 3 |

> **Note (18:36)**: These 20 results were originally stored only in `tier2_screen_results.csv` and not merged into `tier2_full_results.csv` when the 157-polytope batch ran later. All 7 top entries above were rerun and confirmed exactly. Now merged into the full CSV (177 total).

**Scoring breakdown** (T2 out of 55): clean h⁰=3 count (0-15), h⁰≥3 abundance (0-10), K3 fibrations (0-6), elliptic fibrations (0-6), D³ diversity (0-5), simplicity bonus for h11_eff≤14 (0-3).

**Decision**: Remaining ~317 Tier 1 candidates need intermediate screening (Tier 1.5) before committing to full T2 analysis.

**Commits**: tier2_screen.py, results/tier2_screen_results.csv

---

## 2026-02-22 15:15 — Tier 1 screening: 337 candidates from scan v2 (partial)

**Work done**: Built `tier1_screen.py`. Fast screener (~1s/polytope) that reads scan log, then runs 3 cheap checks per polytope: (1) del Pezzo divisor classification, (2) Swiss cheese structure via Kähler cone tip + 10× hierarchy scaling, (3) GL(Z,4) toric symmetry order. Uses scan's max h⁰ rather than recomputing (fast path).

**Results** (337 candidates from ~60% complete scan v2):
- 190/337 (56%) have Swiss cheese structure
- 257/337 (76%) have ≥3 del Pezzo divisors
- 190/337 have Swiss + h⁰≥3 — immediate pipeline candidates
- Top candidate (pre-T2): h18/poly8 (score 41/55, 7 dP, Swiss cheese τ=12.9)

**Commits**: tier1_screen.py, results/tier1_screen_results.csv

---

## 2026-02-22 15:15 — Scan v2: non-favorable polytopes revealed (in progress)

**Work done**: Re-launched `scan_chi6_h0.py` with the B-11 fix (`h11_eff = len(div_basis)`). All 1025 polytopes now processable.

**Status at documentation time**: ~682/1025 lines, h11=21 processing, 414 HITs (h⁰≥3). Still running (PID 393136).

**Interim findings**: Hit rate ~61% (vs 42% in scan v1 which only saw favorable polytopes). Non-favorable polytopes dominate the landscape and contain the strongest candidates.

---

## 2026-02-22 15:15 — B-11: c2 mismatch fix + B-02: pipeline cleanup

**B-11 Root cause**: Non-favorable polytopes have `len(divisor_basis()) < h11`. CYTools' `second_chern_class(in_basis=True)` returns a vector sized to the toric divisor basis, not the full $h^{1,1}$. The scan was comparing `len(c2) != h11` and rejecting 705/1025 polytopes.

**Fix**: Use `h11_eff = len(div_basis)` as the working dimension throughout `scan_chi6_h0.py`. The HRR formula and Koszul lattice-point method already operate in the toric basis, so everything is consistent. Non-favorable polytopes are marked `[NF]` in output.

**Verification**: Tested on h11=14,16 polytopes that previously failed — all now process successfully. Example: h11=14 poly 2 (non-favorable, h11_eff=13) shows max h⁰=11.

**B-02**: Removed fabricated `proven_h0_3 = True` from `pipeline_40_152.py`. Replaced with `False` and a comment citing the Koszul disproof (dragon_slayer_40h/40i). Tier 2 score now correctly shows 5/6, total 19/20.

**Commits**: scan_chi6_h0.py, pipeline_40_152.py, BACKLOG.md

---

## 2026-02-22 10:28 — h13-P1 Full Pipeline: 18/20, New Best Candidate

**Work done**: Built pipeline_h13_P1.py. Full Stages 1-4 of FRAMEWORK.md on h11=13, polytope 1.

**Key results**:
- **18/20 score** — beats Polytope 40's corrected 10/20 on the same scorecard
- **25 clean bundles**: h⁰=3, h¹=h²=h³=0 (no higher cohomology at all)
- Swiss cheese structure confirmed: e12 has τ=10.0 at V=308352 (ratio 0.0022)
- 11,054 total χ=±3 bundles searched (max_nonzero=4, max_coeff=3)
- Max h⁰ = 6 (12 bundles)
- 76 bundles with h⁰≥3 total
- No nef bundles (universal across all χ=-6 polytopes)

**Methodology**: Kähler cone tip via `toric_kahler_cone().tip_of_stretched_cone(1.0)`, then 10× hierarchy scaling to find Swiss cheese. h³ verified by computing h⁰(-D) for all 25 exact bundles.

**Decision**: h13-P1 is now the primary candidate. Polytope 40 demoted.

## 2026-02-22 10:04 — Repo Cleanup + FRAMEWORK.md

**Work done**: 
- Created FRAMEWORK.md: 7-stage theoretical pipeline from CY geometry to phenomenology
- Created refs/refs.bib: 7 key references (KS, Braun et al, Anderson et al, LVS, etc.)
- Archived 12 scratch scripts to archive/
- Moved 13 result files to results/
- Committed at b17bc7d

---

## 2026-02-22 09:54 — B-01: χ=-6 landscape scan — h⁰=3 EXISTS

**Work done**: Built scan_chi6_h0.py. Scanned 1025 polytopes across h11=13..24 (all h21 = h11+3, giving χ=-6). Used verified Koszul pipeline.

**Key results**:
- 320 polytopes successfully analyzed (705 skipped due to c2 size mismatch — a CYTools `second_chern_class(in_basis=True)` inconsistency at higher h11)
- **136 polytopes (42%) have at least one line bundle with h⁰ ≥ 3**
- max h⁰ distribution: {1: 145, 2: 39, 3: 84, 4: 30, 5: 9, 6: 6, 7: 1, 9: 1, 10: 3, 13: 1, 14: 1}

**Headline**: h11=13, poly 0 has **12 line bundles** with h⁰ = χ = 3 and h³ = 0 (e.g., D = 2e₀ + e₆ + e₈). h11=13, poly 2 has **17 such bundles** (e.g., D = 2e₄ + 2e₅). Polytope 40 (h11=15) was the **exception**, not the rule — most χ=-6 CYs comfortably achieve h⁰ = 3.

**Issue encountered**: CYTools `second_chern_class(in_basis=True)` sometimes returns arrays shorter than h11 at higher h11 values. 705/1025 polytopes had to be skipped. Needs investigation — may be a divisor basis vs reduced basis issue.

**Decision**: h⁰=3 line bundles are abundant in the χ=-6 landscape. Polytope 40's max h⁰=2 is unusually low. The h11=13 polytopes are the cleanest candidates (smallest h11 with χ=-6, all 3 have h⁰ ≥ 4). Next: deep characterization of h11=13 poly 0 (the "new champion").

**Commits**: scan_chi6_h0.py

---

## 2026-02-22 07:43 — Verification complete, h⁰=2 confirmed

**Work done**: Built 7-test verification suite (dragon_slayer_40i.py). Discovered Bug #7 (GLSM linrels ≠ character translations). Confirmed h⁰=2 via 8 character translations. Cross-checked Koszul method against known quintic values (n=-3..7, all match). Updated MATH_SPEC.md.

**Issue encountered**: Test 1 (linear equivalence invariance) initially appeared to FAIL — lattice point counts of 2, 39, 225 for different representatives. Root cause: `glsm_linear_relations()` returns 5 vectors, but only 4 are character translations (dim M = 4). The 5th shifts the origin coordinate and changes the actual divisor class. This is NOT a bug in our computation — it's a subtlety of the GLSM formalism.

**Decision**: h⁰=2 is the definitive answer for all 119 χ=3 line bundles on Polytope 40. No further re-verification needed. Documented as Bug #7 in MATH_SPEC.md.

**Commits**: 72931ed (MATH_SPEC.md), 1a3c382 (verification + Bug #7)

**Next**: Choose between B-01 (scan other polytopes), B-02 (fix pipeline), or B-03 (higher-rank bundles).

---

## 2026-02-22 02:03 — MATH_SPEC.md created

**Work done**: Audited all 8 dragon_slayer scripts (40, 40b-40h) plus the original pipeline. Cataloged every formula, sign convention, index convention, CYTools API contract, and the 6 bugs encountered. Created MATH_SPEC.md as the single source of truth.

**Decision**: All future computation scripts must reference MATH_SPEC.md. Any new bug gets added to the registry immediately.

**Commit**: 72931ed

---

## 2026-02-22 01:54 — h⁰=3 definitively disproven

**Work done**: dragon_slayer_40h.py — Koszul exact sequence + lattice point counting + toric h¹ correction. Scanned all 119 χ=+3 bundles (1-4 divisors, coefficients ±1..3).

**Result**: max h⁰(X, D) = 2. h¹(V, D+K_V) = 0 for ALL bundles (Koszul formula is exact).

**Bugs fixed**: Bug #4 (off-by-one in lattice points, from 40g). Bug #5 (cohomCalg SR limit, from 40e/f).

**Impact**: Pipeline score confirmed at 19/20. The `proven_h0_3 = True` in pipeline_40_152.py is fabricated.

**Commit**: 5e3d727

---

## 2026-02-22 01:24 — Dragon Slayer: pipeline audit

**Work done**: Systematic audit of pipeline_40_152.py claims. Built dragon_slayer_40.py through 40g iteratively, each fixing bugs found in the previous version.

**Bug trail**:
1. Bug #1: `proven_h0_3 = True` hardcoded without computation
2. Bug #2: Intersection number coordinate mismatch (toric vs basis)
3. Bug #3: Mori cone pairing dimension mismatch (15-dim vs 20-dim)
4. Bug #6: Conflating |χ|/2=3 with h⁰(L)=3

**Key finding**: The "proven bundle" D=e3+e4+e10 has D³=14, χ=2.667 — not even an integer. The pipeline score should be 19/20.

**Decision**: Proceed to rigorously compute h⁰ for all χ=3 bundles (became 40c-40h).

**Commit**: a1b72e2

---

## 2026-02-22 01:14 — Ample Champion retraction

**Work done**: Rigorous testing of Z₃×Z₃ action on Ample Champion (h11=2, h21=29, χ=-54). Found pure g₁, g₂ have fixed curves on CY. Full quotient is singular.

**Salvaged**: Diagonal Z₃ acts freely → quotient has χ=-18, not χ=-6. Gets 9 generations, not 3.

**Decision**: Pivot to Polytope 40 (native χ=-6) as the cleaner 3-generation candidate.

**Commit**: dac8132

---

## 2026-02-22 00:29 — Polytope 40 pipeline run

**Work done**: Ran full 20-check pipeline on Polytope 40 (h11=15, h21=18, χ=-6). Scored 20/20.

**Issue**: Score was inflated — check 20 (`proven_h0_3`) was hardcoded True. All other 19 checks are genuine.

**Commit**: ccd69bf

---

## 2026-02-22 00:50 — Ample Champion analysis + fibrations

**Work done**: Analyzed Ample Champion quotient geometry. Computed Polytope 40 fibration structure (3 K3, 3 elliptic).

**Commit**: 58504ec

---

## 2026-02-21 23:01 — Landscape survey

**Work done**: Surveyed h11=2 polytopes for ample χ=3 bundles. Found they exist only at h11=2.

**Commit**: 64eb46b

---

## 2026-02-21 22:06 — Full scan

**Work done**: Scanned 1000 χ=-6 polytopes. Identified Polytope 40 and Polytope 152 as top candidates.

**Commit**: bc133fd

---

## Issue Register

Issues that surfaced during the project, for reference.

| # | Date | Issue | Resolution | Bug # |
|---|------|-------|------------|-------|
| I-01 | 02-22 01:24 | `proven_h0_3` hardcoded True | Disproven; max h⁰=2 | Bug #1 |
| I-02 | 02-22 01:24 | Intersection numbers: toric vs basis coords | Always use `in_basis=True` | Bug #2 |
| I-03 | 02-22 01:24 | Mori pairing: 15-dim D vs 20-dim C | Explicit index mapping via div_basis | Bug #3 |
| I-04 | 02-22 01:54 | Lattice point off-by-one (origin at index 0) | Iterate over ray_indices, not re-indexed array | Bug #4 |
| I-05 | 02-22 01:54 | cohomCalg: 97 SR gens > 64 limit | Check SR count before calling; use Koszul instead | Bug #5 |
| I-06 | 02-22 01:24 | \|χ\|/2=3 conflated with h⁰=3 | Different claims; document clearly | Bug #6 |
| I-07 | 02-22 07:43 | GLSM linrels include origin direction | Filter by origin_component==0 for char translations | Bug #7 |
| I-08 | 02-22 01:14 | Ample Champion Z₃×Z₃ has fixed curves | Full quotient singular; diagonal Z₃ acts freely | — |
| I-09 | 02-22 00:50 | Ample Champion misidentified as P²×P² | Different toric variety; det-3 lattice transform | — |
| I-10 | 02-24 | pipeline_v2 upsert clobbers old metrics | MONOTONIC_MAX on upsert; 1,173 values restored | — |
| I-11 | 02-26 | CYTools `fetch_polytopes()` hidden limit=1000 | Added `--limit N` CLI arg (v5.1) | — |
| I-12 | 02-26 | yukawa_rank fallback: 0 is falsy in `or` | Explicit `is None` check (v5) | — |
| I-13 | 02-26 | MONOTONIC_MAX score drift: sm_score overwrites | Post-upsert rescore from merged DB row (v5.2) | — |

---

## 2026-02-23 — B-26: GL12/D₆ Mirror Map, ODE Factorization & j-Invariant

**Commit**: (pending)

**Summary**: Extended the GL12/D₆ Picard-Fuchs analysis with three major results:

1. **ODE Factorization**: The 3rd-order PF ODE on the z₁-axis factors as θ·[₂F₁ ODE]:
   - θ · [θ² + 27t(θ+1/3)(θ+2/3)] = 0
   - Verified numerically (n=1..15): 3rd-order recurrence = n × 2nd-order recurrence
   - Consequence: z₁-axis is an **elliptic curve family** (cubic in ℙ²), not CY3
   - No independent double-log period → no CY3 prepotential on this slice

2. **Logarithmic Period & Mirror Map** (exact rational arithmetic, order 30):
   - h₁(n) = 3(H_{3n} − H_n) where H_n = harmonic number
   - q(t) = t − 15t² + 279t³ − 5729t⁴ + ...  (all integer coefficients ✓)
   - t(q) = q + 15q² + 171q³ + 1679q⁴ + 15054q⁵ + ...  (all integer ✓)
   - Wronskian: W(ω₀, ω₁) = 1/(t·(1+27t))

3. **j-Invariant** (Hesse pencil ↔ Klein j-function):
   - Hesse pencil: X³+Y³+Z³ = 3ψXYZ with ψ = −1/(3z₁^{1/3})
   - j(t) = (216t−1)³ / (t·(1+27t)³)
   - j(q) = −1/q + 744 − 196884q + 21493760q² − ...
   - **Absolute values match Klein j-function** (OEIS A000521) exactly!
   - 196884 = 196883 + 1 (Monster Moonshine coefficient) — deep cross-check

**Bug fixed**: Previous code/docs stated (θ+1)³ instead of the correct θ³ for the signed PF ODE.

**Files modified**: mori_pf.py (log periods, mirror map, j-invariant, ODE factorization), GL12_GEOMETRY.md (comprehensive update), BACKLOG.md

---

## 2026-02-23 — Z₂ Bundle Analysis: h16/P329 (B-22)

**Goal**: Test whether P329's Z₂ involution splits 3 generations as 2+1,
providing Yukawa texture zeros.

**Method**:
- Computed σ action on N-lattice (swap coords 2↔3)
- Determined ray permutation: 5 fixed, 7 swapped pairs
- Used GLSM linear relations to handle non-basis divisor mapping (e₁₁→D₁₅)
- Built full 14×14 sigma matrix S on Pic(X), verified S²=Id
- Enumerated 220 unique clean bundles, classified as Z₂-fixed (11) or paired (24)
- For each fixed bundle: computed section lattice points, traced σ* action

**Result**: All 11 Z₂-fixed bundles have Tr(σ*)=3 → 3+0 split (trivial).
Zero 2+1 texture-zero bundles. σ* = Id on H⁰ for all fixed bundles because
section monomials live entirely in the σ-fixed hyperplane (m₁=m₂).

**Key code issue fixed**: v1 script hung (brute force 7^14 loop). v2 used
cy_compute.find_chi3_bundles but failed on non-basis divisor mapping (e₁₁→toric 15).
v3 used GLSM charge matrix to properly express σ on Pic(X).

**Finding**: Finding 12 — P329 Z₂ trivial on generations.
**Files**: z2_bundle_analysis.py, get_glsm.py, results/z2_h16_P329_analysis.txt

---

## 2026-02-23 — AGLP Line Bundle Sum Search

**Goal**: Search for rank-5 line bundle sums V = L₁⊕···⊕L₅ with c₁=0, c₃=±6
(3 generations) on h14/P2 and h16/P329 — AGLP SU(5) GUT construction.

**Script**: aglp_bundle_sum.py

**Development**:
1. Wrote v1 with naive O(N⁴) 4-tuple search. Committed as 46c8e02.
2. First run on Codespace: 268 clean bundles on P2, C(268,4)=210M 4-tuples.
   SSH session killed before completion (would have taken hours).
3. Rewrote search with meet-in-the-middle 3+2 decomposition: build pair-sum
   dict (C(N,2) pairs), scan triples (C(N,3)) with O(1) dict lookup. ~65×
   speedup. Committed as 5b1d34b.
4. v2 completed in 5.3s on P2, 3.3s on P329.

**Results**:
- h14/P2: 14,608 χ=±3 → 268 clean → **0 five-sets with c₁=0** → 0 solutions
- h16/P329: 24,312 χ=±3 → 220 clean → **0 five-sets with c₁=0** → 0 solutions
- Relaxed run (max-coeff=5, max-nonzero=6) killed after 11min still enumerating
  bundles (~1.7B candidate vectors at h¹¹_eff=13)

**Diagnosis**: The h⁰=3 pre-filter removes ~98% of χ=±3 bundles, leaving too
sparse a subset for any 5 elements to cancel in a 13–14 dimensional lattice.
In proper AGLP, individual Lᵢ don't need h⁰=3 — only the sum V needs physical
properties. High h¹¹ makes brute-force AGLP intractable without the filter.

**Finding**: Finding 13 — AGLP fails at high Picard rank. Negative result.
**Files**: aglp_bundle_sum.py, results/aglp_h14_P2.txt, results/aglp_h16_P329.txt

---

## 2026-02-23 — Database & Pipeline v2

**Goal**: Build centralized SQLite database (cy_landscape.db) and a production
gap-aware scanning pipeline (pipeline_v2.py) to replace the scattered CSV/JSON
workflow.

**Key deliverables**:
- `db_utils.py` — SQLite layer (polytopes, fibrations, scan_log tables)
- `consolidate_db.py` — One-time ingestion of all old CSVs into the DB
- `pipeline_v2.py` — 4-tier gap-aware scanner (T0→T025→T1→T2+)
- `merge_receipts.py` — Ingest receipt JSONs from remote runs
- Receipt system for DB-free remote (Codespace) runs

**Commit**: bc12d8a (Finding 14: database + pipeline_v2)

---

## 2026-02-24 — h17 Full Scan on Codespace

**Goal**: Scan all 76,863 h¹¹=17 polytopes through pipeline_v2.

**Execution**: Ran on GitHub Codespace (16-core), completed in ~25 min.
- T0: 76,863 → T025: 4,010 → T1: 519 → T2+: 519
- 509 SM fibrations, 2,770 total fibrations
- Receipt: `v2_h17_20260225_033412_codespaces-8b9ac8.json`

**Commit**: 4d8e3fc

---

## 2026-02-24 — h13–h16 Rescan & Loser Analysis

**Goal**: Rescan h13–h16 with pipeline_v2 (`--gap-min 0`) for uniform methodology.
Profile "loser" polytopes (zero clean bundles).

**Results**:
- h13: 3 polytopes, 1 winner, 1 loser (P1: 946 bundles, 0 clean). 2s.
- h14: 22 polytopes, 6 winners, 1 loser (P9: 1,388 bundles, 0 clean). 11s.
- h15: 553 polytopes, **all 71 deep-analyzed have clean bundles**. +22 new winners. 6.4 min.
- h16: 5,180 polytopes, **all 154 deep-analyzed clean**. +3 new winners. 10.7 min.
- Old 7 h15 "losers" all killed at T025 (h⁰<5). h16/P1230 killed at T0 (eff=16>EFF_MAX).

**Commit**: 2b389a4

---

## 2026-02-24 — Conflict Audit & Threshold Fix

**Goal**: Investigate 216 data conflicts — polytopes where old scans found
n_clean>0 but pipeline_v2 screened them at T0 or T025.

**Root causes found**:

1. **Cat 1 — EFF_MAX=15 too low (59 polytopes)**: All favorable h¹¹=N polytopes
   have eff=N by definition. Old EFF_MAX=15 excluded all favorable h16+ polytopes.
   Old scans found up to 40 clean per polytope.

2. **Cat 2 — h⁰ clobber bug + H0_MIN=5 too high (152 polytopes)**:
   `compute_h0_koszul(min_h0=5)` returned 0 (not real h⁰) when h⁰(V,D)<5.
   T025 upsert then overwrote correct old values (3–4) with 0.
   Additionally, H0_MIN=5 filtered polytopes with true h⁰=3–4 that had confirmed
   clean bundles (e.g., h16/P52: 94 clean from 9,966 bundles).

3. **Cat 3 — AUT_MAX=3 too low (5 polytopes)**: All sym_order=4.
   h15/P18 had 19 clean, h16/P1 had 16 clean.

**Fixes applied**:
- EFF_MAX: 15 → 20 (covers all favorable polytopes through h20)
- H0_MIN_T025: 5 → 3 (stops filtering confirmed winners)
- AUT_MAX: 3 → 5 (includes sym_order=4 polytopes)
- Removed early-exit `return 0` from `compute_h0_koszul` (cy_compute.py)
- Restored 1,173 corrupted max_h0 values in DB from old CSV sources
- Result: 216 conflicts → 0

**Finding**: Finding 15 — pipeline threshold revision.
**Commit**: 7dce177
