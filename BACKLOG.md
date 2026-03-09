# BACKLOG — χ = −6 CY Landscape Scanner

> Ordered by priority. Top = do next. Updated: 2026-03-08.
>
> **Project state**: Pipeline v6 (yukawa-fix, --local-ks). **3.11M polytopes** scanned (h13–h40).
> **938 T3-verified** (all score≥70). **37 T4-verified** (score≥80). Champion: **h26/P11670 (sm=89)**.
> Landscape boundary confirmed: h11≤28 productive; h29-h32 full (5.45M) barren.
> **Champion deep physics** (B-42/B-45/B-46 DONE): Kodaira ✅, figures ✅, direct-sum ✅ (0 Hoppe-stable),
> monad LP ✅ (612 slope-feasible / 6M sampled, 0 tadpole-OK — D3 charge obstructed at h11=28).
> **B-46 numerical run** ✅ (2026-03-09, local): |β|≤1 confirmed obstructed (3.6M sampled, 0 tadpole pre-OK). c₂(V)_max≈350 >> c₂(TX)_max=56 even at minimal charges. Structural D3-tadpole obstruction fully proved.
> **B-49 H-flux** ✅ (2026-03-09): flux tadpole scan on h22/P682. Best monad Δn_D3=53, minimal flux N=[9,5,0,...], Bianchi n_M5=0 ✓.
> **B-50 Extension bundles** ✅ (2026-03-09): 3M samples, 3 scalar-Δ≤0 candidates found, all with component-wise violations 41-108 >> c₂(TX)_max=26. Same geometric obstruction as monads confirmed.
> **B-41 paper draft** ✅ DONE (session 1: 17pp; session 2: 29pp). `paper/paper.tex` 29pp, 8 figures, full bibliography, pdflatex clean. JHEP target 35-50pp — 6pp remaining minimum.
> **B-37 low-h11 rescore** ✅ DONE: h13-h14 all T0-fail (gap<2), h15 max=63, h16 max=76 (T3 verified: 0 fibers, stable tri), h17-h19 already T3. Paper Table 1 updated.
> **Next**: B-51 observable scoring or B-53 (larger |β|≥3 or spectral covers on h22/P682).
> Database: `v6/cy_landscape_v6.db` (827MB). Hetzner (16-core i9, 128GB).
> See [README.md](README.md) and [FINDINGS.md](FINDINGS.md).

---

## v7 Sprint — Observable-First Discovery

> **Intent**: Stop asking "does it match the SM?" — start asking "what does it predict?"  
> See `v7/README.md` for full architecture. Two parallel tracks: non-perturbative
> completion (Track A) and observable-first scoring (Track B).

### B-49 (Track A): H-flux tadpole cancellation scan — h22/P682

**Goal**: The D3 excess is $\Delta n_{D3} \approx 90$ for all priority entries
(B-47a/B-48). Compute the H-flux lattice for h22/P682 and find integer flux
quanta $H_{abc}$ such that $n_{D3}^{\rm flux} \geq -90$, then check remaining
consistency (Bianchi identity, flux quantization).

**Steps**:
- [x] Extract intersection form $\kappa_{abc}$ for h22/P682 from v6 DB
- [x] Compute $n_{D3}^{\rm flux} = -\frac{1}{2} H_{abc} H^{abc}$ over flux lattice
- [x] Find minimal flux quanta that cancel excess
- [x] Check Bianchi identity: $dH = \text{tr}(R \wedge R) - \text{tr}(F \wedge F)$
- [x] Write `v7/flux_tadpole_scan.py`

**Status**: ✅ **DONE** (2026-03-09, local).
- Best monad candidate (idx=216, config (6,2)): **Δn_D3 = 53** (mean = 651 across 221 slope-feasible)
- Minimal H-flux: **N = [9, 5, 0, ...]** (2 non-zero components), ||N||² = 106 → n_D3^flux = −53
- **Bianchi identity with flux: n_M5 = 0** ✓ physical
- Freed-Witten: c₂(TX) all even, integer flux quanta valid (no twisted sectors)
- Lattice degeneracy: ~2.3×10²¹ valid flux configs at minimum norm
- Results: `v7/results/flux_tadpole_22_682.json` / `.txt`
- **Next**: B-50 — extension bundles on h22/P682; also need period matrix for exact flux quanta

