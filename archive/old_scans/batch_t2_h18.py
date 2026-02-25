#!/usr/bin/env python3
"""batch_t2_h18.py — Run full T2 screening on h11=18 T0.25 pass candidates.

Reads tier025_h18*.csv files, selects candidates with max_h0 >= MIN_H0
and favorable=True, then runs T2 (bundle count + fibrations) in parallel.

Usage:
    python3 batch_t2_h18.py [--min-h0 5] [--workers 14] [--all]
    
    --min-h0 N    Minimum max_h0 from T0.25 scan (default: 5)
    --workers N   Parallel workers (default: 4)
    --all         Include non-favorable polytopes too
"""

import csv
import sys
import os
import argparse
import time
import concurrent.futures
from collections import defaultdict

import cytools as cy
import numpy as np
from cytools.config import enable_experimental_features
enable_experimental_features()

from cy_compute import (
    compute_h0_koszul,
    compute_D3,
    basis_to_toric,
    find_chi3_bundles,
    count_fibrations,
    precompute_vertex_data,
)

PASS_sym = "\033[92m✓\033[0m"
FAIL_sym = "\033[91m✗\033[0m"
STAR_sym = "\033[93m★\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ══════════════════════════════════════════════════════════════════
#  Load candidates from T0.25 CSVs
# ══════════════════════════════════════════════════════════════════

T025_CSVS = [
    "results/tier025_h18.csv",
    "results/tier025_h18_off100000.csv",
]

def load_candidates(min_h0=5, include_nonfav=False):
    """Read T0.25 CSVs and return candidates sorted by max_h0 desc."""
    seen = set()
    candidates = []
    for csv_path in T025_CSVS:
        if not os.path.exists(csv_path):
            print(f"  [warn] Not found: {csv_path}", flush=True)
            continue
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['status'] != 'pass':
                    continue
                poly_idx = int(row['poly_idx'])
                if poly_idx in seen:
                    continue
                seen.add(poly_idx)
                max_h0 = int(row['max_h0'])
                favorable = row['favorable'] == 'True'
                if max_h0 < min_h0:
                    continue
                if not favorable and not include_nonfav:
                    continue
                candidates.append({
                    'h11': int(row['h11']),
                    'h21': int(row['h21']),
                    'poly_idx': poly_idx,
                    'favorable': favorable,
                    'h11_eff': int(row['h11_eff']),
                    'n_chi3': int(row['n_chi3']),
                    'max_h0_025': max_h0,
                    'first_hit_at': int(row['first_hit_at']),
                })
    # Sort by max_h0 desc, then poly_idx asc
    candidates.sort(key=lambda x: (-x['max_h0_025'], x['poly_idx']))
    return candidates


# ══════════════════════════════════════════════════════════════════
#  T2 screen for a single polytope
# ══════════════════════════════════════════════════════════════════

def screen_poly(cand, max_bundles=3000, min_h0=3):
    """Run full T2 screening on one polytope.
    
    Returns dict with all results.
    """
    h11 = cand['h11']
    poly_idx = cand['poly_idx']
    t_start = time.time()
    result = dict(cand)
    result.update({
        'n_bundles_checked': 0,
        'n_clean': 0,
        'max_h0_t2': 0,
        'n_k3': 0,
        'n_elliptic': 0,
        'error': '',
        'elapsed': 0.0,
        'status': 'FAIL',
    })

    try:
        # Fetch polytope
        polys = list(cy.fetch_polytopes(h11=h11, h21=cand['h21'], lattice='N',
                                        limit=max(poly_idx + 5, 100)))
        if poly_idx >= len(polys):
            result['error'] = f'poly_idx {poly_idx} out of range ({len(polys)})'
            return result
        p = polys[poly_idx]

        # Triangulate and build CY
        tri = p.triangulate()
        cyobj = tri.get_cy()

        # Extract raw arrays for cy_compute functions (matching tier2_screen.py)
        pts = np.array(p.points(), dtype=int)
        n_toric = pts.shape[0]
        ray_indices = list(range(1, n_toric))
        div_basis = [int(x) for x in cyobj.divisor_basis()]
        h11_eff = len(div_basis)

        intnums = dict(cyobj.intersection_numbers(in_basis=True))
        c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

        if len(c2) != h11_eff:
            result['error'] = 'c2_mismatch'
            return result

        # Bundle search parameters scaled by dimension
        if h11_eff <= 13:
            max_coeff, max_nonzero = 3, 4
        elif h11_eff <= 16:
            max_coeff, max_nonzero = 3, 3
        elif h11_eff <= 20:
            max_coeff, max_nonzero = 2, 3
        else:
            max_coeff, max_nonzero = 2, 2

        bundles = find_chi3_bundles(intnums, c2, h11_eff, max_coeff, max_nonzero)
        result['n_bundles_checked'] = len(bundles)

        # Precompute vertex data once for fast h⁰ bounding
        _precomp = precompute_vertex_data(pts, ray_indices)

        n_clean = 0
        max_h0_seen = 0

        for D_basis, chi_val in bundles:
            D_toric = basis_to_toric(D_basis, div_basis, n_toric)

            if chi_val > 0:
                # χ=+3: compute h⁰(D) directly
                h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=_precomp)
            else:
                # χ=-3: h³(D) = h⁰(-D) by Serre duality
                D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
                h0 = compute_h0_koszul(pts, ray_indices, D_neg_toric, _precomp=_precomp)

            if h0 < 0:
                continue

            if h0 > max_h0_seen:
                max_h0_seen = h0

            # For χ=+3, h⁰=3: verify h³=0 by computing h⁰(-D)
            if h0 == 3 and abs(chi_val - 3.0) < 0.01:
                D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
                h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric, _precomp=_precomp)
                if h3 == 0:
                    n_clean += 1

        result['n_clean'] = n_clean
        result['max_h0_t2'] = max_h0_seen

        # Fibrations (only if clean bundles found)
        if n_clean > 0:
            try:
                n_k3, n_ell = count_fibrations(p)
                result['n_k3'] = int(n_k3)
                result['n_elliptic'] = int(n_ell)
            except Exception as e:
                result['n_k3'] = -1
                result['n_elliptic'] = -1

        result['elapsed'] = time.time() - t_start
        result['status'] = 'PASS' if n_clean > 0 else 'NONE'

    except Exception as e:
        result['error'] = str(e)[:120]
        result['elapsed'] = time.time() - t_start

    return result


