# PROCESS LOG — CYTools Project

> Chronological record of investigations, decisions, and issues encountered.
> New entries go at the top. Reference BACKLOG.md items by ID.

---

## 2026-02-23 00:30 — h15/poly61 full pipeline (25/26, τ=14,300) + h16 complete

**Work done (B-23, B-19)**: Full pipeline on h15/poly61. h16 scan complete (5180/5180). h16 screened through T1→T1.5→T2.

### h15/poly61 full pipeline → 25/26, LVS champion

`python pipeline.py --h11 15 --poly 61` → 13s runtime.

| Metric | T2 (probe) | Full Pipeline | Δ |
|--------|-----------|---------------|---|
| Clean h⁰=3 | 103 | **110** | +7% |
| h⁰≥3 | (probe) | **338** | — |
| Max h⁰ | 4 | **4** | same |
| χ=±3 bundles | — | **13,256** | — |

Key result: **Swiss cheese τ = 14,300.0** — 6.5× the previous best (h17/poly8 at τ=2,208). Only loses the dP point (0 del Pezzo divisors → 0/1). Score: **25/26**.

### Updated full pipeline leaderboard

| Polytope | Score | Clean | K3 | Ell | dP | Swiss τ | Title |
|----------|-------|-------|----|-----|----|---------|-------|
| h14/poly2 | 26/26 | **320** | 3 | 3 | 3 | 58.5 | Heterotic champion |
| h16/poly11 | 26/26 | **298** | 3 | 3 | 5 | 150.0 | |
| h17/poly96 | 25/26 | **252** | 2 | 1 | 0 | 252.0 | |
| h17/poly63 | 26/26 | **218** | 5 | 10 | 6 | 84.0 | F-theory champion |
| h17/poly9 | 23/26 | **192** | 1 | 0 | 0 | 72.0 | |
| h18/poly34 | 26/26 | **184** | 4 | 6 | 5 | 0.0 | |
| h17/poly8 | 26/26 | **180** | 3 | 3 | 4 | 2,208 | |
| **h15/poly61** | **25/26** | **110** | 3 | 3 | 0 | **14,300** | **LVS champion** |

### h16 full scan → 5,180/5,180 complete ✅

| Metric | Value |
|--------|-------|
| Polytopes scanned | 5,180 (100%) |
| Hits (h⁰≥3) | 1,811 (35%) |
| Runtime | 52.9 min |
| Throughput | 1.6 poly/s |

### h16 T1 → T1.5 → T2 screening

- **T1**: 30 screened, 17/30 Swiss cheese. Best: h16/poly329 (score=41, max h⁰=15). 374 total T1 entries.
- **T1.5**: 20 screened, 19/20 T2-worthy (17s). 338 total T1.5 entries.
- **T2**: 20 screened, all 20 ★★★ (56s). 36 total T2 entries.

T2 top new performers:
- h19/poly16: T2=45, 69 clean, max h⁰=27, 5 K3 + 6 ell
- h18/poly32: T2=45, 49 clean, max h⁰=30
- h17/poly53: T2=45, 45 clean
- h15/poly94: T2=45, 36 clean, 4 K3 + 4 ell

### Scan coverage

| h11 | Polytopes | Scanned | Coverage |
|-----|-----------|---------|----------|
| 13 | 3 | 3 | 100% |
| 14 | 22 | 22 | 100% |
| 15 | 553 | 553 | 100% |
| 16 | 5,180 | 5,180 | 100% |
| 17 | 38,735 | 100 | 0.26% |

h13–h16 fully covered. h17 (38,735 polytopes, ~3.7 hrs) deferred to Codespace.

---

## 2026-02-22 23:30 — Expanded scan: h15 complete, h16 running, new T2 discovery

**Work done (B-19)**: Built `scan_parallel.py` multiprocessing scanner and expanded the scan beyond the original `limit=100` cap.

### scan_parallel.py — 4× speedup

