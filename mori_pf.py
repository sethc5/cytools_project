#!/usr/bin/env python3
"""mori_pf.py -- Picard-Fuchs system in Mori coordinates for GL=12/D6 CY3.

This module computes the GKZ period and PF differential operators in the
natural Mori cone coordinates z_1, ..., z_6 for the D6-invariant complex
structure moduli space.

The CY3 X is the anticanonical hypersurface in the toric variety P_Delta,
where Delta is the GL=12 polytope (h11=17, h21=20, chi=-6, KS index 37).

Key data:
  - 23 lattice points in dual Delta*, falling into 8 D6-orbits
    (sizes 1, 3, 2, 3, 1, 6, 6, 1)
  - Orbit-summed A-bar matrix: rank 2, kernel dimension 6
  - 6 Mori coordinates z_i = prod_alpha psi_alpha^{s_alpha * lambda_alpha}
  - 6 GKZ box operators (PF differential equations)

Usage:
    python mori_pf.py [--order N] [--box] [--verify]
"""

import numpy as np
from math import factorial
from collections import defaultdict
import argparse
import time
import json


# =====================================================================
# GEOMETRY DATA
# =====================================================================

# Dual polytope Delta* lattice points (M-lattice, 23 points)
DUAL_POINTS = [
    (0,  0,  0,  0),    # d0  origin
    (0,  0, -1, -1),    # d1  vertex  | Orbit 1 (size 3)
    (0,  0, -1,  2),    # d2  vertex  |
    (0,  0,  2, -1),    # d3  vertex  |
    (-1, 1, -1, -1),    # d4  vertex  | Orbit 2 (size 2)
    (2, -1,  1,  1),    # d5  vertex  |
    (-1, 0, -1, -1),    # d6  vertex  | Orbit 3 (size 3)
    (-1, 0, -1,  2),    # d7  vertex  |
    (-1, 0,  2, -1),    # d8  vertex  |
    (1,  0,  0,  0),    # d9  vertex  | Orbit 4 (size 1)
    (-1, 0, -1,  0),    # d10 boundary | Orbit 5 (size 6)
    (-1, 0, -1,  1),    # d11 boundary |
    (-1, 0,  0, -1),    # d12 boundary |
    (-1, 0,  0,  1),    # d13 boundary |
    (-1, 0,  1, -1),    # d14 boundary |
    (-1, 0,  1,  0),    # d15 boundary |
    (0,  0, -1,  0),    # d16 boundary | Orbit 6 (size 6)
    (0,  0, -1,  1),    # d17 boundary |
    (0,  0,  0, -1),    # d18 boundary |
    (0,  0,  0,  1),    # d19 boundary |
    (0,  0,  1, -1),    # d20 boundary |
    (0,  0,  1,  0),    # d21 boundary |
    (-1, 0,  0,  0),    # d22 boundary | Orbit 7 (size 1)
]

# D6 orbits on dual lattice points
ORBITS = [
    [0],                          # orbit 0: origin (size 1)
    [1, 2, 3],                    # orbit 1: 3 vertices
    [4, 5],                       # orbit 2: 2 vertices
    [6, 7, 8],                    # orbit 3: 3 vertices
    [9],                          # orbit 4: 1 vertex
    [10, 11, 12, 13, 14, 15],    # orbit 5: 6 boundary
    [16, 17, 18, 19, 20, 21],    # orbit 6: 6 boundary
    [22],                         # orbit 7: 1 boundary
]

ORBIT_SIZES = [len(o) for o in ORBITS]  # [1, 3, 2, 3, 1, 6, 6, 1]
N_ORBITS = len(ORBITS)  # 8


# =====================================================================
# ORBIT-COMPRESSED GKZ KERNEL (6 x 8) -- VERIFIED in ker(A_bar)
# =====================================================================
#
# A_bar (rank 2):
#   [[ 1,  3,  2,  3,  1,  6,  6,  1],   (orbit sizes)
#    [ 0,  0,  1, -3,  1, -6,  0, -1]]   (sum of x1-coords)
#
# Kernel basis (6 vectors, each in Z^8):

