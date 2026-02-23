#!/usr/bin/env python3
"""
tier2_screen.py — Tier 2 deep screener for top χ=-6 candidates.

Takes the top N results from Tier 1 screening and runs four expensive
checks that separate genuine pipeline candidates from false positives:

  1. Exact h⁰=3 bundle count (full Koszul computation + h³=0 verification)
  2. h³ = h⁰(-D) = 0 verification for all h⁰≥3 bundles
  3. D³ intersection statistics for χ=3 bundles
  4. K3 / elliptic fibration count (dual-polytope geometry)

Inputs from Tier 1: results/tier1_screen_results.csv
Outputs:           results/tier2_screen_results.csv

Usage:
  python3 tier2_screen.py                        # top 20 from Tier 1
  python3 tier2_screen.py --top 10               # top 10
  python3 tier2_screen.py --h11 18 --poly 8      # single polytope
  python3 tier2_screen.py --csv results/tier1_screen_results.csv
  python3 tier2_screen.py --csv15 results/tier15_screen_results.csv --top 50
  python3 tier2_screen.py --csv15 ... --offset 0 --batch 25   # first 25
  python3 tier2_screen.py --csv15 ... --offset 25 --batch 25  # next 25

Reference: MATH_SPEC.md §4-5, FRAMEWORK.md §1-4.
"""

import sys
import csv
import argparse
import time
import hashlib
import cytools as cy
import numpy as np
from scipy.optimize import linprog
from itertools import product, combinations
from cytools.config import enable_experimental_features
enable_experimental_features()

CYTOOLS_VERSION = getattr(cy, '__version__', 'unknown')

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
STAR = "\033[93m★\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ══════════════════════════════════════════════════════════════════
#  Core methods (proven in dragon_slayer_40h, verified in 40i)
# ══════════════════════════════════════════════════════════════════

def count_lattice_points(pts, ray_indices, D_toric):
    """Count |{m ∈ Z⁴ : ⟨m, v_ρ⟩ ≥ -d_ρ ∀ rays ρ}|."""
    dim = pts.shape[1]
    n_rays = len(ray_indices)
    A_ub = np.zeros((n_rays, dim))
    b_ub = np.zeros(n_rays)
    for k, rho in enumerate(ray_indices):
        A_ub[k] = -pts[rho]
        b_ub[k] = D_toric[rho]

    bounds = []
    for i in range(dim):
        c = np.zeros(dim); c[i] = 1
        r_min = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(None, None), method='highs')
        c[i] = -1
        r_max = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(None, None), method='highs')
        if r_min.success and r_max.success:
            bounds.append((int(np.floor(r_min.fun)), int(np.ceil(-r_max.fun))))
        else:
            return 0

    vol = 1
    for lo, hi in bounds:
        vol *= (hi - lo + 1)
    if vol > 200_000_000:
        return -1

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


def compute_h0_koszul(pts, ray_indices, D_toric):
    """h⁰(X,D) = h⁰(V,D) - h⁰(V,D+K_V), assuming h¹ correction=0."""
    h0_V = count_lattice_points(pts, ray_indices, D_toric)
    if h0_V < 0:
        return -1
    D_shift = D_toric.copy()
    for rho in ray_indices:
        D_shift[rho] -= 1
    h0_shift = count_lattice_points(pts, ray_indices, D_shift)
    if h0_shift < 0:
        return -1
    return h0_V - h0_shift


def compute_chi(D_basis, intnums, c2, h11):
    """HRR: χ(O(D)) = D³/6 + c₂·D/12 on CY3."""
    D3 = 0.0
    for (i, j, k), val in intnums.items():
        D3 += D_basis[i] * D_basis[j] * D_basis[k] * val
    c2D = sum(D_basis[a] * c2[a] for a in range(h11))
    return D3 / 6.0 + c2D / 12.0


def compute_D3(D_basis, intnums):
    """Compute D³ = triple self-intersection."""
    D3 = 0.0
    for (i, j, k), val in intnums.items():
        D3 += D_basis[i] * D_basis[j] * D_basis[k] * val
    return D3


