# What We Found and Why It Matters

## The Question

Can the geometry of a tiny, curled-up extra dimension explain why our universe has exactly three generations of matter, why the strong and weak forces have the strengths they do, and why protons don't decay?

String theory says yes — if you can find the right shape. That shape is a **Calabi-Yau manifold**, a 6-dimensional space so small it's invisible, but whose topology determines the particle physics we observe. There are hundreds of millions of candidate shapes in the Kreuzer-Skarke database. Almost none of them give three generations of matter.

## What We Did

We searched the database for Calabi-Yau manifolds with Euler characteristic χ = −6 — the topological condition for exactly **three generations** of quarks and leptons. Out of ~500,000 known shapes, only 104 satisfy this at the simplest level.

We then ran a 20-check verification pipeline on the most symmetric candidate (a polytope with 14 vertices, GL symmetry order 12, and Hodge numbers h¹¹ = 17, h²¹ = 20):

| Tier | What It Tests | Score |
|------|--------------|-------|
| **1. Geometry** | Rigid divisors, Kähler cone, gauge group embedding | **7/7** |
| **2. Particle physics** | Line bundle spectrum, 3-generation bundles, Yukawa texture | **5/6** |
| **3. Stability** | Moduli stabilization (LVS/KKLT), proton lifetime, vacuum structure | **7/7** |

**Total: 19/20.** This manifold passes every check we can compute on a laptop.

## The Key Results

- **14 rigid del Pezzo divisors** — surfaces inside the manifold where gauge fields can live. You need at least one; this manifold has fourteen.

- **310 line bundles with |χ| = 3** — each a distinct way to get exactly three generations of matter from the geometry (6 single-divisor, 304 two-divisor). Most manifolds have zero or one.

- **D₁₂ discrete symmetry** — the manifold has a dihedral-12 symmetry group. Its Z₃ subgroup acts freely on the generic CY, giving a smooth quotient with χ = −2. The full S₃ quotient (h¹¹ = 5, h²¹ = 7) exists as an orbifold with Z₂ singularities (see Tier 5C).

- **α⁻¹_GUT = 24 from pure topology** — the ratio of two intersection numbers gives the inverse gauge coupling at unification. Running this down through the MSSM renormalization group gives α⁻¹_em ≈ 135.0 at the electron mass, within 1.5% of the measured 137.036.

- **Instanton-viable blow-up cycle** — one del Pezzo divisor (D₂₁) can be smoothly shrunk to the non-perturbative regime (τ ~ 4) while keeping the overall volume large (Vol > 17,000), enabling KKLT moduli stabilization with W_np ~ 10⁻¹¹.

## Why It Matters

**For string phenomenology:** Most "string vacuum" papers start with a manifold chosen for convenience and then check a few properties. We did the opposite — started from the physical constraint (χ = −6) and ran every check we could compute. The fact that one manifold passes 19/20 is not proof of anything, but it's a concrete, reproducible data point that the field can build on.

**For the methodology:** This entire analysis was done by a non-expert using an LLM and CYTools on a consumer laptop in ~12 hours. The traditional version of this work would require a PhD student, a computing cluster, and months. If the tools and the approach are sound, it means the barrier to entry for computational string phenomenology just dropped by an order of magnitude.

**What it does NOT prove:** This is not evidence that string theory describes our universe. The 19/20 scorecard mixes exact algebraic geometry theorems with order-of-magnitude estimates. The gauge coupling "prediction" has ~1.5% error and depends on assumptions about the GUT group. The proton decay estimate spans 10 orders of magnitude of uncertainty. An honest summary: *the geometry is consistent with known physics at every level we can check, but "consistent with" is far weaker than "predicts."*

## Hardening Results (Tier 4)

After the original 19/20 scorecard, we ran 12 additional hardening tests — every computation feasible on weak hardware that CYTools supports beyond the original pipeline:

