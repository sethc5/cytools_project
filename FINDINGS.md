# Findings

Detailed write-ups of key results. For the quick summary, see [README.md](README.md). For the ruled-out list, see [CATALOGUE.md](CATALOGUE.md).

---

## 1. h13/poly1 — Benchmark Candidate (Pipeline Score: 18/20)

**Date**: 2026-02-23. **Script**: [pipeline_h13_P1.py](pipeline_h13_P1.py).

The strongest χ = −6 candidate found in our scan. Smallest h¹¹ in the landscape, completely clean line bundles.

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

### h17 — deferred

38,735 polytopes. Estimated ~3.7 hours with 4 workers. Deferred to Codespace (needs longer compute window).

### Impact on the Screening Pipeline

The expanded scan has fundamentally changed the leaderboard — h15/poly61 was discovered, fast-tracked through all tiers, and scored **25/26 on full pipeline** with τ=14,300. 36 total T2 entries now span h13–h19. The expanded h16 scan added 20 new T2 candidates, all quality-rated ★★★. This validates expanding the scan coverage as the most productive strategy for finding new physics candidates.