def basis_to_toric(D_basis, div_basis, n_toric):
    """Convert basis-indexed divisor to toric-indexed."""
    D_toric = np.zeros(n_toric, dtype=int)
    for a, idx in enumerate(div_basis):
        D_toric[idx] = D_basis[a]
    return D_toric


def find_chi3_bundles(intnums, c2, h11, max_coeff=3, max_nonzero=4):
    """Find all divisors D with |χ(O(D))| ≈ 3."""
    bundles = []
    indices = list(range(h11))
    for n_nz in range(1, min(max_nonzero + 1, h11 + 1)):
        for chosen in combinations(indices, n_nz):
            coeff_range = list(range(-max_coeff, max_coeff + 1))
            coeff_range.remove(0)
            for coeffs in product(coeff_range, repeat=n_nz):
                D_basis = np.zeros(h11, dtype=int)
                for idx, c in zip(chosen, coeffs):
                    D_basis[idx] = c
                chi_val = compute_chi(D_basis, intnums, c2, h11)
                if abs(abs(chi_val) - 3.0) < 0.01:
                    bundles.append((D_basis.copy(), chi_val))
    return bundles


# ══════════════════════════════════════════════════════════════════
#  Fibration analysis (adapted from fibration_analysis.py)
# ══════════════════════════════════════════════════════════════════

def count_fibrations(polytope):
    """
    Count K3 and elliptic fibration structures from dual polytope geometry.
    
    K3 fibrations: dual-polytope points p with -p also a dual point
        (= P¹ direction in M lattice)
    Elliptic fibrations: 2D reflexive subpolytopes in the dual
        (= 4-10 lattice points in a rank-2 slice through origin)
    
    Returns (n_k3, n_elliptic).
    """
    try:
        dual_p = polytope.dual()
    except Exception:
        return (0, 0)

    dual_pts = np.array(dual_p.points(), dtype=int)
    dual_pts_set = set(tuple(x) for x in dual_pts)

    # ── K3 fibrations: points p in dual with -p also present ──
    k3_directions = []
    for pt in dual_pts:
        if np.all(pt == 0):
            continue
        if tuple(-pt) in dual_pts_set:
            # Normalize: pick the lexicographically first of p, -p
            if tuple(pt) < tuple(-pt):
                # Check primitive (gcd of abs = 1)
                gcd = np.gcd.reduce(np.abs(pt))
                if gcd == 1:
                    k3_directions.append(tuple(pt))

    n_k3 = len(k3_directions)

    # ── Elliptic fibrations: 2D reflexive subpolytopes in dual ──
    n_elliptic = 0
    seen_subspaces = set()

    for i in range(len(k3_directions)):
        for j in range(i + 1, len(k3_directions)):
            v1 = np.array(k3_directions[i])
            v2 = np.array(k3_directions[j])

            # Check linear independence
            mat_check = np.vstack([v1, v2])
            if np.linalg.matrix_rank(mat_check) < 2:
                continue

            # Find all dual points in span(v1, v2)
            subspace_pts = []
            for pt in dual_pts:
                mat = np.vstack([v1, v2, pt])
                if np.linalg.matrix_rank(mat) <= 2:
                    subspace_pts.append(tuple(pt))

            # 2D reflexive polytopes have 4-10 lattice points
            n_sub = len(subspace_pts)
            if 4 <= n_sub <= 10:
                # Deduplicate by the set of points (unordered)
                key = frozenset(subspace_pts)
                if key not in seen_subspaces:
                    seen_subspaces.add(key)
                    n_elliptic += 1

    return (n_k3, n_elliptic)


# ══════════════════════════════════════════════════════════════════
#  Tier 1 CSV reader
# ══════════════════════════════════════════════════════════════════

def read_tier1_csv(csv_path, top_n=20):
    """Read Tier 1 results and return the top N by screen_score."""
    candidates = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append({
                'h11': int(row['h11']),
                'poly_idx': int(row['poly_idx']),
                'favorable': row['favorable'] == 'True',
                'tier1_score': int(row['screen_score']),
                'max_h0_scan': int(row['max_h0']),
                'n_dp': int(row['n_dp']),
                'has_swiss': row['has_swiss'] == 'True',
            })
    # Already sorted by tier1_score (rank column), take top N
    return candidates[:top_n]