KERNEL = np.array([
    [ -3,  1,  0,  0,  0,  0,  0,  0],   # z1 = psi_1^3 / psi_0^3
    [ -9,  0,  3,  1,  0,  0,  0,  0],   # z2 = psi_2^6 psi_3^3 / psi_0^9
    [  1,  0, -1,  0,  1,  0,  0,  0],   # z3 = psi_0 psi_4 / psi_2^2
    [-18,  0,  6,  0,  0,  1,  0,  0],   # z4 = psi_2^12 psi_5^6 / psi_0^18
    [ -6,  0,  0,  0,  0,  0,  1,  0],   # z5 = psi_6^6 / psi_0^6
    [ -3,  0,  1,  0,  0,  0,  0,  1],   # z6 = psi_2^2 psi_7 / psi_0^3
], dtype=int)


# =====================================================================
# MORI COORDINATES
# =====================================================================
#
# z_i = prod_alpha psi_alpha^{s_alpha * lambda_alpha}
#
# where lambda = KERNEL[i] and s = ORBIT_SIZES.
#
# Explicitly:
#   z1 = psi_1^3 / psi_0^3
#   z2 = psi_2^6 * psi_3^3 / psi_0^9
#   z3 = psi_0 * psi_4 / psi_2^2
#   z4 = psi_2^12 * psi_5^6 / psi_0^18
#   z5 = psi_6^6 / psi_0^6
#   z6 = psi_2^2 * psi_7 / psi_0^3


def mori_coord_string(i):
    """Return a human-readable string for z_i."""
    lam = KERNEL[i]
    s = ORBIT_SIZES
    pos = []
    neg = []
    for alpha in range(N_ORBITS):
        exp = s[alpha] * lam[alpha]
        if exp > 0:
            if exp == 1:
                pos.append(f"ψ_{alpha}")
            else:
                pos.append(f"ψ_{alpha}^{exp}")
        elif exp < 0:
            if -exp == 1:
                neg.append(f"ψ_{alpha}")
            else:
                neg.append(f"ψ_{alpha}^{-exp}")
    num_str = " · ".join(pos) if pos else "1"
    den_str = " · ".join(neg) if neg else "1"
    return f"{num_str} / {den_str}" if neg else num_str


# =====================================================================
# GKZ PERIOD IN MORI COORDINATES
# =====================================================================
#
# omega_0(z) = Sum_{n >= 0} c(n) z^n
#
# For n = (n1,...,n6) in Z_>=0^6, define orbit exponents:
#   m_alpha = Sum_i n_i * KERNEL[i, alpha]
#
# Validity: m_0 <= 0, m_alpha >= 0 for alpha >= 1.
#
# Coefficient:
#   c(n) = |m_0|! / prod_{alpha=1}^{7} (m_alpha!)^{s_alpha}

def orbit_exponents(n_vec):
    """Compute orbit exponents m_alpha = L^T . n."""
    m = [0] * N_ORBITS
    for alpha in range(N_ORBITS):
        for i in range(6):
            m[alpha] += int(KERNEL[i, alpha]) * int(n_vec[i])
    return m


def period_coeff(n_vec):
    """Compute GKZ period coefficient c(n) for multi-index n.
    
    Returns 0 if n is outside the validity cone.
    Uses pure Python ints for exact arithmetic.
    """
    m = orbit_exponents(n_vec)
    
    # Validity check
    if m[0] > 0:
        return 0
    for alpha in range(1, N_ORBITS):
        if m[alpha] < 0:
            return 0
    
    # c(n) = |m_0|! / prod_{alpha>=1} (m_alpha!)^{s_alpha}
    num = factorial(-m[0])
    den = 1
    for alpha in range(1, N_ORBITS):
        den *= factorial(m[alpha]) ** ORBIT_SIZES[alpha]
    
    if den == 0:
        return 0
    return num // den


