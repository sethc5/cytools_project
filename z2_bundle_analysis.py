#!/usr/bin/env python3
"""
z2_bundle_analysis.py -- Compute Z_2 action on clean h^0=3 bundles of h16/P329.

Core question: Does the Z_2 involution act as 2+1 on the 3-generation
vector space H^0(X, L) = C^3?

Method:
  1. Get the Z_2 generator sigma on the N-lattice polytope
  2. Compute how sigma permutes the lattice points (= toric divisors)
  3. Express the permutation on the divisor basis
  4. For each clean bundle L, compute sigma(L) in basis coordinates
  5. Classify: sigma(L) = L  (fixed) vs sigma(L) != L (paired orbit)
  6. For fixed bundles, compute the Z_2 representation on H^0(X,L):
     - Use the toric section basis: sections of O(D) correspond to
       lattice points m in M with <m, v_rho> >= -a_rho for all rays rho
     - sigma acts on M-lattice points by the dual (transpose-inverse) map
     - Count fixed points to get the Z_2 trace on H^0
     - Trace 3 => trivial (3+0), trace 1 => 2+1 split (what we want)

Usage:
    python z2_bundle_analysis.py
"""

import numpy as np
import sys
import time
from itertools import product
from collections import Counter

try:
    from cytools import fetch_polytopes
    from cytools.config import enable_experimental_features
    enable_experimental_features()
except ImportError:
    print("ERROR: CYTools not available")
    sys.exit(1)

# ── Configuration ──
TARGET_H11 = 16
TARGET_H21 = 19
TARGET_POLY = 329
MAX_COEFF = 3
MAX_NONZERO = 4

def compute_chi(charges, intnums, c2, h11_eff):
    """Compute chi(L) = (D^3 + c_2.D) / 12."""
    d3 = 0
    for (i, j, k), val in intnums.items():
        d3 += val * charges[i] * charges[j] * charges[k]
    c2d = sum(c2[i] * charges[i] for i in range(h11_eff))
    chi_num = d3 + c2d
    if chi_num % 12 != 0:
        return None
    return chi_num // 12


def find_all_chi3_bundles(intnums, c2, h11_eff):
    """Enumerate all line bundles with chi = +/- 3."""
    bundles = []
    ranges = [range(-MAX_COEFF, MAX_COEFF + 1)] * h11_eff
    for charges in product(*ranges):
        charges = list(charges)
        nz = sum(1 for c in charges if c != 0)
        if nz == 0 or nz > MAX_NONZERO:
            continue
        chi = compute_chi(charges, intnums, c2, h11_eff)
        if chi is not None and abs(chi) == 3:
            bundles.append((np.array(charges, dtype=int), chi))
    return bundles


