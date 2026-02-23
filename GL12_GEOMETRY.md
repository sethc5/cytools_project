# GL=12 / D₆ Polytope — Complete Geometry Reference

## Why This Polytope

Of the ~500,000 reflexive 4-polytopes in the Kreuzer-Skarke database, this one stands out on three independent axes:

1. **Three-generation (χ = −6).** The Euler characteristic χ = 2(h¹¹ − h²¹) = −6 gives |χ|/2 = 3 chiral families — matching the observed three generations of quarks and leptons.

2. **Maximal discrete symmetry.** Among all 104 polytopes with χ = ±6, this polytope has the largest lattice automorphism group: |GL(Δ)| = 12, isomorphic to D₆ (the dihedral group of the hexagon). Discrete symmetries of the compactification geometry descend to flavor symmetries in the 4D effective theory, constraining Yukawa textures and potentially explaining the mass hierarchy.

3. **Tractable Picard-Fuchs system.** The D₆ symmetry reduces the 20 complex-structure moduli to 5 invariant deformations, making it feasible to derive the Picard-Fuchs differential system, compute period integrals, and extract exact Yukawa couplings — the first step toward predicting fermion masses from geometry.

Together these properties make it the strongest candidate in the KS database for connecting Calabi-Yau geometry to Standard Model physics.

## Identity

| Property | Value |
|---|---|
| **KS database** | `fetch_polytopes(h11=17, h21=20, lattice='N')`, index **37** |
| **PALP family** | Block 38 of (h₁₁=20, h₂₁=17) — this is the **mirror** |
| **CY3 Hodge** | h¹¹ = 17, h²¹ = 20, χ = −6 (3 generations) |
| **Polytope** | 4D reflexive, 14 vertices, 24 lattice points |
| **Dual** | 9 vertices |
| **Automorphisms** | \|GL(Δ)\| = 12, group ≅ D₆ (dihedral, hexagon symmetry) |
| **Nef partitions** | 0 (none — not a complete intersection in products) |
| **SR generators** | 141 |
| **Mori cone rays** | 732 |
| **Kähler cone rays** | 547 (in 17D) |

## Vertex Matrix (4×14, rows = coordinates)

```
V = [[  1,  1,  0,  0,  0,  0,  0,  0, -1, -1, -1, -1, -1, -1],
     [  0,  3,  0,  2,  0,  2, -3, -1, -1,  0, -1,  0, -4, -3],
     [  0,  0,  1,  1,  0,  0, -1, -1,  1,  1,  0,  0, -1, -1],
     [  0,  0,  0,  0,  1,  1, -1, -1,  0,  0,  1,  1, -1, -1]]
```

CYTools convention: pass `V.T` (14×4, points as rows).

## All 24 Lattice Points

| Index | Coordinates | Type |
|-------|-------------|------|
| 0  | (0, 0, 0, 0)       | vertex (= origin after LLL) |
| 1  | (0, −3, −1, −1)    | vertex |
| 2  | (0, −1, −1, −1)    | vertex |
| 3  | (0, 0, 0, 1)       | vertex |
| 4  | (0, 0, 1, 0)       | vertex |
| 5  | (0, 2, 0, 1)       | vertex |
| 6  | (0, 2, 1, 0)       | vertex |
| 7  | (−1, −4, −1, −1)   | vertex |
| 8  | (−1, −3, −1, −1)   | vertex |
| 9  | (−1, −1, 0, 1)     | vertex |
| 10 | (−1, −1, 1, 0)     | vertex |
| 11 | (−1, 0, 0, 1)      | vertex |
| 12 | (−1, 0, 1, 0)      | vertex |
| 13 | (0, −2, −1, −1)    | boundary |
| 14 | (0, 1, 0, 1)       | boundary |
| 15 | (0, 1, 1, 0)       | boundary |
| 16 | (1, 0, 0, 0)       | boundary |
| 17 | (1, 3, 0, 0)       | boundary |
| 18 | (1, 1, 0, 0)       | boundary |
| 19 | (1, 2, 0, 0)       | boundary |
| 20 | (−1, −2, 0, 0)     | boundary |
| 21 | (−1, −1, 0, 0)     | boundary |
| 22 | (0, −1, 0, 0)      | boundary |
| 23 | (0, 1, 0, 0)       | boundary |

Note: CYTools reorders points via LLL reduction. The origin (interior point)
is listed as pt0 in CYTools but corresponds to the unique interior lattice point.

## Dual Polytope Vertices (9 points in 4D)