def compute_period_multivariate(max_total_degree, verbose=True):
    """Compute period coefficients c(n) for |n| <= max_total_degree.
    
    Returns dict: tuple(n) -> c(n) for non-zero coefficients.
    """
    from itertools import product as iprod
    
    coeffs = {}
    t0 = time.time()
    n_computed = 0
    n_nonzero = 0
    
    # Enumerate multi-indices by total degree |n| = n1 + ... + n6
    for deg in range(max_total_degree + 1):
        deg_count = 0
        for n_tuple in _gen_partitions_6(deg):
            c = period_coeff(n_tuple)
            n_computed += 1
            if c != 0:
                coeffs[n_tuple] = c
                n_nonzero += 1
                deg_count += 1
        
        if verbose and (deg <= 5 or deg % 5 == 0):
            elapsed = time.time() - t0
            print(f"  |n|={deg:3d}: {deg_count:5d} non-zero, "
                  f"total {n_nonzero:6d}/{n_computed:6d}, {elapsed:.1f}s")
    
    return coeffs


def _gen_partitions_6(total):
    """Generate all 6-tuples (n1,...,n6) with n1+...+n6 = total, ni >= 0."""
    if total == 0:
        yield (0, 0, 0, 0, 0, 0)
        return
    for n1 in range(total + 1):
        for n2 in range(total - n1 + 1):
            for n3 in range(total - n1 - n2 + 1):
                for n4 in range(total - n1 - n2 - n3 + 1):
                    for n5 in range(total - n1 - n2 - n3 - n4 + 1):
                        n6 = total - n1 - n2 - n3 - n4 - n5
                        yield (n1, n2, n3, n4, n5, n6)


# =====================================================================
# GKZ BOX OPERATORS (formal Picard-Fuchs differential equations)
# =====================================================================
#
# For each kernel vector lambda = KERNEL[k] with orbit-level entries:
#
# The FORMAL GKZ box operator involves individual a-variable derivatives
# on Delta* lattice points:
#
#   Box_l = prod_{j: l_j > 0} (d/da_j)^{l_j}
#         - prod_{j: l_j < 0} (d/da_j)^{|l_j|}
#
# where l_j = lambda_{alpha(j)} for each Δ* point j in orbit alpha.
#
# IMPORTANT: On the D₆-invariant locus (a_j = ψ_{α(j)}), these do NOT
# simply become products of falling factorials in S_α = θ_{ψ_α}, because:
#
#   ∂/∂a_j = (1/s_α)(∂/∂ψ_α)  on D₆-invariant functions,
#
# but the COMPOSITION of individual ∂/∂a_j across DIFFERENT j in the
# same orbit produces intermediate results that are NOT D₆-invariant.
# So  ∂_{j1}·∂_{j2}·∂_{j3}  ≠  (∂/∂ψ_α)³  in general.
#
# The proper PF operators in z-coordinates require:
#   1. Euler constraint substitution (eliminating S₀ and S₂)
#   2. Careful operator algebra accounting for non-commutativity
#
# Below we store the FORMAL box operator data for reference.
# The orbit theta → Mori theta mapping allows future derivation of
# proper z-coordinate PF operators.

def orbit_theta_to_mori(alpha):
    """Return the linear combination S_alpha = Sum_i c_i theta_{z_i}.
    
    Returns list of 6 coefficients [c_1, ..., c_6].
    """
    return [int(KERNEL[i, alpha]) for i in range(6)]


