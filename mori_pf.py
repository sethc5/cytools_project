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
# EXPLICIT PF OPERATORS IN θ-COORDINATES
# =====================================================================
#
# Each S_alpha = sum_i KERNEL[i, alpha] * theta_i
# so the box operators become polynomial differential operators in
# theta_1, ..., theta_6 (where theta_i = z_i d/dz_i).
#
# Box_k = prod_{alpha: l>0} (S_alpha)(S_alpha-1)...(S_alpha - s_alpha*l_alpha + 1)
#       - z_{k+1} * prod_{alpha: l<0} (S_alpha)(S_alpha-1)...(S_alpha - s_alpha*|l_alpha| + 1)
#
# The falling factorial of an operator F of degree d is:
#   F^(d) = F(F-1)(F-2)...(F-d+1)

def format_s_expr(alpha, varname='θ'):
    """Pretty-print S_alpha = sum_i L[i,alpha] theta_i."""
    coeffs = [int(KERNEL[i, alpha]) for i in range(6)]
    terms = []
    for i, c in enumerate(coeffs):
        if c == 0:
            continue
        var = f"{varname}_{i+1}"
        if not terms:
            if c == 1:
                terms.append(var)
            elif c == -1:
                terms.append(f"-{var}")
            else:
                terms.append(f"{c}{var}")
        else:
            if c == 1:
                terms.append(f"+ {var}")
            elif c == -1:
                terms.append(f"- {var}")
            elif c > 0:
                terms.append(f"+ {c}{var}")
            else:
                terms.append(f"- {-c}{var}")
    return ' '.join(terms) if terms else '0'


def _falling_op_str(S_str, degree):
    """Format falling factorial: S(S-1)(S-2)...(S-degree+1)."""
    if degree == 0:
        return '1'
    parts = []
    for j in range(degree):
        if j == 0:
            parts.append(f"({S_str})")
        else:
            parts.append(f"({S_str} - {j})")
    return '·'.join(parts)


def print_pf_operators():
    """Print all 6 PF operators in explicit theta notation."""
    print("────────────────────────────────────────────────────────────────")
    print("  GKZ PF OPERATORS  □_k ω₀ = 0  in Mori θ-coordinates")
    print("  θᵢ = zᵢ ∂/∂zᵢ,   Sα = Σᵢ L[i,α] θᵢ")
    print("────────────────────────────────────────────────────────────────")
    print()

    A_bar = [[1, 3, 2, 3, 1, 6, 6, 1],
             [0, 0, 1,-3, 1,-6, 0,-1]]
    print("  Euler constraints (orbit theta-operators):")
    for row, rhs, label in zip(A_bar, [-1, 0], ['E₀', 'E₁']):
        terms = [f"{c}·S{a}" for a, c in enumerate(row) if c != 0]
        print(f"  {label}: {' + '.join(terms).replace('+ -','- ')} = {rhs}")
    print()
    print("  Orbit theta-operators in Mori coordinates:")
    for alpha in range(N_ORBITS):
        S_str = format_s_expr(alpha)
        print(f"  S{alpha} = {S_str}")
    print()

    for k in range(6):
        lam = KERNEL[k]
        s = ORBIT_SIZES

        pos_parts = []
        neg_parts = []
        total_pos_deg = 0
        total_neg_deg = 0
        for alpha in range(N_ORBITS):
            if lam[alpha] > 0:
                deg = s[alpha] * lam[alpha]
                total_pos_deg += deg
                S_str = format_s_expr(alpha)
                pos_parts.append(_falling_op_str(S_str, deg))
            elif lam[alpha] < 0:
                deg = s[alpha] * abs(lam[alpha])
                total_neg_deg += deg
                S_str = format_s_expr(alpha)
                neg_parts.append(_falling_op_str(S_str, deg))

        pos_str = '·'.join(pos_parts) if pos_parts else '1'
        neg_str = '·'.join(neg_parts) if neg_parts else '1'

        print(f"  □_{k+1}  [deg {total_neg_deg}]")
        print(f"    POS:  {pos_str}")
        print(f"    NEG:  z_{k+1} · {neg_str}")
        print(f"    □_{k+1} ω = 0  ⟺  POS·ω = NEG·ω")
        print()


