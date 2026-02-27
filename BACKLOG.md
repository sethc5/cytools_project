# BACKLOG — χ = −6 CY Landscape Scanner

> Ordered by priority. Top = do next. Updated: 2026-02-26.
>
> **Project state**: Pipeline v5.2. 70,000 polytopes scanned (h20–h40).
> 1,787 T2-scored with 100-point SM composite. Champions: h28/P874,
> h28/P186 (score 87). Database: `v4/cy_landscape_v4.db`. Hetzner (16-core).
> See [README.md](README.md) and [CATALOGUE.md](CATALOGUE.md).

---

## NOW — Active Sprint

### B-33: Stage 5 — Higher-rank bundles on h28 champions
- **Why**: Line bundles only give U(1). Standard Model needs SU(3)×SU(2)×U(1), requiring rank 4 or 5 vector bundles. `rank_n_bundles.py` has been tested on h14/poly2 only — the h28 champions (P874, P186, P187) are untested.
- **What**: Run SU(4)/SU(5) direct-sum and monad scanners on all three h28 Tier A candidates. Check stability (Hoppe criterion + ∧²V), compute chiral index and Higgs doublet count.
- **Prior results (h14/poly2)**: 100+ SU(4) direct sums with |χ|=3, 100+ SU(5) with |χ(∧²V)|=3, 3 Hoppe-stable monads. All direct sums polystable (never truly stable).
- **Acceptance**: At least one stable rank-n bundle with net chirality = 3 on any h28 champion.
- **Estimate**: Large (research + computation).

### B-34: Triangulation stability — expand FRST sampling
- **Why**: Top-20 T3 deep analysis used 50 random FRSTs per candidate. Stability percentages (e.g. P874 at 50%, P187 at 55%) have wide confidence intervals at n=50.
- **What**: Expand to 200+ FRSTs for all Tier A candidates. Report c₂ hash and κ hash distributions, refine stability confidence intervals.
- **Acceptance**: 200+ FRST samples per Tier A candidate with ≤5% CI on stability fraction.
- **Estimate**: Small–Medium (computation only, infrastructure exists).

### B-35: Paper draft
- **Why**: Tier A candidates (P874, P186, P187) + pipeline methodology + triangulation stability + catalogue of negative results are paper-ready. The v5.2 pipeline, 70K-polytope scan, and scoring system are a contribution regardless of SM discovery.
- **What**: Draft structure in [paper_outline.md](paper_outline.md). Key sections: methodology (pipeline stages), landscape statistics, champion cluster geometry, triangulation stability, CYTools gotchas.
- **Acceptance**: Complete draft with figures, tables, and bibliography.
- **Estimate**: Large.

### B-36: Documentation cleanup sprint ✅ DONE
- **Why**: Docs were frozen at early project state (Polytope 40 era, 1,025 polytopes, 26-point scoring). Needed updating to reflect v5.2 pipeline, 70K polytopes, h28 champions.
- **What**: Systematic review and update of all .md files.
- **Completed**:
  - ✅ FINDINGS.md: Rebuilt from 2,176→~450 lines, executive summary, consolidated leaderboard (commit `83e37be`)
  - ✅ PROCESS_LOG.md: Added 6 missing entries, fixed dates and formatting (commit `83e37be`)
  - ✅ VERSIONS.md: Added v4.1 and v5 sections (commit `831f269`)
  - ✅ MATH_SPEC.md: Fixed numbering, resolved open questions, added §11–§12 (commit `961c7c7`)
  - ✅ FRAMEWORK.md: Updated all stages to current numbers, v5.2 leaderboard (commit `37414ef`)
  - ✅ CATALOGUE.md: Updated coverage, funnel, leaderboard, deep results (commit `a49622e`)
  - ✅ BACKLOG.md: This update

---

## NEXT — Ready to Start

### B-37: Low-h¹¹ rescore under v5.2
- **Why**: h13–h19 legacy candidates were scored with the old 26-point system (v3–v4). Some may rank competitively under the 100-point SM composite, especially those with strong Yukawa or LVS metrics.
- **What**: Ingest legacy polytopes into `cy_landscape_v4.db`, run T2 scoring with v5.2 pipeline. Compare rankings.
- **Acceptance**: All legacy top-20 candidates have v5.2 scores. Any scoring ≥75 get T3 deep analysis.

### B-38: GL=12/D₆ — full 6-parameter prepotential
- **Why**: The 1-parameter slice (z₁-axis = Hesse pencil) is solved. The full CY3 prepotential requires the 6-parameter PDE system in Mori coordinates.
- **What**: Solve the coupled PF system □₁–□₆ for the full period vector. Extract genus-0 GW invariants. Compare with existing literature (AESZ database, OEIS).
- **Acceptance**: Genus-0 GW invariants for at least one non-trivial class.
- **Estimate**: Hard (multi-parameter PDE solving).

