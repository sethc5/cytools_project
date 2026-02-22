"""
DRAGON SLAYER 40d: CORRECTED nef test with proper basis conversion.

The bug: Mori cone rays are in TORIC coordinates (20-dim),
but D was in BASIS coordinates (15-dim). Need to convert.
"""

import cytools as cy
import numpy as np
from cytools.config import enable_experimental_features
enable_experimental_features()

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"

print("=" * 65)
print("  CORRECTED NEF TEST: POLYTOPE 40")
print("=" * 65)

polys = list(cy.fetch_polytopes(h11=15, h21=18, lattice='N', limit=1000))
p = polys[40]
tri = p.triangulate()
cyobj = tri.get_cy()

h11 = cyobj.h11()
n_toric = cyobj.glsm_charge_matrix().shape[1]
div_basis = list(cyobj.divisor_basis())
intnums_basis = dict(cyobj.intersection_numbers(in_basis=True))
c2_basis = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

print(f"h11 = {h11}, n_toric = {n_toric}")
print(f"div_basis = {list(div_basis)}")

# Get the GLSM matrix and linear relations
glsm = cyobj.glsm_charge_matrix()
linrels = cyobj.glsm_linear_relations()

print(f"GLSM matrix: {glsm.shape}")
print(f"Linear relations: {linrels.shape}")

# The Mori cone is the dual of the Kähler cone.
# Rays live in H_2(X, Z) ≅ Z^{h11}.
# But CYTools gives them in the TORIC basis (Z^{n_toric}).

# The proper pairing: D·C = Σ_ρ D_ρ * C_ρ (sum over toric divisors)
# where D_ρ is D written in the full toric divisor basis.

# To convert D from h11-basis to toric basis:
# D_toric[div_basis[a]] = D_basis[a] for each basis element a
# D_toric[other] = sum of linear relation contributions

# Actually, CYTools uses the convention that a divisor D in the basis
# corresponds to the toric divisor:
# D_toric = sum_a D_a * delta_{ρ, div_basis[a]}
# (i.e., only the basis divisors get nonzero coefficients)
# BUT this ignores the linear relations.

# The correct approach: the linear relations tell us that 
# D_ρ = Σ_a L_{ρ,a} * D_a for non-basis divisors.
# Here L is the "inverse" of the GLSM charge matrix restricted to basis.

# Let me just compute D·C properly.
# Actually, the SIMPLEST correct approach:
# D·C = Σ_a D_a * K_a where K_a = e_a · C (pairing of basis divisor with curve)
# and K_a = C[div_basis[a]] for Mori cone in toric coords.

# Wait, that's not right either. Let me think carefully.
# 
# The Mori cone rays C are in the space Z^{n_toric} / (linear relations).
# The pairing D·C where D is a divisor:
#   D = Σ_a d_a * E_a where E_a is the a-th basis divisor
#   C is given as a vector in Z^{n_toric}
#   The pairing is: D·C = Σ_ρ d_ρ * C_ρ
#   where d_ρ = d_a if ρ = div_basis[a], and d_ρ is determined by linear relations otherwise.
#
# Alternatively, since E_a = D_{div_basis[a]} in the toric divisor basis:
#   D·C = Σ_a d_a * C[div_basis[a]]

# Let me verify this understanding.

# Get Mori cone
mori = cyobj.toric_mori_cone()
mori_gens = mori.rays()
print(f"\nMori cone: {len(mori_gens)} generators, each {len(mori_gens[0])}-dimensional")

# Get Kähler cone for cross-check
kahler = cyobj.toric_kahler_cone()

# Let's check: are mori_gens in Z^{n_toric} or Z^{h11}?
print(f"Mori ray dimension: {len(mori_gens[0])}")
print(f"n_toric = {n_toric}")
print(f"h11 = {h11}")

if len(mori_gens[0]) == n_toric:
    print("Mori rays are in TORIC coordinates")
    # Pairing: D·C = Σ_a d_a * C[div_basis[a]]
    def pairing(D_basis, C_toric):
        """D in basis coords, C in toric coords."""
        return sum(D_basis[a] * C_toric[div_basis[a]] for a in range(h11))
elif len(mori_gens[0]) == h11:
    print("Mori rays are in BASIS coordinates")
    def pairing(D_basis, C_basis):
        """Both in basis coords."""
        return sum(D_basis[a] * C_basis[a] for a in range(h11))
else:
    print(f"UNEXPECTED: Mori ray dimension = {len(mori_gens[0])}")
    exit(1)

# VERIFICATION: the Kähler cone generators should pair positively with Mori cone generators
print("\n--- Sanity check: Kähler cone gens vs Mori cone gens ---")
kahler_gens = kahler.rays()
print(f"Kähler cone: {len(kahler_gens)} generators, each {len(kahler_gens[0])}-dimensional")

