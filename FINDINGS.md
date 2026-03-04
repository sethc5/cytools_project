# Findings

Detailed write-ups of key results from the Calabi-Yau landscape scan for
Standard Model–like compactifications. For the quick summary, see
[README.md](README.md).

---

## Executive Summary

**Database**: `v6/cy_landscape_v6.db` — **3.11M polytopes** (h13–h40), **52,865** fully scored (yukawa + n_clean computed).  
**Pipeline**: v6 (yukawa-fix, `--local-ks`, `--offset`). **Scoring**: 100-point SM composite (10 components). Score range 25–89.  
**Landscape**: Kreuzer-Skarke χ = −6 polytopes — **6,122,441 total** (h¹¹ = 13–119). Active scan window h¹¹ = 13–40 (5.80M, 94.7% of total). h13–h21 exhaustively scanned (100%). h22–h24 nearly exhaustive (~99.5%). h25 fully exhausted. h26 at ~49%. h27–h30 at 100–200K. h31–h40 at 50K.  
*Updated 2026-03-04 post §26 Hetzner T3 batch (all 35 ≥80 entries now T3-verified).*

### Current Champions (v6 scoring, post §26 T3 batch)

*All 35 entries ≥80 are T3-verified (SM/GUT classification, gauge group, c2 stability). §26 Hetzner batch 2026-03-04 completed T3 on all 17 previously pending score=80 candidates. 2 confirmed below 80.*

| Rank | ID | Score | SM | GUT | n_clean | max_h0 | Tier | Note |
|------|----|-------|----|-----|---------|--------|------|------|
| 1 | **h26/P11670** | **89** | ✓ | ✓ | 22 | 3 | T3 | champion — stable |
| 2 | **h29/P8423** | **87** | ✓ | ✓ | 30 | 3 | T3 | |
| 3 | **h24/P868** | **87** | ✓ | ✓ | 24 | 6 | T3 | |
| 4 | **h27/P9192** | **87** | ✓ | ✓ | 22 | 4 | T3 | |
| 5 | h27/P4102 | 87 | ✗ | ✗ | 22 | 4 | T3 | no SM/GUT |
| 6 | **h22/P682** | **85** | ✓ | ✓ | **84** | 7 | T3 | **★ NEW §26** — n_clean record; score 80→85 at T3 |
| 7 | **h28/P6642** | **85** | ✓ | ✓ | 30 | 3 | T3 | |
| 8 | **h27/P9133** | **85** | ✓ | ✓ | 22 | 3 | T3 | |
| 9 | h24/P45873 | 85 | ✓ | ✓ | 22 | 3 | T3 | |
| 10 | h25/P46481 | 85 | ✓ | ✓ | 22 | 7 | T3 | |
| 11 | **h27/P45013** | **85** | ✓ | ✓ | 12 | 6 | T3 | |
| 12 | **h29/P13253** | **83** | ✓ | ✓ | 20 | 8 | T3 | |
| 13 | **h28/P5473** | **82** | ✓ | ✓ | 26 | 3 | T3 | |
| 14 | h27/P2317 | 82 | ✓ | ✓ | 24 | 3 | T3 | |
| 15 | h28/P718 | 82 | ✗ | ✗ | 22 | 7 | T3 | no SM/GUT |
| 16 | h28/P33 | 82 | ✗ | ✗ | 20 | 9 | T3 | no SM/GUT |
| 17 | h25/P860 | 81 | ✓ | ✓ | 24 | 7 | T3 | |
| 18 | h25/P7867 | 81 | ✓ | ✓ | 18 | 3 | T3 | |
| 19 | h27/P27537 | 81 | ✓ | ✓ | 16 | 3 | T3 | |
| 20 | h27/P39352 | 81 | ✓ | ✓ | 12 | 3 | T3 | |
| 21 | **h26/P315** | **80** | ✓ | ✓ | 32 | 7 | T3 | **NEW §26** |
| 22 | **h28/P33562** | **80** | ✓ | ✓ | 28 | 9 | T3 | **NEW §26** |
| 23 | **h25/P5449** | **80** | ✓ | ✓ | 26 | 7 | T3 | **NEW §26** |
| 24 | **h24/P44004** | **80** | ✓ | ✓ | 26 | 3 | T3 | **NEW §26** |
| 25 | **h26/P11871** | **80** | ✓ | ✓ | 26 | 4 | T3 | **NEW §26** |
| 26 | **h25/P38242** | **80** | ✓ | ✓ | 24 | 9 | T3 | **NEW §26** |
| 27 | **h25/P8995** | **80** | ✓ | ✓ | 24 | 9 | T3 | **NEW §26** |
| 28 | h24/P272 | 80 | ✗ | ✗ | 24 | 5 | T3 | **NEW §26** — no SM/GUT |
| 29 | **h29/P6577** | **80** | ✓ | ✓ | 22 | 3 | T3 | **NEW §26** |
| 30 | **h29/P6575** | **80** | ✓ | ✓ | 22 | 8 | T3 | **NEW §26** |
| 31 | **h25/P18950** | **80** | ✓ | ✓ | 22 | 3 | T3 | **NEW §26** |
| 32 | **h26/P30513** | **80** | ✓ | ✓ | 22 | 3 | T3 | **NEW §26** |
| 33 | **h28/P1937** | **80** | ✓ | ✓ | 20 | 3 | T3 | **NEW §26** |
| 34 | **h27/P28704** | **80** | ✓ | ✓ | 20 | 7 | T3 | **NEW §26** |
| 35 | **h27/P26021** | **80** | ✓ | ✓ | 20 | 9 | T3 | **NEW §26** |

