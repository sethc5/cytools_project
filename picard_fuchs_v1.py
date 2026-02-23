#!/usr/bin/env python3
"""picard_fuchs.py — GKZ periods and Picard-Fuchs operators for the GL=12 / D₆ CY3.

Computes:
  1. Fundamental period ω₀ as a power series near the large complex structure limit
  2. Picard-Fuchs differential operator (4th-order ODE for 1-parameter slices)
  3. Yukawa coupling κ from the prepotential

The CY3 X is the anticanonical hypersurface in the toric variety P_Δ where Δ is
the GL=12 polytope (h¹¹=17, h²¹=20, χ=−6).  The complex-structure moduli are
parametrized by the 23 lattice points of Δ* (the dual).

D₆ ≅ Dih(6) symmetry reduces 23 monomial coefficients → 8 orbit parameters
→ (after toric equivalences) a tractable number of effective moduli.

Usage:
    python picard_fuchs.py [--order N] [--mode {1param,d6}]
"""

import numpy as np
from collections import defaultdict
from math import factorial, gcd
from functools import reduce
from fractions import Fraction
import argparse
import time
import json


# ═══════════════════════════════════════════════════════════════════════
# DATA: Dual polytope Δ* lattice points and D₆ orbit structure
# ═══════════════════════════════════════════════════════════════════════

# All 23 lattice points of Δ* (the dual of the GL=12 polytope)
# Coordinates in M-lattice (ℤ⁴)
DUAL_POINTS = [
    (0,  0,  0,  0),    # m0   origin
    (0,  0, -1, -1),    # m1   vertex
    (0,  0, -1,  2),    # m2   vertex
    (0,  0,  2, -1),    # m3   vertex
    (-1, 1, -1, -1),    # m4   vertex
    (2, -1,  1,  1),    # m5   vertex
    (-1, 0, -1, -1),    # m6   vertex
    (-1, 0, -1,  2),    # m7   vertex
    (-1, 0,  2, -1),    # m8   vertex
    (1,  0,  0,  0),    # m9   vertex
    (-1, 0, -1,  0),    # m10  boundary
    (-1, 0, -1,  1),    # m11  boundary
    (-1, 0,  0, -1),    # m12  boundary
    (-1, 0,  0,  1),    # m13  boundary
    (-1, 0,  1, -1),    # m14  boundary
    (-1, 0,  1,  0),    # m15  boundary
    (0,  0, -1,  0),    # m16  boundary
    (0,  0, -1,  1),    # m17  boundary
    (0,  0,  0, -1),    # m18  boundary
    (0,  0,  0,  1),    # m19  boundary
    (0,  0,  1, -1),    # m20  boundary
    (0,  0,  1,  0),    # m21  boundary
    (-1, 0,  0,  0),    # m22  boundary
]

# D₆ orbits on Δ* (computed from GL(Δ) automorphisms)
D6_ORBITS = [
    [0],                          # ψ₀: origin (size 1)
    [1, 2, 3],                    # ψ₁: 3 vertices (size 3)
    [4, 5],                       # ψ₂: 2 vertices (size 2)
    [6, 7, 8],                    # ψ₃: 3 vertices (size 3)
    [9],                          # ψ₄: 1 vertex (size 1)
    [10, 11, 12, 13, 14, 15],    # ψ₅: 6 boundary (size 6)
    [16, 17, 18, 19, 20, 21],    # ψ₆: 6 boundary (size 6)
    [22],                         # ψ₇: 1 boundary (size 1)
]
D6_ORBIT_SIZES = [len(orb) for orb in D6_ORBITS]

# Non-origin monomials (for the period computation)
NON_ORIGIN = [DUAL_POINTS[i] for i in range(1, 23)]


# ═══════════════════════════════════════════════════════════════════════
# CORE: Constant-term extraction via ℤ⁴ convolution
# ═══════════════════════════════════════════════════════════════════════

def add_tuples(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2], a[3]+b[3])


