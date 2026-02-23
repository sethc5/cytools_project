# PROCESS LOG — CYTools Project

> Chronological record of investigations, decisions, and issues encountered.
> New entries go at the top. Reference BACKLOG.md items by ID.

---

## 2026-02-25 — Merge fix: early T2 (20) + batch T2 (157) → 177 total

**Issue discovered**: The 20 polytopes screened in the early T2 run (2026-02-22) were stored in `tier2_screen_results.csv` but never merged into `tier2_full_results.csv` when the 157-polytope batch ran. This caused 20 real results — including several top candidates — to be missing from the "full" CSV and all downstream documentation. Zero overlap between the two sets.

**Fix**: Merged both CSVs. Reran all 7 top early-T2 candidates to confirm reproducibility — all matched exactly. Backup of early results: `tier2_screen_results_early20_backup.csv`.

**New total**: 177 T2-screened polytopes.

---

## 2026-02-24 — T2 batch complete: 157/157, new leaders discovered

**Work done**: All 4 Codespace T2 pipes finished (33–41 min each). Pulled results locally, saved to `results/tier2_full_results.csv`. Updated CATALOGUE.md, README.md, FINDINGS.md.

**Key discoveries from the combined 177-polytope T2 results** (157 batch + 20 early):

| Polytope | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell | Note |
|----------|-----|------------|-------|--------|-----|-----|------|
| **h14/poly2** | 41 | **268** | 828 | 13 | 3 | 1 | Most clean bundles. Lowest h¹¹ in top 20. |
| **h16/poly11** | 41 | **255** | 840 | 13 | 3 | 1 | #2 clean count. From early T2 batch. |
| **h17/poly96** | 39 | 227 | 930 | **65** | 2 | 1 | Highest max h⁰ ever recorded. |
| **h17/poly63** | 45 | **198** | 922 | 40 | 5 | 6 | Top T2=45 by clean count + best fibrations. |
| **h18/poly34** | 45 | 189 | 730 | 16 | 4 | 4 | From early T2 batch. |
| h16/poly74 | 45 | 24 | 80 | 4 | 5 | **10** | Most elliptic fibrations → F-theory target. |
| h17/poly45 | 45 | 61 | 404 | 16 | **6** | **8** | Most K3 fibrations. |

**Score distribution**: 30 at T2=45 (max), 80 at T2≥41, 177 total. The T2 scoring saturates — clean bundle count is the better discriminator.

**Decision**: h14/poly2 and h17/poly63 are the two priority candidates for full pipeline runs. h14/poly2 has the most clean bundles at lowest h¹¹; h17/poly63 is the top T2=45 scorer (198 clean, 5 K3 + 6 elliptic).

**Commits**: tier2_full_results.csv (merged), updated CATALOGUE/README/FINDINGS/BACKLOG

---

## 2026-02-24 — Repo restructured for open-source

**Work done**: Rewrote README.md, created CATALOGUE.md and CONTRIBUTING.md, updated FINDINGS.md and BACKLOG.md. Archived old README and FINDINGS. Pushed to GitHub.

**Strategic direction**: Open-source pipeline + catalogue. Build the sieve, record what passes, make it contributor-friendly. "Nothing big unless we find the big one."

**Commits**: 8dc9d63

---

## 2026-02-22 — Tier 1.5 sweep complete: 157 T2-worthy candidates

**Work done**: Ran `tier15_screen.py` on all 317 remaining Tier 1 candidates (excluding 20 already T2-screened). Phase A (fibrations) + Phase B (300-bundle capped probe). Total runtime: 26.8 min locally.

**Results**:
- 244/317 (77%) have clean h⁰=3 bundles in the 300-bundle probe
- **157/317 have ≥3 clean → T2-worthy** (promotion threshold)
- 1,584 total clean bundles found from probing alone
- ALL 317 have K3/elliptic fibrations (universal for χ=-6)

**Top T1.5 candidates** (not yet T2-screened):

| Rank | Polytope | T1.5 | Probe clean | Probe h⁰≥3 | max h⁰ | K3 | Ell |
|------|----------|------|-------------|-------------|--------|-----|-----|
| 1 | h18/poly32 [NF] | 40 | 21 | 89 | 30 | 4 | 4 |
| 2 | h17/poly53 [NF] | 40 | 20 | 74 | 10 | 3 | 3 |
| 3 | h18/poly31 [NF] | 40 | 18 | 90 | 20 | 4 | 4 |
| 4 | h15/poly61 [NF] | 40 | 15 | 40 | 4 | 3 | 3 |
| 5 | h16/poly53 [NF] | 40 | 14 | 70 | 12 | 5 | 6 |

**Early T2 validation** of top T1.5 candidates:
- h18/poly32: T2=45/55, **49 clean bundles** (21 found in 300-probe → full search found 49)
- h18/poly31: T2=45/55, **29 clean bundles**

**Next step**: Full T2 on all 157 T2-worthy candidates via 4-pipe parallel batch on Codespace (`run_t2_batch.sh`). Estimated ~40 min with 4 cores.

