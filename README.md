# 3-Generation Calabi-Yau Search

**Systematic scan of the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) for Calabi-Yau 3-folds compatible with 3-generation particle physics.**

The Standard Model has three generations of quarks and leptons. In string compactifications, this number comes from the topology of the extra-dimensional geometry — specifically, Calabi-Yau manifolds with Euler characteristic χ = −6 give |χ|/2 = 3 generations. There are **6.12 million** such polytopes in the Kreuzer-Skarke database of 473 million reflexive polytopes (spanning h¹¹ = 13–119). This project builds the pipeline to find and screen them.

> **Status**: Pipeline v5.2 · **174K polytopes** scanned (2.8% of 6.12M KS χ=−6 landscape) · **2,012 T2-scored** with 100-point SM composite · Champion: h30/P289 (score 89) · h27 fibration-rich zone discovered · Deployed on Hetzner (16-core) · [Contributors welcome](CONTRIBUTING.md)

### What's Here

- **A 7-stage screening pipeline** — `v4/pipeline_v4.py` scans polytopes through tiered geometric checks (T0 → T1 → T2 → T3 deep analysis with triangulation stability). 100-point SM composite scoring with 12 components.
- **A SQLite database** — `v4/cy_landscape_v4.db` (174K polytopes, 2,012 scored) with programmatic access via `v4/db_utils_v4.py`
- **Documented findings** — Champion cluster analysis, pipeline methodology, negative results ([FINDINGS.md](FINDINGS.md))
- **Documented pitfalls** — 9+ CYTools API bugs discovered and worked around ([MATH_SPEC.md](MATH_SPEC.md))

## The Landscape

There are **104 distinct Hodge number pairs** with χ = −6 in the KS database. The full χ = −6 landscape contains **6,122,441 polytopes** spanning h¹¹ = 13–119 (dying to zero above h¹¹ = 119). The bulk (94.7%) sits at h¹¹ = 13–40 where we focus our scan.

| h¹¹ range | KS total | Scanned | Coverage | Top score | Notes |
|-----------|----------|---------|----------|-----------|-------|
| 13–16 | 5,758 | 5,758 | **100%** | — | Exhaustive (legacy v3 scoring) |
| 17–19 | 327,833 | 400 | 0.1% | — | Legacy scoring only |
| 20–26 | 2,736,315 | 7,000 | 0.3% | 81 | 257K–447K per level |
| **27** | **393,842** | **50,000** | **12.7%** | **86** | **Fibration-rich zone** |
| **28** | **354,495** | **50,000** | **14.1%** | **87** | h28 stability cluster |
| 29 | 322,535 | 1,000 | 0.3% | 76 | |
| **30** | **276,639** | **50,000** | **18.1%** | **89** | **#1: h30/P289** |
| 31–40 | 1,377,373 | 10,000 | 0.7% | 80 | Barren above h37 |
| 41–119 | 327,131 | 0 | 0% | — | Tail: 49K at h41 → 0 by h120 |
| **Grand total** | **6,122,441** | **174,158** | **2.8%** | **89** | |

**Database**: `v4/cy_landscape_v4.db` — 174K polytopes, 2,012 T2-scored. h27–h30 dominates (8 of top 10). See [CATALOGUE.md](CATALOGUE.md) for full per-h¹¹ coverage.

> **Note on scale**: The KS database has 473.8M reflexive 4-polytopes total; filtering to χ = −6 (3 generations) yields 6.12M. Each polytope admits many triangulations (→ distinct CY threefolds), each CY admits many vector bundles, and each (CY, bundle) pair admits many flux configurations. The famous "10^500 string vacua" estimate counts the product of all these choices — we work at the polytope level, the top of this hierarchy.

## Current Results

### Screening Funnel (v5.2)

```
168,000 polytopes (h11=20..40, v5.2 pipeline) + 6,158 legacy (h13–h19)
  └─ 5,344 pass T0 (geometry + EFF_MAX=22) ──── 3.2%
      └─ 2,012 pass T1 → T2 scored ────────────── 1.2%
          └─ 22 deep-analyzed (T3) ───────────── 20 FRSTs each
              ├─ Tier A (paper-ready): 3 (h28 stability cluster)
              └─ Tier C (score+fibrations): 7 (h27+h30, all SM+GUT)
```

### Top Candidates (v5.2, 100-point SM composite)