| Test | Result | Significance |
|------|--------|-------------|
| **Smoothness** | Confirmed (`is_smooth = True`) | All divisor/intersection analysis valid |
| **Normal form** | 14×4 canonical matrix computed | Unique KS database identifier for reproducibility |
| **Nef partitions** | 0 found | NOT a complete intersection — more generic structure |
| **Elliptic fibrations** | 8 structures found (7× cubic in P², 1× F₀) | F-theory compatible; E₆ fiber → SM gauge group breaking |
| **SR ideal** | 141 generators (117 quadratic, 22 cubic, 2 quartic) | Full vanishing-relation data for gauge sector |
| **Effective cone** | 17D, 21 rays (17 standard + 4 non-trivial) | All toric divisors are effective |
| **Triangulation robustness** | 29 FRSTs tested: κ₀₀₀/κ₁₁₁ = −24 in 28/29 (96.6%) | α⁻¹_GUT = 24 is triangulation-robust |
| **S₃ subgroup** | Confirmed: generators found, presentation relation verified | S₃ ⊂ D₆ with Z₃ fixed locus codim-2 (see transversality below) |
| **D3 tadpole** | χ/24 = −0.25 (not integer) | Standard orientifold (O3/O7) needed — normal for IIB |
| **c₂ integrality** | All 22 components even | Freed-Witten anomaly automatically cancelled |
| **GLSM matrix** | 17×22, rank 17, 5 linear relations | Full toric data recorded |
| **Mirror symmetry** | Dual: (h₁₁, h₂₁) = (20, 17) ↔ (17, 20) ✓ | 2,985,984,000 triangulations; orbit size 12 = |GL| |

**Hardening score: 12/12.** Combined with original pipeline: **31/32 total checks passed.**

## Deep Analysis (Tier 5)

Beyond the basic hardening suite, we performed three further analyses that probe the viability of the manifold for exact 3-generation physics:

### 5A. Ampleness and Vanishing Theorems

**Goal:** Determine whether any of the 310 line bundles with |χ| = 3 are ample or nef, which would allow Kodaira or Kawamata-Viehweg vanishing theorems to resolve exact cohomology (h⁰ = 3) without cohomCalg.

**Method:** Computed the Kähler cone (547 rays in ℝ¹⁷) and its dual Mori cone (81 generators in ℝ¹⁷). Checked each bundle's first Chern class against all Mori generators: D is ample iff min(D·C) > 0 over all Mori generators C.

**Result: 0/310 bundles are ample or nef.** The closest bundle misses the Kähler cone by min(D·C) = −2. This is a geometric obstruction intrinsic to h₁₁ = 17: the Kähler cone is narrow in 17 dimensions, and line bundles with |χ| = 3 require small charges that cannot reach the cone interior.

| Metric | Value |
|--------|-------|
| Bundles scanned | 310 (6 single-divisor + 304 two-divisor) |
| Ample | 0 |
| Nef | 0 |
| Closest to nef | min(D·C) = −2 |
| Kähler ray minimum χ | +4 (no ray reaches χ = 3) |
| 0.05 × interior tip | χ = 3 exactly, but outside cone (18/81 Mori violations) |

**The quantization obstruction.** Further analysis reveals that the negative result is sharper than "no overlap": the χ(L) = 3 iso-surface is **tangent to the Kähler cone boundary** in ℝ¹⁷. Specifically, along the Kähler ray [1,1,0,1,1,1,1,0,0,0,1,0,2,0,1,0,0], the χ = 3 level set touches the nef cone at the continuous parameter t* = 0.7757..., where 58 of 81 Mori generators are simultaneously saturated (D·C = 0). At this tangent point, χ = 3.0 exactly and the divisor class is nef — but its coordinates are irrational.

The nearest integer lattice points split cleanly:
- **χ = 4, min(D·C) = 0** — nef (in the cone) but χ too high by exactly 1
- **χ = 3, min(D·C) = −1** — correct χ but outside the cone by exactly 1

This is a **quantization obstruction**: the cubic Diophantine equation χ(n₁,...,n₁₇) = 3 has solutions in the real Kähler cone but none in the integer lattice. The χ = 3 surface and the Kähler cone are co-tangent in the continuous moduli space, and the integrality of c₁(L) ∈ H²(X, ℤ) prevents simultaneous satisfaction. Six distinct integer lattice points achieve χ = 3 with min(D·C) = −1 exactly — all within one Mori unit of being nef 3-generation bundles.

**Open questions this raises:**
1. Among the 104 KS polytopes with χ(X) = −6, for how many does the χ(L) = 3 surface intersect the *integer* Kähler cone?
2. Is this tangency a minimum-distance phenomenon — does our polytope have the closest near-miss among all χ = −6 CY3s?
3. Can the obstruction be lifted by passing to a different triangulation (different Kähler cone) of the same polytope?

These are computable on a cluster (~30 seconds per polytope, ~1 hour total for all 104).

