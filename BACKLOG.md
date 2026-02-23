# BACKLOG — χ = −6 CY Landscape Scanner

> Ordered by priority. Top = do next. Updated: 2026-02-23.
>
> **Project direction**: Open-source pipeline + catalogue. Build the sieve,
> record what passes and what doesn't, make it contributor-friendly.
> See [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## NOW — Active Sprint

### B-19: Expand scan — remove limit=100 cap at h¹¹ = 15–17
- **Why**: We've only scanned 100/553 at h15, 100/5180 at h16, 100/38735 at h17. The strongest candidates are all in this range.
- **What**: Run `scan_parallel.py` (multiprocessing, 4 workers) at h15–17. Update T1 → T1.5 → T2 pipeline on new hits.
- **Acceptance**: ≥500 polytopes scanned per h¹¹ value.
- **Status**:
  - ✅ h15: **553/553 complete** (333 hits, 60%). T1→T1.5→T2 done. h15/poly61 → full pipeline 25/26.
  - ✅ h16: **5,180/5,180 complete** (1,811 hits, 35%). T1→T1.5→T2 done. 20 new T2 entries.
  - ❌ h17: 38,735 polytopes, ~3.7 hrs. Deferred to Codespace.
- **Estimate**: h17 ~4hrs Codespace.

### B-23: Full pipeline on h15/poly61 (new #5 discovery) ✅ DONE
- **Why**: 103 clean h⁰=3 bundles — discovered in expanded h15 scan.
- **Result**: 25/26 score, 110 clean bundles, τ=14,300 (LVS champion). See FINDINGS.md.
- **Completed**: 2026-02-23.

---

## NEXT — Ready to Start

### B-20: Stage 5 — Higher-rank vector bundles
- **Why**: Line bundles only give U(1). Standard Model needs SU(3)×SU(2)×U(1), which requires rank 4 or 5 vector bundles. This is the critical gap.
- **What**: Implement monad/extension bundle construction on top candidates (h14/poly2 or h17/poly63). Check stability, compute chiral index.
- **Acceptance**: At least one stable rank-n bundle with net chirality = 3 on any candidate.
- **Estimate**: Large (research + implementation). External contributions especially welcome.

### B-21: F-theory discriminant locus classification
- **Why**: h17/poly63 has **10 elliptic fibrations** — the most of any analyzed candidate. Each is a potential F-theory compactification with non-abelian gauge symmetry.
- **What**: For h17/poly63 (10 elliptic fibs), classify singular fibers (Kodaira types), determine gauge algebra.
- **Acceptance**: Documented gauge groups for at least one fibration.
- **Estimate**: Medium-Large.

### B-22: Run full pipeline on remaining top candidates ✅ DONE
- All 7 top candidates analyzed. 5× score 26/26. See PROCESS_LOG 22:00 entry.

---

## LATER — Backlog

### B-07: Paper draft
- **Why**: Publishable as a methodology/survey paper even without SM discovery. The pipeline, catalogue of negative results, and CYTools gotchas are useful to the community.
- **Status**: Deferred until B-22 (more full pipeline runs) completes.

### B-06: Ample Champion orbifold resolution
- **Why**: The full Z₃×Z₃ quotient is singular. Could resolve and check if χ changes to −6.
- **What**: Compute resolved Hodge numbers for the Z₃×Z₃ orbifold.
- **Status**: Parked. Native χ = −6 candidates (h14/poly2, h17/poly63) are stronger paths.

### B-09: Self-mirror polytope (h11=20, h21=20) deep analysis
- **Why**: Novel self-mirror CY with χ = 0. Rich fibration structure. Undocumented.
- **What**: Full pipeline analysis. Check for freely-acting symmetries. F-theory applications.
- **Status**: Parked. Math curiosity, not a 3-generation candidate.

---

## DONE — Completed

| ID | Item | Completed |
|----|------|-----------|
| D-23 | B-23: Full pipeline h15/poly61 → 25/26, 110 clean, τ=14,300 (LVS champ) | 2026-02-23 |
| D-22b | B-19 partial: h16 full scan (5180/5180, 1811 hits) + T1→T2 | 2026-02-23 |
| D-22 | B-19 partial: h15 full scan (553/553, 333 hits) + scan_parallel.py | 2026-02-22 |
| D-21 | B-22: Full pipeline on all 7 top candidates (5× 26/26) | 2026-02-22 |\n| D-20 | B-18c: Generic `pipeline.py` (replaces per-candidate scripts) | 2026-02-22 |
| D-19 | B-18b: `cy_compute.py` shared core — 19× pipeline speedup | 2026-02-22 |
| D-18b | B-18: Full pipeline h17/poly63 → 26/26, 218 clean (F-theory champ) | 2026-02-22 |
| D-18a | B-18: Full pipeline h14/poly2 → 26/26, 320 clean (heterotic champ) | 2026-02-22 |
| D-18 | B-17: Repo restructuring (README, CATALOGUE, CONTRIBUTING) | 2026-02-24 |
| D-17 | B-13: Tier 1.5 screening (157 survivors) | 2026-02-23 |
| D-16 | B-11: Fix c2 mismatch (non-favorable polytopes) | 2026-02-22 |
| D-15 | B-02: Rebuild pipeline_40_152.py honestly | 2026-02-22 |
| D-14 | B-10: h13-P1 full pipeline (18/20, 25 clean bundles) | 2026-02-23 |
| D-13 | B-12: Write FRAMEWORK.md (theoretical pipeline) | 2026-02-23 |
| D-12 | B-05: Repo hygiene (archive, results/, refs/) | 2026-02-23 |
| D-11 | B-01: Scan χ=-6 polytopes for h⁰=3 (1025 total) | 2026-02-22 |
| D-10 | B-15: Complete scan v2 (634 hits / 1025 polytopes) | 2026-02-24 |
| D-01 | Prove h⁰ ≤ 2 on Polytope 40 (dragon slayer) | 2026-02-22 |
| D-02 | Create MATH_SPEC.md gold standard | 2026-02-22 |
| D-03 | Verify h⁰=2 (char translation + quintic benchmark) | 2026-02-22 |
| D-04 | Correct pipeline to 19/20 (retract fabricated claim) | 2026-02-21 |
| D-05 | Retract full Z₃×Z₃ freely-acting claim | 2026-02-21 |
| D-06 | Ample Champion quotient analysis | 2026-02-20 |
| D-07 | Polytope 40 fibration structure | 2026-02-20 |
