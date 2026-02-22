# χ = −6 Calabi-Yau Landscape Scanner

An open computational search through the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) for Calabi-Yau 3-folds with properties compatible with 3-generation particle physics models.

**Status**: Active scan. Pipeline operational. Contributors welcome.

## What This Project Does

1. **Scans** the KS database for χ = −6 CY 3-folds (the geometry that gives |χ|/2 = 3 generations)
2. **Screens** candidates through a 3-tier pipeline: fast topology checks → fibration + bundle probes → full deep analysis
3. **Catalogues** what works, what doesn't, and why — so nobody repeats the work
4. **Documents** every bug, formula, and CYTools API gotcha encountered (see [MATH_SPEC.md](MATH_SPEC.md))

This is primarily a **pipeline and catalogue** project. We're building the sieve and recording what passes through it. If someone finds the Standard Model needle, great — but the reusable tooling and the "ruled out" list are the main deliverables.

## The Landscape

There are **104 distinct Hodge number pairs** with χ = −6 in the KS database, spanning h¹¹ = 13 to 128. The number of polytopes per Hodge pair grows explosively:

| h¹¹ | Polytopes | Scanned | Coverage |
|-----|----------|---------|----------|
| 13 | 3 | 3 | 100% |
| 14 | 22 | 22 | 100% |
| 15 | 553 | 100 | 18% |
| 16 | 5,180 | 100 | 1.9% |
| 17 | 38,735 | 100 | 0.26% |
| 18–24 | ~millions | 100 ea. | ~0% |
| 25–128 | huge | 0 | 0% |

**We have scanned ~1,025 polytopes out of potentially millions.** But h¹¹ = 13–17 is the physically most interesting range (fewer moduli, simpler stabilization), and that's where our best candidates cluster.

## Current Results

### Screening Funnel

```
1,025 polytopes scanned (h11=13..24, limit=100/h11)
  └─ 634 have h⁰ ≥ 3 line bundles (62%)
      └─ 337 pass Tier 1 (dP divisors + Swiss cheese + symmetry)
          └─ 157 pass Tier 1.5 (fibrations + 300-bundle probe, ≥3 clean)
              └─ 157 Tier 2 complete ✅ (full bundle search + h³ verification)
                  └─ 23 scored T2=45 (max), 66 scored T2≥41
```

### Top Candidates (by clean h⁰=3 bundle count)

| Polytope | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 fib | Ell fib |
|----------|-----|------------|-------|--------|--------|--------|
| **h14/poly2** [NF] | 41 | **268** | 828 | 13 | 3 | 1 |
| h17/poly96 [NF] | 39 | 227 | 930 | **65** | 2 | 1 |
| h17/poly63 [NF] | 45 | 198 | 922 | 40 | 5 | 6 |
| h18/poly34 [NF] | 45 | 189 | 730 | 16 | 4 | 4 |
| h17/poly8 [NF] | 45 | 159 | 558 | 13 | 3 | 3 |
| h13/poly1 (bench) | 45 | 25 | 76 | 6 | 3 | 3 |

Full results in [results/](results/). All top candidates are **non-favorable** polytopes — these were invisible until we fixed [Bug B-11](PROCESS_LOG.md).

## Pipeline Stages

| Stage | Description | Status |
|-------|-------------|--------|
| 1. CY Geometry | Enumerate χ = −6 polytopes, triangulate | ✅ Done |
| 2. Divisor Analysis | Classify divisors, Swiss cheese, intersection numbers | ✅ Done |
| 3. Line Bundle Cohomology | h⁰ via Koszul, scan for h⁰ ≥ 3 | ✅ Done |
| 4. Net Chirality | h¹ − h², Serre duality cross-check | 🔶 Partial |
| 5. Vector Bundles (rank 4/5) | Monad construction, stability, chiral spectrum | ❌ Not started |
| 6. Moduli Stabilization | LVS/KKLT, flux superpotential | 🔶 Swiss cheese only |
| 7. Phenomenology | Yukawas, proton decay, gauge unification | ❌ Not started |

Stage 5 (higher-rank bundles for non-abelian gauge groups) is the critical gap. Line bundles only give U(1). Contributions here would be especially valuable. See [FRAMEWORK.md](FRAMEWORK.md) for the full theoretical map.

## Key Negative Results

These save you time. Don't re-check them:

- **No nef h⁰=3 bundles exist** on any scanned χ = −6 polytope. Kodaira vanishing never applies.
- **All χ = −6 polytopes have K3 + elliptic fibrations.** This is universal, not selective — don't use it as a discriminator.
- **Polytope 40 (h11=15) has max h⁰ = 2.** Definitively proven via Koszul + lattice point counting. 7-script audit trail. Don't try to find h⁰ = 3 on this specific polytope.
- **Ample Champion Z₃×Z₃ quotient is singular.** Pure g₁, g₂ have fixed curves on the CY hypersurface. Diagonal Z₃ gives χ = −18 (9 generations), not −6.
- **705/1025 polytopes were invisible** in scan v1 due to a CYTools `second_chern_class` bug for non-favorable polytopes. Fixed. But the strongest candidates are all non-favorable.
- **cohomCalg fails** when the SR ideal has >64 generators. Most high-h¹¹ polytopes hit this. Our Koszul pipeline bypasses it.

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

# Screen a single polytope (deep analysis, ~30s)
python tier2_screen.py --h11 13 --poly 1

# Full pipeline run
python scan_chi6_h0.py                          # Stage 1+3: landscape scan
python tier1_screen.py                           # Fast screen
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
scan_chi6_h0.py      — Landscape scanner (Stages 1+3)
tier1_screen.py      — Fast screener: dP divisors, Swiss cheese, symmetry
tier15_screen.py     — Intermediate: fibrations + 300-bundle probe
tier2_screen.py      — Deep: exact bundle count, h³, D³, fibrations
pipeline_h13_P1.py   — Full Stages 1–4 benchmark pipeline
run_t2_batch.sh      — Parallel batch runner (4 pipes)

FRAMEWORK.md         — 7-stage theoretical pipeline map
MATH_SPEC.md         — Formulas, conventions, CYTools API contracts, bugs
CATALOGUE.md         — What's been checked and what's ruled out
FINDINGS.md          — Detailed write-ups of key results
PROCESS_LOG.md       — Chronological investigation diary
BACKLOG.md           — Task tracking

results/             — CSV + log outputs from all runs
archive/             — Old scripts (kept for audit trail)
refs/                — Bibliography
```

## References

- [Kreuzer-Skarke Database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) — 473,800,776 reflexive 4-polytopes
- [CYTools](https://cy.tools) — Demirtas, Long, McAllister, Stillman
- Anderson, Gray, Lukas, Palti (2012) — Systematic line bundle cohomology on CY3
- Braun, He, Ovrut, Pantev (2006) — Heterotic Standard Model template
- Balasubramanian, Berglund, Conlon, Quevedo (2005) — Large Volume Scenario

## License

MIT