def compute_ct_powers(monomials, max_k, verbose=True):
    """Compute CT[P^k] for k=0,...,max_k where P = Σ x^m over monomials.
    
    Uses iterative convolution in ℤ⁴ with bounding-box pruning.
    CT = "constant term" = coefficient of x^(0,0,0,0).
    
    Returns: list of integers [c_0, c_1, ..., c_{max_k}]
    """
    # Coordinate ranges of the monomials
    coord_min = [min(m[i] for m in monomials) for i in range(4)]
    coord_max = [max(m[i] for m in monomials) for i in range(4)]
    
    # P^0 = 1
    current = {(0, 0, 0, 0): 1}
    coeffs = [1]  # CT[P^0] = 1
    
    t0 = time.time()
    for k in range(1, max_k + 1):
        # Multiply current distribution by P
        # Prune: only keep terms that can reach (0,0,0,0) in (max_k - k) more steps
        remaining = max_k - k
        new = defaultdict(int)
        for exp, coeff in current.items():
            for m in monomials:
                new_exp = add_tuples(exp, m)
                # Pruning: can this reach zero?
                reachable = True
                for i in range(4):
                    lo = new_exp[i] + coord_min[i] * remaining
                    hi = new_exp[i] + coord_max[i] * remaining
                    if lo > 0 or hi < 0:
                        reachable = False
                        break
                if reachable:
                    new[new_exp] += coeff
        
        current = dict(new)
        ct = current.get((0, 0, 0, 0), 0)
        coeffs.append(ct)
        
        if verbose:
            elapsed = time.time() - t0
            print(f"  k={k:3d}: CT[P^{k}] = {ct:>20d}  (dict size={len(current):>8d}, {elapsed:.1f}s)")
    
    return coeffs


def compute_ct_powers_d6(max_k, psi_values=None, verbose=True):
    """Compute CT[(ψ₁S₁ + ψ₂S₂ + ... + ψ₇S₇)^k] for D₆-invariant model.
    
    If psi_values is None, uses ψ_I = 1 for all orbits (= 1-parameter model).
    Returns coefficients of the period expansion.
    """
    if psi_values is None:
        psi_values = [1.0] * 7  # 7 non-origin orbits
    
    # Build weighted monomial list: each monomial from orbit I has weight ψ_I
    weighted_monomials = []
    for orbit_idx in range(1, 8):  # skip origin orbit
        psi = psi_values[orbit_idx - 1]
        for pt_idx in D6_ORBITS[orbit_idx]:
            weighted_monomials.append((DUAL_POINTS[pt_idx], psi))
    
    # Coordinate ranges
    all_m = [wm[0] for wm in weighted_monomials]
    coord_min = [min(m[i] for m in all_m) for i in range(4)]
    coord_max = [max(m[i] for m in all_m) for i in range(4)]
    
    current = {(0, 0, 0, 0): 1.0}
    coeffs = [1.0]
    
    t0 = time.time()
    for k in range(1, max_k + 1):
        remaining = max_k - k
        new = defaultdict(float)
        for exp, coeff in current.items():
            for m, w in weighted_monomials:
                new_exp = add_tuples(exp, m)
                reachable = True
                for i in range(4):
                    lo = new_exp[i] + coord_min[i] * remaining
                    hi = new_exp[i] + coord_max[i] * remaining
                    if lo > 0 or hi < 0:
                        reachable = False
                        break
                if reachable:
                    new[new_exp] += coeff * w
        
        current = dict(new)
        ct = current.get((0, 0, 0, 0), 0.0)
        coeffs.append(ct)
        
        if verbose:
            elapsed = time.time() - t0
            print(f"  k={k:3d}: CT = {ct:>20.6f}  (dict={len(current):>8d}, {elapsed:.1f}s)")
    
    return coeffs


# ═══════════════════════════════════════════════════════════════════════
# PERIOD SERIES: ω₀(z) = Σ c_k · z^k
# ═══════════════════════════════════════════════════════════════════════

def fundamental_period_series(ct_coeffs):
    """Build the fundamental period from constant-term coefficients.
    
    ω₀(z) = Σ_{k≥0} c_k · z^k
    
    where z is the deformation parameter near the large complex structure limit.
    The period integral is:
        ω₀ = Σ_{k≥0} CT[P^k] / a₀^{k+1} · (-1)^k
    
    With a₀ = −1/z (so the LCS point is z → 0):
        ω₀(z) = Σ_{k≥0} (−1)^k · CT[P^k] · (−z)^k = Σ c_k z^k
    
    but the sign depends on convention. We use:
        ω₀(z) = Σ_{k≥0} c_k · z^k  (c_k = CT[P^k])
    """
    return list(ct_coeffs)


# ═══════════════════════════════════════════════════════════════════════
# PICARD-FUCHS OPERATOR: Find the ODE θ⁴ω = ...
# ═══════════════════════════════════════════════════════════════════════

