# 3-Generation Calabi-Yau Search

**Systematic scan of the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) for Calabi-Yau 3-folds compatible with 3-generation particle physics.**

The Standard Model has three generations of quarks and leptons. In string compactifications, this number comes from the topology of the extra-dimensional geometry — specifically, Calabi-Yau manifolds with Euler characteristic χ = −6 give |χ|/2 = 3 generations. There are potentially millions of such manifolds in the Kreuzer-Skarke database of 473 million reflexive polytopes. This project builds the pipeline to find and screen them.

> **Status**: ~112,000 polytopes scanned · h13–h16 **complete** · h17 **complete** (200 ranked) · h18 T1 batch running (Hetzner, ~8K/105K processed) · **13 findings** documented · GL=12/D₆ Picard-Fuchs study complete · [Contributors welcome](CONTRIBUTING.md)

### What's Here

- **A screening pipeline** — scans polytopes for the right topology, then filters through 3 tiers of increasingly expensive geometric checks (divisor structure → fibrations → full cohomology)
- **A catalogue of results** — what passed, what didn't, and why ([CATALOGUE.md](CATALOGUE.md)) — so nobody has to repeat the work
- **A Picard-Fuchs / Yukawa study** — deep geometry of the most symmetric χ = −6 polytope (GL=12, D₆ symmetry). Closed-form period formula, 26 D₆-invariant Yukawa couplings, GKZ system analysis. See [GL12_GEOMETRY.md](GL12_GEOMETRY.md).
- **Documented pitfalls** — 9 CYTools API bugs discovered and worked around ([MATH_SPEC.md](MATH_SPEC.md))

## The Landscape

There are **104 distinct Hodge number pairs** with χ = −6 in the KS database, spanning h¹¹ = 13 to 128. The number of polytopes per Hodge pair grows explosively:

| h¹¹ | Polytopes | Scanned | Coverage |
|-----|----------|---------|----------|
| 13 | 3 | 3 | 100% |
| 14 | 22 | 22 | 100% |
| 15 | 553 | **553** | **100%** |
| 16 | 5,180 | **5,180** | **100%** |
| 17 | 38,735 | **200 ranked** | T0.25 complete, top 200 deep-scanned |
| 18 | ~195,000 | 🔶 ~105,000 | T0.25 done; T1 batch running (Hetzner, 14 workers) |
| 19–24 | ~millions | 100 ea. | ~0% |
| 25–128 | huge | 0 | 0% |

**We have scanned ~112,000 polytopes out of potentially millions.** h¹¹ = 13–16 are fully covered. h¹¹ = 17 T0.25 complete with top 200 candidates ranked. h¹¹ = 18 T0.25 complete (~105K polytopes), T1 batch running on Hetzner (14 workers, ~8K processed). See [PROCESS_LOG.md](PROCESS_LOG.md).

## Current Results

### Screening Funnel

```
6,658 polytopes scanned (h11=13..24, h15+h16 complete)
  └─ 2,779+ have h⁰ ≥ 3 line bundles (~42%)
      └─ 374 pass Tier 1 (dP divisors + Swiss cheese + symmetry)
          └─ 338 pass Tier 1.5 (fibrations + 300-bundle probe, ≥3 clean)
              └─ 36 Tier 2 complete ✅ (full bundle search + h³ verification)
                  └─ 14 scored T2=45 (max), 30 scored T2≥41
```

### Top Candidates (by clean h⁰=3 bundle count)

| Polytope | Score | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 fib | Ell fib | Notes |
|----------|-------|------------|-------|--------|--------|---------|-------|
| **★ h14/poly2** [NF] | **26/26** | **320** | 828 | 13 | 3 | 3 | Heterotic champion |
| **★ h16/poly53** [NF] | 23/26 | **300** | 1100 | 16 | 5 | 10 | 2nd most clean, no Swiss cheese |
| **★ h16/poly11** [NF] | **26/26** | **298** | 840 | 13 | 3 | 3 | 5 dP divisors |
| **★ h17/poly96** [NF] | **25/26** | **252** | 930 | **65** | 2 | 1 | Highest max h⁰ |
| **★ h17/poly63** [NF] | **26/26** | **218** | 922 | 40 | 5 | 10 | Former F-theory champ |
| **★ h17/poly9** [NF] | **23/26** | **192** | 876 | 15 | 1 | 0 | |
| **★ h18/poly34** [NF] | **26/26** | **184** | 730 | 16 | 4 | 6 | 5 dP, h¹¹=18 |
| **★ h17/poly8** [NF] | **26/26** | **180** | 558 | 13 | 3 | 3 | τ=2208 |
| **★ h17/poly25** [NF] | **26/26** | **170** | 490 | 8 | **6** | **15** | **F-theory + triple-threat champ** |
| **★ h15/poly61** [NF] | **25/26** | **110** | 338 | 4 | 3 | 3 | **τ=14,300 (LVS champ)** |
| **★ h19/poly16** [NF] | 22/26 | 86 | 564 | 27 | 5 | 10 | h¹¹=19 |
| **★ h16/poly63** [NF] | **26/26** | 78 | 584 | 37 | 4 | 6 | τ=836, triple-threat |
| h13/poly1 (bench) | 18/20 | 25 | 76 | 6 | 3 | 3 | Benchmark |