if len(kahler_gens[0]) == n_toric:
    print("Kähler rays are in TORIC coordinates")
    # Pairing: J·C = Σ_ρ J_ρ * C_ρ
    n_positive = 0
    n_zero = 0
    n_negative = 0
    for J in kahler_gens[:5]:
        for C in mori_gens[:5]:
            p_val = sum(J[rho] * C[rho] for rho in range(n_toric))
            if p_val > 1e-10:
                n_positive += 1
            elif p_val < -1e-10:
                n_negative += 1
            else:
                n_zero += 1
    print(f"  Kähler·Mori: {n_positive} positive, {n_zero} zero, {n_negative} negative")
    if n_negative > 0:
        print(f"  {WARN}: Some negative pairings (duality check failed!)")
else:
    print(f"  Kähler rays are {len(kahler_gens[0])}-dimensional")

# Cross-check: use CYTools tips
tip = kahler.tip_of_stretched_cone(1)
print(f"\nKähler tip: {list(tip[:5])}... (dim={len(tip)})")

# Pair tip with each Mori generator
tip_pairings = []
for i, C in enumerate(mori_gens):
    if len(tip) == n_toric:
        p_val = sum(tip[rho] * C[rho] for rho in range(n_toric))
    else:
        p_val = sum(tip[a] * C[div_basis[a]] for a in range(min(len(tip), h11)))
    tip_pairings.append(p_val)

print(f"Tip · Mori pairings: min={min(tip_pairings):.4f}, max={max(tip_pairings):.4f}")
if min(tip_pairings) > -1e-10:
    print(f"{PASS}: Tip is in interior of nef cone (all pairings ≥ 0)")
else:
    print(f"{FAIL}: Tip is NOT nef! Something is wrong.")

# ================================================================
# NOW: Proper nef test for χ=3 bundles
# ================================================================
print("\n" + "=" * 65)
print("  PROPER NEF TEST FOR χ=3 BUNDLES")
print("=" * 65)

# Build all χ=3 bundles (basis coordinates)
chi3_bundles = []

# Single divisor
for a in range(h11):
    for n in range(-5, 6):
        if n == 0:
            continue
        D = np.zeros(h11, dtype=int)
        D[a] = n
        D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
        c2D = sum(D[k]*c2_basis[k] for k in range(h11))
        chi_val = D3/6.0 + c2D/12.0
        if abs(abs(chi_val) - 3) < 0.01:
            chi3_bundles.append((D.copy(), int(round(chi_val)), D3))

# Two-divisor
for a in range(h11):
    for b in range(a+1, h11):
        for na in range(-3, 4):
            for nb in range(-3, 4):
                if na == 0 and nb == 0:
                    continue
                D = np.zeros(h11, dtype=int)
                D[a] = na
                D[b] = nb
                D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
                c2D = sum(D[k]*c2_basis[k] for k in range(h11))
                chi_val = D3/6.0 + c2D/12.0
                if abs(abs(chi_val) - 3) < 0.01:
                    chi3_bundles.append((D.copy(), int(round(chi_val)), D3))

# Three-divisor (unit coefficients)
for a in range(h11):
    for b in range(a, h11):
        for c in range(b, h11):
            D = np.zeros(h11, dtype=int)
            D[a] += 1; D[b] += 1; D[c] += 1
            D3 = sum(D[i]*D[j]*D[k]*val for (i,j,k), val in intnums_basis.items())
            c2D = sum(D[k]*c2_basis[k] for k in range(h11))
            chi_val = D3/6.0 + c2D/12.0
            if abs(abs(chi_val) - 3) < 0.01:
                chi3_bundles.append((D.copy(), int(round(chi_val)), D3))

print(f"Total χ=±3 bundles found: {len(chi3_bundles)}")

# Nef test
nef_bundles = []
nef_and_big = []

for idx, (D, chi_val, D3) in enumerate(chi3_bundles):
    is_nef = True
    min_pair = float('inf')
    for C in mori_gens:
        p_val = pairing(D, C)
        min_pair = min(min_pair, p_val)
        if p_val < -1e-10:
            is_nef = False
            break
    
    if is_nef:
        nef_bundles.append((D, chi_val, D3, min_pair))
        if D3 > 0:
            nef_and_big.append((D, chi_val, D3))

print(f"\nNef bundles with |χ|=3: {len(nef_bundles)}")
print(f"Nef AND big (D³>0): {len(nef_and_big)}")

