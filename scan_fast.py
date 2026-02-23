#!/usr/bin/env python3
"""
Tier 0.25 fast pre-filter for χ=-6 polytopes.

Scans all χ=3 bundles per polytope but STOPS as soon as the first
h⁰ ≥ 3 bundle is found ("early termination"). Combined with the
min_h0=3 ambient bound (skips the second Koszul lattice-point count
when h⁰(V,D) < 3), this gives ~2-3× speedup over the full scan
with 100% recall — zero false negatives.

Two output modes:
    pass:  first h⁰ ≥ 3 found → polytope is worth full analysis
    skip:  no h⁰ ≥ 3 after all bundles → not interesting

Output:
    results/tier025_h{X}.csv

Usage:
    python scan_fast.py --h11 18                        # pre-filter h18
    python scan_fast.py --h11 17 18 19 --workers 4      # multi-h11
    python scan_fast.py --h11 15 --validate results/scan_h15.csv  # verify recall

Validation mode (--validate):
    Compares T0.25 results against a full-scan CSV to confirm recall.
"""

import argparse
import csv
import multiprocessing as mp
import os
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

def _scan_one_fast(args):
    """Tier 0.25: scan a polytope with early termination on first h⁰≥3.

    Key optimizations over the full scan:
      1. Stops as soon as first h⁰ ≥ 3 bundle is found (~10× faster on hits)
      2. Uses min_h0=3 early exit (skips second Koszul count when ambient h⁰ < 3)

    Args: (polytope_vertices, poly_idx, h11_val, h21_val)
    Returns: result dict with classification
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

    # Adapt search range (same as scan_parallel.py)
    if h11_eff <= 15:
        max_coeff, max_nonzero = 3, 3
    elif h11_eff <= 20:
        max_coeff, max_nonzero = 2, 3
    else:
        max_coeff, max_nonzero = 2, 2

    # Find χ=3 bundles (vectorized, fast — ~0.1s)
    bundles = find_chi3_bundles(intnums, c2, h11_eff, max_coeff, max_nonzero)

    if not bundles:
        return {
            'status': 'no_chi3', 'n_toric': n_toric, 'h11': h11,
            'h11_eff': h11_eff, 'favorable': is_favorable,
            'n_chi3': 0, 'n_computed': 0, 'max_h0': 0,
            'first_hit_at': -1, 'n_ambient_skip': 0,
            'h11_val': h11_val, 'h21_val': h21_val, 'poly_idx': poly_idx,
        }

    _precomp = precompute_vertex_data(pts, ray_indices)

    # ── Scan ALL bundles with early termination ──
    max_h0 = 0
    n_computed = 0
    n_ambient_skip = 0
    first_hit_at = -1

    for D_basis, chi in bundles:
        D_toric = basis_to_toric(D_basis, div_basis, n_toric)

        if chi > 0:
            h0 = compute_h0_koszul(pts, ray_indices, D_toric,
                                   _precomp=_precomp, min_h0=3)
        else:
            D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
            h0 = compute_h0_koszul(pts, ray_indices, D_neg,
                                   _precomp=_precomp, min_h0=3)

        n_computed += 1

        if h0 == 0:
            n_ambient_skip += 1

        if h0 > max_h0:
            max_h0 = h0

        # ── EARLY TERMINATION: first h⁰ ≥ 3 found → stop ──
        if h0 >= 3:
            first_hit_at = n_computed
            break

    status = 'pass' if max_h0 >= 3 else 'skip'

    return {
        'status': status,
        'n_toric': n_toric,
        'h11': h11,
        'h11_eff': h11_eff,
        'favorable': is_favorable,
        'n_chi3': len(bundles),
        'n_computed': n_computed,
        'max_h0': max_h0,
        'first_hit_at': first_hit_at,
        'n_ambient_skip': n_ambient_skip,
        'h11_val': h11_val,
        'h21_val': h21_val,
        'poly_idx': poly_idx,
    }


# ──────────────────────────────────────────────────────────────
#  Validation
# ──────────────────────────────────────────────────────────────

def validate_results(t025_results, full_csv_path):
    """Compare T0.25 results against full-scan CSV to measure recall."""
    ground_truth = {}
    with open(full_csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row['h11']), int(row['poly_idx']))
            ground_truth[key] = int(row.get('max_h0', 0))

    tp = fp = tn = fn = 0
    fn_list = []

    for r in t025_results:
        if r['status'] in ('tri_fail', 'origin_fail', 'c2_mismatch'):
            continue
        key = (r['h11_val'], r['poly_idx'])
        if key not in ground_truth:
            continue

        actual_hit = ground_truth[key] >= 3
        predicted_hit = r['status'] == 'pass'

        if predicted_hit and actual_hit:
            tp += 1
        elif predicted_hit and not actual_hit:
            fp += 1
        elif not predicted_hit and not actual_hit:
            tn += 1
        elif not predicted_hit and actual_hit:
            fn += 1
            fn_list.append({
                'h11': key[0], 'poly_idx': key[1],
                'actual_max_h0': ground_truth[key],
                'probe_max_h0': r.get('max_h0', 0),
            })

    total = tp + fp + tn + fn
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0

    return {
        'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn,
        'total': total, 'recall': recall, 'precision': precision,
        'false_negatives': fn_list,
    }


# ──────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Tier 0.25: fast χ=-6 polytope pre-filter with early termination')
    parser.add_argument('--h11', type=int, nargs='+', required=True,
                        help='h¹¹ values to scan (e.g. 18 19 20)')
    parser.add_argument('--limit', type=int, default=0,
                        help='Max polytopes per h11 (0 = all)')
    parser.add_argument('--workers', type=int, default=0,
                        help='Number of worker processes (0 = all cores)')
    parser.add_argument('--resume', type=str, default=None,
                        help='Path to existing T0.25 CSV to resume from')
    parser.add_argument('--offset', type=int, default=0,
                        help='Skip polytopes with index < offset (for batched runs)')
    parser.add_argument('--validate', type=str, default=None,
                        help='Path to full-scan CSV for recall validation')
    args = parser.parse_args()

    n_workers = args.workers if args.workers > 0 else mp.cpu_count()
    h11_list = sorted(args.h11)
    limit = args.limit if args.limit > 0 else 100_000
    offset = args.offset

    h_min, h_max = min(h11_list), max(h11_list)
    tag = f"h{h_min}" if h_min == h_max else f"h{h_min}-h{h_max}"
    if offset > 0:
        tag += f"_off{offset}"
    csv_path = f"results/tier025_{tag}.csv"

    # Resume support
    done_set = set()
    if args.resume and os.path.exists(args.resume):
        with open(args.resume) as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_set.add((int(row['h11']), int(row['poly_idx'])))
        print(f"  Resuming: {len(done_set)} polytopes already done")
        csv_path = args.resume

    os.makedirs("results", exist_ok=True)

    print("=" * 72)
    print(f"  TIER 0.25 FAST PRE-FILTER (early termination + min_h0 bound)")
    offset_msg = f", offset={offset}" if offset > 0 else ""
    print(f"  h¹¹ = {h11_list}, limit={args.limit or 'all'}{offset_msg}, workers={n_workers}")
    print("=" * 72)

    csv_mode = 'a' if done_set else 'w'
    csv_f = open(csv_path, csv_mode, newline='')
    csv_writer = csv.writer(csv_f)
    if not done_set:
        csv_writer.writerow([
            'h11', 'h21', 'poly_idx', 'favorable', 'h11_eff',
            'n_chi3', 'n_computed', 'max_h0', 'first_hit_at',
            'n_ambient_skip', 'status',
        ])

    total_scanned = 0
    total_pass = 0
    total_skip = 0
    total_bundles_saved = 0
    all_results = []
    t_global = time.time()

    for h11_val in h11_list:
        h21_val = h11_val + 3
        t_fetch = time.time()

        try:
            polys = cy.fetch_polytopes(
                h11=h11_val, h21=h21_val, lattice='N', limit=limit
            )
        except Exception as e:
            print(f"  FETCH FAILED for h11={h11_val}: {e}")
            continue

        n_polys = len(polys)
        fetch_time = time.time() - t_fetch

        print(f"\n{'─' * 60}")
        print(f"  h11={h11_val}, h21={h21_val}  —  {n_polys} polytopes"
              f" (fetched in {fetch_time:.1f}s)")
        print(f"{'─' * 60}")

        work = []
        for idx, p in enumerate(polys):
            if idx < offset:
                continue
            if (h11_val, idx) in done_set:
                continue
            verts = np.array(p.points(), dtype=int).tolist()
            work.append((verts, idx, h11_val, h21_val))

        if not work:
            print(f"  All {n_polys} polytopes already done (resume)")
            continue

        n_todo = len(work)
        skipped = n_polys - n_todo
        if skipped > 0:
            print(f"  Skipping {skipped} already done, scanning {n_todo}")

        t_scan = time.time()
        results = []
        completed = 0
        h_pass = 0
        h_skip = 0
        h_bundles_saved = 0

        with mp.Pool(n_workers) as pool:
            for result in pool.imap_unordered(_scan_one_fast, work, chunksize=4):
                results.append(result)
                all_results.append(result)
                completed += 1

                if result.get('status') == 'pass':
                    h_pass += 1
                    saved = result.get('n_chi3', 0) - result.get('n_computed', 0)
                    h_bundles_saved += max(0, saved)
                elif result.get('status') == 'skip':
                    h_skip += 1

                if completed % 100 == 0 or completed == n_todo:
                    elapsed = time.time() - t_scan
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (n_todo - completed) / rate if rate > 0 else 0
                    print(f"  [{completed}/{n_todo}] "
                          f"{elapsed:.0f}s, "
                          f"{rate:.1f} poly/s, "
                          f"ETA {eta:.0f}s, "
                          f"{h_pass} pass / {h_skip} skip",
                          flush=True)

        results.sort(key=lambda r: r.get('poly_idx', 0))

        for r in results:
            csv_writer.writerow([
                h11_val, h21_val, r.get('poly_idx', ''),
                r.get('favorable', ''),
                r.get('h11_eff', ''),
                r.get('n_chi3', 0),
                r.get('n_computed', 0),
                r.get('max_h0', 0),
                r.get('first_hit_at', -1),
                r.get('n_ambient_skip', 0),
                r.get('status', ''),
            ])
        csv_f.flush()

        scan_time = time.time() - t_scan
        total_scanned += len(results)
        total_pass += h_pass
        total_skip += h_skip
        total_bundles_saved += h_bundles_saved

        pass_rate = h_pass / len(results) * 100 if results else 0
        print(f"  h11={h11_val}: {len(results)} scanned in {scan_time:.0f}s "
              f"({len(results)/scan_time:.1f} poly/s), "
              f"{h_pass} pass ({pass_rate:.0f}%) / {h_skip} skip, "
              f"{h_bundles_saved:,} bundles saved by early term")

    # ── Global summary ──
    total_time = time.time() - t_global
    pass_rate = total_pass / total_scanned * 100 if total_scanned else 0

    print(f"\n{'=' * 72}")
    print(f"  TIER 0.25 SUMMARY")
    print(f"{'=' * 72}")
    print(f"  Total scanned:      {total_scanned}")
    print(f"  Pass (h⁰≥3):       {total_pass} ({pass_rate:.1f}%)")
    print(f"  Skip:               {total_skip}")
    print(f"  Bundles saved:      {total_bundles_saved:,} (by early termination)")
    print(f"  Total time:         {total_time:.0f}s ({total_time/60:.1f} min)")
    print(f"  Rate:               {total_scanned/total_time:.1f} poly/s")
    print(f"  Output:             {csv_path}")

    # Efficiency stats
    if all_results:
        pass_results = [r for r in all_results if r.get('status') == 'pass']
        if pass_results:
            hit_ats = [r['first_hit_at'] for r in pass_results
                       if r.get('first_hit_at', -1) > 0]
            n_chi3s = [r['n_chi3'] for r in pass_results if r.get('n_chi3', 0) > 0]
            if hit_ats and n_chi3s:
                avg_hit_at = np.mean(hit_ats)
                avg_n_chi3 = np.mean(n_chi3s)
                print(f"\n  Early termination stats (pass polytopes):")
                print(f"    Avg first hit at bundle #{avg_hit_at:.0f} / {avg_n_chi3:.0f}"
                      f" ({avg_hit_at/avg_n_chi3*100:.1f}% of bundles)")

    # Top passes
    passes = [r for r in all_results if r.get('status') == 'pass']
    if passes:
        passes.sort(key=lambda r: (r.get('first_hit_at', 9999),
                                    r.get('h11_val', 0),
                                    r.get('poly_idx', 0)))
        print(f"\n{'─' * 60}")
        print(f"  T0.25 PASSES — fastest hits first")
        print(f"{'─' * 60}")
        for r in passes[:20]:
            fav_tag = '' if r.get('favorable', True) else ' [NF]'
            print(f"  h11={r['h11_val']}, poly {r['poly_idx']:4d}: "
                  f"hit at #{r['first_hit_at']}/{r['n_chi3']}, "
                  f"max h⁰={r['max_h0']}"
                  f"{fav_tag}")

    csv_f.close()

    # ── Validation ──
    if args.validate:
        print(f"\n{'=' * 72}")
        print(f"  VALIDATION vs {args.validate}")
        print(f"{'=' * 72}")

        stats = validate_results(all_results, args.validate)
        print(f"  True Positives:   {stats['tp']:5d}")
        print(f"  True Negatives:   {stats['tn']:5d}")
        print(f"  False Positives:  {stats['fp']:5d}")
        print(f"  False Negatives:  {stats['fn']:5d}")
        print(f"  ────────────────────────")
        print(f"  Recall:     {stats['recall']:.4f} "
              f"({stats['tp']}/{stats['tp']+stats['fn']} actual hits caught)")
        print(f"  Precision:  {stats['precision']:.4f} "
              f"({stats['tp']}/{stats['tp']+stats['fp']} passes are real)")

        if stats['false_negatives']:
            print(f"\n  ⚠ FALSE NEGATIVES ({len(stats['false_negatives'])} missed):")
            for fn_item in stats['false_negatives'][:10]:
                print(f"    h11={fn_item['h11']}, poly {fn_item['poly_idx']}: "
                      f"actual max h⁰={fn_item['actual_max_h0']}")
        else:
            print(f"\n  ✓ PERFECT RECALL — zero false negatives!")

    print("\nDone.")


if __name__ == '__main__':
    main()
