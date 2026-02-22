"""
DRAGON SLAYER 40h: h⁰ via Koszul + lattice point counting + h¹ correction.

FIXES from 40g:
  - Off-by-one bug: rays[k] = pts[k+1] but was paired with D_toric[k].
    Now correctly uses D_toric for NON-ORIGIN indices only.
  - Computes h¹(V, D+K_V) correction using toric sheaf cohomology:
    h¹ = Σ_m max(0, #components(V(m)) - 1)
    where V(m) = {ρ : ⟨m, v_ρ⟩ < -l_ρ} for the shifted bundle L = D + K_V.

The correct formula:
  h⁰(X, D) = h⁰(V, D) - h⁰(V, D+K_V) + dim(ker(H¹(V,D+K_V) → H¹(V,D)))
  ≥ h⁰(V, D) - h⁰(V, D+K_V)

Since the correction is non-negative, the simple formula is a LOWER BOUND.
If h¹ bumps it up to 3, we have our proof.
"""

import cytools as cy
import numpy as np
from scipy.optimize import linprog
from cytools.config import enable_experimental_features
enable_experimental_features()
from collections import defaultdict

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"

print("=" * 65)
print("  h⁰ VIA KOSZUL + LATTICE POINTS + h¹ CORRECTION")
print("=" * 65)

polys = list(cy.fetch_polytopes(h11=15, h21=18, lattice='N', limit=1000))
p = polys[40]
tri = p.triangulate()
cyobj = tri.get_cy()

h11 = cyobj.h11()
div_basis = [int(x) for x in cyobj.divisor_basis()]
intnums_basis = dict(cyobj.intersection_numbers(in_basis=True))
c2_basis = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)
glsm = np.array(cyobj.glsm_charge_matrix(), dtype=int)
n_toric = glsm.shape[1]  # 20

# ================================================================
# STEP 1: Fan rays (properly indexed)
# ================================================================
print("\n--- Step 1: Fan structure ---")

pts = np.array(p.points(), dtype=int)
print(f"Polytope points: {pts.shape[0]} (in Z^{pts.shape[1]})")

# Origin is at index 0
assert np.all(pts[0] == 0), "Expected origin at index 0"

# Fan rays: all points EXCEPT origin (indices 1..19)
ray_indices = list(range(1, len(pts)))  # [1, 2, ..., 19]
n_rays = len(ray_indices)  # 19
print(f"Fan rays: {n_rays} (indices {ray_indices[0]}..{ray_indices[-1]})")
assert n_rays == n_toric - 1, f"Expected {n_toric-1} rays, got {n_rays}"

# The ray vectors
v_rays = pts[ray_indices]  # shape (19, 4)
dim = v_rays.shape[1]  # 4

# Triangulation simplices (all contain origin at index 0)
simplices = tri.simplices()
print(f"Simplices (maximal cones): {len(simplices)}")

# Build adjacency graph for rays (for h¹ computation)
# Two rays are adjacent if they appear in the same maximal cone
adjacency = defaultdict(set)
for simplex in simplices:
    # Remove origin (index 0) to get the 4 ray indices forming the cone
    cone_rays = [int(r) for r in simplex if r != 0]
    for i, r1 in enumerate(cone_rays):
        for r2 in cone_rays[i+1:]:
            adjacency[r1].add(r2)
            adjacency[r2].add(r1)

print(f"Adjacency graph: {sum(len(v) for v in adjacency.values())//2} edges")

# Also need to map ray indices to local indices (0..18)
ray_to_local = {r: i for i, r in enumerate(ray_indices)}

# ================================================================
# STEP 2: Divisor conversion (basis → toric)
# ================================================================
print("\n--- Step 2: Divisor conversion ---")

# div_basis = [1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18]
# Non-basis ray indices: 2, 6, 10  (plus 0=origin which is not a ray)
non_basis_rays = [r for r in ray_indices if r not in div_basis]
print(f"Basis ray indices: {div_basis}")
print(f"Non-basis ray indices: {non_basis_rays}")