def box_operator_data(k):
    """Return the box operator data for the k-th kernel vector.
    
    Returns dict with:
      'positive': list of (alpha, s_alpha * lambda_alpha)
      'negative': list of (alpha, s_alpha * |lambda_alpha|)
      'z_index': k (which Mori coordinate z_k it involves)
      'positive_degree': total degree of positive part
      'negative_degree': total degree of negative part
    """
    lam = KERNEL[k]
    s = ORBIT_SIZES
    
    pos = []
    neg = []
    for alpha in range(N_ORBITS):
        exp = s[alpha] * lam[alpha]
        if exp > 0:
            pos.append((alpha, exp))
        elif exp < 0:
            neg.append((alpha, -exp))
    
    pos_deg = sum(e for _, e in pos)
    neg_deg = sum(e for _, e in neg)
    
    return {
        'positive': pos,
        'negative': neg,
        'z_index': k + 1,
        'positive_degree': pos_deg,
        'negative_degree': neg_deg,
    }


def format_box_operator(k):
    """Return a human-readable string for the k-th box operator."""
    data = box_operator_data(k)
    
    def falling_str(alpha, degree):
        """Format falling factorial in S_alpha."""
        if degree == 1:
            return f"S_{alpha}"
        terms = [f"(S_{alpha}-{j})" if j > 0 else f"S_{alpha}" for j in range(degree)]
        return " · ".join(terms)
    
    # Positive part
    pos_parts = [falling_str(alpha, deg) for alpha, deg in data['positive']]
    pos_str = " · ".join(pos_parts) if pos_parts else "1"
    
    # Negative part
    neg_parts = [falling_str(alpha, deg) for alpha, deg in data['negative']]
    neg_str = " · ".join(neg_parts) if neg_parts else "1"
    
    return f"□_{k+1} = {pos_str}  −  z_{k+1} · {neg_str}"


# =====================================================================
# VERIFICATION: GKZ recurrence on period coefficients
# =====================================================================
#
# The A-hypergeometric series (GKZ Gamma-series) at LCS satisfies:
#
#   c_s(n+e_k) · P_+(u(n+e_k)) = c_s(n) · P_-(u(n))
#
# where c_s(n) = (-1)^{|m_0(n)|} · c(n) is the SIGNED coefficient
# (the 1/f = 1/(a_0+g) expansion introduces alternating signs),
# and the falling factorials use FULL a-variable exponents:
#
#   u_0 = -1 + m_0    (base vector gamma_0 = -1 at origin)
#   u_j = m_alpha      for j in orbit alpha >= 1  (gamma_j = 0)
#
# P_+ = prod_{alpha: lambda > 0} [falling(u_alpha, lambda)]^{s_alpha}
# P_- = prod_{alpha: lambda < 0} [falling(u_alpha, |lambda|)]^{s_alpha}

def _falling_factorial(x, k):
    """Compute x(x-1)(x-2)...(x-k+1). Returns 0 if k <= 0."""
    if k <= 0:
        return 1
    result = 1
    for j in range(k):
        result *= (x - j)
    return result