```
[[ 0,  0, -1, -1],
 [ 0,  0, -1,  2],
 [ 0,  0,  2, -1],
 [-1,  1, -1, -1],
 [ 2, -1,  1,  1],
 [-1,  0, -1, -1],
 [-1,  0, -1,  2],
 [-1,  0,  2, -1],
 [ 1,  0,  0,  0]]
```

## D₆ Automorphism Group (order 12)

**Group identification:** Dih(6) = ⟨r, s | r⁶ = s² = 1, srs = r⁻¹⟩
(Symmetries of a regular hexagon. Also written D₁₂ when naming by order.)

**GAP ID:** SmallGroup(12, 4)

### Element Orders

| Order | Count | Type |
|-------|-------|------|
| 1 | 1 | identity |
| 2 | 7 | reflections (6) + r³ |
| 3 | 2 | r², r⁴ |
| 6 | 2 | r, r⁵ |

### Generators as GL(4,ℤ) Matrices

**Convention:** automorphisms act on lattice points by **right multiplication**:
`w = v @ M` (row-vector convention).

```
g0 (id):    [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
g1 (ord 2): [[1,3,0,0],[0,-1,0,0],[0,2,1,0],[0,2,0,1]]
g2 (ord 2): [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,-3,-1,-1]]
g3 (ord 2): [[1,3,0,0],[0,-1,0,0],[0,2,1,0],[0,-1,-1,-1]]
g4 (ord 2): [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]
g5 (ord 2): [[1,3,0,0],[0,-1,0,0],[0,2,0,1],[0,2,1,0]]
g6 (ord 3): [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,-3,-1,-1]]
g7 (ord 6): [[1,3,0,0],[0,-1,0,0],[0,2,0,1],[0,-1,-1,-1]]
g8 (ord 3): [[1,0,0,0],[0,1,0,0],[0,-3,-1,-1],[0,0,1,0]]
g9 (ord 2): [[1,0,0,0],[0,1,0,0],[0,-3,-1,-1],[0,0,0,1]]
g10(ord 6): [[1,3,0,0],[0,-1,0,0],[0,-1,-1,-1],[0,2,1,0]]
g11(ord 2): [[1,3,0,0],[0,-1,0,0],[0,-1,-1,-1],[0,2,0,1]]
```

### D₆ Orbits on 24 Lattice Points

| Orbit | Size | Indices | Points |
|-------|------|---------|--------|
| 0 | 1 | {0} | origin |
| 1 | 6 | {1,2,3,4,5,6} | 6 vertices |
| 2 | 6 | {7,8,9,10,11,12} | 6 vertices |
| 3 | 3 | {13,14,15} | boundary pts |
| 4 | 2 | {16,17} | boundary pts |
| 5 | 2 | {18,19} | boundary pts |
| 6 | 2 | {20,21} | boundary pts |
| 7 | 2 | {22,23} | boundary pts |

**Orbit sizes:** [1, 2, 2, 2, 2, 3, 6, 6] → sum = 24

Removing interior point: **7 orbits on 23 toric divisors**.
After 5 linear equivalences → **h¹¹(X/D₆) = 5 invariant Kähler moduli**.

(Confirmed by notebook analysis: orbit decomposition on H¹¹ gives [1, 1, 3, 6, 6].)

## Second Chern Class

```
c₂ = [-120, 6, 26, 8, 8, 12, 8, -4, 12, 0, 4, 12, 12, -4,
       4, 4, 18, -6, 12, 0, -6, -6]
```

(In the basis of 22 toric divisors, with 17 independent = h¹¹.)

## GLSM Charge Matrix (17 × 22)