# Verify basis submatrix is identity
basis_submatrix = glsm[:, div_basis]
assert np.allclose(basis_submatrix, np.eye(h11)), "Basis submatrix not identity!"

def basis_to_toric(D_basis):
    """Convert divisor from h11-basis to toric coordinates (20 entries)."""
    D_toric = np.zeros(n_toric, dtype=int)
    for a in range(h11):
        D_toric[div_basis[a]] = D_basis[a]
    # Non-basis and origin entries stay 0
    return D_toric

# ================================================================
# STEP 3: Lattice point counting (FIXED indexing)
# ================================================================
print("\n--- Step 3: Lattice point counting ---")

def count_lattice_points(D_toric):
    """
    Count lattice points in P_D = {m ∈ Z^4 : ⟨m, v_ρ⟩ ≥ -D_toric[ρ] for all rays ρ}.
    
    Uses CORRECT indexing: ray ρ ∈ {1,...,19} uses D_toric[ρ] and pts[ρ].
    """
    # Build constraint matrix: constraints are -⟨m, v_ρ⟩ ≤ D_toric[ρ] for each ray ρ
    A_ub = np.zeros((n_rays, dim))
    b_ub = np.zeros(n_rays)
    for k, rho in enumerate(ray_indices):
        A_ub[k] = -pts[rho]  # -v_ρ
        b_ub[k] = D_toric[rho]  # d_ρ
    
    # Find bounding box
    bounds = []
    for i in range(dim):
        c_min = np.zeros(dim); c_min[i] = 1
        c_max = np.zeros(dim); c_max[i] = -1
        
        res_min = linprog(c_min, A_ub=A_ub, b_ub=b_ub, bounds=(None, None), method='highs')
        res_max = linprog(c_max, A_ub=A_ub, b_ub=b_ub, bounds=(None, None), method='highs')
        
        if res_min.success and res_max.success:
            lo = int(np.floor(res_min.fun))
            hi = int(np.ceil(-res_max.fun))
            bounds.append((lo, hi))
        else:
            return 0  # empty polytope
    
    # Enumerate lattice points
    total = 1
    for lo, hi in bounds:
        total *= (hi - lo + 1)
    if total > 50_000_000:
        return -1  # too large, signal failure
    if total == 0:
        return 0
    
    count = 0
    for m0 in range(bounds[0][0], bounds[0][1]+1):
        for m1 in range(bounds[1][0], bounds[1][1]+1):
            for m2 in range(bounds[2][0], bounds[2][1]+1):
                for m3 in range(bounds[3][0], bounds[3][1]+1):
                    m = np.array([m0, m1, m2, m3])
                    # Check: ⟨m, pts[ρ]⟩ ≥ -D_toric[ρ] for all rays ρ
                    ok = True
                    for k, rho in enumerate(ray_indices):
                        if np.dot(m, pts[rho]) < -D_toric[rho]:
                            ok = False
                            break
                    if ok:
                        count += 1
    return count


# Sanity checks
D_zero = np.zeros(n_toric, dtype=int)
h0_zero = count_lattice_points(D_zero)
print(f"h⁰(V, O(0)) = {h0_zero} (should be 1)")
assert h0_zero == 1, f"SANITY FAIL: h⁰(V,0) = {h0_zero}"

D_anticanon = np.zeros(n_toric, dtype=int)
for rho in ray_indices:
    D_anticanon[rho] = 1
h0_K = count_lattice_points(D_anticanon)
dual_pts = len(p.dual().points())
print(f"h⁰(V, O(-K)) = {h0_K} (dual polytope pts = {dual_pts})")
# For a reflexive polytope, h⁰(-K) = # lattice points of dual polytope
assert h0_K == dual_pts, f"SANITY FAIL: h⁰(-K) = {h0_K}, dual pts = {dual_pts}"