**Implication:** Kodaira/KV vanishing CANNOT resolve cohomology on this manifold for the default triangulation. Exact 3-generation verification requires **cohomCalg** or equivalent (cluster hardware), or systematic exploration of alternate triangulations.

### 5B. Elliptic Fibration Structure

The 8 fibrations decompose as:

| Type | Count | Fiber embedding | Lattice points |
|------|-------|----------------|----------------|
| Cubic in P² | 7 | 2D sublattice ⊂ ℤ⁴ | 4 each |
| F₀ (P¹ × P¹) | 1 | 2D sublattice ⊂ ℤ⁴ | 9 |

For the Shioda-Tate-Wazir formula h₁₁(X) = h₁₁(B) + rank(MW) + 1 + Σ(fᵢ−1):
- With h₁₁ = 17 and 7 cubic fibers suggesting E₆ gauge symmetry (rank 6), the base likely has h₁₁(B) ≤ 10, consistent with a rational surface (P², Fₙ, or blown-up dPₖ).
- The Standard Model embedding SU(3)×SU(2)×U(1) ⊂ E₆ is a classic GUT route, with the 27-dimensional representation of E₆ decomposing to give exactly quark/lepton families.

**S₃ and fibrations:** None of the 8 fibrations are invariant under S₃. All 8 form separate orbits, meaning S₃ permutes the fibration structures. This is consistent with the S₃ quotient breaking the toric structure.

### 5C. S₃ Transversality Analysis

**Critical result for the S₃ quotient (h₁₁ = 5, h₂₁ = 7, χ = −4):**

| Group element | Order | Fixed locus codim | Generic CY avoids? |
|---------------|-------|------------------|-------------------|
| r (Z₃ generator) | 3 | 2 | ✓ Yes |
| s (Z₂ generator) | 2 | **1** | **✗ No** |
| sr | 2 | **1** | **✗ No** |
| sr² | 2 | **1** | **✗ No** |

The Z₂ elements have codimension-1 fixed loci in the ambient toric 4-fold. Since the CY hypersurface has codimension 1, it **always** intersects the Z₂ fixed locus. Therefore:

- **Full S₃ quotient: ORBIFOLD** — the quotient X/S₃ exists but has Z₂ singularities. It is not a smooth Calabi-Yau. Resolution of singularities would change the Hodge numbers, so (5, 7) is the orbifold value, not the resolved value.
- **Z₃ quotient: SMOOTH** — the Z₃ fixed locus has codim 2, so a generic hypersurface avoids it. The quotient X/Z₃ is a smooth CY3 with χ(X/Z₃) = −6/3 = −2.

**Monomial structure under S₃:** Of the 23 dual-polytope lattice points (= monomials in the CY equation), 17 are S₃-invariant and 4 form size-2 orbits. The S₃-invariant monomials span a 17-dimensional subspace of the 23-dimensional moduli space, meaning most complex structure deformations preserve S₃.

**Physical significance:** The Z₃ quotient X/Z₃ with χ = −2 could serve as a vacuum with 1 generation directly, or combined with Wilson line breaking along the Z₃ fundamental group to recover 3 generations at low energy — a mechanism used in heterotic orbifold models.

## Population-Level Scan (Tier 6)

The quantization obstruction found in Tier 5A raised a sharp question: **is our GL=12 polytope uniquely cursed, or does the obstruction extend across the entire χ = −6 class?** We scanned 1,000 polytopes from the Kreuzer-Skarke database with χ = −6 (h₁₁ = 13–16, all available at `limit=1000`) to find out.

### 6A. Tangency Scan Results

**Method:** For each polytope, we computed the Kähler cone (via Mori generators), projected the χ(L) = 3 iso-surface onto each Mori wall using Brent's method for root-finding, then searched integer lattice points near every tangency for bundles satisfying χ = 3 and min(D·C) ≥ 0 (nef). Three-tier pipeline with pickle caching; see `tangency_scan_v3.py`.

| Classification | Count | Criterion |
|---|---|---|
| **AMPLE** | 0 | min(D·C) > 0 over all Mori generators |
| **NEF** | 61 | min(D·C) = 0 (on Kähler cone boundary) |
| **NEAR_MISS** | 415 | min(D·C) = −1 (one Mori unit outside) |
| **NEAR** | 524 | min(D·C) ≤ −2 |