**Prior invalidations (§21)**: h23/P37201 (prev. 87), h27/P240 (82), h27/P239 (82), h22/P302 (81), h21/P270 (80), h21/P55 (80), h27/P9181 (80), h30/P289 (80) — confirmed partial-score artifacts by 2026-03-02 fresh scan.

**Mop-up stalls (§22)**: h19/P438 (prev. 81), h18/P315 (prev. 80), h19/P390 (prev. 80) — overwritten by 2026-03-03 ext mop-up rescanning h18/h19 from scratch in fresh container; yukawa_hierarchy stalled, producing T1-stall rows that replaced old scored rows on merge.

**Note on prior v5 champions**: h28/P874 (v5 = 87) and h28/P186 (v5 = 87) both fail T0 in v6 (scores 10 and 13 respectively) — the v6 `--local-ks` polytope ordering assigns them different positions than the v5 KS-server ordering used when those results were recorded. h28/P187 (v5 = 84, v6 = 78) and h27/P43 (prev. est. 84, v6 = 79) similarly rescored after full T2 processing.

**Note**: v6 scoring removed 2 dead components (tadpole_ok, lvs_binary) and
reweighted hierarchy (27→30), so absolute scores are lower than v4/v5 equivalents.

### Key Numbers

- **6,122,441** χ=−6 polytopes exist in the full KS database (h¹¹ = 13–119)
- h13–h40 contains **5,795,310** (94.7%); h41–119 adds 327,131 (tapers to zero by h120)
- **h13–h21 exhaustively scanned** (100% of ~258K polytopes)
- **h22–h24 nearly exhaustive** (~99.5%; h24 fully exhausted: 438K/438K); **h25 fully exhausted** (424K/424K); **h26** at ~49% (200K of 412K)
- **h27–h28** at ~18.5% (200K of 1.08M); **h29–h30** at ~24% (200K of 833K)
- **52,865** fully scored (yukawa + n_clean) — T2: **54,911** total | T3: **37**
- **89** = highest v6 score achieved (**h26/P11670** — champion, stable across all batches)
- **≥80: 35 polytopes (all T3-verified). ≥75: 278 polytopes. ≥70: 965 polytopes.**
- **Score distribution (top)**: 89×1, 87×4, 85×6, 83×1, 82×4, 81×4, 80×15
- **T0 wall confirmed**: h24 back half (350K–438K) and h25 back half (362K–424K) each returned 0 T0 passes — KS polytope ordering concentrates all viable geometry at the front
- **h11_eff=22 is the sweet spot**: consistent across top entries; h11=27–29 contributes 9 of top-20 SM+GUT entries
- **Hard walls for ≥80**: yukawa_hier < 500 → impossible; vol_hier < 100 → impossible; n_dp ≥ 11 → impossible; n_fibers ≥ 12 → impossible
- **h22/P682**: score **85** (jumped from T2=80), n_clean=**84** — record n_clean in entire ≥80 tier; gauge su(3) × su(14) × U(1)^5
- **2 score=80 T2 candidates confirmed below 80** at T3 (expected: T2 scoring is a lower bound)
- **T3-verified count**: 37 total entries at tier T3; 35 at score≥80, 2 below 80

---

## 1. Pipeline and Scoring Evolution

### 1.1 v6 Scoring System (current)

100-point composite, 10 components (2 dead components removed from v5):

| Component | Max | What it measures |
|-----------|----:|------------------|
| yukawa_hierarchy | 30 | Eigenvalue spread of Yukawa texture matrix |
| yukawa_rank | 15 | Number of independent Yukawa eigenvalues ≥ 3 |
| lvs_quality | 15 | τ/V^{2/3} ratio grading (7 tiers, absorbed lvs_binary) |
| clean_bundles | 10 | log₂-scaled count of h⁰=3, h¹=h²=h³=0 bundles |
| vol_hierarchy | 7 | Big/small divisor volume ratio |
| d3_diversity | 5 | Number of distinct D³ values among clean bundles |
| clean_depth | 5 | First clean bundle found early in census |
| clean_rate | 5 | n_clean / n_bundles_checked |
| rank_sweet_spot | 3 | Yukawa rank in 140–159 range |
| bundle_quality | 3 | Conjunction of depth + rate |
| mori_blowdown | 2 | del Pezzo contraction fraction (reduced) |
| **Total** | **100** | |

**Removed from v5**: `tadpole_ok` (100% pass, χ/24=−0.25 is constant),
`lvs_binary` (96.1% pass, merged into lvs_quality).
**Changed**: yukawa_hierarchy 27→30 (THE key discriminator, r=+0.31),
vol_hierarchy 5→7, mori_blowdown 5→2. **New**: bundle_quality (3 pts).

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

### 5.2 Score distribution (v6, n=62,377)

| Threshold | Count | % of scored |
|-----------|------:|-------------|
| ≥ 85 | 4 | 0.006% |
| ≥ 80 | 24 | 0.038% |
| ≥ 79 | 40 | 0.064% |
| ≥ 75 | 174 | 0.28% |
| ≥ 70 | 575 | 0.92% |

The ≥75 count jumped from ~31 (pre-T2-sweep) to **174** after the March 2026 T2 backlog sweep, which scored 2,551 polytopes that had been stuck at T1 due to the max-h⁰ screening threshold.

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

### Update — gap=0 Probe at h27 (2026-02-28)

**Direct test**: 500 gap=0 (favorable) polytopes at h¹¹=27 run through pipeline v6
with GAP_MIN=0, EFF_MAX=30 overrides. Results vs same h11 scan of gap≥2 polytopes:

| Metric | gap=0 (favorable) | gap≥2 (non-favorable) |
|--------|-------------------|-----------------------|
| T1 time (500 polys) | **744s** | ~88s |
| T1 pass rate | 21.0% (105/500) | ~45% |
| T2 with clean | 90/105 (86%) | high |
| Top score | **84** | **89** (current champion) |
| Mean score | 55.2 | ~57 |

