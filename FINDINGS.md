# Findings

Detailed write-ups of key results. For the quick summary, see [README.md](README.md). For the ruled-out list, see [CATALOGUE.md](CATALOGUE.md).

---

## 0. v4 Landscape Trends — h22-30 (9,000 polytopes, 1,134 T2-scored)

**Date**: 2026-02-26. **Database**: `v4/cy_landscape_v4.db` (3.1 MB).

### New Champion: h30/P289 (SM Score: 82)

| Property | h30/P289 | Population avg |
|----------|----------|---------------|
| SM score | **82** | 57.4 |
| h11_eff | 20 | 18.1 |
| gap | 10 | 6.2 |
| n_clean | 12 | 25.3 |
| yukawa_hierarchy | **34,318** | 311 |
| lvs_score | **0.00178** | 0.0172 |
| yukawa_rank | 147 | 130 |
| volume_form | swiss_cheese | — |
| n_k3_fib | 3 | 2.9 |
| n_ell_fib | 1 | 1.8 |

h30/P289 has **110× the population-average yukawa hierarchy** and elite-tier
LVS quality. It achieves the highest SM score in the database despite having
only 12 clean bundles — demonstrating that **quality of Yukawa texture
dominates quantity of clean bundles** as a predictor of SM-like physics.

### Top 10 Polytopes (v4 scoring)

| Rank | ID | Score | clean | yuk_h | lvs | eff | gap |
|------|-----------|-------|-------|--------|--------|-----|-----|
| 1 | h30/P289 | 82 | 12 | 34,318 | 0.0018 | 20 | 10 |
| 2 | h24/P479 | 79 | 64 | 8,449 | 0.0133 | 19 | 5 |
| 3 | h23/P283 | 79 | 22 | 2,821 | 0.0031 | 20 | 3 |
| 4 | h24/P88 | 79 | 46 | 2,256 | 0.0023 | 20 | 4 |
| 5 | h23/P97 | 79 | 52 | 1,650 | 0.0227 | 18 | 5 |
| 6 | h25/P411 | 79 | 44 | 1,597 | 0.0043 | 19 | 6 |
| 7 | h24/P48 | 79 | 24 | 1,345 | 0.0032 | 18 | 6 |
| 8 | h25/P934 | 78 | 22 | 1,666 | 0.0022 | 20 | 5 |
| 9 | h24/P247 | 77 | 34 | 2,054 | 0.0053 | 19 | 5 |
| 10 | h27/P68 | 76 | 18 | 624 | 0.0002 | 19 | 8 |

### Key Landscape Trends

1. **Yukawa hierarchy and LVS quality are orthogonal** (Pearson r = −0.027).
   These are independent axes of SM quality — not redundant.

2. **Score achievability drops monotonically**: 31.7% of h22 polytopes
   have both clean≥10 and yuk_h≥100, but only 2.9% at h29.

3. **n_dp anti-correlates with score**: fewer del Pezzo divisors → higher
   SM scores. Elite polytopes average n_dp=5.0 vs population 6.5.

4. **Volume hierarchy > 1000 predicts high scores**: avg 59.9 vs 53.4
   for vol_hierarchy < 100. Currently unscored — v5 candidate.

5. **yukawa_rank sweet spot is 140-159**: optimal intersection ring
   complexity. Above 160, hierarchy drops back.

6. **h11_eff=19 vs 20 paradox**: eff=19 has higher *average* quality;
   eff=20 has higher *peak* quality (the champion). Extra degree of
   freedom enables both excellence and mediocrity.

---

## 0.1. v4.1 Landscape Trends — h22-40 (19,000 polytopes, 1,300 T2-scored)

**Date**: 2026-02-26. **Database**: `v4/cy_landscape_v4.db` (5.7 MB).
**Pipeline version**: v4.1 (EFF_MAX=22, dp_divisors→vol_hierarchy, yukawa_hierarchy 25→27).

### New Champions: h28/P874, h28/P187, h28/P186, h30/P289 (SM Score: 84)

Four polytopes now share the top score of **84** (up from 82 in v4.0). Three
are a tight cluster at h28 (P186/P187/P874) that were **inaccessible at
EFF_MAX=20** — they have h11_eff=21-22 and were unlocked by the v4.1 ceiling
raise. The fourth is the returning champion h30/P289, rescored from 82→84 by
the weight redistribution.

| Property | h28 cluster (avg) | h30/P289 | Population avg |
|----------|-------------------|----------|----------------|
| SM score | **84** | **84** | 56.4 |
| h11_eff | 21.7 | 20 | 18.4 |
| gap | 6.3 | 10 | 6.2 |
| n_clean | 14 | 12 | 25 |
| yukawa_hierarchy | **1,152** | **34,318** | 650 |
| volume_hierarchy | **1,716** | **1,737** | 600 |
| yukawa_rank | 154 | 147 | 130 |
| kappa_signature | (1,21) | (1,19) | varies |
| volume_form | swiss_cheese | swiss_cheese | swiss_cheese |
| blowdown fraction | 0.93 | 0.88 | 0.80 |
| n_dp | 10 | 7 | 6 |

**Key observation**: The h28 cluster and h30/P289 reach the same score via
*different mechanisms*. h30/P289 has 30× higher yukawa hierarchy (maxing
out the 27-point component) but lower blowdown fraction. The h28 trio have
moderate yukawa hierarchy but near-perfect Mori cone blowdown (93%) and
higher d3 diversity (10-12 distinct values vs 6).

### Top 15 Polytopes (v4.1 scoring)

| Rank | ID | Score | eff | gap | yuk_h | vol_h | clean | d3_n |
|------|-----------|----|-----|-----|--------|--------|-------|------|
| 1 | h28/P874 | 84 | 22 | 6 | 1,150 | 1,657 | 14 | 10 |
| 2 | h28/P187 | 84 | 22 | 6 | 1,160 | 1,766 | 14 | 12 |
| 3 | h28/P186 | 84 | 21 | 7 | 1,147 | 1,725 | 14 | 10 |
| 4 | h30/P289 | 84 | 20 | 10 | 34,318 | 1,737 | 12 | 6 |
| 5 | h27/P219 | 79 | 21 | 6 | 901 | 1,451 | 12 | 10 |
| 6 | h25/P411 | 79 | 19 | 6 | 1,597 | 423 | 44 | 14 |
| 7 | h24/P479 | 79 | 19 | 5 | 8,449 | 300 | 64 | 16 |
| 8 | h24/P88 | 79 | 20 | 4 | 2,256 | 1,080 | 46 | 23 |
| 9 | h24/P48 | 79 | 18 | 6 | 1,345 | 830 | 24 | 18 |
| 10 | h23/P283 | 79 | 20 | 3 | 2,821 | 810 | 22 | 16 |
| 11 | h23/P97 | 79 | 18 | 5 | 1,650 | 442 | 52 | — |
| 12 | h25/P934 | 78 | 20 | 5 | 1,666 | 1,831 | 22 | — |
| 13 | h32/P94 | 77 | 20 | 12 | 2,759 | 877 | 42 | — |
| 14 | h32/P42 | 77 | 20 | 12 | 1,022 | 794 | 60 | — |
| 15 | h26/P305 | 76 | 20 | 6 | 2,991 | 3,973 | 10 | — |

### EFF_MAX=22 Impact

