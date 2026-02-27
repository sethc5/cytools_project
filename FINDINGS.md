# Findings

Detailed write-ups of key results from the Calabi-Yau landscape scan for
Standard Model–like compactifications. For the quick summary, see
[README.md](README.md).

---

## Executive Summary

**Database**: `v4/cy_landscape_v4.db` — 168,000 polytopes, 2,012 T2-scored.
**Pipeline**: v5.2. **Scoring**: 100-point SM composite (12 components).
**Landscape**: Kreuzer-Skarke χ = −6 polytopes, h¹¹ = 20–40.

### Current Champions

| Rank | ID | Score | Hier | MBD | VolH | Clean | c₂ stab | Tier |
|------|----|-------|------|------|-------|-------|---------|------|
| 1 | **h30/P289** | **89** | 34,318 | 0.88 | 1,737 | 12 | 0% | C |
| 2 | h28/P874 | **87** | 1,150 | 0.95 | 1,656 | 14 | 55% | A |
| 3 | h28/P186 | **87** | 1,147 | 0.94 | 1,725 | 14 | 35% | A |
| 4 | **h27/P22835** | **86** | 1,046 | — | 844 | 16 | 0% | C |
| 5 | **h27/P13954** | **85** | 695 | — | 1,339 | 16 | 25% | — |
| 6 | h28/P187 | 84 | 1,160 | 0.95 | 1,766 | 14 | 55% | A |
| 7 | h27/P1085 | 83 | 731 | — | 1,744 | 32 | 0% | — |
| 8 | h27/P1520 | 83 | 17,287 | — | 362 | 16 | 0% | — |
| 9 | h27/P11889 | 83 | 5,498 | — | 711 | 62 | 0% | — |
| 10 | h27/P22799 | 83 | 1,026 | — | 806 | 16 | 0% | — |

**Tier A** (paper-ready) = high score + triangulation stability.
**Tier B** = perfect stability but limited triangulation sampling.
**Tier C** = high score but fragile geometry.

### Key Numbers

- **168,000** polytopes scanned (50K each at h27, h28, h30)
- **2,012** T2-scored with 100-point SM composite
- **89** = highest score achieved (h30/P289)
- **55%** = best c₂ triangulation stability among top candidates (h28/P874, h28/P187)
- **h27 is a fibration-rich zone**: all 6 T3-analyzed h27 candidates have SM+GUT gauge groups
- h27 50K scan produced 2 new top-5 entries: P22835 (86) and P13954 (85)
- h27–h30 dominates: 8 of top 10 candidates
- P289 remains #1 but h27 cluster provides multiple SM-compatible alternatives

---

## 1. Pipeline and Scoring Evolution

### 1.1 v5 Scoring System (current)

100-point composite, 12 components:

| Component | Max | What it measures |
|-----------|----:|------------------|
| yukawa_hierarchy | 27 | Eigenvalue spread of Yukawa texture matrix |
| yukawa_rank | 15 | Number of independent Yukawa eigenvalues ≥ 3 |
| clean_bundles | 10 | log₂-scaled count of h⁰=3, h¹=h²=h³=0 bundles |
| lvs_quality | 10 | τ/V^{2/3} grading for Large Volume Scenario |
| lvs_binary | 5 | Swiss cheese structure exists (yes/no) |
| vol_hierarchy | 5 | Big/small divisor volume ratio |
| mori_blowdown | 5 | Fraction of Mori rays with dP contractions |
| tadpole_ok | 5 | \|χ/24\| ≤ 20 |
| d3_diversity | 5 | Number of distinct D³ values among clean bundles |
| clean_depth | 5 | First clean bundle found early in census |
| clean_rate | 5 | n_clean / n_bundles_checked |
| rank_sweet_spot | 3 | Yukawa rank in 140–159 range |
| **Total** | **100** | |

### 1.2 Changes from v4 → v5