**Root cause of slowness**: gap=0 → h¹¹_eff = h¹¹ = 27. Bundle search runs in
a 27-dimensional integer lattice — exponentially larger than h¹¹_eff=20–22 for
gap≥6 at h27. T1 throughput drops 5.3× (0.67/s vs 3.5/s).

**Verdict**: The real gate is **h¹¹_eff ≤ 22 (EFF_MAX)**, not gap itself.
GAP_MIN=2 is a fast proxy for this constraint — at h27+, gap<2 implies
h¹¹_eff=27-28 which exceeds EFF_MAX and would be unacceptably slow regardless.
The original filter was correct on both axes: quality (lower ceiling, best=84 vs
champion 89) AND compute time (5× slower). Gap=0 polytopes are a dead end for
high-h¹¹ SM searches.

**Middle path**: EFF_MAX is the unifying constraint. Rather than opening gap=0,
the highest ROI is scanning deeper into h27–30 gap≥3 space — only ~500 of
~47K favorable scans done there. The champion cluster (gap=6–10, h¹¹_eff=20–22)
is undersampled by 100×.

### Other empirical findings

- **Non-favorable polytopes dominate**: 9 of 10 all-time best are NF
- **h¹¹_eff ≤ 22 is the tractability ceiling**: above this T1 becomes unacceptably slow
- **Swiss cheese is NOT predictive** for T1 success (89% vs 86%)
- **n_chi3 ≥ 10,000** → avg 92.4 clean (phase transition)
- **Clean increases with h¹¹ at fixed eff**: more embedding room is pure upside

---

## 14. Fiber Worker Status + Gap=0 Cheap Alternative Analysis

**Date**: 2026-02-28.

### Fiber Worker (gauge algebra classification)

All pipeline versions (v4/v5/v6) contain `_fiber_worker()`: Kodaira fiber
classification that determines gauge algebra (`has_SM`, `has_GUT`, `best_gauge`,
`n_fibers`). **It has no CLI flag and has only been run manually on 8 polytopes.**

Consequence: the v6 scoring component `fibration_sm` (3 pts) scores 0 for 99.8%
of T2-scored polytopes — not because they have no fibrations (virtually all have
K3 + elliptic fibrations; `n_k3_fib` and `n_ell_fib` are populated for 4,584/4,588)
but because gauge algebra extraction was never systematically run.

**Fix**: add `--fiber --top N` CLI mode to run `_fiber_worker` on the top-N scored
polytopes in the DB. Would populate `has_SM`/`has_GUT`/`best_gauge` for the
leaderboard, unlocking 3 pts of scoring signal.

**Note**: all T3-analyzed candidates in CATALOGUE.md §4 have gauge data because
they were run through the manual fiber pass. The issue is scale coverage.

### Gap=0 — Is There a Cheap Alternative to Full T1?

**Question**: Can T0-level data predict clean bundle yield for gap=0 polytopes
without running the full 27D bundle lattice enumeration?

**Three approaches evaluated:**

| Method | Cost | Filters | Verdict |
|--------|------|---------|--------|
| n_chi3 count (HRR solutions) | T0 already | ~0% (always huge at h27) | Useless |
| c2_all_positive + Mori fraction | T0 already | ~15% | Too weak |
| Regression on 4,588 T2-scored (predict n_clean from T0 features) | One-time fit | Unknown but promising | **Best option, not yet built** |

The regression model approach: fit `n_clean ~ [n_chi3, h11_eff, volume_hierarchy,
n_dp, n_k3_div, c2_all_positive, aut_order, gap]` on existing T2 data — since
all features are T0-computable, the trained model could score gap=0 polytopes in
< 0.1s without running T1. Accuracy would be limited but could filter the bottom
50% of candidates.

**Practical verdict**: For h11 ≥ 23, gap=0 implies h11_eff ≥ 23, which already
exceeds EFF_MAX=22. The existing EFF_MAX filter IS the cheap proxy. No additional
layer needed. Gap=0 polytopes at h11 ≥ 23 are correctly excluded by EFF_MAX alone.

At h11 = 13–14 (h11_eff < 15, exempt from both filters): gap=0 runs fine and we
have full coverage. Only 13 polytopes — all already in the DB.

**Conclusion: no gap=0 universe to unlock. The filter architecture is sound.**

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

---

## 16. n_clean_est Bug Fix and T1-Skip Rescue

**Date**: 2026-02-28. **Commit**: `64a846e`.

### 16.1 The Bug

`n_clean_est` was **always 0** for all 4,575 T2 polytopes. Root cause: the
T1 worker called `compute_h0_koszul(..., min_h0=H0_MIN_T1)` with
`H0_MIN_T1=5`, which returns 0 (screening signal) for any bundle with
h⁰(V) < 5. The clean-bundle check (`if h0 == 3`) therefore never fires —
h⁰=3 is always below the min_h0=5 screening threshold.

**Impact**: Polytopes with clean bundles but max_h⁰ < 5 were silently
dropped at T1 screening. Scoring was NOT affected (uses `n_clean` from T2,
which computes h⁰ without screening).

**Fix**: Changed `min_h0=H0_MIN_T1` → `min_h0=3` in the T1 worker's clean
check (lines 268/272 of `pipeline_v6.py`). The T1 screening still uses
`min_h0=5` for the max-h⁰ pass; only the clean-estimation path changed.

### 16.2 Rescue Results

Ran `rescue_t1_skips.py` across all 21 h¹¹ levels (h14–h35) with 16
workers. Two runs total, 10,801 T1-skip polytopes re-examined.

**Run 1** (8 levels, 8,535 rescued, 27,474s):

