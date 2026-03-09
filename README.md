# 3-Generation Calabi-Yau Search

**Systematic scan of the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) for Calabi-Yau 3-folds compatible with 3-generation particle physics.**

The Standard Model has three generations of quarks and leptons. In string compactifications, this number comes from the topology of the extra-dimensional geometry — specifically, Calabi-Yau manifolds with Euler characteristic χ = −6 give |χ|/2 = 3 generations. There are **6.12 million** such polytopes in the Kreuzer-Skarke database of 473 million reflexive polytopes (spanning h¹¹ = 13–119). This project builds the pipeline to find and screen them.

> **Status**: Pipeline v6 complete · **v7 in progress** (observable-first, non-perturbative) · **3.11M polytopes** scanned · **54,931 T2-scored** · **37 T4-verified** · Champion: **h26/P11670 (score 89)** · **Universal D3 tadpole obstruction** proven for perturbative SU(4/5) monads on all 5 priority entries (0/104,145 pass, Findings §30–33) · Deployed on Hetzner (i9-9900, 128GB) · [Contributors welcome](CONTRIBUTING.md)

### What's Here

- **A 7-stage screening pipeline** — `v6/pipeline_v6.py` scans polytopes through tiered geometric checks (T0 → T1 → T2 → T3 deep analysis with triangulation stability). 100-point SM composite scoring with 10 physics-driven components.
- **A SQLite database** — `v6/cy_landscape_v6.db` (2.94M polytopes, 37,937 fully T2-scored after audit) with programmatic access via `v6/db_utils_v6.py`
- **Local KS index** — Pre-indexed χ=−6 polytope files for fast offline scanning (`--local-ks` flag)
- **Documented findings** — Champion cluster analysis, pipeline methodology, negative results ([FINDINGS.md](FINDINGS.md))
- **Documented pitfalls** — 9+ CYTools API bugs discovered and worked around ([MATH_SPEC.md](MATH_SPEC.md))

## The Landscape

There are **104 distinct Hodge number pairs** with χ = −6 in the KS database. The full χ = −6 landscape contains **6,122,441 polytopes** spanning h¹¹ = 13–119 (dying to zero above h¹¹ = 119). The bulk (94.7%) sits at h¹¹ = 13–40 where we focus our scan.

| h¹¹ range | KS total | Scanned | Coverage | T2-scored | Top score | Notes |
|-----------|----------|---------|----------|-----------|-----------|-------|
| 13–16 | 5,758 | 5,758 | **100%** | 215 | 62 | Exhaustive |
| **17–19** | **327,833** | **327,833** | **100%** | **9,729** | **81** | **Exhaustive — h19/P438 (81)** |
| **20–21** | **257,148** | **258,000** | **~100%** | **620** | **74** | Exhaustive — T0 wall reached |
| **22–24** | **982,565** | **978,000** | **~99.5%** | **25,800** | **85** | **Nearly exhaustive — h24 fully exhausted (438K/438K)** |
| **25–26** | **836,598** | **840,000** | **~100%** | **14,500** | **89** | **#1: h26/P11670; h25+h26 fully exhausted; T0 wall confirmed** |
| 27 | 637,470 | 100,000 | 15.7% | 2,200 | **87** | h27: max=87; T0 wall beyond 100K |
| 28 | 441,506 | 100,000 | 22.7% | 1,200 | **85** | h28: max=85 |
| 29–32 | ~650,000 | 200,000 | ~31% | 600 | <70 | **Barren** — no scores >70 found |
| 33–40 | ~700,000 | 400,000 | ~57% | 67 | <65 | EFF_MAX=22 wall dominant |
| 41–119 | 327,131 | 0 | 0% | — | — | Tail: 49K at h41 → 0 by h120 |
| **Grand total** | **6,122,441** | **3,113,640** | **~50.9%** | **54,931** | **89** | T3=965 · T4=37 · Fibs=2,463 |