| Change | Old (v4.1) | New (v5) | Rationale |
|--------|-----------|----------|-----------|
| fibration_sm | 3 pts | **removed** | Only 3 of 19K polytopes had SM gauge group — 3 pts permanently stranded |
| rank_sweet_spot | — | **3 pts (new)** | Yukawa rank 140–159 is the SM sweet spot for h11_eff=18–22 |
| mori_blowdown | 5 (binary) | **5 (graded)** | Fraction-based: ≥0.9→5, ≥0.7→4, etc. |
| yukawa_rank fallback | falsy `or` | **explicit None check** | Bug fix: texture_rank=0 was falling through to κ triple count, inflating 194 polytopes by +10 to +18 |

### 1.3 Coverage expansion (v5.1–v5.2)

**v5.1**: CYTools `fetch_polytopes()` has a hidden `limit=1000` default.
All prior scans retrieved only the first 1,000 polytopes per h¹¹ from the
KS web server. Actual chi=−6 populations: **50,000+** per h¹¹. Fixed with
`--limit N` CLI argument.

**v5.2**: MONOTONIC_MAX score drift bug. When rescanning existing polytopes,
`MONOTONIC_MAX` columns (n_clean, yukawa_rank, etc.) correctly preserve the
higher of old vs new values, but sm_score was computed from the T2 worker's
local data and unconditionally overwritten. Fixed with post-upsert rescore.

---

## 2. The h28 Champion Cluster

### 2.1 Geometry

The three h28 champions are **genuinely distinct polytopes** but closely
related through single-vertex operations:

| Polytope | Points | Vertices | h11_eff | gap | Vertex hash |
|----------|--------|----------|---------|-----|-------------|
| P186 | 29 | 10 | 21 | 7 | `2bfa85a7` |
| P187 | 31 | 10 | 22 | 6 | `50725757` |
| P874 | 30 | 11 | 22 | 6 | `678a4b08` |

**Vertex relationships:**
- **P186 ↔ P187**: Share 9 of 10 vertices. Differ by one substitution:
  P186 has `[0,−3,−3,−2]`, P187 has `[1,−2,−2,−2]`.
- **P186 → P874**: P874 contains all 10 of P186's vertices plus one
  additional vertex `[1,−1,−1,−1]`.

The h28 cluster is a **connected family in the KS polytope graph** — the
score-87 region is a localized island in polytope space.

### 2.2 Intersection ring fingerprints

| Champion | κ entries | κ sum | κ range | κ hash |
|----------|-----------|-------|---------|--------|
| P186 | 271 | −6 | [−179, 57] | `e4457720` |
| P187 | 296 | −6 | [−161, 51] | `ad6cab0a` |
| P874 | 291 | −6 | [−170, 54] | `f48a7149` |

All have κ_sum = −6 = χ (consistency check). κ values are dominated by
small integers (|κ|=1,2,3 account for >70% of entries).

### 2.3 Divisor structure

All champions share a common architecture:

| Feature | P186 | P187 | P874 |
|---------|------|------|------|
| D0 (c₂·D) | −122 | −134 | −128 |
| K3-like (c₂·D ≥ 24) | 3 | 2 | 2 |
| dP candidates (12 ≤ c₂·D < 24) | 2 | 2 | 4 |
| Rigid (c₂·D < 0) | 7 | 6 | 7 |

### 2.4 Why P187 scores lower (84 vs 87)

P187's yukawa_rank of 164 falls *above* the 140–159 sweet spot, missing the
rank_sweet_spot bonus (3 pts). Its yukawa_hierarchy of 1,160 puts it in the
same tier as P874 (1,150) and P186 (1,147). The grading correctly
discriminates within the former "tied at 84" cluster from v4.1.

---

## 3. Triangulation Stability (T3 Deep Analysis)

**Method**: For each of 20 candidates, generate up to 50 random FRST
triangulations. Compute c₂ and κ hashes. Report fraction of 20 triangulations
sharing the modal hash.