91 new polytopes with h11_eff ∈ {21, 22} entered the scoring pipeline:
- **38 at eff=21**, **53 at eff=22** reached T2
- 3 of the 4 global champions (the h28 cluster) are in this group
- avg score at eff=21-22 is 52 (below eff=19-20's 60), but *peak* quality
  is the highest in the entire dataset
- Confirms the v4.0 "paradox": extra degrees of freedom enable both
  excellence and mediocrity — EFF_MAX=22 was the right call

### Updated Correlations (n=1,300)

| Pair | Pearson r | Interpretation |
|------|-----------|----------------|
| yukawa_hierarchy ↔ volume_hierarchy | **+0.006** | Still orthogonal (was −0.027) |
| yukawa_hierarchy → sm_score | **+0.214** | Moderate predictor |
| volume_hierarchy → sm_score | **+0.003** | Near-zero (surprise!) |
| gap → sm_score | **−0.336** | Gap anti-correlates — lower gap = higher score |
| n_dp → sm_score | **−0.089** | Weak anti-correlation (was −0.19) |
| n_clean → sm_score | **+0.511** | Strongest predictor |

**Surprise**: volume_hierarchy has near-zero correlation with score despite
being designed as a positive indicator. The 5 points it contributes help at
the elite level (all score-84 polytopes have vol_h > 1,600) but don't
discriminate across the broader population. This is the hallmark of a good
*threshold* feature — only matters at the top.

### Landscape Fertile Window

| h11 | Total | T1+ | T2+ | T2% | Max Score |
|-----|-------|-----|-----|-----|-----------|
| 22 | 1,000 | 632 | 281 | 28.1% | 75 |
| 23 | 1,000 | 453 | 235 | 23.5% | 79 |
| 24 | 1,000 | 380 | 184 | 18.4% | 79 |
| 25 | 1,000 | 242 | 138 | 13.8% | 79 |
| 26 | 1,000 | 282 | 113 | 11.3% | 76 |
| 27 | 1,000 | 192 | 63 | 6.3% | 79 |
| 28 | 1,000 | 182 | 95 | 9.5% | **84** |
| 29 | 1,000 | 91 | 39 | 3.9% | 73 |
| 30 | 1,000 | 128 | 56 | 5.6% | **84** |
| 31 | 1,000 | 52 | 27 | 2.7% | 70 |
| 32 | 1,000 | 54 | 41 | 4.1% | 77 |
| 33 | 1,000 | 31 | 7 | 0.7% | 65 |
| 34 | 1,000 | 17 | 15 | 1.5% | 70 |
| 35 | 1,000 | 11 | 3 | 0.3% | 62 |
| 36 | 1,000 | 6 | 2 | 0.2% | 30 |
| 37 | 1,000 | 3 | 0 | 0.0% | — |
| 38 | 1,000 | 0 | 0 | 0.0% | — |
| 39 | 1,000 | 1 | 1 | 0.1% | 49 |
| 40 | 1,000 | 0 | 0 | 0.0% | — |

**Key findings**:

1. **The fertile window is h22-35**, beyond which T2 achievability drops
   below 0.3%. The landscape is effectively barren at h37+.

2. **h28 is the sweet spot**: exceptional peak quality (score=84) with
   reasonable T2 yield (9.5%). It outperforms even h22-25 on *peak*
   despite having 3× lower T2 yield.

3. **h32 and h34 have anomalously high T1→T2 pass rates** (76% and 88%
   respectively, vs ~50% average). This means the polytopes that survive
   T0+T1 screening at high h11 are disproportionately good — the filter
   is working well. h32 also peaks at 77, the highest above h30.

4. **h39/P0 — the lone survivor at gap=18**: a single polytope passes all
   the way through at h39 (score=49, eff=21, aut=2). Remarkable survival
   — it has the largest gap (18) in the entire database. Swiss cheese
   volume form with vol_hierarchy=529.

5. **Monotonic T2 decline is not perfectly smooth**: h28 > h27 in T2 yield,
   h32 > h31, h34 > h33. Even-h₁₁ values sometimes have structural
   advantages (symmetry of the polytope lattice).

### What Separates 79 from 84

| Property | Score=84 (n=4) | Score=79 (n=7) | Score=70 (n=28) |
|----------|----------------|----------------|-----------------|
| avg eff | 21.2 | 19.3 | 18.8 |
| avg gap | 7.2 | 5.0 | 7.8 |
| avg yuk_h | 9,444 | 2,717 | 1,326 |
| avg vol_h | 1,721 | 762 | 1,575 |
| avg d3_n | 10 | 17 | 13 |
| blowdown frac | 0.931 | 0.721 | 0.856 |

The leap from 79→84 requires: higher h11_eff (21+ vs 19), higher yukawa
hierarchy (9,400+ vs 2,700), and near-perfect Mori blowdown (93% vs 72%).
Interestingly, score-79 polytopes have *more* d3 diversity (17 vs 10) —
the 84s trade flux diversity for Yukawa/geometric excellence.

### Chi = −6 Universality

**Every single polytope** in the 19,000-row database has χ = −6. This is by
construction — the h₁₁ range 22-40 combined with the Kreuzer-Skarke
database constraint produces only χ = −6 manifolds. All T2-scored polytopes
are swiss_cheese volume form. These are not tunable parameters — they are
structural constraints of the landscape at this h₁₁ range.

### Theoretical Ceiling: Score = 84 is Near-Maximum

The current scoring formula has a **hard ceiling near 84-87** for the
chi = −6 landscape. Why:

- **LVS is blocked**: 0 of 117 score-70+ polytopes have lvs_score > 0.1.
  The lvs_binary (5 pts) and lvs_quality (10 pts) components are
  effectively unreachable — 15 points stranded.
- **Fibration SM is blocked**: 0 polytopes have has_SM=1 or has_GUT=1.
  The fibration_sm component (3 pts) is unreachable.
- **Theoretical maximum achievable**: ~82 pts (100 − 15 lvs − 3 fib_sm).
  The h28 champions already score 84, *above* this estimate, because
  multiple sub-components each top out at less-than-maximum.

**Implication**: To break 84, we would need either (a) polytopes with
genuine LVS compatibility (larger strong Swiss cheese hierarchies), or
(b) a scoring revision that redistributes the stranded 18 points. Option
(b) risks score inflation without physical insight — the 15 LVS points
represent *real physics* that these manifolds lack.

---

## 1. h13/poly1 — Benchmark Candidate (Pipeline Score: 18/20)

**Date**: 2026-02-23. **Script**: [pipeline_h13_P1.py](pipeline_h13_P1.py).

The original benchmark for the pipeline. Smallest h¹¹ in the landscape, completely clean line bundles. Superseded in all metrics by h14/poly2 (320 clean, 26/26) but remains the standard test polytope.

### Geometry
- h¹¹ = 13, h²¹ = 16, χ = −6 (native 3-generation, no quotient needed)
- 18 toric coordinates, 17 rays, non-favorable (h¹¹_eff = 13)
- c₂ = [16, 2, 18, 18, 12, 6, −4, −2, −2, 2, −4, −4, −4]
- 101 intersection entries, 73 Mori cone generators, 87 SR ideal generators

### Divisor Structure
- **3 del Pezzo**: e₁ (dP₄), e₅ (dP₆), e₉ (dP₄)
- **1 K3-like**: e₄ (D³=0, c₂·D=12)
- **5 high-D³ rigid**: e₆, e₇, e₈, e₁₀, e₁₁, e₁₂ (D³ = 7–8)
- **3 rigid (D³<0)**: e₀, e₂, e₃
- All 13 divisors rigid (h¹·⁰ = h²·⁰ = 0)

### Swiss Cheese
e₁₂ (toric idx 17): τ = 10.0, V = 308,352, τ/V²ᐟ³ = 0.0022. Excellent LVS hierarchy.

### Line Bundles
- **11,054 total χ = ±3 bundles** (5,527 each sign)
- **25 completely clean**: h⁰ = 3, h¹ = h² = h³ = 0
- 76 with h⁰ ≥ 3, max h⁰ = 6
- **Zero nef bundles** (min Mori pairing = −19)

### Why It's the Best
1. Only polytope with BOTH h⁰ = 3 bundles AND Swiss cheese structure
2. 25 completely clean bundles (no vector-like pairs, no higher cohomology)
3. Smallest h¹¹ in the χ = −6 landscape → simplest geometric complexity
4. dP₆ divisor (e₅) → candidate for E₆ instanton effects

### Open Questions
- Stability of the 25 clean bundles (slope or Gieseker)?
- Can rank-4/5 bundles be built from these line bundles?
- Full fibration classification (K3, elliptic)?
- Does e₁₂ correspond to a blow-up of a del Pezzo?

---

## 2. h17/poly25 — F-Theory + Triple-Threat Champion (Pipeline Score: 26/26, 170 clean, 15 elliptic)

**Date**: 2026-02-23. **Script**: `python pipeline.py --h11 17 --poly 25`. **Output**: [results/pipeline_h17_P25_output.txt](results/pipeline_h17_P25_output.txt).

New record holder for elliptic fibrations — **15 elliptic fibrations** (50% more than the previous record of 10). Also has 6 K3 fibrations. Combined with Swiss cheese structure (τ=56) and 170 clean bundles, this is the only candidate that excels at heterotic, F-theory, AND Large Volume Scenario simultaneously — the "triple-threat."

### Geometry
- h¹¹ = 17, h²¹ = 20, χ = −6 (native 3-generation, no quotient needed)
- 19 toric coordinates, non-favorable

### Divisor Structure
- **2 del Pezzo**: e₂ (dP₇), e₃ (dP₈)
- **1 K3-like**
- **4 rigid**

### Swiss Cheese
τ = 56.0, ratio = 0.00370. Viable LVS hierarchy.

### Line Bundles
- **18,362 χ = ±3 bundles** (matching h17/poly63)
- **170 completely clean**: h⁰ = 3, h¹ = h² = h³ = 0
- 490 with h⁰ ≥ 3, max h⁰ = 8

### Fibrations
- **6 K3 fibrations** — tied for most of any candidate
- **15 elliptic fibrations** — **ALL-TIME RECORD**. 50% more than previous best (h17/poly63 at 10)

### Scorecard: 26/26 (PERFECT)
- χ = −6: 3/3 ✓
- |χ|/2 = 3 generations: 3/3 ✓
- h⁰ ≥ 3 exists: 3/3 ✓
- Clean bundles: 5/5 ✓ (170)
- Max h⁰: 2/2 ✓ (8)
- Swiss cheese: 3/3 ✓ (τ = 56.0)
- K3 fibrations: 2/2 ✓ (6)
- Elliptic fibrations: 2/2 ✓ (15!)
- del Pezzo divisors: 1/1 ✓ (2)
- D³ diversity: 1/1 ✓
- h¹¹ tractable: 1/1 ✓ (17)

### Why It's the Triple-Threat Champion
1. **15 elliptic fibrations** — all-time record. Each is a distinct F-theory compactification pathway with potential non-abelian gauge groups.
2. **6 K3 fibrations** — tied for most of any candidate. Combined with 15 ell, gives 21 total fibrations (far exceeding any other candidate).
3. **Swiss cheese τ = 56** — viable LVS moduli stabilization. Not the strongest (h15/poly61 has τ=14,300), but functional.
4. **170 clean bundles** — solid heterotic target space.
5. **Only candidate excelling at all three approaches** — heterotic (170 clean), F-theory (15 ell), and LVS (Swiss cheese).

### Comparison — Triple-Threat Candidates

| Metric | h17/poly25 | h16/poly63 | h17/poly8 | h16/poly11 |
|--------|-----------|-----------|-----------|------------|
| Score | 26/26 | 26/26 | 26/26 | 26/26 |
| Clean bundles | 170 | 78 | 180 | **298** |
| Elliptic fib. | **15** | 6 | 3 | 3 |
| K3 fib. | **6** | 4 | 3 | 3 |
| Swiss τ | 56 | **836** | 2,208 | 150 |
| dP divisors | 2 | 5 | 4 | 5 |
| Best for... | F-theory | Balanced | LVS | Heterotic |

### Open Questions
- Which of the 15 elliptic fibrations yield the richest gauge algebras (Kodaira classification)?
- Can the 6 K3 fibrations be leveraged for heterotic/F-theory duality constructions?
- Does the modest τ=56 suffice for realistic moduli stabilization, or is tuning needed?

---

## 2a. h17/poly63 — Former F-Theory Champion (Pipeline Score: 26/26, 218 clean)

**Date**: 2026-02-22. **Script**: `python pipeline.py --h11 17 --poly 63`. **Output**: [results/pipeline_h17_P63_output.txt](results/pipeline_h17_P63_output.txt).

The richest fibration structure of any candidate — 5 K3 + 10 elliptic fibrations. Max h⁰ = 40, the highest of any polytope scoring T2=45. Prime target for F-theory model building.

### Geometry
- h¹¹ = 17, h²¹ = 20, χ = −6 (native 3-generation, no quotient needed)
- 18 toric coordinates, 17 rays, non-favorable (h¹¹_eff = 13)
- c₂ = [36, 18, 2, 16, 18, 10, −4, 2, 6, 8, 8, −18, −6]
- 97 intersection entries, 65 Mori cone generators, 80 SR ideal generators
- SHA-256 fingerprint: 3cc2448f341e6e9a

### Divisor Structure
- **6 del Pezzo**: e₂ (dP₄), e₅ (dP₈), e₇ (dP₄), e₈ (dP₆), e₉ (dP₇), e₁₀ (dP₇)
- **1 K3-like**: e₀ (D³=0, c₂·D=36)
- **6 rigid**: e₁, e₃, e₄, e₆, e₁₁, e₁₂

### Swiss Cheese
e₁₂ (toric idx 17): τ = 84.0, V = 853,536, τ/V²ᐟ³ = 0.0093. Good LVS hierarchy.

### Line Bundles
- **14,458 total χ = ±3 bundles** (7,229 each sign)
- **218 completely clean**: h⁰ = 3, h¹ = h² = h³ = 0
- 922 with h⁰ ≥ 3, max h⁰ = 40
- **1 nef bundle** (the rarest finding — almost all χ=−6 bundles are non-nef)
- 61 distinct D³ values among clean bundles (range [−59, 59])

### Fibrations
- **5 K3 fibrations** — base P¹ directions: [0,1,1,0], [0,0,0,1], [0,0,1,1], [0,1,0,−1], [0,1,0,0]
- **10 elliptic fibrations** — the most of any fully-analyzed candidate. Rich 2D reflexive subpolytope structure in the dual.

### Why It's the F-Theory Champion
1. **10 elliptic fibrations** — more than any other analyzed polytope. Each is a distinct F-theory compactification pathway.
2. **6 del Pezzo divisors** — twice as many as h14/poly2. Each dP divisor supports non-perturbative E-type effects.
3. **Max h⁰ = 40** — extremely large global sections suggest deep bundle structure for rank-4/5 constructions.
4. **218 clean bundles with zero higher cohomology** — broad target space for heterotic embedding.

### Comparison with Heterotic Champion

| Metric | h14/poly2 | h17/poly63 | Winner |
|--------|-----------|------------|--------|
| Score | 26/26 | 26/26 | Tie |
| Clean bundles | **320** | 218 | h14/poly2 |
| Max h⁰ | 13 | **40** | h17/poly63 |
| K3 fibrations | 3 | **5** | h17/poly63 |
| Elliptic fib. | 3 | **10** | h17/poly63 |
| dP divisors | 3 | **6** | h17/poly63 |
| Swiss cheese | **3 dirs** | 1 dir | h14/poly2 |
| h¹¹ | **14** | 17 | h14/poly2 |

### Open Questions
- Which of the 10 elliptic fibrations gives the richest gauge algebra from singular fibers?
- Can rank-4/5 bundles be built leveraging the 6 dP divisors?
- Does the single nef bundle have special significance?

---

## 2a′. h16/poly63 — Triple-Threat #2 (Pipeline Score: 26/26, 78 clean, τ=836)

**Date**: 2026-02-23. **Script**: `python pipeline.py --h11 16 --poly 63`. **Output**: [results/pipeline_h16_P63_output.txt](results/pipeline_h16_P63_output.txt).

Second-best triple-threat candidate. Strong across all three compactification approaches with particularly good LVS hierarchy (τ=836, 3rd overall) and 5 del Pezzo divisors.

### Geometry
- h¹¹ = 16, h²¹ = 19, χ = −6, non-favorable

### Divisor Structure
- **5 del Pezzo**: e₀ (dP₈), e₁ (dP₈), e₃ (dP₆), e₅ (dP₄), e₉ (dP₅)
- **2 K3-like**
- **6 rigid**

### Swiss Cheese
τ = 836.2, ratio = 0.04192. Third-best LVS hierarchy overall (after h15/poly61 at 14,300 and h17/poly8 at 2,208).

### Line Bundles
- **12,736 χ = ±3 bundles** (each sign)
- **78 completely clean**: h⁰ = 3, h¹ = h² = h³ = 0
- 584 with h⁰ ≥ 3, max h⁰ = 37

### Fibrations
- **4 K3 fibrations**
- **6 elliptic fibrations**

### Scorecard: 26/26 (PERFECT)
All 26 points scored. Loses nothing.

### Status
✅ Full pipeline complete. 26/26 score.

---

## 2a″. h16/poly53 — Second-Most Clean Bundles (Pipeline Score: 23/26, 300 clean)

**Date**: 2026-02-23. **Script**: `python pipeline.py --h11 16 --poly 53`. **Output**: [results/pipeline_h16_P53_output.txt](results/pipeline_h16_P53_output.txt).

Second-highest clean bundle count of any candidate (300, behind only h14/poly2 at 320). Rich fibration structure (5 K3 + 10 ell) and 6 dP divisors. The only weakness: **no Swiss cheese structure** → loses 3 LVS points.

### Geometry
- h¹¹ = 16, h²¹ = 19, χ = −6, non-favorable

### Divisor Structure
- **6 del Pezzo**: e₂ (dP₈), e₄ (dP₄), e₅ (dP₇), e₉ (dP₅), e₁₀ (dP₅), e₁₁ (dP₄), e₁₂ (dP₄)
- **0 K3-like**
- **10 rigid**

### Swiss Cheese
None found. This is the critical weakness.

### Line Bundles
- **18,362 χ = ±3 bundles** (each sign)
- **300 completely clean**: h⁰ = 3, h¹ = h² = h³ = 0
- 1,100 with h⁰ ≥ 3, max h⁰ = 16

### Fibrations
- **5 K3 fibrations**
- **10 elliptic fibrations**

### Scorecard: 23/26
- Swiss cheese: **0/3 ✗** (no Swiss cheese structure found)
- All other categories: full marks

### Why It Matters
300 clean bundles is tantalizing — nearly matching the heterotic champion. This is an excellent heterotic + F-theory candidate (5 K3 + 10 ell), but LVS moduli stabilization would require alternative approaches (e.g., KKLT).

### Status
✅ Full pipeline complete. 23/26 score.

---

## 2a‴. h19/poly16 — High-h¹¹ Candidate (Pipeline Score: 22/26, 86 clean)

**Date**: 2026-02-23. **Script**: `python pipeline.py --h11 19 --poly 16`. **Output**: [results/pipeline_h19_P16_output.txt](results/pipeline_h19_P16_output.txt).

Highest h¹¹ in the full pipeline set. Rich fibration structure (5 K3 + 10 ell) and 5 dP divisors, but loses points on Swiss cheese (none) and h¹¹ tractability (19 > 18).

### Geometry
- h¹¹ = 19, h²¹ = 22, χ = −6, non-favorable

### Divisor Structure
- **5 del Pezzo**
- **0 K3-like**
- **7 rigid**

### Line Bundles
- **86 completely clean**: h⁰ = 3, h¹ = h² = h³ = 0
- 564 with h⁰ ≥ 3, max h⁰ = 27

### Fibrations
- **5 K3 fibrations**
- **10 elliptic fibrations**

### Scorecard: 22/26
- Swiss cheese: **0/3 ✗**
- h¹¹ tractable (≤18): **0/1 ✗** (h¹¹=19)

### Status
✅ Full pipeline complete. 22/26 score.

---

## 2b. h17/poly8 — Second-Best T2=45 Scorer (159 clean)

**Date**: 2026-02-24. **Script**: [tier2_screen.py](tier2_screen.py).

Second highest clean h⁰ = 3 count among all polytopes scoring T2 = 45 (maximum). Strong fibration structure with balanced K3/elliptic content.

### Key Data
- h¹¹ = 17, h²¹ = 20, χ = −6, non-favorable (h¹¹_eff = 13)
- 159 clean h⁰ = 3 line bundles
- 558 with h⁰ ≥ 3, max h⁰ = 13
- 12,928 total χ = ±3 bundles
- 3 K3 fibrations, 3 elliptic fibrations
- D³ range: [−60, 108], 152 distinct values

### Why It Matters
Among the 30 polytopes achieving the maximum T2 score, h17/poly8 has the second most clean bundles (159). Its balanced fibration structure (3 K3 + 3 elliptic) makes it a strong candidate for both heterotic and F-theory embeddings. Clean bundle count 6× that of h13/poly1.

### Status
Needs full pipeline run (Stages 1–4 deep analysis + scorecard).

---

## 2b′. h15/poly61 — LVS Champion (Pipeline Score: 25/26, 110 clean, τ=14,300)

**Date**: 2026-02-22 (discovered), 2026-02-23 (full pipeline). **Script**: `python pipeline.py --h11 15 --poly 61`. **Output**: [results/pipeline_h15_P61_output.txt](results/pipeline_h15_P61_output.txt).

Discovered in the expanded h15 scan (polytope index 61, invisible to original limit=100 scan). Now fully analyzed. **Best Large Volume Scenario candidate by a factor of 6.5×** — Swiss cheese τ = 14,300 vs previous best 2,208 (h17/poly8).

### Geometry
- h¹¹ = 15, h²¹ = 18, χ = −6, non-favorable
- SHA-256 fingerprint: 7ffc1e727a82fac4

### Divisor Structure
- **0 del Pezzo** (only weakness — loses 1 scorecard point)
- **1 K3-like**
- **6 rigid**
- 2 Swiss cheese directions, best: **τ = 14,300.0**, ratio = 0.04822

### Line Bundles
- **13,256 total χ = ±3 bundles**
- **110 completely clean**: h⁰ = 3, h¹ = h² = h³ = 0
- 338 with h⁰ ≥ 3, max h⁰ = 4 (modest but practical)
- 40 distinct D³ values among clean bundles (range [−52, 52])

### Fibrations
- **3 K3 fibrations**
- **3 elliptic fibrations**

### Scorecard: 25/26
- χ = −6: 3/3 ✓
- |χ|/2 = 3 generations: 3/3 ✓
- h⁰ ≥ 3 exists: 3/3 ✓
- Clean bundles: 5/5 ✓ (110)
- Max h⁰: 2/2 ✓ (4)
- Swiss cheese: 3/3 ✓ (τ = 14,300.0!)
- K3 fibrations: 2/2 ✓ (3)
- Elliptic fibrations: 2/2 ✓ (3)
- del Pezzo divisors: **0/1 ✗** (0 candidates)
- D³ diversity: 1/1 ✓ (40 distinct)
- h¹¹ tractable: 1/1 ✓ (15)

### Why It's the LVS Champion
1. **τ = 14,300** — 6.5× the previous best (h17/poly8 at τ = 2,208). The strongest LVS hierarchy of any candidate.
2. **Discovered only through scan expansion** — validates the decision to go beyond limit=100
3. **h¹¹ = 15** — lower than most top candidates → simpler moduli stabilization
4. **110 clean bundles → 7 more than T2 predicted** (103 → 110, 7% uplift from full enumeration)
5. **Balanced fibration structure** (3 K3 + 3 ell) — viable for both heterotic and F-theory

### Comparison with Other Top Candidates

| Metric | h15/poly61 | h17/poly8 | h14/poly2 |
|--------|-----------|-----------|----------|
| Score | 25/26 | 26/26 | 26/26 |
| Clean bundles | 110 | 180 | **320** |
| Swiss τ | **14,300** | 2,208 | 58.5 |
| dP divisors | 0 | 4 | 3 |
| K3 / Ell | 3/3 | 3/3 | 3/3 |
| h¹¹ | **15** | 17 | 14 |

### Open Questions
- Can the absence of dP divisors be compensated by other instanton sources?
- Does the extreme τ translate to viable moduli stabilization in a concrete flux model?
- Are rank-4/5 monad bundles available despite 0 dP divisors?

### Status
✅ Full pipeline complete. 25/26 score.

---

## 2b″. h15/poly127 — Highest T1 Score in Expanded Scan

**Date**: 2026-02-22. **Discovered by**: `scan_parallel.py` expanded h15 scan.

Highest T1 screening score among all new h15 polytopes: score 40, max h⁰ = 17, 8 del Pezzo divisors (most of any h15 candidate). Swiss cheese structure confirmed.

### Key Data (T1 screen)
- h¹¹ = 15, h²¹ = 18, χ = −6, favorable
- max h⁰ = 17, T1 score = 40
- 8 del Pezzo divisors (highest count at h15)
- Swiss cheese: τ = 193.5, ratio = 0.0035

### Status
Through T1 screen. Needs T2 + full pipeline.

---

## 2c. h14/poly2 — Heterotic Champion (Pipeline Score: 26/26, 320 clean)

**Date**: 2026-02-22. **Script**: `python pipeline.py --h11 14 --poly 2`. **Output**: [results/pipeline_h14_P2_output.txt](results/pipeline_h14_P2_output.txt).

Most clean h⁰ = 3 bundles of any polytope analyzed. Lowest h¹¹ (14) among top candidates. The strongest candidate for heterotic string compactification.

### Geometry
- h¹¹ = 14, h²¹ = 17, χ = −6, non-favorable (h¹¹_eff = 13)
- SHA-256 fingerprint: f6c14152f6f3b812

### Key Data (full pipeline)
- **320 clean h⁰ = 3 line bundles** (most of any candidate)
- 828 with h⁰ ≥ 3, max h⁰ = 13
- 14,608 total χ = ±3 bundles
- 3 K3 fibrations, 3 elliptic fibrations
- 61 distinct D³ values (range [−63, 63])
- 3 del Pezzo (dP₄, dP₄, dP₇), 2 K3-like, 6 rigid
- 3 Swiss cheese directions (best: e₉ τ=58.5, ratio=0.001)
- 1 nef bundle

### Why It's the Heterotic Champion
1. **320 clean bundles** — 12.8× more than h13/poly1, 1.5× more than h17/poly63
2. **h¹¹ = 14** — lowest among top candidates → simplest moduli stabilization
3. **3 Swiss cheese directions** — strongest LVS structure of any candidate
4. **L = O(±e₀)** — simplest clean bundle is a single-divisor 3-generation model

### Status
✅ Full pipeline complete. 26/26 score.

---

## 2c. h17/poly96 — Extreme max h⁰ = 65 (T2=39)

**Date**: 2026-02-24. Discovered in Codespace T2 batch.

The highest max h⁰ ever recorded on a χ = −6 polytope.

### Key Data
- h¹¹ = 17, h²¹ = 20, χ = −6, non-favorable (h¹¹_eff = 13)
- 227 clean h⁰ = 3 bundles
- 930 with h⁰ ≥ 3, **max h⁰ = 65**
- 10,208 total χ = ±3 bundles
- 2 K3 fibrations, 1 elliptic fibration

### Why It Matters
max h⁰ = 65 means very large global sections exist — this could enable exotic bundle constructions not possible on lower-h⁰ polytopes. The lower T2 score (39) is due to fewer fibrations, but the raw cohomological richness is unmatched.

---

## 3. Polytope 40 (h15/poly40) — Proven Dead End for Line Bundles

**Date**: 2026-02-22. **Scripts**: dragon_slayer series (40.py through 40i.py).

Extensively investigated. 7-script audit trail proves max h⁰ = 2. Do not re-investigate this polytope for line bundle h⁰ = 3.

### Geometry
- h¹¹ = 15, h²¹ = 18, χ = −6 (native 3-generation)
- 11 del Pezzo divisors (dP₁ through dP₇), 1 K3-like
- Swiss cheese: τ = 4.0, V = 17,506
- Z₂ symmetry, 116 three-divisor χ = 3 bundles

### The h⁰ = 2 Proof
Method: Koszul exact sequence on the CY hypersurface + lattice point counting on the ambient toric 4-fold + toric h¹ correction.

For ALL 119 χ = +3 bundles (coefficients up to ±3, 1–4 nonzero entries):
- **Max h⁰(X, D) = 2**
- h¹(V, D+K_V) = 0 for ALL bundles → Koszul formula is exact
- No Kodaira vanishing pathway (zero nef+big bundles; closest to nef: min Mori pairing = −2)
- cohomCalg blocked (97 SR generators > 64 limit)

### The Pipeline Score Problem
Original pipeline script hardcoded `proven_h0_3 = True` with the comment "We KNOW these exist from previous analysis" — without verification. This was the fabricated 20th point in the "20/20" score. Corrected score: 10/20 (see Scorecard in [CATALOGUE.md](CATALOGUE.md)).

### Still Interesting For
- Higher-rank vector bundles (monad construction) where h¹(V) = 3 might be achievable
- F-theory models using its K3/elliptic fibrations
- Teaching example of rigorous cohomology computation on toric CY3

---

## 4. Ample Champion (h11=2, h21=29, χ=−54) — Quotient Fails

**Date**: 2026-02-20. **Script**: [ample_champion_quotient.py](ample_champion_quotient.py).

### What Was Attempted
Find a freely-acting Z₃×Z₃ quotient to get χ = −54/9 = −6 (3 generations).

### What Works
- Z₃×Z₃ symmetry genuinely exists: g₁ = (0 4 5), g₂ = (1 2 3), commuting, order 3
- "Diagonal" elements g₁ᵃg₂ᵇ (a≠0 AND b≠0) act freely on the CY

### What Fails
- **Pure g₁, g₂ have fixed curves**: 2D fixed loci on the ambient toric variety intersect the CY in curves. Numerically confirmed: |P|² ≈ 10⁻⁸⁸ on fixed locus.
- **Full Z₃×Z₃ quotient is singular**: orbifold singularities along two fixed curve images
- χ = −6 is never achieved without resolution, which changes χ

### Salvaged
- Diagonal Z₃ acts freely → χ = −54/3 = −18 → 9 generations. Not 3, but documented.
- The orbifold path (resolve singularities) remains theoretically open but is a much harder calculation.

---

## 5. General Landscape Facts

### Non-Favorable Dominance
705/1025 (69%) of χ = −6 polytopes are non-favorable. These have h¹¹_eff < h¹¹, meaning the toric divisor basis doesn't span H¹·¹. Before Bug B-11 was fixed, all of these were invisible. Every top-20 T2 candidate except h15/poly33 is non-favorable.

### Fibration Universality
Every χ = −6 polytope in our scan at h¹¹ ≥ 13 has both K3 and elliptic fibrations. This is expected (generic CY3 at these Hodge numbers are fibered) but means fibration existence is not a useful discriminator. What varies is the *number* and *type* of fibrations — the top candidates have 3–6 of each.

### Bundle Abundance Distribution
From the full scan v2 (1,025 polytopes), max h⁰ distribution:

| max h⁰ | Count | Cumulative % |
|---------|-------|-------------- |
| 1 | 316 | 31% |
| 2 | 76 | 38% |
| 3 | 249 | 62% |
| 4–6 | 209 | 83% |
| 7–10 | 87 | 91% |
| 11–20 | 52 | 96% |
| 21–56 | 36 | 100% |

62% of polytopes have max h⁰ ≥ 3 — the geometric prerequisites for 3-generation models are abundant. The bottleneck is Stages 5–7 (non-abelian bundles, chirality, moduli stabilization).

---

## 6. Self-Mirror Polytope (h11=20, h21=20, χ=0)

**Date**: 2026-02-19. **Script**: various (archive/).

Not a 3-generation candidate (χ = 0), but mathematically notable:
- Self-mirror CY with h¹¹ = h²¹ = 20
- 3 K3 fibrations, 3 elliptic fibrations (highly symmetric structure)
- K3 fiber directions: [0,1,0,−1], [1,0,0,−1], [1,−1,0,0]
- Potential for F-theory compactifications (generations from brane geometry, not χ)
- Undocumented in recent systematic scans

Parked as a curiosity. May be relevant for F-theory path.

---

## 7. Expanded Scan Results (h15 complete, h16 in progress)

**Date**: 2026-02-22. **Script**: [scan_parallel.py](scan_parallel.py).

### Motivation

The original scan (`scan_chi6_h0.py`) capped at `limit=100` polytopes per h¹¹ value. This was fine for h13 (3 polytopes) and h14 (22), but left the vast majority of h15–17 unscanned. The expanded scan uses `scan_parallel.py` (4-worker multiprocessing) to cover them fully.

### h15 — 553/553 complete

| Metric | Value |
|--------|-------|
| Polytopes scanned | 553 (100%) |
| Hits (h⁰≥3) | 333 (60%) |
| Runtime | 9.2 min |
| Throughput | 1.0 poly/s |

New candidates discovered beyond original limit=100:
- **h15/poly 127**: max h⁰=17, 8 dP divisors, Swiss cheese (T1 score=40)
- **h15/poly 214**: max h⁰=15, 7 dP divisors, Swiss cheese (T1 score=40)
- **h15/poly 61**: **103 clean h⁰=3 bundles** (T2 #5 overall)
- **h15/poly 248**: max h⁰=16, Swiss cheese
- **h15/poly 94**: 36 clean bundles, 4 K3 + 4 elliptic fibrations
- 257 total new hits (poly index ≥ 100)

### h16 — 5,180/5,180 complete

| Metric | Value |
|--------|-------|
| Polytopes scanned | 5,180 (100%) |
| Hits (h⁰≥3) | 1,811 (35%) |
| Runtime | 52.9 min |
| Throughput | 1.6 poly/s |

T1→T1.5→T2 screening on top 30 hits:
- **T1**: 30 screened → 17/30 Swiss cheese. Best: h16/poly329 (score=41, max h⁰=15)
- **T1.5**: 20 screened → 19/20 T2-worthy (17s)
- **T2**: 20 screened → all 20 ★★★, 5 scored T2=45 (maximum). Best overall: h15/poly61 (T2=45, 103 clean)

New T2-notable from expanded scan:
- **h19/poly16**: T2=45, 69 clean, max h⁰=27, 5 K3 + 6 elliptic fibrations
- **h18/poly32**: T2=45, 49 clean, max h⁰=30, 4 K3 + 4 ell
- **h17/poly53**: T2=45, 45 clean, 3 K3 + 3 ell
- **h15/poly94**: T2=45, 36 clean, 4 K3 + 4 ell

### h17 — 38,735/38,735 complete

| Metric | Value |
|--------|-------|
| Polytopes scanned | 38,735 (100%) |
| T0.25 hits (h⁰≥3) | 10,624 (27.4%) |
| Deep-analyzed (Stage 1, top 200) | 200 |
| Fiber-classified (Stage 2) | 193 |
| Score 26/26 | **87** |
| SM gauge group (100%) | 193/193 |
| SU(5) GUT candidates | 166/193 (86%) |
| Runtime | 3 min (Codespace, 3 workers) |

This is a dramatic scaling jump — **87 perfect-score polytopes** at h17 vs. 19 at h11≤16 combined. The h17 landscape is the richest single Hodge number for χ=−6 candidate physics. See §10 for the full h17 analysis.

### h18 — in progress

~195,000 polytopes. T0.25 complete (100K→29,984 passes, 30%). T1 running on Hetzner (Docker, 14 workers): 5,745/29,984 (19%). ETA ~42 hrs.

### Impact on the Screening Pipeline

The expanded scan has fundamentally changed the leaderboard — h15/poly61 was discovered, fast-tracked through all tiers, and scored **25/26 on full pipeline** with τ=14,300. 36 total T2 entries now span h13–h19. The expanded h16 scan added 20 new T2 candidates, all quality-rated ★★★. This validates expanding the scan coverage as the most productive strategy for finding new physics candidates.

---

## 8. GL=12 / D₆ Polytope — Picard-Fuchs and Yukawa Study

**Date**: 2026-02-23. **Scripts**: [picard_fuchs.py](picard_fuchs.py). **Reference**: [GL12_GEOMETRY.md](GL12_GEOMETRY.md).

### Motivation

Among the 104 Hodge pairs with χ = −6, the polytope at `fetch_polytopes(h11=17, h21=20, lattice='N')` index 37 has the **largest lattice automorphism group**: |GL(Δ)| = 12, isomorphic to D₆ (dihedral group of the hexagon). This symmetry reduces the 20 complex structure moduli to just 6 invariant deformations, making Picard-Fuchs computation tractable.

### Key Results

**GKZ System:**
- A-matrix: 5×23 (from 23 dual lattice points), rank 5, β=(−1,0,0,0,0)
- Integer kernel: 18-dimensional
- D₆ orbit compression: 8 orbits on Δ*, rank(Ā)=2 → **6 invariant complex structure moduli** (h²¹_inv=6)
- 6 orbit-compressed Mori coordinates z₁…z₆ defining the invariant moduli space

**Closed-Form Period:**
- CT[P^k] = Σ_{a,γ} k!·(r−γ)! / [a!²·(γ+a)!·β!·γ!·j!³]
- 501 exact coefficients computed in 38 seconds
- First non-trivial: c₃=6, c₄=72, c₅=540 (c₅₀₀ has 469 digits)

**D₆-Invariant Yukawa Couplings:**
- 26 non-zero entries from 283 raw triple intersection numbers
- Two-sector structure: Sector A {O1,O3,O4,O5} (19 couplings) + Sector B {O2,O6} (4 couplings) + 1 cross-coupling κ(O1,O2,O3)=18
- Invariant c₂ numbers: O1=68, O2=36, O3=4, O4=12, O5=12, O6=−12

**Coordinate Issue:**
- PF in z=1/ψ (1-parameter model) has polynomial degree ≈ Vol(Δ*) = 72 — confirmed intractable by modular Gaussian elimination over 501 terms
- Resolution: use the 6 Mori coordinates z₁…z₆

### What Remains
- Quantum Yukawa corrections (Gromov-Witten invariants from instanton sums)
- Physical prepotential computation

### PF Operators (completed)

*Added 2026-02-23. See [GL12_GEOMETRY.md](GL12_GEOMETRY.md) §"Explicit PF Operators" for full details.*

The GKZ PF system was successfully derived in Mori θ-coordinates:
- **6 box operators** □₁–□₆ (degrees 3, 9, 2, 18, 6, 3) acting on the period ω₀
- **S_α mapping**: 8 orbit theta-operators expressed in 6 Mori θ-operators
- **9,366/9,366 GKZ recurrence checks pass** (verified to |n| ≤ 5)
- **1-parameter ODE** (z₁-axis): [(θ+1)³ + t(3θ+1)(3θ+2)(3θ+3)]ω = 0
- **Hypergeometric identification**: ₃F₂([1/3,2/3,1];[1,1];27t), AESZ #1
- This is the period of the mirror family of cubic curves in ℙ² (elliptic curve family)

---

## 9. Complete Pipeline Survey — 37 T2=45 Candidates (B-24)

**Date**: 2026-02-23. **Script**: `pipeline.py`.

All 37 polytopes scoring T2=45 (the maximum tier-2 score) have been analyzed with the full 26-point pipeline. This represents the complete set of top candidates from the χ=−6 landscape at h¹¹ = 13–19.

### Score Distribution

| Score | Count | Examples |
|-------|-------|----------|
| 26/26 | **19** | h15/poly94, h14/poly2, h16/poly11, h16/poly86 |
| 25/26 | 5 | h17/poly53, h17/poly51, h19/poly67, h17/poly96, h15/poly61 |
| 23/26 | 10 | h16/poly53, h17/poly9, h15/poly23, h16/poly22 |
| 22/26 | 2 | h18/poly32, h19/poly16 |
| 18/20 | 1 | h13/poly1 (old pipeline format) |

### Top 10 by Clean Bundle Count

| Rank | Candidate | Score | Clean | τ_SC | K3 | Ell |
|------|-----------|-------|-------|------|----|-----|
| 1 | **h17/poly53** | 25/26 | **418** | 1,016 | 3 | 3 |
| 2 | **h15/poly94** | 26/26 | **380** | 241 | 4 | 6 |
| 3 | h17/poly51 | 25/26 | 340 | 210 | 3 | 3 |
| 4 | h14/poly2 | 26/26 | 320 | 58 | 3 | 3 |
| 5 | h19/poly67 | 25/26 | 312 | 24 | 3 | 3 |
| 6 | h18/poly32 | 22/26 | 308 | — | 4 | 6 |
| 7 | h16/poly53 | 23/26 | 300 | — | 5 | 10 |
| 8 | h16/poly11 | 26/26 | 298 | 150 | 3 | 3 |
| 9 | h17/poly96 | 25/26 | 252 | 252 | 2 | 1 |
| 10 | h16/poly86 | 26/26 | 224 | 1,536 | 4 | 6 |

### Records

- **Most clean bundles (any score)**: h17/poly53 — 418 clean h⁰=3 bundles
- **Most clean bundles (26/26)**: h15/poly94 — 380 clean bundles (surpasses h14/poly2's 320)
- **Best τ (Swiss cheese)**: h15/poly61 — τ=14,300 (LVS champion)
- **Best τ among 26/26**: h15/poly25 — τ=5,255
- **Most elliptic fibrations**: h17/poly25, h17/poly45 — 15 each
- **Most K3 fibrations**: h17/poly25, h17/poly45 — 6 each

### 23/26 Pattern

All 10 polytopes scoring 23/26 fail the same 3 Swiss cheese / LVS checkpoints. These are geometrically viable 3-generation candidates whose Kähler cone does not admit the large-τ / small-τ hierarchy required for Large Volume Scenario moduli stabilization. They remain valid for other stabilization mechanisms (KKLT, racetrack, etc.).

---

## 10. h17 Automated Landscape Scan — 87 Perfect-Score Polytopes (B-19/B-28)

**Date**: 2026-02-25. **Script**: `auto_scan.py --h11 17 --skip-t025 --top 200 -w 3`.

The first fully automated deep scan of a single Hodge number using `auto_scan.py`. The h17 landscape (h¹¹=17, h²¹=20) turns out to be spectacularly rich — **87 polytopes achieve a perfect 26/26 score**, more than 4× the combined total from h11≤16. Every single fiber-analyzed polytope (193/193) contains the Standard Model gauge group SU(3)×SU(2)×U(1).

### Pipeline Summary

| Stage | Input | Output | Time |
|-------|-------|--------|------|
| T0.25 pre-filter | 38,735 polytopes | 10,624 passes (27.4%) | (prior scan) |
| Top-200 selection | 10,624 passes | 200 (max_h0 cutoff ≥ 10) | — |
| Stage 1: Deep analysis | 200 polytopes | 200 scored | ~2 min |
| Stage 2: Fiber classification | 193 with fibrations | 193 gauge algebras | ~30s |
| **Total** | **38,735** | **200 ranked** | **3.0 min** |

### Score Distribution

| Score | Count | Description |
|-------|-------|-------------|
| 26/26 | **87** | Perfect — all criteria met |
| 25/26 | 26 | Missing 1 point (usually dP diversity or ell count) |
| 23/26 | 64 | No Swiss cheese (−3 LVS points) |
| 22/26 | 19 | No Swiss cheese + 1 other weakness |
| ≤21 | 4 | Multiple weaknesses |

### Gauge Group Results

| Metric | Count | Rate |
|--------|-------|------|
| SM gauge (SU3×SU2×U1) | 193 | **100%** |
| SU(5) GUT | 166 | 86% |
| E₇ or E₈ factors | 46 | 24% |

The 100% SM rate is remarkable — at h17, the toric geometry is rich enough that *every* polytope with good line bundle cohomology also supports Standard Model gauge factors through its elliptic fibrations.

### Top 20 Candidates

| Rank | Poly | Score | Clean | h⁰ | dP | τ | K3 | Ell | GUT | Best Gauge |
|------|------|-------|-------|-----|----|----|-----|------|-----|------------|
| 1 | **P767** | 26/26 | **59** | 17 | 3 | 1.5 | 5 | 10 | ★ | su(2)×su(4)×su(2)×su(3)×su(6) |
| 2 | P389 | 26/26 | 41 | 10 | 3 | 186 | 2 | 1 | — | su(2)×su(3)×su(4)×su(2)×su(3) |
| 3 | P251 | 26/26 | 38 | 10 | 6 | 539 | 4 | 4 | ★ | su(4)×su(9)/e₈ |
| 4 | **P1033** | 26/26 | 35 | 15 | 5 | 64 | 6 | **11** | ★ | su(2)×su(4)²×su(2)×su(3)×su(2) |
| 5 | P1096 | 26/26 | 35 | 12 | 6 | 344 | 4 | 4 | ★ | su(4)×su(8)/e₇ |
| 6 | P996 | 26/26 | 35 | **32** | 3 | 30 | 3 | 3 | ★ | su(4)²×su(2)×su(4)×su(2) |
| 7 | P4126 | 26/26 | 35 | 11 | 5 | 74 | 3 | 3 | ★ | su(6)²×su(3) |
| 8 | P1180 | 26/26 | 34 | 10 | 6 | 564 | 5 | 6 | ★ | su(5)×su(8)/e₇ |
| 9 | P2297 | 26/26 | 33 | 23 | 6 | 28 | 5 | 8 | ★ | su(2)×su(6)² |
| 10 | P894 | 26/26 | 33 | 10 | 5 | 110 | 4 | 6 | ★ | su(2)²×su(4)×su(5)×su(2) |
| 11 | P543 | 26/26 | 33 | 10 | 7 | 48 | 3 | 1 | ★ | su(3)×su(4)×su(7) |
| 12 | P923 | 26/26 | 32 | 10 | 6 | 84 | 4 | 4 | ★ | su(5)×su(9)/e₈ |
| 13 | **P860** | 26/26 | 31 | 12 | **8** | **1,139** | 5 | 6 | ★ | su(4)×su(3)×su(4)×su(3) |
| 14 | P229 | 26/26 | 31 | 10 | 4 | 664 | 4 | 4 | ★ | su(5)×su(7) |
| 15 | P1061 | 26/26 | 31 | 14 | 4 | 390 | 3 | 1 | ★ | su(3)×su(4)×su(2)×su(5) |
| 16 | P120 | 26/26 | 31 | 10 | 3 | 93 | 2 | 1 | ★ | su(6)×su(2)×su(3)×su(5) |
| 17 | P2828 | 26/26 | 30 | 12 | 6 | 420 | 4 | 4 | ★ | su(3)×su(8)/e₇×su(4) |
| 18 | P1375 | 26/26 | 30 | 11 | 7 | 128 | 3 | 3 | ★ | su(6)²×su(3) |
| 19 | P363 | 26/26 | 30 | 10 | 4 | 282 | 3 | 3 | ★ | su(4)×su(2)²×su(3)×su(2)²×su(3) |
| 20 | P1324 | 26/26 | 30 | 10 | 5 | 140 | 2 | 1 | — | su(2)²×su(3)²×su(4) |

### Category Champions

#### Triple-Threats (clean≥25, ell≥6, Swiss cheese)

These polytopes excel at heterotic (clean bundles), F-theory (elliptic fibrations), AND LVS (Swiss cheese) simultaneously:

| Poly | Clean | Ell | K3 | τ | GUT | Best Gauge |
|------|-------|-----|-----|---|-----|------------|
| **P767** | 59 | 10 | 5 | 1.5 | ★ | su(2)×su(4)×su(2)×su(3)×su(6) |
| **P1033** | 35 | 11 | 6 | 64 | ★ | su(2)×su(4)²×su(2)×su(3)×su(2) |
| **P1180** | 34 | 6 | 5 | 564 | ★ | su(5)×su(8)/e₇ |
| **P2297** | 33 | 8 | 5 | 28 | ★ | su(2)×su(6)² |
| **P894** | 33 | 6 | 4 | 110 | ★ | su(2)²×su(4)×su(5)×su(2) |
| **P860** | 31 | 6 | 5 | 1,139 | ★ | su(4)×su(3)×su(4)×su(3) |
| **P2338** | 25 | 11 | 6 | 3,750 | ★ | su(3)×su(5)×su(6) |
| **P1377** | 25 | 8 | 5 | 300 | ★ | su(4)×su(5)×su(2)×su(4)×su(2) |

**P767** is the standout — most clean bundles (59), 10 elliptic fibrations, 5 K3 fibrations, GUT-viable. Its only weakness is a low τ (1.5), meaning LVS would need fine-tuning. For a triple-threat that also has strong LVS, **P2338** (τ=3,750, 11 ell, 25 clean) or **P860** (τ=1,139, 6 ell, 31 clean, 8 dP) are better balanced.

#### F-Theory GUT Champions (ell≥8, GUT★)

| Poly | Ell | K3 | Clean | τ | Best Gauge |
|------|-----|-----|-------|---|------------|
| **P695** | **15** | 6 | 22 | 54 | su(2)×su(4)×su(2)×su(3)×su(6) |
| P1033 | 11 | 6 | 35 | 64 | su(2)×su(4)²×su(2)×su(3)×su(2) |
| P2338 | 11 | 6 | 25 | 3,750 | su(3)×su(5)×su(6) |
| P1471 | 11 | 6 | 24 | 798 | su(4)×su(2)×su(6)×su(2) |
| P13144 | 11 | 6 | 20 | 1,554 | su(4)²×su(2)⁴ |
| P5030 | 11 | 6 | 7 | 600 | su(5)×su(3)×su(5)×su(2) |
| P767 | 10 | 5 | 59 | 1.5 | su(2)×su(4)×su(2)×su(3)×su(6) |

**P695** holds the all-time record with **15 elliptic fibrations** — same as the previously-known h17/poly25, but now confirmed with full gauge algebra classification. The cluster of 6 polytopes with 11 elliptic fibrations is new territory; P2338 is particularly notable with τ=3,750 (strong LVS).

#### LVS Champions (τ > 1,000)

| Poly | τ | Clean | Ell | GUT | Best Gauge |
|------|---|-------|-----|-----|------------|
| **P340** | **8,608** | 13 | 1 | ★ | su(7)×su(6) |
| P985 | 6,440 | 25 | 4 | ★ | su(3)×su(8)/e₇×su(4) |
| P902 | 6,003 | 25 | 3 | ★ | su(6)×su(7) |
| P2338 | 3,750 | 25 | 11 | ★ | su(3)×su(5)×su(6) |
| P17 | 3,166 | 26 | 0 | — | — |
| P270 | 2,546 | 27 | 1 | — | su(2)×su(3)²×su(2)² |
| P1311 | 2,310 | 19 | 1 | ★ | su(2)×su(5)×su(7) |
| P8 | 2,208 | 25 | 3 | ★ | su(3)²×su(7) |
| P13144 | 1,554 | 20 | 11 | ★ | su(4)²×su(2)⁴ |
| P860 | 1,139 | 31 | 6 | ★ | su(4)×su(3)×su(4)×su(3) |

**P340** has τ=8,608 — the best h17 LVS hierarchy, though still below the all-time record of h15/poly61 at τ=14,300. **P2338** (τ=3,750) uniquely combines top-tier LVS with 11 ell fibrations and GUT viability.

#### Heterotic Champions (clean≥40)

| Poly | Clean | h⁰ | dP | Ell | τ | GUT | Best Gauge |
|------|-------|-----|-----|-----|---|-----|------------|
| **P767** | **59** | 17 | 3 | 10 | 1.5 | ★ | su(2)×su(4)×su(2)×su(3)×su(6) |
| P2548 | 54 | 10 | 7 | 4 | 0 | ★ | su(5)×su(8)/e₇ |
| P1040 | 50 | 16 | 6 | 1 | 0 | — | su(3)×su(4)×su(2)×su(4) |
| P14261 | 46 | 22 | 6 | 4 | 0 | ★ | su(3)×su(9)/e₈×su(3) |
| P53 | 45 | 10 | 0 | 3 | 1,016 | — | su(3)×su(4)×su(2)×su(3) |
| P883 | 43 | 10 | 6 | 4 | 0 | ★ | su(9)/e₈×su(3) |
| P389 | 41 | 10 | 3 | 1 | 186 | — | su(2)×su(3)×su(4)×su(2)×su(3) |

**P767** (59 clean) is the h17 heterotic champion and exceeds the previous h17 record-holder P53 (now confirmed at 45 clean by auto_scan). Note that the all-time heterotic champion h17/poly53 (418 clean from old full-pipeline analysis) was not in the top-200 by max_h0 — it likely ranks lower by that metric but has exceptional depth at h⁰=3. The auto_scan's top-200 selection biases toward high max_h0, which correlates with but doesn't perfectly predict clean bundle count.

#### E-Type Gauge Factors

24% of analyzed polytopes (46/193) have E₇ or E₈ gauge factors — these are particularly interesting for GUT model building since E₈ is the natural gauge group of heterotic string theory:

| Poly | Score | Clean | Gauge |
|------|-------|-------|-------|
| P251 | 26 | 38 | su(4) × su(9)/e₈ |
| P1096 | 26 | 35 | su(4) × su(8)/e₇ |
| P1180 | 26 | 34 | su(5) × su(8)/e₇ |
| P923 | 26 | 32 | su(5) × su(9)/e₈ |
| P2828 | 26 | 30 | su(3) × su(8)/e₇ × su(4) |

### Cross-Reference with Prior Leaderboard

The previously known h17 candidates from the T2 pipeline have been re-ranked in the auto_scan:

| Old Name | Poly | Old Clean | Auto Clean | Auto Rank | Notes |
|----------|------|-----------|------------|-----------|-------|
| h17/poly63 | P63 | 218 | 14 | 81 | Different analysis depth (full vs auto) |
| h17/poly53 | P53 | 418 | 45 | 88 | Not in top-200 by max_h0 |
| h17/poly25 | P25 | 170 | — | >200 | Below max_h0 cutoff of 10 |

The apparent drop in clean bundle counts is because auto_scan analyzes top-200 *by max_h0*, not by clean count. The old pipeline used full `min_h0=3` enumeration (much slower). The key insight: auto_scan efficiently identifies the *different* leaders — polytopes like P767 (59 clean, 10 ell) that were missed by the old pipeline's manual candidate selection.

### Summary

h17 is the **richest single Hodge number** in the χ=−6 landscape:
- **87 perfect scores** (26/26) — more than all lower h¹¹ values combined
- **100% Standard Model gauge group** across all 193 analyzed polytopes
- **86% SU(5) GUT** candidates
- Multiple new record-holders: P767 (clean+ell combined), P2338 (LVS+F-theory), P860 (balanced)
- The previous manual pipeline found ~19 perfect-score candidates at h11≤16; h17 alone has 4.6× that
---

## 11. Automorphism Group Scan — Symmetry vs. Three-Generation Tension (B-21)

**Date**: 2026-02-26. **Script**: [scan_automorphisms.py](scan_automorphisms.py). **Data**: [results/aut_scan.log](results/aut_scan.log).

### Motivation

An external analysis proposed that the GL=12 polytope's D₆ (dihedral-6) symmetry group could constrain Yukawa textures via a 2+1 generation splitting (E₁⊕A₁ irrep). This required testing whether **any** 3-generation polytopes have nontrivial discrete symmetries — a "binary gate" test before investing in representation-theoretic analysis.

Additionally, the GL=12 polytope (h17/P37) was conclusively falsified for line bundle phenomenology: across all 1,720 χ=−6 bundles, **max h⁰ = 1** — zero clean h⁰=3 bundles exist. The D₆ line bundle Yukawa program is dead.

### Method

Computed `p.automorphisms()` (polytope automorphism group) for:
1. All **592 top-200 candidates** across h15/h16/h17 (those appearing in auto_scan results)
2. All polytopes at each h-value with |Aut|>1, cross-referenced with scan CSVs for max_h0 and h0_3_count

### Key Results

**Among 592 top candidates:**
- 539 (91%) have trivial |Aut| = 1
- 49 (8%) have |Aut| = 2 (Z₂)
- 4 (1%) have |Aut| = 4 (Z₂×Z₂ or Z₄)
- **Maximum |Aut| = 4** — no D₆, A₄, or larger flavor symmetries

**Across ALL polytopes (h15+h16+h17) with |Aut|>1 AND h⁰≥3:**
- **532 polytopes total** (46 at h15, 112 at h16, 374 at h17)
- |Aut| distribution: 511× Z₂, 19× Z₄-class, 2× |Aut|=8

**Highest-symmetry polytopes with 3-generation bundles:**

| Polytope | h¹¹ | |Aut| | max_h⁰ | h⁰=3 count | Notes |
|----------|------|-------|---------|-------------|-------|
| P0 | 16 | **8** | 3 | 4 | Highest symmetry with h⁰≥3 |
| P2997 | 17 | **8** | 3 | 2 | Z₂³ or Z₈ |
| P18 | 15 | 4 | 13 | 40 | Best |Aut|=4 candidate |
| P468 | 17 | 4 | 4 | 32 | |
| P633 | 17 | 4 | 4 | 18 | |

**Top Z₂ candidates (|Aut|=2, h⁰=3 count ≥ 100):**

| Polytope | h¹¹ | max_h⁰ | h⁰=3 count | Notes |
|----------|------|---------|-------------|-------|
| P27751 | 17 | 6 | 192 | Highest h⁰=3 count with symmetry |
| P31 | 15 | 10 | 190 | |
| P329 | 16 | 15 | 164 | **Already pipeline'd: 26/26, 228 clean** |
| P164 | 15 | 10 | 162 | |
| P8 | 15 | 4 | 146 | |
| P9 | 17 | 10 | 142 | |
| P92 | 15 | 4 | 136 | |
| P1821 | 16 | 9 | 134 | |
| P2001 | 17 | 7 | 126 | |
| P937 | 17 | 5 | 124 | |
| P1545 | 17 | 7 | 120 | |
| P427 | 17 | 4 | 116 | |
| P1403 | 17 | 4 | 108 | |
| P15531 | 17 | 10 | 108 | |
| P1629 | 17 | 9 | 106 | |
| P383 | 16 | 10 | 102 | |

### The Symmetry-vs-h⁰ Tension

**Confirmed**: Higher polytope symmetry anti-correlates with h⁰ diversity.
- GL=12 (|Aut|=12): max_h⁰ = 1, zero h⁰=3 bundles
- |Aut|=8: max_h⁰ = 3, only 2-4 h⁰=3 bundles
- |Aut|=4: max_h⁰ up to 13, up to 40 h⁰=3 bundles
- |Aut|=2: max_h⁰ up to 17, up to 192 h⁰=3 bundles
- |Aut|=1: max_h⁰ up to 26+, up to 524+ h⁰=3 bundles

**Physical interpretation**: Polytope symmetries constrain the lattice of effective divisors, reducing the degrees of freedom available for line bundle charges. The same rigidity that produces beautiful group theory kills the combinatorial room needed for χ=−6 with h⁰=3. This is a fundamental tension: **flavor symmetry from geometry competes with phenomenological viability from line bundles**.

### Implications

1. **D₆/A₄-level flavor symmetries do not exist** among viable 3-generation candidates
2. **Z₂ is the realistic maximum** for combining symmetry with rich bundle structure
3. The 2+1 generation splitting idea is **transplantable** to Z₂ polytopes (Z₂ acts as parity, splitting generations into even+odd)
4. **h16/P329** is the standout: already scored 26/26 with 228 clean bundles, |Aut|=2, 7 elliptic fibrations, AND 164 h⁰=3 bundles from ALL line bundles

---

## Finding 12: Z₂ Acts Trivially on Generations (P329)

**Date**: 2025-02-23
**Commit**: (z2_bundle_analysis v3)

### Question

Does the Z₂ involution of h16/P329 split 3 generations as 2+1, providing
texture zeros in the Yukawa matrix?

### Method

1. Computed the Z₂ generator σ on the N-lattice:
   σ = [[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]] (swap coords 2↔3), det = −1
2. Determined σ's action on all 18 toric divisors via ray permutation:
   - 5 fixed rays, 7 swapped pairs
   - **Critical**: e₁₁ (toric 16) → toric 15, which is NOT in the divisor basis
3. Used GLSM linear relations to express D₁₅ ~ D₁ − D₃ − D₅ − D₇ − D₁₆,
   giving the full σ action matrix S on Pic(X) ≅ Z¹⁴
4. Verified S² = Id, Tr(S) = 2 → Picard splits as **8(+1) ⊕ 6(−1)**
5. Enumerated 220 unique clean (h⁰=3, h³=0) line bundles
6. Applied S^T to classify bundles as Z₂-fixed vs Z₂-paired
7. For each fixed bundle: found section lattice points S_D, computed
   Tr(σ*|H⁰(X,D)) = #{m ∈ S_D : σ^T m = m} − #{m ∈ S_{D+K} : σ^T m = m}
8. Computed eigenspace dimensions: dim(±1) = (h⁰ ± Tr)/2

### Results

| Category | Count | Notes |
|----------|-------|-------|
| Clean bundles | 220 | unique, h⁰=3, h³=0 |
| Z₂-fixed | 11 | σ(L) = L |
| Z₂-paired | 24 pairs | σ(L) ≠ L, both clean |
| σ-image outside enumeration | 161 | NOT fixed, don't affect 2+1 |

**Z₂ representation on H⁰ for all 11 fixed bundles**:

| Bundle | |S_D| | f_D | |S_{D+K}| | f_{D+K} | Tr | dim(+1) | dim(−1) | Split |
|--------|-------|-----|---------|---------|-----|---------|---------|-------|
| L0–L10 | 3 | 3 | 0 | 0 | 3 | 3 | 0 | 3+0 |

**Every single fixed bundle has Tr(σ*) = 3, giving a trivial 3+0 split.**

### Why It's Trivial

The dual action σ* on the M-lattice swaps m₁ ↔ m₂ (since σ swaps N-lattice
coords 2↔3, and σ^T = σ for this symmetric matrix). All section lattice
points of the 11 fixed bundles satisfy m₁ = m₂, lying entirely in the
fixed hyperplane. This is not coincidental — these bundles have charges
only on the Z₂-invariant part of Pic(X), so their section polytopes
inherit the full σ symmetry.

### Physical Interpretation

**P329's Z₂ does NOT produce a 2+1 generation split.** The symmetry that
looked promising for Yukawa texture zeros acts as the identity on H⁰(X,L)
for every Z₂-invariant line bundle. The Z₂ is too "mild" — a single
coordinate swap that commutes with the section monomial structure.

This confirms and deepens Finding 11 (symmetry-vs-h⁰ tension):

- The subset of clean bundles preserved by symmetry is small (11/220 = 5%)
- Even within that subset, the symmetry acts trivially on generations
- **The SM's three generations are not explained by polytope automorphisms**

### Implications for Next Steps

1. **Z₂ at single-bundle level is dead** for texture zeros on P329
2. The 2+1 split could still arise at the **rank-5 sum level**: five bundles
   L₁+...+L₅ could carry a combined Z₂ representation that distinguishes
   generations, even if individual bundles don't
3. More promising: the **paired bundles** (24 pairs) where σ swaps
   H⁰(X,L) ↔ H⁰(X,σ*L), giving a 3+3 combined representation.
   Choosing paired Li in the rank-5 sum creates mandatory correlations
   between generation indices
4. Alternative approach: look for **non-geometric discrete symmetries**
   (Wilson lines, orbifold actions) rather than polytope automorphisms

---

## Finding 13: AGLP Line Bundle Sum Search — No Solutions at High Picard Rank

**Date**: 2026-02-23
**Script**: `aglp_bundle_sum.py` (meet-in-the-middle 3+2 decomposition)
**Targets**: h14/P2, h16/P329

### Setup

Searched for rank-5 line bundle sums V = L₁ ⊕ L₂ ⊕ L₃ ⊕ L₄ ⊕ L₅ satisfying
heterotic SU(5) GUT constraints (AGLP construction):

- c₁(V) = 0: L₁ + L₂ + L₃ + L₄ + L₅ = 0 in Pic(X)
- c₃(V) = ±6: 3 net chiral generations
- c₂(TX) − c₂(V) effective: anomaly cancellation
- Slope stability: μ(Lᵢ) < 0 at Kähler cone tip

Search strategy: pick 5 clean bundles (h⁰=3, h³=0) from the χ=±3 list
and check if any 5-element subset sums to zero.

### Results

| Manifold | χ=±3 bundles | Clean (h⁰=3, h³=0) | h¹¹_eff | 5-sets c₁=0 | c₃=±6 |
|----------|:---:|:---:|:---:|:---:|:---:|
| h14/P2   | 14,608 | 268 | 13 | **0** | 0 |
| h16/P329 | 24,312 | 220 | 14 | **0** | 0 |

**Zero solutions on both targets.** Not a single combination of 5 clean bundles
sums to zero in either lattice.

Search completed in seconds thanks to meet-in-the-middle optimization
(O(N³) instead of naive O(N⁴) — 3.2M triples vs 210M 4-tuples).

Relaxing coefficient bounds (max-coeff=5, max-nonzero=6) was attempted on P2
but enumeration alone exceeds hours at h¹¹_eff=13 (~1.7 billion candidate
vectors), and was killed.

### Why This Failed

1. **The h⁰=3 filter is too restrictive.** It kills ~98% of χ=±3 bundles
   (14,608→268 on P2, 24,312→220 on P329), leaving a subset too sparse for
   any 5 elements to cancel in a 13–14 dimensional lattice.

2. **Wrong pre-filter.** In the proper AGLP construction, individual Lᵢ are
   just lattice vectors in Pic(X) ≅ ℤ^{h¹¹}. Only the *sum* V needs
   physical properties (c₃=±6, anomaly cancellation). Requiring each Lᵢ to
   independently have h⁰=3 is not part of the AGLP prescription.

3. **High Picard rank is the enemy.** AGLP in the literature (Anderson–Gray–
   Lukas–Palti, 1307.4787) typically works at h¹¹=2–5 where the Kähler cone
   is manageable and the lattice is small. At h¹¹_eff=13–14, even without the
   h⁰ filter, the search space for 5 vectors summing to zero with c₃=±6 is
   a cubic Diophantine problem in ~60 integer unknowns.

### Lessons

- **The polytope scanning pipeline remains the primary tool.** It identifies
  which manifolds have the right topological prerequisites. Bundle
  construction is a downstream step for the best candidates.
- **Bundle searches at h¹¹>10 need fundamentally different algorithms:**
  direct lattice constraint solving (eliminate L₅ via c₁=0, reduce c₃=±6
  to a cubic form), randomized/MCMC sampling, or monad/extension sequences
  rather than line bundle sums.
- **The script works correctly and efficiently** — the meet-in-the-middle
  algorithm scanned 3.2M triples in 5s. The failure is mathematical, not
  computational.
5. **h16/P0** (|Aut|=8) deserves a pipeline run despite only 4 h⁰=3 bundles — the symmetry structure may reveal interesting Yukawa constraints on those few bundles

---

## Finding 14: Database Landscape Analysis — The Gap Variable and Data-Driven Pipeline Redesign

**Date**: 2026-02-27 (initial), 2026-02-28 (circularity audit + loser analysis).
**Scripts**: [db_utils.py](db_utils.py), [consolidate_db.py](consolidate_db.py), [pipeline_v2.py](pipeline_v2.py).
**Database**: `cy_landscape.db` (74,823 polytopes, 4,387 fibrations).
**Commits**: `468b4ae` (initial), `4d8e3fc` (h17 receipt merge).

### Motivation

After accumulating scan results across 15+ CSV/JSON files spanning h¹¹ = 13–19, we
consolidated everything into a single SQLite database and ran 30 exploratory queries
to discover cross-h¹¹ empirical patterns before scaling to h¹¹ = 19–20 (~244K–490K
polytopes). The goal: which variables actually predict success, and which are noise?

### Data Provenance

All data comes from our own pipeline scans, consolidated from:

| Source file(s) | Polytopes | h¹¹ | Tier |
|---------------|-----------|------|------|
| scan_h{15,16,17}.csv | 44,468 | 15-17 | T0.25 |
| tier025_results.csv | 58,508 | 13-18 | T0.25 |
| tier1_screen_results.csv | 272 | 13-17 | T1 |
| tier1_h18_results.csv | 30,293 | 18 | T1 |
| tier15_screen_results.csv | 87 | 13-17 | T1.5 |
| tier2_screen_results.csv | 116 | 13-17 | T2 |
| auto_h{15,16,17}.csv | 615 | 15-17 | T2+ |
| chi6_tier1_scan.csv | 35 | 19 | T1 |
| fiber_h{15,16,17}.json | 35 fibrations | 15-17 | T2+ |

After deduplication (upsert on (h¹¹, poly_idx)), this yields **74,819 unique polytopes**
with the deepest tier data retained for each.

### Coverage

| h¹¹ | In DB | KS chi-6 total | Coverage | Deep (≥T1) |
|------|------:|---------------:|:--------:|:----------:|
| 13 | 3 | 3 | 100% | 3 |
| 14 | 20 | 20 | 100% | 20 |
| 15 | 553 | 553 | 100% | 467 |
| 16 | 5,180 | 5,180 | 100% | 246 |
| 17 | 38,735 | 38,735 | 100% | 252 |
| 18 | 30,293 | ~105,493 | 28.7% | 67 |
| 19 | 35 | ~244,000 est. | 0.01% | 35 |

### Key Findings

#### 14a. The Gap Variable: gap = h¹¹ − h¹¹_eff (Query 17, **strongest predictor found**)

The "gap" — the difference between total Picard number and effective Picard number —
is a useful predictor of clean bundle yield. This measures how many divisors
become linearly dependent in the effective (intersection-constrained) description.

**Unbiased data only** (pre-pipeline_v2, N=496, excl h17):

| gap | N (at T1+) | avg clean | Hit rate | max clean |
|:---:|:----------:|:---------:|:--------:|:---------:|
| 0 | 231 | 12.6 | 97.0% | 86 |
| 1 | 95 | 15.2 | 97.9% | 53 |
| 2 | 99 | 20.4 | **100%** | 59 |
| 3 | 36 | 20.7 | **100%** | 69 |
| 4 | 24 | 27.0 | **100%** | 94 |
| 5+ | 11 | 65.2 | **100%** | 189 |

**Note**: The prior version of this table mixed biased and unbiased data. After
running pipeline_v2 on h17 (which filters gap≥2 before T1), the h17 contribution
is circular and cannot validate the gap finding. The numbers above are from
pre-pipeline_v2 scans only.

**Physical interpretation**: Higher gap means more redundant divisors in the toric
ambient, providing extra geometric flexibility for line bundles to satisfy anomaly
cancellation while maintaining clean cohomology.

#### 14b. Non-Favorable Polytopes Dominate (Query 2)

| Class | Best clean | Best h⁰ | Population |
|-------|:---------:|:-------:|:----------:|
| Non-favorable (NF) | **189** | **57** | Majority at h¹¹≥14 |
| Favorable (F) | 86 | 17 | 100% at h13, drops to 70% at h18 |

The top-20 polytopes by clean count are **all non-favorable** (except h13/P0,
which is favorable but the only option at h¹¹=13). Non-favorable polytopes
have h¹¹_eff < h¹¹ (i.e., gap > 0), confirming the gap analysis.

Favorable fraction by h¹¹: 100% (h13), 91% (h15), 84% (h16), 84% (h17),
70% (h18), 3% (h19 — only 35 sampled).

#### 14c. h¹¹_eff = 13 Sweet Spot (Query 3)

| h¹¹_eff | avg h⁰ | % with clean | Best clean |
|:-------:|:------:|:------------:|:----------:|
| 12 | 8.1 | 50% | 94 |
| **13** | **6.4** | **38%** | **189** |
| 14 | 4.6 | 26% | 49 |
| 15 | 3.1 | 17% | 59 |
| 16 | 2.3 | 11% | 59 |
| 17 | 1.9 | 0.04% | 40 |

At eff=13, polytopes have enough complexity for rich bundle structure but not
so much that the Kähler cone becomes unmanageable. At fixed eff=13, clean
count **increases with h¹¹** (Q18): h13→86, h17→102, h18→189. More
embedding dimensions at the same effective complexity is pure upside.

#### 14d. Swiss Cheese is NOT Predictive (Query 4)

| Category | T1 pass rate |
|----------|:------------:|
| Has Swiss cheese | 89% |
| No Swiss cheese | 86% |

Swiss cheese structure is essentially noise for predicting T1 success. We
retain the computation for the record but remove it from triage gates.

#### 14e. Del Pezzo is Non-Monotonic (Query 5)

| n_dp | avg clean |
|:----:|:---------:|
| 0 | 22.5 |
| 1-3 | 15-20 |
| 4-9 | 8-12 |
| 10+ | 6.8 |

Too many del Pezzo divisors fragment the Kähler cone. Zero dP is actually
best — these manifolds have fewer geometric constraints on bundle choices.

#### 14f. Symmetry Kills (Query 14)

| |Aut| | avg clean | Best clean |
|:-----:|:---------:|:----------:|
| 1 | 9.5 | — |
| 2 | 6.2 | — |
| 4 | 3.8 | — |
| 8 | **0** | 0 |

Higher automorphism groups systematically reduce clean bundle counts.
|Aut| ≥ 4 should be deprioritized (not eliminated, but pushed to end of queue).

#### 14g. n_chi3 Phase Transition at 10K+ (Query 9)

| n_chi3 bucket | avg clean | N |
|:-------------:|:---------:|:-:|
| 0-499 | 8.2 | 33 |
| 500-999 | 15.3 | 90 |
| 1000-4999 | 18.8 | 410 |
| 5000-9999 | 19.3 | 165 |
| **10000+** | **92.4** | **9** |

Polytopes with 10,000+ χ=±3 bundles are massive outliers — avg 92.4 clean.
These are the "10K club" (all eff=12-13, all non-favorable). This threshold
serves as a cheap probe: count χ=±3 before doing full cohomology.

#### 14h. Clean Increases with h¹¹ at Fixed Effective Complexity (Query 18)

At fixed h¹¹_eff = 13:

| h¹¹ | max clean | avg clean (T2) |
|:----:|:---------:|:--------------:|
| 13 | 86 | 86 |
| 16 | 69 | 45 |
| 17 | 102 | 48 |
| 18 | 189 | 97 |

This is perhaps the most encouraging result for scaling: going to higher h¹¹
while keeping eff fixed **improves** outcomes. The extra toric structure
provides more degrees of freedom without increasing computational complexity.

#### 14i. The Untouched Goldmine (Query 20)

Polytopes stuck at T0.25 (no deep analysis) with promising indicators:

| h¹¹ | T025-only, h⁰ ≥ 5 | h⁰ ≥ 10 |
|:----:|:------------------:|:--------:|
| 17 | 767 | 59 |
| 18 | 193 | 28 |

These are prime targets for the new pipeline.

#### 14j. SM Rate Gap is a Data Gap, Not Physics (Query 10)

Score 40+ polytopes show only 3% SM gauge group rate vs 94% at score 20-29.
Root cause: high-scoring h18/h19 polytopes haven't had fiber analysis run yet.
The SM fraction will rise once the Hetzner batch completes.

#### 14k. Best Polytopes — All-Time Leaderboard (Query 28)

| Rank | Polytope | eff | gap | χ₃ | clean | h⁰ | NF/F |
|:----:|----------|:---:|:---:|:---:|:-----:|:---:|:----:|
| 1 | h18/P34 | 13 | 5 | 12,886 | **189** | 16 | NF |
| 2 | h19/P7 | 13 | 6 | 11,604 | **114** | 6 | NF |
| 3 | h17/P58 | 13 | 4 | 15,372 | **102** | 6 | NF |
| 4 | h17/P32 | 13 | 4 | 10,616 | **95** | 13 | NF |
| 5 | h16/P52 | 12 | 4 | 9,966 | **94** | 4 | NF |
| 6 | h13/P0 | 13 | 0 | 11,114 | **86** | 10 | F |
| 7 | h19/P16 | 12 | 7 | 7,652 | **69** | 27 | NF |
| 8 | h16/P40 | 13 | 3 | 11,932 | **69** | 7 | NF |
| 9 | h17/P45 | 13 | 4 | 10,880 | **61** | 16 | NF |
| 10 | h18/P57 | 12 | 6 | 10,528 | **60** | 17 | NF |

Pattern: **9 of 10 are non-favorable, all have eff ∈ {12,13}, all have gap ≥ 3** (except P0).

#### 14l. High-Gap Specimens — Untouched Gold (Query 29)

Polytopes with gap ≥ 6 that are still stuck at T0.25:

| Polytope | eff | gap | χ₃ | Tier |
|----------|:---:|:---:|:---:|:----:|
| h18/P111 | 12 | 6 | 1,934 | T025 |
| h18/P163 | 12 | 6 | 1,350 | T025 |
| h18/P206 | 12 | 6 | 1,390 | T025 |
| h18/P294 | 12 | 6 | 1,722 | T025 |
| h18/P156 | 11 | 7 | 1,048 | T025 |
| h18/P165 | 11 | 7 | 898 | T025 |
| h18/P207 | 10 | 8 | 550 | T025 |
| h18/P280 | 10 | 8 | 828 | T025 |

All are non-favorable. These should be prioritized immediately in the next batch.

### Pipeline Redesign Based on These Findings

The empirical data demands a fundamentally different triage strategy:

**Old pipeline** (current):
```
T0.25 (all polytopes) → h⁰ ≥ 3 gate → T1 → Swiss cheese gate → T1.5 → T2
```

**New pipeline** (data-driven):
```
T0 (0.1s): Compute h¹¹_eff.
  SKIP if h¹¹_eff ≥ 16 (near-zero clean rate at T2)
  SKIP if gap < 2 AND h⁰ < 5 (97% hit rate but low avg clean)
  SKIP if |Aut| ≥ 4 (avg clean ≈ 0)

T0.25 (0.5s): Standard screening.
  PROMOTE if h⁰ ≥ 5 (raised from ≥3)
  PROMOTE if n_chi3 ≥ 5000 (phase transition indicator)

T1 (3s): Full divisor analysis + probe.
  Score by gap + eff, NOT Swiss cheese
  SKIP symmetry check as gate (compute, don't gate)

T2 (30s): Full bundles + fibrations → database.
  Priority order: gap DESC, n_chi3 DESC
```

**Estimated impact**:
- T0 pre-filter kills ~90% of polytopes in ~0.1s each (vs 0.5s per at T0.25)
- At h¹¹ = 19 (~244K polytopes): T0 filters to ~24K → T0.25 filters to ~5K → T1: ~500 → T2: ~100
- Total time estimate: **3–4 hours** for h19 (vs 30+ hours with current pipeline)
- At h¹¹ = 20 (~490K): **5–6 hours** estimated

### Diagnostic Variables — What to Compute vs What to Gate On

| Variable | Gate? | Why |
|----------|:-----:|-----|
| h¹¹_eff | **YES** | eff ≥ 16 → near-zero clean rate |
| gap = h¹¹ − h¹¹_eff | **YES** | gap < 2 reduces avg clean 2x |
| |Aut| | **YES** | |Aut| ≥ 4 → avg clean ≈ 0 |
| h⁰ | Gate at ≥5 | Raised from ≥3 based on data |
| Swiss cheese | Compute only | 89% vs 86% — noise |
| n_dp | Compute only | Non-monotonic, poor predictor |
| n_chi3 | Soft gate | ≥5000 gets priority |
| favorable | Compute only | NF is systematically better |

### Conclusions

1. **gap = h¹¹ − h¹¹_eff is a useful yield predictor** — avg clean 23.8 at gap≥2
   vs 13.7 at gap<2 (1.7× multiplier). Hit rate difference is only 2.8pp (100% vs
   97.2% in unbiased data, N=496).
2. **Non-favorable polytopes dominate the leaderboard** — 9 of top 10, all NF.
3. **Swiss cheese and del Pezzo count are not predictive** for clean bundles.
4. **The landscape gets BETTER at higher h¹¹** for fixed eff — more embedding room.
5. **The T0 pre-filter will cut ~90% of compute** at h19/h20 with minimal false negatives.
6. **Thousands of high-gap polytopes sit untouched** at T0.25 — priority targets.

### Circularity Audit (2026-02-28)

**The h17 pipeline_v2 run (N=519) cannot independently validate the gap finding**
because pipeline_v2 filters on gap≥2 before T1. The 100% hit rate at gap≥2 in h17
is a tautology — we only looked at what we expected to succeed.

**Honest numbers** (pre-pipeline_v2 only, N=496 at T1+, excl h17):

| Gap | N | Hits | Hit% | Avg clean (when hit) |
|:---:|:-:|:----:|:----:|:-------------------:|
| 0 | 231 | 224 | 97.0% | 13.0 |
| 1 | 95 | 93 | 97.9% | 15.5 |
| 2 | 99 | 99 | 100% | 20.4 |
| 3 | 36 | 36 | 100% | 20.7 |
| 4 | 24 | 24 | 100% | 27.0 |
| 5+ | 11 | 11 | 100% | 65.2 |

Gap≥2: 170/170 = 100% hit. Gap<2: 317/326 = 97.2% hit. Difference: 2.8pp.
Gap is an **efficiency knob** (prioritize richer targets), not a **quality gate**
(almost nothing fails regardless).

For h17 specifically, all gap<2 polytopes were killed at T0 by the eff≤15 + |Aut|≤3
constraints. The gap filter was redundant — it didn't actually exclude anything that
other filters wouldn't have caught.

### Loser Analysis (2026-02-28)

Only **9 out of 1,284** deep-analyzed polytopes (0.7%) have zero clean bundles:

| Polytope | eff | gap | h⁰ | Favorable | Swiss |
|----------|:---:|:---:|:---:|:---------:|:-----:|
| h14/P9 | 13 | 1 | 7 | NF | no |
| h15/P83 | 15 | 0 | 4 | F | yes |
| h15/P340 | 14 | 1 | 4 | NF | no |
| h15/P424 | 15 | 0 | 4 | F | no |
| h15/P457 | 15 | 0 | 4 | F | no |
| h15/P505 | 15 | 0 | 4 | F | yes |
| h15/P542 | 15 | 0 | 4 | F | no |
| h15/P544 | 15 | 0 | 4 | F | yes |
| h16/P1230 | 16 | 0 | 7 | F | no |

**Loser profile vs winners**:

| Metric | Losers (N=9) | Winners (N=1,275) |
|--------|:------------:|:-----------------:|
| avg h⁰ | 4.7 | 8.3 |
| avg gap | 0.2 | 1.8 |
| % favorable | 77.8% | 22.3% |
| % swiss cheese | 33.3% | 52.3% |
| avg n_dp | 6.2 | 5.4 |

Losers are favorable (3.5× overrepresented), low-gap, borderline-h⁰ polytopes.
They are marginal by every metric. The loser rate drops with h¹¹: h14 14.3%,
h15 3.5%, h16 0.5%, h18–h19 0%. At higher h¹¹, the landscape self-selects

---

## Finding 15: Pipeline v2 conflict audit & DB upsert fix (2026-02-24)

### Problem discovered
After rescanning h13–h16 with pipeline_v2, **216 polytopes** showed data conflicts:
old scans found `n_clean > 0` but v2 screened them at T0 or T025.

### Root causes

**Category 1 — EFF_MAX screening (59 polytopes):**
All favorable h16 polytopes have `h11_eff = 16` by definition (favorable ⟹ eff = h¹¹).
`EFF_MAX = 15` correctly skips them for speed at scale. Old scans (no eff filter)
found up to 40 clean bundles per polytope — real results, but these polytopes are
known-good and not the target of the large-scale scan.

**Category 2 — DB upsert clobber bug (152 polytopes):**
`compute_h0_koszul(min_h0=5)` correctly returns 0 as a fast screening signal when
h⁰(V,D) < 5. But `db_upsert_t025` blindly wrote `max_h0 = 0` to the DB, **overwriting**
correct old values (3–4). The early-exit is a valid optimization for speed — the bug
was in the upsert, not the math.

**Category 3 — AUT_MAX screening (5 polytopes):**
All had `sym_order = 4`. h15/P18 (19 clean), h16/P1 (16 clean). Correctly screened
for speed — high symmetry polytopes are expensive and marginal.

### Fix applied

**DB upsert monotonic MAX** (the real fix): Both `upsert_polytope` and
`upsert_polytopes_batch` in db_utils.py now use `MAX(COALESCE(existing, 0), new)`
for metric columns (`max_h0`, `n_clean`, `n_bundles_checked`, `max_h0_t2`,
`h0_ge3`, `n_chi3`, `n_computed`). Screening passes can never clobber deeper
analysis results. The `compute_h0_koszul` early-exit is restored — it's a
legitimate ~2× speedup for T025 screening at scale.

**Thresholds kept at speed-optimized values**: EFF_MAX=15, H0_MIN=5, AUT_MAX=3.
These are aggressive by design — the goal is to scan hundreds of thousands of
polytopes fast. The 216 "missed" polytopes are known-good but marginal; they
won't reveal the next breakthrough, they're just nice in their own way.

**DB restoration:** 1,173 corrupted `max_h0` values restored from old CSV sources.
Verified: 0 remaining polytopes with `max_h0=0` and `n_clean>0`.

### Impact
The upsert fix is permanent — future rescans can never corrupt existing data.
Aggressive thresholds maintained for speed at h18+ scale (100K+ polytopes).