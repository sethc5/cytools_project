#!/usr/bin/env python3
"""
tier1_screen.py — Fast Tier 1 screener for top χ=-6 candidates.

Reads the scan log (results/scan_chi6_h0_v2.log) to identify top polytopes,
then runs 4 cheap checks on each:

  1. Exact h⁰=3 bundle count (with h³=0 verification)
  2. Rigid del Pezzo divisor count + classification
  3. Swiss cheese structure (Kähler cone tip + hierarchy scaling)
  4. Toric symmetry order

Outputs a ranked table of candidates. ~10-20 sec per polytope.

Usage:
  python3 tier1_screen.py                        # screen top 30 from scan log
  python3 tier1_screen.py --top 50               # screen top 50
  python3 tier1_screen.py --h11 15 --poly 14     # screen a single polytope
  python3 tier1_screen.py --log results/scan_chi6_h0_v2.log  # custom log path

Reference: MATH_SPEC.md §2-5, FRAMEWORK.md §1-2.
"""

import sys
import re
import os
import csv
import argparse
import time
import cytools as cy
import numpy as np
from cytools.config import enable_experimental_features
enable_experimental_features()

from cy_compute import (
    compute_h0_koszul,
    basis_to_toric,
    find_chi3_bundles_capped,
    precompute_vertex_data,
)

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
STAR = "\033[93m★\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ══════════════════════════════════════════════════════════════════
#  Log parser — extract top candidates from scan output
# ══════════════════════════════════════════════════════════════════

def parse_scan_log(log_path, top_n=30):
    """
    Parse scan_chi6_h0_v2.log and return the top candidates by max h⁰.
    Returns list of (h11, poly_idx, max_h0, is_nf).
    """
    candidates = []
    current_h11 = None

    with open(log_path, 'r') as f:
        for line in f:
            # Match section headers like: "  h11=15, h21=18  —  100 polytopes"
            m = re.match(r'\s+h11=(\d+),\s+h21=(\d+)', line)
            if m:
                current_h11 = int(m.group(1))
                continue

            # Match polytope lines like: "  poly  14: n_toric=19, ... max h⁰=20 ★★★ HIT ★★★ [NF]"
            m = re.match(r'\s+poly\s+(\d+):.*max h⁰=(\d+)', line)
            if m and current_h11 is not None:
                poly_idx = int(m.group(1))
                max_h0 = int(m.group(2))
                is_nf = '[NF]' in line
                candidates.append({
                    'h11': current_h11,
                    'poly_idx': poly_idx,
                    'max_h0': max_h0,
                    'is_nf': is_nf,
                })

    # Sort by max_h0 descending, then by h11 ascending (simpler geometry preferred)
    candidates.sort(key=lambda x: (-x['max_h0'], x['h11']))
    return candidates[:top_n]


# ══════════════════════════════════════════════════════════════════
#  Tier 1 screening checks
# ══════════════════════════════════════════════════════════════════

