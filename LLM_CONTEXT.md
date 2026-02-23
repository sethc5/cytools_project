# CyTools Project — Deep Context for LLM Sessions

*Comprehensive operational brief. Updated 2026-02-23.*

---

## 1. THE QUESTION

**Can we find Calabi-Yau threefolds that explain why there are exactly three generations of matter in the Standard Model?**

The Standard Model has three generations of quarks and leptons. In string compactifications, this number is determined by topology: a Calabi-Yau threefold with Euler characteristic χ = −6 gives |χ|/2 = 3 chiral fermion generations. The question then becomes: which CY3s have χ = −6 AND all the other properties needed to build realistic physics?

This project is a systematic computational scan of the Kreuzer-Skarke (KS) database — 473 million reflexive polytopes — looking for the strongest 3-generation candidates.

---

## 2. INFRASTRUCTURE

### Software stack
- **CYTools** (MIT): Python library for triangulating reflexive polytopes and computing CY3 geometry. Key API: `fetch_polytopes()`, `Polytope.get_cy()`, `CalabiYau.get_divisors()`, `Divisor.cohomology()`, `CalabiYau.get_line_bundle_cohomologies()`
- **PALP** (underlying CYTools): triangulation engine
- **SageMath** (optional): algebraic cross-checks
- Custom Python pipeline: `pipeline.py`, `scan_parallel.py`, `tier1_screen.py`, `tier2_screen.py`

### Compute setup
- Local dev: VS Code, `/home/seth/dev/cytools_project/`, venv activated via `activate.sh`
- Remote: Hetzner dedicated server (14 workers), GitHub Codespace (4 workers)
- The pipeline is CPU-bound — each full polytope analysis runs ~5–20 min per polytope depending on h¹¹

### What the pipeline computes
**Tier 1 screen** (fast, ~seconds): Check χ = −6, count divisors with del Pezzo structure, identify Swiss cheese divisors (τ/V²/³ ratio), flag elliptic/K3 fibration candidates.

**Tier 1.5 screen** (minutes): Probe 300 random line bundles, require ≥3 bundles with h⁰ ≥ 3. Fibration identification via dual polytope subfaces.

**Tier 2 full pipeline** (hours): Complete bundle scan over all χ = ±3 line bundles, full cohomology h⁰/h¹/h²/h³, count "clean" bundles (h⁰=3, h¹=h²=h³=0), classify divisor types, compute Second Chern class c₂, verify Swiss cheese parameters (τ, volume V, τ/V²/³).

**Scoring (26-point system)**:
| Category | Max pts |
|---|---|
| χ = −6 (right Euler characteristic) | 3 |
| \|χ\|/2 = 3 (three generations) | 3 |
| h⁰ ≥ 3 line bundle exists | 3 |
| Count of completely clean bundles | 5 |
| Max h⁰ value across all bundles | 2 |
| Swiss cheese structure (LVS) | 3 |
| K3 fibrations (heterotic-F-theory duality) | 2 |
| Elliptic fibrations (F-theory model building) | 2 |
| del Pezzo divisors (non-perturbative effects) | 1 |
| D³ diversity | 1 |
| h¹¹ tractable | 1 |

---

## 3. SCAN COVERAGE (as of 2026-02-23)

The KS database has 104 distinct Hodge pairs (h¹¹, h²¹) with χ = −6, ranging h¹¹ = 13 to 128.

| h¹¹ | Polytopes in KS | Scanned | Coverage |
|-----|-----------------|---------|----------|
| 13 | 3 | 3 | **100%** |
| 14 | 22 | 22 | **100%** |
| 15 | 553 | 553 | **100%** |
| 16 | 5,180 | 5,180 | **100%** |
| 17 | 38,735 | ~16,200 | 42% (Codespace) |
| 18 | ~195,000 | ~98,000 | 50% (Hetzner) |
| 19–24 | ~millions | ~100 each | ~0% |
| 25–128 | enormous | 0 | 0% |