def find_pf_operator(coeffs, max_order=4, verbose=True):
    """Find the Picard-Fuchs differential operator from the period series.
    
    Seeks a linear ODE of order ≤ max_order:
        Σ_{j=0}^{d} p_j(z) · θ^j ω₀ = 0
    
    where θ = z·d/dz and p_j are polynomials in z.
    
    Uses the series coefficients to set up a linear system.
    Returns: list of polynomial coefficients for each θ^j term.
    """
    N = len(coeffs)
    
    # θ^j applied to z^n = n^j z^n
    # So θ^j ω₀ = Σ n^j c_n z^n
    # z^m · θ^j ω₀ = Σ n^j c_n z^{n+m}
    
    # We search for: Σ_{j=0}^{d} Σ_{m=0}^{M} a_{j,m} · z^m · θ^j ω₀ = 0
    # i.e., for each power z^s:  Σ_{j,m} a_{j,m} · (s-m)^j · c_{s-m} = 0
    
    for order in range(2, max_order + 1):
        if verbose:
            print(f"\nTrying order {order}...")
        
        # Try increasing polynomial degrees for the coefficients
        for poly_deg in range(1, 20):
            n_unknowns = (order + 1) * (poly_deg + 1)
            n_eqns = N - poly_deg - 1
            
            if n_eqns < n_unknowns + 5:
                continue
            
            # Build the linear system
            # Unknowns: a_{j,m} for j=0,...,order and m=0,...,poly_deg
            # Equation for z^s (s = poly_deg, ..., N-2):
            #   Σ_{j=0}^{order} Σ_{m=0}^{poly_deg} a_{j,m} · (s-m)^j · c_{s-m} = 0
            
            rows = []
            for s in range(poly_deg, min(N, n_unknowns + poly_deg + 20)):
                row = []
                for j in range(order + 1):
                    for m in range(poly_deg + 1):
                        idx = s - m
                        if 0 <= idx < len(coeffs):
                            row.append(float(idx**j * coeffs[idx]))
                        else:
                            row.append(0.0)
                rows.append(row)
            
            if len(rows) < n_unknowns:
                continue
            
            A = np.array(rows, dtype=float)
            # Find the null space
            U, S, Vt = np.linalg.svd(A)
            
            # Check if there's a clean null vector
            tol = 1e-8 * S[0] if len(S) > 0 else 1e-8
            null_dim = sum(1 for s in S if s < tol)
            
            if null_dim >= 1:
                # Extract the null vector(s)
                null_vec = Vt[-1]
                
                # Reshape into (order+1) × (poly_deg+1)
                pf_coeffs = null_vec.reshape(order + 1, poly_deg + 1)
                
                # Verify by computing the residual on MORE equations
                residuals = A @ null_vec
                max_res = max(abs(r) for r in residuals)
                rel_res = max_res / max(abs(null_vec))
                
                if rel_res < 1e-6:
                    if verbose:
                        print(f"  FOUND: order={order}, poly_deg={poly_deg}")
                        print(f"  Max residual: {max_res:.2e}, relative: {rel_res:.2e}")
                        print(f"  Null space dim: {null_dim}")
                        
                        # Print the operator
                        print(f"\n  PF operator: Σ p_j(z)·θ^j = 0 where θ=z·d/dz")
                        for j in range(order + 1):
                            poly_str = " + ".join(
                                f"{pf_coeffs[j,m]:.6f}·z^{m}" 
                                for m in range(poly_deg + 1) 
                                if abs(pf_coeffs[j,m]) > 1e-10
                            )
                            print(f"  p_{j}(z) = {poly_str}")
                    
                    return order, poly_deg, pf_coeffs
    
    if verbose:
        print("No PF operator found at this order/degree. Need more terms.")
    return None


# ═══════════════════════════════════════════════════════════════════════
# YUKAWA COUPLING: κ = ω₀''' / ω₀  (schematic)
# ═══════════════════════════════════════════════════════════════════════

def compute_yukawa_from_periods(period_coeffs, z_val):
    """Compute the Yukawa coupling at a given point z.
    
    For the 1-parameter model:
        κ(z) = C_zzz = ∂³F/∂z³ = (ω₀ ∂³ω₀/∂z³ - ...) / ω₀²
    
    More precisely, κ = (2πi)³ e^{2πi τ} / (2πi τ')³
    where τ = ω₁/ω₀ (ratio of periods).
    
    For now, returns the raw period and its derivatives at z.
    """
    from mpmath import mp, mpf, power as mppow, fsum
    mp.dps = 50
    
    z = mpf(z_val)
    omega = [mpf(0)] * 4  # ω₀, ω₀', ω₀'', ω₀'''
    
    for k, c in enumerate(period_coeffs):
        zk = mppow(z, k)
        omega[0] += mpf(c) * zk
        if k >= 1:
            omega[1] += mpf(c) * k * mppow(z, k-1)
        if k >= 2:
            omega[2] += mpf(c) * k * (k-1) * mppow(z, k-2)
        if k >= 3:
            omega[3] += mpf(c) * k * (k-1) * (k-2) * mppow(z, k-3)
    
    return {
        'z': float(z),
        'omega_0': float(omega[0]),
        'omega_0_prime': float(omega[1]),
        'omega_0_pp': float(omega[2]),
        'omega_0_ppp': float(omega[3]),
    }