**Commits**: tier15_screen_results.csv, tier2_screen.py (--csv15/--offset/--batch), run_t2_batch.sh

---

## 2026-02-22 — Tier 2 deep screening: top 20 from Tier 1

**Work done**: Built `tier2_screen.py`. Four expensive checks per polytope: (1) exact h⁰=3 bundle count with full Koszul computation, (2) h³=h⁰(-D)=0 verification for all h⁰≥3 bundles, (3) D³ intersection statistics, (4) K3/elliptic fibration count from dual-polytope geometry.

**Validated**: Tested on h13-P1 benchmark — found 25 clean bundles, 3 K3, 3 elliptic, matching `pipeline_h13_P1.py` exactly. T2 score 45/55.

**Top results from early T2 run** (20 candidates from Tier 1, 29 min total):

| Rank | Polytope | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell |
|------|----------|-----|------------|-------|--------|-----|-----|
| 1 | h17/poly63 [NF] | 45 | **198** | 922 | 40 | 5 | 6 |
| 2 | h18/poly34 [NF] | 45 | **189** | 730 | 16 | 4 | 4 |
| 3 | h17/poly90 [NF] | 45 | **148** | 542 | 16 | 3 | 3 |
| 4 | h16/poly63 [NF] | 45 | 72 | 584 | 37 | 4 | 4 |
| 5 | h18/poly6 [NF] | 45 | 56 | 514 | 24 | 3 | 3 |
| 6 | h15/poly94 [NF] | 45 | 36 | 126 | 10 | 4 | 4 |
| 12 | h16/poly11 [NF] | 41 | **255** | 840 | 13 | 3 | 1 |
| — | h13-P1 (bench) | 45 | 25 | 76 | 6 | 3 | 3 |

> **Note (2026-02-25)**: These 20 results were originally stored only in `tier2_screen_results.csv` and not merged into `tier2_full_results.csv` when the 157-polytope batch ran later. All 7 top entries above were rerun and confirmed exactly. Now merged into the full CSV (177 total).

**Scoring breakdown** (T2 out of 55): clean h⁰=3 count (0-15), h⁰≥3 abundance (0-10), K3 fibrations (0-6), elliptic fibrations (0-6), D³ diversity (0-5), simplicity bonus for h11_eff≤14 (0-3).

**Decision**: Remaining ~317 Tier 1 candidates need intermediate screening (Tier 1.5) before committing to full T2 analysis.

**Commits**: tier2_screen.py, results/tier2_screen_results.csv

---

## 2026-02-22 — Tier 1 screening: 337 candidates from scan v2 (partial)

**Work done**: Built `tier1_screen.py`. Fast screener (~1s/polytope) that reads scan log, then runs 3 cheap checks per polytope: (1) del Pezzo divisor classification, (2) Swiss cheese structure via Kähler cone tip + 10× hierarchy scaling, (3) GL(Z,4) toric symmetry order. Uses scan's max h⁰ rather than recomputing (fast path).

**Results** (337 candidates from ~60% complete scan v2):
- 190/337 (56%) have Swiss cheese structure
- 257/337 (76%) have ≥3 del Pezzo divisors
- 190/337 have Swiss + h⁰≥3 — immediate pipeline candidates
- Top candidate (pre-T2): h18/poly8 (score 41/55, 7 dP, Swiss cheese τ=12.9)

**Commits**: tier1_screen.py, results/tier1_screen_results.csv

---

## 2026-02-22 — Scan v2: non-favorable polytopes revealed (in progress)

**Work done**: Re-launched `scan_chi6_h0.py` with the B-11 fix (`h11_eff = len(div_basis)`). All 1025 polytopes now processable.

**Status at documentation time**: ~682/1025 lines, h11=21 processing, 414 HITs (h⁰≥3). Still running (PID 393136).

**Interim findings**: Hit rate ~61% (vs 42% in scan v1 which only saw favorable polytopes). Non-favorable polytopes dominate the landscape and contain the strongest candidates.

---

## 2026-02-22 — B-11: c2 mismatch fix + B-02: pipeline cleanup

**B-11 Root cause**: Non-favorable polytopes have `len(divisor_basis()) < h11`. CYTools' `second_chern_class(in_basis=True)` returns a vector sized to the toric divisor basis, not the full $h^{1,1}$. The scan was comparing `len(c2) != h11` and rejecting 705/1025 polytopes.

**Fix**: Use `h11_eff = len(div_basis)` as the working dimension throughout `scan_chi6_h0.py`. The HRR formula and Koszul lattice-point method already operate in the toric basis, so everything is consistent. Non-favorable polytopes are marked `[NF]` in output.

**Verification**: Tested on h11=14,16 polytopes that previously failed — all now process successfully. Example: h11=14 poly 2 (non-favorable, h11_eff=13) shows max h⁰=11.

**B-02**: Removed fabricated `proven_h0_3 = True` from `pipeline_40_152.py`. Replaced with `False` and a comment citing the Koszul disproof (dragon_slayer_40h/40i). Tier 2 score now correctly shows 5/6, total 19/20.

**Commits**: scan_chi6_h0.py, pipeline_40_152.py, BACKLOG.md

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