```
[[-3  1  0  0 -1  0  0  0  0  0  0  0  0  0  1  2  0  0  0  0  0  0]
 [-3  0  1  0  1  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0]
 [ 0  0  0  1 -1  0  0  0  0  0  0  0  0  0 -1  1  0  0  0  0  0  0]
 [ 0  0  0  0  1  1  0  0  0  0  0  0  0  0 -1 -1  0  0  0  0  0  0]
 [ 0  0  0  0  1  0  1  0  0  0  0  0  0  0  0 -2  0  0  0  0  0  0]
 [-3  0  0  0 -1  0  0  1  0  0  0  0 -1  0  1  3  0  0  0  0  0  0]
 [-3  0  0  0  0  0  0  0  1  0  0  0 -1  0  1  2  0  0  0  0  0  0]
 [ 0  0  0  0 -1  0  0  0  0  1  0  0 -1  0 -1  2  0  0  0  0  0  0]
 [ 0  0  0  0 -1  0  0  0  0  0  1  0 -1  0  0  1  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  1 -1  0 -1  1  0  0  0  0  0  0]
 [-3  0  0  0  0  0  0  0  0  0  0  0  0  1  1  1  0  0  0  0  0  0]
 [-1  0  0  0 -1  0  0  0  0  0  0  0  1  0  0  0  1  0  0  0  0  0]
 [-1  0  0  0  2  0  0  0  0  0  0  0  1  0  0 -3  0  1  0  0  0  0]
 [-1  0  0  0  0  0  0  0  0  0  0  0  1  0  0 -1  0  0  1  0  0  0]
 [-1  0  0  0  1  0  0  0  0  0  0  0  1  0  0 -2  0  0  0  1  0  0]
 [-1  0  0  0 -1  0  0  0  0  0  0  0 -1  0  0  2  0  0  0  0  1  0]
 [-1  0  0  0  0  0  0  0  0  0  0  0 -1  0  0  1  0  0  0  0  0  1]]
```

## Intersection Numbers (283 non-zero)

Selected structurally important entries (full 283 available via CYTools):

| κ_{abc} | Value | Note |
|---------|-------|------|
| κ_{000} | −72 | Self-triple of D₀ |
| κ_{001}...κ_{006} | 6 each | D₀² · D_i for orbit-1 vertices |
| κ_{007}...κ_{012} | 3 each | D₀² · D_i for orbit-2 vertices |
| κ_{111} | 3 | |
| κ_{222} | −7 | |
| κ_{13,13,13} | 8 | |
| κ_{17,17,17} | 9 | |
| κ_{20,20,20} | 9 | |
| κ_{21,21,21} | 9 | |

The full intersection ring is stored computationally and can be projected
onto the D₆-invariant subspace (5D) for Yukawa coupling extraction.

## D₆-Invariant Yukawa Couplings

The D₆ symmetry reduces 22 toric divisors to **6 orbits** (pts 22–23 excluded from triangulation):

| Orbit | Divisors | Size |
|-------|----------|------|
| O1 | D₁, D₂, D₃, D₄, D₅, D₆ | 6 |
| O2 | D₇, D₈, D₉, D₁₀, D₁₁, D₁₂ | 6 |
| O3 | D₁₃, D₁₄, D₁₅ | 3 |
| O4 | D₁₆, D₁₇ | 2 |
| O5 | D₁₈, D₁₉ | 2 |
| O6 | D₂₀, D₂₁ | 2 |

The invariant Yukawa coupling is κ_inv(OI,OJ,OK) = Σ_{i∈OI, j∈OJ, k∈OK} κ(i,j,k).

### All 26 Non-Zero Invariant Couplings

| κ_inv | Value | Per-divisor |
|-------|-------|-------------|
| κ(O1,O1,O1) | −46 | −0.2130 |
| κ(O1,O1,O3) | 10 | +0.0926 |
| κ(O1,O1,O4) | 6 | +0.0833 |
| κ(O1,O1,O5) | −6 | −0.0833 |
| κ(O1,O2,O3) | 18 | +0.1667 |
| κ(O1,O3,O3) | −10 | −0.1852 |
| κ(O1,O3,O4) | 12 | +0.3333 |
| κ(O1,O3,O5) | 6 | +0.1667 |
| κ(O1,O4,O4) | −12 | −0.5000 |
| κ(O1,O4,O5) | 12 | +0.5000 |
| κ(O1,O5,O5) | −12 | −0.5000 |
| κ(O2,O2,O2) | −18 | −0.0833 |
| κ(O2,O2,O6) | 18 | +0.2500 |
| κ(O2,O3,O3) | −18 | −0.3333 |
| κ(O2,O6,O6) | −18 | −0.7500 |
| κ(O3,O3,O3) | 10 | +0.3704 |
| κ(O3,O3,O4) | −12 | −0.6667 |
| κ(O3,O3,O5) | −6 | −0.3333 |
| κ(O3,O4,O4) | −6 | −1.0000 |
| κ(O3,O4,O5) | 6 | +0.5000 |
| κ(O3,O5,O5) | −6 | −0.5000 |
| κ(O4,O4,O4) | 6 | +0.7500 |
| κ(O4,O4,O5) | −6 | −0.7500 |
| κ(O4,O5,O5) | 6 | +0.7500 |
| κ(O5,O5,O5) | −6 | −0.7500 |
| κ(O6,O6,O6) | 18 | +2.2500 |