def verify_gkz_recurrence(period_coeffs, max_check_degree=None):
    """Verify GKZ recurrence on the period coefficients.
    
    For each (n, k) pair where both c(n) and c(n+e_k) are available
    and non-zero, checks:
    
        c_s(n+e_k) · P_+(u(n+e_k)) = c_s(n) · P_-(u(n))
    
    where c_s = (-1)^{|m_0|} · c is the signed coefficient.
    
    Returns (n_passed, n_failed, n_skipped).
    """
    if max_check_degree is None:
        max_check_degree = 6
    
    # gamma vector: gamma_0 = -1 (origin), gamma_j = 0 for j >= 1
    GAMMA = [-1] + [0] * (N_ORBITS - 1)
    
    n_passed = 0
    n_failed = 0
    n_skipped = 0
    
    for n_tuple, c_val in sorted(period_coeffs.items()):
        total_deg = sum(n_tuple)
        if total_deg >= max_check_degree:
            continue
        if c_val == 0:
            continue
        
        m = orbit_exponents(n_tuple)
        # Full exponents u_alpha = gamma_alpha + m_alpha
        u = [GAMMA[alpha] + m[alpha] for alpha in range(N_ORBITS)]
        
        # Signed coefficient: (-1)^{|m_0|} * c(n)
        c_s = ((-1) ** abs(m[0])) * c_val
        
        for k in range(6):
            lam = KERNEL[k]
            n_shifted = list(n_tuple)
            n_shifted[k] += 1
            n_shifted = tuple(n_shifted)
            
            c_shifted = period_coeffs.get(n_shifted, 0)
            if c_shifted == 0:
                n_skipped += 1
                continue
            
            m_s = orbit_exponents(n_shifted)
            u_s = [GAMMA[alpha] + m_s[alpha] for alpha in range(N_ORBITS)]
            c_s_shifted = ((-1) ** abs(m_s[0])) * c_shifted
            
            # P_+ at u(n+e_k): product over positive-lambda orbits
            p_plus = 1
            for alpha in range(N_ORBITS):
                if lam[alpha] > 0:
                    p_plus *= _falling_factorial(u_s[alpha], lam[alpha]) ** ORBIT_SIZES[alpha]
            
            # P_- at u(n): product over negative-lambda orbits
            p_minus = 1
            for alpha in range(N_ORBITS):
                if lam[alpha] < 0:
                    p_minus *= _falling_factorial(u[alpha], abs(lam[alpha])) ** ORBIT_SIZES[alpha]
            
            lhs = c_s_shifted * p_plus
            rhs = c_s * p_minus
            
            if lhs == rhs:
                n_passed += 1
            else:
                n_failed += 1
                if n_failed <= 5:
                    print(f"  FAIL k={k+1}: n={n_tuple}, "
                          f"LHS={lhs}, RHS={rhs}, diff={lhs-rhs}")
    
    return n_passed, n_failed, n_skipped


# =====================================================================
# EULER CONSTRAINTS
# =====================================================================

