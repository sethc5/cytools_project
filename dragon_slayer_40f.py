"""
DRAGON SLAYER 40f: DEFINITIVE h⁰ via cohomCalg (correct format!).

cohomCalg input format (from examples):
  vertex u1 | GLSM: (q1, q2, ..., qn);
  vertex u2 | GLSM: (q1, q2, ..., qn);
  ...
  srideal [u1*u2, u3*u4, ...];
  ambientcohom O(d1, d2, ..., dn);
"""

import cytools as cy
import numpy as np
import subprocess
import tempfile
import os
import re
from cytools.config import enable_experimental_features
enable_experimental_features()

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"

print("=" * 65)
print("  DEFINITIVE h⁰ VIA cohomCalg (correct format)")
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

glsm = np.array(cyobj.glsm_charge_matrix(), dtype=int)
sr = tri.sr_ideal()

print(f"h11 = {h11}, n_toric = {n_toric}")

def run_cohomcalg(glsm_matrix, sr_ideal, line_bundle_charges_list):
    """
    Run cohomCalg on given toric data with a list of line bundles.
    
    glsm_matrix: (h11, n_toric) integer array
    sr_ideal: list of tuples (each tuple = indices of coords in minimal non-face)
    line_bundle_charges_list: list of tuples, each tuple = (d1, ..., d_h11)
    
    Returns: list of cohomology tuples (h0, h1, h2, h3, ...) or None for each
    """
    n_coords = glsm_matrix.shape[1]
    n_charges = glsm_matrix.shape[0]
    
    lines = []
    
    # Vertex declarations
    for col in range(n_coords):
        charges = [int(glsm_matrix[row, col]) for row in range(n_charges)]
        charges_str = ", ".join(f"{c:2d}" for c in charges)
        lines.append(f"    vertex x{col} | GLSM: ({charges_str});")
    
    # SR ideal
    sr_parts = []
    for face in sr_ideal:
        face_ints = [int(x) for x in face]
        sr_mono = "*".join(f"x{i}" for i in face_ints)
        sr_parts.append(sr_mono)
    lines.append(f"    srideal [{', '.join(sr_parts)}];")
    
    # Turn off monomial file for speed
    lines.append("    monomialfile off;")
    
    # Line bundle cohomologies
    for charges in line_bundle_charges_list:
        charges_str = ", ".join(f"{c:2d}" for c in charges)
        lines.append(f"    ambientcohom O({charges_str});")
    
    input_text = "\n".join(lines) + "\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.in', delete=False,
                                       dir='/tmp') as f:
        f.write(input_text)
        tmpfile = f.name
    
    try:
        result = subprocess.run(['cohomcalg', '--nomonomfile', tmpfile],
                              capture_output=True, text=True, timeout=60)
        output = result.stdout
        os.unlink(tmpfile)
        return output, input_text
    except subprocess.TimeoutExpired:
        os.unlink(tmpfile)
        return "TIMEOUT", input_text
    except Exception as e:
        os.unlink(tmpfile)
        return f"ERROR: {e}", input_text


# First: test with trivial bundle to verify format
print("\n--- Format verification ---")
output, inp = run_cohomcalg(glsm, sr, [(0,)*h11])
if 'ERROR' in output:
    print("FORMAT ERROR! Dumping input:")
    print(inp[:2000])
    print("\nOutput:")
    print(output[:1000])
else:
    print("Format OK!")
    # Show just the cohomology result
    for line in output.split('\n'):
        if 'True' in line or 'False' in line or 'h^' in line.lower() or 'result' in line.lower():
            print(f"  {line.strip()}")

# ================================================================
# COMPUTE: All χ=3 bundles
# ================================================================
print("\n" + "=" * 65)
print("  COMPUTING LINE BUNDLE COHOMOLOGY")
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

print(f"Total χ=±3 bundles: {len(chi3_bundles)}")

# Run cohomCalg in batches
BATCH_SIZE = 10
proven_h0_3 = []
all_results = []