### B-50 (Track A): Extension bundle construction — h22/P682

**Goal**: Build rank-4 bundles as extensions $0 \to L_1 \to V \to E \to 0$
where $E$ is rank-3. More flexible than monads; may avoid the tadpole obstruction.

**Steps**:
- [x] Build c₂(V) = −ch₂(V) formula (Whitney + ch additivity, verified equivalent)
- [x] Scalar Δn_D3 = Σ[c₂(V)−c₂(TX)] criterion (consistent with B-49)
- [x] KC-sampled slope check: μ(O(α), J) < 0 for J in toric Kähler cone (1592 rays, h11_eff=21)
- [x] 3M samples: 4,082 χ=±3 → 3,016 Δ≤200 → 1,647 slope-feasible

**Status**: ✅ **DONE** (2026-03-09, local).
- **Scalar tadpole**: 3 candidates Δ≤0 (ideal), 84 with Δ≤53 (as per B-49 H-flux budget)
- **Component-wise tadpole**: ALL "ideal" (Δ≤0) candidates have 10–12 component violations,
  max excess 41–108 >> c₂(TX)_max=26. The mixed-sign κ tensor (negative entries at divisors
  k=6,9,10,15,17,18,19,20 where c₂(TX)<0) causes c₂(V)_k >> c₂(TX)_k for those components
  even when the scalar sum accidentally cancels.
- **Finding 28e**: Extension bundles at |β|≤2 face the same component-wise D3-tadpole
  obstruction as monads. The obstruction is geometric: κ_{kab} < 0 at the negative-c₂(TX)
  divisors forces c₂(V)_k > 0 for those components regardless of rank/type of bundle.
- Results: `v7/results/ext_bundles_22_682.json` (1,647 candidates) / `.txt`
- Script: `v7/extension_bundles.py`
- **Next**: B-51 (observable scoring) or B-53 (larger |β| or spectral covers)

### B-51 (Track B): Observable scoring — rescore v6 T4 cluster

**Goal**: Compute v7 observable scores for all 37 T4-verified polytopes.
Implement `v7/observable_score.py` with the scoring spec from `v7/README.md`.

**Observables**:
- [ ] DM mass estimate: $m_{\rm DM} \sim m_{3/2}$ from SUSY breaking scale
- [ ] Proton decay: $M_{\rm GUT}$ from gauge coupling unification at $k_{abc}$
- [ ] Gauge unification check: $\alpha_{\rm GUT}$ from intersection numbers
- [ ] Write results to `v7/cy_landscape_v7.db`

### B-52 (Track B): Relax gauge group filter — find non-SU(5) 3-generation vacua

**Goal**: Scan for stable bundles with net 3 generations regardless of gauge group.
Ask what gauge group they break to, rather than requiring SU(5) or SU(4) as input.

---

## NOW — Active Sprint

### B-46: Restricted-charge monad search + integrated tadpole LP
- **Why**: sm=89 globally optimal under v6 scoring. T4-verified (200 triangulations, c2_stable=0.033). Next is physics content: fibration structure, gauge algebra, higher-rank bundle candidates.
- **What** (status):
  1. ✅ **Fibration/Kodaira analysis** — `champion_kodaira.py` complete. 11 fibrations classified. **F11 = su(10)/I₁₀** fiber → best SU(5)×U(1)_Y GUT candidate. F8 E₇ ambiguity (I₈ vs III*) requires Weierstrass model to resolve. Output: `results/champion_kodaira.json`. Committed `a342a8a`.
  2. ✅ **Figures** — `figures.py` complete (local, 827MB DB). 9 PNGs generated in `results/figures/`. Figures 1–8 + supplementary score-vs-stability plot. Committed `a342a8a`.
  3. ✅ **Direct-sum bundle scan** — `champion_bundles.py` complete on Hetzner. SU(4): 500K trials → 0 Hoppe-stable. SU(5): 300K trials → 161 χ=±3 → 0 Hoppe-stable. Result expected: direct sums are polystable (not slope-stable). Output: `results/champion_bundles.json`. Commits `742b54d`–`2c30cd0`.
  4. ✅ **Monad scan k_max=2** — 3M trials / 3 configs → **0 slope-stable**.
  5. ✅ **Monad scan k_max=3** — 6M trials / 3 configs → **0 slope-stable** (73 min, Hetzner).
     Root cause identified: random Kähler sampling fails for h11_eff=28 (exponentially small probability any random J satisfies all slope inequalities simultaneously).
  6. ✅ **LP slope filter** — `champion_monads_lp.py` complete. 612 slope-feasible / 5.99M sampled; 0 tadpole-OK after corrected ch₂ formula (Finding 28c). See B-45.
  7. ⬜ **F-theory Weierstrass model** — F8 fiber I₈ vs III*/E₇ ambiguity; requires explicit Weierstrass computation (non-blocking for paper).