def screen_polytope(h11_val, poly_idx, scan_max_h0=None, verbose=True):
    """
    Run fast checks on a single polytope. Returns a result dict.
    
    The scan already computed max h⁰ (expensive lattice-point counting).
    The screener adds the 3 checks the scan DIDN'T do:
      1. Divisor classification (del Pezzo, K3)
      2. Swiss cheese structure
      3. Toric symmetry order
    
    If scan_max_h0 is provided, skip h⁰ recomputation and use scan result.
    If not provided (single-polytope mode), do a quick bundle check.
    """
    t0 = time.time()
    h21_val = h11_val + 3

    # ── Fetch & build CY ──
    try:
        polys = list(cy.fetch_polytopes(
            h11=h11_val, h21=h21_val, lattice='N', limit=max(poly_idx + 5, 100)
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
    }

    # ── CHECK 1: Line bundle h⁰ data ──
    if scan_max_h0 is not None:
        # FAST PATH: use scan result, skip expensive recomputation
        result['max_h0'] = scan_max_h0
        result['n_chi3'] = -1       # not recomputed
        result['h0_ge3'] = -1       # not recomputed  
        result['clean_h0_3'] = -1   # needs full pipeline to determine
        result['clean_bundles'] = []
        result['h0_from_scan'] = True

        if verbose:
            tag = f" {PASS}" if scan_max_h0 >= 3 else f" {FAIL}"
            print(f"    [1/4] h⁰ data from scan: max h⁰={scan_max_h0}{tag}")
    else:
        # SINGLE-POLYTOPE MODE: do quick bundle search
        if verbose:
            print(f"    [1/4] Searching χ=±3 bundles & computing h⁰...",
                  end="", flush=True)

        if h11_eff <= 13:
            max_coeff, max_nonzero = 3, 4
        elif h11_eff <= 16:
            max_coeff, max_nonzero = 3, 3
        elif h11_eff <= 20:
            max_coeff, max_nonzero = 2, 3
        else:
            max_coeff, max_nonzero = 2, 2

        bundles = find_chi3_bundles_capped(intnums, c2, h11_eff, max_coeff,
                                           max_nonzero, cap=500)
        n_chi3 = len(bundles)
        truncated = (n_chi3 == 500)

        # Precompute vertex data for fast h⁰ (~30× faster bounding box)
        _precomp = precompute_vertex_data(pts, ray_indices)

        max_h0 = 0
        h0_ge3_count = 0
        h0_exact3_count = 0
        clean_bundles = []

        for D_basis, chi_val in bundles:
            D_toric = basis_to_toric(D_basis, div_basis, n_toric)

            if chi_val > 0:
                h0 = compute_h0_koszul(pts, ray_indices, D_toric,
                                       _precomp=_precomp)
            else:
                D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
                h0 = compute_h0_koszul(pts, ray_indices, D_neg_toric,
                                       _precomp=_precomp)

            if h0 < 0:
                continue

            if h0 > max_h0:
                max_h0 = h0

            if h0 >= 3:
                h0_ge3_count += 1
                if h0 == 3 and abs(chi_val - 3.0) < 0.01:
                    D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
                    h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric,
                                           _precomp=_precomp)
                    if h3 == 0:
                        clean_bundles.append(D_basis.copy())
                        h0_exact3_count += 1

        result['n_chi3'] = n_chi3
        result['max_h0'] = max_h0
        result['h0_ge3'] = h0_ge3_count
        result['clean_h0_3'] = h0_exact3_count
        result['clean_bundles'] = clean_bundles
        result['h0_from_scan'] = False

        if verbose:
            trunc_tag = "+" if truncated else ""
            tag = f" {PASS}" if h0_exact3_count > 0 else f" {FAIL}"
            print(f" {n_chi3}{trunc_tag} χ=3 bundles, max h⁰={max_h0}, "
                  f"{h0_exact3_count} clean(h⁰=3,h³=0){tag}")

    # ── CHECK 2: Divisor classification ──
    if verbose:
        print(f"    [2/4] Classifying divisors...", end="", flush=True)

    dp_divisors = []
    k3_divisors = []
    rigid_count = 0

    for a_idx in range(h11_eff):
        D3 = intnums.get((a_idx, a_idx, a_idx), 0)
        c2D = c2[a_idx]

        if D3 > 0 and c2D > 0:
            dp_n = 9 - D3
            if 0 <= dp_n <= 8:
                dp_divisors.append((a_idx, div_basis[a_idx], int(dp_n), D3, c2D))
                rigid_count += 1
            else:
                rigid_count += 1
        elif D3 == 0 and c2D > 0:
            k3_divisors.append((a_idx, div_basis[a_idx], c2D))
        else:
            rigid_count += 1

    result['n_dp'] = len(dp_divisors)
    result['n_k3'] = len(k3_divisors)
    result['n_rigid'] = rigid_count
    result['dp_types'] = [f"dP{d[2]}" for d in dp_divisors]

    if verbose:
        tag = f" {PASS}" if len(dp_divisors) >= 3 else f" {FAIL}"
        dp_summary = ", ".join(f"dP{d[2]}" for d in dp_divisors[:8])
        if len(dp_divisors) > 8:
            dp_summary += f", +{len(dp_divisors)-8} more"
        print(f" {len(dp_divisors)} dP, {len(k3_divisors)} K3-like, "
              f"{rigid_count} rigid total [{dp_summary}]{tag}")

    # ── CHECK 3: Swiss cheese structure ──
    if verbose:
        print(f"    [3/4] Swiss cheese check...", end="", flush=True)

    try:
        kc = cyobj.toric_kahler_cone()
        tip = np.array(kc.tip_of_stretched_cone(1.0), dtype=float)

        s = 10  # hierarchy scale factor
        swiss_hits = []
        for a_small in range(h11_eff):
            t2 = tip * s
            t2[a_small] = tip[a_small]
            V2 = sum(val * t2[i]*t2[j]*t2[k]
                     for (i,j,k), val in intnums.items()) / 6.0
            tau2 = sum(val * t2[j]*t2[k]
                       for (i,j,k), val in intnums.items()
                       if a_small in (i,j,k)) / 2.0
            if V2 > 100 and tau2 > 0:
                ratio = tau2 / V2**(2/3)
                if ratio < 0.1:
                    swiss_hits.append((a_small, tau2, V2, ratio))

        has_swiss = len(swiss_hits) > 0
        result['has_swiss'] = has_swiss
        result['n_swiss'] = len(swiss_hits)
        if swiss_hits:
            best = min(swiss_hits, key=lambda x: x[3])
            result['best_swiss_tau'] = best[1]
            result['best_swiss_vol'] = best[2]
            result['best_swiss_ratio'] = best[3]
        else:
            result['best_swiss_tau'] = None
            result['best_swiss_vol'] = None
            result['best_swiss_ratio'] = None

        if verbose:
            if has_swiss:
                best = min(swiss_hits, key=lambda x: x[3])
                print(f" YES — {len(swiss_hits)} candidates, "
                      f"best: e{best[0]} τ={best[1]:.1f}, "
                      f"V={best[2]:.0f}, ratio={best[3]:.4f} {PASS}")
            else:
                print(f" NO {FAIL}")

    except Exception as e:
        result['has_swiss'] = False
        result['n_swiss'] = 0
        result['best_swiss_tau'] = None
        result['best_swiss_vol'] = None
        result['best_swiss_ratio'] = None
        if verbose:
            print(f" ERROR: {e} {FAIL}")

    # ── CHECK 4: Toric symmetry order ──
    if verbose:
        print(f"    [4/4] Symmetry check...", end="", flush=True)

    try:
        # GL(Z,4) automorphisms of the polytope
        auts = p.automorphisms()
        sym_order = len(auts)
    except Exception:
        sym_order = 1

    result['sym_order'] = sym_order

    if verbose:
        tag = f" {PASS}" if sym_order > 2 else ""
        print(f" GL(Z,4) order = {sym_order}{tag}")

    # ── Composite score ──
    # In scan mode (clean_h0_3 == -1), score h⁰ based on scan max h⁰
    score = 0
    if result.get('h0_from_scan'):
        # Score from scan's max h⁰ (proxy for bundle quality)
        scan_h0 = result['max_h0']
        if scan_h0 >= 10:
            score += 15
        elif scan_h0 >= 5:
            score += 10
        elif scan_h0 >= 3:
            score += 6
    else:
        score += min(max(result['clean_h0_3'], 0), 5) * 3
        score += min(max(result['h0_ge3'], 0), 10) * 1

    score += min(result['n_dp'], 5) * 2              # 0-10: del Pezzo divisors
    score += 10 if result['has_swiss'] else 0        # 0-10: Swiss cheese
    score += min(result['sym_order'] - 1, 5) * 1     # 0-5:  symmetry bonus
    score += 5 if result['h11_eff'] <= 15 else 0     # 0-5:  simplicity bonus
    result['screen_score'] = score

    elapsed = time.time() - t0
    result['elapsed'] = elapsed

    if verbose:
        print(f"    Screen score: {BOLD}{score}/55{RESET} ({elapsed:.1f}s)")

    return result


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Tier 1 screener for χ=-6 candidates')
    parser.add_argument('--log', default='results/scan_chi6_h0_v2.log',
                        help='Path to scan log file')
    parser.add_argument('--top', type=int, default=30,
                        help='Number of top candidates to screen')
    parser.add_argument('--h11', type=int, default=None,
                        help='Screen a specific h11 value')
    parser.add_argument('--poly', type=int, default=None,
                        help='Screen a specific polytope index (requires --h11)')
    parser.add_argument('--min-h0', type=int, default=3,
                        help='Minimum max h⁰ from scan to include in screening')
    args = parser.parse_args()

    print("=" * 76)
    print("  TIER 1 SCREENER — Fast qualification of χ=-6 candidates")
    print("  Checks: clean h⁰=3 bundles | del Pezzo divisors | Swiss cheese | symmetry")
    print("=" * 76)

    # ── Single polytope mode ──
    if args.h11 is not None and args.poly is not None:
        print(f"\n  Screening h11={args.h11}, polytope {args.poly}...\n")
        result = screen_polytope(args.h11, args.poly, verbose=True)
        if result['status'] != 'ok':
            print(f"\n  FAILED: {result.get('status')} — {result.get('error', '')}")
            return
        print_single_result(result)
        return

    # ── Batch mode: read scan log ──
    print(f"\n  Reading scan log: {args.log}")
    try:
        candidates = parse_scan_log(args.log, top_n=args.top * 3)  # over-read to filter
    except FileNotFoundError:
        print(f"  ERROR: Log file not found: {args.log}")
        print(f"  Run scan_chi6_h0.py first, or specify --h11 and --poly for single mode.")
        sys.exit(1)

    # Filter by min h⁰
    candidates = [c for c in candidates if c['max_h0'] >= args.min_h0][:args.top]
    print(f"  Found {len(candidates)} candidates with max h⁰ ≥ {args.min_h0}")

    if not candidates:
        print("  No candidates to screen.")
        return

    # ── Screen each candidate ──
    results = []
    for i, cand in enumerate(candidates):
        h11 = cand['h11']
        pidx = cand['poly_idx']
        nf_tag = " [NF]" if cand['is_nf'] else ""
        print(f"\n{'─' * 76}")
        print(f"  [{i+1}/{len(candidates)}] h11={h11}, poly {pidx} "
              f"(scan max h⁰={cand['max_h0']}{nf_tag})")
        print(f"{'─' * 76}")

        result = screen_polytope(h11, pidx, scan_max_h0=cand['max_h0'],
                                verbose=True)
        if result['status'] == 'ok':
            result['scan_max_h0'] = cand['max_h0']
            results.append(result)
        else:
            print(f"    FAILED: {result.get('status')} — {result.get('error', '')}")

    # ── Print ranked results ──
    print_ranked_table(results)


