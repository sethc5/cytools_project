# 3-Generation Calabi-Yau Search

**Systematic scan of the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) for Calabi-Yau 3-folds compatible with 3-generation particle physics.**

The Standard Model has three generations of quarks and leptons. In string compactifications, this number comes from the topology of the extra-dimensional geometry — specifically, Calabi-Yau manifolds with Euler characteristic χ = −6 give |χ|/2 = 3 generations. There are **6.12 million** such polytopes in the Kreuzer-Skarke database of 473 million reflexive polytopes (spanning h¹¹ = 13–119). This project builds the pipeline to find and screen them.

> **Status**: Pipeline v6 (yukawa-fix) · **3.09M polytopes** scanned (~50.5% of 5.8M active h13–h40 landscape) · **34,067 fully T2-scored** (0 partial-score violations; 2026-03-03 ext merge) · Champion: **h26/P11670 (score 89)**, #2: h24/P45873 (85), #4: h24/P868 (83) · h13–h21 exhaustive · h24/h25 fully exhausted · h22 at 50%, h26 at 49% · T0 wall confirmed in back halves of h24/h25 · Deployed on Hetzner (16-core i9, 128GB) · [Contributors welcome](CONTRIBUTING.md)

### What's Here

- **A 7-stage screening pipeline** — `v6/pipeline_v6.py` scans polytopes through tiered geometric checks (T0 → T1 → T2 → T3 deep analysis with triangulation stability). 100-point SM composite scoring with 10 physics-driven components.
- **A SQLite database** — `v6/cy_landscape_v6.db` (2.94M polytopes, 37,937 fully T2-scored after audit) with programmatic access via `v6/db_utils_v6.py`
- **Local KS index** — Pre-indexed χ=−6 polytope files for fast offline scanning (`--local-ks` flag)
- **Documented findings** — Champion cluster analysis, pipeline methodology, negative results ([FINDINGS.md](FINDINGS.md))
- **Documented pitfalls** — 9+ CYTools API bugs discovered and worked around ([MATH_SPEC.md](MATH_SPEC.md))

## The Landscape

There are **104 distinct Hodge number pairs** with χ = −6 in the KS database. The full χ = −6 landscape contains **6,122,441 polytopes** spanning h¹¹ = 13–119 (dying to zero above h¹¹ = 119). The bulk (94.7%) sits at h¹¹ = 13–40 where we focus our scan.

| h¹¹ range | KS total | Scanned | Coverage | Scored | Top score | Notes |
|-----------|----------|---------|----------|--------|-----------|-------|
| 13–16 | 5,758 | 5,758 | **100%** | 215 | 62 | Exhaustive |
| **17–19** | **327,833** | **327,833** | **100%** | **9,729** | **81** | **Exhaustive — h19/P438 (81)** |
| **20–21** | **257,148** | **258,000** | **~100%** | **620** | **74** | Exhaustive — T0 wall reached |
| **22–24** | **982,565** | **978,000** | **~99.5%** | **9,600** | **85** | **Nearly exhaustive — h24 fully exhausted (438K/438K)** |
| **25–26** | **836,598** | **624,018** | **~74.6%** | **5,500** | **89** | **#1: h26/P11670; h25 fully exhausted (424K/424K); T0 wall confirmed in back halves** |
| 27–28 | 1,078,976 | 200,031 | 18.5% | 1,200 | 79 | h27/h28 top=79 after fresh rescan |
| 29–30 | 832,645 | 200,000 | 24.0% | 250 | 75 | h29 top=75; h30 top=70 |
| 31–40 | 1,360,792 | 500,000 | 36.7% | 245 | 75 | EFF_MAX=22 wall |
| 41–119 | 327,131 | 0 | 0% | — | — | Tail: 49K at h41 → 0 by h120 |
| **Grand total** | **6,122,441** | **3,093,641** | **~50.5%** | **34,067** | **89** | |

**Database**: `v6/cy_landscape_v6.db` — 3.09M polytopes, **34,067 fully T2-scored** (0 partial-score violations; ext scan merged 2026-03-03). h24 and h25 are now **fully exhausted** through the KS universe — their back halves returned 0 T0 passes, confirming the T0 wall hypothesis. The h24–h26 sweet spot dominates (9 of 14 verified ≥80). See [FINDINGS.md §22](FINDINGS.md) for the ext-scan post-mortem.

> **Note on scale**: The KS database has 473.8M reflexive 4-polytopes total; filtering to χ = −6 (3 generations) yields 6.12M. Each polytope admits many triangulations (→ distinct CY threefolds), each CY admits many vector bundles, and each (CY, bundle) pair admits many flux configurations. The famous "10^500 string vacua" estimate counts the product of all these choices — we work at the polytope level, the top of this hierarchy.

## Current Results

### Screening Funnel (v6)

```
3,093,641 polytopes (h13–h40, v6 pipeline, 0 partial-score violations)
  └─ h13–h21: ~586K exhaustive (100% coverage, T0 wall reached)
  └─ h22–h30: ~2,507K (h24/h25 fully exhausted; h26 at 49%)
      └─ 34,067 fully T2-scored ───────────── 1.1%
          └─ 119 scoring ≥75 ─────────────── 0.35%
              └─ 14 scoring ≥80 ──────────── 0.040%
                  └─ 3 scoring ≥85 ─────────── elite tier
  Note: 246 unscored T2 rows remain (persistent Yukawa timeouts)
```

### Top Candidates (v6, 100-point SM composite)

| Rank | ID | Score | Yukawa hier | Clean | chi | Note |
|------|----|-------|-------------|-------|-----|------|
| 1 | **h26/P11670** | **89** | 2,390 | 22 | +6 | champion |
| 2 | **h24/P45873** | **85** | 1,222 | 22 | +6 | |
| 3 | h25/P46481 | **85** | 4,893 | 22 | +6 | |
| 4 | h24/P868 | **83** | 1,220 | 24 | +6 | |
| 5 | h25/P7867 | **81** | 513 | 18 | +6 | |
| 6 | **h22/P682** | 80 | 1,464 | **84** | +6 | highest n_clean in ≥80 tier |

All 14 entries at ≥80 verified clean (0 partial-score violations) after 2026-03-03 extension scan + merge. See [FINDINGS.md §22](FINDINGS.md) for ext-scan post-mortem and full invalidation history.

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
v6/pipeline_v6.py    — Main pipeline: --scan, --deep, --rescore, --fiber
v6/cy_compute_v6.py  — Computational core (Koszul, Yukawa, Swiss cheese, etc.)
v6/db_utils_v6.py    — SQLite database layer (upsert, query, rescore)
v6/cy_landscape_v6.db — Active database (1.93M polytopes, 60K scored)
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