# ══════════════════════════════════════════════════════════════════
#  Output
# ══════════════════════════════════════════════════════════════════

FIELDNAMES = [
    'h11', 'h21', 'poly_idx', 'favorable', 'h11_eff', 'n_chi3',
    'max_h0_025', 'first_hit_at',
    'n_bundles_checked', 'n_clean', 'max_h0_t2',
    'n_k3', 'n_elliptic', 'elapsed', 'status', 'error',
]

OUT_CSV = "results/tier2_h18.csv"


def write_result(writer, result, f_out):
    """Write one result row, flush immediately."""
    row = {k: result.get(k, '') for k in FIELDNAMES}
    writer.writerow(row)
    f_out.flush()


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Batch T2 screen for h11=18")
    parser.add_argument('--min-h0', type=int, default=5,
                        help='Min max_h0 from T0.25 scan (default: 5)')
    parser.add_argument('--workers', type=int, default=4,
                        help='Parallel workers (default: 4)')
    parser.add_argument('--all', action='store_true',
                        help='Include non-favorable polytopes')
    parser.add_argument('--max-bundles', type=int, default=5000,
                        help='Max bundles per polytope (default: 5000)')
    parser.add_argument('--resume', action='store_true',
                        help='Skip already completed poly_idx in output CSV')
    args = parser.parse_args()

    candidates = load_candidates(min_h0=args.min_h0, include_nonfav=getattr(args, 'all', False))

    # Resume: skip already done
    done_polys = set()
    if args.resume and os.path.exists(OUT_CSV):
        with open(OUT_CSV) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_polys.add(int(row['poly_idx']))
        candidates = [c for c in candidates if c['poly_idx'] not in done_polys]
        print(f"  [resume] Skipping {len(done_polys)} already done polys", flush=True)

    print("=" * 70, flush=True)
    print(f"  TIER 2 BATCH SCREEN  h11=18", flush=True)
    print(f"  Candidates: {len(candidates)} (min_h0>={args.min_h0})", flush=True)
    print(f"  Workers: {args.workers}  Max bundles: {args.max_bundles}", flush=True)
    print("=" * 70, flush=True)
    print(f"  {'poly_idx':>8}  {'max_h0':>6}  {'n_clean':>7}  {'k3':>4}  {'ell':>4}  {'time':>6}  status", flush=True)
    print(f"  {'-'*8}  {'-'*6}  {'-'*7}  {'-'*4}  {'-'*4}  {'-'*6}  ------", flush=True)

    t_global = time.time()
    n_done = 0
    n_pass = 0
    champions = []

    # Write CSV header  
    write_header = not (args.resume and os.path.exists(OUT_CSV))
    f_out = open(OUT_CSV, 'a' if args.resume else 'w', newline='')
    writer = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
    if write_header:
        writer.writeheader()

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(screen_poly, c, args.max_bundles): c for c in candidates}
        for fut in concurrent.futures.as_completed(futs):
            r = fut.result()
            n_done += 1
            if r['status'] == 'PASS':
                n_pass += 1
                champions.append(r)
            write_result(writer, r, f_out)

            sym = STAR_sym if r['n_clean'] > 0 else ('  ' if not r['error'] else '! ')
            err_note = f"  ERR: {r['error'][:40]}" if r['error'] else ''
            print(f"  {r['poly_idx']:>8}  {r['max_h0_025']:>6}  {r['n_clean']:>7}"
                  f"  {r['n_k3']:>4}  {r['n_elliptic']:>4}"
                  f"  {r['elapsed']:>5.1f}s  {r['status']}{err_note}", flush=True)

    f_out.close()

    elapsed_total = time.time() - t_global

    print()
    print("=" * 70, flush=True)
    print(f"  DONE — {n_done} screened, {n_pass} PASS, {elapsed_total:.0f}s total", flush=True)
    print(flush=True)

    if champions:
        champions.sort(key=lambda x: (-x['n_clean'], -x['max_h0_t2']))
        print(f"  TOP CANDIDATES (n_clean>0), sorted by n_clean:", flush=True)
        print(f"  {'poly_idx':>8}  {'max_h0':>6}  {'n_clean':>7}  {'k3':>4}  {'ell':>4}", flush=True)
        for r in champions:
            print(f"  {r['poly_idx']:>8}  {r['max_h0_t2']:>6}  {r['n_clean']:>7}"
                  f"  {r['n_k3']:>4}  {r['n_elliptic']:>4}", flush=True)
    else:
        print("  No PASS candidates found.", flush=True)


if __name__ == '__main__':
    main()
