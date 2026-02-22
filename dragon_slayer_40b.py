"""
DRAGON SLAYER 40b: Deep dive on the chi=3 bundle claim.

The pipeline claimed D = e3+e4+e10 gives D³=1 and chi=3.
Dragon slayer 40 computed D³=14 and chi=2.667.

Something is WRONG. Let's find out what.
"""

import cytools as cy
import numpy as np
from cytools.config import enable_experimental_features
enable_experimental_features()

polys = list(cy.fetch_polytopes(h11=15, h21=18, lattice='N', limit=1000))
p = polys[40]
tri = p.triangulate()
cyobj = tri.get_cy()

intnums = dict(cyobj.intersection_numbers())
c2 = np.array(cyobj.second_chern_class(), dtype=float)
n_toric = cyobj.glsm_charge_matrix().shape[1]
if len(c2) < n_toric:
    c2 = np.pad(c2, (0, n_toric - len(c2)))

div_basis = list(cyobj.divisor_basis())
h11 = cyobj.h11()

print(f"h11 = {h11}, div_basis has {len(div_basis)} elements")
print(f"n_toric = {n_toric}")
print(f"div_basis = {div_basis}")
print(f"c2 shape = {len(c2)}")
print()

# First: What are e3, e4, e10 referring to?
# In CYTools, divisor_basis() returns the TORIC INDICES of the basis divisors.
# e_k means the k-th basis element, which corresponds to toric divisor div_basis[k].
print("Basis element → Toric divisor mapping:")
for k, ti in enumerate(div_basis):
    print(f"  e{k} → D{ti}")

print()

# Now compute D = e3 + e4 + e10 properly
# This means coefficients [0,0,0,1,1,0,0,0,0,0,1,0,0,0,0] in the DIVISOR BASIS
# which translates to toric divisor D_{div_basis[3]} + D_{div_basis[4]} + D_{div_basis[10]}
e3_toric = div_basis[3]
e4_toric = div_basis[4]
e10_toric = div_basis[10]

print(f"e3 → D{e3_toric}")
print(f"e4 → D{e4_toric}")
print(f"e10 → D{e10_toric}")

# Method 1: Using toric indices directly
D_coeffs_toric = np.zeros(n_toric, dtype=int)
D_coeffs_toric[e3_toric] = 1
D_coeffs_toric[e4_toric] = 1
D_coeffs_toric[e10_toric] = 1

D3_toric = 0
for (a, b, c), val in intnums.items():
    D3_toric += D_coeffs_toric[a] * D_coeffs_toric[b] * D_coeffs_toric[c] * val
c2D_toric = sum(D_coeffs_toric[k] * c2[k] for k in range(min(n_toric, len(c2))))
chi_toric = D3_toric / 6.0 + c2D_toric / 12.0

print(f"\nMethod 1 (toric indices):")
print(f"  D³ = {D3_toric}")
print(f"  c2.D = {c2D_toric}")
print(f"  chi = {chi_toric:.6f}")

# Method 2: Maybe the intnum keys are already in basis form?
# Check what the intersection number keys look like
print("\n--- Intersection number key analysis ---")
all_keys = list(intnums.keys())
print(f"Total intersection numbers: {len(all_keys)}")
min_idx = min(min(k) for k in all_keys)
max_idx = max(max(k) for k in all_keys)
print(f"Index range: {min_idx} to {max_idx}")

# Are the keys toric indices or basis indices?
# If max_idx < h11, they're basis indices
# If max_idx >= h11, they're toric indices
if max_idx < h11:
    print("KEYS ARE BASIS INDICES")
    key_type = "basis"
elif max_idx >= h11:
    print("KEYS ARE TORIC INDICES")
    key_type = "toric"
else:
    print("AMBIGUOUS")
    key_type = "unknown"

# Method 3: Use basis indices directly
print("\nMethod 3 (basis indices):")
D_coeffs_basis = np.zeros(h11, dtype=int)
D_coeffs_basis[3] = 1
D_coeffs_basis[4] = 1
D_coeffs_basis[10] = 1

D3_basis = 0
for (a, b, c), val in intnums.items():
    if a < h11 and b < h11 and c < h11:
        D3_basis += D_coeffs_basis[a] * D_coeffs_basis[b] * D_coeffs_basis[c] * val