★ = Full pipeline complete (Stages 1–4 + scorecard). [NF] = non-favorable.

**h17/poly25** is the new F-theory champion: **15 elliptic fibrations** (record) + 6 K3 fibrations + Swiss cheese τ=56. The only candidate that excels at heterotic, F-theory, AND LVS simultaneously — a "triple-threat."

**h15/poly61** has the best Large Volume Scenario hierarchy: Swiss cheese τ = 14,300 (6.5× runner-up h17/poly8 at τ = 2,208).

Full results in [results/](results/). All top candidates are **non-favorable** polytopes — these were invisible until we fixed [Bug B-11](PROCESS_LOG.md).

## Pipeline Stages

| Stage | Description | Status |
|-------|-------------|--------|
| 1. CY Geometry | Enumerate χ = −6 polytopes, triangulate | ✅ Done |
| 2. Divisor Analysis | Classify divisors, Swiss cheese, intersection numbers | ✅ Done |
| 3. Line Bundle Cohomology | h⁰ via Koszul, scan for h⁰ ≥ 3 | ✅ Done |
| 4. Net Chirality | h¹ − h², Serre duality cross-check | ✅ Done |
| 5. Vector Bundles (rank 4/5) | Monad construction, stability, chiral spectrum | 🔶 `rank_n_bundles.py` built |
| 6. Moduli Stabilization | LVS/KKLT, flux superpotential | 🔶 Swiss cheese + PF periods |
| 7. Phenomenology | Yukawas, proton decay, gauge unification | 🔶 D₆-invariant Yukawas computed |

Stage 5 has initial results: `rank_n_bundles.py` finds SU(4) and SU(5) direct sums and monads with |χ|=3, with Hoppe stability checks. Stage 7 now includes D₆-invariant Yukawa couplings for the GL=12 polytope (see [GL12_GEOMETRY.md](GL12_GEOMETRY.md)). See [FRAMEWORK.md](FRAMEWORK.md) for the full theoretical map.

## Key Negative Results

These save you time. Don't re-check them:

- **No nef h⁰=3 bundles exist** on any scanned χ = −6 polytope. Kodaira vanishing never applies.
- **All χ = −6 polytopes have K3 + elliptic fibrations.** This is universal, not selective — don't use it as a discriminator.
- **Polytope 40 (h11=15) has max h⁰ = 2.** Definitively proven via Koszul + lattice point counting. 7-script audit trail. Don't try to find h⁰ = 3 on this specific polytope.
- **Ample Champion Z₃×Z₃ quotient is singular.** Pure g₁, g₂ have fixed curves on the CY hypersurface. Diagonal Z₃ gives χ = −18 (9 generations), not −6.
- **705/1025 polytopes were invisible** in scan v1 due to a CYTools `second_chern_class` bug for non-favorable polytopes. Fixed. But the strongest candidates are all non-favorable.
- **cohomCalg fails** when the SR ideal has >64 generators. Most high-h¹¹ polytopes hit this. Our Koszul pipeline bypasses it.
- **Z₂ acts trivially on generations** (Finding 12). On h16/P329, the Z₂ automorphism (coord swap) fixes 11/220 clean bundles, but acts as the identity on H⁰(X,L) for all of them → 3+0 representation, no 2+1 texture zeros.
- **AGLP line bundle sums fail at high Picard rank** (Finding 13). Searched V=L₁⊕···⊕L₅ with c₁=0, c₃=±6 on h14/P2 (268 clean bundles) and h16/P329 (220 clean). Zero 5-element subsets sum to zero. The h⁰=3 pre-filter is too restrictive at h¹¹_eff≥13.

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

# Full pipeline on any candidate (~25-30s)
python pipeline.py --h11 14 --poly 2      # Heterotic champion
python pipeline.py --h11 17 --poly 63     # F-theory champion
python pipeline.py --h11 18 --poly 34     # Next candidate

# Screening pipeline (to find new candidates)
python scan_parallel.py --h11 15 16 --workers 4       # Parallel scan (4× faster)
python scan_chi6_h0.py                                # Serial scan (legacy)
python tier1_screen.py --log results/scan_h15.log      # Fast screen
python tier15_screen.py --csv results/tier1_screen_results.csv   # Intermediate
python tier2_screen.py --csv15 results/tier15_screen_results.csv # Deep
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
# Pipeline scripts
pipeline.py          — Full Stages 1–4 pipeline for any candidate (--h11, --poly)
cy_compute.py        — Shared computational core (vectorized lattice points, batch χ)
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