**Total: ~50,000+ polytopes scanned.**

### Screening funnel (cumulative through h11=24)
```
~50,000 polytopes scanned
  └── ~21,000 have h⁰ ≥ 3 line bundles (42%)
       └── 374 pass Tier 1 (dP divisors + Swiss cheese + symmetry)
            └── 338 pass Tier 1.5 (fibrations + 300-bundle probe)
                 └── 36 Tier 2 complete ✅
                      └── 14 scored T2 = 45 (max), 30 scored T2 ≥ 41
```

---

## 4. TOP CANDIDATES

All candidates below have χ = −6 (native 3-generation — no orbifold quotient needed).

### h14/poly2 — Heterotic Champion
**Score: 26/26 | 320 clean bundles | h¹¹ = 14**

The strongest heterotic string theory candidate. Smallest tractable Hodge number in the pool of 26/26 scorers, with 320 perfectly clean (h⁰=3, h¹=h²=h³=0) line bundles — far more internal variety than any other candidate. Three Swiss cheese divisors in three independent Kähler directions (the most of any candidate), enabling Large Volume Scenario moduli stabilization in multiple directions simultaneously.

Key properties:
- h¹¹ = 14, h²¹ = 17, χ = −6
- 3 del Pezzo divisors including dP₅, supporting non-perturbative E₅ instanton contributions
- 3 K3 fibrations, 3 elliptic fibrations
- Swiss cheese: 3 independent directions (unique among all candidates)
- 828 bundles with h⁰ ≥ 3, max h⁰ = 13
- Non-favorable toric ambient space (h¹¹_eff = 13)

**Open questions**: Which of the 320 clean bundles are slope-stable? Rank-4/5 bundle constructions from this base?

---

### h17/poly25 — Triple-Threat Champion (F-theory record)
**Score: 26/26 | 170 clean bundles | 15 elliptic fibrations (ALL-TIME RECORD)**

The only candidate excelling at all three compactification approaches simultaneously: heterotic (170 clean bundles), F-theory (15 elliptic fibrations — 50% more than the previous record), and LVS (Swiss cheese τ = 56). The 15 distinct elliptic fibrations represent 15 different F-theory compactification pathways, each with potentially different non-abelian gauge algebra from singular fibers.

Key properties:
- h¹¹ = 17, h²¹ = 20, χ = −6
- 2 del Pezzo divisors: dP₇ and dP₈ — both support rich non-perturbative effects
- **15 elliptic fibrations** — unprecedented. Each is a distinct F-theory model.
- **6 K3 fibrations** — largest among all candidates
- Swiss cheese τ = 56 — functional LVS hierarchy
- 490 bundles with h⁰ ≥ 3, max h⁰ = 8

**Open questions**: Kodaira singularity types for each of the 15 fibrations? Is τ = 56 sufficient for realistic de Sitter uplift?

---

### h17/poly63 — Former F-Theory Champion
**Score: 26/26 | 218 clean bundles | 10 elliptic fibrations**

Rich divisor structure (6 del Pezzo, including dP₄/₆/₇/₈ types), max h⁰ = 40 (highest of any T2-complete candidate), and the only candidate with a nef line bundle (almost all χ = −6 bundles are non-nef). 5 K3 + 10 elliptic fibrations before poly25 overtook the elliptic record.

Special feature: **1 nef bundle** — extremely rare in χ = −6 space. Nef bundles are automatically slope-semistable, removing the hardest stability verification step.

- SHA-256 fingerprint: `3cc2448f341e6e9a`
- Swiss cheese τ = 84, good LVS hierarchy

---

### h16/poly53 — Second Heterotic, No LVS
**Score: 23/26 | 300 clean bundles**

Second-highest clean bundle count. Rich fibration structure (5 K3 + 10 ell, matching poly25). Weakness: **no Swiss cheese structure** → loses all 3 LVS points. Would require KKLT or alternative moduli stabilization.