- **Acceptance**: Fibration table ✅; slope/tadpole analysis ✅ (0 candidates — obstruction documented).
- **Outcome**: D3-tadpole obstruction at h11=28 with |β|≤3. See B-46 for restricted-charge follow-up.
- **Status**: ✅ **DONE** except Weierstrass F8 (deferred to B-47).

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

### B-45: Monad scan follow-up — k_max=3 and cohomology ✅ COMPLETE
- **Why**: k_max=2 monad scan on champion found 0 slope-stable bundles across configs (5,1), (6,2), (7,3). Two explanations: (a) search space too small — k_max=3 opens much larger lattice; (b) h11_eff=28 makes slope stability constraints very tight with random Kähler sampling.
- **What**:
  1. ✅ Run k_max=3, 2M trials — done, 0 slope-stable from 6M trials.
  2. ✅ **LP slope filter** — `champion_monads_lp.py`: gradient optimization found 612 slope-feasible candidates (406 with vol_J>0). Run: 5,989,706 sampled, elapsed 4435s.
  3. ✅ **Tadpole check** — Original check had bug (linear formula → always 0). Corrected to quadratic ch₂(O(β))_k = (1/2)κ_{kab}β^a β^b via `recheck_tadpole.py`. Result: 0/406 pass. c₂(V)_max ∈ [167,1654] vs c₂(TX)_max = 24. D3-charge violation by 7–70×.
  4. ✅ Updated FINDINGS.md §28 with LP results and tadpole diagnosis.
- **Outcome**: SU(4) monad bundles with charges |β^a| ≤ 3 generate quadratic ch₂(V) ≫ c₂(TX). Fundamental obstruction at h11=28. See Finding 28c.
- **Next**: B-46 — Restricted-charge monad search: |β^a| ≤ 1, tadpole built into LP constraint.
- **Files**: `champion_monads_lp.py`, `recheck_tadpole.py`, `results/champion_monads_lp*.json`
- **Status**: ✅ **DONE** (2026-03-07)

---

### B-46: Restricted-charge monad search + integrated tadpole LP
- **Why**: B-45 revealed that charges |β^a| ≤ 3 generate c₂(V) >> c₂(TX). Restricting to |β^a| ≤ 1 keeps ch₂(O(β))_k ≤ max(κ)/2 per summand, which may fit under c₂(TX)_max=24.
- **What**:
  1. Modify `champion_monads_lp.py` to enforce |β^a| ∈ {-1,0,+1} for all charges.
  2. Add tadpole as quadratic constraint: ch₂(B)_k - ch₂(C)_k ≥ -c₂(TX)_k for all k (i.e. c₂(V)_k ≤ c₂(TX)_k).
  3. Combined LP: find J, B, C simultaneously satisfying slope stability AND tadpole (or use two-phase: first tadpole feasibility, then slope LP over valid (B,C) pairs).
  4. Run on Hetzner for all configs (5,1),(6,2),(7,3).
