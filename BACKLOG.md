# BACKLOG — χ = −6 CY Landscape Scanner

> Ordered by priority. Top = do next. Updated: 2026-02-24.
>
> **Project direction**: Open-source pipeline + catalogue. Build the sieve,
> record what passes and what doesn't, make it contributor-friendly.
> See [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## NOW — Active Sprint

### B-19: Expand scan — remove limit=100 cap at h¹¹ = 15–18
- **Why**: We've only scanned 100/553 at h15, 100/5180 at h16, 100/38735 at h17. The strongest candidates are all in this range.
- **What**: Run `scan_parallel.py` (multiprocessing, 4 workers) at h15–17, `scan_fast.py` (14 workers) at h18.
- **Acceptance**: ≥500 polytopes scanned per h¹¹ value.
- **Status**:
  - ✅ h15: **553/553 complete** (333 hits, 60%). T1→T1.5→T2 done. h15/poly61 → full pipeline 25/26.
  - ✅ h16: **5,180/5,180 complete** (1,811 hits, 35%). T1→T1.5→T2 done. 20 new T2 entries.
  - 🔶 h17: **running on Codespace** (tmux `h17scan`, 4 workers). ~27,000/38,735 (70%). ETA ~3 hrs remaining.
  - 🔶 h18: **running on Hetzner** (tmux `h18scan`, 14 workers). ~98,000/100,000 (98%). **Nearly done.**
- **Estimate**: h17 ~6hrs Codespace, h18 minutes remaining.

### B-26: GL=12/D₆ Picard-Fuchs study ✅ DONE (core)
- **Why**: The GL=12 polytope (h11=17, h21=20) has the largest automorphism group (|GL(Δ)|=12, D₆) among all χ=−6 polytopes. D₆ symmetry reduces moduli from 20 to 6, making Picard-Fuchs tractable.
- **What**: Compute GKZ periods, derive PF PDE system, extract Yukawa couplings.
- **Completed**:
  - ✅ GKZ A-matrix (5×23, rank 5), integer kernel (18-dim)
  - ✅ D₆ orbit compression: 6 invariant complex structure moduli
  - ✅ Closed-form CT formula (double factorial sum, 501 exact coefficients in 38s)
  - ✅ 26 D₆-invariant Yukawa couplings + invariant c₂ numbers
  - ✅ `picard_fuchs.py` module + `GL12_GEOMETRY.md` reference
  - ✅ PF PDE system in Mori coordinates z₁…z₆ — 6 GKZ box operators (mori_pf.py)
  - ✅ S_α orbit-theta table, explicit □₁-□₆ in θ-form (GL12_GEOMETRY.md §PF Operators)
  - ✅ 1-parameter ODE: ₃F₂ = ₂F₁(1/3,2/3;1;−27t), AESZ #1
  - ✅ ODE factorization: θ·[₂F₁ equation] — z₁-axis is elliptic curve family
  - ✅ Logarithmic period, mirror map (integer coefficients to order 30)
  - ✅ j-invariant: reproduces Klein j (196884 = Monster Moonshine coefficient)
  - ✅ Hesse pencil identification, Wronskian, discriminant locus
  - ✅ 9,366/9,366 GKZ recurrence checks pass
- **Open extensions** (not blocking acceptance):
  - ❌ Full 6-parameter prepotential (CY3 GW invariants require multi-param analysis)
- **Acceptance**: ✅ PF operators in Mori coordinates, verified against period series.

### B-25: Tier 0.25 fast pre-filter (`scan_fast.py`) ✅ DONE
- **Why**: Full scans at h18+ take many hours. A fast pre-filter identifies polytopes worth full analysis without computing exact h⁰ counts for all bundles.
- **What**: Early-termination scanner — scans all χ=3 bundles with `min_h0=3` ambient bound, stops at first h⁰≥3 hit. 100% recall (zero false negatives), ~2.4× speedup.
- **Result**: Validated on h15 (553 polytopes): 333/333 hits caught, 0 false negatives, 2.4 poly/s. On hit polytopes, finds first h⁰≥3 at bundle #316/2408 on average (13% of bundles scanned).
- **Completed**: 2026-02-24.

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
- **Why**: h17/poly25 has **15 elliptic fibrations** (record) and h17/poly63 has 10. Each is a potential F-theory compactification with non-abelian gauge symmetry.
- **What**: For h17/poly25 (15 elliptic fibs) and h17/poly63 (10 elliptic fibs), classify singular fibers (Kodaira types), determine gauge algebra.
- **Acceptance**: Documented gauge groups for at least one fibration.
- **Estimate**: Medium-Large.

### B-24: Run full pipeline on remaining T2 candidates ✅ DONE
- **Result**: All 24 remaining T2=45 candidates analyzed. **37 total pipeline runs** (13 prior + 24 new).
- **19 score 26/26** (perfect). New discoveries: h15/poly94 (380 clean, τ=241), h17/poly53 (418 clean, τ=1016), h17/poly51 (340 clean), h16/poly74 (158 clean, 10 ell fibs).
- **Completed**: 2026-02-23.

### B-22: Run full pipeline on remaining top candidates ✅ DONE
- All 8 original top candidates + 4 new → **12 total**, 7× score 26/26. See PROCESS_LOG entries.

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