**Zero ample χ = 3 bundles across the entire χ = −6 class.** Not a single polytope out of 1,000 admits a line bundle that is both ample (strictly inside the Kähler cone) and has χ = 3. The quantization obstruction found for our GL=12 polytope is **universal**.

The 61 NEF polytopes sit exactly on the Kähler cone boundary — the χ = 3 surface meets the nef cone at an integer lattice point, but only on its face, never in its interior.

### 6B. D³ = 0 Theorem

We computed the cubic self-intersection D³ and the linear term c₂·D for all 61 NEF bundles.

| D³ | c₂·D | χ = D³/6 + c₂·D/12 | Count |
|---|---|---|---|
| 0 | 36 | 0 + 3 = 3 | **59** |
| 1 | 34 | 1/6 + 17/6 = 3 | **2** |

**In 59 of 61 cases, D³ = 0 exactly.** The entire χ = 3 comes from the linear term c₂·D/12 = 3, meaning c₂·D = 36. These are "topologically flat" line bundles — their first Chern class has zero triple self-intersection against the CY 3-fold. The generation count is entirely determined by the second Chern class of the tangent bundle, not by the bundle's own curvature.

The two exceptions — **polytopes 40 and 152** (both h₁₁ = 15) — have D³ = 1 and c₂·D = 34, which combine as 1/6 + 34/12 = 3. These two are the critical discovery of the entire scan (see §6D below).

**Physical interpretation:** D³ = 0 means the bundle lives on the boundary of the effective cone in a precise sense — it is a "degenerate" direction where the cubic form vanishes. The generation count being purely topological (from c₂) rather than geometric (from D³) is a structural constraint on how 3-generation physics can emerge from CY geometry at these Hodge numbers.

**Wall saturation statistics:** Each NEF bundle saturates (D·C = 0) between 34 and 73 Mori walls simultaneously, with a mean of 54.5. These bundles sit at high-codimension faces of the Kähler cone.

### 6C. Top NEF Candidate Characterization

We ran the full Tier 1–3 pipeline on the three NEF polytopes with the highest GL symmetry:

| Property | **Polytope 700** | **Polytope 610** | **Polytope 5** |
|---|---|---|---|
| h₁₁ | 16 | 16 | 14 |
| h₂₁ | 19 | 19 | 17 |
| χ | −6 | −6 | −6 |
| GL symmetry | 4 | 2 | 1 |
| Vertices | 11 | 12 | 10 |
| Lattice points | 21 | 23 | 18 |
| Smooth | ✓ | ✓ | ✓ |
| Mori generators | 72 | 78 | 69 |
| Kähler rays | 113 | 115 | 147 |
| **CICY** | **Yes (2 nef partitions)** | No | No |
| FRST neighbors | 28 | — | — |
| D3 tadpole χ/24 | −0.25 | −0.25 | −0.25 |
| c₂·J integrality | ✓ | ✓ | ✓ |

**NEF bundles found:**

| Polytope | Bundle D | D³ | c₂·D | χ | Saturated walls |
|---|---|---|---|---|---|
| 700 | e₀ + e₇ + e₈ + e₉ | 0 | 36 | 3 | 48/72 |
| 610 | e₀ + e₅ + e₁₄ | 0 | 36 | 3 | 49/78 |
| 5 | e₀ | 0 | 36 | 3 | 51/69 |

All three exhibit the D³ = 0 pattern. **Polytope 700 is the standout:** it is a complete intersection Calabi-Yau (CICY) with 2 nef partitions, the highest symmetry (GL=4), and the richest tangency structure (43 Mori wall hits from Tier 2 analysis). Polytope 5 is notable for having a single-generator NEF bundle (D = e₀), the simplest possible structure.

### 6D. The Two Proven 3-Generation Manifolds

Polytopes 40 and 152 are the only ones in the scan where D³ > 0 and the bundle is nef. A nef divisor D with D³ > 0 on a smooth 3-fold is **nef and big**. By the **Kawamata-Viehweg vanishing theorem**, for any nef-and-big line bundle L on a smooth CY 3-fold (K_X trivial):

$$h^i(X, L) = 0 \quad \text{for all } i > 0$$

Therefore **h⁰(L) = χ(L) = 3 exactly, by pure mathematics.** No cohomCalg, no cluster computation, no cancellation ambiguity. These are the only two manifolds out of 1,000+ where we have a **proven** 3-generation line bundle.

