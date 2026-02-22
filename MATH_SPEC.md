# MATH_SPEC.md — Gold Standard Reference

> **Purpose**: Canonical reference for every formula, sign convention, index convention,
> and CYTools API contract used in this project. Check this BEFORE writing any computation.
> Every bug we've hit is documented here so we don't repeat it.

---

## 1. Geometry Setup

### 1.1 The Objects

| Symbol | Meaning |
|--------|---------|
| $\Delta$ | Reflexive polytope in $N \cong \mathbb{Z}^4$ |
| $\Delta^\circ$ | Dual (polar) polytope in $M \cong \mathbb{Z}^4$ |
| $V$ | Ambient toric 4-fold (from fan over faces of $\Delta$) |
| $X \subset V$ | Calabi-Yau 3-fold hypersurface in class $[-K_V]$ |
| $v_\rho \in N$ | Ray (1-cone generator) of the fan, one per toric coord |
| $D_\rho$ | Toric (prime) divisor associated to ray $v_\rho$ |

### 1.2 Dimensions and Counts

| Quantity | Formula | Polytope 40 value |
|----------|---------|-------------------|
| Ambient complex dimension | $\dim V = 4$ | 4 |
| CY complex dimension | $\dim X = 3$ | 3 |
| Lattice rank | $\text{rk}(N) = \text{rk}(M) = 4$ | 4 |
| Number of toric coordinates | $n_\text{toric} = \text{cols}(\text{GLSM})$ | 20 |
| Number of fan rays | $n_\text{rays} = n_\text{toric} - 1$ | 19 |
| $h^{1,1}(X)$ | $= \text{rows}(\text{GLSM})$ | 15 |

---

## 2. Index Conventions

### 2.1 Polytope Points and Fan Rays

**CRITICAL — this is where Bug #4 lived.**

```
p.points() returns shape (n_toric, 4)

  pts[0]  = (0,0,0,0)   ← THE ORIGIN (not a fan ray!)
  pts[1]  = v_1          ← first fan ray
  pts[2]  = v_2
  ...
  pts[19] = v_19         ← last fan ray
```

**Rule**: Fan rays are `pts[1], ..., pts[n_toric-1]`. The origin at `pts[0]` is the
apex of the fan, NOT a ray. There are `n_toric - 1` rays, not `n_toric`.

**Rule**: Toric divisor $D_\rho$ corresponds to `pts[ρ]` for $\rho = 0, 1, \ldots, 19$.
But $D_0$ (the origin "divisor") is not a standard toric divisor in the fan.
CYTools indexes GLSM columns 0..19 with column $\rho$ corresponding to `pts[ρ]`.

### 2.2 Divisor Basis

```python
div_basis = [int(x) for x in cyobj.divisor_basis()]
# Returns TORIC INDICES of the chosen basis divisors
# Polytope 40: [1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]
```

| Basis index $a$ | Toric index `div_basis[a]` | Notation |
|:---:|:---:|:---:|
| 0 | 1 | $e_0 = D_1$ |
| 1 | 3 | $e_1 = D_3$ |
| 2 | 4 | $e_2 = D_4$ |
| 3 | 5 | $e_3 = D_5$ |
| 4 | 7 | $e_4 = D_7$ |
| ... | ... | ... |
| 14 | 18 | $e_{14} = D_{18}$ |

**Non-basis toric indices** (Polytope 40): $\{0, 2, 6, 10, 19\}$

- Index 0 = origin
- Indices 2, 6, 10, 19 = non-basis rays (their divisor classes are determined by linear relations)

### 2.3 GLSM Charge Matrix

```python
glsm = cyobj.glsm_charge_matrix()  # shape (h11, n_toric) = (15, 20)
```

**Verified property**: `glsm[:, div_basis] == I_{h11}` (identity matrix).
This means the GLSM charges of basis divisors are just standard unit vectors.

### 2.4 Intersection Numbers

```python
# TORIC-indexed (keys are toric indices 0..19):
intnums_toric = dict(cyobj.intersection_numbers())

# BASIS-indexed (keys are basis indices 0..14):
intnums_basis = dict(cyobj.intersection_numbers(in_basis=True))
```

**⚠️ RULE**: Always use `in_basis=True` and work in basis coordinates.
Mixing toric-indexed intersection numbers with basis-indexed divisor vectors
is the #1 source of silent errors.

### 2.5 Second Chern Class

```python
# TORIC-indexed (length may be < n_toric, padded with zeros):
c2_toric = cyobj.second_chern_class()

# BASIS-indexed (length h11):
c2_basis = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)
```