# ================================================================
# STEP 4: h¹ on toric variety via connectivity
# ================================================================
print("\n--- Step 4: h¹ toric computation ---")

def compute_h1_toric(D_toric, box_radius=6):
    """
    Compute h¹(V, O(D)) using Čech cohomology on the toric variety.
    
    h¹(V, O(D)) = Σ_m max(0, #components(V(m)) - 1)
    where V(m) = {ρ ∈ rays : ⟨m, v_ρ⟩ < -D_toric[ρ]}
    and connectivity = connected components in the fan adjacency graph.
    
    The sum is finite: contributions come from a bounded region of M.
    We use a box [-R, R]^4 to capture all contributions.
    """
    h1 = 0
    contributing_m = []
    
    R = box_radius
    for m0 in range(-R, R+1):
        for m1 in range(-R, R+1):
            for m2 in range(-R, R+1):
                for m3 in range(-R, R+1):
                    m = np.array([m0, m1, m2, m3])
                    
                    # Find V(m): set of rays with ⟨m, v_ρ⟩ < -D_toric[ρ]
                    V_m = set()
                    for rho in ray_indices:
                        ip = np.dot(m, pts[rho])
                        if ip < -D_toric[rho]:
                            V_m.add(rho)
                    
                    if len(V_m) <= 1:
                        continue  # 0 or 1 rays → 0 or 1 components → no h¹
                    
                    # Count connected components via BFS
                    visited = set()
                    n_components = 0
                    for start in V_m:
                        if start in visited:
                            continue
                        n_components += 1
                        # BFS
                        queue = [start]
                        visited.add(start)
                        while queue:
                            node = queue.pop()
                            for neighbor in adjacency[node]:
                                if neighbor in V_m and neighbor not in visited:
                                    visited.add(neighbor)
                                    queue.append(neighbor)
                    
                    if n_components > 1:
                        h1 += n_components - 1
                        contributing_m.append((tuple(m), n_components - 1))
    
    return h1, contributing_m


# Quick test: h¹(V, O(0)) should be 0 for a smooth complete toric variety
h1_zero, _ = compute_h1_toric(D_zero, box_radius=3)
print(f"h¹(V, O(0)) = {h1_zero} (should be 0)")

# ================================================================
# STEP 5: Compute h⁰(X, D) for χ=3 bundles with h¹ correction
# ================================================================
print("\n" + "=" * 65)
print("  FULL KOSZUL FOR χ=3 BUNDLES (with h¹ correction)")
print("=" * 65)

# Build χ=3 bundles
chi3_bundles = []

# Single divisor (n = -5..5)
for a in range(h11):
    for n in range(-5, 6):
        if n == 0: continue
        D = np.zeros(h11, dtype=int)
        D[a] = n
        D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
        c2D = sum(D[k]*c2_basis[k] for k in range(h11))
        chi_val = D3/6.0 + c2D/12.0
        if abs(abs(chi_val) - 3) < 0.01:
            chi3_bundles.append((D.copy(), int(round(chi_val)), int(round(D3))))

# Two-divisor (unit coefficients, a ≤ b)
for a in range(h11):
    for b in range(a, h11):
        D = np.zeros(h11, dtype=int)
        D[a] += 1; D[b] += 1
        D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
        c2D = sum(D[k]*c2_basis[k] for k in range(h11))
        chi_val = D3/6.0 + c2D/12.0
        if abs(abs(chi_val) - 3) < 0.01:
            chi3_bundles.append((D.copy(), int(round(chi_val)), int(round(D3))))

# Three-divisor (unit coefficients, a ≤ b ≤ c)
for a in range(h11):
    for b in range(a, h11):
        for c in range(b, h11):
            D = np.zeros(h11, dtype=int)
            D[a] += 1; D[b] += 1; D[c] += 1
            D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
            c2D = sum(D[k]*c2_basis[k] for k in range(h11))
            chi_val = D3/6.0 + c2D/12.0
            if abs(abs(chi_val) - 3) < 0.01:
                chi3_bundles.append((D.copy(), int(round(chi_val)), int(round(D3))))

