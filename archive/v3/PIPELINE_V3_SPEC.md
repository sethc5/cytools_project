# Pipeline v3 Specification

> **Goal**: Find the Standard Model vacuum in the Kreuzer-Skarke landscape.
>
> v2 asked: *"Does this polytope have clean bundles?"* — binary, at massive scale.
> v3 asks: *"How close is this geometry to the Standard Model?"* — continuous score, physics-driven.

---

## Architecture: 5 Tiers

```
T0   (0.05s)  Geometry fingerprint       kills ~85%       [from v2, refined]
T05  (0.1s)   Intersection algebra        kills ~50%       [NEW — the big addition]
T1   (0.5s)   Bundle screening            kills ~70%       [v2 T025+T1 merged]
T2   (3-30s)  Deep physics                scores top ~1K   [restructured + Yukawa/LVS]
T3   (30s+)   Full phenomenology          top ~50          [NEW]
```

Each tier writes to `cy_landscape_v3.db` immediately. No data is lost on crash.

---

## T0: Geometry Fingerprint (~0.05s/poly)

**Same as v2** with one fix: compute `chi = 2*(h11 - h21)` from actual Hodge
numbers instead of hardcoding `-6`.

### Computes
- `h11`, `h21`, `chi`
- `h11_eff` (effective Picard rank = len(divisor_basis()))
- `gap = h11 - h11_eff`
- `favorable` (h11_eff == h11)
- `aut_order` (polytope automorphism group order)

### Filters (hard kills)
- `h11_eff > EFF_MAX (20)` → skip (too large for bundle search)
- `gap < GAP_MIN (2) AND h11_eff >= 15` → skip (low gap + high eff = unlikely clean)
- `aut_order > AUT_MAX (4)` → skip (expensive, rarely yields clean bundles)
- `|chi| != 6` → skip (need 3-generation: |χ/2| = 3)

### CYTools API used
```python
p = Polytope(vertices)
tri = p.triangulate()
cy = tri.get_cy()
cy.h11(), cy.h21()
cy.divisor_basis()
len(p.automorphisms())
```

---

## T05: Intersection Algebra (~0.1s/poly) ← NEW

This is the key v3 innovation. Extracts physics-relevant structure from data
that T0 already computes (intersection numbers, c₂) at near-zero marginal cost.

### Computes

#### 1. Yukawa Rank
The Yukawa coupling tensor is Y_{abc} ∝ κ_{ijk} L^i_a L^j_b L^k_c where
κ_{ijk} are the triple intersection numbers and L is the line bundle.

At T05 we don't have the bundle yet, but we can characterize the "Yukawa
capacity" of the geometry: how many nonzero κ_{ijk} exist in the divisor basis.

- `yukawa_rank` = number of nonzero κ_{ijk} entries (basis-indexed)
- `yukawa_density` = yukawa_rank / total possible triples
- A viable SM needs rank ≥ 3 (3 generations × mass hierarchy)
- **Filter**: reject if yukawa_rank < h11_eff / 2 (too sparse)

#### 2. Tadpole Bound
The D3-brane tadpole: N_flux + N_D3 = χ(X)/24.
- `chi_over_24` = chi / 24.0
- Extreme values (|χ/24| > 50) make flux tuning exponentially harder
- Stored for scoring, not hard-filtered