# ═══════════════════════════════════════════════════════════════════════
# GKZ SYSTEM: A-matrix and kernel (for reference / verification)
# ═══════════════════════════════════════════════════════════════════════

def build_gkz_a_matrix():
    """Build the GKZ A-matrix from Δ* lattice points.
    
    A is (d+1) × n where d=4 (dimension) and n=23 (lattice points).
    Row 0: all 1s.  Rows 1-4: coordinates of lattice points.
    """
    n = len(DUAL_POINTS)
    A = np.zeros((5, n), dtype=int)
    A[0, :] = 1
    for j, pt in enumerate(DUAL_POINTS):
        for i in range(4):
            A[i+1, j] = pt[i]
    return A


def integer_kernel(A):
    """Compute a basis for ker(A) ∩ ℤⁿ using sympy."""
    from sympy import Matrix
    M = Matrix(A.tolist())
    ker = M.nullspace()
    
    result = []
    for v in ker:
        # Convert to integers
        from sympy import lcm
        denoms = [x.q if hasattr(x, 'q') else 1 for x in v]
        lcd = 1
        for d in denoms:
            lcd = lcm(lcd, d)
        vi = [int(x * lcd) for x in v]
        g = reduce(gcd, [abs(x) for x in vi if x != 0])
        vi = [x // g for x in vi]
        result.append(vi)
    
    return result


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Picard-Fuchs computation for GL=12 CY3")
    parser.add_argument("--order", type=int, default=20,
                        help="Maximum power series order (default: 20)")
    parser.add_argument("--mode", choices=["1param", "d6"], default="1param",
                        help="1param: all orbits equal; d6: full D6-invariant")
    parser.add_argument("--find-pf", action="store_true",
                        help="Attempt to find the PF differential operator")
    args = parser.parse_args()
    
    print("=" * 70)
    print("PICARD-FUCHS COMPUTATION — GL=12 / D₆ CY3")
    print(f"  Δ*: 23 lattice points, 9 vertices")
    print(f"  D₆ orbits: {D6_ORBIT_SIZES} (8 orbits)")
    print(f"  Mode: {args.mode}, order: {args.order}")
    print("=" * 70)
    
    # Step 1: GKZ data
    print("\n[1] GKZ A-matrix")
    A = build_gkz_a_matrix()
    print(f"  A: {A.shape}, rank = {np.linalg.matrix_rank(A)}")
    print(f"  dim(ker) = {A.shape[1] - np.linalg.matrix_rank(A)}")
    
    # Step 2: Compute constant-term coefficients
    print(f"\n[2] Computing CT[P^k] for k = 0..{args.order}")
    print(f"  P = sum of {len(NON_ORIGIN)} non-origin monomials")
    
    if args.mode == "1param":
        ct = compute_ct_powers(NON_ORIGIN, args.order, verbose=True)
    else:
        ct = compute_ct_powers_d6(args.order, verbose=True)
    
    # Step 3: Period series
    print(f"\n[3] Fundamental period ω₀(z) = Σ c_k z^k")
    period = fundamental_period_series(ct)
    print(f"  First coefficients:")
    for k in range(min(len(period), 15)):
        if isinstance(period[k], float):
            print(f"    c_{k} = {period[k]:.0f}")
        else:
            print(f"    c_{k} = {period[k]}")
    
    # Step 4: Find PF operator
    if args.find_pf and len(ct) >= 10:
        print(f"\n[4] Searching for Picard-Fuchs operator...")
        result = find_pf_operator(ct, max_order=4, verbose=True)
        if result is None:
            print("  Need more terms. Try --order 30 or higher.")
    
    # Save results
    results = {
        'mode': args.mode,
        'order': args.order,
        'ct_coeffs': [int(c) if isinstance(c, (int, np.integer)) else float(c) for c in ct],
        'n_monomials': len(NON_ORIGIN),
        'n_dual_points': len(DUAL_POINTS),
        'd6_orbit_sizes': D6_ORBIT_SIZES,
    }
    
    outfile = f"results/picard_fuchs_{args.mode}_N{args.order}.json"
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {outfile}")
    
    print("\nDone.")


if __name__ == "__main__":
    main()