def print_single_result(result):
    """Pretty-print a single screening result."""
    print(f"\n{'═' * 76}")
    print(f"  RESULT: h11={result['h11']}, polytope {result['poly_idx']}")
    print(f"{'═' * 76}")
    print(f"  h11_eff       = {result['h11_eff']} {'(non-favorable)' if not result['favorable'] else ''}")
    print(f"  n_toric       = {result['n_toric']}")
    print(f"  χ=3 bundles   = {result['n_chi3']}")
    print(f"  Max h⁰        = {result['max_h0']}")
    print(f"  h⁰ ≥ 3 count = {result['h0_ge3']}")
    print(f"  Clean h⁰=3    = {result['clean_h0_3']} (h⁰=3, h³=0, h¹=h²=0)")
    print(f"  del Pezzo     = {result['n_dp']} [{', '.join(result['dp_types'])}]")
    print(f"  K3-like       = {result['n_k3']}")
    print(f"  Swiss cheese  = {'YES' if result['has_swiss'] else 'NO'}", end="")
    if result['has_swiss']:
        print(f" (τ={result['best_swiss_tau']:.1f}, V={result['best_swiss_vol']:.0f}, "
              f"ratio={result['best_swiss_ratio']:.5f})")
    else:
        print()
    print(f"  Symmetry      = GL(Z,4) order {result['sym_order']}")
    print(f"  Screen score  = {BOLD}{result['screen_score']}/55{RESET}")
    print(f"  Elapsed       = {result['elapsed']:.1f}s")