# Show all nef bundles
for i, (D, chi_val, D3, mp) in enumerate(nef_bundles[:20]):
    nonzero = [(k, D[k]) for k in range(h11) if D[k] != 0]
    parts = []
    for k, v in nonzero:
        ti = div_basis[k]
        if v == 1: parts.append(f"e{k}")
        elif v == -1: parts.append(f"-e{k}")
        else: parts.append(f"{v}*e{k}")
    label = " + ".join(parts).replace(" + -", " - ")
    nef_label = "nef+big" if D3 > 0 else "nef (D³≤0)"
    print(f"  [{nef_label}] D = {label}: D³={D3}, χ={chi_val}, min(D·C)={mp:.1f}")

# ================================================================
# REPORT
# ================================================================
print("\n" + "=" * 65)
if nef_and_big:
    print(f"  {PASS} PROVEN: {len(nef_and_big)} BUNDLES WITH h⁰ = 3")
    print("=" * 65)
    print(f"""
By Kawamata-Viehweg vanishing:
  D nef + D big (D³ > 0) ⟹ hⁱ(O(D)) = 0 for i > 0
  Therefore h⁰(O(D)) = χ(O(D)) = 3  ∎
""")
    for i, (D, chi_val, D3) in enumerate(nef_and_big[:10]):
        nonzero = [(k, D[k]) for k in range(h11) if D[k] != 0]
        parts = []
        for k, v in nonzero:
            if v == 1: parts.append(f"e{k}")
            elif v == -1: parts.append(f"-e{k}")
            else: parts.append(f"{v}*e{k}")
        label = " + ".join(parts).replace(" + -", " - ")
        toric_parts = []
        for k, v in nonzero:
            ti = div_basis[k]
            if v == 1: toric_parts.append(f"D{ti}")
            elif v == -1: toric_parts.append(f"-D{ti}")
            else: toric_parts.append(f"{v}D{ti}")
        toric_label = " + ".join(toric_parts).replace(" + -", " - ")
        print(f"  ★ Bundle {i+1}: {label} = {toric_label}")
        print(f"    D³ = {D3}, χ = {chi_val}, h⁰ = 3 (PROVEN)")
        
        # Show nef certificate
        pairings_sorted = sorted([pairing(D, C) for C in mori_gens])
        print(f"    Min Mori pairing: {pairings_sorted[0]:.0f}")
        print()
else:
    print(f"  VERDICT: NO NEF+BIG χ=3 BUNDLES FOUND")
    print("=" * 65)
    
    # Let's find the CLOSEST to nef
    print(f"\nBundles closest to being nef:")
    near_nef = []
    for D, chi_val, D3 in chi3_bundles:
        if D3 <= 0:
            continue
        min_pair = min(pairing(D, C) for C in mori_gens)
        near_nef.append((D, chi_val, D3, min_pair))
    
    near_nef.sort(key=lambda x: -x[3])  # sort by most-positive min pairing
    for i, (D, chi_val, D3, mp) in enumerate(near_nef[:10]):
        nonzero = [(k, D[k]) for k in range(h11) if D[k] != 0]
        parts = []
        for k, v in nonzero:
            if v == 1: parts.append(f"e{k}")
            elif v == -1: parts.append(f"-e{k}")
            else: parts.append(f"{v}*e{k}")
        label = " + ".join(parts).replace(" + -", " - ")
        print(f"  D = {label}: D³={D3}, χ={chi_val}, min(D·C)={mp}")
    
    if near_nef:
        best = near_nef[0]
        if best[3] >= -2:
            print(f"\n  CLOSE: Best bundle misses nef by {-best[3]} (min pairing = {best[3]})")
            print(f"  This bundle might still have h⁰=3 by other arguments.")
    
    # ================================================================
    # ALTERNATIVE: Koszul sequence approach
    # ================================================================
    print(f"\n{'='*65}")
    print(f"  ALTERNATIVE: LATTICE POINT COUNTING (ambient toric)")
    print(f"{'='*65}")
    
    # For a line bundle O(D) on the CY hypersurface X ⊂ V:
    # The Koszul sequence gives:
    #   h⁰(X, D) = h⁰(V, D) - h⁰(V, D - K_V⁻¹) + h¹(V, D - K_V⁻¹) - h¹(V, D)
    #
    # On a toric variety V, h⁰(V, D) = lattice points in polyhedron P_D.
    # P_D = { m ∈ M_R : ⟨m, u_ρ⟩ ≥ -d_ρ ∀ρ }
    # where u_ρ are the ray generators and d_ρ = D·D_ρ.
    
    # Get the fan data
    pts = p.points()
    print(f"  Polytope points: {len(pts)}")
    print(f"  (Would need fan ray generators and anticanonical class to proceed)")
    print(f"  This requires a more sophisticated computation (cohomCalg).")