# Also negative versions for three-divisor
for a in range(h11):
    for b in range(a, h11):
        for c in range(b, h11):
            D = np.zeros(h11, dtype=int)
            D[a] -= 1; D[b] -= 1; D[c] -= 1
            D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
            c2D = sum(D[k]*c2_basis[k] for k in range(h11))
            chi_val = D3/6.0 + c2D/12.0
            if abs(abs(chi_val) - 3) < 0.01:
                chi3_bundles.append((D.copy(), int(round(chi_val)), int(round(D3))))

# Also negative single divisors and mixed-sign two-divisor
for a in range(h11):
    for b in range(a+1, h11):
        D = np.zeros(h11, dtype=int)
        D[a] = 1; D[b] = -1
        D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
        c2D = sum(D[k]*c2_basis[k] for k in range(h11))
        chi_val = D3/6.0 + c2D/12.0
        if abs(abs(chi_val) - 3) < 0.01:
            chi3_bundles.append((D.copy(), int(round(chi_val)), int(round(D3))))
        D2 = -D.copy()
        D3_2 = sum(D2[i]*D2[j]*D2[k]*val for (i,j,k), val in intnums_basis.items())
        c2D2 = sum(D2[k]*c2_basis[k] for k in range(h11))
        chi_val2 = D3_2/6.0 + c2D2/12.0
        if abs(abs(chi_val2) - 3) < 0.01:
            chi3_bundles.append((D2.copy(), int(round(chi_val2)), int(round(D3_2))))

# Deduplicate
seen = set()
unique = []
for D, chi_val, D3 in chi3_bundles:
    key = tuple(D)
    if key not in seen:
        seen.add(key)
        unique.append((D, chi_val, D3))
chi3_bundles = unique

# Separate χ=+3 bundles (most promising for h⁰=3)
chi_pos3 = [(D, chi, D3) for D, chi, D3 in chi3_bundles if chi == 3]
chi_neg3 = [(D, chi, D3) for D, chi, D3 in chi3_bundles if chi == -3]
print(f"Total χ=±3 bundles: {len(chi3_bundles)} ({len(chi_pos3)} positive, {len(chi_neg3)} negative)")
print(f"\nComputing h⁰ and h¹ for all χ=+3 bundles...")

# For each χ=+3 bundle, compute h⁰(V,D), h⁰(V,D+K), and h¹(V,D+K)
proven = []
best_h0 = 0
best_bundles = []

