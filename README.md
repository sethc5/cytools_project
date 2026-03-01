# 3-Generation Calabi-Yau Search

**Systematic scan of the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) for Calabi-Yau 3-folds compatible with 3-generation particle physics.**

The Standard Model has three generations of quarks and leptons. In string compactifications, this number comes from the topology of the extra-dimensional geometry — specifically, Calabi-Yau manifolds with Euler characteristic χ = −6 give |χ|/2 = 3 generations. There are **6.12 million** such polytopes in the Kreuzer-Skarke database of 473 million reflexive polytopes (spanning h¹¹ = 13–119). This project builds the pipeline to find and screen them.

> **Status**: Pipeline v6 · **1.38M polytopes** scanned (23.9% of 6.12M KS χ=−6 landscape) · **50,232 T2-scored** with 100-point SM composite (10 components) · Champion: **h26/P11670 (score 89)**, #2: h23/P37201 (87) · h13–h19 exhaustive · h20–h40 at 50K+ · Deployed on Hetzner (16-core i9, 128GB) · [Contributors welcome](CONTRIBUTING.md)

### What's Here

- **A 7-stage screening pipeline** — `v6/pipeline_v6.py` scans polytopes through tiered geometric checks (T0 → T1 → T2 → T3 deep analysis with triangulation stability). 100-point SM composite scoring with 10 physics-driven components.
- **A SQLite database** — `v6/cy_landscape_v6.db` (1.38M polytopes, 50,232 scored) with programmatic access via `v6/db_utils_v6.py`
- **Local KS index** — Pre-indexed χ=−6 polytope files for fast offline scanning (`--local-ks` flag)
- **Documented findings** — Champion cluster analysis, pipeline methodology, negative results ([FINDINGS.md](FINDINGS.md))
- **Documented pitfalls** — 9+ CYTools API bugs discovered and worked around ([MATH_SPEC.md](MATH_SPEC.md))

## The Landscape

There are **104 distinct Hodge number pairs** with χ = −6 in the KS database. The full χ = −6 landscape contains **6,122,441 polytopes** spanning h¹¹ = 13–119 (dying to zero above h¹¹ = 119). The bulk (94.7%) sits at h¹¹ = 13–40 where we focus our scan.

| h¹¹ range | KS total | Scanned | Coverage | Scored | Top score | Notes |
|-----------|----------|---------|----------|--------|-----------|-------|
| 13–16 | 5,758 | 5,758 | **100%** | 215 | 62 | Exhaustive |
| **17–19** | **327,833** | **327,833** | **100%** | **9,729** | **81** | **Exhaustive — h19/P438 (81)** |
| **20–21** | **257,148** | **100,000** | **38.9%** | **11,657** | **80** | High T0 pass rate (~26%) |
| **22–24** | **982,565** | **150,000** | **15.3%** | **18,410** | **87** | **Sweet spot — 3 of top 6** |
| **25–26** | **850,073** | **100,000** | **11.8%** | **6,868** | **89** | **#1: h26/P11670** |
| 27–28 | 1,078,976 | 100,000 | 9.3% | 2,636 | 84 | h27 favorable cluster |
| 29–30 | 832,645 | 100,000 | 12.0% | 471 | 80 | Diminishing returns |
| 31–40 | 1,360,792 | 500,000 | 36.7% | 246 | 75 | EFF_MAX=22 wall |
| 41–119 | 327,131 | 0 | 0% | — | — | Tail: 49K at h41 → 0 by h120 |
| **Grand total** | **6,122,441** | **1,383,592** | **23.9%** | **50,232** | **89** | |

**Database**: `v6/cy_landscape_v6.db` — 1.38M polytopes, 50,232 T2-scored. The h22–h26 sweet spot dominates the leaderboard (7 of top 10). See [FINDINGS.md](FINDINGS.md) for full per-h¹¹ coverage.

> **Note on scale**: The KS database has 473.8M reflexive 4-polytopes total; filtering to χ = −6 (3 generations) yields 6.12M. Each polytope admits many triangulations (→ distinct CY threefolds), each CY admits many vector bundles, and each (CY, bundle) pair admits many flux configurations. The famous "10^500 string vacua" estimate counts the product of all these choices — we work at the polytope level, the top of this hierarchy.

## Current Results

### Screening Funnel (v6)

```
1,383,592 polytopes (h13–h40, v6 pipeline)
  └─ h13–h19: 333,591 exhaustive (100% coverage)
  └─ h20–h40: 1,050,001 (50K per level + T2 backlog sweep)
      └─ 50,232 T2-scored ──────────────── 3.6%
          └─ 26 scoring ≥80 ──────────────── 0.05%
              └─ 4 scoring ≥85 ───────────── elite tier
```

### Top Candidates (v6, 100-point SM composite)

| Rank | ID | Score | Yukawa hier | Clean | Vol hier | Gap | Fibers |
|------|----|-------|-------------|-------|----------|-----|--------|
| 1 | **h26/P11670** | **89** | 2,389 | 22 | 18,493 | 4 | 4 K3 + 4 ell |
| 2 | **h23/P37201** | **87** | 1,598 | 26 | 2,303 | 2 | 3 K3 + 1 ell |
| 3 | h24/P45873 | **85** | 1,221 | 22 | 1,432 | 3 | 3 K3 + 1 ell |
| 4 | h25/P46481 | **85** | 4,893 | 22 | 3,024 | 4 | 3 K3 + 3 ell |
| 5 | h27/P43 | **84** | 621 | 24 | 71,546 | 0 | — |
| 6 | h24/P868 | **83** | 1,219 | 24 | 6,373 | 2 | 2 K3 + 1 ell |
| 7 | h27/P240 | **82** | 576 | 24 | 21,343 | 0 | — |
| 8 | h27/P239 | **82** | 531 | 26 | 19,527 | 1 | — |
| 9 | h25/P7867 | **81** | 512 | 18 | 2,187 | 3 | — |
| 10 | h19/P438 | **81** | 49,282 | 56 | 602 | 3 | 6 K3 + 7 ell |