# =====================================================================
# 1-PARAMETER SPECIALIZATION: z₁ = t, z₂=...=z₆ = 0
# =====================================================================
#
# Along the z₁-axis:
#   Only monomials n = (n₁, 0, 0, 0, 0, 0) contribute.
#   S₀ = -3θ₁,   S₁ = θ₁,   all other Sα = 0 on this slice.
#
# Box₁ reduces to the 3rd-order ODE (MUM at t=0):
#   θ³ ω = -t · (3θ+1)(3θ+2)(3θ+3) ω
#
# i.e., [θ³ + t(3θ+1)(3θ+2)(3θ+3)] ω_s = 0
#
# The SIGNED period (GKZ Gamma-series) on this slice is:
#   ω_s(t) = Σ_{n≥0} (-1)^n · (3n)! / (n!)³ · tⁿ
#           = Σ (-1)^n binom(3n,n) binom(2n,n) tⁿ
#
# The CORRECT ODE for the signed Gamma-series ω_s(t) = Σ (-1)^n (3n)!/n!³ t^n
# from the verified recurrence (n+1)³ c(n+1) + (3n+1)(3n+2)(3n+3) c(n) = 0 is:
#
#   [θ³ + t(3θ+1)(3θ+2)(3θ+3)] ω_s(t) = 0
#
# with MUM point (indicial roots s = 0, 0, 0) at t = 0.
#
# NOTE: An earlier version erroneously stated (θ+1)³ instead of θ³.
# In AESZ notation this is related to entry #1 (period of cubic in P²).

def compute_1param_series(max_n=20):
    """Compute ω_s(t) = Σ (-1)^n (3n)!/n!³ tⁿ on the z₁-slice."""
    coeffs = []
    for n in range(max_n + 1):
        c_unsigned = factorial(3*n) // (factorial(n)**3)
        c_signed = ((-1)**n) * c_unsigned
        coeffs.append((n, c_unsigned, c_signed))
    return coeffs


def derive_1param_ode():
    """Derive and print the 1-parameter PF ODE from Box₁ on z₁-slice.
    
    On z₁-slice: S₀ = -3θ, S₁ = θ, all other Sα = 0.
    
    Box₁ kernel: KERNEL[0] = [-3, 1, 0, 0, 0, 0, 0, 0]
    
    PF equation (derived from the recurrence of ω_s = Σ(-1)^n(3n)!/n!³ t^n):
        θ³ ω + t·(3θ+1)(3θ+2)(3θ+3) ω = 0
    
    This is a 3rd-order ODE at MUM (indicial roots 0, 0, 0).
    """
    print("────────────────────────────────────────────────────────────────")
    print("  1-PARAMETER SPECIALIZATION: z₁ = t, z₂=...=z₆ = 0")
    print("────────────────────────────────────────────────────────────────")
    print()
    print("  On this slice, only n = (n₁,0,0,0,0,0) terms survive:")
    print("    c(n₁) = (3n₁)! / (n₁!)³  [unsigned period coefficients]")
    print("    ω_s(t) = Σ (-1)^n · (3n)!/(n!)³ · tⁿ  [SIGNED Gamma-series]")
    print()

    # Print the first terms
    series = compute_1param_series(12)
    print("  Period coefficients (unsigned, up to n=12):")
    terms = [f"{c_u}" for _, c_u, _ in series]
    print("    " + ", ".join(terms[:10]))
    print()
    print("  Signed coefficients:")
    terms_s = [f"{c_s}" for _, _, c_s in series]
    print("    " + ", ".join(terms_s[:10]))
    print()

    # The PF ODE
    print("  PF ODE from the recurrence (θ = t d/dt):")
    print("    [θ³ + t·(3θ+1)(3θ+2)(3θ+3)] ω_s(t) = 0")
    print()
    print("  Indicial equation at t=0: s³ = 0  ⟹  s = 0,0,0  (MUM point)")
    print()
    print("  Expand (3θ+1)(3θ+2)(3θ+3) = 27(θ+1/3)(θ+2/3)(θ+1):")
    print("    θ³ + 27t·(θ+1/3)(θ+2/3)(θ+1) = 0")
    print()
    print("  Expanded form:")
    print("    (1+27t)θ³ + 54tθ² + 33tθ + 6t = 0")
    print()

    # Verify numerically from recurrence
    print("  Numerical verification of recurrence  c(n+1)/c(n):")
    print("    (n+1)³ c_s(n+1) = -(3n+1)(3n+2)(3n+3) c_s(n)")
    series_c = compute_1param_series(6)
    ok = True
    for i in range(len(series_c)-1):
        n, _, c_s_n = series_c[i]
        n1, _, c_s_n1 = series_c[i+1]
        lhs = (n+1)**3 * c_s_n1
        rhs = -(3*n+1)*(3*n+2)*(3*n+3) * c_s_n
        status = "✓" if lhs == rhs else f"✗ ({lhs} vs {rhs})"
        print(f"    n={n}: (n+1)³ c_s(n+1) = {lhs},  rhs = {rhs}  {status}")
        if lhs != rhs:
            ok = False
    if ok:
        print("    All recurrence checks PASS ✓")
    print()

    # Connection to known hypergeometric series
    print("  Hypergeometric form:")
    print("    Unsigned: Σ (3n)!/n!³ t^n = ₃F₂([1/3, 2/3, 1]; [1, 1]; 27t)")
    print("             (radius of convergence: |t| < 1/27)")
    print("    Signed:  Σ (-1)^n (3n)!/n!³ t^n = ₃F₂([1/3,2/3,1];[1,1];-27t)")
    print()
    print("  AESZ cross-reference:")
    print("    This is the period of the mirror family of degree-3 hypersurfaces")
    print("    in P² (elliptic curve family), embedded in the z₁-direction of")
    print("    the GL=12/D₆ moduli space. AESZ #1 in 2-variable Calabi-Yau tables.")


