# 3-Generation Calabi-Yau Search

**Systematic scan of the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) for Calabi-Yau 3-folds compatible with 3-generation particle physics.**

The Standard Model has three generations of quarks and leptons. In string compactifications, this number comes from the topology of the extra-dimensional geometry — specifically, Calabi-Yau manifolds with Euler characteristic χ = −6 give |χ|/2 = 3 generations. There are potentially millions of such manifolds in the Kreuzer-Skarke database of 473 million reflexive polytopes. This project builds the pipeline to find and screen them.

> **Status**: ~75,000 polytopes catalogued · 1,284 deep-analyzed · h13–h17 **complete** · h18 partial (45 deep / ~105K T0) · **14 findings** documented · Receipt-based remote pipeline operational · [Contributors welcome](CONTRIBUTING.md)

### What's Here

- **A data-driven screening pipeline** — `pipeline_v2.py` scans polytopes through 4 tiers of increasingly expensive geometric checks (T0: h¹¹_eff → T0.25: probe → T1: deep bundles → T2: fibrations + gauge groups). Receipt system enables remote runs on Codespaces.
- **A SQLite database** — `cy_landscape.db` (74,823 polytopes, 4,387 fibrations) with programmatic access via `db_utils.py`
- **Documented findings** — 14 findings including the gap variable discovery, loser analysis, and circularity audit ([FINDINGS.md](FINDINGS.md))
- **Documented pitfalls** — 9 CYTools API bugs discovered and worked around ([MATH_SPEC.md](MATH_SPEC.md))

## The Landscape

There are **104 distinct Hodge number pairs** with χ = −6 in the KS database, spanning h¹¹ = 13 to 128. The number of polytopes per Hodge pair grows explosively:

| h¹¹ | Polytopes | In DB | Deep (T1+) | Coverage |
|-----|----------|-------|:----------:|:--------:|
| 13 | 3 | 3 | 1 | 100% |
| 14 | 24 | 24 | 9 | 100% |
| 15 | 553 | 553 | 467 | 100% |
| 16 | 5,180 | 5,180 | 216 | 100% |
| 17 | 38,735 | 38,735 | **519** | **100%** |
| 18 | ~105,000 | 30,293 | 45 | ~29% |
| 19 | ~244,000 | 35 | 27 | <0.1% |
| 20+ | millions | 0 | 0 | 0% |

**Database**: 74,823 polytopes, 1,284 deep-analyzed, 4,387 fibrations. h¹¹ = 13–17 have 100% T0 coverage. See [PROCESS_LOG.md](PROCESS_LOG.md).

## Current Results

### Screening Funnel (all h¹¹ combined)

```
74,823 polytopes catalogued
  └─ 1,284 deep-analyzed (T1+)
      └─ 1,275 have clean bundles (99.3%)
          └─ 924 at T2+ with fibration analysis
              └─ 898 with SM-compatible gauge groups (97.2%)
                  └─ 4,387 total fibrations catalogued
```

### Top Candidates (by clean h⁰=3 bundle count)

| # | Polytope | eff | gap | Clean | h⁰ | Score | SM | Fibs | Notes |
|---|----------|:---:|:---:|:-----:|:---:|:-----:|:--:|:----:|-------|
| 1 | **h18/P34** [NF] | 13 | 5 | **189** | 16 | 40/26 | — | — | All-time champion, needs T2 fiber |
| 2 | **h19/P7** [NF] | 13 | 6 | **114** | 6 | 27/26 | — | — | Highest gap in top 5 |
| 3 | **h16/P52** [NF] | 12 | 4 | **94** | 4 | 14/26 | — | — | |
| 4 | **h13/P0** [F] | 13 | 0 | **86** | 10 | 27/26 | — | — | Only favorable in top 10 |
| 5 | **h16/P40** [NF] | 13 | 3 | **69** | 7 | 23/26 | — | — | |
| 6 | **h19/P16** [NF] | 12 | 7 | **69** | 27 | 31/26 | — | — | Highest h⁰ in top 10 |
| 7 | **h18/P57** [NF] | 12 | 6 | **60** | 17 | 32/26 | — | — | |
| 8 | **h18/P68** [NF] | 16 | 2 | **59** | 10 | 20/26 | — | — | |
| 9 | **h17/P767** [NF] | 15 | 2 | **59** | 17 | 26/26 | SM | 10 | Best h17, SM confirmed |
| 10 | **h16/P55** [NF] | 12 | 4 | **57** | 7 | 13/26 | — | — | |

[NF] = non-favorable, [F] = favorable. Top 10 are 9/10 non-favorable, all gap ≥ 2 except h13/P0.

### The 9 Losers (T1+ with zero clean bundles)