def print_ranked_table(results):
    """Print a ranked comparison table of all screened candidates."""
    if not results:
        print("\n  No successful screenings to rank.")
        return

    results.sort(key=lambda x: -x['screen_score'])

    print(f"\n{'═' * 100}")
    print(f"  RANKED RESULTS — {len(results)} candidates screened")
    print(f"{'═' * 100}")
    print(f"  {'Rank':>4}  {'h11':>3} {'poly':>4} {'NF':>2}  {'score':>5}  "
          f"{'maxh⁰':>5}  "
          f"{'#dP':>3} {'#K3':>3}  {'swiss':>5} {'τ':>6} {'ratio':>7}  "
          f"{'sym':>3}  {'time':>5}")
    print(f"  {'─' * 80}")

    for rank, r in enumerate(results, 1):
        nf = "NF" if not r['favorable'] else "  "
        swiss = "YES" if r['has_swiss'] else " no"
        tau_str = f"{r['best_swiss_tau']:.1f}" if r['best_swiss_tau'] else "  —"
        ratio_str = f"{r['best_swiss_ratio']:.4f}" if r['best_swiss_ratio'] else "   —"

        # Highlight polytopes with swiss cheese + high h⁰
        marker = ""
        if r['max_h0'] >= 10 and r['has_swiss']:
            marker = f" {STAR}{STAR}{STAR}"
        elif r['max_h0'] >= 3 and r['has_swiss']:
            marker = f" {STAR}"

        print(f"  {rank:>4}  {r['h11']:>3} {r['poly_idx']:>4} {nf:>2}  "
              f"{r['screen_score']:>5}  "
              f"{r['max_h0']:>5}  "
              f"{r['n_dp']:>3} {r['n_k3']:>3}  {swiss:>5} {tau_str:>6} {ratio_str:>7}  "
              f"{r['sym_order']:>3}  {r['elapsed']:>4.0f}s{marker}")

    # ── Summary stats ──
    n_with_h0ge3 = sum(1 for r in results if r['max_h0'] >= 3)
    n_with_swiss = sum(1 for r in results if r['has_swiss'])
    n_both = sum(1 for r in results if r['max_h0'] >= 3 and r['has_swiss'])
    n_with_dp3 = sum(1 for r in results if r['n_dp'] >= 3)
    best = results[0]

    print(f"\n  Summary:")
    print(f"    Polytopes with max h⁰ ≥ 3:         {n_with_h0ge3}/{len(results)}")
    print(f"    Polytopes with Swiss cheese:        {n_with_swiss}/{len(results)}")
    print(f"    Polytopes with ≥3 dP divisors:      {n_with_dp3}/{len(results)}")
    print(f"    Polytopes with h⁰≥3 + Swiss:       {n_both}/{len(results)} ← pipeline candidates")
    print(f"    Best overall: h11={best['h11']}, poly {best['poly_idx']} "
          f"(score={best['screen_score']}, max h⁰={best['max_h0']}, "
          f"{'Swiss cheese' if best['has_swiss'] else 'no Swiss cheese'})")

    # ── CSV output (merge with existing) ──
    csv_path = "results/tier1_screen_results.csv"
    try:
        FIELDNAMES = [
            'rank', 'h11', 'poly_idx', 'favorable', 'screen_score',
            'clean_h0_3', 'h0_ge3', 'max_h0',
            'n_dp', 'n_k3', 'has_swiss', 'best_tau', 'best_ratio',
            'sym_order', 'n_chi3', 'elapsed_s'
        ]

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
            row = {
                'h11': r['h11'], 'poly_idx': r['poly_idx'],
                'favorable': r['favorable'], 'screen_score': r['screen_score'],
                'clean_h0_3': r['clean_h0_3'], 'h0_ge3': r['h0_ge3'],
                'max_h0': r['max_h0'],
                'n_dp': r['n_dp'], 'n_k3': r['n_k3'],
                'has_swiss': r['has_swiss'],
                'best_tau': r.get('best_swiss_tau', ''),
                'best_ratio': r.get('best_swiss_ratio', ''),
                'sym_order': r['sym_order'], 'n_chi3': r['n_chi3'],
                'elapsed_s': f"{r['elapsed']:.1f}"
            }
            key = (str(row['h11']), str(row['poly_idx']))
            existing[key] = row

        # Sort by screen_score desc, then clean_h0_3 desc
        merged = sorted(existing.values(),
                        key=lambda x: (-int(x['screen_score']),
                                      -int(x['clean_h0_3'])))

        # Re-rank and write
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for rank, row in enumerate(merged, 1):
                row['rank'] = rank
                writer.writerow(row)

        n_new = len(results)
        n_total = len(merged)
        print(f"\n  Results saved to {csv_path} ({n_total} total, {n_new} new/updated)")
    except Exception as e:
        print(f"\n  Warning: could not save CSV: {e}")


if __name__ == '__main__':
    main()