**⚠️ RULE**: Always use `in_basis=True`. Pair with basis-indexed $D$.

---

## 3. Core Formulas

### 3.1 Hirzebruch-Riemann-Roch on CY3

$$\chi(\mathcal{O}_X(D)) = \frac{D^3}{6} + \frac{c_2(X) \cdot D}{12}$$

where:

$$D^3 = \sum_{i,j,k} D_i D_j D_k \, \kappa_{ijk}, \qquad
c_2 \cdot D = \sum_i D_i \, (c_2)_i$$

with $\kappa_{ijk}$ and $(c_2)_i$ **both in basis coordinates**.

**Implementation**:
```python
D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
c2D = sum(D[k] * c2_basis[k] for k in range(h11))
chi = D3/6 + c2D/12
```

**Sanity check**: $\chi$ must be an integer. If it's not, something is wrong.

### 3.2 Euler Characteristic and Generations

$$\chi(X) = 2(h^{1,1} - h^{2,1})$$

In the **standard embedding** ($V = TX$), the number of generations is:

$$N_\text{gen} = \frac{|\chi(X)|}{2} = |h^{1,1} - h^{2,1}|$$

**⚠️ WARNING**: This is NOT the same as $h^0(L) = 3$ for a line bundle $L$.
These are two completely different statements:
1. $N_\text{gen} = |\chi|/2$ — topological, always true for standard embedding
2. $h^0(L) = 3$ — analytical, requires proving vanishing of higher cohomology

### 3.3 Divisor Topology (del Pezzo classification)

For a single basis divisor $D_i$:

$$\chi(\mathcal{O}_{D_i}) = \kappa_{iii} + (c_2)_i$$

| $\chi(\mathcal{O}_D)$ | $\kappa_{iii}$ | Surface type |
|:---:|:---:|:---|
| 3 | any | dP$_0$ ($\mathbb{P}^2$) or smooth rational |
| 4 | any | dP$_1$ (blow-up of $\mathbb{P}^2$ at 1 point) |
| ... | ... | ... |
| $3 + n$ | any | dP$_n$ (for $\kappa_{iii} > 0$, rigid if $n \leq 8$) |
| 24 | 0 | K3-like |

### 3.4 Swiss Cheese Volume

At the tip of the stretched Kähler cone:

$$\mathcal{V} = \text{cyobj.compute\_cy\_volume}(t), \qquad
\tau_i = \text{cyobj.compute\_divisor\_volumes}(t)[i]$$

Swiss cheese structure: $\tau_\text{small} / \mathcal{V}^{2/3} \ll 1$.

---

## 4. Cohomology Computation

### 4.1 Koszul Exact Sequence

The CY hypersurface $X$ sits in the linear system $|{-K_V}|$. The Koszul (restriction) sequence is:

$$0 \to \mathcal{O}_V(D + K_V) \to \mathcal{O}_V(D) \to \mathcal{O}_X(D) \to 0$$

**Sign convention**: $K_V = -\sum_\rho D_\rho$ (canonical = negative sum of toric divisors).
So $D + K_V$ in toric coordinates means $d_\rho \mapsto d_\rho - 1$ for each ray $\rho$.

The long exact sequence in cohomology gives:

$$h^0(X, D) = h^0(V, D) - h^0(V, D + K_V) + \dim\ker\big(H^1(V, D+K_V) \to H^1(V, D)\big)$$

**Lower bound** (exact when $h^1 = 0$):

$$h^0(X, D) \geq h^0(V, D) - h^0(V, D + K_V)$$

### 4.2 Lattice Point Counting (Toric $h^0$)

On the ambient toric variety:

$$h^0(V, \mathcal{O}(D)) = \#\{m \in M \cap P_D\}$$

where the polytope is:

$$P_D = \{m \in M_\mathbb{R} : \langle m, v_\rho \rangle \geq -d_\rho \;\;\forall\;\text{rays}\;\rho\}$$

**⚠️ CRITICAL INDEXING**: The sum is over **rays** $\rho \in \{1, \ldots, 19\}$ (NOT index 0 = origin).
Use `pts[ρ]` for $v_\rho$ and `D_toric[ρ]` for $d_\rho$.

**Implementation** (correct):
```python
ray_indices = list(range(1, n_toric))  # [1, ..., 19]
# For each ray ρ: constraint is ⟨m, pts[ρ]⟩ ≥ -D_toric[ρ]
```