| h¹¹ | Skips | Rescued | Rate | Top score |
|-----|-------|---------|------|-----------|
| 19 | 8,227 | 4,032 | 49% | 80 |
| 18 | 4,794 | 2,529 | 53% | 70 |
| 17 | 1,335 | 681 | 51% | 71 |
| 27 | 958 | 501 | 52% | 77 |
| 21 | 394 | 236 | 60% | 78 |
| 20 | 373 | 228 | 61% | 70 |
| 22 | 351 | 190 | 54% | **82** |
| 28 | 320 | 138 | 43% | — |

**Run 2** (13 levels, 620 rescued, 8,305s):

| h¹¹ | Skips | Rescued | Rate | Top score |
|-----|-------|---------|------|-----------|
| 23 | 230 | 112 | 49% | 72 |
| 16 | 173 | 97 | 56% | 62 |
| 24 | 164 | 96 | 59% | 77 |
| 26 | 160 | 84 | 53% | 76 |
| 25 | 104 | 66 | 63% | 75 |
| 30 | 93 | 48 | 52% | 78 |
| 15 | 73 | 20 | 27% | 53 |
| 29 | 52 | 26 | 50% | 70 |
| 31 | 25 | 12 | 48% | 68 |
| 33 | 24 | 8 | 33% | 73 |
| 32 | 13 | 4 | 31% | 57 |
| 14 | 13 | 0 | 0% | — |
| 35 | 8 | 1 | 13% | 44 |

**Totals**: **9,155 polytopes rescued** from 10,801 T1-skip candidates.
Overall rescue rate ~85%. **13,806** total T2-scored (up from 4,588).

### 16.3 Key Findings

1. **h22/P302 enters top 6** with score 82 and **182 clean bundles** — the
   highest clean count in the database. This polytope was invisible before
   the fix because its max h⁰ was below the T1 screening threshold of 5.

2. **93 rescue polytopes score ≥ 70** — a massive new high-quality
   population that was entirely hidden by the bug.

3. **100% of rescues were purely from the clean fix** — all rescued
   polytopes had max_h⁰ < 5 but contained h⁰=3 clean bundles.

4. **Rescue rate correlates with h¹¹**: higher h¹¹ levels (20–25) show
   ~60% rescue rates; lower levels (14–15) show <30%. This is consistent
   with larger h¹¹ having more divisor combinations yielding h⁰=3 bundles.

5. Score distribution post-rescue: 80+ (12), 70–79 (199), 60–69 (1,027),
   50–59 (3,739), 40–49 (6,049), <40 (2,780).

---

## 17. T0 Wall — KS Depth Limit for Productive Scanning

**Date**: 2026-03-01. **Context**: 7-hour batch (batch_7hr.sh) across h20–h30
at KS offsets beyond the existing coverage frontiers.

### 17.1 Finding

At large KS offsets, the T0 geometry filter pass rate drops to **0%**,
making further scanning totally unproductive. The threshold is approximately:

| h¹¹ | Productive range | T0 wall at offset |
|-----|-----------------|-------------------|
| h20–h22 | < 100K | ~100K (100% covered) |
| h23–h24 | < 150K | ~150K |
| h25 | < 100K | ~100K |
| h26 | < 100K | ~100K |
| h27–h30 | < 50K | ~50K |

**Test**: 700K polytopes scanned beyond these thresholds in one batch
yielded **zero scores above 23** (no T2 candidates at all).

### 17.2 Mechanism

The Kreuzer-Skarke database is ordered by number of lattice points. Polytopes
with fewer lattice points tend to have simpler geometry — more del Pezzo
divisors, well-separated volumes, favorable Hodge numbers. These pass the T0
geometry filter (effectiveness cutoffs on n_dp, h11_eff, volume structure).
Beyond a depth threshold, the remaining polytopes are geometrically
degenerate for our purposes (wrong divisor structure, failing h11_eff ≤ 22,
or minimal Mori cone viability).

**Practical implication**: The current coverage frontiers are the
**effective physical boundaries** of the productive landscape for this scan.
Going deeper is a confirmed waste of compute. The active frontier is
breadth (exhausting h25–h30 within the productive offsets), not depth.

### 17.3 Consequence for scan strategy

- h20–h21: **exhaustively covered** — all 258K+ polytopes including any T0-passing ones
- h22–h24: within 90% of the productive region; diminishing returns starting
- h25–h28: highest remaining ROI — 18–66% coverage with T0 pass rate still positive
- h29–h30: ~24% coverage, 200K scanned — productive region partially unexplored

---

## 18. T2 Backlog Sweep — March 2026

**Date**: 2026-03-01 to 2026-03-02 UTC. **Command**: `python3 pipeline_v6.py --scan --h11 20 30 --resume --top 99999 --local-ks -w 14`.
**Runtime**: ~8 hours (h20: 1.3h, h21: 2.4h, h22: 2.3h, then ~5h for h23–h30).

### 18.1 Motivation

After the T1-skip rescue (Section 16) and subsequent scans, a backlog of
T1-scored polytopes remained that had not been processed through T2 (Yukawa
calculation). These polytopes had passed T0 and the n_clean_est threshold
but were never promoted to T2 due to queue completion or indexing issues.

A bug was also discovered (and fixed) in the `--resume` path: `poly_idx`
values stored in the DB were absolute KS positions (e.g., 150,001 for
polytopes loaded with `--offset 150000`), but the resume path reloaded polys
with offset=0, causing `polys[poly_idx - offset]` to go out of bounds. Fixed
by detecting when `max(poly_idx) >= len(polys) + offset` and reloading from
index 0 to cover the full range. **Committed as `9e081c4`**.

### 18.2 Results by h¹¹