| Rank | ID | Score | Hierarchy | Clean | c₂ stab | SM+GUT | Tier |
|------|----|-------|-----------|-------|---------|--------|------|
| 1 | **h30/P289** | **89** | 34,318 | 12 | 0% | ✅ su(3)×su(17) | C |
| 2 | h28/P874 | **87** | 1,150 | 14 | 55% | — | A |
| 3 | h28/P186 | **87** | 1,147 | 14 | 35% | — | A |
| 4 | **h27/P22835** | **86** | 1,046 | 16 | 0% | ✅ 6 fibrations | C |
| 5 | **h27/P13954** | **85** | 695 | 16 | 25% | ✅ e7×su(12) | — |

**Tier A** = high score + stability. **Tier C** = high score + SM/GUT fibrations. All 6 h27 candidates in the top 10 have SM+GUT gauge groups — h27 is a **fibration-rich zone**. See [FINDINGS.md](FINDINGS.md) for the full top-10 and T3 analysis.

## Pipeline Architecture

### v4/pipeline_v4.py — Tiered Scanner (v5.2 scoring)

```
T0: Geometry + EFF_MAX filter (h11_eff ≤ 22)
T1: Full divisor analysis, bundle census, LVS check
T2: 100-point SM composite scoring (12 components)
T3: Deep analysis — 50 random FRSTs, c₂/κ stability
```

Scoring components: yukawa_hierarchy (27), yukawa_rank (15), clean_bundles (10), lvs_quality (10), lvs_binary (5), vol_hierarchy (5), mori_blowdown (5), tadpole_ok (5), d3_diversity (5), clean_depth (5), clean_rate (5), rank_sweet_spot (3).

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

# Scan a range of h11 values (v5.2 pipeline)
python v4/pipeline_v4.py --scan --h11 28 --limit 1000 -w 12

# Deep coverage scan (50K polytopes at one h11)
python v4/pipeline_v4.py --scan --h11 28 --limit 50000 -w 12

# Deep analysis: top N candidates, 50 random FRSTs each
python v4/pipeline_v4.py --deep --top 20

# Rescore all existing T2 records (after scoring formula changes)
python v4/pipeline_v4.py --rescore

# Query champions
python v4/review_champions.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The most valuable contributions right now:

1. **Stage 5: Higher-rank bundles on h28 champions** — find a stable rank-4/5 bundle with χ = 3
2. **Triangulation stability** — expand FRST sampling beyond 50 for Tier A candidates
3. **F-theory on h28** — Kodaira fiber classification on new champions
4. **Low-h¹¹ rescore** — ingest legacy h13–h19 polytopes into v4 DB and score under v5.2
5. **Bug fixes** — cohomology computation alternatives to cohomCalg

## File Structure

```
# Active pipeline (v5.2 scoring, v4 DB schema)
v4/pipeline_v4.py    — Main pipeline: --scan, --deep, --rescore
v4/cy_compute_v4.py  — Computational core (Koszul, Yukawa, LVS, etc.)
v4/db_utils_v4.py    — SQLite database layer (upsert, query, rescore)
v4/review_champions.py — Query and display top candidates
v4/cy_landscape_v4.db — Active database (70,000 polytopes, 1,787 scored)

# v5 scoring engine (imported by v4)
v5/pipeline_v5.py    — v5 scoring formulas (used by v4/pipeline_v4.py)
v5/cy_compute_v5.py  — Graded mori, rank_sweet_spot, tri_stability
v5/db_utils_v5.py    — v4 schema + tri columns (auto-migrated)

# Documentation
FRAMEWORK.md         — 7-stage theoretical pipeline map
MATH_SPEC.md         — Formulas, CYTools API contracts, bugs
CATALOGUE.md         — Coverage, funnel, leaderboard, ruled-out list
FINDINGS.md          — Detailed results and champion cluster analysis
PROCESS_LOG.md       — Chronological investigation diary
VERSIONS.md          — Pipeline version lineage (v1→v5.2)
BACKLOG.md           — Prioritized task list + sprint tracking
results/             — CSV + log outputs from all runs
archive/             — Audit trail (v2, v3, early scripts, superseded docs)
```

## References

- [Kreuzer-Skarke Database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) — 473,800,776 reflexive 4-polytopes
- [CYTools](https://cy.tools) — Demirtas, Long, McAllister, Stillman
- Anderson, Gray, Lukas, Palti (2012) — Systematic line bundle cohomology on CY3
- Braun, He, Ovrut, Pantev (2006) — Heterotic Standard Model template
- Balasubramanian, Berglund, Conlon, Quevedo (2005) — Large Volume Scenario

## License

MIT