The 300 vs 320 clean bundles gap from poly2 is small. This is the best pure heterotic + F-theory candidate without LVS support.

---

### h15/poly61 — LVS Champion
**Score: 25/26 | τ = 14,300 (record)**

Largest τ/V²/³ ratio by a factor of ~7 over the second-best (h17/poly8 at τ=2,208). An extreme Swiss cheese: the small cycle is vastly smaller than the volume modulus. Ideal for checking LVS instability corrections and de Sitter uplift constructions. 110 clean bundles, 3 K3, 3 elliptic fibrations.

---

### h17/poly96 — Highest max h⁰
**Score: 25/26 | max h⁰ = 65 (record)**

Most global sections of any candidate. Large h⁰ = 65 suggests unusually deep bundle structure and potential for rank-2 bundles with large splitting numbers. 65 K3 fibrations (also a record for K3 count, though this may reflect counting ambiguity in the dual polytope method).

---

### Comparison table (select 26/26 scorers)

| Polytope | Score | Clean h⁰=3 | Max h⁰ | K3 fib | Ell fib | Swiss τ | dP | Best for |
|----------|-------|------------|--------|--------|---------|---------|-----|------|
| h14/poly2 | 26/26 | **320** | 13 | 3 | 3 | 3-dir | 3 | Heterotic |
| h16/poly11 | 26/26 | 298 | 13 | 3 | 3 | 150 | 5 | Heterotic #2 |
| h17/poly25 | 26/26 | 170 | 8 | **6** | **15** | 56 | 2 | F-theory / Triple-threat |
| h17/poly63 | 26/26 | 218 | **40** | 5 | 10 | 84 | 6 | F-theory #2 |
| h17/poly8 | 26/26 | 180 | — | 3 | 3 | 2,208 | 4 | LVS #2 |
| h16/poly63 | 26/26 | 78 | 37 | 4 | 6 | 836 | 5 | Balanced |
| h15/poly61 | 25/26 | 110 | 4 | 3 | 3 | **14,300** | — | LVS |

---

## 5. GL=12 / D₆ POLYTOPE — DEEP GEOMETRY STUDY

### Why this polytope is special
Of the full KS database, the h¹¹=17, h²¹=20 polytope at index 37 (fetched via `fetch_polytopes(h11=17, h21=20, lattice='N')`) is exceptional on three independent axes:

1. **χ = −6**: Native 3-generation, no quotient needed
2. **Maximal discrete symmetry**: |GL(Δ)| = 12, group ≅ D₆ (dihedral of the hexagon). This is the largest automorphism group of any polytope in the χ = ±6 class across all 104 Hodge pairs.
3. **Tractable period system**: D₆ reduces 20 complex-structure moduli to 5 D₆-invariant deformations, making the Picard-Fuchs system feasible.

This is the strongest candidate in the KS database for computing fermion mass hierarchies from geometry.

### Identity
| Property | Value |
|---|---|
| CYTools fetch | `fetch_polytopes(h11=17, h21=20, lattice='N')`, index 37 |
| Hodge numbers | h¹¹ = 17, h²¹ = 20, χ = −6 |
| Polytope | 4D reflexive, 14 vertices, 24 lattice points total |
| Dual | 9 vertices |
| Automorphism group | D₆ = Dih(6) = ⟨r,s \| r⁶=s²=1, srs=r⁻¹⟩, GAP ID SmallGroup(12,4) |
| SR ideal generators | 141 |
| Mori cone rays | 732 |
| Kähler cone rays | 547 |

### D₆ orbit structure on 24 lattice points
The 24 lattice points decompose into 8 orbits under D₆:
- 1 orbit of size 1 (origin/interior)
- 2 orbits of size 6 (the 12 vertices)
- 5 orbits of size 2–3 (boundary points)

After removing the interior point: **7 orbits on 23 toric divisors**. After 5 linear equivalences → **5 D₆-invariant Kähler moduli** (confirmed computationally). This is the dramatic dimension reduction that makes the Picard-Fuchs system tractable.

