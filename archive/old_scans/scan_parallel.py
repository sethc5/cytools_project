#!/usr/bin/env python3
"""
Parallel scanner for χ=-6 polytopes in the Kreuzer-Skarke database.

Uses multiprocessing to scan polytopes across all CPU cores.
Produces output compatible with tier1_screen.py's log parser.

Usage:
    python scan_parallel.py --h11 15           # scan all h15 polytopes
    python scan_parallel.py --h11 15 16 17     # scan h15-h17
    python scan_parallel.py --h11 16 --limit 500  # first 500 at h16
    python scan_parallel.py --h11 15 16 17 --workers 4  # explicit worker count

Output saved to results/scan_h{min}-h{max}.log (compatible with tier1_screen.py)
and results/scan_h{min}-h{max}.csv (machine-readable).
"""

import argparse
import csv
import multiprocessing as mp
import os
import sys
import time

import numpy as np
import cytools as cy
from cytools.config import enable_experimental_features
enable_experimental_features()

from cy_compute import (
    find_chi3_bundles,
    compute_h0_koszul,
    basis_to_toric,
    precompute_vertex_data,
)


# ──────────────────────────────────────────────────────────────
#  Worker function (runs in subprocess)
# ──────────────────────────────────────────────────────────────

def _scan_one(args):
    """Scan a single polytope. Designed for multiprocessing Pool.map.

    Args: (polytope_vertices, poly_idx, h11_val, h21_val)
    Returns: result dict
    """
    vert, poly_idx, h11_val, h21_val = args

    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()

        p = Polytope(vert)
        tri = p.triangulate()
        cyobj = tri.get_cy()
    except Exception as e:
        return {
            'status': 'tri_fail', 'error': str(e),
            'h11_val': h11_val, 'h21_val': h21_val, 'poly_idx': poly_idx,
        }

    h11 = cyobj.h11()
    pts = np.array(p.points(), dtype=int)
    n_toric = pts.shape[0]
    ray_indices = list(range(1, n_toric))
    div_basis = [int(x) for x in cyobj.divisor_basis()]
    intnums = dict(cyobj.intersection_numbers(in_basis=True))
    c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

    if not np.all(pts[0] == 0):
        return {
            'status': 'origin_fail',
            'h11_val': h11_val, 'h21_val': h21_val, 'poly_idx': poly_idx,
        }

    h11_eff = len(div_basis)
    is_favorable = (h11_eff == h11)

    if len(c2) != h11_eff:
        return {
            'status': 'c2_mismatch', 'n_toric': n_toric, 'h11': h11,
            'h11_eff': h11_eff, 'c2_len': len(c2),
            'h11_val': h11_val, 'h21_val': h21_val, 'poly_idx': poly_idx,
        }

    # Adapt search range
    if h11_eff <= 15:
        max_coeff, max_nonzero = 3, 3
    elif h11_eff <= 20:
        max_coeff, max_nonzero = 2, 3
    else:
        max_coeff, max_nonzero = 2, 2

    bundles = find_chi3_bundles(intnums, c2, h11_eff, max_coeff, max_nonzero)

    if not bundles:
        return {
            'status': 'no_chi3', 'n_toric': n_toric, 'h11': h11,
            'h11_eff': h11_eff, 'favorable': is_favorable,
            'n_chi3': 0, 'max_h0': 0, 'h0_3_count': 0,
            'h11_val': h11_val, 'h21_val': h21_val, 'poly_idx': poly_idx,
        }

    _precomp = precompute_vertex_data(pts, ray_indices)

    max_h0 = 0
    best_bundle = None
    h0_3_count = 0
    n_computed = 0

    for D_basis, chi in bundles:
        D_toric = basis_to_toric(D_basis, div_basis, n_toric)

        if chi > 0:
            h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=_precomp)
        else:
            D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
            h0 = compute_h0_koszul(pts, ray_indices, D_neg, _precomp=_precomp)

        n_computed += 1
        if h0 < 0:
            continue
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
        'h11_val': h11_val,
        'h21_val': h21_val,
        'poly_idx': poly_idx,
    }


