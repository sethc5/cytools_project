# BACKLOG — χ = −6 CY Landscape Scanner

> Ordered by priority. Top = do next. Updated: 2026-03-06.
>
> **Project state**: Pipeline v6 (yukawa-fix, --local-ks). **3.11M polytopes** scanned (h13–h40).
> **965 T3-verified** (all score≥70). **37 T4-verified** (score≥80, T4 confirmed stable
> at 200/60 samples — zero score changes). Champion: **h26/P11670 (sm=89)**.
> Landscape boundary confirmed: h11≤28 productive; h29-h32 full (5.45M) barren.
> Database: `v6/cy_landscape_v6.db` (827MB). Hetzner (16-core i9, 128GB).
> See [README.md](README.md) and [FINDINGS.md](FINDINGS.md).

---

## NOW — Active Sprint

### B-41: Paper draft
- **Why**: The v6 scan is publishable. 3.11M polytopes through a T4-verified pipeline, boundary confirmation (barren past h11=28), a clear champion cluster, and T4 triangulation stability tables are a methodological contribution regardless of full SM vacuum construction.
- **What**: Draft in [paper_outline.md](paper_outline.md). Key sections: motivation (chi=−6 generation counting), pipeline methodology (T0→T4 stages, 100-pt scoring), landscape statistics (funnel, T0-wall, h11 trend), champion cluster (h26/P11670 geometry), boundary confirmation (§29 h29-h32 barren), triangulation stability (T4 results table), discussion (what score means, path to vacuum).
- **Acceptance**: Complete draft with abstract, 6 sections, figures described, tables, bibliography skeleton.
- **Estimate**: Large. See [paper_outline.md](paper_outline.md) for current state.

### B-42: Champion deep physics — h26/P11670
- **Why**: sm=89 globally optimal under v6 scoring. T4-verified (200 triangulations, c2_stable=0.033). Next is physics content: fibration structure, gauge algebra, higher-rank bundle candidates.
- **What**:
  1. **Fibration/Kodaira analysis** — run `fibration_analysis.py` on h26/P11670. The DB already shows it has SM+GUT fibrations (from T3 screening). Classify Kodaira types, tabulate gauge content, identify G4-flux candidates.
  2. **Higher-rank bundles** — SU(4)/SU(5) direct-sum and monad scanner (was `rank_n_bundles.py`, tested on h14/poly2). Check Hoppe stability + ∧²V, compute chiral index, Higgs doublet count.
  3. **F-theory discriminant locus** — elliptic fibrations with ADE monodromy give non-Abelian gauge sectors; compare with SM gauge algebra target.
- **Acceptance**: Fibration table complete; at least one SU(4)/SU(5) bundle checked for stability.
- **Estimate**: Medium-Large (research + computation). Detailed plan in [FINDINGS.md §28](FINDINGS.md).

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
- **What**: Run `fibration_analysis.py` on h26/P11670 (champion). Classify Kodaira types. Determine gauge content.
  - *Updated from B-39 (h28/P874,P186,P187) — h28 champions rescored under v6 to sm<80; h26/P11670 is now the clear target.*
- **Acceptance**: Gauge algebra tabulated for all fibrations of h26/P11670; SU(5) GUT fibrations identified.

---

## NEXT — Ready to Start

### B-37: Low-h¹¹ rescore under v6
- **Why**: h13–h19 legacy candidates were scored with the old v4/v5 pipeline. Some may rank competitively under v6's 100-point SM composite.
- **What**: Ingest legacy polytopes into `cy_landscape_v6.db`, run T2 scoring with v6 pipeline. Compare rankings.
- **Acceptance**: All legacy top-20 candidates have v6 scores. Any scoring ≥75 get T3 deep analysis.

### B-38: GL=12/D₆ — full 6-parameter prepotential
- **Why**: The 1-parameter slice (z₁-axis = Hesse pencil) is solved. The full CY3 prepotential requires the 6-parameter PDE system in Mori coordinates.
- **What**: Solve the coupled PF system □₁–□₆ for the full period vector. Extract genus-0 GW invariants. Compare with AESZ database.
- **Acceptance**: Genus-0 GW invariants for at least one non-trivial class.
- **Estimate**: Hard (multi-parameter PDE solving).

### B-43: h30+h31 full scan (optional closure)
- **Why**: h30 is ~7% covered (100K / 1.43M), h31 is ~4% (50K / 1.26M). Coverage gaps are real, though trend is strongly negative (max_sm=75 at 7% coverage). Marginal probability of new sm≥80 is low.
- **What**: Copy `batch_ext_h29_h32.sh`, trim to h30/h31, offset=0, limit=9999999. ~4h on Hetzner.
- **Acceptance**: h30/h31 exhausted; any new sm≥80 T3-verified and merged.
- **Estimate**: Small (infrastructure exists). Verdict: skip unless closure is required before paper submission.

---

## LATER — Backlog

### B-06: Ample Champion orbifold resolution
- **Why**: The full Z₃×Z₃ quotient is singular. Could resolve and check if χ changes to −6.
- **What**: Compute resolved Hodge numbers for the Z₃×Z₃ orbifold.
- **Status**: Parked. h26/P11670 (sm=89) is the far stronger path.

### B-09: Self-mirror polytope (h11=20, h21=20) deep analysis
- **Why**: Novel self-mirror CY with χ = 0. Rich fibration structure. Undocumented.
- **What**: Full pipeline analysis. Check for freely-acting symmetries. F-theory applications.
- **Status**: Parked. Math curiosity, not a 3-generation candidate.

### B-40: Raise EFF_MAX beyond 22
- **Why**: h37+ is barren at EFF_MAX=22. Raising the ceiling could unlock new populations.
- **What**: Test EFF_MAX=25 or 28 at h35–h40. Measure T0 pass rate vs compute time.
- **Status**: Very low priority — §29 full scan (5.45M) confirmed barren past h11=28 even at current EFF_MAX.

### B-44: hetzner2 provisioning
- **Why**: W-2295/256GB at 144.76.222.125 still in rescue mode. Would provide 32 cores for heavier compute.
- **What**: `installimage` → Debian 12, rsync chi6 files + DB, rebuild devcontainer.
- **Status**: Parked pending need.

---

## DONE — Completed

| ID | Item | Completed |
|----|------|-----------|
| D-47 | §30 T4 deep triangulation — 37/37 top candidates, 200/60 samples, 39 min, zero score changes | 2026-03-06 |
| D-46 | §29 scan — h29-h32 full (5.45M polytopes, barren, landscape boundary h11≤28 confirmed) | 2026-03-06 |
| D-45 | §28 scan — h26-h28 +50K each (barren, 0/150K T0 passes) | 2026-03-06 |
| D-44 | §27 T3 sweep — all score≥70 T2-only candidates T3-verified (628 entries, zero crossed ≥74) | 2026-03-05 |
| D-43 | §26b T3 sweep — score 70-79 tier, 300 candidates, 2 crossed ≥80 | 2026-03-04 |
| D-42 | §26a T3 sweep — score=80 T2-only, 27 candidates, fibration bug fixed (merge_t3_results.py) | 2026-03-04 |
| D-41 | B-36: Documentation cleanup sprint — FINDINGS, PROCESS_LOG, VERSIONS, MATH_SPEC, FRAMEWORK, CATALOGUE, BACKLOG | 2026-02-26 |
| D-40 | v5.2 MONOTONIC_MAX score drift bug fix — post-upsert rescore | 2026-02-26 |
| D-39 | B-34: T3 Deep Analysis — top candidates, T4 now supersedes (200/60 samples, commit d97d158) | 2026-02-26 / 2026-03-06 |
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