# =====================================================================
# LOGARITHMIC PERIODS AND MIRROR MAP
# =====================================================================
#
# The GKZ Gamma-series with shift parameter ρ in the i-th Mori direction:
#   c(n; ρ e_i) = Γ(1 - m₀(n+ρe_i)) / ∏_{α≥1} Γ(1 + m_α(n+ρe_i))^{s_α}
#
# Differentiating log c w.r.t. ρ at ρ=0:
#   h_i(n) = −L_{i,0} · H_{|m₀|} − Σ_{α≥1} s_α · L_{i,α} · H_{m_α}
#
# where H_n = Σ_{k=1}^n 1/k is the n-th harmonic number (H_0 = 0).
#
# The Euler-Mascheroni constant γ cancels due to the kernel condition
# Σ_α s_α L_{i,α} = 0 (row of Ā · l_i^T = 0).
#
# The i-th logarithmic period is:
#   ω_i(z) = ω₀(z) · log(z_i) + Σ_n c(n) · h_i(n) · z^n
#
# The mirror map (flat coordinate):
#   τ_i = ω_i / ω₀ = log(z_i) + g_i(z) / ω₀(z)
#
# where g_i(z) = Σ_n c(n) · h_i(n) · z^n.
#
# The "nome" variable: q_i = exp(τ_i) = z_i · exp(g_i/ω₀).

from fractions import Fraction


def harmonic_number(n):
    """Compute H_n = Σ_{k=1}^n 1/k as an exact Fraction. H_0 = 0."""
    return sum(Fraction(1, k) for k in range(1, n + 1))


def log_period_deriv(n_vec, i):
    """Compute h_i(n) = d/dρ log c(n + ρe_i)|_{ρ=0} as exact Fraction.
    
    Formula: h_i(n) = −L_{i,0}·H_{|m₀|} − Σ_{α≥1} s_α·L_{i,α}·H_{m_α}
    
    Returns 0 if c(n) = 0 (n outside validity cone).
    """
    m = orbit_exponents(n_vec)
    
    # Validity check (same as period_coeff)
    if m[0] > 0:
        return Fraction(0)
    for alpha in range(1, N_ORBITS):
        if m[alpha] < 0:
            return Fraction(0)
    
    h = Fraction(0)
    # Numerator contribution: −L_{i,0} · H_{|m₀|}
    h -= KERNEL[i, 0] * harmonic_number(abs(m[0]))
    # Denominator contributions: −s_α · L_{i,α} · H_{m_α}
    for alpha in range(1, N_ORBITS):
        h -= ORBIT_SIZES[alpha] * KERNEL[i, alpha] * harmonic_number(m[alpha])
    
    return h