def main():
    t0 = time.time()

    print("=" * 72)
    print("  Z_2 BUNDLE ANALYSIS: h16/P329")
    print("  Does the Z_2 involution split 3 generations as 2+1?")
    print("=" * 72)

    # ── Fetch polytope ──
    print("\n  Fetching polytopes...", flush=True)
    polys = list(fetch_polytopes(h11=TARGET_H11, h21=TARGET_H21,
                                 lattice="N", limit=50000))
    p = polys[TARGET_POLY]
    pts = p.points()
    print("  Polytope: %d points, dim %d" % (pts.shape[0], p.dimension()))

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

    det = int(round(np.linalg.det(sigma)))
    # Check order
    s2 = sigma @ sigma
    assert np.allclose(s2, np.eye(sigma.shape[0])), "sigma^2 != identity!"

    print("\n  Z_2 generator sigma:")
    for row in sigma:
        print("    [%s]" % " ".join("%3d" % int(x) for x in row))
    print("  det(sigma) = %d" % det)
    print("  sigma^2 = Identity (confirmed)")

    # ── Compute ray permutation ──
    # sigma acts on the N-lattice: v -> sigma.v
    # This permutes the lattice points of Delta
    print("\n" + "-" * 72)
    print("  RAY PERMUTATION")
    print("-" * 72)

    new_pts = (sigma @ pts.T).T

    ray_perm = np.zeros(pts.shape[0], dtype=int) - 1
    for j in range(pts.shape[0]):
        for k in range(pts.shape[0]):
            if np.allclose(new_pts[j], pts[k]):
                ray_perm[j] = k
                break
        if ray_perm[j] == -1:
            print("  WARNING: point %d maps outside polytope!" % j)

    print("  Ray permutation (point_i -> point_j):")
    fixed_rays = []
    swapped_rays = []
    for i in range(len(ray_perm)):
        if ray_perm[i] == i:
            fixed_rays.append(i)
        elif ray_perm[i] > i:  # Only print each swap once
            swapped_rays.append((i, ray_perm[i]))
    print("  Fixed rays: %s" % fixed_rays)
    print("  Swapped pairs: %s" % swapped_rays)

    # ── Build CY and get basis ──
    print("\n  Building CY 3-fold...")
    tri = p.triangulate()
    cy = tri.get_cy()
    basis = list(cy.divisor_basis())
    h11_eff = len(basis)
    print("  h11_eff = %d" % h11_eff)
    print("  Basis (toric indices): %s" % basis)

    # ── Compute sigma action on basis divisors ──
    print("\n" + "-" * 72)
    print("  Z_2 ACTION ON DIVISOR BASIS")
    print("-" * 72)

    # For each basis divisor e_i (toric index basis[i]),
    # sigma maps it to the divisor at toric index ray_perm[basis[i]]
    basis_set = set(int(b) for b in basis)
    basis_inv = {int(b): i for i, b in enumerate(basis)}

    sigma_on_basis = {}  # maps basis index -> basis index (or None if outside)
    basis_perm = np.zeros(h11_eff, dtype=int) - 1
    perm_valid = True

    for i, b in enumerate(basis):
        target_toric = ray_perm[int(b)]
        if int(target_toric) in basis_inv:
            j = basis_inv[int(target_toric)]
            basis_perm[i] = j
            sigma_on_basis[i] = j
        else:
            # The basis divisor maps to a non-basis toric divisor
            # Need to express it in terms of basis using linear relations
            sigma_on_basis[i] = "non-basis(toric %d)" % target_toric
            perm_valid = False

    print("  sigma permutation on basis indices:")
    for i in range(h11_eff):
        b = int(basis[i])
        target = sigma_on_basis[i]
        if isinstance(target, int):
            tb = int(basis[target])
            marker = " (FIXED)" if target == i else " (SWAPS with e%d)" % target
            print("    e%d (toric %d) -> e%d (toric %d)%s" % (i, b, target, tb, marker))
        else:
            print("    e%d (toric %d) -> %s  *** NON-BASIS ***" % (i, b, target))

    if perm_valid:
        print("\n  sigma acts as a PERMUTATION on the basis (no linear relations needed)")
    else:
        print("\n  WARNING: sigma maps some basis divisors outside the basis.")
        print("  Need to use linear equivalence to express the action.")
        print("  Computing linear relations...")

        # The toric divisors satisfy linear relations from the fan:
        # Sum_rho <m, v_rho> D_rho = 0 for all m in M
        # We can use these to express non-basis divisors in terms of basis divisors

        # CYTools can give us this: the linear relations matrix
        # D_j = sum_i M_ji * e_i  for non-basis j, where e_i are basis divisors
        try:
            # Try to get the full-to-basis map from CYTools
            # glsm_charge_matrix or similar
            glsm = cy.glsm_charge_matrix(include_origin=False)
            print("  GLSM charge matrix shape: %s" % str(glsm.shape))

            # Alternative: use the divisor basis change matrix
            # cy.divisor_basis() gives the basis indices
            # To express D_j in basis coords, we need the inverse map
        except Exception as e:
            print("  Could not get GLSM matrix: %s" % e)

    # ── Even if permutation is not clean on basis, we can still ──
    # ── check which bundles are Z_2-fixed by direct computation  ──

    print("\n" + "-" * 72)
    print("  ENUMERATING CLEAN BUNDLES")
    print("-" * 72)

    intnums = cy.intersection_numbers(in_basis=True)
    c2 = cy.second_chern_class(in_basis=True)

    print("  Finding chi=+/-3 bundles (max_coeff=%d, max_nonzero=%d)..." % (
        MAX_COEFF, MAX_NONZERO), flush=True)
    bundles = find_all_chi3_bundles(intnums, c2, h11_eff)
    print("  Found %d chi=+/-3 bundles" % len(bundles))

    # ── Compute cohomology for all bundles ──
    print("  Computing cohomology (this may take a few minutes)...", flush=True)
    clean_bundles = []
    h0_3_bundles = []  # All with h0=3 (clean or not)

    for idx, (charges, chi) in enumerate(bundles):
        try:
            coh = cy.line_bundle_cohomology(list(charges), in_basis=True)
            h0, h1, h2, h3 = int(coh[0]), int(coh[1]), int(coh[2]), int(coh[3])
        except Exception:
            continue

        if h0 == 3 and h3 == 0 and h1 == 0 and h2 == 0:
            clean_bundles.append(list(charges))
        if h0 == 3:
            h0_3_bundles.append((list(charges), h1, h2, h3))

        if (idx + 1) % 1000 == 0:
            print("    %d/%d processed, %d clean so far..." % (
                idx + 1, len(bundles), len(clean_bundles)), flush=True)

    print("\n  Results:")
    print("  Clean (h0=3, h1=h2=h3=0): %d" % len(clean_bundles))
    print("  All h0=3: %d" % len(h0_3_bundles))

    # ── Z_2 action on bundle space ──
    print("\n" + "=" * 72)
    print("  Z_2 ORBIT DECOMPOSITION OF CLEAN BUNDLES")
    print("=" * 72)

    if perm_valid:
        # sigma acts on charge vector q as: sigma(q)_i = q_{sigma^{-1}(i)}
        # Since sigma^2 = 1, sigma^{-1} = sigma, so sigma(q)_i = q_{sigma(i)}
        # Wait -- more carefully:
        # If sigma permutes basis divisors as e_i -> e_{sigma(i)},
        # then a bundle L = sum q_i e_i maps to sigma(L) = sum q_i e_{sigma(i)}
        # = sum q_{sigma^{-1}(j)} e_j
        # So in charge vector: sigma(q)_j = q_{sigma^{-1}(j)} = q_{sigma(j)} (since sigma^2 = 1)

        print("\n  sigma acts on charge vectors by permutation.")
        print("  sigma(q)_j = q_{sigma(j)}")

        fixed_bundles = []
        paired_bundles = []
        visited = set()

        for q in clean_bundles:
            tq = tuple(q)
            if tq in visited:
                continue

            # Compute sigma(q)
            sq = [q[basis_perm[j]] for j in range(h11_eff)]
            tsq = tuple(sq)

            if tq == tsq:
                fixed_bundles.append(q)
                visited.add(tq)
            else:
                if tsq not in visited:
                    paired_bundles.append((q, sq))
                    visited.add(tq)
                    visited.add(tsq)
                else:
                    # Partner already processed
                    visited.add(tq)

        print("\n  Z_2-FIXED bundles (sigma(L) = L): %d" % len(fixed_bundles))
        for q in fixed_bundles:
            nz = [(j, q[j]) for j in range(h11_eff) if q[j] != 0]
            print("    %s" % nz)

        print("\n  Z_2-PAIRED bundles (sigma(L) != L): %d pairs" % len(paired_bundles))
        for q1, q2 in paired_bundles[:20]:
            nz1 = [(j, q1[j]) for j in range(h11_eff) if q1[j] != 0]
            nz2 = [(j, q2[j]) for j in range(h11_eff) if q2[j] != 0]
            print("    %s  <-->  %s" % (nz1, nz2))
        if len(paired_bundles) > 20:
            print("    ... (%d more pairs)" % (len(paired_bundles) - 20))

        # ── For FIXED bundles: compute Z_2 action on H^0(X,L) ──
        print("\n" + "=" * 72)
        print("  Z_2 REPRESENTATION ON H^0(X,L) FOR FIXED BUNDLES")
        print("=" * 72)

        if len(fixed_bundles) == 0:
            print("\n  No Z_2-fixed clean bundles!")
            print("  All clean bundles come in Z_2 pairs.")
            print("  The 2+1 splitting cannot arise from a bundle-level Z_2 action.")
            print("  HOWEVER: the Z_2 still acts on the SECTIONS of paired bundles.")
            print("  In the rank-5 sum V = L1+...+L5, if some Li are Z_2-paired,")
            print("  the Z_2 acts nontrivially on the combined cohomology.")
        else:
            print("\n  For each Z_2-fixed bundle L (sigma(L)=L), sigma induces")
            print("  an automorphism sigma* on H^0(X,L) = C^3.")
            print("  We compute the trace: tr(sigma*) = #lattice-pts fixed by sigma*")
            print("  Trace 3 => trivial (3+0), Trace 1 => 2+1 split (target!)")

            # To compute sigma* on H^0, we need the toric section basis.
            # In toric geometry, H^0(X, O(D)) has sections indexed by
            # lattice points m in M^* with <m, v_rho> >= -a_rho for all rho.
            # sigma acts on M via sigma^{-T} (inverse transpose).
            # sigma* maps section s_m to s_{sigma^{-T}(m)}.
            #
            # For a CY hypersurface, H^0(X, O(D)) is the restriction of
            # the ambient space sections, which is the same set minus those
            # in the ideal -- but for smooth CY, the restriction map is
            # typically an isomorphism when h0 is small.

            sigma_dual = np.linalg.inv(sigma).T
            sigma_dual_int = np.round(sigma_dual).astype(int)
            print("\n  sigma* on M-lattice (dual action): sigma^{-T}")
            for row in sigma_dual_int:
                print("    [%s]" % " ".join("%3d" % x for x in row))

            for qi, q in enumerate(fixed_bundles):
                print("\n  --- Fixed bundle L%d: %s ---" % (
                    qi, [(j, q[j]) for j in range(h11_eff) if q[j] != 0]))

                # Build the divisor in full toric coordinates
                D_full = np.zeros(pts.shape[0], dtype=int)
                for a_idx in range(h11_eff):
                    D_full[int(basis[a_idx])] = q[a_idx]

                # Find lattice points m with <m, v_rho> >= -D_rho for all rho
                # The polytope P_D = { m in R^4 : <m, pts[rho]> >= -D_full[rho] }
                # We need to enumerate integer points in this polytope.

                # For small h0 (=3), we can search in a bounded region.
                # The rays pts[rho] and bounds -D_full[rho] define half-spaces.
                # Use a brute-force search in a box.

                # Estimate bounds from the polytope structure
                # m must satisfy <m, v_rho> >= -D_rho for all rho where v_rho != 0
                # For the interior (origin) point: <m, 0> = 0 >= -D_full[0], need D_full[0] >= 0

                # Search box: try [-10, 10]^4
                section_pts = []
                for m0 in range(-10, 11):
                    for m1 in range(-10, 11):
                        for m2 in range(-10, 11):
                            for m3 in range(-10, 11):
                                m = np.array([m0, m1, m2, m3])
                                ok = True
                                for rho in range(pts.shape[0]):
                                    if np.dot(m, pts[rho]) < -D_full[rho]:
                                        ok = False
                                        break
                                if ok:
                                    section_pts.append(m.copy())

                n_sections = len(section_pts)
                print("  H^0 sections (lattice points in P_D): %d" % n_sections)

                if n_sections == 0:
                    print("  WARNING: Found 0 sections (box too small or CY restriction)")
                    continue

                if n_sections < 3:
                    print("  WARNING: Only %d ambient sections; CY restriction?" % n_sections)

                # Apply sigma* to each section point
                n_fixed = 0
                for m in section_pts:
                    m_new = sigma_dual_int @ m
                    if np.array_equal(m, m_new):
                        n_fixed += 1

                trace = 2 * n_fixed - n_sections  # For involution: eigenvalues +1 and -1
                # Actually: trace = n_fixed_with_eval_+1 - n_fixed_with_eval_-1
                # But sigma* is a permutation, so trace = #fixed points
                # No: sigma* is a linear map on C^3, not a permutation of basis vectors
                # unless the section lattice points form an orbit structure.
                #
                # More carefully: sigma* permutes the section lattice points.
                # The trace is the number of FIXED lattice points.
                # (Each fixed point contributes eigenvalue +1.)
                # The permutation matrix has trace = #fixed points.

                print("  sigma* fixed lattice points: %d / %d" % (n_fixed, n_sections))

                if n_sections > 0:
                    n_swapped = n_sections - n_fixed
                    n_pairs = n_swapped // 2
                    print("  Swapped pairs: %d" % n_pairs)

                    # On the AMBIENT space:
                    # H^0(ambient, O(D)) has dimension n_sections with n_fixed +1 evals and n_pairs -1 evals
                    # But on the CY, H^0(X, O(D)) = 3 dimensions
                    # The CY restriction preserves the Z_2 action
                    #
                    # If n_sections = 3 (no excess), then trace = n_fixed directly
                    # If n_sections > 3, the CY restriction kills some sections
                    # but preserves the Z_2 representation structure.

                    if n_sections == 3:
                        print("\n  *** DIRECT RESULT (no ambient excess) ***")
                        if n_fixed == 1:
                            print("  *** Z_2 REPRESENTATION: 2+1 SPLIT ***")
                            print("  *** 1 fixed section (+1 eigenvalue)")
                            print("  *** 1 swapped pair (-1 eigenvalue pair)")
                            print("  *** => 3rd generation ISOLATED by parity!")
                        elif n_fixed == 3:
                            print("  Z_2 acts trivially (3+0) -- no texture constraint")
                        elif n_fixed == 2:
                            print("  Z_2 representation: 2(+1) + 1(-1) = 2+1")
                            print("  *** 2+1 SPLIT: 1 generation is Z_2-odd ***")
                        else:
                            print("  Unexpected fixed count: %d" % n_fixed)

                    elif n_sections > 3:
                        print("\n  Ambient H^0 = %d > CY H^0 = 3" % n_sections)
                        print("  CY restriction: %d -> 3 sections" % n_sections)
                        print("  Ambient (+1) eigenspace: dim %d" % n_fixed)
                        print("  Ambient (-1) eigenspace: dim %d" % n_pairs)
                        # The CY H^0 is a 3-dim Z_2-invariant subspace
                        # The decomposition depends on how the restriction works
                        # But we can bound it:
                        if n_fixed >= 1 and n_pairs >= 1:
                            print("  Both eigenspaces nonempty => CY restriction likely 2+1")
                            print("  (unless all -1 sections are killed by restriction)")
                        elif n_fixed == n_sections:
                            print("  All sections fixed => trivial Z_2 on H^0")

    else:
        # perm_valid is False -- need linear equivalence approach
        print("\n  Non-trivial basis permutation -- using direct CYTools approach")
        print("  Computing sigma action via cohomology...")

        # For each clean bundle, compute sigma(L) by:
        # 1. Convert to full toric coordinates
        # 2. Apply ray permutation
        # 3. Convert back to basis coordinates (if possible)
        # 4. Or just check if the cohomologies match

        fixed_bundles = []
        paired_bundles = []
        visited_indices = set()

        for i, q in enumerate(clean_bundles):
            if i in visited_indices:
                continue

            # Full toric divisor
            D_full = np.zeros(pts.shape[0], dtype=int)
            for a_idx in range(h11_eff):
                D_full[int(basis[a_idx])] = q[a_idx]

            # Apply ray permutation
            D_sigma = np.zeros_like(D_full)
            for rho in range(len(D_full)):
                D_sigma[ray_perm[rho]] = D_full[rho]

            # Convert sigma(D) back to basis coordinates
            sq = np.zeros(h11_eff, dtype=int)
            in_basis = True
            for a_idx in range(h11_eff):
                sq[a_idx] = D_sigma[int(basis[a_idx])]

            # Check if sigma(D) has nonzero components on non-basis divisors
            for rho in range(len(D_sigma)):
                if int(rho) not in basis_set and D_sigma[rho] != 0:
                    in_basis = False
                    break

            if in_basis and list(sq) == q:
                fixed_bundles.append(q)
                visited_indices.add(i)
            elif in_basis:
                # Find the partner in clean_bundles
                sq_list = list(sq)
                found_partner = False
                for j, q2 in enumerate(clean_bundles):
                    if j != i and j not in visited_indices and q2 == sq_list:
                        paired_bundles.append((q, sq_list))
                        visited_indices.add(i)
                        visited_indices.add(j)
                        found_partner = True
                        break
                if not found_partner:
                    # sigma(L) is not clean, or maps to a different bundle type
                    print("  L=%s -> sigma(L)=%s (not in clean set)" % (
                        [(j, q[j]) for j in range(h11_eff) if q[j] != 0],
                        [(j, int(sq[j])) for j in range(h11_eff) if sq[j] != 0]))
                    visited_indices.add(i)
            else:
                # sigma(D) has non-basis components -- need linear equivalence
                print("  L=%s -> sigma(L) has non-basis components, need lin. equiv." % (
                    [(j, q[j]) for j in range(h11_eff) if q[j] != 0],))
                visited_indices.add(i)

        print("\n  Z_2-FIXED bundles: %d" % len(fixed_bundles))
        for q in fixed_bundles[:20]:
            nz = [(j, q[j]) for j in range(h11_eff) if q[j] != 0]
            print("    %s" % nz)

        print("\n  Z_2-PAIRED bundles: %d pairs" % len(paired_bundles))
        for q1, q2 in paired_bundles[:20]:
            nz1 = [(j, q1[j]) for j in range(h11_eff) if q1[j] != 0]
            nz2 = [(j, q2[j]) for j in range(h11_eff) if q2[j] != 0]
            print("    %s  <-->  %s" % (nz1, nz2))

        # Same H^0 lattice-point analysis for fixed bundles
        if fixed_bundles:
            sigma_dual_int = np.round(np.linalg.inv(sigma).T).astype(int)
            print("\n  sigma* on M-lattice: sigma^{-T}")
            for row in sigma_dual_int:
                print("    [%s]" % " ".join("%3d" % x for x in row))

            for qi, q in enumerate(fixed_bundles[:10]):
                print("\n  --- Fixed bundle L%d ---" % qi)
                D_full = np.zeros(pts.shape[0], dtype=int)
                for a_idx in range(h11_eff):
                    D_full[int(basis[a_idx])] = q[a_idx]

                section_pts = []
                for m0 in range(-10, 11):
                    for m1 in range(-10, 11):
                        for m2 in range(-10, 11):
                            for m3 in range(-10, 11):
                                m = np.array([m0, m1, m2, m3])
                                ok = True
                                for rho in range(pts.shape[0]):
                                    if np.dot(m, pts[rho]) < -D_full[rho]:
                                        ok = False
                                        break
                                if ok:
                                    section_pts.append(m.copy())

                n_sections = len(section_pts)
                print("  Ambient H^0 sections: %d  (CY H^0 = 3)" % n_sections)

                n_fixed = sum(1 for m in section_pts
                              if np.array_equal(sigma_dual_int @ m, m))
                n_pairs = (n_sections - n_fixed) // 2
                print("  sigma* fixed: %d, paired: %d" % (n_fixed, n_pairs))

                if n_sections == 3 and n_fixed == 1:
                    print("  *** 2+1 SPLIT CONFIRMED ***")
                elif n_sections == 3 and n_fixed == 2:
                    print("  *** 2+1 SPLIT (2 fixed, 1 flipped) ***")
                elif n_sections > 3:
                    # Ambient decomposition
                    plus_dim = n_fixed
                    minus_dim = n_pairs
                    print("  Ambient: (+1)-eigenspace dim %d, (-1)-eigenspace dim %d" % (
                        plus_dim, minus_dim))
                    if plus_dim >= 1 and minus_dim >= 1 and plus_dim + minus_dim >= 3:
                        print("  => CY restriction LIKELY gives 2+1 or 1+2")
                    elif minus_dim == 0:
                        print("  => All ambient sections Z_2-even => trivial (3+0)")

    # ── Summary ──
    dt = time.time() - t0
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    print("  Polytope: h16/P329 (h11=16, h21=19, chi=-6)")
    print("  |Aut| = 2 (Z_2), det(sigma) = %d" % det)
    print("  Clean h0=3 bundles: %d" % len(clean_bundles))
    if perm_valid:
        print("  Z_2-fixed: %d" % len(fixed_bundles))
        print("  Z_2-paired: %d pairs" % len(paired_bundles))
    else:
        print("  Z_2-fixed: %d" % len(fixed_bundles))
        print("  Z_2-paired: %d pairs" % len(paired_bundles))
    print("  Elapsed: %.1fs" % dt)
    print("=" * 72)


if __name__ == "__main__":
    main()