### 3.1 Full results

| # | Candidate | Score | Hier | c₂ stab | κ stab | Inst | K3 | Ell | Tris |
|---|-----------|-------|------|---------|--------|------|-----|-----|------|
| 1 | h28/P874 | **87** | 1,150 | **0.50** | **0.50** | Y | 1 | 0 | 20 |
| 2 | h28/P186 | **87** | 1,147 | 0.30 | 0.30 | Y | 1 | 0 | 20 |
| 3 | h30/P289 | **86** | 34,318 | 0.00 | 0.00 | Y | 3 | 1 | 20 |
| 4 | h28/P187 | 84 | 1,160 | **0.55** | **0.55** | Y | 1 | 0 | 20 |
| 5 | h25/P934 | 81 | 1,666 | 0.25 | 0.25 | Y | 1 | 0 | 20 |
| 6 | h20/P903 | 81 | 510 | 0.00 | 0.00 | Y | 1 | 0 | 20 |
| 7 | h32/P94 | 80 | 2,759 | **1.00** | **1.00** | N | 3 | 1 | 6 |
| 8 | h25/P411 | 80 | 1,597 | 0.05 | 0.05 | N | 4 | 4 | 20 |
| 9 | h32/P42 | 79 | 1,022 | **1.00** | **1.00** | Y | 3 | 1 | 4 |
| 10 | h27/P219 | 79 | 901 | **0.55** | **0.55** | Y | 1 | 0 | 20 |
| 11 | h23/P283 | 79 | 2,821 | 0.20 | 0.20 | Y | 1 | 0 | 5 |
| 12 | h21/P496 | 79 | 49,186 | 0.00 | 0.00 | Y | 3 | 1 | 20 |
| 13 | h26/P305 | 79 | 2,991 | 0.00 | 0.00 | Y | 3 | 1 | 20 |
| 14 | h28/P190 | 78 | 201 | 0.20 | 0.20 | Y | 1 | 0 | 20 |
| 15 | h21/P55 | 78 | 608 | 0.15 | 0.15 | N | 1 | 0 | 20 |
| 16 | h28/P188 | 78 | 214 | 0.00 | 0.00 | Y | 1 | 0 | 20 |
| 17 | h24/P479 | 78 | 8,449 | 0.00 | 0.00 | N | 2 | 1 | 20 |
| 18 | h24/P88 | 77 | 2,256 | 0.30 | 0.30 | N | 2 | 1 | 20 |
| 19 | h28/P45 | 77 | 198 | 0.10 | 0.10 | Y | 1 | 0 | 20 |
| 20 | h28/P247 | 77 | 2,340 | 0.00 | 0.00 | Y | 2 | 1 | 20 |

### 3.2 Key findings

1. **No SM or GUT fibrations** in any of the 20 candidates. All
   K3/elliptic fibrations produce non-SM gauge groups.

2. **Stability is bimodal:**
   - Robust (c₂ stab ≥ 0.50): h32/P94, h32/P42, h28/P187, h27/P219, h28/P874
   - Moderate (0.10–0.30): h28/P186, h24/P88, h25/P934, h23/P283, h28/P190, h28/P45
   - Fragile (0.00–0.05): h30/P289, h20/P903, h21/P496, h26/P305, h28/P188, h28/P247, h24/P479, h25/P411

3. **Score and stability are weakly correlated.** h28/P874 (87, 50% stable)
   vs h30/P289 (86, 0% stable). Scoring captures average-case quality;
   stability measures triangulation robustness — different axes.

4. **High hierarchy ≠ stability.** h21/P496 (hier=49,186) and h30/P289
   (hier=34,318) are both 0% stable. Their extreme Yukawa eigenvalue
   spreads are triangulation-dependent artifacts.

### 3.3 Revised champion tiers

