# Catalogue of Results — χ = −6 CY Landscape

> **Purpose**: Record what's been checked, what passed, and what's ruled out.
> If a polytope or approach appears here, you don't need to redo the work.
>
> **Last updated**: 2026-02-27. Pipeline v5.2, 100-point SM composite scoring. **174,158 polytopes** scanned (3.0% of 5.80M KS χ=−6 landscape, h13–h40). **2,012 T2-scored**. Champion: h30/P289 (score 89). Database: `v4/cy_landscape_v4.db`. Deployed on Hetzner (16-core).

---

## 1. Scan Coverage

### What We Scanned

Two eras of scanning:

**Era 1 (v3–v4, h13–h24)**: 6,158 polytopes, 26-point scoring, limit=100/h¹¹ (h13–h16 exhaustive).
**Era 2 (v4.1–v5.2, h20–h40)**: 168,000 polytopes, 100-point SM composite, 1K–50K/h¹¹.

#### Complete Coverage — KS Ground-Truth Counts (h13–h40)

Exact KS database totals queried from the live Kreuzer-Skarke database
(http://quark.itp.tuwien.ac.at) on 2026-02-27. Counts are for χ = −6
reflexive 4-polytopes (lattice N).

| h¹¹ | h²¹ | KS total | Scanned | Coverage | T2-scored | Best | Era |
|------|------|----------|---------|----------|-----------|------|-----|
| 13 | 16 | 3 | 3 | **100%** | — | — | v3 |
| 14 | 17 | 22 | 22 | **100%** | — | — | v3 |
| 15 | 18 | 553 | 553 | **100%** | — | — | v3 |
| 16 | 19 | 5,180 | 5,180 | **100%** | — | — | v3 |
| 17 | 20 | 38,735 | 200 | 0.5% | — | — | v3 |
| 18 | 21 | 105,811 | 100 | 0.09% | — | — | v3 |
| 19 | 22 | 183,287 | 100 | 0.05% | — | — | v3 |
| 20 | 23 | 257,613 | 1,000 | 0.4% | 190 | 81 | v5 |
| 21 | 24 | 329,227 | 1,000 | 0.3% | 228 | 80 | v5 |
| 22 | 25 | 407,667 | 1,000 | 0.2% | 281 | 75 | v5 |
| 23 | 26 | 443,162 | 1,000 | 0.2% | 235 | 79 | v5 |
| 24 | 27 | 447,109 | 1,000 | 0.2% | 184 | 78 | v5 |
| 25 | 28 | 432,081 | 1,000 | 0.2% | 138 | 81 | v5 |
| 26 | 29 | 419,456 | 1,000 | 0.2% | 113 | 79 | v5 |
| **27** | **30** | **393,842** | **50,000** | **12.7%** | **270** | **86** | v5 |
| **28** | **31** | **354,495** | **50,000** | **14.1%** | **164** | **87** | v5 |
| 29 | 32 | 322,535 | 1,000 | 0.3% | 39 | 76 | v5 |
| **30** | **33** | **276,639** | **50,000** | **18.1%** | **74** | **89** | v5 |
| 31 | 34 | 244,599 | 1,000 | 0.4% | 27 | 71 | v5 |
| 32 | 35 | 212,314 | 1,000 | 0.5% | 41 | 80 | v5 |
| 33 | 36 | 181,542 | 1,000 | 0.6% | 7 | 67 | v5 |
| 34 | 37 | 164,257 | 1,000 | 0.6% | 15 | 72 | v5 |
| 35 | 38 | 137,448 | 1,000 | 0.7% | 3 | 62 | v5 |
| 36 | 39 | 119,284 | 1,000 | 0.8% | 2 | 31 | v5 |
| 37 | 40 | 100,863 | 1,000 | 1.0% | 0 | — | v5 |
| 38 | 41 | 87,038 | 1,000 | 1.1% | 0 | — | v5 |
| 39 | 42 | 69,757 | 1,000 | 1.4% | 1 | 49 | v5 |
| 40 | 43 | 60,271 | 1,000 | 1.7% | 0 | — | v5 |
| **Total** | | **5,795,310** | **174,158** | **3.0%** | **2,012** | **89** | |

**Key stats**:
- **5.80 million** χ=−6 polytopes exist in the KS database for h¹¹ ∈ [13, 40]
- We have scanned **174K (3.0%)** of this landscape
- h13–h16 are **exhaustively scanned** (100% coverage, 5,758 polytopes)
- Even our deepest v5 levels (h27/h28/h30 at 50K) are only **12–18% covered**
- The peak is h24 with **447K polytopes** — we've hit only 0.2%
- 2,012/168,000 (1.2%) of the v5 scan survive to T2 scoring
- h27–h30 dominates: 8 of the top 10 candidates
- **h27 is a fibration-rich zone**: all 6 T3-analyzed h27 candidates have SM+GUT gauge groups
- h30/P289 (score 89) remains the overall champion
- h37+ is barren — the χ=−6 landscape is exhausted above h¹¹ ≈ 36
- v3 legacy polytopes (h13–h19) were scored with the old 26-point system; not yet rescored under v5.2

### What We Haven't Scanned

- **h¹¹ = 13–16**: Exhaustively scanned (100% coverage). Scored under legacy 26-point system only.
- **h¹¹ = 17–19**: 200/100/100 of 38K/106K/183K scanned (<0.5%). Legacy scoring only.
- **h¹¹ = 20–26, 29, 31–40**: Only 1K of 100K–450K polytopes scanned (0.2–1.7% coverage). Major unexplored territory, especially h22–h26 which each have 400K+ polytopes.
- **h27 beyond 50K**: 393,842 total — 50K scanned = 12.7% coverage. 343K polytopes remain in the fibration-rich zone.
- **h28 beyond 50K**: 354,495 total — 50K scanned = 14.1% coverage. 304K polytopes remain.
- **h30 beyond 50K**: 276,639 total — 50K scanned = 18.1% coverage. 227K polytopes remain. The champion P289 (89) came from this level.
- **h¹¹ = 37–128**: Barren at EFF_MAX=22 — zero or near-zero T0 pass rate. Would require raising EFF_MAX (with attendant computational cost) to access.
- **Deeper triangulation sampling**: Top-10 candidates sampled at 20 random FRSTs. Expanding to 200+ would refine c₂ stability percentages.

---

## 2. Screening Funnel Results

### Current Pipeline (v5.2, h20–h40)

```
168,000 polytopes (h11=20..40, v5.2 pipeline)
  │
  ├─ 5,344 pass T0 (geometry + EFF_MAX=22) ──── 3.2% pass
  │   │
  │   └─ 2,012 pass T1 → T2 scored ─────────── 1.2% of total
  │       (100-point SM composite: hierarchy, Yukawa, LVS, clean bundles, ...)
  │       │
  │       ├─ 22 deep-analyzed (T3) ─────── 20 random FRSTs each
  │       │   h30/P289: SM+GUT, su(3)×su(17)×U(1)^10
  │       │   h27 cluster: ALL 6 have SM+GUT fibrations
  │       │   Tier A (paper-ready): 3 candidates (h28 stability cluster)
  │       │   Tier C (score+fibrations): 4 candidates (h27+h30)
  │       │
  │       └─ Score distribution:
  │           89: 1,  86–87: 3,  83–85: 7,  80–82: 14,  70–79: 247,  <70: 1,740
```

### Legacy Pipeline (v3–v4, h13–h24)

```
1,025 polytopes (scan v2, h11=13..24, limit=100/h11)
  │
  ├─ 634 have h⁰ ≥ 3 line bundles ─────────── 62% pass
  │   │
  │   ├─ 337 pass Tier 1 ──────────────────── 33% of total
  │   │   │
  │   │   └─ 157 pass Tier 1.5 → Tier 2 ──── 15% of total
  │   │       23 scored T2=45 (max)
  │   │
  │   └─ 297 filtered at T1
  │
  └─ 391 have max h⁰ ≤ 2 ──────────────────── 38% fail
```

---

## 3. Top Candidates

### Current Leaderboard (v5.2, 100-point SM composite)

| Rank | ID | Score | Hierarchy | MBD | Vol-Hier | Clean | c₂ stab | Tier |
|------|----|-------|-----------|------|----------|-------|---------|------|
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
**Tier C** = high score but fragile geometry (0% c₂ stability).

**Observations**:
- **h27 is a fibration-rich zone**: all 6 T3-analyzed h27 candidates have SM+GUT gauge groups
- h30/P289 (score 89) remains the champion with su(3) × su(17) × U(1)^10
- h27/P22835 (score 86) has **6 fibrations** — the most of any top-10 candidate — with su(2) × su(4) × su(8) or e7 × su(7)
- h27/P11889 (score 83) has **62 clean bundles** — new record among top-10 if we count h27
- The h28 cluster (P874/P186/P187) has the best triangulation stability (35–55%) but no SM/GUT fibrations
- h27/P13954 (score 85) has 25% c₂ stability — best among h27 candidates with SM+GUT

### Legacy Top-20 (v3–v4, 26-point scoring — superseded)

These candidates were identified during the early h13–h24 scan. They provided proof-of-concept for the pipeline but are outscored by the h28 champions under the 100-point SM composite.

| Rank | Polytope | Score (v4) | Clean h⁰=3 | max h⁰ | K3 | Ell | Notes |
|------|----------|------------|------------|--------|-----|-----|-------|
| 1 | h14/poly2 | 26/26 | 320 | 13 | 3 | 3 | Heterotic champion |
| 2 | h16/poly11 | 26/26 | 298 | 13 | 3 | 3 | 5 dP divisors |
| 3 | h17/poly96 | 25/26 | 252 | 65 | 2 | 1 | Highest max h⁰ |
| 4 | h17/poly63 | 26/26 | 218 | 40 | 5 | 10 | F-theory champion |
| 5 | h17/poly25 | 26/26 | 170 | 8 | 6 | 15 | 15 ell fib (record) |
| 6 | h15/poly61 | 25/26 | 110 | 4 | 3 | 3 | LVS τ=14,300 |
| 7 | h17/poly8 | 26/26 | 180 | 13 | 3 | 3 | LVS τ=2,208 |

---

## 4. Deep Analysis Results (T3)

### T3 Deep Analysis: Top 10 (20 random FRSTs each)

The top 10 candidates by v5.2 score were subjected to deep analysis:
triangulation stability (20 random FRSTs, c₂ + κ hashing), fibration
enumeration (K3 + elliptic), and gauge group identification via fiber
analysis.

**Key discovery**: h27 is a **fibration-rich zone** — all 6 h27 candidates
in the top 10 have SM+GUT gauge groups. This contrasts sharply with the
h28 cluster, which has zero fibrations despite higher stability.

#### Tier A — Paper-Ready (high score + stability, no fibrations)

| ID | Score | c₂ stab | Hier | Fibers | Key strength |
|----|-------|---------|------|--------|-------------|
| h28/P874 | 87 | 55% | 1,150 | 0 | Best stability overall |
| h28/P186 | 87 | 35% | 1,147 | 0 | h28 cluster sibling |
| h28/P187 | 84 | 55% | 1,160 | 0 | h28 cluster sibling |

#### Tier C — Score + Fibrations (SM+GUT gauge groups)

| ID | Score | c₂ stab | Hier | Fibers | Gauge group | Key strength |
|----|-------|---------|------|--------|-------------|-------------|
| h30/P289 | 89 | 0% | 34,318 | 1 | su(3) × su(17) × U(1)^10 | Champion, extreme hierarchy |
| h27/P22835 | 86 | 0% | 1,046 | 6 | su(2)×su(4)×su(8) or e7×su(7) | Most fibrations in top 10 |
| h27/P13954 | 85 | 25% | 695 | 1 | su(2)×su(8) or e7×su(12) | Best c₂ stab with SM gauge |
| h27/P1085 | 83 | 0% | 731 | 3 | su(2)×su(6)×su(6)×su(12) | Instanton divisor |
| h27/P1520 | 83 | 0% | 17,287 | 1 | su(13)×su(7)×U(1)^6 | Second-highest hierarchy |
| h27/P11889 | 83 | 0% | 5,498 | 3 | su(6)×su(11)×su(5) | 62 clean bundles |
| h27/P22799 | 83 | 0% | 1,026 | 1 | su(2)×su(8) or e7×su(11) | Instanton divisor |

### Legacy Deep Pipeline (12 complete, v3–v4, 26-point scoring)

These were the first candidates to receive full pipeline analysis.
Key results preserved for reference:

- **h14/poly2**: 320 clean bundles, 3 Swiss cheese directions (τ=58.5), first heterotic champion
- **h17/poly25**: 15 elliptic fibrations (record), 6 K3, triple-threat (heterotic + F-theory + LVS)
- **h15/poly61**: Swiss cheese τ=14,300 (extreme LVS), 0 dP (−1 point)
- **h17/poly63**: 218 clean bundles, max h⁰=40, 10 elliptic fibrations
- **h16/poly11** (298 clean), **h18/poly34** (184 clean), **h17/poly8** (180 clean, τ=2,208)
- All 12 runs: see [FINDINGS.md](FINDINGS.md)

### h13/poly1 — Benchmark (Score: 18/20, legacy scoring)

The original benchmark candidate. Full write-up in [FINDINGS.md](FINDINGS.md).

- h¹¹=13, h²¹=16, χ=−6
- **25 completely clean bundles**
- 3 dP divisors, Swiss cheese τ=10.0

### Polytope 40 (h15/poly40) — Pipeline Score: 10/20

Extensively studied but definitively limited. Write-up in [FINDINGS.md](FINDINGS.md).

- h¹¹=15, h²¹=18, χ=−6
- **Max h⁰ = 2** (rigorously proven via 7-script audit)
- 116 three-divisor χ=3 bundles, 2 single-divisor
- 11 del Pezzo divisors (dP₁ through dP₇)
- Swiss cheese: τ=4.0, V=17,506
- Z₂ symmetry
- **No line bundle has h⁰ = 3. Do not re-investigate this polytope for line bundle h⁰.**

---

## 5. Ruled Out — Don't Re-Check These

### 5a. Specific Polytopes

| Polytope | What Was Tried | Why It Fails | Evidence |
|----------|---------------|--------------|----------|
| h15/poly40 | Line bundle h⁰=3 search | Max h⁰ = 2, rigorously proven | Koszul + lattice points, 7-script dragon slayer series |
| Ample Champion (h11=2, h21=29) | Z₃×Z₃ quotient to χ=−6 | Pure g₁, g₂ have fixed curves → singular quotient | Numerical optimizer found \|P\|² ≈ 10⁻⁸⁸ on fixed locus |
| Ample Champion | Diagonal Z₃ quotient | Gives χ=−18 (9 generations), not −6 | Hodge number calculation |

### 5b. General Negative Results

| Claim | Scope | Proof |
|-------|-------|-------|
| **No nef h⁰=3 bundles exist** | All 1,025 scanned polytopes | Min Mori pairing < 0 for every χ=3 bundle found. Kodaira vanishing never applies. |
| **K3 + elliptic fibrations are universal** | All 157 T1.5 survivors | Every χ=−6 polytope at h¹¹≥13 has both K3 and elliptic fibrations. This is not a discriminator. |
| **Non-favorable polytopes dominate** | 705/1025 = 69% | Most χ=−6 polytopes are non-favorable. The strongest candidates are ALL non-favorable. |
| **cohomCalg is blocked** at high h¹¹ | h¹¹ ≥ 15 typically | SR ideal exceeds 64 generators → hard failure. Must use Koszul or other methods. |
| **h⁰ distribution peaks at 1–3** | 1,025 polytopes | Distribution: h⁰_max = 1 (316), 2 (76), 3 (249), 4 (117), 5 (42), 6+ (225) |

### 5c. CYTools Bugs That Caused False Results

These bugs wasted significant time. If you're using CYTools 1.4.5, be aware:

| Bug | Description | Impact | Workaround |
|-----|-------------|--------|------------|
| B-11 | `second_chern_class(in_basis=True)` returns wrong-size vector for non-favorable polytopes | 705/1025 polytopes invisible in scan v1 | Use `h11_eff = len(div_basis)` as working dimension |
| #2 | Intersection numbers have toric vs basis coordinate confusion | Wrong D³, wrong χ computation | Always use `in_basis=True` |
| #3 | Mori cone: 15-dim divisor vs 20-dim Mori generators | Index mismatch in nef check | Explicit index mapping to basis |
| #5 | cohomCalg hard limit of 64 SR generators | Cannot compute cohomology on complex polytopes | Use Koszul pipeline instead |
| #7 | `glsm_linear_relations()` includes non-character translations | Misleading for linear equivalence | Check dimensions manually |

---

## 6. What Needs Doing Next

Ordered by expected impact:

1. **Stage 5: Higher-rank bundles on h28 champions** — `rank_n_bundles.py` has been tested on h14/poly2 only. Run SU(4)/SU(5) direct-sum and monad scanners on h28/P874, h28/P186, h28/P187. Find a truly stable (not just polystable) rank-4/5 bundle with net chirality = 3.

2. **Triangulation stability — expand sampling** — Top-20 sampled at 50 random FRSTs. Expand to 200+ for Tier A candidates to refine c₂ stability percentages and establish tighter confidence intervals.

3. **Picard-Fuchs in Mori coordinates** — The GL=12/D₆ polytope has a closed-form period formula and 26 D₆-invariant Yukawa couplings. Derive the PF PDE system in 6 Mori coordinates for exact period integrals.

4. **F-theory discriminant locus** — h17/poly25 has 15 elliptic fibrations (record). Classify singular fibers (Kodaira types) to determine gauge algebras.

5. **Low-h¹¹ rescore** — Rescore h13–h19 legacy candidates under v5.2. Some may rank competitively despite lower h¹¹_eff.

6. **Paper draft** — Tier A candidates (P874, P186, P187) + triangulation stability methodology are paper-ready. Draft structure in [paper_outline.md](paper_outline.md).

---

## 7. How to Run the Pipeline

The current pipeline is v5.2, deployed on the Hetzner server (16-core).

```bash
# Scan a range of h11 values (v5.2 pipeline)
python v4/pipeline_v4.py --scan --h11 28 --limit 1000 -w 12

# Scan with deeper coverage (50K polytopes at one h11)
python v4/pipeline_v4.py --scan --h11 28 --limit 50000 -w 12

# Deep analysis: top N candidates, 50 random FRSTs each
python v4/pipeline_v4.py --deep --top 20

# Rescore all existing T2 records (after scoring formula changes)
python v4/pipeline_v4.py --rescore
```

Results go into `v4/cy_landscape_v4.db` (SQLite). Query with `v4/review_champions.py` or direct SQL.