New multiprocessing scanner using `mp.Pool` with configurable workers. Key design decisions:
- Worker function `_scan_one()` takes serialized vertex lists (CYTools `Polytope` objects aren't picklable)
- `imap_unordered` with `chunksize=4` for load balancing across polytopes of varying complexity
- Resume support via `--resume CSV_PATH` (skips already-scanned `(h11, poly_idx)` pairs)
- Dual output: `.log` (tier1_screen.py compatible) + `.csv` (machine-readable)
- Progress reporting every 50 polytopes with rate and ETA

Performance: **1.0–1.4 poly/s** with 4 workers on a 4-core machine (vs ~0.3 poly/s serial).

### h15 full scan — 553/553 complete ✅

| Metric | Original (limit=100) | Expanded (all 553) |
|--------|---------------------|--------------------|
| Polytopes scanned | 100 | **553** |
| Hits (h⁰≥3) | ~60 | **333** (60%) |
| Runtime | ~2 min | **9.2 min** |

### h16 scan — in progress 🔶

5,180 polytopes at 1.4 poly/s. At 1800/5180 (35%) with 913 hits (51% rate). ETA ~40 min.

### T1 → T1.5 → T2 screening on new h15 candidates

Ran the full screening pipeline on new h15 hits while h16 scan runs:

- **T1**: Top 30 screened → 16/30 have Swiss cheese structure. **h15/poly 127** scores 40 (max h⁰=17, 8 dP divisors)
- **T1.5**: 20 screened → 19/20 T2-worthy (≥3 clean in 300-bundle probe)
- **T2**: 20 screened → **h15/poly 61 has 103 clean bundles** (new #5 overall)

### New discovery: h15/poly 61

Previously invisible (poly index 61 > original limit of 100). Now ranks #5 in the entire T2 leaderboard:

| Rank | Polytope | Clean h⁰=3 | Source |
|------|----------|-----------|--------|
| 1 | h16/poly11 | 255 | Pipeline |
| 2 | h17/poly63 | 198 | Pipeline |
| 3 | h18/poly34 | 189 | Pipeline |
| 4 | h17/poly90 | 148 | T2 |
| **5** | **h15/poly61** | **103** | **NEW — expanded scan** |
| 6 | h14/poly5 | 74 | T2 |

h15/poly 61 has 3 K3 + 3 elliptic fibrations and max h⁰ = 4 (modest). Needs full pipeline run.

**Also notable**: h15/poly 94 (36 clean, 4 K3+4 ell), h15/poly 33 (16 clean, 9 dP — highest dP count).

### Infrastructure
- `.gitignore`: Added `!results/*.log` exception so scan logs are tracked
- Committed `d45fbd8`: scanner + h15 results
- Total scanned: 1,025 → **1,478** polytopes (h15 expanded from 100 to 553)

---

## 2026-02-22 22:00 — Full pipeline on all top 7 candidates: 5× perfect 26/26

**Work done**: Ran `pipeline.py` on the remaining 5 top T2 candidates (h16/poly11, h17/poly96, h18/poly34, h17/poly9, h17/poly8). Combined with the earlier h14/poly2 and h17/poly63 runs, all 7 top candidates are now fully analyzed.

**Full leaderboard** (sorted by clean bundles):

| Polytope | Score | Clean | T2→Pipe Δ | K3 | Ell | dP | Swiss τ |
|----------|-------|-------|-----------|-----|-----|-----|---------|
| h14/poly2 | 26/26 | **320** | +52 | 3 | 3 | 3 | 58.5 |
| h16/poly11 | 26/26 | **298** | +43 | 3 | 3 | 5 | 150.0 |
| h17/poly96 | 25/26 | **252** | +25 | 2 | 1 | 0 | 252.0 |
| h17/poly63 | 26/26 | **218** | +20 | 5 | **10** | **6** | 84.0 |
| h17/poly9 | 23/26 | **192** | +11 | 1 | 0 | 0 | 72.0 |
| h18/poly34 | 26/26 | **184** | −5 | 4 | 6 | 5 | 0.0 |
| h17/poly8 | 26/26 | **180** | +21 | 3 | 3 | 4 | **2208** |

**Key findings**:
- **5 of 7 score 26/26** (perfect). h17/poly96 loses 1 point (no dP). h17/poly9 loses 3 (no ell, no dP).
- **Full pipeline consistently finds more clean bundles** than T2 screen (avg +24, range −5 to +52). The more thorough h³ verification via Serre duality catches bundles the T2 heuristic misses.
- **h16/poly11 is the new #2** — 298 clean, 5 dP, 3 ell. Previously had only 1 ell fibration in T2.
- **h17/poly8 has best LVS structure**: τ=2208 is 37× larger than any other candidate. Extremely strong volume hierarchy.
- **h18/poly34 has τ=0.0** — a degenerate Swiss cheese direction. The flag passes but the LVS hierarchy is absent. May need investigation.
- **h17/poly9 scores lowest (23/26)** despite 192 clean bundles — zero elliptic fibrations and zero dP divisors limit its physics utility.

**Runtime**: 16-18s per candidate (total batch ~85s). All output saved to `results/pipeline_h{h11}_P{poly}_output.txt`.

---

## 2026-02-22 21:00 — Generic pipeline.py + h17/poly63 Full Pipeline: 26/26, 218 clean

**Work done**: Refactored all pipeline code into a single generic `pipeline.py` that takes `--h11` and `--poly` arguments. No more per-candidate custom scripts. All heavy computation imported from `cy_compute.py`. Ran full Stages 1-4 on h17/poly63.

**Architecture change**: `cy_compute.py` is the shared computational core (vectorized lattice points, batch χ, precomputed vertex data). `pipeline.py` is the single entry point:
```
python pipeline.py --h11 14 --poly 2    # champion
python pipeline.py --h11 17 --poly 63   # F-theory champion
python pipeline.py --h11 18 --poly 34   # next candidate
```
Old per-candidate scripts (`pipeline_h14_P2.py`, `pipeline_h13_P1.py`) still work but are superseded.

**h17/poly63 Full Pipeline Results**:
- **26/26 score** — perfect (same as h14/poly2)
- **218 clean bundles**: h⁰=3, h¹=h²=h³=0 (up from 198 in T2 screen)
- 14,458 total χ=±3 bundles searched (max_nonzero=4, max_coeff=3)
- 922 bundles with h⁰≥3 (6.4% of total)
- Max h⁰ = 40
- 1 nef bundle out of 14,458
- 61 distinct D³ values among clean bundles (range [-59, 59])
- Non-favorable: h11=17, h11_eff=13
- SHA-256 fingerprint: 3cc2448f341e6e9a
- Runtime: 25s

**Divisor structure**:
- 6 del Pezzo candidates (e2: dP₄, e5: dP₈, e7: dP₄, e8: dP₆, e9: dP₇, e10: dP₇)
- 1 K3-like divisor (e0: D³=0, c₂·D=36)
- 6 rigid divisors

**Swiss cheese structure**: 1 direction
- e12: τ=84.0, V=853536, τ/V^(2/3)=0.00934

**Fibrations**: 5 K3 + 10 elliptic (up from 6 elliptic in T2 — full pipeline methodology finds more)

**Comparison of the two champions**:

| Metric | h14/poly2 | h17/poly63 | Winner |
|--------|-----------|------------|--------|
| Score | 26/26 | 26/26 | Tie |
| Clean bundles | **320** | 218 | h14/poly2 |
| Max h⁰ | 13 | **40** | h17/poly63 |
| K3 fibrations | 3 | **5** | h17/poly63 |
| Elliptic fibrations | 3 | **10** | h17/poly63 |
| dP divisors | 3 | **6** | h17/poly63 |
| Swiss cheese dirs | **3** | 1 | h14/poly2 |
| h¹¹ (lower=simpler) | **14** | 17 | h14/poly2 |

h14/poly2 = **heterotic champion** (most clean bundles, simplest moduli). h17/poly63 = **F-theory champion** (most fibrations, richest divisor structure).

**Performance**: All screening scripts + pipeline now import from `cy_compute.py`. Speedups:
- pipeline: 271s → 25-30s (10-19×)
- tier2 per polytope: 87s → 7.4s (12×)
- scan per polytope: 8s → 0.6s (13×)
- ~700 lines of duplicated code removed across 5 scripts

**Commits**: `9bc4145` (pipeline_h14_P2 refactor), `6e3da48` (generic pipeline.py + h17/poly63)

---

## 2026-02-22 20:15 — cy_compute refactoring: all scripts accelerated

**Work done**: Created `cy_compute.py` shared computational module. Refactored all 4 screening scripts (`scan_chi6_h0.py`, `tier1_screen.py`, `tier15_screen.py`, `tier2_screen.py`) and `pipeline_h14_P2.py` to import from it.

**Bug found and fixed**: `build_intnum_tensor()` was symmetrizing intersection numbers to all 6 permutations of (i,j,k). CYTools stores sorted-index entries only (i≤j≤k), so the scalar `compute_chi()` sums correctly, but the symmetrized tensor caused 3-6× D³ overcounting. Fixed by removing symmetrization. Verified: all test bundles match scalar vs batch.

**Commits**: `d37e1e1` (cy_compute creation), `761fd34` (screening refactoring + tensor fix)

---

## 2026-02-22 19:30 — h14/poly2 Full Pipeline: 26/26, 320 clean bundles — new champion

**Work done**: Built `pipeline_h14_P2.py`. Full Stages 1-4 of FRAMEWORK.md on h11=14, polytope 2 — the #1 ranked candidate from 177 T2-screened polytopes.

**Bug fixed during development**: `IndexError: index 13 is out of bounds for axis 0 with size 13`. Root cause: non-favorable polytope (h11=14 but h11_eff=13). All 5 instances of `range(h11)` replaced with `range(h11_eff)` where `h11_eff = len(div_basis)`. Same class as Bug #11 (B-11).

**Key results**:
- **26/26 score** — perfect on the expanded 26-point scorecard
- **320 clean bundles**: h⁰=3, h¹=h²=h³=0 (no higher cohomology)
- 14,608 total χ=±3 bundles searched (max_nonzero=4, max_coeff=3)
- 828 bundles with h⁰≥3 (5.7% of total)
- Max h⁰ = 13 (6 bundles, e.g. D = 3·e0 + 3·e4 + 1·e8 + 1·e11)
- 1 nef bundle out of 14,608
- 61 distinct D³ values among clean bundles (range [-63, 63])
- Non-favorable: h11=14, h11_eff=13
- SHA-256 fingerprint: f6c14152f6f3b812
- Runtime: 271s (4.5 min)

**Divisor structure**:
- 3 del Pezzo candidates (e5: dP₄, e9: dP₄, e10: dP₇)
- 2 K3-like divisors (e0: D³=0, c₂·D=36; e2: D³=0, c₂·D=12)
- 6 rigid divisors

**Swiss cheese structure**: 3 directions found
- e9: τ=58.5, τ/V^(2/3)=0.00113 — best LVS candidate
- e8: τ=723.0, τ/V^(2/3)=0.01395
- e6: τ=1487.5, τ/V^(2/3)=0.02835

**Fibrations**: 3 K3 + 3 elliptic (matches T2 for K3; T2 only found 1 elliptic — full pipeline methodology is more thorough)

**Cohomology breakdown** (h⁰≥3 bundles):
- 320 clean (h⁰=3, h³=0) — of which 160 have h¹-h²=0 (truly pristine), 207+89 have h¹-h²=6 (vector-like pairs)
- 74 with h⁰=6, 53 with h⁰=10, 6 with h⁰=11, 3 with h⁰=13

**Comparison with previous champions**:

| Polytope | Score | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell | Swiss |
|----------|-------|------------|-------|--------|-----|-----|-------|
| **h14/poly2** | **26/26** | **320** | **828** | **13** | 3 | 3 | 3 dirs |
| h13/poly1 | 18/20 | 25 | 76 | 6 | 3 | 3 | 1 dir |
| Polytope 40 | 10/20 | 0 | 0 | 2 | 3 | 3 | 1 dir |

h14/poly2 has **12.8× more clean bundles** than h13/poly1 and **2.2× higher max h⁰**. This is the strongest 3-generation Calabi-Yau manifold identified in the project.

**Representative simplest clean bundles**: L = O(±e0), with D³=0 and all higher cohomology vanishing — a single-divisor 3-generation model.

**Next**: Full pipeline on h17/poly63 (#2 priority candidate: T2=45, 198 clean, 5 K3 + 6 elliptic fibrations).

---

## 2026-02-22 18:36 — Merge fix: early T2 (20) + batch T2 (157) → 177 total

**Issue discovered**: The 20 polytopes screened in the early T2 run (15:15) were stored in `tier2_screen_results.csv` but never merged into `tier2_full_results.csv` when the 157-polytope batch ran. This caused 20 real results — including several top candidates — to be missing from the "full" CSV and all downstream documentation. Zero overlap between the two sets.

**Fix**: Merged both CSVs. Reran all 7 top early-T2 candidates to confirm reproducibility — all matched exactly. Backup of early results: `tier2_screen_results_early20_backup.csv`.

**New total**: 177 T2-screened polytopes.

---

## 2026-02-22 17:24 — T2 batch complete: 157/157, new leaders discovered

**Work done**: All 4 Codespace T2 pipes finished (33–41 min each). Pulled results locally, saved to `results/tier2_full_results.csv`. Updated CATALOGUE.md, README.md, FINDINGS.md.

**Key discoveries from the combined 177-polytope T2 results** (157 batch + 20 early):

| Polytope | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell | Note |
|----------|-----|------------|-------|--------|-----|-----|------|
| **h14/poly2** | 41 | **268** | 828 | 13 | 3 | 1 | Most clean bundles. Lowest h¹¹ among top candidates. |
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

## 2026-02-22 17:16 — Repo restructured for open-source

**Work done**: Rewrote README.md, created CATALOGUE.md and CONTRIBUTING.md, updated FINDINGS.md and BACKLOG.md. Archived old README and FINDINGS. Pushed to GitHub.

**Strategic direction**: Open-source pipeline + catalogue. Build the sieve, record what passes, make it contributor-friendly. "Nothing big unless we find the big one."

**Commits**: 8dc9d63

---

## 2026-02-22 15:46 — Tier 1.5 sweep complete: 157 T2-worthy candidates

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

## 2026-02-22 15:15 — Tier 2 deep screening: top 20 from Tier 1

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

> **Note (18:36)**: These 20 results were originally stored only in `tier2_screen_results.csv` and not merged into `tier2_full_results.csv` when the 157-polytope batch ran later. All 7 top entries above were rerun and confirmed exactly. Now merged into the full CSV (177 total).

**Scoring breakdown** (T2 out of 55): clean h⁰=3 count (0-15), h⁰≥3 abundance (0-10), K3 fibrations (0-6), elliptic fibrations (0-6), D³ diversity (0-5), simplicity bonus for h11_eff≤14 (0-3).

**Decision**: Remaining ~317 Tier 1 candidates need intermediate screening (Tier 1.5) before committing to full T2 analysis.

**Commits**: tier2_screen.py, results/tier2_screen_results.csv

---

## 2026-02-22 15:15 — Tier 1 screening: 337 candidates from scan v2 (partial)

**Work done**: Built `tier1_screen.py`. Fast screener (~1s/polytope) that reads scan log, then runs 3 cheap checks per polytope: (1) del Pezzo divisor classification, (2) Swiss cheese structure via Kähler cone tip + 10× hierarchy scaling, (3) GL(Z,4) toric symmetry order. Uses scan's max h⁰ rather than recomputing (fast path).

**Results** (337 candidates from ~60% complete scan v2):
- 190/337 (56%) have Swiss cheese structure
- 257/337 (76%) have ≥3 del Pezzo divisors
- 190/337 have Swiss + h⁰≥3 — immediate pipeline candidates
- Top candidate (pre-T2): h18/poly8 (score 41/55, 7 dP, Swiss cheese τ=12.9)

**Commits**: tier1_screen.py, results/tier1_screen_results.csv

---

## 2026-02-22 15:15 — Scan v2: non-favorable polytopes revealed (in progress)

**Work done**: Re-launched `scan_chi6_h0.py` with the B-11 fix (`h11_eff = len(div_basis)`). All 1025 polytopes now processable.

**Status at documentation time**: ~682/1025 lines, h11=21 processing, 414 HITs (h⁰≥3). Still running (PID 393136).

**Interim findings**: Hit rate ~61% (vs 42% in scan v1 which only saw favorable polytopes). Non-favorable polytopes dominate the landscape and contain the strongest candidates.

---

## 2026-02-22 15:15 — B-11: c2 mismatch fix + B-02: pipeline cleanup

**B-11 Root cause**: Non-favorable polytopes have `len(divisor_basis()) < h11`. CYTools' `second_chern_class(in_basis=True)` returns a vector sized to the toric divisor basis, not the full $h^{1,1}$. The scan was comparing `len(c2) != h11` and rejecting 705/1025 polytopes.

**Fix**: Use `h11_eff = len(div_basis)` as the working dimension throughout `scan_chi6_h0.py`. The HRR formula and Koszul lattice-point method already operate in the toric basis, so everything is consistent. Non-favorable polytopes are marked `[NF]` in output.

**Verification**: Tested on h11=14,16 polytopes that previously failed — all now process successfully. Example: h11=14 poly 2 (non-favorable, h11_eff=13) shows max h⁰=11.

**B-02**: Removed fabricated `proven_h0_3 = True` from `pipeline_40_152.py`. Replaced with `False` and a comment citing the Koszul disproof (dragon_slayer_40h/40i). Tier 2 score now correctly shows 5/6, total 19/20.

**Commits**: scan_chi6_h0.py, pipeline_40_152.py, BACKLOG.md

---

## 2026-02-22 10:28 — h13-P1 Full Pipeline: 18/20, New Best Candidate

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

## 2026-02-22 10:04 — Repo Cleanup + FRAMEWORK.md

**Work done**: 
- Created FRAMEWORK.md: 7-stage theoretical pipeline from CY geometry to phenomenology
- Created refs/refs.bib: 7 key references (KS, Braun et al, Anderson et al, LVS, etc.)
- Archived 12 scratch scripts to archive/
- Moved 13 result files to results/
- Committed at b17bc7d

---

## 2026-02-22 09:54 — B-01: χ=-6 landscape scan — h⁰=3 EXISTS

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

## 2026-02-22 07:43 — Verification complete, h⁰=2 confirmed

**Work done**: Built 7-test verification suite (dragon_slayer_40i.py). Discovered Bug #7 (GLSM linrels ≠ character translations). Confirmed h⁰=2 via 8 character translations. Cross-checked Koszul method against known quintic values (n=-3..7, all match). Updated MATH_SPEC.md.

**Issue encountered**: Test 1 (linear equivalence invariance) initially appeared to FAIL — lattice point counts of 2, 39, 225 for different representatives. Root cause: `glsm_linear_relations()` returns 5 vectors, but only 4 are character translations (dim M = 4). The 5th shifts the origin coordinate and changes the actual divisor class. This is NOT a bug in our computation — it's a subtlety of the GLSM formalism.

**Decision**: h⁰=2 is the definitive answer for all 119 χ=3 line bundles on Polytope 40. No further re-verification needed. Documented as Bug #7 in MATH_SPEC.md.

**Commits**: 72931ed (MATH_SPEC.md), 1a3c382 (verification + Bug #7)

**Next**: Choose between B-01 (scan other polytopes), B-02 (fix pipeline), or B-03 (higher-rank bundles).

---

## 2026-02-22 02:03 — MATH_SPEC.md created

**Work done**: Audited all 8 dragon_slayer scripts (40, 40b-40h) plus the original pipeline. Cataloged every formula, sign convention, index convention, CYTools API contract, and the 6 bugs encountered. Created MATH_SPEC.md as the single source of truth.

**Decision**: All future computation scripts must reference MATH_SPEC.md. Any new bug gets added to the registry immediately.

**Commit**: 72931ed

---

## 2026-02-22 01:54 — h⁰=3 definitively disproven

**Work done**: dragon_slayer_40h.py — Koszul exact sequence + lattice point counting + toric h¹ correction. Scanned all 119 χ=+3 bundles (1-4 divisors, coefficients ±1..3).

**Result**: max h⁰(X, D) = 2. h¹(V, D+K_V) = 0 for ALL bundles (Koszul formula is exact).

**Bugs fixed**: Bug #4 (off-by-one in lattice points, from 40g). Bug #5 (cohomCalg SR limit, from 40e/f).

**Impact**: Pipeline score confirmed at 19/20. The `proven_h0_3 = True` in pipeline_40_152.py is fabricated.

**Commit**: 5e3d727

---

## 2026-02-22 01:24 — Dragon Slayer: pipeline audit

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

## 2026-02-22 01:14 — Ample Champion retraction

**Work done**: Rigorous testing of Z₃×Z₃ action on Ample Champion (h11=2, h21=29, χ=-54). Found pure g₁, g₂ have fixed curves on CY. Full quotient is singular.

**Salvaged**: Diagonal Z₃ acts freely → quotient has χ=-18, not χ=-6. Gets 9 generations, not 3.

**Decision**: Pivot to Polytope 40 (native χ=-6) as the cleaner 3-generation candidate.

**Commit**: dac8132

---

## 2026-02-22 00:29 — Polytope 40 pipeline run

**Work done**: Ran full 20-check pipeline on Polytope 40 (h11=15, h21=18, χ=-6). Scored 20/20.

**Issue**: Score was inflated — check 20 (`proven_h0_3`) was hardcoded True. All other 19 checks are genuine.

**Commit**: ccd69bf

---

## 2026-02-22 00:50 — Ample Champion analysis + fibrations

**Work done**: Analyzed Ample Champion quotient geometry. Computed Polytope 40 fibration structure (3 K3, 3 elliptic).

**Commit**: 58504ec

---

## 2026-02-21 23:01 — Landscape survey

**Work done**: Surveyed h11=2 polytopes for ample χ=3 bundles. Found they exist only at h11=2.

**Commit**: 64eb46b

---

## 2026-02-21 22:06 — Full scan

**Work done**: Scanned 1000 χ=-6 polytopes. Identified Polytope 40 and Polytope 152 as top candidates.

**Commit**: bc133fd

---

## Issue Register

Issues that surfaced during the project, for reference.

| # | Date | Issue | Resolution | Bug # |
|---|------|-------|------------|-------|
| I-01 | 02-22 01:24 | `proven_h0_3` hardcoded True | Disproven; max h⁰=2 | Bug #1 |
| I-02 | 02-22 01:24 | Intersection numbers: toric vs basis coords | Always use `in_basis=True` | Bug #2 |
| I-03 | 02-22 01:24 | Mori pairing: 15-dim D vs 20-dim C | Explicit index mapping via div_basis | Bug #3 |
| I-04 | 02-22 01:54 | Lattice point off-by-one (origin at index 0) | Iterate over ray_indices, not re-indexed array | Bug #4 |
| I-05 | 02-22 01:54 | cohomCalg: 97 SR gens > 64 limit | Check SR count before calling; use Koszul instead | Bug #5 |
| I-06 | 02-22 01:24 | \|χ\|/2=3 conflated with h⁰=3 | Different claims; document clearly | Bug #6 |
| I-07 | 02-22 07:43 | GLSM linrels include origin direction | Filter by origin_component==0 for char translations | Bug #7 |
| I-08 | 02-22 01:14 | Ample Champion Z₃×Z₃ has fixed curves | Full quotient singular; diagonal Z₃ acts freely | — |
| I-09 | 02-22 00:50 | Ample Champion misidentified as P²×P² | Different toric variety; det-3 lattice transform | — |
