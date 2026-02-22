# PROCESS LOG — CYTools Project

> Chronological record of investigations, decisions, and issues encountered.
> New entries go at the top. Reference BACKLOG.md items by ID.

---

## 2026-02-23 — h13-P1 Full Pipeline: 18/20, New Best Candidate

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

## 2026-02-23 — Repo Cleanup + FRAMEWORK.md

**Work done**: 
- Created FRAMEWORK.md: 7-stage theoretical pipeline from CY geometry to phenomenology
- Created refs/refs.bib: 7 key references (KS, Braun et al, Anderson et al, LVS, etc.)
- Archived 12 scratch scripts to archive/
- Moved 13 result files to results/
- Committed at b17bc7d

---

## 2026-02-22 — B-01: χ=-6 landscape scan — h⁰=3 EXISTS

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

## 2026-02-22 — Verification complete, h⁰=2 confirmed

**Work done**: Built 7-test verification suite (dragon_slayer_40i.py). Discovered Bug #7 (GLSM linrels ≠ character translations). Confirmed h⁰=2 via 8 character translations. Cross-checked Koszul method against known quintic values (n=-3..7, all match). Updated MATH_SPEC.md.

**Issue encountered**: Test 1 (linear equivalence invariance) initially appeared to FAIL — lattice point counts of 2, 39, 225 for different representatives. Root cause: `glsm_linear_relations()` returns 5 vectors, but only 4 are character translations (dim M = 4). The 5th shifts the origin coordinate and changes the actual divisor class. This is NOT a bug in our computation — it's a subtlety of the GLSM formalism.

**Decision**: h⁰=2 is the definitive answer for all 119 χ=3 line bundles on Polytope 40. No further re-verification needed. Documented as Bug #7 in MATH_SPEC.md.

**Commits**: 72931ed (MATH_SPEC.md), 1a3c382 (verification + Bug #7)

**Next**: Choose between B-01 (scan other polytopes), B-02 (fix pipeline), or B-03 (higher-rank bundles).

---

## 2026-02-22 — MATH_SPEC.md created

**Work done**: Audited all 8 dragon_slayer scripts (40, 40b-40h) plus the original pipeline. Cataloged every formula, sign convention, index convention, CYTools API contract, and the 6 bugs encountered. Created MATH_SPEC.md as the single source of truth.

**Decision**: All future computation scripts must reference MATH_SPEC.md. Any new bug gets added to the registry immediately.

**Commit**: 72931ed

---

## 2026-02-22 — h⁰=3 definitively disproven

**Work done**: dragon_slayer_40h.py — Koszul exact sequence + lattice point counting + toric h¹ correction. Scanned all 119 χ=+3 bundles (1-4 divisors, coefficients ±1..3).

**Result**: max h⁰(X, D) = 2. h¹(V, D+K_V) = 0 for ALL bundles (Koszul formula is exact).

**Bugs fixed**: Bug #4 (off-by-one in lattice points, from 40g). Bug #5 (cohomCalg SR limit, from 40e/f).

**Impact**: Pipeline score confirmed at 19/20. The `proven_h0_3 = True` in pipeline_40_152.py is fabricated.

**Commit**: 5e3d727

---

## 2026-02-21 — Dragon Slayer: pipeline audit

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

## 2026-02-21 — Ample Champion retraction

**Work done**: Rigorous testing of Z₃×Z₃ action on Ample Champion (h11=2, h21=29, χ=-54). Found pure g₁, g₂ have fixed curves on CY. Full quotient is singular.

**Salvaged**: Diagonal Z₃ acts freely → quotient has χ=-18, not χ=-6. Gets 9 generations, not 3.

**Decision**: Pivot to Polytope 40 (native χ=-6) as the cleaner 3-generation candidate.

**Commit**: dac8132

---

## 2026-02-20 — Polytope 40 pipeline run

**Work done**: Ran full 20-check pipeline on Polytope 40 (h11=15, h21=18, χ=-6). Scored 20/20.

**Issue**: Score was inflated — check 20 (`proven_h0_3`) was hardcoded True. All other 19 checks are genuine.

**Commit**: ccd69bf

---

## 2026-02-20 — Ample Champion analysis + fibrations

**Work done**: Analyzed Ample Champion quotient geometry. Computed Polytope 40 fibration structure (3 K3, 3 elliptic).

**Commit**: 58504ec

---

## 2026-02-18 — Landscape survey

**Work done**: Surveyed h11=2 polytopes for ample χ=3 bundles. Found they exist only at h11=2.

**Commit**: 64eb46b

---

## 2026-02-17 — Full scan

**Work done**: Scanned 1000 χ=-6 polytopes. Identified Polytope 40 and Polytope 152 as top candidates.

**Commit**: bc133fd

---

## Issue Register

Issues that surfaced during the project, for reference.

| # | Date | Issue | Resolution | Bug # |
|---|------|-------|------------|-------|
| I-01 | 02-21 | `proven_h0_3` hardcoded True | Disproven; max h⁰=2 | Bug #1 |
| I-02 | 02-21 | Intersection numbers: toric vs basis coords | Always use `in_basis=True` | Bug #2 |
| I-03 | 02-21 | Mori pairing: 15-dim D vs 20-dim C | Explicit index mapping via div_basis | Bug #3 |
| I-04 | 02-22 | Lattice point off-by-one (origin at index 0) | Iterate over ray_indices, not re-indexed array | Bug #4 |
| I-05 | 02-22 | cohomCalg: 97 SR gens > 64 limit | Check SR count before calling; use Koszul instead | Bug #5 |
| I-06 | 02-21 | \|χ\|/2=3 conflated with h⁰=3 | Different claims; document clearly | Bug #6 |
| I-07 | 02-22 | GLSM linrels include origin direction | Filter by origin_component==0 for char translations | Bug #7 |
| I-08 | 02-20 | Ample Champion Z₃×Z₃ has fixed curves | Full quotient singular; diagonal Z₃ acts freely | — |
| I-09 | 02-20 | Ample Champion misidentified as P²×P² | Different toric variety; det-3 lattice transform | — |