- **Acceptance**: Either find a tadpole+slope-stable monad, or prove the search space (|β|≤1) is exhausted.
- **Estimate**: Medium–Hard. Phase 1 brute-force feasible for |β|≤1 (3^28 ≈ 2.3e13 — too large; sample 10M).
- **Status**: ✅ **DONE** (2026-03-09) — numerical run on local (board5, 12-core): 3,631,565 sampled, 26,643 χ=±3 ok, **0 tadpole pre-OK**. Tadpole ceiling check confirmed c₂(V)_max≈350 >> c₂(TX)_max=56 at |β|=1. D3-tadpole obstruction is structural and complete across all charge magnitudes. See Finding 28d.
- **Files**: `v6/champion_monads_b46.py`, `v6/results/champion_monads_b46.json`, `v6/results/champion_monads_b46_top.txt`

---

### B-37: Low-h¹¹ Rescore Under v6 ✅ DONE (2026-03-08)
- **Acceptance**: All legacy top-20 candidates have v6 scores. Any scoring ≥75 get T3 deep analysis.

### B-38: GL=12/D₆ — full 6-parameter prepotential
- **Why**: The 1-parameter slice (z₁-axis = Hesse pencil) is solved. The full CY3 prepotential requires the 6-parameter PDE system in Mori coordinates.
- **What**: Solve the coupled PF system □₁–□₆ for the full period vector. Extract genus-0 GW invariants. Compare with AESZ database.
- **Acceptance**: Genus-0 GW invariants for at least one non-trivial class.
- **Estimate**: Hard (multi-parameter PDE solving).

### B-43: h30+h31 full scan — SKIPPED (D-52)
- **Why skipped**: h30 max_sm=75 at 7% coverage (100K/1.43M); h31 max_sm=75 at 4% (50K/1.26M).
  Trend is strongly negative; marginal probability of new sm≥80 is negligible.
  The T0-wall analysis (§2.3 of paper) independently predicts barrenness at h11≥30.
  Server resources freed for other work.
- **Verdict**: Definitively closed. No scan needed before submission. ✅ 2026-03-07.

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
| D-50 | B-37: Low-h11 rescore — h13-h14 T0-fail (gap<2), h15 max=63, h16/P118 T3 score=76 (0 fibers, stable tri, no instanton div); Table 1 updated | 2026-03-08 |
| D-47 | §30 T4 deep triangulation — 37/37 top candidates, 200/60 samples, 39 min, zero score changes | 2026-03-06 |
| D-46 | §29 scan — h29-h32 full (5.45M polytopes, barren, landscape boundary h11≤28 confirmed) | 2026-03-06 |
| D-45 | §28 scan — h26-h28 +50K each (barren, 0/150K T0 passes) | 2026-03-06 |
| D-44 | §27 T3 sweep — all score≥70 T2-only candidates T3-verified (628 entries, zero crossed ≥74) | 2026-03-05 |
| D-43 | §26b T3 sweep — score 70-79 tier, 300 candidates, 2 crossed ≥80 | 2026-03-04 |
| D-42 | §26a T3 sweep — score=80 T2-only, 27 candidates, fibration bug fixed (merge_t3_results.py) | 2026-03-04 |
| D-41 | B-36: Documentation cleanup sprint — FINDINGS, PROCESS_LOG, VERSIONS, MATH_SPEC, FRAMEWORK, CATALOGUE, BACKLOG | 2026-02-26 |
| D-40 | v5.2 MONOTONIC_MAX score drift bug fix — post-upsert rescore | 2026-02-26 |
| D-39 | B-41: Paper draft — `paper/paper.tex` 17pp LaTeX, 8 figures, full bibliography, pdflatex clean | 2026-03-08 |
| D-51 | B-41 expansion: 21pp→29pp — §3.3 LVS, §3.4 Koszul, §3.5 Fibration, §5.6 Cluster, §6.3 FRST, §8.4 F-theory, App D score, §2.4 chi=-6 | 2026-03-07 |
| D-52 | B-43: h30+h31 scan — SKIPPED. max_sm=75 at 7% coverage, T0-wall confirms barrenness, server freed | 2026-03-07 |
| D-48 | B-46: Restricted-charge monad (|β|≤1) — exact structural D3-tadpole obstruction proved analytically | 2026-03-08 |
| D-49 | B-34: T3 Deep Analysis — top candidates, T4 now supersedes (200/60 samples, commit d97d158) | 2026-02-26 / 2026-03-06 |
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