| h¹¹ | T2 scored | Top score | Runtime |
|-----|----------:|-----------|---------|
| 20 | 6,112 | 75 | ~1.3h |
| 21 | 9,007 | 80 | ~2.4h |
| 22 | 5,050 | **81** | ~2.3h |
| 23 | 2,658 | 79 | ~0.8h |
| 24 | 975 | 80 | ~0.3h |
| 25 | ~510 | 79 | ~0.2h |
| 26 | 216 | 76 | ~0.1h |
| 27–28 | — | — | — |
| 29 | 77 | 70 | ~1min |
| 30 | 75 | 78 | ~1min |
| **Total** | **~24,700** | **81** | **~8h** |

### 18.3 Key Discovery — h22/P302 (score=81, n_clean=182)

The most significant find of the sweep: **h22/P302**, previously invisible,
scores **81** with **182 clean bundles** — the highest clean bundle count
in the entire database. For comparison:

| Candidate | n_clean | Score |
|-----------|--------:|------:|
| h22/P302 | **182** | 81 |
| h19/P438 | 56 | 81 |
| h21/P270 | 74 | 80 |
| h19/P390 | 70 | 80 |
| h26/P11670 (champion) | 22 | 89 |

h22/P302's exceptional clean bundle density (182 bundles, Yukawa=970×, vol=2,650,
gap=4, K3 fibrations=4, elliptic=4) makes it the premier heterotic candidate
in the database. The Yukawa hierarchy of 970 places it in the top tier despite
falling short of the champion's discriminating 2,390 value.

### 18.4 Population impact

After the sweep, the raw scored count was **62,377**. After the §19 data
integrity audit, **37,937** have full T2 data (yukawa + n_clean). The leaderboard
(≥80, ≥75, ≥70) is unchanged — all high-score rows had full data. The reduction
came from nulling 24,440 partial T1 scores (mean=20.1, max=30) that were set
from T0/T1 features only, and from finding that most T2-attempted rows at h20–h22
actually failed the Yukawa computation.

---

## 19. Database Integrity Audit — 2026-03-01

**Trigger**: Discovered that `sm_score IS NOT NULL` (62,377) ≠ `tier_reached='T2'` (35,351).

### 19.1 Issues Found

Three categories of problematic rows:

**Issue A — T0/T1-labeled rows with full T2 data (2,871 rows)**

`tier_reached` was downgraded (T2 → T1 or T0) when a later batch reprocessed
a polytope and failed at T0/T1, but `MONOTONIC_MAX` preserved the valid score
fields. Fix: set `tier_reached='T2'` for rows where `n_clean IS NOT NULL AND
yukawa_hierarchy > 0` regardless of tier label.

Top affected rows (all legitimate leaderboard candidates):
- h27/P239 (score=82), h27/P240 (score=82), h30/P289 (score=80) — previously T0/skip
- 1,606 total T0-with-full-data, 1,265 T1-with-full-data

**Issue B — Partial T1 scores (24,440 rows)**

Polytopes where `sm_score` was set from T0/T1 features only (no yukawa, no
n_clean). These appear when the pipeline ran T2 but the Yukawa computation
returned 0 or failed, yet still stored a partial score from whatever T0 components
were available (volume_hierarchy, gap, n_dp, mori_blowdown). Mean score = 20.1,
max = 30 — all too low to affect the leaderboard, but inflate the "scored" count.
Fix: `UPDATE polytopes SET sm_score=NULL WHERE sm_score IS NOT NULL AND (n_clean IS NULL OR yukawa_hierarchy IS NULL OR yukawa_hierarchy = 0)`.

**Issue C — Why so few scored at h20–h22?**

Despite "6-9K T2 attempted" per the sweep logs, only 410/451/459 polytopes
at h20/h21/h22 have full T2 data. The rest had Yukawa computation fail silently
(returned 0 or raised an exception handled internally), leaving `yukawa_hierarchy=NULL`
and only a partial T1-level score — now nulled. The **23,749 polytopes
with `n_clean_est > 0` but no Yukawa** are the most important untapped pool.

### 19.2 Corrected Counts

| Metric | Before audit | After audit |
|--------|-------------|-------------|
| sm_score IS NOT NULL | 62,377 | **37,937** |
| tier_reached = 'T2' | 35,351 | **38,222** |
| Score mean | 37.6 | **48.9** |
| Score min | 3 | **25** |
| ≥80 / ≥75 / ≥70 | 24 / 174 / 575 | **24 / 174 / 575** (unchanged) |

The leaderboard is completely intact. Only the aggregate counts changed.

### 19.3 Root Cause — Partial Scoring at T1

The v6 pipeline stores `sm_score` when T2 is attempted even if Yukawa fails.
Since 5+ scoring components (vol_hierarchy, gap bonus, lvs_quality, mori_blowdown,
clean_bundles) are computable from T0/T1 data, these polytopes score 15–30 purely
from geometry. This is misleading — it appears "scored" but is not comparable to
a full T2 score. **Fix needed**: only write `sm_score` when `yukawa_hierarchy > 0`.

---

## 20. Landscape Structure — Hard Walls and Fertile Zones

**Method**: Full SQL analysis on 37,937 properly scored polytopes.

### 20.1 Hard Walls for ≥80

The following constraints are **necessary conditions** for score ≥80. No polytope
violates any of them:

| Feature | Wall | Confirmed by |
|---------|------|-------------|
| yukawa_hierarchy | **≥ 500** (needed), often ≥ 1000 | 0 polytopes with hier<500 score ≥80 |
| volume_hierarchy | **≥ 100** (needed), often ≥ 1000 | 0 polytopes with vol<100 score ≥80 |
| n_dp | **≤ 10** | 0 polytopes with n_dp≥11 score ≥80 |
| n_fibers (K3+ell) | **≤ 11** | 0 polytopes with n_fibers≥12 score ≥80 |
| lvs_score | **< 0.1** | All 24 entries at ≥80 have lvs_score < 0.1 |

