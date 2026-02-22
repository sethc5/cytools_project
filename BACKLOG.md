# BACKLOG — χ = −6 CY Landscape Scanner

> Ordered by priority. Top = do next. Updated: 2026-02-24.
>
> **Project direction**: Open-source pipeline + catalogue. Build the sieve,
> record what passes and what doesn't, make it contributor-friendly.
> See [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## NOW — Active Sprint

### B-17: Repo restructuring for open-source ✅ DONE
- Rewrote README.md for public contributors. Created CATALOGUE.md (ruled-out list), CONTRIBUTING.md, updated FINDINGS.md + BACKLOG.md. Archived old docs in archive/.

### B-16: Full T2 on 157 T1.5 survivors (batch) 🔶 IN PROGRESS
- **Status**: 20/157 complete (running on Codespace, 4 parallel pipes).
- **What**: Run `./run_t2_batch.sh` on Codespace. Merge results.
- **Acceptance**: Complete T2 scores for all 157 candidates. Merged master CSV.

---

## NEXT — Ready to Start

### B-18: Full pipeline on h17/poly63
- **Why**: Top T2 scorer (45/55, 198 clean bundles, 5 K3 + 6 elliptic, max h⁰=40). Needs full Stages 1–4 treatment like h13/poly1 got.
- **What**: Build `pipeline_h17_P63.py`. Full divisor analysis, cohomology table, net chirality.
- **Acceptance**: Complete 20-check scorecard. Document in FINDINGS.md.
- **Estimate**: Medium.

### B-19: Expand scan — remove limit=100 cap at h¹¹ = 15–17
- **Why**: We've only scanned 100/553 at h15, 100/5180 at h16, 100/38735 at h17. The strongest candidates are all in this range.
- **What**: Run `scan_chi6_h0.py` with `limit=1000` (or unlimited) at h15–17. Update T1 → T1.5 → T2 pipeline on new hits.
- **Acceptance**: ≥500 polytopes scanned per h¹¹ value.
- **Estimate**: Large (compute-heavy, hours per h¹¹ value).

### B-20: Stage 5 — Higher-rank vector bundles
- **Why**: Line bundles only give U(1). Standard Model needs SU(3)×SU(2)×U(1), which requires rank 4 or 5 vector bundles. This is the critical gap.
- **What**: Implement monad/extension bundle construction on top candidates (h13/poly1 or h17/poly63). Check stability, compute chiral index.
- **Acceptance**: At least one stable rank-n bundle with net chirality = 3 on any candidate.
- **Estimate**: Large (research + implementation). External contributions especially welcome.

### B-21: F-theory discriminant locus classification
- **Why**: All top candidates have elliptic fibrations. Discriminant locus determines gauge groups directly from geometry.
- **What**: For h17/poly63 (6 elliptic fibs), classify singular fibers, determine gauge algebra.
- **Acceptance**: Documented gauge groups for at least one fibration.
- **Estimate**: Medium-Large.

---

## LATER — Backlog

### B-06: Ample Champion orbifold resolution
- **Why**: The full Z₃×Z₃ quotient is singular. Could resolve and check if χ changes to −6.
- **What**: Compute resolved Hodge numbers for the Z₃×Z₃ orbifold.
- **Status**: Parked. Native χ = −6 candidates (h13/poly1, h17/poly63) are cleaner paths.

### B-09: Self-mirror polytope (h11=20, h21=20) deep analysis
- **Why**: Novel self-mirror CY with χ = 0. Rich fibration structure. Undocumented.
- **What**: Full pipeline analysis. Check for freely-acting symmetries. F-theory applications.
- **Status**: Parked. Math curiosity, not a 3-generation candidate.

### B-07: Paper draft
- **Why**: Publishable as a methodology/survey paper even without SM discovery. The pipeline, catalogue of negative results, and CYTools gotchas are useful to the community.
- **Status**: Deferred until T2 batch completes and full pipeline on h17/poly63 is done.

---

## DONE — Completed

| ID | Item | Completed |
|----|------|-----------|
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
