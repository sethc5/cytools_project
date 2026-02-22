#!/usr/bin/env python3
"""
B-01: Scan χ=-6 polytopes for h⁰=3 line bundles.

Uses the verified Koszul + lattice-point method (from dragon_slayer_40h.py,
cross-checked against the quintic in 40i.py).

Reference: MATH_SPEC.md §4-5
"""

import cytools as cy
import numpy as np
from scipy.optimize import linprog
from itertools import product
from cytools.config import enable_experimental_features
enable_experimental_features()

# ──────────────────────────────────────────────────────────────
#  Core lattice-point counting (proven method from 40h, verified in 40i)
# ──────────────────────────────────────────────────────────────

def count_lattice_points(pts, ray_indices, D_toric):
    """
    Count |{m ∈ Z^4 : <m, v_ρ> ≥ -d_ρ  ∀ rays ρ}|.

    MATH_SPEC §4: rays are pts[1..n_toric-1], origin is pts[0] (excluded).
    """
    dim = pts.shape[1]
    n_rays = len(ray_indices)

    # Build constraint system: -pts[ρ] · m ≤ D_toric[ρ]
    A_ub = np.zeros((n_rays, dim))
    b_ub = np.zeros(n_rays)
    for k, rho in enumerate(ray_indices):
        A_ub[k] = -pts[rho]
        b_ub[k] = D_toric[rho]

    # Find bounding box via LP
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
            return 0  # Empty polytope

    # Check volume isn't insane
    vol = 1
    for lo, hi in bounds:
        vol *= (hi - lo + 1)
    if vol > 100_000_000:
        return -1  # Too large, skip

    # Enumerate
    count = 0
    for m0 in range(bounds[0][0], bounds[0][1] + 1):
        for m1 in range(bounds[1][0], bounds[1][1] + 1):
            for m2 in range(bounds[2][0], bounds[2][1] + 1):
                for m3 in range(bounds[3][0], bounds[3][1] + 1):
                    m = np.array([m0, m1, m2, m3])
                    ok = True
                    for k, rho in enumerate(ray_indices):
                        if np.dot(m, pts[rho]) < -D_toric[rho]:
                            ok = False
                            break
                    if ok:
                        count += 1
    return count


def compute_h0_koszul(pts, ray_indices, D_toric, div_basis, h11):
    """
    Compute h⁰(X, O(D)) via Koszul exact sequence.

    MATH_SPEC §4.2:
      h⁰(X, D) = h⁰(V, D) - h⁰(V, D+K_V) + correction
      where K_V = -sum of all toric divisors, so D+K_V means d_ρ → d_ρ - 1
      Correction from h¹(V, D+K_V) — compute if needed, was 0 for Polytope 40.
    """
    n_toric = pts.shape[0]

    h0_V = count_lattice_points(pts, ray_indices, D_toric)
    if h0_V < 0:
        return -1  # Overflow

    # Shifted divisor D + K_V: subtract 1 from each ray coefficient
    D_shift = D_toric.copy()
    for rho in ray_indices:
        D_shift[rho] -= 1

    h0_shift = count_lattice_points(pts, ray_indices, D_shift)
    if h0_shift < 0:
        return -1

    # For now, assume h¹(V, D+K_V) = 0 (was true for all 119 bundles on Polytope 40)
    # This makes h⁰(X,D) = h⁰(V,D) - h⁰(V,D+K_V)  — a LOWER BOUND in general
    h0_CY = h0_V - h0_shift

    return h0_CY


def compute_chi(D_basis, intnums, c2, h11):
    """HRR: χ(O(D)) = D³/6 + c₂·D/12 on CY3."""
    D3 = 0.0
    for (i, j, k), val in intnums.items():
        D3 += D_basis[i] * D_basis[j] * D_basis[k] * val
    c2D = sum(D_basis[a] * c2[a] for a in range(h11))
    return D3 / 6.0 + c2D / 12.0