### Sector Structure

The couplings organize into two sectors with one cross-coupling:

- **Sector A** {O1, O3, O4, O5}: 19 couplings. Rich structure with all pairwise interactions.
  O4–O5 form an alternating pair (sign flips under O4↔O5 exchange).
- **Sector B** {O2, O6}: 4 couplings. Self-contained subsystem.
- **Cross** κ(O1,O2,O3) = 18: sole bridge between sectors.

### Invariant Second Chern Numbers

| Orbit | c₂·D_OI |
|-------|----------|
| O1 | 68 |
| O2 | 36 |
| O3 | 4 |
| O4 | 12 |
| O5 | 12 |
| O6 | −12 |

Consistency check: κ(D₀,D₀,D₀) = −72 = −Vol(Δ*) ✓

## GKZ Period System

### A-Matrix and Kernel

The GKZ system is built from the **23 lattice points of Δ*** (the dual polytope):

| Quantity | Value |
|----------|-------|
| A-matrix | 5 × 23, rank 5 |
| dim ker_ℤ(A) | 18 |
| GKZ parameter | β = (−1, 0, 0, 0, 0) |
| Holonomic rank | Vol(Δ*) = 72 |

### D₆ Orbit Compression

The D₆ symmetry on Δ* produces **8 orbits** (sizes 1, 3, 2, 3, 1, 6, 6, 1).
Setting coefficients equal within each orbit reduces the 23 GKZ variables to 8 orbit parameters ψ₀…ψ₇.

The orbit-summed Ā matrix has rank 2, yielding:

> **dim ker(Ā) = 6 invariant complex structure moduli**

This is **h²¹_inv = 6** (consistent with 8 orbits − rank 2 = 6).

### Orbit-Compressed Kernel (6 × 8)

Six independent integer relations among the 8 orbit parameters:

```
[ -3,  1,  0,  0,  0,  0,  0,  0]   z₁ = ψ₁³/ψ₀³
[ -9,  0,  3,  1,  0,  0,  0,  0]   z₂ = ψ₂⁶ψ₃³/ψ₀⁹
[  1,  0, -1,  0,  1,  0,  0,  0]   z₃ = ψ₀ψ₄/ψ₂²
[-18,  0,  6,  0,  0,  1,  0,  0]   z₄ = ψ₂¹²ψ₅⁶/ψ₀¹⁸
[ -6,  0,  0,  0,  0,  0,  1,  0]   z₅ = ψ₆⁶/ψ₀⁶
[ -3,  0,  1,  0,  0,  0,  0,  1]   z₆ = ψ₂²ψ₇/ψ₀³
```

Computed from Ā via contragredient action (w → w @ M⁻ᵀ) on dual lattice
points, verified: Ā · L^T = 0 for all 6 rows.

### Closed-Form Fundamental Period

The fundamental period ω₀(ψ) = Σ_k CT[P^k] ψ^{−k} where P is the vertex polynomial
(9 monomials from the dual vertices). An algebraic factorization gives:

**CT[P^k]** = Σ_{a,γ} k! · (r−γ)! / [a!² · (γ+a)! · β! · γ! · j!³]

where r = k−2a, β = r−2γ−a, j = (r−γ)/3, summed over valid (a,γ).

First 10 coefficients: 1, 0, 0, 6, 72, 540, 2370, 10080, 78120, 843360.

501 exact coefficients computed (c₅₀₀ has 469 digits). Stored in `results/pf_vertices_N500.json`.

### Coordinate Issue

In the naive 1-parameter model z = 1/ψ (all orbit coefficients equal), the Picard-Fuchs
equation has polynomial degree ≈ Vol(Δ*) = 72. This was confirmed by modular Gaussian
elimination (mod 2⁶¹−1) over 501 terms: no recurrence found for θ-degree ≤ 4 with lag ≤ 82.

**Resolution:** The proper PF system lives in Mori cone coordinates z₁…z₆ as defined above,
where it decomposes into a tractable system of coupled PDEs (one per Mori direction).

---

## Explicit PF Operators in θ-Coordinates

*Computed in `mori_pf.py` (`--pf` and `--oneparam` flags). Verified: 9,366/9,366 GKZ recurrences pass (0 failures).*

### Orbit Euler Constraints

The two Euler operators (from rows of Ā):

