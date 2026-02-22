# BACKLOG — CYTools Project

> Ordered by priority. Top = do next. Updated: 2026-02-23.

---

## NOW — Active Sprint

### B-10: Deep characterization of h11=13 "New Champions" ✅ DONE
- Moved to DONE table (D-14). Full pipeline on h13-P1: 18/20 score, 25 clean h⁰=3 bundles.

### B-02: Rebuild pipeline_40_152.py honestly ✅ DONE
- Moved to DONE table (D-15). `proven_h0_3 = False`, fabricated claims replaced with documented correction. Score now correctly prints 19/20.

### B-11: Fix c2 mismatch issue at higher h11 ✅ DONE
- Moved to DONE table (D-16). Root cause: non-favorable polytopes have `len(div_basis) < h11`. Fix: use `h11_eff = len(div_basis)` as working dimension. All 705 previously-skipped polytopes now processable.

---

## NEXT — Ready to Start

### B-13: Tier 1.5 intermediate screening ✅ DONE
- Moved to DONE. Built and ran `tier15_screen.py` on all 317 remaining candidates (27 min). Result: 157 T2-worthy (≥3 clean in 300-bundle probe). ALL have fibrations.

### B-16: Full T2 on 157 T1.5 survivors (batch)
- **Why**: 157 candidates survived T1.5 screening. Need full T2 deep analysis (exact bundle count, D³ stats, h³ verification).
- **What**: Run `./run_t2_batch.sh` on Codespace (4 parallel pipes, ~40 candidates each). Merge results with `./run_t2_batch.sh merge`.
- **Acceptance**: Complete T2 scores for all 157 candidates. Merged master CSV.
- **Estimate**: ~40 min on 4-core Codespace. Codespace-only.

### B-14: Full pipeline on h17/poly63 (new primary candidate)
- **Why**: Top T2 scorer (45/55, 198 clean bundles, 5 K3 + 6 elliptic, max h⁰=40). Needs full Stages 1-4 pipeline treatment like h13-P1 got.
- **What**: Build pipeline_h17_P63.py. Full divisor analysis, nefness check, cohomology table, net chirality deduction.
- **Acceptance**: Complete 20-check scorecard. Document in FINDINGS.md.
- **Estimate**: Medium.
- **Depends on**: None (data already available from T2 run).

### B-15: Complete scan v2 + re-run Tier 1 on full results
- **Why**: Scan v2 still running (~60% done). Final h11=21-24 polytopes may contain additional strong candidates.
- **What**: Wait for scan completion. Re-run `tier1_screen.py --top 500 --min-h0 3` on complete log. Update T1 CSV.
- **Acceptance**: Complete landscape map with all 1025 polytopes screened.
- **Estimate**: Small (mostly waiting).

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

### B-05: Repo hygiene — archive scratch scripts ✅ DONE
- Moved to DONE table (D-12). 12 scratch scripts → `archive/`, results → `results/`, refs skeleton → `refs/`.

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
| D-16 | B-11: Fix c2 mismatch (non-favorable polytopes) | 2026-02-22 | (this session) |
| D-15 | B-02: Rebuild pipeline_40_152.py honestly | 2026-02-22 | (this session) |
| D-14 | B-10: h13-P1 full pipeline (18/20, 25 clean bundles) | 2026-02-23 | (this session) |
| D-13 | B-12: Write FRAMEWORK.md (theoretical pipeline) | 2026-02-23 | (this session) |
| D-12 | B-05: Repo hygiene (archive, results/, refs/) | 2026-02-23 | (this session) |
| D-11 | B-01: Scan χ=-6 polytopes for h⁰=3 | 2026-02-22 | (this session) |
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