### The 12 D₆ generators as GL(4,ℤ) matrices
Acting by **right multiplication** on row-vector lattice points (`w = v @ M`):
```
g0 (id,  ord 1): [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
g1 (ord 2): [[1,3,0,0],[0,-1,0,0],[0,2,1,0],[0,2,0,1]]
g2 (ord 2): [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,-3,-1,-1]]
g4 (ord 2): [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]  ← swap coords 2↔3
g6 (ord 3): [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,-3,-1,-1]]
g7 (ord 6): [[1,3,0,0],[0,-1,0,0],[0,2,0,1],[0,-1,-1,-1]]
```
(Full set of 12 matrices in GL12_GEOMETRY.md.)

### Second Chern class
```
c₂ = [-120, 6, 26, 8, 8, 12, 8, -4, 12, 0, 4, 12, 12, -4,
        4,  4, 18, -6, 12, 0, -6, -6]
```
In the basis of 22 toric divisors (17 independent = h¹¹).

### D₆-invariant Yukawa couplings
The full 283 intersection numbers κ_{abc} project onto a **5×5×5 D₆-invariant sub-tensor** with 26 independent Yukawa couplings. These encode tree-level fermion masses and mixing angles in the 4D effective theory. The computation pipeline:
```
Triangulation → intersection ring → D₆-invariant projection → Yukawa tensor → Picard-Fuchs system → moduli-average of physical couplings
```
Status: Intersection ring computed. D₆ projection gives 26 invariant couplings. GKZ hypergeometric system for periods being analyzed.

### Picard-Fuchs / GKZ system
The 5 D₆-invariant deformations parametrize the period integrals Π(z₁,...,z₅) of the mirror family. The Gauss-Kiefer-Ziegler (GKZ) system for these periods consists of differential operators:
- ℤ-lattice of GKZ exponents determined by the GLSM charge matrix (17×22 matrix, given in GL12_GEOMETRY.md)
- Goal: closed-form period formula → exact Yukawa couplings as functions of complex-structure moduli
- Then: average over the moduli stabilization locus to extract physical predictions

---

## 6. KNOWN BUGS / PITFALLS (CYTools API)

Documented in MATH_SPEC.md. Key ones:

1. **`get_line_bundle_cohomologies()` argument convention**: Pass charges as a list of lists `[[c1, c2, ...]]`, not a flat list. Flat lists cause silent wrong results.