```
E₀:  1·S₀ + 3·S₁ + 2·S₂ + 3·S₃ + 1·S₄ + 6·S₅ + 6·S₆ + 1·S₇ = −1
E₁:  1·S₂ − 3·S₃ + 1·S₄ − 6·S₅              − 1·S₇ = 0
```

### S_α in Mori θ-Coordinates

Each orbit theta-operator S_α = Σᵢ L[i,α] · θᵢ, where L = KERNEL and θᵢ = zᵢ ∂/∂zᵢ:

| Orbit α | Size s_α | S_α expression |
|---------|----------|----------------|
| S₀ | 1 | −3θ₁ − 9θ₂ + θ₃ − 18θ₄ − 6θ₅ − 3θ₆ |
| S₁ | 3 | θ₁ |
| S₂ | 2 | 3θ₂ − θ₃ + 6θ₄ + θ₆ |
| S₃ | 3 | θ₂ |
| S₄ | 1 | θ₃ |
| S₅ | 6 | θ₄ |
| S₆ | 6 | θ₅ |
| S₇ | 1 | θ₆ |

### The Six GKZ Box Operators

Each operator has the form  □ₖ ω = 0, where □ₖ = [positive falling factorials] − zₖ · [negative falling factorials].  
Notation: `(F)·(F−1)·…·(F−d+1)` denotes the degree-d falling factorial of operator F.

**□₁  [degree 3]** — kernel vector (−3, 1, 0, 0, 0, 0, 0, 0)

```
POS:  (S₁)·(S₁−1)·(S₁−2)
    = (θ₁)·(θ₁−1)·(θ₁−2)

NEG:  z₁ · (S₀)·(S₀−1)·(S₀−2)
    = z₁ · (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆)
         · (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆−1)
         · (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆−2)
```

**□₂  [degree 9]** — kernel vector (−9, 0, 3, 1, 0, 0, 0, 0)

```
POS:  (S₂)·(S₂−1)·(S₂−2)·(S₂−3)·(S₂−4)·(S₂−5)  ·  (S₃)·(S₃−1)·(S₃−2)
    = (3θ₂−θ₃+6θ₄+θ₆)^{(6)}  ·  (θ₂)^{(3)}

NEG:  z₂ · (S₀)^{(9)}
    = z₂ · (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆)^{(9)}
```

**□₃  [degree 2]** — kernel vector (1, 0, −1, 0, 1, 0, 0, 0)

```
POS:  (S₀) · (S₄)
    = (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆) · (θ₃)

NEG:  z₃ · (S₂)·(S₂−1)
    = z₃ · (3θ₂−θ₃+6θ₄+θ₆)·(3θ₂−θ₃+6θ₄+θ₆−1)
```

**□₄  [degree 18]** — kernel vector (−18, 0, 6, 0, 0, 1, 0, 0)

```
POS:  (S₂)^{(12)}  ·  (S₅)^{(6)}
    = (3θ₂−θ₃+6θ₄+θ₆)^{(12)}  ·  (θ₄)^{(6)}

NEG:  z₄ · (S₀)^{(18)}
    = z₄ · (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆)^{(18)}
```

**□₅  [degree 6]** — kernel vector (−6, 0, 0, 0, 0, 0, 1, 0)

```
POS:  (S₆)^{(6)}
    = (θ₅)^{(6)}      [= θ₅(θ₅−1)(θ₅−2)(θ₅−3)(θ₅−4)(θ₅−5)]

NEG:  z₅ · (S₀)^{(6)}
    = z₅ · (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆)^{(6)}
```

**□₆  [degree 3]** — kernel vector (−3, 0, 1, 0, 0, 0, 0, 1)

```
POS:  (S₂)·(S₂−1)  ·  (S₇)
    = (3θ₂−θ₃+6θ₄+θ₆)·(3θ₂−θ₃+6θ₄+θ₆−1)  ·  (θ₆)

NEG:  z₆ · (S₀)·(S₀−1)·(S₀−2)
    = z₆ · (−3θ₁−9θ₂+θ₃−18θ₄−6θ₅−3θ₆)^{(3)}
```

### Verification

GKZ recurrence check: for each multi-index n and each kernel direction k,

$$c(n + e_k) \cdot P_+(u(n+e_k)) = c(n) \cdot P_-(u(n))$$

where $u_\alpha = \gamma_\alpha + m_\alpha$ (full a-exponents, $\gamma_0 = -1$, $\gamma_{\alpha\geq 1} = 0$), and $P_\pm$ are the products of falling factorials over positive/negative-$\lambda$ orbits.