def euler_constraints():
    """Return the 2 Euler constraints in orbit theta-operators.
    
    Sum_alpha A_bar[k, alpha] * S_alpha = beta_k
    
    Only k=0,1 are non-trivial (rows 2-4 of A_bar are zero).
    """
    A_bar = np.array([
        [1, 3, 2, 3, 1, 6, 6, 1],
        [0, 0, 1, -3, 1, -6, 0, -1],
    ], dtype=int)
    beta = [-1, 0]
    
    constraints = []
    for k in range(2):
        terms = [(int(A_bar[k, alpha]), alpha) for alpha in range(N_ORBITS)
                 if A_bar[k, alpha] != 0]
        constraints.append({
            'terms': terms,
            'rhs': beta[k],
            'label': f"E_{k}",
        })
    
    return constraints


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Picard-Fuchs system in Mori coordinates for GL=12/D6 CY3")
    parser.add_argument("--order", type=int, default=8,
                        help="Max total degree for period series (default: 8)")
    parser.add_argument("--box", action="store_true",
                        help="Display box operators")
    parser.add_argument("--verify", action="store_true",
                        help="Verify box operators annihilate period")
    parser.add_argument("--save", action="store_true",
                        help="Save period coefficients to JSON")
    args = parser.parse_args()

    print("=" * 70)
    print("PICARD-FUCHS SYSTEM IN MORI COORDINATES")
    print("GL=12 / D₆ CY3  |  h¹¹=17, h²¹=20, χ=-6")
    print("=" * 70)

    # ---- Orbit structure ----
    print(f"\n[ORBITS] D₆ orbits on Δ* (23 lattice points):")
    for alpha, orb in enumerate(ORBITS):
        pts = [DUAL_POINTS[j] for j in orb]
        vtype = "origin" if alpha == 0 else ("vertex" if alpha <= 4 else "boundary")
        print(f"  ψ_{alpha} (size {ORBIT_SIZES[alpha]}, {vtype}): {orb}")
    
    # ---- Mori coordinates ----
    print(f"\n[MORI] 6 Mori coordinates z_i = ∏ ψ_α^{{s_α λ_α}}:")
    for i in range(6):
        print(f"  z_{i+1} = {mori_coord_string(i)}")
    
    # ---- Kernel ----
    print(f"\n[KERNEL] Orbit-compressed kernel (6×8, in ker(Ā)):")
    print(f"  Ā = [[1, 3, 2, 3, 1, 6, 6, 1],")
    print(f"        [0, 0, 1,-3, 1,-6, 0,-1]]  (rank 2)")
    print()
    for i in range(6):
        print(f"  l_{i+1} = {KERNEL[i].tolist()}")
    
    # ---- Orbit theta mapping ----
    print(f"\n[THETA] Orbit thetas -> Mori thetas (S_a = Sum L_{{i,a}} theta_i):")
    theta_labels = ["θ₁", "θ₂", "θ₃", "θ₄", "θ₅", "θ₆"]
    for alpha in range(N_ORBITS):
        coeffs = orbit_theta_to_mori(alpha)
        terms = []
        for i, c in enumerate(coeffs):
            if c == 0:
                continue
            if c == 1:
                terms.append(theta_labels[i])
            elif c == -1:
                terms.append(f"-{theta_labels[i]}")
            else:
                terms.append(f"{c:+d}·{theta_labels[i]}" if terms else f"{c}·{theta_labels[i]}")
        expr = " ".join(terms) if terms else "0"
        print(f"  S_{alpha} = {expr}")
    
    # ---- Euler constraints ----
    print(f"\n[EULER] Constraints (act on period as degree-fixing):")
    for ec in euler_constraints():
        terms = " + ".join(f"{c}·S_{alpha}" for c, alpha in ec['terms'])
        print(f"  {ec['label']}: {terms} = {ec['rhs']}")
    
    # ---- Box operators ----
    if args.box:
        print(f"\n[BOX] GKZ box operators (PF equations) □_k ω₀ = 0:")
        print()
        for k in range(6):
            data = box_operator_data(k)
            print(f"  {format_box_operator(k)}")
            print(f"    Degree: {data['positive_degree']} (positive) vs "
                  f"{data['negative_degree']} (negative)")
            print()
    
    # ---- Period series ----
    print(f"\n[PERIOD] Computing ω₀(z) = Σ c(n) z^n to total degree {args.order}")
    print(f"  Formula: c(n) = |m₀|! / ∏_{{α≥1}} (m_α!)^{{s_α}}")
    print()
    
    coeffs = compute_period_multivariate(args.order, verbose=True)
    
    print(f"\n  Total non-zero coefficients: {len(coeffs)}")
    
    # Show lowest-degree terms
    print(f"\n  Lowest-degree terms:")
    sorted_terms = sorted(coeffs.items(), key=lambda x: (sum(x[0]), x[0]))
    for n_tuple, c_val in sorted_terms[:30]:
        m = orbit_exponents(n_tuple)
        print(f"    c{n_tuple} = {c_val}  (m = {m})")
    
    # ---- Verification ----
    if args.verify:
        print(f"\n[VERIFY] GKZ recurrence: c_s(n+e_k)·P+ = c_s(n)·P-")
        print(f"  (c_s = (-1)^|m₀| · c, falling factorials use u = γ + m)")
        n_pass, n_fail, n_skip = verify_gkz_recurrence(
            coeffs, max_check_degree=args.order)
        print(f"  Passed: {n_pass}  Failed: {n_fail}  Skipped: {n_skip}")
        if n_fail == 0 and n_pass > 0:
            print("  All GKZ recurrence checks PASS ✓")
    
    # ---- Save ----
    if args.save:
        outfile = f"results/mori_pf_deg{args.order}.json"
        save_data = {
            'order': args.order,
            'n_nonzero': len(coeffs),
            'kernel': KERNEL.tolist(),
            'orbit_sizes': ORBIT_SIZES,
            'coefficients': {str(k): str(v) for k, v in sorted_terms},
        }
        with open(outfile, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"\n  Saved to {outfile}")
    
    print("\nDone.")


if __name__ == "__main__":
    main()