def basis_to_toric(D_basis, div_basis, n_toric):
    """
    Convert basis-indexed divisor to toric-indexed.
    MATH_SPEC §2.2: D_toric[div_basis[a]] = D_basis[a], rest = 0.
    """
    D_toric = np.zeros(n_toric, dtype=int)
    for a, idx in enumerate(div_basis):
        D_toric[idx] = D_basis[a]
    return D_toric


# ──────────────────────────────────────────────────────────────
#  Bundle search
# ──────────────────────────────────────────────────────────────

def find_chi3_bundles(intnums, c2, h11, max_coeff=3, max_nonzero=3):
    """
    Find all basis-indexed divisors D with |χ(O(D))| ≈ 3.
    Restrict to at most max_nonzero nonzero coefficients in range [-max_coeff, max_coeff].
    """
    bundles = []
    indices = list(range(h11))

    # Generate combinations: pick up to max_nonzero basis indices
    from itertools import combinations
    for n_nz in range(1, min(max_nonzero + 1, h11 + 1)):
        for chosen in combinations(indices, n_nz):
            # Try all coefficient combinations for chosen indices
            coeff_range = list(range(-max_coeff, max_coeff + 1))
            coeff_range.remove(0)
            for coeffs in product(coeff_range, repeat=n_nz):
                D_basis = np.zeros(h11, dtype=int)
                for idx, c in zip(chosen, coeffs):
                    D_basis[idx] = c
                chi = compute_chi(D_basis, intnums, c2, h11)
                if abs(abs(chi) - 3.0) < 0.01:
                    bundles.append((D_basis.copy(), chi))
    return bundles


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

    # Safety: check c2 matches h11
    if len(c2) != h11:
        return {'status': 'c2_mismatch', 'n_toric': n_toric, 'h11': h11,
                'c2_len': len(c2)}

    # Find χ=3 bundles
    # Adapt search range based on h11
    if h11 <= 15:
        max_coeff = 3
        max_nonzero = 3
    elif h11 <= 20:
        max_coeff = 2
        max_nonzero = 3
    else:
        max_coeff = 2
        max_nonzero = 2

    bundles = find_chi3_bundles(intnums, c2, h11, max_coeff, max_nonzero)

    if not bundles:
        return {
            'status': 'no_chi3',
            'n_toric': n_toric,
            'h11': h11,
        }

    # Compute h⁰ for each χ=3 bundle
    max_h0 = 0
    best_bundle = None
    h0_3_count = 0
    n_computed = 0

    for D_basis, chi in bundles:
        D_toric = basis_to_toric(D_basis, div_basis, n_toric)

        # Only compute for χ=+3 (not -3) since h⁰ is interesting for positive χ
        if chi > 0:
            h0 = compute_h0_koszul(pts, ray_indices, D_toric, div_basis, h11)
        else:
            # For χ=-3: by Serre, h³=h⁰(-D). Check h⁰(-D)
            D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
            h0 = compute_h0_koszul(pts, ray_indices, D_neg, div_basis, h11)

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
                tag = ""
                if max_h0 >= 3:
                    tag = " ★★★ HIT ★★★"
                    hits.append(result)
                elif max_h0 >= 2:
                    tag = " (h⁰=2)"
                print(f"  poly {idx:3d}: n_toric={result['n_toric']:2d}, "
                      f"{n_chi3:4d} χ=3 bundles, max h⁰={max_h0}{tag}")
            elif status == 'no_chi3':
                print(f"  poly {idx:3d}: n_toric={result['n_toric']:2d}, "
                      f"NO χ=3 bundles found")
            elif status == 'c2_mismatch':
                print(f"  poly {idx:3d}: SKIP (c2 size {result.get('c2_len')} ≠ h11={result.get('h11')})")
            else:
                print(f"  poly {idx:3d}: {status}")

    # ── Summary ──
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)

    ok_results = [r for r in results if r['status'] == 'ok']
    print(f"\nPolytopes scanned: {len(results)}")
    print(f"Successfully analyzed: {len(ok_results)}")
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