Only 9 out of 1,284 deep-analyzed polytopes failed to produce any clean bundles:

| Polytope | eff | gap | h⁰ | Favorable |
|----------|:---:|:---:|:---:|:---------:|
| h14/P9 | 13 | 1 | 7 | NF |
| h15/P83 | 15 | 0 | 4 | F |
| h15/P340 | 14 | 1 | 4 | NF |
| h15/P424–P544 (5) | 15 | 0 | 4 | F |
| h16/P1230 | 16 | 0 | 7 | F |

**Pattern**: 7/9 favorable, 7/9 gap=0, 7/9 max_h⁰=4. Losers are marginal polytopes that barely qualified. Zero losses at gap ≥ 2 (N=170 unbiased). The loser rate drops toward zero at higher h¹¹.

## Pipeline Architecture

### pipeline_v2.py — Data-Driven 4-Tier Scanner

```
T0 (0.1s/poly): Compute h¹¹_eff, gap, |Aut|
  SKIP if eff ≥ 16 or |Aut| > 3
  SKIP if gap < 2 AND h⁰ < 5

T0.25 (0.5s): Bundle probe, h⁰ screening
  PROMOTE if h⁰ ≥ 5

T1 (3s): Full divisor analysis, complete bundle search
  Score by gap + eff, not Swiss cheese

T2 (30s): Fibrations, gauge groups, SM check
  Priority: gap DESC, n_chi3 DESC
```

Receipt system for remote runs: pipeline writes JSON to `receipts/`, `merge_receipts.py` ingests into local DB.

| Stage | Description | Status |
|-------|-------------|--------|
| 1. CY Geometry | Enumerate χ = −6 polytopes, triangulate | ✅ Done |
| 2. Divisor Analysis | Classify divisors, Swiss cheese, intersection numbers | ✅ Done |
| 3. Line Bundle Cohomology | h⁰ via Koszul, scan for h⁰ ≥ 3 | ✅ Done |
| 4. Net Chirality | h¹ − h², Serre duality cross-check | ✅ Done |
| 5. Vector Bundles (rank 4/5) | Monad construction, stability, chiral spectrum | 🔶 `rank_n_bundles.py` built |
| 6. Moduli Stabilization | LVS/KKLT, flux superpotential | 🔶 Swiss cheese + PF periods |
| 7. Phenomenology | Yukawas, proton decay, gauge unification | 🔶 D₆-invariant Yukawas computed |

## Key Negative Results

These save you time. Don't re-check them:

- **Gap is an efficiency knob, not a quality gate.** In unbiased data (N=496, excl pipeline_v2), gap<2 hits 97.2% vs gap≥2 at 100%. The 2.8pp difference is real but small. Gap predicts *yield* (avg 23.8 vs 13.7 clean) not pass/fail. Finding 14 originally overclaimed this — see circularity audit in [PROCESS_LOG.md](PROCESS_LOG.md).
- **Only 9 losers exist** out of 1,284 deep-analyzed. All are favorable + gap≤1 + borderline h⁰. The pipeline almost never wastes compute.
- **No nef h⁰=3 bundles exist** on any scanned χ = −6 polytope. Kodaira vanishing never applies.
- **All χ = −6 polytopes have K3 + elliptic fibrations.** Universal, not selective — don't use it as a discriminator.
- **Ample Champion Z₃×Z₃ quotient is singular.** Fixed curves on the CY hypersurface. Diagonal Z₃ gives χ = −18 (9 generations), not −6.
- **705/1025 polytopes were invisible** in scan v1 due to a CYTools `second_chern_class` bug for non-favorable polytopes. Fixed.
- **Z₂ acts trivially on generations** (Finding 12). On h16/P329, σ* = Id on H⁰(X,L) for all Z₂-fixed bundles → 3+0, no texture zeros.
- **AGLP line bundle sums fail at high Picard rank** (Finding 13). Zero 5-element subsets summing to zero among clean bundles at h¹¹_eff≥13.

See [CATALOGUE.md](CATALOGUE.md) for the full ruled-out list.

## Bugs & CYTools Gotchas

9 documented issues. If you're using CYTools, check [MATH_SPEC.md](MATH_SPEC.md) first:

| # | Issue | Impact |
|---|-------|--------|
| B-11 | `second_chern_class(in_basis=True)` wrong-size vector for non-favorable | **705/1025 polytopes invisible** |
| #5 | cohomCalg hard limit of 64 SR generators | Cannot use cohomCalg on complex polytopes |
| #7 | `glsm_linear_relations()` includes non-character translations | Misleading for linear equivalence |
| #2 | Intersection numbers: toric vs basis coordinates | Must always use `in_basis=True` |
| #3 | Mori cone: 15-dim divisor vs 20-dim Mori generators | Need explicit index mapping |