def compute_log_period_1param(max_n=50):
    """Compute the logarithmic period correction g₁(t) on the z₁-axis.
    
    For ω_s(t) = Σ a_n t^n  (signed fundamental period),
    the log period is: ω₁(t) = ω₀(t)·log(t) + g₁(t)
    where g₁(t) = Σ_{n≥1} b_n t^n  and  b_n = a_n · h₁(n).
    
    On the z₁-axis, h₁(n) = 3(H_{3n} - H_n).
    
    Returns list of (n, a_n, b_n) tuples with exact Fraction values.
    """
    result = []
    for n in range(max_n + 1):
        a_n = ((-1)**n) * (factorial(3*n) // factorial(n)**3)
        if n == 0:
            b_n = Fraction(0)  # H_0 - H_0 = 0
        else:
            # h_1(n) = 3(H_{3n} - H_n)
            h_n = 3 * (harmonic_number(3*n) - harmonic_number(n))
            b_n = Fraction(a_n) * h_n
        result.append((n, Fraction(a_n), b_n))
    return result


def compute_mirror_map_1param(max_n=50, verbose=True):
    """Compute the mirror map q(t) = t · exp(g₁(t)/ω₀(t)) on the z₁-axis.
    
    Returns (q_coeffs, t_coeffs):
      q_coeffs: q(t) = Σ q_k t^k  (forward mirror map, q_1 = 1)
      t_coeffs: t(q) = Σ t_k q^k  (inverse mirror map, t_1 = 1)
    
    All computations in exact rational arithmetic.
    """
    log_data = compute_log_period_1param(max_n)
    
    # Extract power series coefficients as Fractions
    N = max_n + 1
    a = [Fraction(0)] * N  # ω₀ coefficients
    b = [Fraction(0)] * N  # g₁ coefficients
    for n, a_n, b_n in log_data:
        a[n] = a_n
        b[n] = b_n
    
    if verbose:
        print("  First 6 log-period correction coefficients b_n = a_n · h_1(n):")
        for n in range(min(6, N)):
            if n == 0:
                print(f"    n=0: b_0 = 0  (H_0 - H_0 = 0)")
            else:
                h_n = 3 * (harmonic_number(3*n) - harmonic_number(n))
                print(f"    n={n}: h_1({n}) = {h_n} = {float(h_n):.6f},  "
                      f"b_{n} = {b[n]} = {float(b[n]):.4f}")
        print()
    
    # Compute ratio g₁/ω₀ as power series: r(t) = g₁(t)/ω₀(t)
    # Then q(t) = t · exp(r(t))
    
    # Step 1: r(t) = g₁/ω₀ via power series division
    # g₁ = b[0] + b[1]t + ... , ω₀ = a[0] + a[1]t + ...
    # r = g₁ / ω₀, computed iteratively: r[n] = (b[n] - Σ_{k=0}^{n-1} r[k]·a[n-k]) / a[0]
    r = [Fraction(0)] * N
    for n in range(N):
        s = b[n]
        for k in range(n):
            s -= r[k] * a[n - k]
        r[n] = s / a[0]
    
    if verbose:
        print("  g₁/ω₀ ratio coefficients r_n (first 6):")
        for n in range(min(6, N)):
            print(f"    r_{n} = {r[n]} = {float(r[n]):.8f}")
        print()
    
    # Step 2: exp(r(t)) as power series
    # exp(r) = Σ e_n t^n, with e[0] = exp(r[0]) = exp(0) = 1
    # e[n] = (1/n) Σ_{k=1}^n k · r[k] · e[n-k]
    e = [Fraction(0)] * N
    e[0] = Fraction(1)  # r[0] = 0, so exp(r[0]) = 1
    for n in range(1, N):
        s = Fraction(0)
        for k in range(1, n + 1):
            if k < N:
                s += k * r[k] * e[n - k]
        e[n] = s / n
    
    # Step 3: q(t) = t · exp(r(t)), so q_coeffs[n] = e[n-1] for n >= 1
    q_coeffs = [Fraction(0)] * N
    for n in range(1, N):
        q_coeffs[n] = e[n - 1]
    
    if verbose:
        print("  Mirror map q(t) = t · exp(g₁/ω₀):")
        print("    q(t) = t", end="")
        for n in range(2, min(8, N)):
            c = q_coeffs[n]
            if c > 0:
                print(f" + {c}·t^{n}", end="")
            elif c < 0:
                print(f" - {-c}·t^{n}", end="")
        print(" + ...")
        print()
        print("    Numerical coefficients (first 15):")
        for n in range(1, min(16, N)):
            print(f"      q_{n} = {float(q_coeffs[n]):+.10f}  "
                  f"({q_coeffs[n]})")
        print()
    
    # Step 4: Invert q(t) to get t(q) by power series reversion
    # q = t + q_2 t^2 + q_3 t^3 + ...
    # t = q + t_2 q^2 + t_3 q^3 + ...
    # Using the standard inversion formula
    t_coeffs = [Fraction(0)] * N
    t_coeffs[1] = Fraction(1)
    for n in range(2, N):
        # t_n = -Σ_{k=2}^n q_k * [sum over partitions giving t^n from the substitution]
        # Iterative: substitute t = q + t_2 q^2 + ... into q = Σ q_k t^k
        # For each n, compute the coefficient of q^n in Σ q_k (t_1 q + t_2 q^2 + ...)^k
        # using previously computed t_1, ..., t_{n-1}
        s = Fraction(0)
        # Compute powers of the partial inverse t̂ = Σ_{j=1}^{n-1} t_j q^j
        # t̂^k has degree ≥ k, so only k ≤ n contribute to the q^n coefficient
        # power_coeffs[j] = coefficient of q^j in t̂^power
        # Initialize: t̂^1 = t̂
        # We need coeff of q^n in Σ_{k=1}^n q_k · t̂^k
        power_n = [Fraction(0)] * (n + 1)  # coeff of q^j in current power of t̂
        power_n[0] = Fraction(1)  # t̂^0 = 1
        for k in range(1, n + 1):
            # Multiply power_n by t̂ to get t̂^k
            new_power = [Fraction(0)] * (n + 1)
            for j1 in range(n + 1):
                if power_n[j1] == 0:
                    continue
                for j2 in range(1, n + 1):
                    if j2 >= len(t_coeffs) or t_coeffs[j2] == 0:
                        continue
                    j_sum = j1 + j2
                    if j_sum <= n:
                        new_power[j_sum] += power_n[j1] * t_coeffs[j2]
            power_n = new_power
            # Add q_k * coeff(q^n in t̂^k) to s
            if k < len(q_coeffs) and q_coeffs[k] != 0:
                s += q_coeffs[k] * power_n[n]
        # The equation is: s = q^n coefficient of q(t(q))
        # But q(t(q)) should be q, so: s = δ_{n,1}
        # For n ≥ 2: s + q_1 · t_n = 0 → t_n = -s  (since q_1 = 1)
        t_coeffs[n] = -s
    
    if verbose:
        print("  Inverse mirror map t(q) = Σ t_k q^k:")
        print("    t(q) = q", end="")
        for n in range(2, min(8, N)):
            c = t_coeffs[n]
            if c > 0:
                print(f" + {c}·q^{n}", end="")
            elif c < 0:
                print(f" - {-c}·q^{n}", end="")
        print(" + ...")
        print()
        print("    Numerical coefficients (first 15):")
        for n in range(1, min(16, N)):
            print(f"      t_{n} = {float(t_coeffs[n]):+.10f}  "
                  f"({t_coeffs[n]})")
        print()
    
    return q_coeffs, t_coeffs


def compute_log_period_coeff_multi(n_vec, i):
    """Compute h_i(n) for the i-th multi-parameter logarithmic period.
    
    Formula: h_i(n) = −L_{i,0}·H_{|m₀|} − Σ_{α≥1} s_α·L_{i,α}·H_{m_α}
    
    The i-th logarithmic period of the multivariate GKZ system:
      ω_i(z) = ω₀(z)·log(z_i) + Σ_n c(n)·h_i(n)·z^n
    
    Returns (c_val, h_val) where c_val = c(n) and h_val = h_i(n),
    both as exact Fractions. Returns (0, 0) if n is outside validity cone.
    """
    c_val = period_coeff(n_vec)
    if c_val == 0:
        return Fraction(0), Fraction(0)
    
    h_val = log_period_deriv(n_vec, i)
    return Fraction(c_val), h_val


def compute_log_periods_multi(max_total_degree, verbose=True):
    """Compute multi-parameter logarithmic period data to given total degree.
    
    For each non-zero period coefficient c(n), computes h_i(n) for all 6
    Mori directions i=0,...,5 (i.e., all 6 logarithmic periods).
    
    Returns dict: n_tuple -> (c(n), [h_0(n), h_1(n), ..., h_5(n)])
    """
    result = {}
    t0 = time.time()
    n_computed = 0
    
    for deg in range(max_total_degree + 1):
        deg_count = 0
        for n_tuple in _gen_partitions_6(deg):
            c = period_coeff(n_tuple)
            n_computed += 1
            if c != 0:
                h_vals = []
                for i in range(6):
                    h_vals.append(log_period_deriv(n_tuple, i))
                result[n_tuple] = (Fraction(c), h_vals)
                deg_count += 1
        
        if verbose and (deg <= 3 or deg % 2 == 0):
            elapsed = time.time() - t0
            print(f"  |n|={deg:3d}: {deg_count:5d} non-zero, "
                  f"total {len(result):6d}/{n_computed:6d}, {elapsed:.1f}s")
    
    return result


# =====================================================================
# ODE FACTORIZATION AND ELLIPTIC CURVE ANALYSIS (z₁-axis)
# =====================================================================
#
# The 3rd-order PF ODE on the z₁-axis FACTORS:
#
#   θ · [θ² + 27t(θ+1/3)(θ+2/3)] ω = 0
#
# PROOF: The operator product θ · L₂ where L₂ = θ² + 27t(θ+1/3)(θ+2/3):
#   θ · (27t P(θ) ω) = 27t(θ+1)P(θ) ω   [since θ(t·g) = t(θ+1)g]
#   So θ·L₂ = θ³ + 27t(θ+1)(θ+1/3)(θ+2/3) = θ³ + 27t(θ+1/3)(θ+2/3)(θ+1)
#   = θ³ + (3θ+1)(3θ+2)(3θ+3)·t = our ODE  ✓
#
# Equivalently: the 3rd-order recurrence n³c_n = -(3n-2)(3n-1)(3n)c_{n-1}
# is n times the 2nd-order recurrence n²c_n = -3(3n-1)(3n-2)c_{n-1}.
#
# CONSEQUENCES:
#   1. The z₁-axis is an ELLIPTIC CURVE family (cubic in ℙ²), not CY3
#   2. The period is ₂F₁(1/3, 2/3; 1; -27t) (Gauss hypergeometric)
#   3. Only TWO independent periods (ω₀, ω₁), plus the trivial constant
#   4. No CY3-type prepotential or GW invariants on this 1-parameter slice
#   5. The mirror map gives a Hauptmodul for Γ₀(3) (modular curve)
#
# HESSE PENCIL IDENTIFICATION:
#   The curve f = 0 in (ℂ*)² with f = 1 + ψ₁(x⁻¹y⁻¹ + x⁻¹y² + x²y⁻¹)
#   is equivalent to the Hesse pencil X³ + Y³ + Z³ = 3ψXYZ
#   via ψ = -1/(3ψ₁) = -ψ₀/(3ψ₁), so ψ³ = -1/(27z₁).
#
# j-INVARIANT:
#   j(ψ) = 27ψ³(ψ³+8)³/(ψ³-1)³    [Hesse pencil]
#   j(t) = (216t-1)³ / (t·(1+27t)³)  [in MUM coordinate t = z₁]
#
#   Special values:
#     t = 0:     j → ∞  (MUM/cusp, τ → i∞)
#     t = 1/216: j = 0  (equianharmonic, CM by ℤ[ω])
#     t = -1/27: j → ∞  (conifold, nodal cubic)
#
# WRONSKIAN:
#   W(ω₀, ω₁) = 1/(t·(1+27t))
#   Discriminant locus: Δ = 1+27t = 0 ⟺ t = -1/27


def compute_j_invariant(max_n=30, verbose=True):
    """Compute the j-invariant j(q) as a q-series on the z₁-axis.
    
    j(t) = (216t - 1)³ / (t · (1+27t)³)
    
    Substitutes t = t(q) (inverse mirror map) to get j(q).
    
    Returns list of Fraction coefficients j_k where j(q) = Σ j_k q^k 
    (starting from k = -1 for the leading 1/q pole).
    """
    # Get inverse mirror map t(q) = Σ t_k q^k
    _, t_coeffs = compute_mirror_map_1param(max_n, verbose=False)
    N = len(t_coeffs)
    
    # Compute numerator = (216t - 1)³ and denominator = t·(1+27t)³ as q-series
    
    # First compute (216t - 1) as q-series:
    # 216t - 1 = -1 + 216·t₁·q + 216·t₂·q² + ...
    lin = [Fraction(0)] * N
    lin[0] = Fraction(-1)
    for k in range(1, N):
        lin[k] = 216 * t_coeffs[k]
    
    # Cube it: (216t-1)³
    num = _poly_mul(_poly_mul(lin, lin, N), lin, N)
    
    # Compute (1+27t) as q-series
    one_plus_27t = [Fraction(0)] * N
    one_plus_27t[0] = Fraction(1)
    for k in range(1, N):
        one_plus_27t[k] = 27 * t_coeffs[k]
    
    # Cube it: (1+27t)³
    den_part = _poly_mul(_poly_mul(one_plus_27t, one_plus_27t, N), one_plus_27t, N)
    
    # Multiply by t: t·(1+27t)³ — this shifts by one power of q
    # t·(1+27t)³ = Σ_{k≥1} [Σ_{j=0}^{k-1} t_j · den_part_{k-1-j}] q^k ... hmm
    # Actually: (t·f)(q) has coeff of q^k = Σ t_j · f_{k-j} for j≥1
    # since t starts at q^1.
    #
    # We compute the series t·(1+27t)³ of degree ≥ 1:
    den_full = _poly_mul(t_coeffs, den_part, N)
    # den_full[0] = 0 (since t_coeffs[0] = 0)
    
    # j(q) = num / den_full
    # Leading terms: num ≈ (-1)³ + ... = -1 + O(q)
    # den_full ≈ t₁·q · 1 = q + O(q²)
    # So j ≈ -1/q + O(1), i.e. j has a simple pole at q = 0
    
    # To extract: write j(q) = j_{-1}/q + j_0 + j_1 q + ...
    # num = den_full · j(q)
    # At order q^k: num[k] = Σ_{m} den_full[k-m+1] · j_m  (shifted by pole)
    # j_{-1} = num[0] / den_full[1]
    # j_m = (num[m+1] - Σ_{k=-1}^{m-1} j_k · den_full[m+1-k]) / den_full[1]
    
    # j_m for m starting from -1:
    j_series = [Fraction(0)] * (N - 1)  # j_series[i] = j_{i-1}, so index 0 = j_{-1}
    j_series[0] = num[0] / den_full[1]  # j_{-1}
    
    for m_idx in range(1, N - 1):
        # m = m_idx - 1 (so m_idx=1 is m=0, m_idx=2 is m=1, etc.)
        m = m_idx - 1
        s = num[m + 1] if m + 1 < N else Fraction(0)
        for prev_idx in range(m_idx):
            prev_m = prev_idx - 1
            shift = m + 1 - prev_m  # = m - prev_m + 1
            if 0 <= shift < N:
                s -= j_series[prev_idx] * den_full[shift]
        j_series[m_idx] = s / den_full[1]
    
    if verbose:
        print("  j-invariant j(q) = (216t-1)³ / (t·(1+27t)³):")
        print(f"    j_{{{-1}}} = {j_series[0]}  (leading pole)")
        for i in range(1, min(12, len(j_series))):
            m = i - 1
            j_val = j_series[i]
            print(f"    j_{{{m:2d}}} = {int(j_val) if j_val.denominator == 1 else float(j_val)}")
        
        # Check: the j-function for Γ₀(3) should have j = 1/q + 248 + ...
        # Actually for the Hauptmodul of Γ₀(3), the expansion depends on
        # the normalization. Let's just display what we get.
        print()
        print(f"    j(q) = {int(j_series[0])}/q", end="")
        for i in range(1, min(6, len(j_series))):
            m = i - 1
            j_val = j_series[i]
            if j_val > 0:
                print(f" + {int(j_val)}·q^{m}" if m > 0 else f" + {int(j_val)}", end="")
            elif j_val < 0:
                print(f" - {int(-j_val)}·q^{m}" if m > 0 else f" - {int(-j_val)}", end="")
        print(" + ...")
        print()
    
    return j_series


def _poly_mul(a, b, max_n):
    """Multiply two truncated power series (as lists of Fractions)."""
    result = [Fraction(0)] * max_n
    for i in range(min(len(a), max_n)):
        if a[i] == 0:
            continue
        for j in range(min(len(b), max_n - i)):
            if b[j] == 0:
                continue
            result[i + j] += a[i] * b[j]
    return result


def verify_ode_factorization(max_n=15):
    """Verify that the 3rd-order ODE factors as θ·[2nd-order ₂F₁].
    
    Checks: n³c_n = n·(n²c_n) where n²c_n = -3(3n-1)(3n-2)c_{n-1}.
    """
    from math import factorial as fac
    from fractions import Fraction
    
    print("  ODE factorization: θ · [θ² + 27t(θ+1/3)(θ+2/3)] = 0")
    print()
    print("  3rd-order recurrence: n³ c_n = -(3n-2)(3n-1)(3n) c_{n-1}")
    print("  2nd-order recurrence: n² c_n = -3(3n-2)(3n-1) c_{n-1}")
    print("  Relation: 3rd = n × 2nd  ✓  (since (3n-2)(3n-1)(3n) = n·3(3n-2)(3n-1))")
    print()
    
    all_ok = True
    for n in range(1, max_n + 1):
        # Exact coefficient
        c_n = Fraction((-1)**n * fac(3*n), fac(n)**3)
        c_nm1 = Fraction((-1)**(n-1) * fac(3*(n-1)), fac(n-1)**3) if n >= 1 else Fraction(1)
        
        lhs_2 = n**2 * c_n
        rhs_2 = -3 * (3*n - 1) * (3*n - 2) * c_nm1
        
        lhs_3 = n**3 * c_n
        rhs_3 = -(3*n - 2) * (3*n - 1) * (3*n) * c_nm1
        
        ok2 = (lhs_2 == rhs_2)
        ok3 = (lhs_3 == rhs_3)
        ok_factor = (lhs_3 == n * lhs_2) and (rhs_3 == n * rhs_2)
        
        if not (ok2 and ok3 and ok_factor):
            all_ok = False
        
        if n <= 8:
            print(f"    n={n}: 2nd✓ 3rd✓ factor✓" if (ok2 and ok3 and ok_factor)
                  else f"    n={n}: {'2nd✓' if ok2 else '2nd✗'} "
                       f"{'3rd✓' if ok3 else '3rd✗'} "
                       f"{'factor✓' if ok_factor else 'factor✗'}")
    
    if all_ok:
        print(f"    ... all {max_n} checks pass ✓")
    print()
    return all_ok


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
                        help="Display box operators in S_alpha notation")
    parser.add_argument("--pf", action="store_true",
                        help="Display explicit PF operators in theta_i notation")
    parser.add_argument("--oneparam", action="store_true",
                        help="Derive 1-parameter ODE along z1-axis")
    parser.add_argument("--mirror", action="store_true",
                        help="Compute mirror map on z1-axis")
    parser.add_argument("--mirrororder", type=int, default=50,
                        help="Order for mirror map series (default: 50)")
    parser.add_argument("--logperiod", action="store_true",
                        help="Compute multi-parameter log period data")
    parser.add_argument("--factor", action="store_true",
                        help="Verify ODE factorization on z1-axis")
    parser.add_argument("--jinv", action="store_true",
                        help="Compute j-invariant on z1-axis")
    parser.add_argument("--verify", action="store_true",
                        help="Verify GKZ recurrence on period coefficients")
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
        print(f"\n[BOX] GKZ box operators (PF equations in S_α notation) □_k ω₀ = 0:")
        print()
        for k in range(6):
            data = box_operator_data(k)
            print(f"  {format_box_operator(k)}")
            print(f"    Degree: {data['positive_degree']} (positive) vs "
                  f"{data['negative_degree']} (negative)")
            print()

    # ---- Explicit PF operators ----
    if args.pf:
        print(f"\n[PF]")
        print_pf_operators()
    
    # ---- Period series ----
    # Skip period computation if only displaying operators/ODE
    skip_series = (args.pf or args.oneparam or args.mirror or args.factor or args.jinv) and not (args.verify or args.save or args.logperiod)
    if not skip_series:
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
    else:
        coeffs = {}
        sorted_terms = []
    # ---- 1-parameter ODE ----
    if args.oneparam:
        print(f"\n[ONEPARAM]")
        derive_1param_ode()

    # ---- Mirror map (1-parameter) ----
    if args.mirror:
        print(f"\n[MIRROR] 1-parameter mirror map on z₁-axis (order {args.mirrororder})")
        print(f"  Computing logarithmic period and mirror map...")
        print()
        q_coeffs, t_coeffs = compute_mirror_map_1param(args.mirrororder)
        
        # Save mirror map data
        outfile = f"results/mirror_map_1param_N{args.mirrororder}.json"
        save_mm = {
            'order': args.mirrororder,
            'description': 'Mirror map on z1-axis of GL12/D6 CY3',
            'ode': 'theta^3 + t*(3*theta+1)*(3*theta+2)*(3*theta+3) = 0',
            'q_coeffs': {str(n): str(q_coeffs[n]) for n in range(len(q_coeffs))
                         if q_coeffs[n] != 0},
            't_coeffs': {str(n): str(t_coeffs[n]) for n in range(len(t_coeffs))
                         if t_coeffs[n] != 0},
        }
        with open(outfile, 'w') as f:
            json.dump(save_mm, f, indent=2)
        print(f"  Saved to {outfile}")

    # ---- Multi-parameter log periods ----
    if args.logperiod:
        print(f"\n[LOGPERIOD] Multi-parameter logarithmic periods to degree {args.order}")
        print(f"  Formula: h_i(n) = −L_{{i,0}}·H_{{|m₀|}} − Σ s_α L_{{i,α}} H_{{m_α}}")
        print()
        log_data = compute_log_periods_multi(args.order)
        print(f"\n  Total non-zero entries: {len(log_data)}")
        
        # Show a few entries
        print(f"\n  Sample entries (first 15):")
        for idx, (n_tuple, (c_val, h_vals)) in enumerate(
                sorted(log_data.items(), key=lambda x: (sum(x[0]), x[0]))):
            if idx >= 15:
                break
            h_strs = [f"{float(h):.4f}" for h in h_vals]
            print(f"    n={n_tuple}: c={c_val}, h=[{', '.join(h_strs)}]")
    
    # ---- ODE factorization ----
    if args.factor:
        print(f"\n[FACTOR] ODE factorization on z₁-axis:")
        verify_ode_factorization()
    
    # ---- j-invariant ----
    if args.jinv:
        print(f"\n[JINV] j-invariant on z₁-axis (order {args.mirrororder})")
        print(f"  j(t) = (216t-1)³ / (t·(1+27t)³)")
        print()
        j_series = compute_j_invariant(args.mirrororder)
        
        # Save
        outfile = f"results/j_invariant_1param_N{args.mirrororder}.json"
        save_j = {
            'order': args.mirrororder,
            'description': 'j-invariant j(q) on z1-axis of GL12/D6 CY3',
            'formula': 'j(t) = (216t-1)^3 / (t*(1+27t)^3)',
            'hesse_pencil': 'X^3 + Y^3 + Z^3 = 3*psi*X*Y*Z, psi = -1/(3*z1^{1/3})',
            'coefficients': {str(i-1): str(j_series[i]) for i in range(len(j_series))
                             if j_series[i] != 0},
        }
        with open(outfile, 'w') as f:
            json.dump(save_j, f, indent=2)
        print(f"  Saved to {outfile}")

    # ---- Verification ----
    if args.verify:
        if not coeffs:
            coeffs = compute_period_multivariate(args.order, verbose=True)
        print(f"\n[VERIFY] GKZ recurrence: c_s(n+e_k)·P+ = c_s(n)·P-")
        print(f"  (c_s = (-1)^|m₀| · c, falling factorials use u = γ + m)")
        n_pass, n_fail, n_skip = verify_gkz_recurrence(
            coeffs, max_check_degree=args.order)
        print(f"  Passed: {n_pass}  Failed: {n_fail}  Skipped: {n_skip}")
        if n_fail == 0 and n_pass > 0:
            print("  All GKZ recurrence checks PASS ✓")

    # ---- Save ----
    if args.save:
        if not coeffs:
            coeffs = compute_period_multivariate(args.order, verbose=True)
        sorted_terms = sorted(coeffs.items(), key=lambda x: (sum(x[0]), x[0]))
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