The h22–h26 sweet spot dominates: 7 of top 10, including the #1 champion. h27 contributes a distinct "favorable cluster" (gap=0, extreme volume hierarchies). h19/P438 has the highest raw Yukawa hierarchy (49,282) but falls short of the 50K threshold for maximum scoring. See [FINDINGS.md](FINDINGS.md) for the full top-20.

## Pipeline Architecture

### v6/pipeline_v6.py — Tiered Scanner (v6 scoring)

```
T0: Geometry + EFF_MAX filter (h11_eff ≤ 22, gap ≥ 2)
T1: Bundle screening with adaptive depth + wall-time limit (120s)
T2: 100-point SM composite scoring (10 components)
T3: Deep analysis — FRSTs, c₂/κ stability, fibration classification
```

Scoring components: yukawa_hierarchy (30), yukawa_rank (15), n_clean (10), volume_hierarchy (10), gap (10), swiss_cheese (5), fibrations (5), del_pezzo (5), rigid_divisors (5), d3_diversity (5).

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

- **Gap=0 is a dead end at high h¹¹ — don't reopen the gate.** Probe at h27 (500 polytopes, 2026-02-28): gap=0 runs 5.3× slower (h¹¹_eff=27 lattice vs h¹¹_eff=20–22 for gap≥6), 21% T1 pass rate (vs ~45%), and top score of 84 vs champion 89. The real constraint is `EFF_MAX=22` (h¹¹_eff), not `GAP_MIN=2` — these are equivalent at h27+ because gap=0 forces h¹¹_eff=h¹¹. At h13–14 (h¹¹_eff<15) gap=0 is fine; everywhere else it hits a compute wall. In unbiased early data (N=496): gap<2 hit rate 97.2% vs gap≥2 100%, yield 1.7× lower. See Finding 11 + circularity audit in [PROCESS_LOG.md](PROCESS_LOG.md).
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

# Scan 50K polytopes at h11=24 using local KS index (fast)
python v6/pipeline_v6.py --scan --h11 24 --limit 50000 --local-ks -w 14

# Scan the NEXT 50K (polytopes 50K-100K) using --offset
python v6/pipeline_v6.py --scan --h11 24 --offset 50000 --limit 50000 --local-ks -w 14

# Scan a range of h11 values
python v6/pipeline_v6.py --scan --h11 20 26 --limit 50000 --local-ks -w 14

# Clear T2 backlog (score all T1-passed polytopes)
python v6/pipeline_v6.py --scan --h11 24 --resume --top 99999 --local-ks -w 14

# Deep analysis: top N candidates with FRST stability
python v6/pipeline_v6.py --deep --top 20

# Rescore all existing T2 records (after scoring changes)
python v6/pipeline_v6.py --rescore
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The most valuable contributions right now:

1. **Deep scan h24/h26** — highest ROI levels (447K/489K total, only 11%/10% covered), richest score density
2. **Higher-rank bundles on top 10** — find a stable rank-4/5 bundle with χ = 3 on h26/P11670 or h23/P37201
3. **Triangulation stability** — FRST sampling on the new champion cluster
4. **Fibration + yukawa_rank** — run `--fiber` pass on top 25 (many have rank=0 = not computed)
5. **Push h19/P438 over 50K** — retriangulation to nudge yukawa_hierarchy from 49,282 past 50K threshold

## File Structure

```
# Active pipeline (v6)
v6/pipeline_v6.py    — Main pipeline: --scan, --deep, --rescore, --fiber
v6/cy_compute_v6.py  — Computational core (Koszul, Yukawa, Swiss cheese, etc.)
v6/db_utils_v6.py    — SQLite database layer (upsert, query, rescore)
v6/cy_landscape_v6.db — Active database (1.38M polytopes, 50K scored)
v6/SPEC.md           — v6 scoring specification
v6/CHANGELOG.md      — v6 change log

# KS index (local polytope files for --local-ks)
ks_index.py          — Indexer: extracts χ=−6 polytopes from raw KS files
ks_raw/chi6/         — Pre-indexed h11_NNN.txt files (one per h¹¹ level)

# Documentation
FRAMEWORK.md         — 7-stage theoretical pipeline map
MATH_SPEC.md         — Formulas, CYTools API contracts, bugs
FINDINGS.md          — Detailed results and champion cluster analysis
PROCESS_LOG.md       — Chronological investigation diary
BACKLOG.md           — Prioritized task list + sprint tracking
results/             — CSV + log outputs from all runs
archive/             — Audit trail (v2–v5, early scripts, superseded docs)
```

## References

- [Kreuzer-Skarke Database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) — 473,800,776 reflexive 4-polytopes
- [CYTools](https://cy.tools) — Demirtas, Long, McAllister, Stillman
- Anderson, Gray, Lukas, Palti (2012) — Systematic line bundle cohomology on CY3
- Braun, He, Ovrut, Pantev (2006) — Heterotic Standard Model template
- Balasubramanian, Berglund, Conlon, Quevedo (2005) — Large Volume Scenario

## License

MIT