**Database**: `v6/cy_landscape_v6.db` (827MB) — 3.11M polytopes, **54,931 fully T2-scored**, **965 T3-deep**, **37 T4-verified**, **2,463 fibrations**. h24 and h25 are **fully exhausted**; h26 fully exhausted confirming the sweet spot. Back halves of h24/h25 returned 0 T0 passes. h27–h28 capped at 100K each (T0 wall confirmed). h29–h32 barren (<70 max). See [FINDINGS.md §22](FINDINGS.md) for the ext-scan post-mortem and [FINDINGS.md §28](FINDINGS.md) for the champion deep-physics plan.

> **Note on scale**: The KS database has 473.8M reflexive 4-polytopes total; filtering to χ = −6 (3 generations) yields 6.12M. Each polytope admits many triangulations (→ distinct CY threefolds), each CY admits many vector bundles, and each (CY, bundle) pair admits many flux configurations. The famous "10^500 string vacua" estimate counts the product of all these choices — we work at the polytope level, the top of this hierarchy.

## Current Results

### Screening Funnel (v6)

```
3,113,640 polytopes (h13–h40, v6 pipeline)
  └─ h13–h26: exhaustive or near-exhaustive (T0 wall reached everywhere)
  └─ h27–h32: 100K–200K samples each (barren beyond h28)
      └─ 54,931 fully T2-scored ──────────── 1.76%
          └─ 965 T3-deep ──────────────────── 0.031%
              └─ 37 T4-verified ────────────── 0.0012%
                  └─ 2,463 fibrations catalogued
                      └─ 1 champion: h26/P11670 (score 89)
  T2 yield: ~149 scored per 1K T0-pass; T3 yield: 1.76% of T2
```

### Top Candidates (v6, 100-point SM composite)

| Rank | ID | Score | h¹¹ | Yukawa hier | Clean | chi | T-stage | Note |
|------|----|-------|-----|-------------|-------|-----|---------|------|
| 1 | **h26/P11670** | **89** | 26 | 2,389.6 | 22 | +6 | **T4** | champion; self-mirror; 3 fibrations |
| 2 | **h24/P45873** | **85** | 24 | 1,222 | 22 | +6 | T3 | |
| 3 | h25/P46481 | **85** | 25 | 4,893 | 22 | +6 | T3 | |
| 4 | h24/P868 | **83** | 24 | 1,220 | 24 | +6 | T3 | |
| 5 | h25/P7867 | **81** | 25 | 513 | 18 | +6 | T3 | |
| 6 | h27/P???  | **87** | 27 | — | — | — | T2 | h27 sweep; pending T3 |
| 7 | **h22/P682** | 80 | 22 | 1,464 | **84** | +6 | T3 | highest n_clean in ≥80 tier |

All 37 T4 entries verified (0 partial-score violations). 965 T3 entries deep-analyzed; 2,463 fibrations catalogued. See [FINDINGS.md §28](FINDINGS.md) for champion deep-physics plan.

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
| **5a. T3 Deep Analysis** | **FRST stability, fibration classification (2,463 fibs)** | **✅ Done (965 entries)** |
| **5b. T4 Verification** | **Triangulation stability, c₂/κ, score audit** | **✅ Done (37 entries)** |
| 6. Vector Bundles (rank 4/5) | SU(4)/SU(5) direct-sum + Hoppe stability on champion | 🔶 `champion_bundles.py` running |
| 7. Kodaira Resolution | Discriminant locus, fiber type classification, GUT gauge | 🔶 `champion_kodaira.py` running |
| 8. Moduli Stabilization | LVS/KKLT, flux superpotential | 🔶 Swiss cheese + volume hierarchy |
| 9. Phenomenology | Yukawas, proton decay, gauge unification | 🔶 D₆-invariant Yukawas computed |

## Key Negative Results

These save you time. Don't re-check them:

- **Gap=0 is a dead end at high h¹¹ — don't reopen the gate.** Probe at h27 (500 polytopes, 2026-02-28): gap=0 runs 5.3× slower (h¹¹_eff=27 lattice vs h¹¹_eff=20–22 for gap≥6), 21% T1 pass rate (vs ~45%), and top score of 84 vs champion 89. The real constraint is `EFF_MAX=22` (h¹¹_eff), not `GAP_MIN=2` — these are equivalent at h27+ because gap=0 forces h¹¹_eff=h¹¹. At h13–14 (h¹¹_eff<15) gap=0 is fine; everywhere else it hits a compute wall. In unbiased early data (N=496): gap<2 hit rate 97.2% vs gap≥2 100%, yield 1.7× lower. See Finding 11 + circularity audit in [PROCESS_LOG.md](PROCESS_LOG.md).
- **T0 wall at KS depth >100–150K per h11.** Confirmed by scanning 700K polytopes beyond existing coverage fronts: 0% T0 pass rate, zero scores above 23. The KS lattice-point ordering is a strong proxy for geometric viability — all productive polytopes are in the first ~100–150K. Current coverage fronts are the effective physical boundaries. See FINDINGS.md §17.
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

1. **Higher-rank bundles on top 10** — find a stable rank-4/5 bundle with χ = 3 on h26/P11670 or h23/P37201
2. **Triangulation stability** — FRST sampling on the new champion cluster
3. **Fibration + yukawa_rank** — run `--fiber` pass on top 25 (many have rank=0 = not computed)
4. **Push h19/P438 over 50K** — retriangulation to nudge yukawa_hierarchy from 49,282 past 50K threshold
5. **Extend h27–h30 coverage** — still at 50K each, only 9–12% coverage; h27 has a promising favorable cluster

> **Note**: Deeper KS scanning (offset >50K) shows diminishing returns — top candidates cluster in the first 50K of KS ordering per h¹¹ level. 550K new polytopes in the 100K batch yielded only 5 scoring ≥75 (best: 77). Depth is less productive than breadth at this stage.

## File Structure

```
# Active pipeline (v6)
v6/pipeline_v6.py       — Main pipeline: --scan, --deep, --rescore, --fiber
v6/cy_compute_v6.py     — Computational core (Koszul, Yukawa, Swiss cheese, etc.)
v6/db_utils_v6.py       — SQLite database layer (upsert, query, rescore)
v6/cy_landscape_v6.db   — Active database (827MB, 3.11M polytopes, 54,931 scored)
v6/monad_scan_top37.py  — Monad LP scanner (--rank, --k-max, --n-sample)
v6/ks_index.py          — Indexer: extracts χ=−6 polytopes from raw KS files
v6/CHANGELOG.md         — v6 change log

# v7 — Observable-first discovery track (in progress)
v7/README.md            — Architecture: Track A (non-perturbative) + Track B (observable scoring)

# Paper
paper/paper.tex         — 31pp draft (JHEP target)
paper/paper_outline.md  — Section outline and writing plan

# Documentation
FRAMEWORK.md            — 7-stage theoretical pipeline map
MATH_SPEC.md            — Formulas, CYTools API contracts, bugs
FINDINGS.md             — Detailed results, champion cluster, D3 obstruction
PROCESS_LOG.md          — Chronological investigation diary
BACKLOG.md              — Prioritized task list + sprint tracking
VERSIONS.md             — v2–v7 architecture history
results/                — CSV + log outputs from all runs
archive/                — Audit trail (v2–v5, early scripts, superseded docs)
```

## References

- [Kreuzer-Skarke Database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) — 473,800,776 reflexive 4-polytopes
- [CYTools](https://cy.tools) — Demirtas, Long, McAllister, Stillman
- Anderson, Gray, Lukas, Palti (2012) — Systematic line bundle cohomology on CY3
- Braun, He, Ovrut, Pantev (2006) — Heterotic Standard Model template
- Balasubramanian, Berglund, Conlon, Quevedo (2005) — Large Volume Scenario

## License

MIT
