#!/usr/bin/env python3
"""
z2_bundle_analysis.py -- Compute Z_2 action on clean h^0=3 bundles of h16/P329.

Core question: Does the Z_2 involution split 3 generations as 2+1?

Method:
  1. Get the Z_2 generator sigma on the N-lattice polytope
  2. Compute how sigma permutes the lattice points (= toric divisors)
  3. For each clean bundle L, compute sigma(L) via ray permutation
  4. Classify: sigma(L) = L (Z_2-fixed) vs sigma(L) != L (Z_2-paired)
  5. For Z_2-fixed bundles: compute sigma* on H^0(X,L) via M-lattice
     section points to determine the 2+1 vs 3+0 representation

Key formula (Koszul + Z_2 trace):
  Tr(sigma* | H^0(X,D)) = f_D - f_{D+K}
  where f_D = #{ m in S_D : sigma^T m = m } (fixed lattice points)
  Then:
    dim(+1 eigenspace) = (h^0 + Tr) / 2
    dim(-1 eigenspace) = (h^0 - Tr) / 2
  A 2+1 split means dim(+1)=2, dim(-1)=1  (Tr=1)
  or equivalently  dim(+1)=1, dim(-1)=2  (Tr=-1)

Usage:
    python z2_bundle_analysis.py
"""

import numpy as np
import sys
import time
from collections import Counter
from scipy.optimize import linprog

from cy_compute import (
    fetch_polytopes_cached,
    find_chi3_bundles,
    compute_h0_koszul,
    basis_to_toric,
    precompute_vertex_data,
)

# ── Configuration ──
TARGET_H11 = 16
TARGET_H21 = 19
TARGET_POLY = 329
MAX_COEFF = 3
MAX_NONZERO = 4


def find_section_lattice_points(pts, ray_indices, D_toric):
    """Find all m in Z^4 with <m, v_rho> >= -d_rho for all rays rho.

    Returns (N, 4) integer array of lattice points.
    Uses vectorized bounding box + constraint checking (same method as
    cy_compute.count_lattice_points but returns the actual points).
    """
    dim = pts.shape[1]
    rays = pts[ray_indices].astype(np.float64)
    d_vals = D_toric[ray_indices].astype(np.float64)

    # Bounding box via LP
    A_ub = -rays
    b_ub = d_vals
    bounds = []
    for i in range(dim):
        c = np.zeros(dim)
        c[i] = 1
        r_min = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(None, None), method='highs')
        c[i] = -1
        r_max = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(None, None), method='highs')
        if r_min.success and r_max.success:
            bounds.append((int(np.floor(r_min.fun)), int(np.ceil(-r_max.fun))))
        else:
            return np.zeros((0, dim), dtype=int)

    vol = 1
    for lo, hi in bounds:
        vol *= (hi - lo + 1)
    if vol > 200_000_000 or vol <= 0:
        return np.zeros((0, dim), dtype=int)

    # Vectorized enumeration
    ranges = [np.arange(lo, hi + 1, dtype=np.int32) for lo, hi in bounds]
    grid = np.stack(np.meshgrid(*ranges, indexing='ij'), axis=-1)
    grid_flat = grid.reshape(-1, dim)

    # Check constraints: rays @ m.T >= -d_vals for all rays
    dots = rays.astype(np.int64) @ grid_flat.astype(np.int64).T
    feasible = np.all(dots >= -d_vals[:, None].astype(np.int64), axis=0)

    return grid_flat[feasible].astype(int)


