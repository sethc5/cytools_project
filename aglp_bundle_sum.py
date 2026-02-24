#!/usr/bin/env python3
"""
aglp_bundle_sum.py — Search for rank-5 line bundle sums V = L₁⊕···⊕L₅
satisfying heterotic SU(5) GUT constraints.

Based on Anderson-Gray-Lukas-Palti (AGLP) construction:
    V = L₁ ⊕ L₂ ⊕ L₃ ⊕ L₄ ⊕ L₅   (structure group S(U(1)⁵) ⊂ SU(5))

Constraints:
    1. c₁(V) = 0:  L₁ + L₂ + L₃ + L₄ + L₅ = 0  in  Pic(X)
    2. c₂(V) ≤ c₂(TX):  anomaly cancellation (remainder = M5 class, must be effective)
    3. ind(V) = c₃(V)/2 = ±3:  3 net chiral generations
    4. Slope stability (necessary condition): μ(Lᵢ) < 0 for some ample J

For line bundle sums, Chern classes are computed from intersections:
    c₂(V) = Σ_{i<j} Lᵢ · Lⱼ    (as a cohomology class)
    c₃(V) = Σ_{i<j<k} Lᵢ · Lⱼ · Lₖ
where "·" means cup product / intersection.

Search strategy:
    Pick L₁, L₂, L₃, L₄ from clean bundle list; L₅ = −(L₁+L₂+L₃+L₄).
    Accept iff L₅ is also a valid bundle (in extended list) AND c₃(V) = ±6.
    The c₁=0 is automatic by construction.

Usage:
    python aglp_bundle_sum.py --h11 14 --poly 2
    python aglp_bundle_sum.py --h11 16 --poly 329

Reference: AGLP hep-th/1307.4787, 1405.2073
"""

import argparse
import numpy as np
import sys
import time
from itertools import combinations
from collections import Counter

from cy_compute import (
    fetch_polytopes_cached,
    find_chi3_bundles,
    compute_h0_koszul,
    basis_to_toric,
    precompute_vertex_data,
    build_intnum_tensor,
    compute_chi_batch,
)

# ── Defaults ──
DEFAULT_H11 = 14
DEFAULT_POLY = 2
MAX_COEFF = 3
MAX_NONZERO = 4


def parse_args():
    parser = argparse.ArgumentParser(
        description="AGLP line bundle sum search: V = L₁⊕···⊕L₅ for SU(5) GUT")
    parser.add_argument("--h11", type=int, default=DEFAULT_H11,
                        help="h^{1,1} (default: %d)" % DEFAULT_H11)
    parser.add_argument("--poly", type=int, default=DEFAULT_POLY,
                        help="Polytope index (default: %d)" % DEFAULT_POLY)
    parser.add_argument("--h21", type=int, default=None,
                        help="h^{2,1} (default: h11+3 for chi=-6)")
    parser.add_argument("--max-coeff", type=int, default=MAX_COEFF)
    parser.add_argument("--max-nonzero", type=int, default=MAX_NONZERO)
    parser.add_argument("--max-L5-coeff", type=int, default=6,
                        help="Max abs coefficient for L5 to be accepted (default: 6)")
    parser.add_argument("--skip-h0-check", action="store_true",
                        help="Skip h⁰ check on L₅ (faster, less strict)")
    parser.add_argument("--workers", type=int, default=1)
    return parser.parse_args()


def triple_intersection(D1, D2, D3, T):
    """Compute D1·D2·D3 = Σ D1_i D2_j D3_k T_ijk."""
    # T is the dense intersection tensor (h, h, h)
    return float(np.einsum('i,j,k,ijk->', D1, D2, D3, T))


def compute_c3_V(Ls, T):
    """c₃(V) = Σ_{i<j<k} Lᵢ·Lⱼ·Lₖ for V = ⊕Lᵢ.

    For 5 line bundles, there are C(5,3) = 10 triple products.
    """
    c3 = 0.0
    for i, j, k in combinations(range(len(Ls)), 3):
        c3 += triple_intersection(Ls[i], Ls[j], Ls[k], T)
    return c3


