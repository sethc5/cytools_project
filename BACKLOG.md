# BACKLOG — CYTools Project

> Ordered by priority. Top = do next. Updated: 2026-02-22.

---

## NOW — Active Sprint

### B-01: Scan χ=-6 polytopes for h⁰=3 line bundles
- **Why**: Polytope 40 maxes at h⁰=2. Other χ=-6 polytopes may succeed.
- **What**: Loop over `fetch_polytopes` with various (h11, h21) giving χ=-6. For each, run the verified Koszul pipeline (from 40h) to find bundles with h⁰≥3.
- **Acceptance**: Table of polytopes with their max h⁰. Any h⁰=3 hit is a headline result.
- **Estimate**: Medium (few hours compute, script is already proven).
- **Depends on**: Nothing — pipeline is verified.

### B-02: Rebuild pipeline_40_152.py honestly
- **Why**: Current pipeline hardcodes `proven_h0_3 = True` (Bug #1). Score is 19/20, not 20/20. The file is misleading as-is.
- **What**: Rewrite the pipeline to use the verified Koszul method for the h⁰ check. Set `proven_h0_3 = False` and update the scorecard to 19/20. Remove fabricated claims.
- **Acceptance**: Pipeline runs, score = 19/20, no hardcoded results, all claims backed by computation.
- **Estimate**: Small (1-2 hours).

---

## NEXT — Ready to Start

### B-03: Higher-rank vector bundles on Polytope 40
- **Why**: Line bundles cap at h⁰=2. A rank-2 or rank-3 bundle might yield h¹(V)=3 via index theorem. This is the standard BSM construction.
- **What**: Construct monad or extension bundles on the toric ambient space, restrict to CY, compute chiral index. Check stability.
- **Acceptance**: Find at least one stable rank-n bundle with net chirality = 3.
- **Estimate**: Large (research + implementation).
- **Depends on**: MATH_SPEC § on vector bundle conventions (to be written).

### B-04: K3/elliptic fibration structure of Polytope 40
- **Why**: Fibration structure determines F-theory compactification and gauge group. Open question in MATH_SPEC §9.3.
- **What**: Analyze 2D and 3D reflexive subpolytopes. Identify base/fiber decomposition. Compute discriminant locus.
- **Acceptance**: Documented fibration structure with identified gauge groups.
- **Estimate**: Medium.

### B-05: Repo hygiene — archive scratch scripts
- **Why**: 12 untracked scratch files (check_*.py, ample_champion_hodge.py) clutter the repo. 36 total scripts with no organization.
- **What**: Move one-off exploration scripts to an `archive/` or `scratch/` directory. Add .gitignore for temporary outputs. Keep only canonical scripts tracked.
- **Acceptance**: Root directory contains only production scripts + docs. Scratch work archived or ignored.
- **Estimate**: Small (30 min).

---

## LATER — Backlog

### B-06: Systematic Ample Champion follow-up
- **Why**: The diagonal Z₃ quotient gives χ=-18 (9 generations), not χ=-6. The full Z₃×Z₃ quotient is singular. Could still be interesting if we resolve the orbifold.
- **What**: Compute resolved Hodge numbers for the Z₃×Z₃ orbifold. Check if resolution gives χ=-6.
- **Estimate**: Medium-Large.
- **Status**: Parked. Polytope 40 native χ=-6 is a cleaner path.

### B-07: Paper draft — Polytope 40 as 3-generation candidate
- **Why**: We have a rigorous, novel result: a native χ=-6 CY3 with 11 del Pezzo divisors, Swiss cheese structure, Z₂ symmetry, 119 χ=3 bundles, and a proven h⁰≤2 bound. This is publishable.
- **What**: Structure: (1) Construction, (2) Topological data, (3) Divisor classification, (4) Bundle analysis, (5) Moduli stabilization viability.
- **Depends on**: B-01 result (if another polytope has h⁰=3, that changes the narrative). B-03 result changes the story too.
- **Estimate**: Large.

### B-08: Expand Koszul pipeline to general h11
- **Why**: The Koszul+lattice-point method (40h) is proven on the quintic and Polytope 40. Packaging it as a reusable tool enables scanning the full KS database.
- **What**: Refactor `dragon_slayer_40h.py` into a library function. Handle arbitrary h11. Add cohomCalg fallback for small SR ideals.
- **Estimate**: Medium.

### B-09: Self-mirror polytope (h11=20, h21=20) deep analysis
- **Why**: Novel self-mirror CY with χ=0. Rich fibration structure (3 K3, 3 elliptic). Undocumented in recent literature.
- **What**: Full pipeline analysis. Check for freely-acting symmetries. Potential F-theory applications.
- **Estimate**: Medium.

---

## DONE — Completed

| ID | Item | Completed | Commit |
|----|------|-----------|--------|
| D-01 | Prove/disprove h⁰=3 on Polytope 40 | 2026-02-22 | 5e3d727 |
| D-02 | Create MATH_SPEC.md gold standard | 2026-02-22 | 72931ed |
| D-03 | Verify h⁰=2 (char translation + quintic) | 2026-02-22 | 1a3c382 |
| D-04 | Dragon Slayer: correct pipeline to 19/20 | 2026-02-21 | a1b72e2 |
| D-05 | Retract full Z₃×Z₃ freely-acting claim | 2026-02-21 | dac8132 |
| D-06 | Ample Champion quotient analysis | 2026-02-20 | 58504ec |
| D-07 | Polytope 40 fibration structure | 2026-02-20 | 58504ec |
| D-08 | Original pipeline run (20/20, now known wrong) | 2026-02-19 | ccd69bf |
| D-09 | Landscape survey (h11=2 ample bundles) | 2026-02-18 | 64eb46b |
| D-10 | Full 1000-polytope scan | 2026-02-17 | bc133fd |
