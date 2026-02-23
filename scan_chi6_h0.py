#!/usr/bin/env python3
"""
B-01: Scan χ=-6 polytopes for h⁰=3 line bundles.

Uses the verified Koszul + lattice-point method (from dragon_slayer_40h.py,
cross-checked against the quintic in 40i.py).

Computation functions imported from cy_compute.py (vectorized, ~19× faster).

Reference: MATH_SPEC.md §4-5
"""

import cytools as cy
import numpy as np
from cytools.config import enable_experimental_features
enable_experimental_features()

from cy_compute import (
    count_lattice_points,
    compute_h0_koszul,
    compute_chi,
    basis_to_toric,
    find_chi3_bundles,
    precompute_vertex_data,
)


# ──────────────────────────────────────────────────────────────
#  Main scanner
# ──────────────────────────────────────────────────────────────

def scan_polytope(p, poly_idx, h11_val, h21_val):
    """Scan a single polytope for h⁰≥3 bundles."""
    try:
        tri = p.triangulate()
        cyobj = tri.get_cy()
    except Exception as e:
        return {'status': 'tri_fail', 'error': str(e)}

    h11 = cyobj.h11()
    pts = np.array(p.points(), dtype=int)
    n_toric = pts.shape[0]
    ray_indices = list(range(1, n_toric))
    div_basis = [int(x) for x in cyobj.divisor_basis()]
    intnums = dict(cyobj.intersection_numbers(in_basis=True))
    c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

    # Verify origin
    if not np.all(pts[0] == 0):
        return {'status': 'origin_fail'}

    # For non-favorable polytopes, len(div_basis) < h11.
    # The toric basis is internally consistent (c2, intnums, div_basis all
    # use the same reduced basis of size n_toric - 5). We work in this
    # basis and note non-favorable cases in the output.
    h11_eff = len(div_basis)  # effective working dimension
    is_favorable = (h11_eff == h11)

    # Safety: c2 must match the toric basis dimension
    if len(c2) != h11_eff:
        return {'status': 'c2_mismatch', 'n_toric': n_toric, 'h11': h11,
                'h11_eff': h11_eff, 'c2_len': len(c2)}

    # Find χ=3 bundles (using effective toric basis dimension)
    # Adapt search range based on h11_eff (toric basis size)
    if h11_eff <= 15:
        max_coeff = 3
        max_nonzero = 3
    elif h11_eff <= 20:
        max_coeff = 2
        max_nonzero = 3
    else:
        max_coeff = 2
        max_nonzero = 2

    bundles = find_chi3_bundles(intnums, c2, h11_eff, max_coeff, max_nonzero)

    if not bundles:
        return {
            'status': 'no_chi3',
            'n_toric': n_toric,
            'h11': h11,
            'h11_eff': h11_eff,
            'favorable': is_favorable,
        }

    # Precompute vertex data for fast h⁰ (~30× faster bounding box)
    _precomp = precompute_vertex_data(pts, ray_indices)

    # Compute h⁰ for each χ=3 bundle
    max_h0 = 0
    best_bundle = None
    h0_3_count = 0
    n_computed = 0

    for D_basis, chi in bundles:
        D_toric = basis_to_toric(D_basis, div_basis, n_toric)

        # Only compute for χ=+3 (not -3) since h⁰ is interesting for positive χ
        if chi > 0:
            h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=_precomp)
        else:
            # For χ=-3: by Serre, h³=h⁰(-D). Check h⁰(-D)
            D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
            h0 = compute_h0_koszul(pts, ray_indices, D_neg, _precomp=_precomp)

        n_computed += 1

        if h0 < 0:
            continue  # Overflow, skip

        if h0 >= 3:
            h0_3_count += 1

        if h0 > max_h0:
            max_h0 = h0
            best_bundle = D_basis.copy()

    return {
        'status': 'ok',
        'n_toric': n_toric,
        'h11': h11,
        'h11_eff': h11_eff,
        'favorable': is_favorable,
        'n_chi3': len(bundles),
        'n_computed': n_computed,
        'max_h0': max_h0,
        'h0_3_count': h0_3_count,
        'best_bundle': best_bundle,
    }