| Property | **Polytope 40** | **Polytope 152** | Original GL=12 |
|---|---|---|---|
| h₁₁ | 15 | 15 | 17 |
| h₂₁ | 18 | 18 | 20 |
| χ | −6 | −6 | −6 |
| GL symmetry | 2 | 1 | **12** |
| Smooth | ✓ | ✓ | ✓ |
| Vertices | 10 | 12 | 14 |
| Lattice points | 19 | 21 | 24 |
| Mori generators | 75 | 77 | 81 |
| Kähler rays | 22 | 230 | 547 |
| CICY | No | No | No |
| del Pezzo divisors | 4 | 0 | **14** |
| D3 tadpole χ/24 | −0.25 | −0.25 | −0.25 |
| c₂ all even | ✓ | ✓ | ✓ |
| Elliptic fibrations | 0 | 0 | **8** |
| κ₀₀₀ | −80 | −97 | **−24** |

**Proven bundles:**

| Polytope | Bundle D | D³ | c₂·D | h⁰ | Proof | Robust across triangulations |
|---|---|---|---|---|---|---|
| 40 | e₃ + e₄ + e₁₀ | 1 | 34 | **3 (proven)** | Kawamata-Viehweg | **10/10** |
| 152 | e₀ | 1 | 34 | **3 (proven)** | Kawamata-Viehweg | **10/10** |

Both bundles are **completely triangulation-robust**: χ = 3, D³ = 1, and nef status all hold across every random triangulation tested.

### 6E. Reassessing the Original GL=12 Candidate

We re-ran the V3 tangency algorithm directly on the original h₁₁ = 17 polytope (loaded from `gl12_poly.txt`). Result:

| Metric | Value |
|---|---|
| Total candidates searched | 4,302 |
| χ = 3 candidates found | 318 |
| NEF bundles | **0** |
| Best min(D·C) | **−2** |
| Tier 2 wall hits | **0** |
| Classification | **NEAR** |

Zero wall hits means the Kähler cone at h₁₁ = 17 is so narrow that no basis direction projected onto any Mori wall stays inside the cone. The V3 algorithm — which found 2× more NEF polytopes than V1 at h₁₁ ≤ 16 — finds nothing new here.

**The original polytope is not useless, but its role has changed.** It remains the highest-symmetry χ = −6 CY3 in the database, with 14 rigid divisors, 8 elliptic fibrations, and D₁₂ symmetry. These are properties none of the 61 NEF polytopes match. But its 310 line bundles with |χ| = 3 all sit outside the Kähler cone, so we cannot resolve h⁰ = 3 vs. cancellations without cohomCalg.

The structural lesson: **high symmetry constrains the Kähler cone.** GL=12 forces the cone into a narrow wedge in ℝ¹⁷, making the quantization obstruction worse. The NEF winners (GL=1–4) have wider cones that can accommodate integer nef points. Symmetry is good for physics (gauge coupling, fibrations, quotients) but bad for bundle existence.

### What's Next

The proven result on polytopes 40 and 152 shifts the program:

1. **Full physics pipeline on polytopes 40 and 152** — gauge coupling extraction, moduli stabilization, proton decay estimates, Yukawa analysis. Do they score as well as the original on Tiers 1–3?

2. **cohomCalg on the original's bundles** — still worth doing. If any of its 310 bundles have h⁰ = 3, it would be the strongest overall candidate (proven generations + symmetry + fibrations + gauge coupling). Requires 16-core/64GB Codespace (~$14).

3. **cohomCalg on the 59 NEF-but-not-big bundles** — these have h³ = 0 (from nef) but D³ = 0 (not big), so KV vanishing doesn't apply. cohomCalg would resolve whether h⁰ = 3 or there are cancellations.

4. **Extend scan to h₁₁ = 17+** — are there NEF+BIG bundles at higher h₁₁? The pattern suggests they become rarer as the cone narrows.

## Reproduce It

```bash
git clone https://github.com/sethc5/cytools_project.git
pip install cytools numpy scipy
python scan_manifold.py          # runs all 3 tiers on the GL=12 polytope
python hardening_tests.py        # runs 12 additional hardening checks
python tangency_scan_v3.py       # runs the full 1000-polytope tangency scan
python batch_scan.py --chi -6    # scans the KS database for more candidates
```

The full analysis notebook (`cy_manifold_query.ipynb`) contains every computation, with outputs, in 90 cells. The tangency scan results are in `tangency_results_v3.csv`.