def main():
    t0 = time.time()

    print("=" * 72)
    print("  Z_2 BUNDLE ANALYSIS: h16/P329")
    print("  Does the Z_2 involution split 3 generations as 2+1?")
    print("=" * 72)

    # ── Fetch polytope ──
    print("\n  Fetching polytopes...", flush=True)
    polys = fetch_polytopes_cached(TARGET_H11, TARGET_H21, limit=50000)
    p = polys[TARGET_POLY]
    pts = np.array(p.points(), dtype=int)
    n_pts = pts.shape[0]
    print("  Polytope: %d lattice points, dim %d" % (n_pts, p.dimension()))

    # ── Get automorphisms ──
    auts = p.automorphisms()
    print("  |Aut(Delta)| = %d" % len(auts))
    assert len(auts) == 2, "Expected Z_2, got |Aut|=%d" % len(auts)

    # Identify the non-identity element
    sigma = None
    for g in auts:
        if not np.allclose(g, np.eye(g.shape[0])):
            sigma = g
            break
    assert sigma is not None
    sigma = sigma.astype(int)

    det_sigma = int(round(np.linalg.det(sigma.astype(float))))
    s2 = sigma @ sigma
    assert np.allclose(s2, np.eye(sigma.shape[0])), "sigma^2 != identity!"

    print("\n  Z_2 generator sigma (on N-lattice):")
    for row in sigma:
        print("    [%s]" % " ".join("%3d" % int(x) for x in row))
    print("  det(sigma) = %d, sigma^2 = Id (confirmed)" % det_sigma)

    # ── Compute ray permutation ──
    print("\n" + "-" * 72)
    print("  RAY PERMUTATION (toric divisor action)")
    print("-" * 72)

    new_pts = (sigma @ pts.T).T
    ray_perm = np.full(n_pts, -1, dtype=int)
    for j in range(n_pts):
        for k in range(n_pts):
            if np.allclose(new_pts[j], pts[k]):
                ray_perm[j] = k
                break

    assert np.all(ray_perm >= 0), "Some rays have no image under sigma!"

    fixed_rays = [i for i in range(n_pts) if ray_perm[i] == i]
    swapped_rays = [(i, ray_perm[i]) for i in range(n_pts)
                    if ray_perm[i] > i]
    print("  Fixed rays (%d): %s" % (len(fixed_rays), fixed_rays))
    print("  Swapped pairs (%d): %s" % (len(swapped_rays), swapped_rays))

    # ── Build CY and get basis ──
    print("\n  Building CY 3-fold...", flush=True)
    tri = p.triangulate()
    cy = tri.get_cy()
    div_basis = list(cy.divisor_basis())
    h11_eff = len(div_basis)
    # ray_indices: all lattice points except the origin (index 0)
    ray_indices = list(range(1, n_pts))
    assert np.all(pts[0] == 0), "Origin check failed"
    print("  h11_eff = %d" % h11_eff)
    print("  Basis (toric indices): %s" % div_basis)

    # ── Sigma action on basis divisors ──
    print("\n" + "-" * 72)
    print("  Z_2 ACTION ON DIVISOR BASIS")
    print("-" * 72)

    basis_set = set(int(b) for b in div_basis)
    basis_inv = {int(b): i for i, b in enumerate(div_basis)}
    basis_perm = np.full(h11_eff, -1, dtype=int)
    perm_clean = True  # True if sigma permutes basis divisors among themselves

    for i, b in enumerate(div_basis):
        target_toric = ray_perm[int(b)]
        if int(target_toric) in basis_inv:
            j = basis_inv[int(target_toric)]
            basis_perm[i] = j
            tgt = int(div_basis[j])
            marker = "(FIXED)" if j == i else "(-> e%d)" % j
            print("    e%d (toric %d) -> e%d (toric %d) %s" % (
                i, int(b), j, tgt, marker))
        else:
            perm_clean = False
            print("    e%d (toric %d) -> toric %d *** NON-BASIS ***" % (
                i, int(b), target_toric))

    # ── Compute sigma action matrix on Picard lattice via GLSM ──
    print("\n" + "-" * 72)
    print("  SIGMA ACTION ON PICARD LATTICE (via GLSM linear relations)")
    print("-" * 72)

    # Linear relations from toric geometry:
    # For each m in M = Z^4: sum_rho <m, v_rho> D_rho ~ 0
    rays_all = pts[1:]  # (18, 4), skip origin
    n_rays = rays_all.shape[0]
    L = rays_all.T  # (4, 18) relation matrix

    # Basis vs non-basis ray indices (0-based within 18 rays)
    basis_ray = [int(b) - 1 for b in div_basis]
    nonbasis_toric = sorted(set(range(1, n_pts)) - basis_set)
    nonbasis_ray = [t - 1 for t in nonbasis_toric]
    print("  Non-basis toric indices: %s" % nonbasis_toric)

    L_B = L[:, basis_ray]  # (4, 14)
    L_N = L[:, nonbasis_ray]  # (4, 4)
    det_LN = np.linalg.det(L_N)
    print("  det(L_N) = %.1f" % det_LN)
    assert abs(det_LN) > 0.5, "L_N is singular!"

    # D_nonbasis = M_NB @ D_basis (express non-basis in terms of basis)
    inv_L_N = np.linalg.inv(L_N)
    M_NB = np.round(-inv_L_N @ L_B).astype(int)  # (4, 14)

    nonbasis_inv = {t: i for i, t in enumerate(nonbasis_toric)}
    for k, nb_toric in enumerate(nonbasis_toric):
        terms = [("(%+d)*D_%d" % (M_NB[k, a], div_basis[a]))
                 for a in range(h11_eff) if M_NB[k, a] != 0]
        print("  D_%d ~ %s" % (nb_toric, " + ".join(terms)))

    # Build sigma action matrix S on Pic(X):
    # sigma(E_a) = sum_b S[a,b] E_b
    sigma_matrix = np.zeros((h11_eff, h11_eff), dtype=int)
    for a, b in enumerate(div_basis):
        target = ray_perm[int(b)]
        if int(target) in basis_inv:
            j = basis_inv[int(target)]
            sigma_matrix[a, j] = 1
        elif int(target) in nonbasis_inv:
            k = nonbasis_inv[int(target)]
            sigma_matrix[a, :] = M_NB[k, :]
        else:
            print("  ERROR: target %d not in basis or non-basis!" % target)

    print("\n  Sigma action matrix S on Pic(X) (14x14):")
    print("  sigma(E_a) = sum_b S[a,b] E_b")
    for i in range(h11_eff):
        print("    [%s]" % " ".join("%3d" % sigma_matrix[i, j]
                                     for j in range(h11_eff)))

    # Verify S^2 = I
    s2_pic = sigma_matrix @ sigma_matrix
    assert np.allclose(s2_pic, np.eye(h11_eff)), "S^2 != I on Pic!"
    print("  S^2 = I on Pic(X): CONFIRMED")

    # The action on bundle basis coordinates: sigma(q) = S^T @ q
    S_T = sigma_matrix.T

    # Trace of S = #(+1 eigenvalues) - #(-1 eigenvalues)
    tr_S = int(np.trace(sigma_matrix))
    n_plus = (h11_eff + tr_S) // 2
    n_minus = (h11_eff - tr_S) // 2
    print("  Tr(S) = %d => Pic splits as %d(+1) + %d(-1)" % (
        tr_S, n_plus, n_minus))

    # ── Enumerate chi=+/-3 bundles ──
    print("\n" + "-" * 72)
    print("  ENUMERATING CHI=+-3 BUNDLES")
    print("-" * 72)

    intnums = cy.intersection_numbers(in_basis=True)
    c2 = cy.second_chern_class(in_basis=True)

    print("  Using cy_compute.find_chi3_bundles (vectorized)...", flush=True)
    t1 = time.time()
    bundles = find_chi3_bundles(intnums, c2, h11_eff,
                                max_coeff=MAX_COEFF, max_nonzero=MAX_NONZERO)
    print("  Found %d chi=+-3 bundles in %.1fs" % (len(bundles), time.time()-t1))

    # ── Compute cohomology ──
    print("\n  Computing h0 (Koszul) for all bundles...", flush=True)
    precomp = precompute_vertex_data(pts, ray_indices)
    n_toric = pts.shape[0]

    clean_bundles = []   # list of (D_basis as list, D_toric_full as array)
    t2 = time.time()

    for idx, (D_basis, chi) in enumerate(bundles):
        if chi > 0:
            D_compute = D_basis
            D_neg = -D_basis
        else:
            D_compute = -D_basis
            D_neg = D_basis

        D_toric = basis_to_toric(D_compute, div_basis, n_toric)
        h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=precomp)
        if h0 < 0 or h0 != 3:
            continue

        D_neg_toric = basis_to_toric(D_neg, div_basis, n_toric)
        h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric, _precomp=precomp)
        if h3 < 0:
            h3 = 0

        if h3 == 0:
            clean_bundles.append((list(D_compute.astype(int)), D_toric.copy()))

        if (idx + 1) % 2000 == 0:
            print("    %d/%d, %d clean so far..." % (
                idx+1, len(bundles), len(clean_bundles)), flush=True)

    # Deduplicate: (D, chi=3) and (-D, chi=-3) both map to same D_compute
    seen_basis = set()
    deduped = []
    for q, D in clean_bundles:
        tq = tuple(q)
        if tq not in seen_basis:
            seen_basis.add(tq)
            deduped.append((q, D))
    print("  Done in %.1fs" % (time.time() - t2))
    print("  Clean (h0=3, h3=0): %d total, %d unique" % (
        len(clean_bundles), len(deduped)))
    clean_bundles = deduped

    # ══════════════════════════════════════════════════════════════
    #  Z_2 ORBIT DECOMPOSITION (using S^T on basis coordinates)
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  Z_2 ORBIT DECOMPOSITION OF CLEAN BUNDLES")
    print("  (using full sigma action on Picard lattice)")
    print("=" * 72)

    # sigma acts on basis coords: sigma(q) = S^T @ q
    fixed_bundles = []       # (q_basis, D_toric)
    paired_bundles = []      # ((q1, D1), (q2, D2))
    visited = set()

    clean_basis_set = set(tuple(q) for q, _ in clean_bundles)
    clean_basis_dict = {tuple(q): (q, D) for q, D in clean_bundles}

    for q, D in clean_bundles:
        tq = tuple(q)
        if tq in visited:
            continue

        # Apply sigma to basis coordinates
        q_arr = np.array(q, dtype=int)
        sq_arr = S_T @ q_arr
        sq = list(sq_arr.astype(int))
        tsq = tuple(sq)

        if tq == tsq:
            fixed_bundles.append((q, D))
            visited.add(tq)
        else:
            if tsq in clean_basis_set:
                _, D_sigma = clean_basis_dict[tsq]
                paired_bundles.append(((q, D), (sq, D_sigma)))
            else:
                # sigma(D) is not in clean set — sigma image has higher
                # max_nonzero than our enumeration cutoff (4).
                # These are NOT fixed, so don't affect 2+1 analysis.
                pass
            visited.add(tq)
            visited.add(tsq)

    unclassified = len(clean_bundles) - len(fixed_bundles) - 2 * len(paired_bundles)
    n_sigma_outside = unclassified  # bundles whose sigma-image wasn't enumerated

    print("\n  Z_2-FIXED bundles (sigma(L) = L): %d" % len(fixed_bundles))
    for q, _ in fixed_bundles[:30]:
        nz = [(j, q[j]) for j in range(h11_eff) if q[j] != 0]
        print("    %s" % nz)
    if len(fixed_bundles) > 30:
        print("    ... (%d more)" % (len(fixed_bundles) - 30))

    print("\n  Z_2-PAIRED bundles (sigma(L) != L): %d pairs" % len(paired_bundles))
    for (q1, _), (q2, _) in paired_bundles[:15]:
        nz1 = [(j, q1[j]) for j in range(h11_eff) if q1[j] != 0]
        nz2 = [(j, q2[j]) for j in range(h11_eff) if q2[j] != 0]
        print("    %s  <-->  %s" % (nz1, nz2))
    if len(paired_bundles) > 15:
        print("    ... (%d more pairs)" % (len(paired_bundles) - 15))

    # ══════════════════════════════════════════════════════════════
    #  Z_2 REPRESENTATION ON H^0 FOR FIXED BUNDLES
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("  Z_2 REPRESENTATION ON H^0(X, L) = C^3")
    print("  For each Z_2-fixed bundle: trace of sigma* on sections")
    print("=" * 72)

    # The pullback sigma* on M-lattice characters:
    #   sigma*(chi^m) = chi^{sigma^T m}
    # (because <sigma^T m, v> = <m, sigma v>, and sigma^{-1} = sigma)
    sigma_T = sigma.T.copy()
    print("\n  sigma^T (action on M-lattice):")
    for row in sigma_T:
        print("    [%s]" % " ".join("%3d" % x for x in row))

    # For a Z_2-fixed line bundle L with divisor D:
    #   H^0(V,D) has monomial basis {x^m : m in S_D}
    #   sigma* permutes this basis: x^m -> x^{sigma^T m}
    #   Trace = # fixed points = #{m in S_D : sigma^T m = m}
    #
    # By Koszul: Tr(sigma*|H^0(X,D)) = f_D - f_{D+K}
    # where f_D = #{m in S_D : sigma^T m = m}
    #
    # Eigenspace dimensions:
    #   dim(+1) = (h^0 + Tr) / 2
    #   dim(-1) = (h^0 - Tr) / 2

    split_21 = []
    split_30 = []
    split_other = []

    print("\n  Computing section lattice points for each fixed bundle...")
    for qi, (q, D_full) in enumerate(fixed_bundles):
        # Section polytope S_D: {m in Z^4 : <m, v_rho> >= -D[rho] for all rays rho}
        sec_D = find_section_lattice_points(pts, ray_indices, D_full)

        # Shifted divisor D + K_V: d_rho -> d_rho - 1 for rays
        D_shift = D_full.copy()
        D_shift[ray_indices] -= 1
        sec_DK = find_section_lattice_points(pts, ray_indices, D_shift)

        h0_V = len(sec_D)
        h0_VK = len(sec_DK)
        h0_cy = h0_V - h0_VK

        # Count sigma^T-fixed lattice points in each section polytope
        if len(sec_D) > 0:
            sec_D_mapped = (sigma_T @ sec_D.T).T  # (N, 4)
            f_D = int(np.sum(np.all(sec_D_mapped == sec_D, axis=1)))
        else:
            f_D = 0

        if len(sec_DK) > 0:
            sec_DK_mapped = (sigma_T @ sec_DK.T).T
            f_DK = int(np.sum(np.all(sec_DK_mapped == sec_DK, axis=1)))
        else:
            f_DK = 0

        trace = f_D - f_DK

        # Eigenspace dimensions
        dim_plus = (h0_cy + trace) // 2
        dim_minus = (h0_cy - trace) // 2

        nz = [(j, q[j]) for j in range(h11_eff) if q[j] != 0]
        print("\n  L%d: %s" % (qi, nz))
        print("    |S_D|=%d (fixed:%d), |S_{D+K}|=%d (fixed:%d)" % (
            h0_V, f_D, h0_VK, f_DK))
        print("    h^0(X,D) = %d - %d = %d" % (h0_V, h0_VK, h0_cy))
        print("    Tr(sigma*) = %d - %d = %d" % (f_D, f_DK, trace))
        print("    Z_2 eigenspaces: dim(+1) = %d, dim(-1) = %d" % (
            dim_plus, dim_minus))

        if h0_cy != 3:
            print("    WARNING: h0_cy=%d != 3 (Koszul check failed)" % h0_cy)
            split_other.append((q, h0_cy, dim_plus, dim_minus))
        elif (h0_cy + trace) % 2 != 0:
            print("    WARNING: (h0 + Tr) is odd — parity error")
            split_other.append((q, h0_cy, trace, -1))
        elif dim_plus == 2 and dim_minus == 1:
            print("    *** 2+1 SPLIT ***")
            split_21.append(q)
        elif dim_plus == 1 and dim_minus == 2:
            print("    *** 1+2 SPLIT ***")
            split_21.append(q)
        elif dim_plus == 3 and dim_minus == 0:
            print("    Trivial (3+0)")
            split_30.append(q)
        elif dim_plus == 0 and dim_minus == 3:
            print("    Anti-trivial (0+3)")
            split_other.append((q, 3, 0, 3))
        else:
            print("    Unexpected: dim(+1)=%d, dim(-1)=%d" % (dim_plus, dim_minus))
            split_other.append((q, h0_cy, dim_plus, dim_minus))

    # ══════════════════════════════════════════════════════════════
    #  PAIRED BUNDLE ANALYSIS (brief)
    # ══════════════════════════════════════════════════════════════
    if paired_bundles:
        print("\n" + "=" * 72)
        print("  Z_2-PAIRED BUNDLES: COMBINED REPRESENTATION")
        print("=" * 72)
        print("\n  For paired (L, sigma*L), the Z_2 acts on")
        print("  H^0(X,L) + H^0(X,sigma*L) = C^3 + C^3 = C^6")
        print("  by swapping the two summands => always 3+3 split.")
        print("  Paired bundles: %d pairs" % len(paired_bundles))

    # ══════════════════════════════════════════════════════════════
    #  SUMMARY
    # ══════════════════════════════════════════════════════════════
    dt = time.time() - t0
    print("\n" + "=" * 72)
    print("  FINAL SUMMARY")
    print("=" * 72)
    print("  Polytope: h16/P329 (h11=%d, h21=%d, chi=-6)" % (TARGET_H11, TARGET_H21))
    print("  Z_2 generator: det(sigma) = %d" % det_sigma)
    print("  Basis divisors permuted cleanly: %s" % perm_clean)
    print()
    print("  Total clean h0=3, h3=0 bundles: %d" % len(clean_bundles))
    print("  Z_2-fixed bundles: %d" % len(fixed_bundles))
    print("  Z_2-paired bundles: %d pairs (%d bundles)" % (
        len(paired_bundles), 2 * len(paired_bundles)))
    if n_sigma_outside > 0:
        print("  Sigma-image outside enumeration: %d" % n_sigma_outside)
        print("  (These bundles are NOT Z_2-fixed, so do not affect the 2+1 test)")
    print()
    print("  Z_2 REPRESENTATION ON H^0 (fixed bundles):")
    print("    2+1 or 1+2 split (TEXTURE ZEROS): %d" % len(split_21))
    print("    3+0 trivial: %d" % len(split_30))
    print("    Other/mismatch: %d" % len(split_other))
    print()

    if split_21:
        pct = 100.0 * len(split_21) / max(len(fixed_bundles), 1)
        print("  *** RESULT: %d/%d fixed bundles show 2+1 generation split (%.0f%%) ***" % (
            len(split_21), len(fixed_bundles), pct))
        print("  *** The Z_2 involution isolates 1 generation from 2,")
        print("      constraining the Yukawa texture and potentially")
        print("      explaining the top-quark mass hierarchy. ***")
        print()
        print("  2+1 bundles are prime candidates for the rank-5")
        print("  AGLP line bundle sum V = L1 + ... + L5.")
    elif len(fixed_bundles) == 0 and len(paired_bundles) > 0:
        print("  RESULT: All clean bundles come in Z_2 pairs (no fixed bundles).")
        print("  The Z_2 acts freely on the bundle moduli space.")
        print("  The 2+1 split can still arise at the rank-5 sum level")
        print("  via nontrivial Z_2 action on the combined system.")
    elif len(fixed_bundles) > 0 and len(split_21) == 0:
        print("  RESULT: All Z_2-fixed bundles have trivial (3+0) representation.")
        print("  No texture zeros from Z_2 at the single-bundle level.")
        print("  Consider rank-5 sum-level analysis or other symmetries.")
    else:
        print("  RESULT: No fixed bundles found.")

    print("\n  Elapsed: %.1fs" % dt)
    print("=" * 72)

    # Write results to file
    outfile = "results/z2_h16_P329_analysis.txt"
    print("\n  Writing results to %s..." % outfile)
    with open(outfile, "w") as f:
        f.write("Z_2 Bundle Analysis: h16/P329\n")
        f.write("=" * 60 + "\n")
        f.write("Clean h0=3 bundles: %d\n" % len(clean_bundles))
        f.write("Z_2-fixed: %d\n" % len(fixed_bundles))
        f.wn_sigma_outside > 0:
            f.write("Sigma-image outside enumeration: %d\n" % n_sigma_outside
            f.write("Unclassified (sigma image not clean): %d\n" % unclassified)
        f.write("\n2+1 split bundles: %d\n" % len(split_21))
        f.write("3+0 trivial: %d\n" % len(split_30))
        f.write("Other: %d\n" % len(split_other))
        f.write("\nFixed bundles (basis coords):\n")
        for q, _ in fixed_bundles:
            nz = [(j, q[j]) for j in range(h11_eff) if q[j] != 0]
            f.write("  %s\n" % nz)
        f.write("\n2+1 split bundles:\n")
        for q in split_21:
            nz = [(j, q[j]) for j in range(h11_eff) if q[j] != 0]
            f.write("  %s\n" % nz)
    print("  Done.")


if __name__ == "__main__":
    main()