def main():
    print("=" * 72)
    print("  B-01: SCAN χ=-6 POLYTOPES FOR h⁰ ≥ 3 LINE BUNDLES")
    print("  Method: Verified Koszul + lattice-point counting")
    print("=" * 72)
    print()

    # χ = 2(h11 - h21) = -6  ⟹  h21 = h11 + 3
    results = []
    hits = []

    for h11_val in range(13, 25):  # h11=13..24
        h21_val = h11_val + 3
        try:
            polys = list(cy.fetch_polytopes(
                h11=h11_val, h21=h21_val, lattice='N', limit=100
            ))
        except Exception:
            continue

        if not polys:
            continue

        print(f"\n{'─' * 60}")
        print(f"  h11={h11_val}, h21={h21_val}  —  {len(polys)} polytopes")
        print(f"{'─' * 60}")

        for idx, p in enumerate(polys):
            result = scan_polytope(p, idx, h11_val, h21_val)
            result['h11_val'] = h11_val
            result['h21_val'] = h21_val
            result['poly_idx'] = idx
            results.append(result)

            status = result['status']
            if status == 'ok':
                max_h0 = result['max_h0']
                n_chi3 = result['n_chi3']
                fav_tag = '' if result.get('favorable', True) else ' [NF]'
                tag = ""
                if max_h0 >= 3:
                    tag = " ★★★ HIT ★★★"
                    hits.append(result)
                elif max_h0 >= 2:
                    tag = " (h⁰=2)"
                print(f"  poly {idx:3d}: n_toric={result['n_toric']:2d}, "
                      f"h11_eff={result.get('h11_eff', '?'):2}, "
                      f"{n_chi3:4d} χ=3 bundles, max h⁰={max_h0}{tag}{fav_tag}")
            elif status == 'no_chi3':
                fav_tag = '' if result.get('favorable', True) else ' [NF]'
                print(f"  poly {idx:3d}: n_toric={result['n_toric']:2d}, "
                      f"NO χ=3 bundles found{fav_tag}")
            elif status == 'c2_mismatch':
                print(f"  poly {idx:3d}: SKIP (c2 size {result.get('c2_len')} ≠ "
                      f"h11_eff={result.get('h11_eff')}, h11={result.get('h11')})")
            else:
                print(f"  poly {idx:3d}: {status}")

    # ── Summary ──
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)

    ok_results = [r for r in results if r['status'] == 'ok']
    nf_results = [r for r in ok_results if not r.get('favorable', True)]
    c2_skip = [r for r in results if r['status'] == 'c2_mismatch']
    print(f"\nPolytopes scanned: {len(results)}")
    print(f"Successfully analyzed: {len(ok_results)} ({len(nf_results)} non-favorable)")
    print(f"Skipped (c2 mismatch): {len(c2_skip)}")
    print(f"Polytopes with χ=3 bundles: {sum(1 for r in ok_results if r['n_chi3'] > 0)}")
    print(f"Polytopes with max h⁰ ≥ 3: {len(hits)}")

    if hits:
        print(f"\n{'─' * 60}")
        print("  ★★★ h⁰ ≥ 3 HITS ★★★")
        print(f"{'─' * 60}")
        for h in hits:
            nz = [(i, h['best_bundle'][i]) for i in range(len(h['best_bundle']))
                   if h['best_bundle'][i] != 0]
            bundle_str = " + ".join(f"{c}·e{i}" for i, c in nz)
            print(f"  h11={h['h11_val']}, poly {h['poly_idx']}: "
                  f"max h⁰={h['max_h0']}, best={bundle_str}, "
                  f"{h['h0_3_count']} bundles with h⁰≥3")
    else:
        print("\n  No h⁰ ≥ 3 found in this scan range.")

    # Distribution of max h⁰
    h0_dist = {}
    for r in ok_results:
        h0 = r['max_h0']
        h0_dist[h0] = h0_dist.get(h0, 0) + 1
    print(f"\nmax h⁰ distribution: {dict(sorted(h0_dist.items()))}")

    print("\nDone.")


if __name__ == '__main__':
    main()