c2D_basis = sum(D_coeffs_basis[k] * c2[k] for k in range(min(h11, len(c2))))
chi_basis = D3_basis / 6.0 + c2D_basis / 12.0

print(f"  D³ = {D3_basis}")
print(f"  c2.D = {c2D_basis}")
print(f"  chi = {chi_basis:.6f}")

# Let's also try the CYTools API directly
print("\n--- CYTools direct computation ---")
# CYTools computes intersection numbers in the divisor basis by default
# Let's get the full intersection tensor
print("Trying cyobj.intersection_numbers(in_basis=True)...")
try:
    intnums_basis = dict(cyobj.intersection_numbers(in_basis=True))
    all_keys_basis = list(intnums_basis.keys())
    print(f"  Total: {len(all_keys_basis)}")
    min_idx_b = min(min(k) for k in all_keys_basis)
    max_idx_b = max(max(k) for k in all_keys_basis)
    print(f"  Index range: {min_idx_b} to {max_idx_b}")
    
    D3_api = 0
    for (a, b, c), val in intnums_basis.items():
        if a < h11 and b < h11 and c < h11:
            D3_api += D_coeffs_basis[a] * D_coeffs_basis[b] * D_coeffs_basis[c] * val
    
    c2_basis_arr = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)
    c2D_api = sum(D_coeffs_basis[k] * c2_basis_arr[k] for k in range(min(h11, len(c2_basis_arr))))
    chi_api = D3_api / 6.0 + c2D_api / 12.0
    
    print(f"  D³ = {D3_api}")
    print(f"  c2.D = {c2D_api}")
    print(f"  chi = {chi_api:.6f}")
except Exception as e:
    print(f"  Error: {e}")

# Now: EXHAUSTIVE SEARCH for 3-divisor bundles with |chi|=3
print("\n\n=== EXHAUSTIVE 3-DIVISOR BUNDLE SEARCH ===")
print("Searching all D = ea + eb + ec with |chi|=3...")

try:
    intnums_b = dict(cyobj.intersection_numbers(in_basis=True))
    c2b = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)
    
    found = []
    for a in range(h11):
        for b in range(a, h11):
            for c in range(b, h11):
                D = np.zeros(h11, dtype=int)
                D[a] += 1
                D[b] += 1
                D[c] += 1
                
                # Compute D³ using intersection numbers
                D3 = 0
                for (i, j, k), val in intnums_b.items():
                    D3 += D[i] * D[j] * D[k] * val
                
                c2D = sum(D[k] * c2b[k] for k in range(h11))
                chi_val = D3 / 6.0 + c2D / 12.0
                
                if abs(abs(chi_val) - 3) < 0.01:
                    found.append((a, b, c, D3, c2D, round(chi_val)))
    
    print(f"Found {len(found)} bundles with |chi|=3:")
    for (a, b, c, D3, c2D, chi_val) in found[:30]:
        if a == b == c:
            label = f"3*e{a}"
        elif a == b:
            label = f"2*e{a}+e{c}"
        elif b == c:
            label = f"e{a}+2*e{b}"
        else:
            label = f"e{a}+e{b}+e{c}"
        print(f"  {label}: D³={D3}, c2.D={c2D:.0f}, chi={chi_val}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Also check: what does D³=1 correspond to?
print("\n\n=== BUNDLES WITH D³=1 ===")
try: 
    count_d3_1 = 0
    for a in range(h11):
        for b in range(a, h11):
            for c in range(b, h11):
                D = np.zeros(h11, dtype=int)
                D[a] += 1
                D[b] += 1
                D[c] += 1
                
                D3 = 0
                for (i, j, k), val in intnums_b.items():
                    D3 += D[i] * D[j] * D[k] * val
                
                if D3 == 1:
                    c2D = sum(D[k] * c2b[k] for k in range(h11))
                    chi_val = 1/6.0 + c2D/12.0
                    count_d3_1 += 1
                    if count_d3_1 <= 20:
                        if a == b == c:
                            label = f"3*e{a}"
                        elif a == b:
                            label = f"2*e{a}+e{c}"
                        elif b == c:
                            label = f"e{a}+2*e{b}"
                        else:
                            label = f"e{a}+e{b}+e{c}"
                        print(f"  {label}: D³=1, c2.D={c2D:.0f}, chi={chi_val:.4f}")
    print(f"Total with D³=1: {count_d3_1}")
except Exception as e:
    print(f"Error: {e}")