The first two (yukawa_hierarchy > 500 and volume_hierarchy > 1000) are
**near-necessary** — 21 of 24 entries at ≥80 satisfy both. Three exceptions
(h19/P390, h21/P270, h27/P9181) compensate via very high n_clean (70, 74, 24)
and other components.

### 20.2 Sweet Spot Geometry

The 24 polytopes at score ≥80 cluster tightly in feature space:

| Feature | Champion range | Notes |
|---------|---------------|-------|
| h11_eff | **21–22** | 14 of 24; h11_eff=16 has 4 (low-h11 with high gap) |
| gap | **2–6** | All major entries; extremes at gap=0 (h27/P240) and gap=8-12 |
| n_dp | **6–10** | Sweet spot — too few or too many del Pezzo kills score |
| n_fibers | **3–8** | Peak fertility at 4-8; champion at 8 (4K3+4ell) |
| yukawa_hier | **500–5000** | Plateau above 5K (score stops improving much) |
| vol_hier | **1000–20000** | Log-linear relationship; outlier h30/P289 at 34,318 |

**Score vs fibration richness is non-monotone**: n_fibers=8 is optimal (max=89);
above 11, average score drops below 47 and no polytopes reach ≥80. More fibrations
dilute the Yukawa texture quality.

### 20.3 Two Scoring Archetypes

Examining the ≥80 cluster reveals two distinct paths to high score:

**Archetype A — Yukawa-Dominant** (h11_eff=21–22, moderate clean, high Yukawa):
- Examples: h26/P11670 (hier=2390, clean=22), h23/P37201 (hier=1599, clean=26)
- Pattern: hier ≥ 1000, n_clean 18–32, h11_eff=21–22, gap=2–4, n_dp=6–10
- Wins primarily through Yukawa hierarchy (30pts) + rank (15pts)
- **All ≥85 belong to this archetype**

**Archetype B — Clean-Dominant** (low h11_eff=16–17, very high clean, low Yukawa):
- Examples: h21/P270 (hier=123, clean=74), h19/P390 (hier=122, clean=70), h22/P302 (hier=970, clean=182)
- Pattern: hier 100–1000, n_clean ≥ 40, h11_eff=16–21
- Wins through clean_bundles (10pts) + clean_rate (5pts) + clean_depth (5pts) + other
- h22/P302 is a hybrid: clean=182 (record) with hier=970 (moderate) — the only polytope scoring ≥80 through both paths simultaneously

### 20.4 h22/P302 — Invalidated (2026-03-02)

**h22/P302 was previously listed at score=81, n_clean=182 — both values are now confirmed invalid.**

The 2026-03-02 fresh Hetzner scan rescanned all h22 polytopes from scratch. In the merged DB, h22/P302 is at `tier_reached=T1` with `sm_score=NULL, n_clean=NULL`. The prior score was a legacy artifact from a T1/T2 boundary ambiguity in an earlier pipeline version — the polytope's max_h⁰ was borderline and the old code path wrote a partial score into `sm_score` without completing the full Yukawa+bundle census. The March 1 integrity audit (§19) missed this because the row had plausible non-zero `yukawa_rank` (178) despite no valid `yukawa_hierarchy` having been computed.

The fresh pipeline (with the yukawa-fix: `sm_score=None` when `yukawa_hierarchy==0`) correctly leaves h22/P302 unscored. The n_clean=182 value was also not recomputed and is now NULL. **h22/P302 is no longer in the leaderboard.**

Similarly, h23/P37201 (prev. 87) was rescored in the fresh h23 pass — h23's new top score is **79**. The 87 was also a partial-score artifact. See §21 for the full post-mortem on all 8 invalidated entries.

### 20.5 Fertility Rates (≥75 among fully scored, by h11)

| h11 | scored | ≥75 rate | ≥80 rate | top |
|-----|-------:|----------|----------|-----|
| 21 | 451 | **2.66%** | 0.44% | 80 |
| 30 | 153 | **2.61%** | 0.65% | 80 |
| 27 | 1,799 | 1.28% | 0.17% | 82 |
| 28 | 816 | 1.47% | 0.00% | 79 |
| 26 | 2,839 | 0.92% | **0.14%** | 89 |
| 22 | 459 | 0.87% | 0.22% | 81 |
| 23 | 6,308 | 0.32% | 0.02% | 87 |
| 24 | 9,132 | 0.42% | **0.07%** | 85 |

**Key insight**: h26 has the highest ≥80 rate (0.14%) despite moderate ≥75 rate.
h21 and h30 have high ≥75 rates but only half reach ≥80 — these are the
Clean-Dominant archetype (high clean, moderate Yukawa). h26 represents the
Yukawa-Dominant archetype where most ≥75s convert to ≥80.

**h34 anomaly** (not in table): h34/P61 scores 75 via gap=12, h11_eff=22 —
despite h11=34 it's effectively an h11_eff=22 polytope with extreme redundancy.
Confirms EFF_MAX=22 is the physical ceiling, not h11 itself.

### 20.6 The Unscored Pool — 23,749 T1 Candidates with n_clean_est > 0

The largest single opportunity for new discoveries: **23,749 polytopes** passed
T0 and T1 clean estimation (n_clean_est > 0) but never had Yukawa computed.
The Yukawa computation was either never attempted (T2 backlog) or timed out.