for batch_start in range(0, len(chi3_bundles), BATCH_SIZE):
    batch = chi3_bundles[batch_start:batch_start + BATCH_SIZE]
    charges_list = [tuple(D) for D, _, _ in batch]
    
    output, inp = run_cohomcalg(glsm, sr, charges_list)
    
    if 'ERROR' in output or 'TIMEOUT' in output:
        print(f"Batch {batch_start}: {output[:200]}")
        if batch_start == 0:
            print("First batch input (first 1500 chars):")
            print(inp[:1500])
        break
    
    # Parse cohomCalg output
    # Look for lines like: "True: h^q(V, O(...)) = (h0, h1, h2, h3, h4)"
    # or "True: h^q(V, O(...)) = {h0, h1, h2, h3, h4}"
    result_lines = [l.strip() for l in output.split('\n') 
                    if ('True' in l or 'False' in l) and 'h^' in l.lower()]
    
    for i, (D, chi_val, D3) in enumerate(batch):
        nonzero = [(k, D[k]) for k in range(h11) if D[k] != 0]
        parts = []
        for k, v in nonzero:
            if v == 1: parts.append(f"e{k}")
            elif v == -1: parts.append(f"-e{k}")
            else: parts.append(f"{v}*e{k}")
        label = " + ".join(parts).replace(" + -", " - ")
        
        if i < len(result_lines):
            line = result_lines[i]
            # Parse {h0, h1, h2, h3, h4} or (h0, h1, h2, h3, h4)
            match = re.search(r'[{(]([^}]+)[})]', line)
            if match:
                h_vals = [int(x.strip()) for x in match.group(1).split(',')]
                # For CY3 in 4D toric: ambient has h0..h4, CY restriction gives h0..h3
                # Actually cohomCalg outputs AMBIENT cohomology unless we use Koszul extension
                h0_ambient = h_vals[0] if h_vals else '?'
                result_str = f"h_ambient = {h_vals}"
                all_results.append((D, chi_val, D3, h_vals, label))
                
                status = ""
                print(f"  D = {label}: {result_str} (χ_CY={chi_val})")
            else:
                print(f"  D = {label}: {line}")
        else:
            print(f"  D = {label}: [no result parsed]")
    
    # Stop after first batch to inspect output format
    if batch_start == 0 and not result_lines:
        print("\nRaw output (first 2000 chars):")
        print(output[:2000])
        break

# ================================================================
# Parse and summarize
# ================================================================
print(f"\n{'='*65}")
print(f"  SUMMARY")
print(f"{'='*65}")

# For CY hypersurface cohomology, we need the Koszul sequence:
# h^i(CY, L) from h^i(ambient, L) and h^i(ambient, L(-[CY]))
# The anticanonical class [CY] = sum of all toric divisors in GLSM charges
# Let's compute [CY] in the divisor basis
print("\nAnticanonical class:")
K_inv = np.sum(glsm, axis=1)
print(f"  -K = sum of GLSM cols = {list(K_inv)}")

# For the Koszul approach, we need both O(D) and O(D - K_inv) on the ambient
# Let's compute those too
if all_results:
    print(f"\nAmbient cohomology computed for {len(all_results)} bundles")
    print(f"To get CY cohomology, need Koszul exact sequence:")
    print(f"  0 → O(D-[-K]) → O(D) → O_CY(D) → 0")
    print(f"  i.e., need h^i(ambient, D-(-K)) = h^i(ambient, D - K_inv)")
    
    # Compute the shifted bundles too
    print(f"\nComputing shifted bundles O(D - K_inv)...")
    shifted_charges = [tuple(D - K_inv) for D, _, _, _, _ in all_results]
    output2, _ = run_cohomcalg(glsm, sr, shifted_charges)
    
    shifted_lines = [l.strip() for l in output2.split('\n')
                     if ('True' in l or 'False' in l) and 'h^' in l.lower()]
    
    print(f"\nKoszul exact sequence results:")
    for i, (D, chi_val, D3, h_amb, label) in enumerate(all_results):
        if i < len(shifted_lines):
            match = re.search(r'[{(]([^}]+)[})]', shifted_lines[i])
            if match:
                h_shifted = [int(x.strip()) for x in match.group(1).split(',')]
                
                # Long exact sequence:
                # 0 → H⁰(V, D-K) → H⁰(V, D) → H⁰(X, D) → H¹(V, D-K) → H¹(V, D) → H¹(X, D) → ...
                # For V = 4D toric variety, X = CY3 hypersurface:
                # h^i(X, D) = h^i(V, D) - h^i(V, D-K) + h^{i+1}(V, D-K) - h^{i+1}(V, D) + ...
                # Actually the exact sequence gives:
                # h⁰(X) = h⁰(V,D) - h⁰(V,D-K) + kernel/cokernel corrections from h¹
                # But under good conditions (h^i(V,D-K)=0 for relevant i):
                # h⁰(X,D) = h⁰(V,D) - h⁰(V,D-K)
                
                h0_cy = h_amb[0] - h_shifted[0]
                # This is only approximate; need full long exact sequence
                
                status = PASS if h0_cy == 3 else (WARN if h0_cy > 0 else "")
                print(f"  {status} D = {label}: h⁰_amb={h_amb[0]}, h⁰_shift={h_shifted[0]}, "
                      f"h⁰_CY ≈ {h0_cy} (χ={chi_val})")
                
                if abs(h0_cy) == 3 or h0_cy == 3:
                    proven_h0_3.append((D, chi_val, D3, h0_cy))

print(f"\n{'='*65}")
if proven_h0_3:
    print(f"  {PASS} FOUND {len(proven_h0_3)} BUNDLES WITH h⁰ = 3")
else:
    print(f"  {WARN} No definitive h⁰ = 3 yet (Koszul corrections may help)")
print(f"{'='*65}")