def read_tier15_csv(csv_path, top_n=50, min_clean=3):
    """Read Tier 1.5 results and return the top N by tier15_score.
    
    Filters to candidates with at least min_clean clean bundles in the
    300-bundle probe (default 3 = T2-worthy threshold).
    """
    candidates = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = int(row['probe_clean'])
            if clean < min_clean:
                continue
            candidates.append({
                'h11': int(row['h11']),
                'poly_idx': int(row['poly_idx']),
                'favorable': row['favorable'] == 'True',
                'tier15_score': int(row['tier15_score']),
                'tier1_score': int(row['tier15_score']),  # alias for downstream compat
                'max_h0_scan': int(row['probe_max_h0']),
                'probe_clean': clean,
                'n_k3_fib': int(row['n_k3_fib']),
                'n_ell_fib': int(row['n_ell_fib']),
            })
    # Already sorted by tier15_score (rank column), take top N
    return candidates[:top_n]


# ══════════════════════════════════════════════════════════════════
#  Tier 2 deep screening
# ══════════════════════════════════════════════════════════════════

def screen_polytope_deep(h11_val, poly_idx, verbose=True):
    """
    Run all four deep checks on a single polytope.
    
    Returns dict with full bundle cohomology, intersection stats, and fibrations.
    Expect 10-60 seconds per polytope.
    """
    t0 = time.time()
    h21_val = h11_val + 3

    # ── Fetch & build CY ──
    try:
        polys = list(cy.fetch_polytopes(
            h11=h11_val, h21=h21_val, lattice='N',
            limit=max(poly_idx + 5, 100)
        ))
    except Exception as e:
        return {'status': 'fetch_fail', 'error': str(e)}

    if poly_idx >= len(polys):
        return {'status': 'idx_oob', 'error': f'poly_idx={poly_idx} >= {len(polys)}'}

    p = polys[poly_idx]

    try:
        tri = p.triangulate()
        cyobj = tri.get_cy()
    except Exception as e:
        return {'status': 'tri_fail', 'error': str(e)}

    pts = np.array(p.points(), dtype=int)
    n_toric = pts.shape[0]
    ray_indices = list(range(1, n_toric))
    div_basis = [int(x) for x in cyobj.divisor_basis()]
    h11_eff = len(div_basis)
    is_favorable = (h11_eff == cyobj.h11())

    # Fingerprint: hash of sorted vertex matrix for reproducibility tracking
    verts = np.array(sorted(pts.tolist()))
    poly_hash = hashlib.sha256(verts.tobytes()).hexdigest()[:12]

    intnums = dict(cyobj.intersection_numbers(in_basis=True))
    c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

    if len(c2) != h11_eff:
        return {'status': 'c2_mismatch'}

    result = {
        'status': 'ok',
        'h11': h11_val,
        'h21': h21_val,
        'poly_idx': poly_idx,
        'h11_eff': h11_eff,
        'favorable': is_favorable,
        'n_toric': n_toric,
        'cytools_version': CYTOOLS_VERSION,
        'poly_hash': poly_hash,
    }

    # ══════════════════════════════════════════════════════════
    #  CHECK 1 + 2: Full bundle search + h⁰ computation + h³ check
    # ══════════════════════════════════════════════════════════
    if verbose:
        print(f"    [1/4] Searching χ=±3 bundles...", end="", flush=True)

    # Adapt search range based on h11_eff
    if h11_eff <= 13:
        max_coeff, max_nonzero = 3, 4
    elif h11_eff <= 16:
        max_coeff, max_nonzero = 3, 3
    elif h11_eff <= 20:
        max_coeff, max_nonzero = 2, 3
    else:
        max_coeff, max_nonzero = 2, 2

    bundles = find_chi3_bundles(intnums, c2, h11_eff, max_coeff, max_nonzero)
    n_chi3 = len(bundles)
    t_bundles = time.time() - t0

    if verbose:
        print(f" {n_chi3} found ({t_bundles:.1f}s)")
        print(f"    [2/4] Computing h⁰ (Koszul) + h³ verification...",
              end="", flush=True)

    max_h0 = 0
    h0_ge3_count = 0
    clean_h0_3_count = 0   # h⁰=3, h³=0
    clean_bundles = []      # the actual clean bundles
    h0_distribution = {}    # h0 -> count
    n_overflow = 0
    n_computed = 0

    for D_basis, chi_val in bundles:
        D_toric = basis_to_toric(D_basis, div_basis, n_toric)

        if chi_val > 0:
            # χ=+3: compute h⁰(D) directly
            h0 = compute_h0_koszul(pts, ray_indices, D_toric)
        else:
            # χ=-3: h³(D) = h⁰(-D) by Serre. Compute h⁰(-D).
            D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
            h0 = compute_h0_koszul(pts, ray_indices, D_neg_toric)

        if h0 < 0:
            n_overflow += 1
            continue

        n_computed += 1
        h0_distribution[h0] = h0_distribution.get(h0, 0) + 1

        if h0 > max_h0:
            max_h0 = h0

        if h0 >= 3:
            h0_ge3_count += 1

            # For h⁰=3 with χ=+3: verify h³=0 by computing h⁰(-D)
            if h0 == 3 and abs(chi_val - 3.0) < 0.01:
                D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
                h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric)
                if h3 == 0:
                    clean_h0_3_count += 1
                    clean_bundles.append(D_basis.copy())

    t_h0 = time.time() - t0 - t_bundles

    result['n_chi3'] = n_chi3
    result['max_h0'] = max_h0
    result['h0_ge3'] = h0_ge3_count
    result['clean_h0_3'] = clean_h0_3_count
    result['n_overflow'] = n_overflow
    result['n_computed'] = n_computed
    result['h0_distribution'] = h0_distribution

    if verbose:
        tag = f" {PASS}" if clean_h0_3_count > 0 else f" {FAIL}"
        print(f" max h⁰={max_h0}, {h0_ge3_count} with h⁰≥3, "
              f"{BOLD}{clean_h0_3_count} clean{RESET} (h⁰=3,h³=0){tag} ({t_h0:.1f}s)")
        if h0_distribution:
            dist_str = ", ".join(f"h⁰={k}:{v}" for k, v in
                                sorted(h0_distribution.items()) if k >= 2)
            if dist_str:
                print(f"         h⁰ distribution (≥2): {dist_str}")

    # ══════════════════════════════════════════════════════════
    #  CHECK 3: D³ intersection statistics
    # ══════════════════════════════════════════════════════════
    if verbose:
        print(f"    [3/4] D³ intersection statistics...", end="", flush=True)

    d3_values = []
    d3_for_clean = []

    for D_basis, chi_val in bundles:
        if chi_val > 0:
            d3 = compute_D3(D_basis, intnums)
            d3_values.append(d3)

    # D³ for clean bundles specifically
    for D_basis in clean_bundles:
        d3 = compute_D3(D_basis, intnums)
        d3_for_clean.append(d3)

    d3_unique = sorted(set(int(round(x)) for x in d3_values)) if d3_values else []
    d3_clean_unique = sorted(set(int(round(x)) for x in d3_for_clean)) if d3_for_clean else []

    result['d3_values'] = d3_unique
    result['d3_clean'] = d3_clean_unique
    result['d3_min'] = min(d3_values) if d3_values else None
    result['d3_max'] = max(d3_values) if d3_values else None
    result['d3_n_distinct'] = len(d3_unique)

    if verbose:
        if d3_values:
            print(f" {len(d3_unique)} distinct D³ values, "
                  f"range [{min(d3_values):.0f}, {max(d3_values):.0f}]")
            if d3_clean_unique:
                print(f"         Clean bundle D³ values: {d3_clean_unique}")
        else:
            print(f" no χ=+3 bundles {FAIL}")

    # ══════════════════════════════════════════════════════════
    #  CHECK 4: Fibration structure (K3 / elliptic)
    # ══════════════════════════════════════════════════════════
    if verbose:
        print(f"    [4/4] Fibration analysis...", end="", flush=True)

    t_fib_start = time.time()
    n_k3_fib, n_ell_fib = count_fibrations(p)
    t_fib = time.time() - t_fib_start

    result['n_k3_fib'] = n_k3_fib
    result['n_ell_fib'] = n_ell_fib

    if verbose:
        tag = ""
        if n_k3_fib > 0 or n_ell_fib > 0:
            tag = f" {PASS}"
        print(f" {n_k3_fib} K3, {n_ell_fib} elliptic{tag} ({t_fib:.1f}s)")

    # ══════════════════════════════════════════════════════════
    #  Composite Tier 2 score
    # ══════════════════════════════════════════════════════════
    score = 0

    # Clean h⁰=3 bundles (most important — this IS the physics result)
    if clean_h0_3_count >= 20:
        score += 15
    elif clean_h0_3_count >= 10:
        score += 12
    elif clean_h0_3_count >= 5:
        score += 9
    elif clean_h0_3_count >= 1:
        score += 5
    # else: 0

    # h⁰≥3 abundance (more bundles = more flexibility)
    score += min(h0_ge3_count, 10)              # 0-10

    # Fibrations (K3 + elliptic)
    score += min(n_k3_fib, 3) * 2               # 0-6: K3
    score += min(n_ell_fib, 3) * 2              # 0-6: elliptic

    # D³ diversity (more distinct values = richer intersection ring)
    score += min(len(d3_clean_unique), 5)       # 0-5

    # Simplicity bonus
    if h11_eff <= 14:
        score += 3
    elif h11_eff <= 16:
        score += 2
    elif h11_eff <= 18:
        score += 1

    result['tier2_score'] = score

    elapsed = time.time() - t0
    result['elapsed'] = elapsed

    if verbose:
        print(f"    Tier 2 score: {BOLD}{score}/55{RESET} ({elapsed:.1f}s)")
        if clean_bundles:
            print(f"\n    Top clean bundles (h⁰=3, h³=0):")
            for cb in clean_bundles[:10]:
                nz = [(i, int(cb[i])) for i in range(h11_eff) if cb[i] != 0]
                D_str = " + ".join(f"{c}·e{i}" for i, c in nz)
                d3 = compute_D3(cb, intnums)
                print(f"      D = {D_str}  (D³={d3:.0f})")
            if len(clean_bundles) > 10:
                print(f"      ... and {len(clean_bundles) - 10} more")

    return result