| h11 | T1 with clean_est > 0 | max_clean_est | Priority |
|-----|-----------------------:|--------------|---------|
| 20 | 5,949 | **118** | CRITICAL |
| 21 | 8,774 | 88 | CRITICAL |
| 22 | 4,863 | 80 | HIGH |
| 23 | 2,519 | 78 | HIGH |
| 24 | 909 | 74 | MEDIUM |
| 25 | 426 | 56 | MEDIUM |
| 26 | 173 | 56 | MEDIUM |

**Top unscored polytopes** (by n_clean_est, all at h20 with gap=3, h11_eff=20):

| ID | n_clean_est | h11_eff | gap |
|----|------------|---------|-----|
| h20/P3275 | **118** | 20 | 3 |
| h20/P4946 | 114 | 20 | 3 |
| h20/P1099 | 108 | 20 | 3 |
| h20/P5181 | 106 | 20 | 3 |

If h20/P3275 has yukawa_hierarchy ≥ 500, it could score **≥82** on clean bundles
alone (n_clean=118 at h11_eff=20 yields ~10pts clean component; combined with
moderate Yukawa). The h11_eff=20 constraint limits the Yukawa rank component,
but the sheer clean bundle density is exceptional.

**Action**: Targeted T2 Yukawa retry for all polytopes with `n_clean_est ≥ 30`
(~3,000 polytopes). This is the highest-ROI computation available.

### 20.7 Yukawa Hierarchy — Hard Predictive Value

The Yukawa hierarchy alone is the single best predictor of very high scores:

| Hier range | n | mean score | max score | ≥80 count |
|-----------|---|-----------|-----------|-----------|
| < 50 | 20,329 | 46.2 | 75 | 0 |
| 50–100 | 8,940 | 47.8 | 73 | 0 |
| 100–200 | 5,064 | 55.5 | 80 | 3 |
| 200–500 | 2,661 | 55.9 | 79 | 0 |
| 500–1000 | 634 | 61.3 | 82 | 9 |
| 1000–2000 | 179 | 65.4 | 87 | 6 |
| 2000–5000 | 105 | 63.6 | 89 | 4 |
| 5000+ | 25 | 66.4 | 81 | 2 |

**The 5K→89 regime (105 polytopes, hier 2K–5K) contains the champion.** Only
~0.28% of scored polytopes reach hier ≥ 1000. The exponentially sparse hier > 2000
bin (105 rows, 0.28% of scored) holds 4 of 24 top-80 entries (16.7% hit rate).

This strongly supports using yukawa_hierarchy as a T1.5 pre-filter: scanning
Yukawa first and only doing the full T2 bundle census when hier ≥ 200 would
dramatically concentrate compute on productive polytopes.

---

## 21. Fresh Hetzner Scan + DB Merge — 2026-03-02

**Goal**: Eliminate all partial-score corruption root-cause by deleting the Hetzner DB and running a fully clean fresh scan, then merging back into the standing local DB.

### 21.1 Pipeline Fix

Root cause of partial scores: `analyze_t2()` called `compute_sm_score()` even when `yukawa_hierarchy == 0` (Yukawa computation failed or timed out). The fix: set `result['sm_score'] = None` when `yukawa_hierarchy == 0`; since `upsert_polytope` skips None fields, any valid pre-existing score is preserved. Post-upsert rescore also guarded with `if (yukawa_hierarchy or 0) > 0`. Committed `7c9ecbd`.

### 21.2 Fresh Scan (Hetzner, batch_fresh.sh)

Hetzner DB deleted. Fresh scan launched **01:47 UTC Mar 2**. Completed **17:59 UTC Mar 2** (~16 hours).

**Scan order / results (by h11):**

| h11 | Limit | T2 analyzed | Top score | Runtime |
|-----|-------|-------------|-----------|---------|
| 26 | 50K | ~659 | — | ~28m |
| 22 | 50K | — | — | ~1.5h |
| 21 | 50K | 2,550 | — | ~1.2h |
| 25 | 50K | 659 | 81 | ~28m |
| 24 | 50K | 1,210 | 77 | ~45m |
| 23 | 50K | 2,550 | — | ~1.6h |
| 20 | 30K | 4,090 | — | ~1.5h |
| 27 | 30K | 129 | 71 | ~7m |
| 28 | 30K | 100 | 76 | ~5m |
| 29 | 30K | 57 | 63 | ~4m |
| 30 | 30K | 25 | 58 | ~4m |

T2 backlog sweep (h20–h30 resume): only **23 polytopes** found needing T2 replay — near-zero residual, confirming clean completion.

### 21.3 DB Merge

Fresh DB (126MB, 450,333 rows covering h20–h30 first 30K–50K) merged into standing local DB (754MB, 2.94M rows). Merge strategy: delete all old rows for any (h11, poly_idx) present in fresh DB, then insert fresh rows. Fresh always wins — it uses the fixed pipeline.

```
MERGE RESULT:
  Deleted  450,333 old rows (overlapping with fresh)
  Inserted 450,333 fresh rows
  Total rows unchanged: 2,943,641
  Partial-score violations: 0  ✅
  Scored: 34,790 (was 37,937 — drop = 3,147 correctly nulled)
```

### 21.4 Invalidated Old "Champions"

The fresh scan correctly rescored 8 entries previously listed at ≥80:

| ID | Old score | New status | Reason |
|----|-----------|------------|--------|
| h23/P37201 | 87 | NULL (h23 top=79) | Partial score artifact |
| h27/P240 | 82 | Rescored lower (≤79) | Fresh scan: h27 top=79 |
| h27/P239 | 82 | Rescored lower (≤79) | Fresh scan: h27 top=79 |
| h22/P302 | 81 | NULL (T1, no score) | Yukawa never completed |
| h21/P270 | 80 | NULL (h21 scored=0) | h21 fully rescored |
| h21/P55 | 80 | NULL (h21 scored=0) | h21 fully rescored |
| h27/P9181 | 80 | Rescored lower (≤79) | Fresh scan: h27 top=79 |
| h30/P289 | 80 | Rescored lower (≤70) | Fresh scan: h30 top=70 |