#### 3. c₂ Positivity (DRS Conjecture)
For each basis divisor D_a, the DRS conjecture requires c₂ · D_a ≥ 0
for all effective divisors.
- `c2_all_positive` = 1 if c₂[a] ≥ 0 for all basis divisors, else 0
- Violations are flagged but not filtered (they're rare and interesting)

#### 4. Volume Form Structure
From κ_{ijk} alone (no Kähler moduli), characterize the cubic volume form
V = (1/6) κ_{ijk} t^i t^j t^k.

Evaluate the Hessian H_ij = ∂²V/∂t^i∂t^j at the Kähler cone tip.
The eigenvalue pattern reveals:
- Swiss cheese: signature (1, h11-1) — one large, rest small
- Fibered: block-diagonal structure
- Generic: no special structure

- `kappa_signature` = "(p, q)" eigenvalue signature of the Hessian
- `volume_form_type` = "swiss_cheese" | "fibered" | "generic"

### CYTools API used
```python
cy.intersection_numbers(in_basis=True)   # κ_{ijk} dict
cy.second_chern_class(in_basis=True)     # c₂ vector
cy.toric_kahler_cone().tip_of_stretched_cone(1.0)  # tip for Hessian eval
```

---

## T1: Bundle Screening (~0.5s/poly)

Merges v2's T025 (early-exit h⁰ check) and the bundle-finding part of v2's T1
into a single pass with adaptive depth.

### Computes
1. Find all χ = ±3 bundles via vectorized search (same as v2)
2. For each bundle, compute h⁰(X, D) via Koszul sequence
   - Early exit at `min_h0 = H0_MIN (5)` as screening signal
3. **New**: For bundles with h⁰ ≥ 5, immediately check h³(V) = h⁰(V*)
   - If h³ ≠ 0, it's not clean → skip (saves wasted T2 time)
4. Adaptive depth: once first clean hit found, continue counting within
   a 2-second time budget to estimate n_clean without full census

### Outputs
- `n_chi3` — total χ = ±3 bundles found
- `max_h0` — maximum h⁰ seen
- `h0_ge3` — bundles with h⁰ ≥ 3
- `n_clean_est` — estimated clean bundles (from time-budgeted probe)
- `first_clean_at` — bundle index of first clean hit

### Filter
- Skip if `max_h0 < H0_MIN (5)` (screening signal, not true h⁰)

### CYTools API used
Same as v2: lattice point counting via precomputed vertex data.
No new CYTools calls — pure cy_compute.py math.

---

## T2: Deep Physics (3-30s/poly)

Only runs on polytopes that passed T1. This is where v3 adds real
physics beyond bundle counting.

### Computes

#### From v2 (retained)
- Full bundle census: all χ = ±3, full h⁰ + h³ computation
- `n_clean`, `max_h0`, `h0_ge3`, `h0_distribution`
- Divisor classification: del Pezzo, K3, rigid
- `n_dp`, `dp_types`, `n_k3_div`, `n_rigid`
- Fibration count: K3 + elliptic from dual polytope
- `n_k3_fib`, `n_ell_fib`

#### NEW: LVS Compatibility Score
Large Volume Scenario needs at least one "small" 4-cycle with
τ_small / V^{2/3} ≪ 1.

```python
kc = cy.toric_kahler_cone()
for ray in kc.extremal_rays():
    dvols = cy.compute_divisor_volumes(ray * scale)
    vol = cy.compute_cy_volume(ray * scale)
    for i, tau in enumerate(dvols):
        ratio = tau / vol**(2/3)
        # Track best (smallest) ratio
```

- `lvs_score` — best τ/V^{2/3} ratio found (smaller = better)
- `best_small_div` — index of the best small divisor
- `volume_hierarchy` — V_big / V_small ratio

#### NEW: Yukawa Texture Analysis
For each clean bundle V with divisor class D:
- Compute Y_{abc} = κ_{ijk} D^i_a D^j_b D^k_c
- Only meaningful as a matrix when h⁰ = 3 (three generations)

Score based on:
- `yukawa_texture_rank` — rank of the 3×3 Yukawa matrix
- `yukawa_hierarchy` — max/min nonzero eigenvalue ratio
- `yukawa_zeros` — number of texture zeros (constrains mass matrices)
- A realistic SM Yukawa has rank 3 with hierarchy ~10⁵

#### NEW: Mori Cone / del Pezzo Contractions
```python
mc = cy.toric_mori_cone()
mori_rays = mc.rays()
```
Check if any Mori cone generator gives a del Pezzo contraction
(curve that shrinks a dP surface → instanton divisor for LVS).
- `n_mori_rays` — number of Mori cone generators
- `n_dp_contract` — del Pezzo contracting curves

#### Gauge Algebra from Fibrations
Same as v2 T2: Kodaira classification → gauge algebra.
- `n_fibers`, `has_SM`, `has_GUT`, `best_gauge`

### SM Score (100-point scale)

```python
SM_SCORE = {
    'chi_match':        10,  # χ = ±6
    'clean_bundles':    15,  # n_clean > 0, scaled by log2(n_clean)
    'yukawa_rank':      15,  # Yukawa texture rank ≥ 3
    'yukawa_hierarchy': 10,  # eigenvalue spread ≥ 10³
    'lvs_compatible':   15,  # τ/V^{2/3} < 0.01
    'fibration_sm':     10,  # contains SU(3)×SU(2)×U(1) or GUT
    'c2_positive':       5,  # c₂·D ≥ 0 for all effective D
    'dp_divisors':       5,  # has del Pezzo divisors (instanton effects)
    'tadpole_ok':        5,  # |χ/24| ≤ 20
    'mori_blowdown':     5,  # has del Pezzo contracting curves
    'h0_diversity':      5,  # many distinct h⁰ values
}
TOTAL = 100
```

---

## T3: Full Phenomenology (30s+/poly)

Run only on the top ~50 polytopes by SM_SCORE. Deep dive tier.

### Computes

#### 1. Triangulation Stability
```python
tris = p.random_triangulations_fast(N=100)
# Check if winning properties (n_clean, Swiss cheese, fibrations)
# are stable across triangulations
```
- `n_triangulations` — how many tested
- `props_stable` — 1 if properties persist across ≥80% of triangulations

#### 2. Moduli Stabilization Feasibility
For LVS, need a rigid divisor (h^{1,0} = h^{2,0} = 0) that's a del Pezzo.
Check using c₂·D and D³:
- dP_n has D³ = 9-n, c₂·D = 3+n
- `has_instanton_divisor` — 1 if suitable rigid del Pezzo exists

#### 3. Flux Landscape Estimate
Given tadpole bound N_flux ≤ χ/24, estimate flux vacua count
via Ashok-Douglas formula.
- `n_flux_vacua_est` — estimated number of flux vacua (log₁₀)

#### 4. Orientifold Compatibility
GLSM charge matrix constrains possible involutions for O3/O7 orientifold.
```python
glsm = cy.glsm_charge_matrix()
# Check Z₂ symmetry structure
```
- `orientifold_ok` — 1 if GLSM structure admits viable orientifold

---

## Database: `cy_landscape_v3.db`

Fresh database (not migrated from v2). Schema in `db_utils_v3.py`.

### New columns vs v2

```sql
-- T05 (new tier)
yukawa_rank      INTEGER,   -- nonzero κ_{ijk} in basis
yukawa_density   REAL,      -- nonzero / total possible triples
chi_over_24      REAL,      -- tadpole bound
c2_all_positive  INTEGER,   -- boolean: DRS conjecture check
kappa_signature  TEXT,      -- Hessian eigenvalue signature "(p,q)"
volume_form_type TEXT,      -- swiss_cheese | fibered | generic

-- T1 (merged T025+T1)
n_clean_est      INTEGER,   -- time-budgeted clean estimate
first_clean_at   INTEGER,   -- bundle index of first clean hit

-- T2 (new physics)
lvs_score        REAL,      -- best τ/V^{2/3} ratio
best_small_div   INTEGER,   -- index of best small divisor
volume_hierarchy REAL,      -- V_big / V_small ratio
yukawa_texture_rank INTEGER,-- rank of Yukawa matrix for clean bundles
yukawa_hierarchy REAL,      -- max/min eigenvalue ratio
yukawa_zeros     INTEGER,   -- texture zeros in Y matrix
n_mori_rays      INTEGER,   -- Mori cone generators
n_dp_contract    INTEGER,   -- del Pezzo contracting curves
sm_score         INTEGER,   -- 0-100 composite SM score

-- T3 (new tier)
n_triangulations INTEGER,   -- triangulations tested
props_stable     INTEGER,   -- properties stable across triangulations
n_flux_vacua_est REAL,      -- log₁₀ estimated flux vacua
has_instanton_div INTEGER,  -- suitable rigid dP for LVS
orientifold_ok   INTEGER,   -- GLSM admits viable orientifold
```

---

## Execution Modes

```bash
# T0+T05 only, fast landscape mapping
python v3/pipeline_v3.py --ladder --h11 13 30

# Full T0→T2 scan for one h11
python v3/pipeline_v3.py --scan --h11 19 -w 14

# T3 deep dive on top candidates from DB
python v3/pipeline_v3.py --deep --top 50

# Rescore existing T2 data with new weights (no recomputation)
python v3/pipeline_v3.py --rescore

# Resume interrupted scan
python v3/pipeline_v3.py --scan --h11 19 --resume
```

---

## Implementation Order

1. `db_utils_v3.py` — fresh schema + LandscapeDB class
2. `cy_compute_v3.py` — new T05 + Yukawa + LVS functions (imports from v2/cy_compute.py)
3. `pipeline_v3.py` — orchestrator with T0→T05→T1→T2→T3
4. Run ladder h13→30 to map landscape shape
5. Targeted deep scans on best h11 levels
6. T3 on top 50 candidates

---

## Design Principles

1. **T05 is the innovation** — extracts physics from data we already compute at near-zero cost
2. **Continuous scoring** — 100-point SM_SCORE replaces binary pass/fail
3. **Monster-friendly** — T0+T05 cost ~0.15s/poly, so h11=30 (1M+ polytopes) takes ~12h
4. **DB-first** — every tier writes immediately; `--rescore` re-ranks without recomputing
5. **v2 code stays untouched** — v3 imports from v2 where possible, adds new layers on top