## Quick Start

```bash
git clone https://github.com/sethc5/cytools_project.git
cd cytools_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Data-driven pipeline (recommended)
python pipeline_v2.py --h11 17 -w 3 --top 20    # Scan all h17, show top 20
python pipeline_v2.py --h11 18 -w 3 --top 0     # Full h18 scan, no limit

# Merge receipts from remote runs
python merge_receipts.py --list                   # Show pending receipts
python merge_receipts.py                          # Merge all into cy_landscape.db

# Legacy pipeline on specific candidates
python pipeline.py --h11 14 --poly 2              # Heterotic champion
python pipeline.py --h11 17 --poly 767            # Best h17 (SM confirmed)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The most valuable contributions:

1. **Expand the scan** — run `scan_chi6_h0.py` with higher `limit` at h11 = 15..17 and PR the logs
2. **Screen new candidates** — run the Tier 1 → 1.5 → 2 pipeline on your scan output
3. **Stage 5 work** — monad bundle construction, stability checks, chiral index
4. **F-theory** — discriminant locus classification on elliptic-fibered candidates
5. **Bug fixes** — especially cohomology computation alternatives to cohomCalg

## File Structure

```
# Pipeline scripts (v2 — data-driven)
pipeline_v2.py       — Gap-aware 4-tier pipeline (T0→T0.25→T1→T2), optional DB, receipt output
merge_receipts.py    — Ingest JSON receipts from remote runs into cy_landscape.db
db_utils.py          — SQLite database layer (LandscapeDB class, upsert, query)
cy_compute.py        — Shared computational core (vectorized lattice points, batch χ)
fiber_analysis.py    — Fibration structure analysis + gauge group classification

# Legacy pipeline scripts
pipeline.py          — Original Stages 1–4 pipeline (--h11, --poly)
auto_scan.py         — Automated scan + ranking with checkpoint/resume
scan_chi6_h0.py      — Landscape scanner (Stages 1+3, serial)
scan_parallel.py     — Multiprocessing scanner (4× faster, resume support)
scan_fast.py         — Tier 0.25 fast pre-filter (early termination, 100% recall)
tier1_screen.py      — Fast screener: dP divisors, Swiss cheese, symmetry
tier15_screen.py     — Intermediate: fibrations + 300-bundle probe
tier2_screen.py      — Deep: exact bundle count, h³, D³, fibrations
verify_results.py    — Spot-check contributed T2 CSVs
batch_t1_h18.py      — Hetzner batch T1 runner for h18 (14 workers)
batch_t2_h18.py      — Hetzner batch T2 runner for h18

# Stage 5+ scripts
rank_n_bundles.py    — SU(4)/SU(5) bundle scanner (direct sum + monad, meet-in-middle)
aglp_bundle_sum.py   — AGLP rank-5 line bundle sum search (meet-in-the-middle)
z2_bundle_analysis.py — Z₂ automorphism action on bundle cohomology
aut_bundle_analysis.py — General automorphism-bundle analysis
fiber_analysis.py    — Fibration structure analysis
picard_fuchs.py      — GKZ periods, D₆-invariant Yukawa couplings, closed-form CT formula
get_glsm.py          — GLSM charge matrix helper
scan_automorphisms.py — Polytope automorphism scanner

# Geometry studies
GL12_GEOMETRY.md     — GL=12 / D₆ polytope: complete geometry, Yukawas, GKZ, periods

# Documentation
FRAMEWORK.md         — 7-stage theoretical pipeline map
MATH_SPEC.md         — Formulas, CYTools API contracts, 9 documented bugs
CATALOGUE.md         — What's been checked, what's ruled out
FINDINGS.md          — Detailed write-ups of key results (13 findings)
PROCESS_LOG.md       — Chronological investigation diary
HETZNER.md           — Dedicated server setup & reconnection guide
BACKLOG.md           — Prioritized task list + sprint tracking

# Output
results/             — CSV + log outputs from all runs

# Archive (audit trail — not needed for running the pipeline)
archive/dragon_slayer/  — h⁰ proof scripts for Polytope 40
archive/exploration/    — Early scanning & analysis scripts
archive/data/           — KS spec files, notebooks, images
archive/docs/           — Superseded documentation
```

## References

- [Kreuzer-Skarke Database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) — 473,800,776 reflexive 4-polytopes
- [CYTools](https://cy.tools) — Demirtas, Long, McAllister, Stillman
- Anderson, Gray, Lukas, Palti (2012) — Systematic line bundle cohomology on CY3
- Braun, He, Ovrut, Pantev (2006) — Heterotic Standard Model template
- Balasubramanian, Berglund, Conlon, Quevedo (2005) — Large Volume Scenario

## License

MIT