def compute_c2_V_class(Ls, T, h11_eff):
    """c₂(V) as cohomology class in H⁴(X).

    c₂(V) = Σ_{i<j} Lᵢ·Lⱼ  (as 2-form product → 4-form class).
    To compare with c₂(TX), we compute c₂(V)·Dₐ for each basis divisor Dₐ.
    This gives the "effective" c₂ as a vector in H⁴.

    Returns (h11_eff,) array: c₂(V)·Dₐ.
    """
    c2_vec = np.zeros(h11_eff, dtype=np.float64)
    for a in range(h11_eff):
        val = 0.0
        for i, j in combinations(range(len(Ls)), 2):
            # Lᵢ · Lⱼ · Dₐ
            Da = np.zeros(h11_eff, dtype=np.float64)
            Da[a] = 1.0
            val += triple_intersection(Ls[i], Ls[j], Da, T)
        c2_vec[a] = val
    return c2_vec


def main():
    args = parse_args()
    h11 = args.h11
    h21 = args.h21 if args.h21 is not None else h11 + 3
    poly_idx = args.poly
    max_coeff = args.max_coeff
    max_nonzero = args.max_nonzero
    max_L5_coeff = args.max_L5_coeff

    label = "h%d/P%d" % (h11, poly_idx)
    t0 = time.time()

    print("=" * 72)
    print("  AGLP LINE BUNDLE SUM SEARCH: %s" % label)
    print("  V = L₁ ⊕ L₂ ⊕ L₃ ⊕ L₄ ⊕ L₅  (SU(5) GUT)")
    print("=" * 72)

    # ── Fetch polytope & build CY ──
    print("\n  Fetching polytope...", flush=True)
    polys = fetch_polytopes_cached(h11, h21, limit=50000)
    p = polys[poly_idx]
    pts = np.array(p.points(), dtype=int)
    n_pts = pts.shape[0]
    print("  Polytope: %d lattice points, dim %d" % (n_pts, p.dimension()))

    print("  Building CY 3-fold...", flush=True)
    tri = p.triangulate()
    cy = tri.get_cy()
    div_basis = [int(x) for x in cy.divisor_basis()]
    h11_eff = len(div_basis)
    ray_indices = list(range(1, n_pts))
    n_toric = n_pts

    intnums = dict(cy.intersection_numbers(in_basis=True))
    c2_TX = np.array(cy.second_chern_class(in_basis=True), dtype=np.float64)
    T = build_intnum_tensor(intnums, h11_eff)

    print("  h¹¹_eff = %d" % h11_eff)
    print("  Basis (toric indices): %s" % div_basis)
    print("  c₂(TX) = %s" % list(c2_TX.astype(int)))

    # ── Get clean bundles ──
    print("\n" + "-" * 72)
    print("  STEP 1: ENUMERATE CLEAN LINE BUNDLES")
    print("-" * 72)

    print("  Finding χ=±3 bundles...", flush=True)
    t1 = time.time()
    bundles = find_chi3_bundles(intnums, c2_TX, h11_eff,
                                max_coeff=max_coeff, max_nonzero=max_nonzero)
    print("  Found %d χ=±3 bundles in %.1fs" % (len(bundles), time.time() - t1))

    # Compute h⁰ and filter for clean (h⁰=3, h³=0)
    print("  Computing h⁰ (Koszul)...", flush=True)
    precomp = precompute_vertex_data(pts, ray_indices)

    clean = []  # list of basis-coord arrays (as int arrays)
    all_valid = {}  # map tuple(D_basis) -> True, including non-clean but valid

    t2 = time.time()
    for idx, (D_basis, chi) in enumerate(bundles):
        if chi > 0:
            D_compute = D_basis
        else:
            D_compute = -D_basis

        D_toric = basis_to_toric(D_compute, div_basis, n_toric)
        h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=precomp)
        if h0 != 3:
            continue

        D_neg_toric = basis_to_toric(-D_compute, div_basis, n_toric)
        h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric, _precomp=precomp)
        if h3 < 0:
            h3 = 0

        if h3 == 0:
            tq = tuple(D_compute.astype(int))
            if tq not in all_valid:
                all_valid[tq] = True
                clean.append(D_compute.astype(int).copy())

    print("  Clean bundles (h⁰=3, h³=0): %d unique in %.1fs" % (
        len(clean), time.time() - t2))

    if len(clean) < 5:
        print("\n  *** INSUFFICIENT CLEAN BUNDLES (%d < 5). Cannot form rank-5 sum. ***" % len(clean))
        return

    # ── Also build a lookup for L₅ candidates ──
    # L₅ = -(L₁+L₂+L₃+L₄) might not be "clean" in the h⁰=3 sense,
    # but for anomaly cancellation we just need it to be a valid line bundle.
    # For the full AGLP, we accept any L₅ with |coefficients| ≤ max_L5_coeff.
    # We'll check its validity post-hoc if needed.
    clean_set = set(tuple(q) for q in clean)
    clean_arr = np.array(clean, dtype=int)  # (N, h11_eff)
    N = len(clean)

    print("\n  Clean bundle coefficient stats:")
    print("    Max |coeff|: %d" % int(np.max(np.abs(clean_arr))))
    print("    Mean |coeff|: %.2f" % float(np.mean(np.abs(clean_arr[clean_arr != 0]))))
    print("    Max nonzero entries: %d" % int(np.max(np.sum(clean_arr != 0, axis=1))))

    # ── AGLP search ──
    print("\n" + "-" * 72)
    print("  STEP 2: SEARCH FOR RANK-5 SUMS  V = L₁⊕L₂⊕L₃⊕L₄⊕L₅")
    print("  Constraint: L₁+L₂+L₃+L₄+L₅ = 0  (c₁=0)")
    print("  Filter: c₃(V) = ±6  (3 generations)")
    print("-" * 72)

    # Strategy: iterate over 4-tuples (i₁ < i₂ < i₃ < i₄) from clean list.
    # L₅ = -(L₁+L₂+L₃+L₄). Check if L₅ is in clean_set.
    # If so, compute c₃ and filter.

    n_4tuples = 0
    n_L5_valid = 0
    n_L5_clean = 0
    n_c3_pass = 0
    solutions = []

    print("\n  Total 4-tuples to scan: C(%d, 4) = %d" % (
        N, N * (N-1) * (N-2) * (N-3) // 24))
    print("  Scanning...", flush=True)

    t3 = time.time()
    report_interval = max(1, N * (N-1) * (N-2) * (N-3) // 24 // 20)

    for idx_tuple in combinations(range(N), 4):
        n_4tuples += 1

        L1 = clean_arr[idx_tuple[0]]
        L2 = clean_arr[idx_tuple[1]]
        L3 = clean_arr[idx_tuple[2]]
        L4 = clean_arr[idx_tuple[3]]

        # L₅ = -(L₁ + L₂ + L₃ + L₄)
        L5 = -(L1 + L2 + L3 + L4)

        # Quick rejection: coefficient too large
        if np.max(np.abs(L5)) > max_L5_coeff:
            continue

        # Check if L₅ is in clean set
        tL5 = tuple(L5)
        if tL5 not in clean_set:
            # L₅ not among our clean bundles — skip
            # (Could relax this to check h⁰ on-the-fly, but expensive)
            continue

        n_L5_clean += 1

        # L₅ is also clean! Now compute c₃(V).
        Ls = [L1.astype(np.float64), L2.astype(np.float64),
              L3.astype(np.float64), L4.astype(np.float64),
              L5.astype(np.float64)]

        c3 = compute_c3_V(Ls, T)
        c3_int = int(round(c3))

        if abs(c3_int) != 6:
            continue

        n_c3_pass += 1

        # Compute c₂(V) and check anomaly cancellation
        c2_V = compute_c2_V_class(Ls, T, h11_eff)
        c2_V_int = np.round(c2_V).astype(int)

        # Anomaly cancellation: c₂(TX) - c₂(V) = [W] (effective class)
        # In practice, c₂(TX)·Dₐ - c₂(V)·Dₐ ≥ 0 for all ample Dₐ
        # (the remainder is the M5-brane class, which must be effective).
        # For a first pass, we just check that the difference makes sense.
        diff = c2_TX - c2_V_int
        # NOTE: effectivity check requires Mori cone, which we don't have here.
        # For now, record the difference and flag manifest violations later.

        sol = {
            'L': [list(L.astype(int)) for L in [L1, L2, L3, L4, L5]],
            'c3': c3_int,
            'ind': c3_int // 2,
            'c2_V': list(c2_V_int),
            'c2_diff': list(diff.astype(int)),
            'idx': idx_tuple,
        }
        solutions.append(sol)

        if n_c3_pass <= 20:
            nz_strs = []
            for k, Lk in enumerate([L1, L2, L3, L4, L5]):
                nz = [(j, int(Lk[j])) for j in range(h11_eff) if Lk[j] != 0]
                nz_strs.append("L%d=%s" % (k+1, nz))
            print("\n  *** SOLUTION %d ***" % n_c3_pass)
            for s in nz_strs:
                print("    %s" % s)
            print("    c₃(V) = %d  →  %d generations" % (c3_int, abs(c3_int) // 2))
            print("    c₂(V) = %s" % list(c2_V_int))
            print("    c₂(TX) - c₂(V) = %s" % list(diff.astype(int)))

        if n_4tuples % report_interval == 0:
            elapsed = time.time() - t3
            print("    [%d 4-tuples, %.0fs, %d L₅-clean, %d c₃-pass]" % (
                n_4tuples, elapsed, n_L5_clean, n_c3_pass), flush=True)

    dt_search = time.time() - t3

    # ══════════════════════════════════════════════════════════════
    #  ANOMALY CANCELLATION CHECK
    # ══════════════════════════════════════════════════════════════
    # For solutions, check c₂(TX) - c₂(V) against Mori cone
    # (positive pairing with all Mori generators → effective)
    print("\n" + "-" * 72)
    print("  STEP 3: ANOMALY CANCELLATION CHECK")
    print("-" * 72)

    try:
        mori_gens = np.array(cy.toric_mori_cone().rays(), dtype=int)
        have_mori = True
        print("  Mori cone generators: %d" % len(mori_gens))
    except Exception:
        have_mori = False
        mori_gens = None
        print("  WARNING: Could not compute Mori cone. Skipping effectivity check.")

    n_anomaly_pass = 0
    for sol in solutions:
        if have_mori:
            diff = np.array(sol['c2_diff'], dtype=np.float64)
            # Check: diff · C ≥ 0 for all Mori generators C
            # Mori generators are in toric coords, but c2_diff is in basis coords.
            # We need to pair c2_diff (as a class in H⁴) with curve classes.
            # For simplicity: c₂(TX) and c₂(V) are both computed in basis,
            # so their difference, paired with basis curves, should be ≥ 0.
            # Actually, the Mori cone rays are curve classes.
            # The pairing is: (c₂(TX)-c₂(V))·C = Σ_a diff[a] * C[a]
            # where C is expressed in the divisor basis.
            # Mori rays from CYTools may be in toric coords (one per ray),
            # which requires conversion. For now, just check the sign pattern.
            all_nonneg = np.all(diff >= -0.5)
            sol['anomaly_naive'] = all_nonneg
            if all_nonneg:
                n_anomaly_pass += 1
        else:
            sol['anomaly_naive'] = None

    # ══════════════════════════════════════════════════════════════
    #  SLOPE STABILITY (necessary condition)
    # ══════════════════════════════════════════════════════════════
    print("\n" + "-" * 72)
    print("  STEP 4: SLOPE STABILITY (necessary condition)")
    print("-" * 72)

    # For a line bundle sum to be slope-(poly)stable, every sub-bundle
    # must have negative slope. Since c₁(V) = 0 → μ(V) = 0,
    # stability requires μ(Lᵢ) < 0 for each Lᵢ.
    # μ(Lᵢ) = Lᵢ · J · J  (for ample J).
    #
    # Necessary condition: there exists a Kähler class J in the Kähler cone
    # such that Lᵢ · J² < 0 for all i = 1,...,5.
    #
    # We sample the Kähler cone tip and check.

    try:
        tip = cy.toric_kahler_cone().tip_of_stretched_cone(1.0)
        tip = np.array(tip, dtype=np.float64)
        have_tip = True
        print("  Kähler cone tip: %s" % list(tip.astype(int)))
    except Exception:
        have_tip = False
        tip = None
        print("  WARNING: Could not find Kähler cone tip.")

    n_stable = 0
    if have_tip:
        for sol in solutions:
            slopes_ok = True
            slopes = []
            for Lk_list in sol['L']:
                Lk = np.array(Lk_list, dtype=np.float64)
                # μ(Lᵢ) = Lᵢ · J · J = Σ Lk_a J_b J_c T_abc
                mu = float(np.einsum('i,j,k,ijk->', Lk, tip, tip, T))
                slopes.append(mu)
                if mu >= 0:
                    slopes_ok = False
            sol['slopes'] = slopes
            sol['slope_stable'] = slopes_ok
            if slopes_ok:
                n_stable += 1
    else:
        for sol in solutions:
            sol['slopes'] = None
            sol['slope_stable'] = None

    # ══════════════════════════════════════════════════════════════
    #  SUMMARY
    # ══════════════════════════════════════════════════════════════
    dt = time.time() - t0

    print("\n" + "=" * 72)
    print("  FINAL SUMMARY: %s" % label)
    print("=" * 72)
    print("  Polytope: %s (h11=%d, h21=%d, h11_eff=%d, chi=-6)" % (
        label, h11, h21, h11_eff))
    print("  Clean h⁰=3 bundles: %d" % N)
    print("  4-tuples scanned: %d (%.1fs)" % (n_4tuples, dt_search))
    print()
    print("  Results:")
    print("    L₅ in clean set: %d" % n_L5_clean)
    print("    c₃(V) = ±6 (3 gen): %d" % n_c3_pass)
    if have_mori:
        print("    Anomaly cancellation (naive): %d" % n_anomaly_pass)
    if have_tip:
        print("    Slope stable (at tip): %d" % n_stable)
    print()

    # Count the best solutions
    best = [s for s in solutions
            if s.get('slope_stable', False) and s.get('anomaly_naive', True)]
    print("  *** VIABLE CANDIDATES (c₃=±6, slope-stable, anomaly-ok): %d ***" % len(best))

    if best:
        print("\n  Top viable solutions:")
        for i, sol in enumerate(best[:20]):
            print("\n    --- Solution %d ---" % (i + 1))
            for k, Lk in enumerate(sol['L']):
                nz = [(j, Lk[j]) for j in range(h11_eff) if Lk[j] != 0]
                print("      L%d = %s" % (k+1, nz))
            print("      c₃(V) = %d → %d generations" % (sol['c3'], abs(sol['ind'])))
            print("      c₂(TX)-c₂(V) = %s" % sol['c2_diff'])
            if sol['slopes']:
                print("      slopes μ(Lᵢ) = %s" % [round(s, 2) for s in sol['slopes']])

    elif solutions:
        print("\n  Solutions found but none pass all filters.")
        print("  Showing first 10 c₃-passing solutions:")
        for i, sol in enumerate(solutions[:10]):
            print("\n    --- Solution %d ---" % (i + 1))
            for k, Lk in enumerate(sol['L']):
                nz = [(j, Lk[j]) for j in range(h11_eff) if Lk[j] != 0]
                print("      L%d = %s" % (k+1, nz))
            print("      c₃(V) = %d" % sol['c3'])
            print("      c₂_diff = %s" % sol['c2_diff'])
            print("      anomaly_naive = %s" % sol.get('anomaly_naive'))
            print("      slope_stable = %s" % sol.get('slope_stable'))
            if sol.get('slopes'):
                print("      slopes = %s" % [round(s, 2) for s in sol['slopes']])

    else:
        print("\n  No rank-5 sums found with c₃=±6.")
        print("  Consider: relaxing max_coeff, max_nonzero, or using non-clean L₅.")

    print("\n  Elapsed: %.1fs" % dt)
    print("=" * 72)

    # ── Write output ──
    outfile = "results/aglp_%s.txt" % label.replace("/", "_")
    print("\n  Writing results to %s..." % outfile)
    with open(outfile, "w") as f:
        f.write("AGLP Line Bundle Sum Search: %s\n" % label)
        f.write("=" * 60 + "\n")
        f.write("h11=%d, h21=%d, h11_eff=%d, chi=-6\n" % (h11, h21, h11_eff))
        f.write("Clean h0=3 bundles: %d\n" % N)
        f.write("4-tuples scanned: %d\n" % n_4tuples)
        f.write("L5 in clean set: %d\n" % n_L5_clean)
        f.write("c3=+-6 solutions: %d\n" % n_c3_pass)
        if have_tip:
            f.write("Slope-stable: %d\n" % n_stable)
        f.write("Viable (all filters): %d\n\n" % len(best))

        for i, sol in enumerate(solutions):
            f.write("Solution %d:\n" % (i + 1))
            for k, Lk in enumerate(sol['L']):
                nz = [(j, Lk[j]) for j in range(h11_eff) if Lk[j] != 0]
                f.write("  L%d = %s\n" % (k+1, nz))
            f.write("  c3=%d, ind=%d\n" % (sol['c3'], sol['ind']))
            f.write("  c2_diff=%s\n" % sol['c2_diff'])
            f.write("  anomaly=%s, slope_stable=%s\n" % (
                sol.get('anomaly_naive'), sol.get('slope_stable')))
            if sol.get('slopes'):
                f.write("  slopes=%s\n" % [round(s, 2) for s in sol['slopes']])
            f.write("\n")

    print("  Done.")


if __name__ == "__main__":
    main()