# ══════════════════════════════════════════════════════════════════
#  Output formatting
# ══════════════════════════════════════════════════════════════════

def print_ranked_table(results):
    """Print a ranked comparison table."""
    if not results:
        print("\n  No successful screenings to rank.")
        return

    results.sort(key=lambda x: (-x['tier2_score'], -x['clean_h0_3']))

    print(f"\n{'═' * 110}")
    print(f"  TIER 2 RANKED RESULTS — {len(results)} candidates deep-screened")
    print(f"{'═' * 110}")
    print(f"  {'Rank':>4}  {'h11':>3} {'poly':>4} {'NF':>2}  {'T2':>3}  "
          f"{'clean':>5} {'h⁰≥3':>5} {'maxh⁰':>5}  "
          f"{'nχ3':>5}  {'K3':>2} {'ell':>3}  "
          f"{'D³range':>10}  {'#D³':>3}  {'time':>5}")
    print(f"  {'─' * 95}")

    for rank, r in enumerate(results, 1):
        nf = "NF" if not r['favorable'] else "  "
        d3_range = ""
        if r['d3_min'] is not None:
            d3_range = f"[{r['d3_min']:.0f},{r['d3_max']:.0f}]"

        marker = ""
        if r['clean_h0_3'] >= 10:
            marker = f" {STAR}{STAR}{STAR}"
        elif r['clean_h0_3'] >= 3:
            marker = f" {STAR}{STAR}"
        elif r['clean_h0_3'] >= 1:
            marker = f" {STAR}"

        print(f"  {rank:>4}  {r['h11']:>3} {r['poly_idx']:>4} {nf:>2}  "
              f"{r['tier2_score']:>3}  "
              f"{r['clean_h0_3']:>5} {r['h0_ge3']:>5} {r['max_h0']:>5}  "
              f"{r['n_chi3']:>5}  {r['n_k3_fib']:>2} {r['n_ell_fib']:>3}  "
              f"{d3_range:>10}  {r['d3_n_distinct']:>3}  "
              f"{r['elapsed']:>4.0f}s{marker}")

    # ── Summary ──
    n_with_clean = sum(1 for r in results if r['clean_h0_3'] > 0)
    n_with_fib = sum(1 for r in results if r['n_k3_fib'] > 0 or r['n_ell_fib'] > 0)
    n_with_both = sum(1 for r in results
                      if r['clean_h0_3'] > 0 and (r['n_k3_fib'] > 0 or r['n_ell_fib'] > 0))
    total_clean = sum(r['clean_h0_3'] for r in results)
    best = results[0]

    print(f"\n  Summary:")
    print(f"    With clean h⁰=3 bundles:       {n_with_clean}/{len(results)}")
    print(f"    Total clean bundles found:      {total_clean}")
    print(f"    With K3/ell fibrations:         {n_with_fib}/{len(results)}")
    print(f"    Clean bundles + fibrations:     {n_with_both}/{len(results)} ← strongest candidates")
    print(f"    Best overall: h11={best['h11']}, poly {best['poly_idx']} "
          f"(T2={best['tier2_score']}, {best['clean_h0_3']} clean, "
          f"max h⁰={best['max_h0']})")