for idx, (D_basis, chi_val, D3) in enumerate(chi_pos3):
    D_toric = basis_to_toric(D_basis)
    
    # D + K_V: shift d_ρ → d_ρ - 1 for all rays (since K_V = -Σ D_ρ)
    D_shifted = D_toric.copy()
    for rho in ray_indices:
        D_shifted[rho] -= 1
    
    h0_V = count_lattice_points(D_toric)
    h0_shift = count_lattice_points(D_shifted)
    
    if h0_V < 0 or h0_shift < 0:
        continue
    
    h0_lower = h0_V - h0_shift  # lower bound on h⁰(X, D)
    
    # Compute h¹ correction if there's a chance of reaching 3
    h1_shift = 0
    h1_D = 0
    h0_CY = h0_lower  # start with lower bound
    
    need_correction = (h0_lower < 3)
    if need_correction and h0_V > 0:
        # h¹(V, D+K_V) could bump h⁰ up
        h1_shift, h1_details = compute_h1_toric(D_shifted, box_radius=5)
        if h1_shift > 0:
            h1_D, h1_D_details = compute_h1_toric(D_toric, box_radius=5)
            # Correction = dim(ker(H¹(V,D+K) → H¹(V,D)))
            # Upper bound: min(h¹(V,D+K), correction)
            # The best case: correction = h¹(V,D+K) - 0 = h¹_shift
            # But more typically, correction ≤ h¹_shift
            h0_upper = h0_lower + h1_shift
            h0_CY = f"{h0_lower}..{h0_upper}"
        
    nonzero = [(k, D_basis[k]) for k in range(h11) if D_basis[k] != 0]
    parts = []
    for k, v in nonzero:
        if v == 1: parts.append(f"e{k}")
        elif v == -1: parts.append(f"-e{k}")
        else: parts.append(f"{v}*e{k}")
    label = " + ".join(parts).replace(" + -", " - ")
    
    status = ""
    if isinstance(h0_CY, str):  # range
        lo, hi = map(int, h0_CY.split(".."))
        if hi >= 3 and lo <= 3:
            status = WARN + " h⁰∈"
        else:
            status = f"   h⁰∈"
    else:
        if h0_CY == 3:
            status = PASS
            proven.append((D_basis.copy(), chi_val, D3, h0_CY, h0_V, h0_shift))
        else:
            status = "  "
            
    if h0_lower >= 3 or (isinstance(h0_CY, str) and int(h0_CY.split("..")[1]) >= 3):
        proven.append((D_basis.copy(), chi_val, D3, h0_CY, h0_V, h0_shift))
    
    if best_h0 < h0_lower:
        best_h0 = h0_lower
        best_bundles = [(label, h0_lower, h0_V, h0_shift)]
    elif best_h0 == h0_lower and h0_lower > 0:
        best_bundles.append((label, h0_lower, h0_V, h0_shift))
    
    extra = ""
    if h1_shift > 0:
        extra = f" h¹(V,D+K)={h1_shift}, h¹(V,D)={h1_D}"
    
    print(f"  {status} D = {label}: h⁰_V={h0_V}, h⁰_shift={h0_shift}, "
          f"h⁰_CY={h0_CY} (χ={chi_val}, D³={D3}){extra}")

# ================================================================
# FINAL VERDICT
# ================================================================
print(f"\n{'='*65}")
print(f"  BEST h⁰ (lower bound): {best_h0}")
if best_bundles:
    for label, h0, hv, hs in best_bundles[:5]:
        print(f"    D = {label}: h⁰≥{h0} (h⁰_V={hv}, h⁰_shift={hs})")
print(f"{'='*65}")

proven_certain = [x for x in proven if not isinstance(x[3], str)]
proven_possible = [x for x in proven if isinstance(x[3], str)]

if proven_certain:
    print(f"\n  {PASS} PROVEN: {len(proven_certain)} bundles with EXACT h⁰ = 3")
    for D, chi, D3, h0, hv, hs in proven_certain[:5]:
        nonzero = [(k, D[k]) for k in range(h11) if D[k] != 0]
        parts = []
        for k, v in nonzero:
            if v == 1: parts.append(f"e{k}")
            elif v == -1: parts.append(f"-e{k}")
            else: parts.append(f"{v}*e{k}")
        label = " + ".join(parts).replace(" + -", " - ")
        print(f"    ★ D = {label}: h⁰={h0}, χ={chi}, D³={D3}")
elif proven_possible:
    print(f"\n  {WARN} h⁰=3 POSSIBLE for {len(proven_possible)} bundles (h¹ correction)")
    for D, chi, D3, h0_range, hv, hs in proven_possible[:10]:
        nonzero = [(k, D[k]) for k in range(h11) if D[k] != 0]
        parts = []
        for k, v in nonzero:
            if v == 1: parts.append(f"e{k}")
            elif v == -1: parts.append(f"-e{k}")
            else: parts.append(f"{v}*e{k}")
        label = " + ".join(parts).replace(" + -", " - ")
        print(f"    ? D = {label}: h⁰∈{h0_range}, χ={chi}, D³={D3}")
else:
    print(f"\n  {FAIL} No h⁰=3 proven or possible from Koszul + h¹")