**Sanity checks**:
- $h^0(V, \mathcal{O}(0)) = 1$ (only $m = 0$ satisfies $\langle m, v_\rho \rangle \geq 0$ for a complete fan)
- $h^0(V, \mathcal{O}(-K_V)) = \#(\text{lattice points of }\Delta^\circ)$ (dual polytope)

### 4.3 Toric $h^1$ via Čech Cohomology

$$h^1(V, \mathcal{O}(D)) = \sum_{m \in M} \max\!\big(0,\; \#\text{components}(V(m)) - 1\big)$$

where:

$$V(m) = \{\rho \in \text{rays} : \langle m, v_\rho \rangle < -d_\rho\}$$

and "components" are connected components of $V(m)$ in the **fan adjacency graph**
(two rays are adjacent if they share a maximal cone).

The sum is finite — only finitely many $m$ give $V(m) \neq \emptyset$.

### 4.4 Basis ↔ Toric Conversion

To convert a divisor $D$ from basis coordinates to toric coordinates for lattice point counting:

```python
def basis_to_toric(D_basis):
    D_toric = np.zeros(n_toric, dtype=int)
    for a in range(h11):
        D_toric[div_basis[a]] = D_basis[a]
    # Non-basis entries (indices 0, 2, 6, 10, 19) remain 0
    return D_toric
```

This works because `glsm[:, div_basis] = I`, so setting the basis entries and zeroing
the rest gives a valid representative of the linear equivalence class. The lattice
point count is invariant under linear equivalence.

---

## 5. Vanishing Theorems

### 5.1 Kodaira Vanishing

**Statement**: If $L$ is an ample line bundle on a smooth projective variety $X$, then:
$$H^i(X, \omega_X \otimes L) = 0 \quad \text{for } i > 0$$

On a CY3 ($\omega_X \cong \mathcal{O}_X$): $L$ ample $\Rightarrow$ $H^i(X, L) = 0$ for $i > 0$ $\Rightarrow$ $h^0(L) = \chi(L)$.

**⚠️ WARNING**: Requires $L$ ample on the CY $X$, not just on the ambient $V$.
Ampleness on $X$ ⊂ nef on $V$ (but nef on $V$ does not imply ample on $X$).

### 5.2 Kawamata-Viehweg Vanishing

**Statement**: If $D$ is nef and big, then $H^i(X, \mathcal{O}(K_X + D)) = 0$ for $i > 0$.

On CY3: $D$ nef + big $\Rightarrow$ $h^i(D) = 0$ for $i > 0$ $\Rightarrow$ $h^0 = \chi$.

**Nef test**: $D$ is nef iff $D \cdot C \geq 0$ for all effective curves $C$.
Operationally: check against all Mori cone generators.

**Big test**: $D$ is big iff $D^3 > 0$.

### 5.3 Serre Duality on CY3

$$h^i(X, L) = h^{3-i}(X, L^{-1})$$

In particular: $h^3(L) = h^0(L^{-1})$ and $h^2(L) = h^1(L^{-1})$.

For effective $D$ (positive coefficients in Kähler cone direction):
$h^3(\mathcal{O}(D)) = h^0(\mathcal{O}(-D)) = 0$ since $-D$ is not effective.

So HRR simplifies to: $\chi = h^0 - h^1 + h^2$.

---

## 6. Cone Pairings

### 6.1 Mori Cone Pairing (Nef Test)

**⚠️ This is where Bug #3 lived.**

Mori cone generators from CYTools are in **toric coordinates** (20-dimensional).

To pair a **basis-indexed** divisor $D$ with a **toric-indexed** Mori generator $C$:

$$D \cdot C = \sum_{a=0}^{h^{1,1}-1} D_a \cdot C[\text{div\_basis}[a]]$$

**Correct implementation**:
```python
mori_rays = cyobj.toric_mori_cone().rays()  # shape (n_gens, 20)
for C in mori_rays:
    pairing = sum(D_basis[a] * C[div_basis[a]] for a in range(h11))
```

**WRONG (Bug #3)**:
```python
# DO NOT DO THIS:
pairing = sum(D_basis[a] * C[a] for a in range(h11))  # WRONG!
# C is 20-dim, D is 15-dim — this truncates C to the wrong 15 entries
```

**Sanity check**: The tip of the stretched Kähler cone must pair non-negatively with all Mori generators:
```python
t_tip = cyobj.toric_kahler_cone().tip_of_stretched_cone(1)
# t_tip is h11-dimensional (basis coords)
# Must get: sum(t_tip[a] * C[div_basis[a]]) >= 0 for all Mori gens C
```

---

## 7. CYTools API Quick Reference

### 7.1 Always Use `in_basis=True`

| Method | Without flag | With `in_basis=True` |
|--------|-------------|---------------------|
| `intersection_numbers()` | Keys = toric indices | **Keys = basis indices** ← USE THIS |
| `second_chern_class()` | Toric-indexed array | **Basis-indexed array** ← USE THIS |

### 7.2 Key API Contracts

```python
# Setup
polys = list(cy.fetch_polytopes(h11=H, h21=K, lattice='N', limit=N))
p = polys[IDX]
tri = p.triangulate()
cyobj = tri.get_cy()

# Hodge numbers
h11 = cyobj.h11()                          # int
h21 = cyobj.h21()                          # int (if available)

# Divisor basis (TORIC indices)
div_basis = [int(x) for x in cyobj.divisor_basis()]

# Intersection numbers (BASIS-indexed)
intnums = dict(cyobj.intersection_numbers(in_basis=True))
# Keys: tuples (i,j,k) with 0 ≤ i ≤ j ≤ k < h11

# Second Chern class (BASIS-indexed)
c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

# GLSM charge matrix
glsm = np.array(cyobj.glsm_charge_matrix(), dtype=int)  # (h11, n_toric)

# Polytope points (N lattice, origin at index 0)
pts = np.array(p.points(), dtype=int)      # (n_toric, 4)
assert np.all(pts[0] == 0), "Origin must be at index 0"

# Cones
mori_gens = cyobj.toric_mori_cone().rays()       # (n_gens, n_toric) — TORIC coords
kahler_gens = cyobj.toric_kahler_cone().rays()    # (n_gens, n_toric) — TORIC coords
t_tip = cyobj.toric_kahler_cone().tip_of_stretched_cone(1)  # (h11,) — BASIS coords

# Volumes
vol = cyobj.compute_cy_volume(t_tip)              # float
tau = cyobj.compute_divisor_volumes(t_tip)         # (h11,) — BASIS-indexed

# Stanley-Reisner ideal
sr = tri.sr_ideal()       # list of tuples of coordinate indices

# Automorphisms
auts = p.automorphisms()   # list of 4×4 integer matrices
```

---

## 8. Bug Registry

Every bug encountered, so we never repeat them.

### Bug 1: Fabricated `proven_h0_3 = True`
- **Where**: pipeline_40_152.py
- **What**: Hardcoded `True` with comment "We KNOW these exist" — never computed.
- **Impact**: Pipeline score inflated 19/20 → 20/20.
- **Lesson**: Never hardcode a claim. Compute it or mark it unverified.

### Bug 2: Intersection number coordinate mismatch
- **Where**: pipeline_40_152.py, early dragon_slayer scripts
- **What**: Used toric-indexed `intersection_numbers()` but built $D$ in basis coords (or vice versa).
- **Lesson**: **Always** use `in_basis=True`. Never mix coordinate systems.

### Bug 3: Mori cone pairing dimension mismatch
- **Where**: dragon_slayer_40c.py
- **What**: Paired 15-dim basis $D$ with 20-dim toric Mori generator by truncation.
- **Lesson**: Use the explicit mapping: $D \cdot C = \sum_a D_a \cdot C[\text{div\_basis}[a]]$.

### Bug 4: Off-by-one in lattice point counting
- **Where**: dragon_slayer_40g.py
- **What**: Removed origin from `pts` to get `rays`, but then paired `rays[k]` with `D_toric[k]` — off by one since `rays[k] = pts[k+1]` but `D_toric[k]` ≠ `D_toric[k+1]`.
- **Fix**: Iterate over explicit `ray_indices = [1,...,19]` and always use `pts[ρ]` with `D_toric[ρ]`.
- **Lesson**: Never re-index. Keep the canonical CYTools indices throughout.

### Bug 5: cohomCalg SR limit
- **Where**: dragon_slayer_40e.py, 40f.py
- **What**: Polytope 40 has 97 SR generators; cohomCalg hard limit is 64.
- **Lesson**: Check `len(tri.sr_ideal())` before attempting cohomCalg.

### Bug 6: Conflating $|\chi|/2 = 3$ with $h^0(L) = 3$
- **Where**: pipeline_40_152.py, original analysis
- **What**: Claimed "3 generations" meant a specific bundle has 3 sections. In fact, $N_\text{gen} = |\chi|/2$ is a topological statement (standard embedding), while $h^0(L) = 3$ is an analytical claim about a specific line bundle.
- **Result**: All χ=3 line bundles on Polytope 40 have $h^0 \leq 2$.
- **Lesson**: These are different claims. Always specify which one you mean.

### Bug 7: GLSM linear relations ≠ character translations
- **Where**: dragon_slayer_40i.py, Test 1
- **What**: Used `cyobj.glsm_linear_relations()` (5 rows, shape 5×20) to generate "equivalent" divisor representatives, then checked lattice-point count invariance. Counts varied wildly (2, 39, 225).
- **Root cause**: The GLSM kernel has dim = $n_\text{toric} - h^{1,1} = 20 - 15 = 5$, but only 4 of the 5 directions are character translations ($\dim M = 4$). The 5th direction involves the origin coordinate ($v_0 = 0$). Specifically:
  - `linrel[0]` has `origin_component = 1` → **NOT** a character translation
  - `linrel[1..4]` have `origin_component = 0` → ARE character translations with integer $m$ vectors
- **Why it matters**: Character translations shift $d_\rho \to d_\rho + \langle m, v_\rho \rangle$, translating the polyhedron $P_D \to P_D + m$ (preserves lattice-point count). A GLSM shift involving the origin changes the *actual* toric divisor class on $V$, so the lattice-point count *should* differ.
- **Impact**: Test 1 was a **false alarm**. The Koszul $h^0 = 2$ result is correct. All 8 pure character translations tested give $h^0 = 2$.
- **Lesson**: For lattice-point testing, ONLY use character translations (inner products $\langle m, v_\rho \rangle$ for $m \in M$). Filter GLSM linrels by `origin_component == 0` before use, or compute character translations directly as $\text{pts}[1:]^T \cdot m$ for $m \in \mathbb{Z}^4$.

---

## 9. Proven Results (Polytope 40: h11=15, h21=18)

### 9.1 Confirmed True
| Claim | Method | Script |
|-------|--------|--------|
| $h^{1,1} = 15, h^{2,1} = 18, \chi = -6$ | CYTools + HRR | dragon_slayer_40.py |
| $N_\text{gen} = 3$ (standard embedding) | $|\chi|/2$ | dragon_slayer_40.py |
| 11 rigid del Pezzo divisors | $\chi(\mathcal{O}_D)$ classification | dragon_slayer_40.py |
| Swiss cheese: $\tau_{D_{17}} = 4.0$, $\mathcal{V} = 17506$ | Volume computation | dragon_slayer_40.py |
| 119 line bundles with $\chi = 3$ | Exhaustive HRR search | dragon_slayer_40b.py, 40h.py |
| $\mathbb{Z}_2$ polytope symmetry | Automorphism computation | dragon_slayer_40.py |
| $\max h^0(X, \mathcal{O}(D)) = 2$ for all $\chi=3$ bundles | Koszul + lattice points | dragon_slayer_40h.py |
| $h^0 = 2$ invariant under character translations (8/8) | Character translation test | dragon_slayer_40i.py |
| Koszul method matches quintic: $h^0(\text{quintic}, \mathcal{O}(n))$ for $n = -3..7$ | Independent cross-check | dragon_slayer_40i.py |

### 9.2 Confirmed False
| Claim | Disproof | Script |
|-------|----------|--------|
| $D = e_3 + e_4 + e_{10}$ has $D^3 = 1$, $\chi = 3$ | Actual: $D^3 = 14$, $\chi = 2.667$ | dragon_slayer_40b.py |
| `proven_h0_3 = True` | No line bundle has $h^0 = 3$; max is 2 | dragon_slayer_40h.py |
| Any $\chi = 3$ bundle is nef | 0 nef bundles among 246; closest Mori pairing = −2 | dragon_slayer_40d.py |

### 9.3 Open / Unresolved
| Question | Status |
|----------|--------|
| Does any higher-rank vector bundle yield $h^1(V) = 3$? | Not investigated |
| Are there other $\chi = -6$ polytopes with $h^0 = 3$ line bundles? | Not investigated |
| K3/elliptic fibration structure of Polytope 40? | Not investigated |

---

## 10. Version History

| Date | Change |
|------|--------|
| 2026-02-22 | Initial spec created from audit of dragon_slayer_40{a-h}.py |
| 2026-02-22 | Bug #7 added (GLSM linrels vs character translations). Verified h⁰=2 via char translations (8/8 pass). Quintic cross-check confirms Koszul method. |