### B-39: F-theory discriminant locus on h28 champions
- **Why**: h28 champions may have elliptic fibrations with interesting gauge algebras. Legacy champion h17/poly25 had 15 elliptic fibrations (record) with SU(5) GUT candidates.
- **What**: Run `fiber_analysis.py` on h28/P874, P186, P187. Classify Kodaira types. Determine gauge content.
- **Acceptance**: Gauge algebra tabulated for all fibrations of all three h28 Tier A candidates.

---

## LATER — Backlog

### B-06: Ample Champion orbifold resolution
- **Why**: The full Z₃×Z₃ quotient is singular. Could resolve and check if χ changes to −6.
- **What**: Compute resolved Hodge numbers for the Z₃×Z₃ orbifold.
- **Status**: Parked. h28 champions (score 87) are far stronger paths.

### B-09: Self-mirror polytope (h11=20, h21=20) deep analysis
- **Why**: Novel self-mirror CY with χ = 0. Rich fibration structure. Undocumented.
- **What**: Full pipeline analysis. Check for freely-acting symmetries. F-theory applications.
- **Status**: Parked. Math curiosity, not a 3-generation candidate.

### B-40: Raise EFF_MAX beyond 22
- **Why**: h37+ is barren at EFF_MAX=22. Raising the ceiling could unlock new populations but at significant computational cost (more bundles to check per polytope).
- **What**: Test EFF_MAX=25 or 28 at h35–h40. Measure T0 pass rate vs compute time.
- **Status**: Low priority — h28 sweet spot already found.

---

## DONE — Completed

| ID | Item | Completed |
|----|------|-----------|
| D-41 | B-36: Documentation cleanup sprint — FINDINGS, PROCESS_LOG, VERSIONS, MATH_SPEC, FRAMEWORK, CATALOGUE, BACKLOG | 2026-02-26 |
| D-40 | v5.2 MONOTONIC_MAX score drift bug fix — post-upsert rescore | 2026-02-26 |
| D-39 | T3 Deep Analysis — top 20 candidates, 50 FRSTs each, tier A/B/C assignments | 2026-02-26 |
| D-38 | 50K h28 deep coverage scan — P1040 (score=80) found, champions not displaced | 2026-02-26 |
| D-37 | v5.1 KS `limit` bug discovery and fix (`--limit N` CLI argument) | 2026-02-26 |
| D-36 | v5.0 scoring overhaul — 100-point SM composite, 12 components, yukawa_rank bug fix | 2026-02-26 |
| D-35 | v4.1 tuning — EFF_MAX=22, dp_divisors removed, vol_hierarchy added | 2026-02-26 |
| D-34 | h20–h40 landscape scan — 21K polytopes, 1,718 T2-scored, new h28 champions (score 87) | 2026-02-26 |
| D-33 | B-18: h18 T0.25 scan complete — 105,811 polytopes, 30,293 passes | 2026-02-25 |
| D-32 | B-19/B-28: h16 auto_scan (5,180→200→190): 58× 26/26, 100% SM, 89% GUT, max clean=50, τ=6,468 | 2026-02-25 |
| D-31 | B-19/B-28: h15 auto_scan (553→200→192): 28× 26/26, 99% SM, 62% GUT, max clean=45, τ=14,436 | 2026-02-25 |
| D-30 | B-19/B-28: h17 auto_scan (38,735→200→193): 87× 26/26, 100% SM, 86% GUT, max clean=59, τ=8,608 | 2026-02-25 |
| D-29 | B-28: Automated scan pipeline (`auto_scan.py`) — unified 6-script replacement, h14 validated, checkpoint/resume | 2026-02-25 |
| D-28 | B-21: F-theory Kodaira fiber classification — 39/39 SM, 17/39 SU(5) GUT (`fiber_analysis.py`) | 2026-02-25 |
| D-26a | B-26: GL12/D₆ closed-form period + Yukawa couplings + picard_fuchs.py | 2026-02-23 |
| D-27 | B-24: Full pipeline on all 37 T2=45 candidates (19× 26/26) | 2026-02-23 |
| D-26c | B-26: PF operators in θ-coordinates + 1-param ODE + AESZ #1 (mori_pf.py + GL12_GEOMETRY.md) | 2026-02-23 |
| D-26b | B-26: GL12_GEOMETRY.md complete geometry reference | 2026-02-23 |
| D-25 | B-25: Tier 0.25 fast pre-filter (`scan_fast.py`) — 100% recall, 2.4× speedup | 2026-02-24 |
| D-24c | B-22+: Full pipeline h16/poly63 → 26/26, 78 clean, τ=836 (triple-threat #2) | 2026-02-23 |
| D-24b | B-22+: Full pipeline h17/poly25 → **26/26**, 170 clean, **15 ell** (F-theory + triple-threat champ) | 2026-02-23 |
| D-24a | B-22+: Full pipeline h16/poly53 → 23/26, 300 clean (2nd most), no Swiss cheese | 2026-02-23 |
| D-24 | B-22+: Full pipeline h19/poly16 → 22/26, 86 clean, h¹¹=19 | 2026-02-23 |
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