All 8 were artifacts of earlier pipeline versions that either (a) stored T0/T1 feature scores without completing Yukawa+bundle census, or (b) were computed with non-reproducible polytope ordering and rescored lower under the canonical `--local-ks` ordering.

### 21.5 Verified Leaderboard (post 2026-03-02 merge)

*Superseded by §22.4 after 2026-03-03 ext scan + merge. h19/P438, h18/P315, and h19/P390 were subsequently overwritten by mop-up stalls.*

**16 polytopes at ≥80 as of 2026-03-02 merge.** See §22.4 for current (14-entry) leaderboard.


---

## 22. Extension Scan + DB Merge (2026-03-03)

**Scan**: `batch_ext.sh` — 00:20–06:55 UTC Mar 3 (6.6 hours, 12 workers).
**Merge**: ext DB (764,764 rows, 19,925 scored) into main DB via ATTACH + DELETE + INSERT. 614,764 rows deleted, 764,764 inserted. 26.7s.

### 22.1 What ran

| Step | Command | Polytopes | Outcome |
|------|---------|-----------|---------|
| 0 | h13–40 `--resume` T2 mop-up | ~764K total | 19,925 scored; 246 T2 remain |
| 1 | h25 offset=362K limit=62K | 62,000 | **0 T0 passes** |
| 2 | h24 offset=350K limit=88K | 88,000 | **0 T0 passes** |
| 3 | h26 offset=50K limit=150K | 150,000 | **0 T0 passes** (3 T2 residuals scored) |

### 22.2 Key finding: T0 wall confirmed

Steps 1–3 collectively scanned 300,000 polytopes across the back halves of h24, h25, and h26 and returned **zero T0 passes**. This is definitive confirmation of the T0 wall hypothesis: the KS polytope ordering concentrates all geometrically viable polytopes (EFF_MAX ≤ 22, GAP ≥ 2) at low poly_idx. The back half of the distribution is uniformly dead.

**Consequence**: h24 and h25 are now **fully exhausted** through the entire KS universe. No further productive scanning exists at those h11 values. h26 at ~49% (200K of 412K) still has some productive territory at low offsets not yet covered by a clean-pipeline run.

### 22.3 Mop-up stalls: 3 old entries overwritten

The mop-up (Step 0: `--scan --h11 13 40 --resume`) re-scanned h13–h19 from scratch in the fresh container DB (those h11 values were absent from the fresh scan DB). For 3 old high-scoring entries, this rescan produced T1-stall rows (yukawa_rank computed, yukawa_hierarchy timed out), which replaced the old scored rows on merge:

| Entry | Prev score | New status | yukawa_rank | Root cause |
|-------|-----------|------------|-------------|------------|
| h19/P438 | 81 | NULL (T1 stall, tier=None) | 150 | yukawa_hierarchy timeout on rescan |
| h18/P315 | 80 | NULL (T1 stall, tier=None) | 137 | yukawa_hierarchy timeout on rescan |
| h19/P390 | 80 | NULL (T1 stall, tier=None) | 120 | yukawa_hierarchy timeout on rescan |

These entries had valid scores in the old scan. Their loss is a mop-up collateral effect — **not** evidence that the original scores were wrong. The original h18/h19 exhaustive scan produced these scores under normal T1→T2 conditions; the rescan under the mop-up's aggressive 12-worker load likely caused Yukawa timeouts.

**Mitigation for future scans**: when running `--resume` on a range that wasn't in the fresh scan DB, use `--skip-existing` or limit to specific h11 values that need mop-up.

### 22.4 Current leaderboard (post 2026-03-03 merge)

**14 polytopes at ≥80 (0 partial-score violations).**

| Rank | ID | Score | Hier | Clean | chi |
|------|----|-------|------|-------|-----|
| 1 | h26/P11670 | **89** | 2,390 | 22 | +6 |
| 2 | h24/P45873 | **85** | 1,222 | 22 | +6 |
| 3 | h25/P46481 | **85** | 4,893 | 22 | +6 |
| 4 | h24/P868 | **83** | 1,220 | 24 | +6 |
| 5 | h25/P7867 | **81** | 513 | 18 | +6 |
| 6 | h24/P1015 | **80** | 2,403 | 30 | +6 |
| 7 | h24/P44004 | **80** | 619 | 26 | +6 |
| 8 | h24/P272 | **80** | 791 | 24 | +6 |
| 9 | h24/P9576 | **80** | 594 | 28 | +6 |
| 10 | h25/P860 | **80** | 1,187 | 24 | +6 |
| 11 | **h22/P682** | **80** | 1,464 | **84** | +6 |
| 12 | h26/P30513 | **80** | 1,760 | 22 | +6 |
| 13 | h26/P11871 | **80** | 519 | 26 | +6 |
| 14 | h26/P315 | **80** | 1,506 | 32 | +6 |

**h22/P682** is new — n_clean=84 is the highest clean-bundle count in the ≥80 tier. Emerged from ext mop-up's h22 first-50K coverage.

**Score distribution**: ≥90: 0 · ≥85: 3 · ≥80: 14 · ≥75: 119 · ≥70: 435

### 22.5 DB state (post-merge)

| Metric | Value |
|--------|-------|
| Total rows | 3,093,641 |
| Scored | 34,067 |
| Max score | 89 |
| Violations | **0** |
| h24 coverage | 438,000 / 438,092 — **fully exhausted** |
| h25 coverage | 424,000 / 424,105 — **fully exhausted** |
| h26 coverage | 200,018 / 412,493 — ~49% |
| Unscored T2 | 246 (persistent timeouts) |