# ──────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Parallel χ=-6 polytope scanner')
    parser.add_argument('--h11', type=int, nargs='+', required=True,
                        help='h¹¹ values to scan (e.g. 15 16 17)')
    parser.add_argument('--limit', type=int, default=0,
                        help='Max polytopes per h11 (0 = all)')
    parser.add_argument('--workers', type=int, default=0,
                        help='Number of worker processes (0 = all cores)')
    parser.add_argument('--resume', type=str, default=None,
                        help='Path to existing CSV to resume from')
    args = parser.parse_args()

    n_workers = args.workers if args.workers > 0 else mp.cpu_count()
    h11_list = sorted(args.h11)
    limit = args.limit if args.limit > 0 else 100_000

    h_min, h_max = min(h11_list), max(h11_list)
    tag = f"h{h_min}" if h_min == h_max else f"h{h_min}-h{h_max}"
    log_path = f"results/scan_{tag}.log"
    csv_path = f"results/scan_{tag}.csv"

    # Resume support: load already-scanned (h11, poly_idx) pairs
    done_set = set()
    if args.resume and os.path.exists(args.resume):
        with open(args.resume) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_set.add((int(row['h11']), int(row['poly_idx'])))
        print(f"  Resuming: {len(done_set)} polytopes already done from {args.resume}")
        csv_path = args.resume  # append to same file

    os.makedirs("results", exist_ok=True)

    print("=" * 72)
    print(f"  PARALLEL SCAN: χ=-6 polytopes")
    print(f"  h¹¹ = {h11_list}, limit={args.limit or 'all'}, workers={n_workers}")
    print("=" * 72)

    # Open log + CSV for writing
    log_f = open(log_path, 'w')
    csv_mode = 'a' if done_set else 'w'
    csv_f = open(csv_path, csv_mode, newline='')
    csv_writer = csv.writer(csv_f)
    if not done_set:
        csv_writer.writerow([
            'h11', 'h21', 'poly_idx', 'favorable', 'h11_eff',
            'n_chi3', 'n_computed', 'max_h0', 'h0_3_count', 'status'
        ])

    total_scanned = 0
    total_hits = 0
    all_hits = []
    t_global = time.time()

    for h11_val in h11_list:
        h21_val = h11_val + 3
        t_fetch = time.time()

        try:
            polys = cy.fetch_polytopes(
                h11=h11_val, h21=h21_val, lattice='N', limit=limit
            )
        except Exception as e:
            msg = f"  FETCH FAILED for h11={h11_val}: {e}"
            print(msg)
            log_f.write(msg + '\n')
            continue

        n_polys = len(polys)
        fetch_time = time.time() - t_fetch

        header = (f"\n{'─' * 60}\n"
                  f"  h11={h11_val}, h21={h21_val}  —  {n_polys} polytopes"
                  f" (fetched in {fetch_time:.1f}s)\n"
                  f"{'─' * 60}")
        print(header)
        log_f.write(header + '\n')

        # Prepare work items — serialize polytope vertices for pickling
        work = []
        for idx, p in enumerate(polys):
            if (h11_val, idx) in done_set:
                continue
            verts = np.array(p.points(), dtype=int).tolist()
            work.append((verts, idx, h11_val, h21_val))

        if not work:
            msg = f"  All {n_polys} polytopes already done (resume)"
            print(msg)
            log_f.write(msg + '\n')
            continue

        n_todo = len(work)
        skipped = n_polys - n_todo
        if skipped > 0:
            print(f"  Skipping {skipped} already done, scanning {n_todo}")

        # Process in parallel with progress reporting
        t_scan = time.time()
        results = []
        completed = 0

        with mp.Pool(n_workers) as pool:
            for result in pool.imap_unordered(_scan_one, work, chunksize=4):
                results.append(result)
                completed += 1

                # Progress every 50 polytopes or 30 seconds
                if completed % 50 == 0 or completed == n_todo:
                    elapsed = time.time() - t_scan
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (n_todo - completed) / rate if rate > 0 else 0
                    hits_so_far = sum(1 for r in results
                                      if r.get('max_h0', 0) >= 3)
                    msg = (f"  [{completed}/{n_todo}] "
                           f"{elapsed:.0f}s elapsed, "
                           f"{rate:.1f} poly/s, "
                           f"ETA {eta:.0f}s, "
                           f"{hits_so_far} hits so far")
                    print(msg, flush=True)

        # Sort results by poly_idx for deterministic output
        results.sort(key=lambda r: r.get('poly_idx', 0))

        scan_time = time.time() - t_scan
        h_hits = 0

        for r in results:
            idx = r.get('poly_idx', '?')
            status = r.get('status', '?')

            # Write CSV row
            csv_writer.writerow([
                h11_val, h21_val, idx,
                r.get('favorable', ''),
                r.get('h11_eff', ''),
                r.get('n_chi3', 0),
                r.get('n_computed', 0),
                r.get('max_h0', 0),
                r.get('h0_3_count', 0),
                status,
            ])

            # Write log line (compatible with tier1_screen.py parser)
            if status == 'ok':
                max_h0 = r['max_h0']
                n_chi3 = r['n_chi3']
                fav_tag = '' if r.get('favorable', True) else ' [NF]'
                tag = ""
                if max_h0 >= 3:
                    tag = " ★★★ HIT ★★★"
                    h_hits += 1
                    all_hits.append(r)
                elif max_h0 >= 2:
                    tag = " (h⁰=2)"
                line = (f"  poly {idx:4d}: n_toric={r['n_toric']:2d}, "
                        f"h11_eff={r.get('h11_eff', '?'):2}, "
                        f"{n_chi3:5d} χ=3 bundles, "
                        f"max h⁰={max_h0}{tag}{fav_tag}")
            elif status == 'no_chi3':
                fav_tag = '' if r.get('favorable', True) else ' [NF]'
                line = (f"  poly {idx:4d}: n_toric={r['n_toric']:2d}, "
                        f"NO χ=3 bundles found{fav_tag}")
            elif status == 'c2_mismatch':
                line = (f"  poly {idx:4d}: SKIP (c2 size {r.get('c2_len')} ≠ "
                        f"h11_eff={r.get('h11_eff')}, h11={r.get('h11')})")
            else:
                line = f"  poly {idx:4d}: {status}"

            log_f.write(line + '\n')

        csv_f.flush()
        log_f.flush()

        total_scanned += len(results)
        total_hits += h_hits

        summary = (f"  h11={h11_val}: {len(results)} scanned in {scan_time:.0f}s "
                   f"({len(results)/scan_time:.1f} poly/s), "
                   f"{h_hits} hits (h⁰≥3)")
        print(summary)
        log_f.write(summary + '\n')

    # ── Global summary ──
    total_time = time.time() - t_global
    footer = (f"\n{'=' * 72}\n"
              f"  SUMMARY\n"
              f"{'=' * 72}\n"
              f"  Total scanned: {total_scanned}\n"
              f"  Total hits (h⁰≥3): {total_hits}\n"
              f"  Total time: {total_time:.0f}s ({total_time/60:.1f} min)\n"
              f"  Rate: {total_scanned/total_time:.1f} poly/s\n")

    if all_hits:
        footer += f"\n{'─' * 60}\n  ★★★ h⁰ ≥ 3 HITS ★★★\n{'─' * 60}\n"
        all_hits.sort(key=lambda h: (-h['max_h0'], h['h11_val'], h['poly_idx']))
        for h in all_hits:
            fav_tag = '' if h.get('favorable', True) else ' [NF]'
            footer += (f"  h11={h['h11_val']}, poly {h['poly_idx']:4d}: "
                       f"max h⁰={h['max_h0']:2d}, "
                       f"{h['h0_3_count']:4d} bundles with h⁰≥3{fav_tag}\n")

    # Distribution of max h⁰
    h0_dist = {}
    # Re-read from all results we have
    footer += f"\n  Output: {log_path} (log), {csv_path} (csv)\n"
    footer += "\nDone.\n"

    print(footer)
    log_f.write(footer)

    log_f.close()
    csv_f.close()


if __name__ == '__main__':
    main()
