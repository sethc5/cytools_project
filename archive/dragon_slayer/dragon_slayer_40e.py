"""
DRAGON SLAYER 40e: DEFINITIVE h⁰ computation via cohomCalg.

cohomCalg computes line bundle cohomology on toric varieties and their
CY hypersurfaces using the algorithm from arXiv:1003.5217.

Input format:
  vertex data (polytope vertices)
  GLSM charge matrix (Stanley-Reisner ideal encoded)
  line bundle charges
"""

import cytools as cy
import numpy as np
import subprocess
import tempfile
import os
from cytools.config import enable_experimental_features
enable_experimental_features()

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"

print("=" * 65)
print("  DEFINITIVE h⁰ COMPUTATION VIA cohomCalg")
print("=" * 65)

# Fetch Polytope 40
polys = list(cy.fetch_polytopes(h11=15, h21=18, lattice='N', limit=1000))
p = polys[40]
tri = p.triangulate()
cyobj = tri.get_cy()

h11 = cyobj.h11()
n_toric = cyobj.glsm_charge_matrix().shape[1]
div_basis = list(cyobj.divisor_basis())
intnums_basis = dict(cyobj.intersection_numbers(in_basis=True))
c2_basis = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

# Get the GLSM charge matrix (rows = U(1) charges, cols = homogeneous coords)
glsm = cyobj.glsm_charge_matrix()
print(f"h11 = {h11}, n_toric = {n_toric}")
print(f"GLSM charge matrix ({glsm.shape[0]} x {glsm.shape[1]}):")
for row in glsm:
    print(f"  {list(row)}")

# Get the Stanley-Reisner ideal
# CYTools triangulation gives the simplicial complex; the SR ideal is
# the set of minimal non-faces.
sr = tri.sr_ideal()
print(f"\nStanley-Reisner ideal: {sr}")

# ================================================================
# Build cohomCalg input
# ================================================================
# Format (from cohomCalg documentation):
# vertex <n_vertices> <ambient_dim>
# <vertex data...>
# 
# Actually, cohomCalg uses a different format. Let me check:
# The input is:
# vertex <n_coords> <dim>
# <GLSM charge matrix rows>
# srideal [<SR monomials>]
# ambientcohom O(D1, D2, ..., Dn)