2. **LLL basis vs. input basis**: CYTools reorders lattice points via LLL reduction. The index `pt0` in CYTools output is NOT necessarily the first row of the vertex matrix you passed in. Always identify the interior lattice point explicitly (it's the unique point with all dual-polytope coordinates negative after polar transformation).

3. **Non-favorable subtelty**: When `h¹¹_amb > h¹¹` (non-favorable), the effective Kähler moduli count is h¹¹_eff = h¹¹, but line bundle charges are in the ambient-space basis (larger dim). Must project down carefully.

4. **`get_cy()` triangulation non-determinism**: For large polytopes, different calls to `get_cy()` with the same polytope may give different fine regular star triangulations (FRST). Use `get_cy(include_points_interior_to_facets=False)` for determinism and to match the KS database convention.

5. **Nef cone vs. Kähler cone**: `is_nef()` checks the Kähler cone of the CY, NOT the ambient toric variety. A divisor nef on the ambient space may not be nef on the CY. Always use `CalabiYau.is_nef(D)`.

6. **Swiss cheese τ computation**: τ = (D³)^{1/2} where D is the small cycle. The formula requires checking curvature of the LVS potential, not just D³ > 0. Use `τ = (D.triple_intersection_number())**(1/2)` but verify sign convention — negative D³ means wrong orientation.

7. **c₂ basis mismatch**: The second Chern class c₂ returned by CYTools is in the basis of ALL toric divisors (including those with linear relations), not the h¹¹-dimensional independent basis. Always apply the linear-relation projection before computing c₂·D for anomaly conditions.

8. **Cohomology timeouts**: For h¹¹ > 16, full bundle scans over all χ = ±3 bundles can take >12 hours. Use Tier 1.5 probe (300 random bundles) first.

9. **Elliptic fibration detection**: The standard method (2D reflexive subpolytopes of the dual) overcounts — some "fibrations" share the same base. Crosscheck with `is_K3_fibration()` and verify the pushforward formula.

---

## 7. ATHANOR RESEARCH HYPOTHESES (string landscape domain)

A parallel AI pipeline (Athanor) was run over the string landscape literature (214 concepts, 296 edges, 20 hypotheses generated). Top hypotheses rated 4.65/5 composite score — all "causal" bridge type:

### H1: Kähler–complex structure back-reaction (score 4.65)
> Complex structure moduli deformations causally constrain the Kähler moduli space through hierarchical back-reaction: ∂²W/∂zᵢ∂zⱼ (superpotential Hessian in complex-structure directions) directly determines the metric curvature of the Kähler moduli subspace via the special geometry relation, reducing effective dimensionality of available Kähler stabilization directions.

**Mechanism**: Complex structure moduli enter W as polynomial terms → deformations shift ∂²W/∂zᵢ∂zⱼ → propagates through Picard-Fuchs to periods Π → periods determine Kähler metric via special geometry → correlates which Kähler moduli can be independently stabilized.

**MDE**: Correlation r > 0.25 between complex-structure deformation and Kähler dimension reduction (n≥100 sampled vacua, 80% power); eigenvalue ratio shift ≥1.5× in effective Kähler metric Hessian.

**Relevance to CyTools**: Directly testable on the GL=12 polytope. The 5 D₆-invariant complex-structure moduli and 5 D₆-invariant Kähler moduli give a tractable 5×5 system to check whether complex-structure variations shift the Kähler metric eigenvalue spectrum.

---

### H2: Unified duality group from homology lattice (score 4.65)
> T-duality and mirror symmetry are commuting elements of a single unified duality group whose algebraic structure is fully determined by the homology lattice of the CY, causally determining which Type IIA and IIB vacua are physically equivalent.

**Mechanism**: T-duality permutes IIA ↔ IIB via odd/even-cycle exchange; mirror symmetry exchanges Kähler and complex moduli. Together they generate a finite-index subgroup of the geometric automorphism group of moduli space. Commutativity implies path-independence of moduli-space orbits under the duality group.

**MDE**: Orbit-matching fraction ≥70% (vs. random null ~20%) with n=500 vacua at α=0.05; Jaccard similarity ≥0.65 for duality-group recovery.

**Relevance**: The D₆ automorphism group of the GL=12 polytope is the concrete starting point — verify whether D₆ acts on the homology lattice in a way that generates known dualities.

---

### H3: Fourfold topology → new swampland criteria (score 4.65)
> CY fourfold singularity structure and fiber topology causally constrains 4D N=1 SUSY EFTs by enforcing non-trivial relations between Kähler moduli, superpotential coefficients, and gauge group representations invisible in threefold compactifications — yielding measurable reduction in consistent 4D vacuum cardinality and new swampland criteria.

**Mechanism**: F-theory on Y₄ induces singular elliptic fibration → monodromy, Kodaira singularity type, discriminant locus → 6D N=1 effective action → dimensional reduction to 4D. The fourfold structure acts as upstream constraint: gauge groups, matter spectra, and Yukawa textures allowed by threefold compactifications are selectively forbidden.

**MDE**: ≥25% absolute difference in fraction of 4D theories realizable exclusively by fourfolds vs. threefolds (n=500 fourfolds, n=10k threefolds, 80% power); R² > 0.25 for multivariate model predicting 4D EFT from fourfold geometry; new constraint reduces consistent 4D theory cardinality by ≥20%.

---

### H4: Singularity invariants → physical moduli constraints (score 4.65)
> Log-canonical threshold, discrepancy, and derived category generators of a CY variety causally determine dimension and structure of the string theory moduli space — varieties with identical smooth deformation types but different singular resolutions yield inequivalent physical consistency constraints and enhanced gauge symmetries.

**Mechanism**: Singularities act as "anchorpoints" for D-brane categories and exceptional collections. (1) Higher log-canonical threshold → fewer geometric deformations → reduced moduli dimension. (2) Non-trivial Chow group generators encode non-geometric fluxes that stabilize moduli. (3) Exceptional collections in derived category lift to enhanced gauge groups via Sen limits.

**MDE**: |ρ| ≥ 0.6 (Spearman) between singularity invariants and moduli dimension; moduli dimension change ≥5 between singular and smooth models (Cohen's d ≥ 1.0).

---

### H5: T-duality compositional closure of the duality taxonomy (score 4.65)
> The complete taxonomy of string dualities can be systematically derived as compositions of T-duality operations and their generalizations (T-folds, non-geometric fluxes, mirror symmetry), forming a semigroup under graph concatenation that generates S-duality, heterotic-Type II duality, and F-theory duality as derived consequences.

**MDE**: ≥75% coverage of documented dualities by T-duality compositions (9/12 major dualities); ≥2 internally consistent novel duality chains discovered with zero swampland violations.

---

### H6: Rigid CY mirror rigidity (score 4.65)
> The mirror of a rigid CY threefold (h¹¹=1, h²¹=0) is either singular or itself rigid (h²¹(Y)=0), preserving the absence of continuous deformations under the duality exchange h^{p,q}(X) ↔ h^{n-p,q}(Y).

**Mechanism**: Under naive mirror exchange, rigid X (h¹¹=1, h²¹=0) maps to Y with h¹¹(Y)=0, h²¹(Y)=1. If rigidity imposes global Hodge-theoretic constraints, the mirror must either inherit dual rigidity or develop special singularities blocking the predicted moduli deformations. Rigidity is preserved under duality, not broken by it.

---

### H7: Gauge coupling unification as landscape attractor (score 4.4)
> Gauge coupling unification (α₁≈α₂≈α₃ within 5% at M_U > 10¹⁵ GeV) is 3–5× enriched over random chance in the string landscape, driven by geometric constraints on Kähler moduli and flux quantization rather than anthropic selection.

**MDE**: f_random ≈ 0.015; f_unif ≥ 0.035 (2.3-fold enrichment) detectable with n=10,000 vacua at power 0.90, α=0.01.

---

### H8: F-theory generation counting via matter curve cohomology (score 4.25)
> Number of chiral fermion generations in F-theory equals dim H¹(C, 𝒪_C) + χ_gauge, where C is the matter curve and χ_gauge accounts for monodromy and bundle topology. Three generations arises when h¹(C, 𝒪_C) ≈ 2–3.

**Mechanism**: Matter localizes on matter curves (elliptic fibration discriminant locus). Chiral zero-mode count = h¹(C, 𝒪_C) + χ_gauge; varying base geometry and bundle structure shifts this by modulating the cohomological dimension.

**MDE**: Pearson r ≥ 0.75 (R² ≈ 0.56); median absolute error ≤ 0.8 generations; h¹(C, 𝒪_C) + χ_gauge accounts for >50% of total SHAP value magnitude.

---

### H9: Reflexive polytope combinatorics → Hodge numbers (score 4.25)
> Normalized lattice point density, Gorenstein index, and face lattice depth causally constrain h¹¹ and singularity genus of CY hypersurfaces, enabling predictive screening without explicit geometric computation.

**Mechanism**: Reflexivity couples lattice point distribution to the algebraic geometry via toric geometry: Hodge diamond determined by Stanley-Reisner ring → encoded in face lattice. Gorenstein index and lattice density proxy for singularity/degeneracy; face lattice depth controls resolution complexity.

**Practical value**: If validated, this is a 10,000× compute speedup for pre-screening the h¹¹ = 18+ layers.

**MDE**: Spearman ρ ≥ 0.40 between any single invariant and h¹¹ (n > 5000); 40% MAE reduction from baseline; classification precision ≥ 0.75.

---

### H10: Moduli stabilization reduces landscape by ≥3 orders of magnitude (score 4.25)
> Flux-quantization compatibility with CY topology (not phenomenological requirements) reduces the viable compactification space by ≥10³, with the causal chain: CY topology → flux-quantization compatibility → moduli-space structure → 4D EFT realizability → phenomenology.

**MDE**: Reduction ratio R_flux ≥ 2.0 (≥100-fold); odds ratio for known models in top 10% of filtered space > 2.5; entropy difference between 4D-viable and unfiltered landscape > 0.5 nats.

---

## 8. CROSS-DOMAIN INSIGHTS (from Athanor cross-domain analysis)

### Information Theory × String Landscape (13 bridges, threshold 0.45)

**Most compelling bridge**: *Stochastic representations of landscape geometries decomposed into integral representations over random measures on moduli spaces*
> Reformulating MCMC exploration of flux vacua as integral representations with random measures could yield principled sampling algorithms with provable convergence guarantees, correcting the current ad-hoc landscape sampling approach.

**Probability distributions over moduli spaces**: Applying Shannon/relative entropy to distributions over string moduli spaces could reveal whether the landscape exhibits phase transitions or universal statistical signatures — analogous to how entropy detects phase transitions in statistical mechanics.

---

### Quantum Computing × String Landscape (40 bridges — unexpectedly dense)

The embedding similarity between quantum computing and string landscape concept graphs was high enough to surface 40 pairs above the 0.45 cosine threshold — far more than any other cross-domain pair involving string landscape. The dominant shared concept hub is `quantum gravity`.

**Most compelling bridge**: *QC architectures derived from CY geometry to simulate quantum gravitational dynamics*
> Embed CY fiber topology into qubit connectivity: circuit geometry IS the compactification geometry. The Kähler cone of the CY gives the space of valid quantum circuit parameters; monodromy around singularities gives the logical gate set. A quantum simulator whose topology mirrors the fibration structure could efficiently propagate quantum gravity dynamics in specific compactifications.

**Planck-scale computational limits**:
> Does the Planck length impose a lower cutoff on the information density representable in a quantum circuit? Does the string landscape degeneracy constrain which quantum gravity computations are physically realizable — i.e., does landscape structure impose a complexity ceiling?

**Why 40 bridges**: Both domains have dense vocabulary around "quantum", "duality", "geometry", "deformation", "stability", "moduli". The embedding model treats these as structurally analogous even though the underlying physics is different. Treat with calibrated skepticism — but the Planck-scale computational limits question is genuinely open.

---

### Athanor Meta × String Landscape (4 bridges)

This is the highest-quality small set. All 4 bridges are variants of the same deep question: **Can machine learning trained on string landscape data serve as a physics oracle?**

> *Can ML systems trained on CY geometry databases (mirror symmetry, periods, Hodge diamonds) systematically discover particle physics models satisfying both theoretical constraints (gauge group structure, anomaly cancellation) and experimental constraints (coupling constants → electroweak precision)?*

This is the operational agenda item: Athanor surfaces the hypothesis; CyTools provides the geometric computational substrate to test it.

---

## 9. IMMEDIATE OPEN PROBLEMS

Listed in priority order by tractability × impact:

**P1 (tractable now): Kähler-complex back-reaction on GL=12**
Using the 5 D₆-invariant complex-structure moduli and the 5 D₆-invariant Kähler moduli of the GL=12 polytope, compute the Hessian ∂²W/∂zᵢ∂zⱼ for a sample of flux choices, then check whether this matrix correlates with the eigenvalue spectrum of the Kähler metric. This is CYTools + Picard-Fuchs, tractable.

**P2 (tractable now): Collision-free Yukawa extraction for GL=12**
26 D₆-invariant Yukawa couplings are determined; moduli-space integral over them has not been computed. Compute the superpotential at several D₆-fixed points in moduli space and compare fermion mass ratios to observed values.

**P3 (near-term compute): h17 scan completion**
h17 has 38,735 polytopes, ~42% scanned (Codespace). 6 T2-complete candidates already found (poly8, poly25, poly63, poly96, ...). Would take ~40 CPU-hours to finish.

**P4 (ML screening): Polytope combinatorics → h¹¹ predictor**
Hypothesis H9 above — train a regression on normalized lattice point density, Gorenstein index, face lattice depth to predict h¹¹. Validation dataset is h11=13–16 (complete). If it works, apply as pre-screen to h11=18+ (195K polytopes). Estimated >100× scan speedup.

**P5 (speculative, high-impact): Elliptic fibration gauge algebra for h17/poly25**
15 elliptic fibrations found. For each, compute the singularity type of the discriminant locus → Kodaira classification → non-abelian gauge algebra. Check which fibrations could give SU(5) or SO(10) GUT gauge group.

---

## 10. KEY FILE LOCATIONS

```
/home/seth/dev/cytools_project/
├── pipeline.py               Main per-polytope analysis script
├── scan_parallel.py          Parallel scan driver (h11 range, n workers)
├── tier1_screen.py           Fast Tier 1 screening
├── tier2_screen.py           Full bundle scan
├── GL12_GEOMETRY.md          Complete geometry of the D₆ polytope
├── FINDINGS.md               Detailed write-ups for each key candidate
├── MATH_SPEC.md              CYTools API bugs + mathematics specification
├── CATALOGUE.md              Full catalogue of what's been tried + ruled out
├── PROCESS_LOG.md            Sequential lab notebook: dates, decisions, results
├── BACKLOG.md                Ranked TODO list
├── results/                  Per-polytope output files (text + JSON)
├── mori_pf.py                Mori cone / Picard-Fuchs analysis scripts
├── picard_fuchs.py           Current PF system computation
└── venv/                     Python virtualenv (activate: source activate.sh)
```

---

## 11. CONVENTIONS & TERMINOLOGY

- **Clean bundle**: Line bundle L on CY3 with h⁰(L)=3, h¹(L)=h²(L)=h³(L)=0. Represents exactly 3 zero-mode families with no vector-like pairs. The gold standard for heterotic model building.
- **Swiss cheese**: Calabi-Yau volume V = (τ_big)^{3/2} - (τ_small)^{3/2}, where τ = D² (size of holomorphic 2-cycle). The small cycle τ_small is the Swiss cheese divisor. Large τ/V^{2/3} ratio → exponential suppression of instanton effects → viable LVS hierarchy.
- **Non-favorable**: Ambient toric space has h¹¹_amb > h¹¹_CY, meaning not all line bundles on the ambient space restrict to independent bundles on the CY. Affects bundle charge convention.
- **T2 score**: Our 26-point scoring rubric (see §2). T2=45 is the old notation (before calibration); now out of 26.
- **NF**: Non-favorable (in candidate tables above).
- **LVS**: Large Volume Scenario. KKLT and LVS are the two main moduli stabilization mechanisms. Both require specific Kähler cone structures.
- **KS database**: Kreuzer-Skarke database of 473 million reflexive polytopes in 4D. Available via `fetch_polytopes()` in CYTools.
- **Hodge pair**: (h¹¹, h²¹). χ = 2(h¹¹ - h²¹). For χ = −6: h²¹ = h¹¹ + 3.
- **D₆ / Dih(6)**: Dihedral group of order 12 (symmetries of a hexagon). Not to be confused with D₆ Lie algebra. In GAP notation: SmallGroup(12,4).
- **GKZ system**: Gelfand-Kapranov-Zelevinsky hypergeometric system. The natural class of differential equations for period integrals of toric hypersurfaces. The PF system for our GL=12 polytope is a GKZ system in 5 variables (D₆-invariant complex-structure moduli).

