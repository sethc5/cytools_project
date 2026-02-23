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

## 2. h17/poly63 — F-Theory Champion (Pipeline Score: 26/26, 218 clean)

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

## 2b. h14/poly2 — Heterotic Champion (Pipeline Score: 26/26, 320 clean)

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