def run_cohomcalg(glsm_matrix, sr_ideal, line_bundle_charges):
    """
    Run cohomCalg and return the cohomology dimensions.
    
    Args:
        glsm_matrix: numpy array, shape (h11, n_coords)
        sr_ideal: list of tuples (minimal non-faces)
        line_bundle_charges: list of integers, one per U(1) = per row of GLSM
    
    Returns:
        dict with h0, h1, h2, h3 or None if failed
    """
    n_coords = glsm_matrix.shape[1]
    n_charges = glsm_matrix.shape[0]
    
    # Build input string
    lines = []
    
    # Vertex section: each row of GLSM matrix
    lines.append(f"vertex {n_coords} {n_charges}")
    for col in range(n_coords):
        charges = [int(glsm_matrix[row, col]) for row in range(n_charges)]
        lines.append(" ".join(str(c) for c in charges))
    
    # SR ideal
    sr_parts = []
    for face in sr_ideal:
        # Each element of sr_ideal is a tuple of coordinate indices
        sr_mono = "*".join(f"x{i}" for i in face)
        sr_parts.append(sr_mono)
    lines.append(f"srideal [{'+'.join(sr_parts)}]")
    
    # Line bundle
    # cohomCalg wants the charges as O(d1, d2, ..., d_h11)
    charges_str = ",".join(str(c) for c in line_bundle_charges)
    lines.append(f"ambientcohom O({charges_str})")
    #lines.append("monomalifile off")
    
    input_text = "\n".join(lines) + "\n"
    
    # Write to temp file and run
    with tempfile.NamedTemporaryFile(mode='w', suffix='.in', delete=False, 
                                       dir='/tmp') as f:
        f.write(input_text)
        tmpfile = f.name
    
    try:
        result = subprocess.run(['cohomcalg', '--nomonomfile', tmpfile], 
                              capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        
        # Parse output for cohomology dimensions
        # Look for lines like: h^i(V, O(d1,...,dn)) = X
        # or the CY hypersurface result
        cohom = {}
        for line in output.split('\n'):
            # Look for ambient cohomology
            if 'True' in line or 'h^' in line.lower() or 'cohom' in line.lower():
                pass
            # The output format is typically:
            # h^0 h^1 h^2 h^3 h^4 (for 4D ambient)
            # followed by the CY restriction
            if 'COHOMOLOGY' in line.upper() or '|' in line:
                pass
        
        os.unlink(tmpfile)
        return output
    except Exception as e:
        os.unlink(tmpfile)
        return f"ERROR: {e}"


# First, let's test with a simple known case to understand the output format
print("\n--- Testing cohomCalg format ---")

# Test with trivial bundle O(0,0,...,0)
# h⁰ should be 1 (constant section)
test_charges = [0] * h11
result = run_cohomcalg(glsm, sr, test_charges)
print("Trivial bundle O(0,...,0):")
print(result[:500])

print("\n" + "=" * 65)

# Now test with the single-divisor chi=3 bundle: 3*e2 (which is D4 n=3)
# In GLSM charges: this means charge 3 on the 3rd U(1) and 0 elsewhere
test_charges = [0] * h11
test_charges[2] = 3
result = run_cohomcalg(glsm, sr, test_charges)
print("Bundle O(0,0,3,0,...,0) = 3*e2 = 3*D4:")
print(result[:800])

print("\n" + "=" * 65)

# Also test -3*e2
test_charges = [0] * h11
test_charges[2] = -3
result = run_cohomcalg(glsm, sr, test_charges)
print("Bundle O(0,0,-3,0,...,0) = -3*e2 = -3*D4:")
print(result[:800])

# ================================================================
# Now run on ALL chi=3 bundles
# ================================================================
print("\n" + "=" * 65)
print("  SYSTEMATIC SCAN: ALL χ=3 BUNDLES")
print("=" * 65)

# Build all χ=3 bundles
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

# Three-divisor (unit coefficients) - just include a subset for now
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

print(f"χ=±3 bundles to test: {len(chi3_bundles)}")

# Run cohomCalg on first several
proven_h0_3 = []
for idx, (D, chi_val, D3) in enumerate(chi3_bundles[:20]):
    charges = list(D)
    result = run_cohomcalg(glsm, sr, charges)
    
    nonzero = [(k, D[k]) for k in range(h11) if D[k] != 0]
    parts = []
    for k, v in nonzero:
        if v == 1: parts.append(f"e{k}")
        elif v == -1: parts.append(f"-e{k}")
        else: parts.append(f"{v}*e{k}")
    label = " + ".join(parts).replace(" + -", " - ")
    
    # Parse for h⁰
    h_vals = None
    for line in result.split('\n'):
        # cohomCalg typically outputs something like:
        # h^0(V, O(...)) = X  or  True: h^q = {h0, h1, h2, h3}
        if 'True' in line and '{' in line:
            # Parse {h0, h1, h2, h3}
            try:
                vals_str = line.split('{')[1].split('}')[0]
                h_vals = [int(x.strip()) for x in vals_str.split(',')]
            except:
                pass
    
    if h_vals:
        h0 = h_vals[0]
        status = PASS if h0 == 3 else (WARN if h0 > 0 else FAIL)
        print(f"  {status} D = {label}: h = {h_vals}  (χ={chi_val}, D³={D3})")
        if h0 == 3:
            proven_h0_3.append((D, chi_val, D3, h_vals))
    else:
        # Just show raw output
        print(f"  D = {label} (χ={chi_val}): [parsing needed]")
        # Show key lines
        for line in result.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) < 100:
                if any(kw in line.lower() for kw in ['cohom', 'h^', 'true', 'false', 'result', 'error']):
                    print(f"    {line}")

print(f"\n{'='*65}")
print(f"  SUMMARY")
print(f"{'='*65}")
print(f"Bundles tested: {min(20, len(chi3_bundles))}")
print(f"Proven h⁰=3: {len(proven_h0_3)}")