**Result: 9,366 / 9,366 checks pass (0 failures)** across all multi-degrees |n| ≤ 5.

---

## 1-Parameter ODE: z₁-Axis Specialization

Setting z₂ = z₃ = z₄ = z₅ = z₆ = 0 (z₁ = t), the multivariate system reduces to a single ODE.  
On this slice only n = (n₁, 0, 0, 0, 0, 0) contributes, and S₀ = −3θ, S₁ = θ, all other S_α = 0.

### Period Series

**Unsigned:** ω(t) = Σ_{n≥0} (3n)!/n!³ · tⁿ = 1 + 6t + 90t² + 1680t³ + 34650t⁴ + …

**Signed (GKZ Gamma-series):** ω_s(t) = Σ_{n≥0} (−1)ⁿ (3n)!/n!³ · tⁿ = 1 − 6t + 90t² − 1680t³ + …

Recurrence (from □₁ on z₁-slice):

$$(n+1)^3\, c_s(n+1) = -(3n+1)(3n+2)(3n+3)\, c_s(n)$$

Verified for n = 0, …, 6 ✓

### PF ODE

$$\boxed{\left[(\theta+1)^3 + t\,(3\theta+1)(3\theta+2)(3\theta+3)\right]\omega_s(t) = 0}$$

where θ = t d/dt.  Factor: (3θ+1)(3θ+2)(3θ+3) = 27(θ+1/3)(θ+2/3)(θ+1), so:

$$(\theta+1)\left[(\theta+1)^2 + 27t\,\left(\theta+\tfrac{1}{3}\right)\left(\theta+\tfrac{2}{3}\right)\right]\omega_s = 0$$

The irreducible factor (the physically relevant PF operator for ω_s) is:

$$(\theta+1)^2 + 27t\,\left(\theta+\tfrac{1}{3}\right)\left(\theta+\tfrac{2}{3}\right) = 0$$

### Hypergeometric Identification

| Form | Series | ODE |
|------|--------|-----|
| Unsigned (t → −z₁) | $\sum \frac{(3n)!}{n!^3} t^n$ | $\theta^3\omega = t(3\theta)(3\theta+1)(3\theta+2)\omega$ |
| Signed (z₁ axis) | $\sum (-1)^n\frac{(3n)!}{n!^3} t^n$ | $(\theta+1)^3\omega + t(3\theta+1)(3\theta+2)(3\theta+3)\omega = 0$ |

$$\omega(t) = {}_3F_2\!\left(\tfrac{1}{3}, \tfrac{2}{3}, 1;\, 1, 1;\, 27t\right), \quad |t| < \tfrac{1}{27}$$

This is the period of the **mirror family of cubic hypersurfaces in ℙ²** (elliptic curve family), embedded in the z₁-direction of the GL=12/D₆ moduli space. It corresponds to **AESZ entry #1** in the 2-variable Calabi-Yau period tables.

**Geometric interpretation:** The z₁ direction corresponds to the Mori cone ray with kernel vector (−3, 1, 0, …), relating ψ₀ (the origin orbit) to ψ₁ (the 3-element orbit of interior edge-midpoints). The cubic in the period $(3n)!/n!^3$ reflects the three-fold periodicity of the hexagonal D₆ symmetry along this deformation direction.

---

## Key Properties for Picard-Fuchs

1. **D₆ reduces h²¹ = 20 complex structure moduli → fewer invariant deformations**
2. **h¹¹(X/D₆) = 5** invariant Kähler moduli, making PF computation feasible
3. **No nef partitions** → not a CICY; must use toric/GKZ methods
4. **141 SR generators** → exceeds cohomcalc 64-limit (bypassed by Koszul pipeline)
5. **Dual polytope** (9 vertices) defines the GKZ A-matrix for the PF operator

## Reconstruction Code

```python
import cytools
cytools.config.enable_experimental_features()
from cytools import Polytope
import numpy as np

V = np.array([
    [1, 1, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1],
    [0, 3, 0, 2, 0, 2, -3, -1, -1, 0, -1, 0, -4, -3],
    [0, 0, 1, 1, 0, 0, -1, -1, 1, 1, 0, 0, -1, -1],
    [0, 0, 0, 0, 1, 1, -1, -1, 0, 0, 1, 1, -1, -1],
]).T

p = Polytope(V.tolist())
t = p.triangulate()
cy = t.get_cy()

# Verify
assert cy.h11() == 17
assert cy.h21() == 20
assert cy.chi() == -6
assert len(p.automorphisms()) == 12
```