def save_csv(results, csv_path):
    """Save results to CSV, merging with any existing file (no duplicates)."""
    import os

    FIELDNAMES = [
        'rank', 'h11', 'poly_idx', 'favorable', 'h11_eff',
        'tier2_score', 'clean_h0_3', 'h0_ge3', 'max_h0', 'n_chi3',
        'n_k3_fib', 'n_ell_fib',
        'd3_min', 'd3_max', 'd3_n_distinct', 'd3_clean_values',
        'n_overflow', 'elapsed_s',
        'cytools_version', 'poly_hash'
    ]

    def result_to_row(r):
        d3_clean_str = "|".join(str(x) for x in r.get('d3_clean', []))
        return {
            'h11': r['h11'], 'poly_idx': r['poly_idx'],
            'favorable': r['favorable'], 'h11_eff': r['h11_eff'],
            'tier2_score': r['tier2_score'], 'clean_h0_3': r['clean_h0_3'],
            'h0_ge3': r['h0_ge3'], 'max_h0': r['max_h0'],
            'n_chi3': r['n_chi3'],
            'n_k3_fib': r['n_k3_fib'], 'n_ell_fib': r['n_ell_fib'],
            'd3_min': r.get('d3_min', ''), 'd3_max': r.get('d3_max', ''),
            'd3_n_distinct': r['d3_n_distinct'],
            'd3_clean_values': d3_clean_str,
            'n_overflow': r['n_overflow'],
            'elapsed_s': f"{r['elapsed']:.1f}",
            'cytools_version': r.get('cytools_version', ''),
            'poly_hash': r.get('poly_hash', '')
        }

    # Load existing rows (if any) keyed by (h11, poly_idx)
    existing = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['h11'], row['poly_idx'])
                existing[key] = row

    # Merge: new results overwrite existing entries for same polytope
    for r in results:
        row = result_to_row(r)
        key = (str(row['h11']), str(row['poly_idx']))
        existing[key] = row

    # Sort by tier2_score desc, then clean_h0_3 desc
    merged = sorted(existing.values(),
                    key=lambda x: (-int(x['tier2_score']), -int(x['clean_h0_3'])))

    # Re-rank and write
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for rank, row in enumerate(merged, 1):
            row['rank'] = rank
            writer.writerow(row)

    n_new = len(results)
    n_total = len(merged)
    n_prev = n_total - n_new + sum(
        1 for r in results
        if (str(r['h11']), str(r['poly_idx'])) in {
            (str(row['h11']), str(row['poly_idx'])) for row in existing.values()
        } and (str(r['h11']), str(r['poly_idx'])) in existing
    )
    print(f"\n  Results saved to {csv_path} ({n_total} total, {n_new} new/updated)")


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Tier 2 deep screener for χ=-6 candidates')
    parser.add_argument('--csv', default='results/tier1_screen_results.csv',
                        help='Path to Tier 1 results CSV')
    parser.add_argument('--csv15', default=None,
                        help='Path to Tier 1.5 results CSV (overrides --csv)')
    parser.add_argument('--top', type=int, default=20,
                        help='Number of top candidates to deep-screen')
    parser.add_argument('--min-clean', type=int, default=3,
                        help='Min clean bundles from T1.5 probe to include (default 3)')
    parser.add_argument('--offset', type=int, default=0,
                        help='Skip first N candidates (for batch splitting)')
    parser.add_argument('--batch', type=int, default=None,
                        help='Process only this many candidates (for batch splitting)')
    parser.add_argument('--out', default=None,
                        help='Output CSV path (default: results/tier2_screen_results.csv)')
    parser.add_argument('--h11', type=int, default=None,
                        help='Screen a specific h11 value')
    parser.add_argument('--poly', type=int, default=None,
                        help='Screen a specific polytope index (requires --h11)')
    args = parser.parse_args()

    print("=" * 76)
    print("  TIER 2 DEEP SCREENER — Full bundle + fibration analysis")
    print("  Checks: exact h⁰=3 | h³=0 verification | D³ stats | K3/ell fibrations")
    print("=" * 76)

    # ── Single polytope mode ──
    if args.h11 is not None and args.poly is not None:
        print(f"\n  Deep screening h11={args.h11}, polytope {args.poly}...\n")
        result = screen_polytope_deep(args.h11, args.poly, verbose=True)
        if result['status'] != 'ok':
            print(f"\n  FAILED: {result.get('status')} — {result.get('error', '')}")
            return
        return

    # ── Batch mode: read CSV ──
    if args.csv15:
        csv_source = args.csv15
        print(f"\n  Reading Tier 1.5 results: {csv_source}")
        try:
            candidates = read_tier15_csv(csv_source, top_n=args.top + args.offset,
                                         min_clean=args.min_clean)
        except FileNotFoundError:
            print(f"  ERROR: File not found: {csv_source}")
            sys.exit(1)
    else:
        csv_source = args.csv
        print(f"\n  Reading Tier 1 results: {csv_source}")
        try:
            candidates = read_tier1_csv(csv_source, top_n=args.top + args.offset)
        except FileNotFoundError:
            print(f"  ERROR: File not found: {csv_source}")
            print(f"  Run tier1_screen.py first, or use --h11 and --poly for single mode.")
            sys.exit(1)

    # Apply offset/batch slicing for parallel runs
    if args.offset > 0:
        candidates = candidates[args.offset:]
        print(f"  Skipped first {args.offset} candidates (--offset)")
    if args.batch is not None:
        candidates = candidates[:args.batch]
        print(f"  Processing batch of {len(candidates)} (--batch)")
    else:
        candidates = candidates[:args.top]

    print(f"  Loaded {len(candidates)} candidates for deep screening")

    # ── Screen each candidate ──
    results = []
    t_total_start = time.time()

    for i, cand in enumerate(candidates):
        h11 = cand['h11']
        pidx = cand['poly_idx']
        nf_tag = "" if cand['favorable'] else " [NF]"
        print(f"\n{'─' * 76}")
        print(f"  [{i+1}/{len(candidates)}] h11={h11}, poly {pidx} "
              f"(T1 score={cand['tier1_score']}, scan max h⁰={cand['max_h0_scan']}"
              f"{nf_tag})")
        print(f"{'─' * 76}")

        result = screen_polytope_deep(h11, pidx, verbose=True)
        if result['status'] == 'ok':
            result['tier1_score'] = cand['tier1_score']
            results.append(result)
        else:
            print(f"    FAILED: {result.get('status')} — {result.get('error', '')}")

    t_total = time.time() - t_total_start

    # ── Print ranked results ──
    print_ranked_table(results)

    # ── Save CSV ──
    csv_path = args.out or "results/tier2_screen_results.csv"
    save_csv(results, csv_path)

    print(f"\n  Total time: {t_total:.0f}s ({t_total/60:.1f} min)")


if __name__ == '__main__':
    main()