| Tier | Candidates | Score | c₂ stab | Assessment |
|------|-----------|-------|---------|------------|
| **A — Paper-ready** | h28/P874 | 87 | 50% | Best overall |
| | h28/P187 | 84 | 55% | Most stable well-sampled |
| | h28/P186 | 87 | 30% | Co-champion |
| **B — Strong** | h32/P94 | 80 | 100% | Perfect stability, only 6 tris |
| | h32/P42 | 79 | 100% | Perfect stability, only 4 tris |
| | h27/P219 | 79 | 55% | Strong MBD (0.97) |
| **C — Score-driven** | h30/P289 | 86 | 0% | Elite hierarchy but fragile |
| | h25/P934 | 81 | 25% | Moderate on both axes |
| | h20/P903 | 81 | 0% | Bundle abundance, fragile |

---

## 4. Deep Coverage Scan — h28 at 50K

**Pipeline**: v5.1 `--scan --h11 28 --limit 50000 -w 12`.
**Runtime**: 13.5 min on Hetzner (16-core, 12 workers).

### 4.1 Motivation

Prior scans retrieved only the first 1,000 of ~50,000+ polytopes per h¹¹
(CYTools' hidden `limit=1000` default). KS server returns polytopes in
deterministic order sorted by lattice point count. Were we missing champions
deeper in the database?

### 4.2 Results

| Stage | Count | Rate |
|-------|------:|------|
| Fetched | 50,000 | — |
| T0 pass | 484 | 1.0% of total |
| T1 pass → T2 | 164 | 33.9% of T0 |
| T2 scored | 164 | — |
| From first 1K | 95 | — |
| From new 49K | 69 | — |

### 4.3 First-1K bias is mild

**Top new polytopes (idx ≥ 1000):**

| ID | Score | n_clean | yuk_hier | vol_hier |
|----------|-------|---------|----------|----------|
| h28/P1040 | 80 | 50 | 3,859 | 2,343 |
| h28/P8319 | 75 | 16 | 397 | 2,858 |
| h28/P20607 | 75 | 32 | 149 | 3,006 |
| h28/P1418 | 73 | 24 | 151 | 1,334 |
| h28/P33827 | 72 | 20 | 120 | 1,001 |

The best new polytope (P1040, score=80) has outstanding clean bundle
abundance (n_clean=50) and Yukawa hierarchy (3,859), but falls 7 points
short of the champions (87). The coverage expansion from 2% → 100%
confirms champion selection is **robust, not an artifact of positional bias**.

Notable: P1105 has **100 clean bundles** (a record) but only scores 70
due to minimal Yukawa hierarchy (12×) — reinforcing that **Yukawa texture
quality dominates clean bundle quantity**.

### 4.4 Score distribution

| Bracket | First 1K | New 49K | Total |
|---------|----------|---------|-------|
| 80+ | 3 | 1 | 4 |
| 70–79 | 16 | 12 | 28 |
| 60–69 | 48 | 25 | 73 |
| 50–59 | 14 | 12 | 26 |
| < 50 | 14 | 19 | 33 |

---

## 5. Landscape Trends

### 5.1 Fertile window (v5, 21K polytopes at 1K/bucket)

| h¹¹ | Total | Scored | T2% | Max | Avg | Avg hier |
|-----|-------|--------|-----|-----|-----|----------|
| 20 | 1,000 | 190 | 19.0% | 80 | 56.2 | 137 |
| 21 | 1,000 | 228 | 22.8% | 79 | 58.2 | 378 |
| 22 | 1,000 | 281 | 28.1% | 75 | 59.5 | 201 |
| 23 | 1,000 | 235 | 23.5% | 79 | 57.9 | 237 |
| 24 | 1,000 | 184 | 18.4% | 78 | 57.6 | 345 |
| 25 | 1,000 | 138 | 13.8% | 81 | 55.5 | 303 |
| 26 | 1,000 | 113 | 11.3% | 79 | 52.3 | 320 |
| 27 | 1,000 | 63 | 6.3% | 79 | 52.0 | 211 |
| 28 | 1,000 | 95 | 9.5% | **87** | 54.2 | 418 |
| 29 | 1,000 | 39 | 3.9% | 76 | 51.5 | 298 |
| 30 | 1,000 | 56 | 5.6% | **86** | 51.6 | 814 |
| 31 | 1,000 | 27 | 2.7% | 71 | 47.4 | 106 |
| 32 | 1,000 | 41 | 4.1% | 80 | 54.6 | 420 |
| 33 | 1,000 | 7 | 0.7% | 67 | 44.9 | 44 |
| 34 | 1,000 | 15 | 1.5% | 72 | 58.9 | 591 |
| 35 | 1,000 | 3 | 0.3% | 62 | 57.0 | 202 |
| 36+ | 5,000 | 3 | <0.1% | 49 | — | — |

**Key findings:**

1. **The fertile window is h20–35**, barren at h37+. Sweet spot for peak
   quality: h25–30. Sweet spot for yield: h20–24.

2. **h28 is the champion tier**: exceptional peak (87) with reasonable T2
   yield (9.5%). Outperforms even h22–25 on peak despite 3× lower yield.

3. **h32 has anomalously high T1→T2 pass rates** (76%), meaning survivors
   at high h¹¹ are disproportionately good.

### 5.2 Score distribution (v5, n=1,718)

| Threshold | Count | % |
|-----------|-------|---|
| ≥ 85 | 3 | 0.2% |
| ≥ 80 | 8 | 0.5% |
| ≥ 75 | 45 | 2.6% |
| ≥ 70 | 151 | 8.8% |
| ≥ 60 | 878 | 51.1% |
| Mean | — | 56.3 |

### 5.3 What separates 79 from 87

| Property | Score=87 (n=2) | Score=79 (n=7) | Score=70 (n=28) |
|----------|----------------|----------------|-----------------|
| avg eff | 21.5 | 19.3 | 18.8 |
| avg yuk_h | 1,149 | 2,717 | 1,326 |
| avg vol_h | 1,691 | 762 | 1,575 |
| blowdown frac | 0.945 | 0.721 | 0.856 |

The leap to 87 requires: higher h11_eff (21+), near-perfect Mori blowdown
(94%+), and yukawa_rank in the 140–159 sweet spot. Interestingly, score-79
polytopes have *higher* average hierarchy — the 87s trade raw hierarchy for
geometric consistency across multiple components.

### 5.4 Structural universals

- **Every polytope in the database has χ = −6** (by construction: h¹¹ range
  22–40 in the KS database produces only χ = −6).
- **All T2-scored polytopes are swiss_cheese volume form.**
- **Yukawa hierarchy and LVS quality are orthogonal** (Pearson r ≈ 0) —
  independent axes of SM quality, not redundant.
- **n_dp anti-correlates with score**: fewer del Pezzo divisors → higher SM
  scores. Elite polytopes average n_dp=5 vs population 6.5.
- **volume_hierarchy is a threshold feature**: near-zero correlation with
  score across the population, but all score-84+ polytopes have vol_h > 1,600.

---

## 6. h30/P289 — The Cautionary Champion

h30/P289 deserves special discussion. It has the **highest yukawa_hierarchy
in the database** (34,318×, compared to ~1,150 for the h28 champions) and
an elite LVS score (0.0018). Under v5 scoring it reaches 86.

But T3 deep analysis reveals **0% triangulation stability** — its c₂ hash
changes with every random triangulation tested. Its spectacular Yukawa
eigenvalue spread is a property of CYTools' default placing triangulation,
not an intrinsic feature of the Calabi-Yau manifold.

**Implication**: Score alone cannot identify paper-ready candidates.
Triangulation stability is the missing discriminator. h30/P289 is
scientifically interesting but requires triangulation-specific caveats
that the h28 cluster does not need.

---

## 7. Earlier Pipeline Results (h13–h19)

Sections 7–15 document findings from the earlier pipeline (v1–v3) at
h¹¹ = 13–19, using a different 26-point scoring system. These used the
old `fetch_polytopes` without the chi=−6 filter and scanned smaller
populations. The candidates and findings remain valid but the scoring
is not directly comparable to the v5 100-point system above.

### 7.1 h13/poly1 — Benchmark Candidate (Pipeline Score: 18/20)

**Date**: 2026-02-23. **Script**: [pipeline_h13_P1.py](pipeline_h13_P1.py).

The original benchmark. Smallest h¹¹ in the landscape, completely clean
line bundles. Superseded in all metrics by h14/poly2 (320 clean, 26/26)
but remains the standard test polytope.

**Geometry:**
- h¹¹ = 13, h²¹ = 16, χ = −6 (native 3-generation, no quotient needed)
- 18 toric coordinates, 17 rays, non-favorable (h¹¹_eff = 13)
- 11,054 total χ = ±3 bundles, **25 completely clean** (h⁰=3, h¹=h²=h³=0)
- Swiss cheese: τ = 10.0, V = 308,352, τ/V^{2/3} = 0.0022
- 3 del Pezzo (dP₄, dP₆, dP₄), 1 K3-like

### 7.2 h17/poly25 — Triple-Threat Champion (26/26, 170 clean, 15 elliptic)

**Date**: 2026-02-23.

New record holder for elliptic fibrations — **15 elliptic fibrations**.
Also 6 K3 fibrations. Combined with Swiss cheese (τ=56) and 170 clean
bundles — the only candidate excelling at heterotic, F-theory, AND LVS.

| Metric | h17/P25 | h16/P63 | h17/P8 | h16/P11 |
|--------|---------|---------|--------|---------|
| Score | 26/26 | 26/26 | 26/26 | 26/26 |
| Clean | 170 | 78 | 180 | **298** |
| Ell fib | **15** | 6 | 3 | 3 |
| K3 fib | **6** | 4 | 3 | 3 |
| Swiss τ | 56 | **836** | 2,208 | 150 |
| Best for | F-theory | Balanced | LVS | Heterotic |

### 7.3 h14/poly2 — Heterotic Champion (26/26, 320 clean)

**Date**: 2026-02-22.

Most clean h⁰ = 3 bundles of any polytope analyzed. Lowest h¹¹ (14) among
top candidates.

- **320 clean h⁰ = 3 line bundles** (all-time record at time of analysis)
- 3 K3 fibrations, 3 elliptic fibrations, 3 Swiss cheese directions
- 61 distinct D³ values

### 7.4 h15/poly61 — LVS Champion (25/26, τ = 14,300)

**Date**: 2026-02-22.

Discovered through scan expansion beyond limit=100. **Best Large Volume
Scenario candidate by 6.5×** — Swiss cheese τ = 14,300 vs previous best
2,208 (h17/poly8).

- 110 completely clean bundles, 3 K3 + 3 elliptic fibrations
- Only weakness: 0 del Pezzo divisors (−1 point)

### 7.5 Other notable candidates

| ID | Score | Clean | τ | Ell | Note |
|----|-------|-------|-----|-----|------|
| h17/poly63 | 26/26 | 218 | 84 | **10** | Former F-theory champion |
| h16/poly63 | 26/26 | 78 | 836 | 6 | Triple-threat #2 |
| h16/poly53 | 23/26 | 300 | — | 10 | No Swiss cheese |
| h17/poly96 | 25/26 | 227 | — | 1 | Record max h⁰ = 65 |
| h15/poly40 | — | 0 | 4 | — | Proven dead end (max h⁰=2) |

### 7.6 Complete T2=45 survey (37 candidates)

All 37 polytopes scoring T2=45 (maximum) analyzed with full 26-point pipeline.
19 scored 26/26 (perfect), 5 scored 25/26, 10 scored 23/26 (all missing Swiss
cheese).

**Records:**
- Most clean bundles (any score): h17/poly53 — 418
- Most clean (26/26): h15/poly94 — 380
- Best τ: h15/poly61 — 14,300
- Most elliptic fibrations: h17/poly25, h17/poly45 — 15 each

---

## 8. h17 Automated Landscape Scan — 87 Perfect-Score Polytopes

**Date**: 2026-02-25. **Script**: `auto_scan.py --h11 17 --skip-t025 --top 200 -w 3`.

The h17 landscape (h¹¹=17, h²¹=20) is spectacularly rich — **87 polytopes
achieve a perfect 26/26 score**, more than 4× the combined total from
h11≤16. Every analyzed polytope (193/193) contains the SM gauge group.

### Key results

| Metric | Value |
|--------|-------|
| Polytopes scanned | 38,735 |
| T0.25 passes | 10,624 (27.4%) |
| Perfect 26/26 | **87** |
| SM gauge (SU₃×SU₂×U₁) | 193/193 = **100%** |
| SU(5) GUT | 166/193 = 86% |
| E₇ or E₈ factors | 46/193 = 24% |

### Category champions

| Category | Polytope | Clean | Ell | τ | Gauge |
|----------|----------|-------|-----|-----|-------|
| Triple-threat | **P767** | 59 | 10 | 1.5 | su(2)×su(4)×su(2)×su(3)×su(6) |
| F-theory GUT | **P695** | 22 | 15 | 54 | su(2)×su(4)×su(2)×su(3)×su(6) |
| LVS | **P340** | 13 | 1 | 8,608 | su(7)×su(6) |
| Heterotic | **P767** | 59 | 10 | 1.5 | (same as triple-threat) |
| LVS + F-theory | **P2338** | 25 | 11 | 3,750 | su(3)×su(5)×su(6) |
| Balanced | **P860** | 31 | 6 | 1,139 | su(4)×su(3)×su(4)×su(3) |

---

## 9. Automorphism Group Scan — Symmetry vs Three-Generation Tension

**Date**: 2026-02-26.

### Key finding

Higher polytope symmetry anti-correlates with h⁰ diversity:

| |Aut| | max h⁰ | max clean | Interpretation |
|:-----:|:-------:|:---------:|------------|
| 12 (D₆) | 1 | 0 | Dead for line bundles |
| 8 | 3 | 4 | Marginal |
| 4 | 13 | 40 | Weak |
| 2 (Z₂) | 17 | 192 | Best with symmetry |
| 1 | 26+ | 524+ | Unconstrained |

**No D₆, A₄, or larger flavor symmetries exist** among viable 3-generation
candidates. Z₂ is the realistic maximum for combining symmetry with rich
bundle structure.

### Z₂ acts trivially on generations (P329)

For h16/P329 (26/26, 228 clean, |Aut|=2), the Z₂ involution was analyzed on
all 11 fixed clean bundles. **Every fixed bundle has Tr(σ*)=3, giving a
trivial 3+0 split.** The Z₂ is too "mild" — a coordinate swap that commutes
with the section monomial structure.

**The SM's three generations are not explained by polytope automorphisms.**

---

## 10. AGLP Line Bundle Sum Search — No Solutions at High Picard Rank

**Date**: 2026-02-23.

Searched for rank-5 line bundle sums V = L₁⊕…⊕L₅ satisfying heterotic SU(5)
GUT constraints on h14/P2 and h16/P329.

| Manifold | Clean bundles | h¹¹_eff | 5-sets c₁=0 |
|----------|:---:|:---:|:---:|
| h14/P2 | 268 | 13 | **0** |
| h16/P329 | 220 | 14 | **0** |

**Zero solutions.** The h⁰=3 constraint kills ~98% of candidate bundles,
leaving a subset too sparse for cancellation in a 13–14 dimensional lattice.
AGLP in the literature works at h¹¹=2–5. At h¹¹_eff ≥ 13, fundamentally
different algorithms are needed (monad/extension sequences, MCMC, direct
lattice constraint solving).

---

## 11. Database Landscape Analysis — The Gap Variable

**Date**: 2026-02-27. **Database**: 74,823 polytopes (h¹¹ = 13–19).

### The gap predictor

gap = h¹¹ − h¹¹_eff measures redundant divisor count. From unbiased
pre-pipeline_v2 data only (N=496):

| gap | N | Hit rate | Avg clean |
|:---:|:-:|:--------:|:---------:|
| 0 | 231 | 97.0% | 12.6 |
| 1 | 95 | 97.9% | 15.2 |
| 2 | 99 | 100% | 20.4 |
| 3 | 36 | 100% | 20.7 |
| 4 | 24 | 100% | 27.0 |
| 5+ | 11 | 100% | 65.2 |

Gap ≥ 2: 170/170 = 100% hit rate. Gap is an **efficiency knob** (prioritize
richer targets), not a quality gate (almost nothing fails regardless).

### Other empirical findings

- **Non-favorable polytopes dominate**: 9 of 10 all-time best are NF
- **h¹¹_eff = 13 is the sweet spot**: enough complexity for bundles, not too much for Kähler cone
- **Swiss cheese is NOT predictive** for T1 success (89% vs 86%)
- **n_chi3 ≥ 10,000** → avg 92.4 clean (phase transition)
- **Clean increases with h¹¹ at fixed eff**: more embedding room is pure upside

---

## 12. GL=12 / D₆ Polytope — Picard-Fuchs and Yukawa Study

**Date**: 2026-02-23.

The polytope at h17/P37 has the **largest lattice automorphism group**
(|GL(Δ)| = 12, D₆). This symmetry reduces 20 complex structure moduli to
6 invariant deformations.

### Results

- **GKZ system**: A-matrix 5×23, D₆ orbit compression → 6 Mori coordinates
- **Closed-form period**: 501 exact coefficients (c₃=6, c₄=72, c₅=540)
- **D₆-invariant Yukawa**: 26 non-zero entries from 283 raw κ, two-sector
  structure
- **1-parameter ODE**: ₃F₂([1/3,2/3,1];[1,1];27t) — period of mirror cubic
  in ℙ² (AESZ #1)
- **6 box operators** □₁–□₆ in Mori θ-coordinates, all 9,366 GKZ checks pass

**However**: max h⁰ = 1 across all 1,720 χ=−6 bundles. The D₆ polytope is
**dead for line bundle phenomenology**.

---

## 13. Pipeline v2 Conflict Audit & DB Upsert Fix

**Date**: 2026-02-24.

After rescanning h13–h16 with pipeline_v2, 216 polytopes showed data
conflicts (old n_clean > 0, new scan screened at T0).

**Root causes:**
1. EFF_MAX screening (59 polytopes) — correctly skipped
2. **DB upsert clobber bug** (152 polytopes) — `max_h0=0` overwrote correct
   old values of 3–4
3. AUT_MAX screening (5 polytopes) — correctly skipped

**Fix**: MONOTONIC_MAX on `upsert_polytope` — metric columns now use
`MAX(COALESCE(existing, 0), new)`. Screening can never clobber deeper
analysis results. 1,173 corrupted values restored.

---

## 14. Ample Champion (h11=2, h21=29, χ=−54) — Quotient Fails

Attempted Z₃×Z₃ quotient for χ = −54/9 = −6. Pure generators have fixed
curves → orbifold singularities. Diagonal Z₃ acts freely → χ = −18 (9 gen).
The full Z₃×Z₃ quotient is singular; orbifold resolution changes χ.

---

## 15. Self-Mirror Polytope (h11=20, h21=20, χ=0)

Not a 3-generation candidate (χ=0). Self-mirror CY with 3 K3 + 3 elliptic
fibrations. Parked as a curiosity for potential F-theory path (generations
from brane geometry, not χ).
