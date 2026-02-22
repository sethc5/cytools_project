#!/usr/bin/env python3
"""
scan_expand_h15_17.py — B-19: Expand scan to limit=1000 at h11=15,16,17.

We previously scanned only 100 polytopes per h11 at these values.
KS database has 553 (h15), 5180 (h16), 38735 (h17).
This script scans up to 1000 per h11, skipping the first 100 already done.

Usage:
  python3 scan_expand_h15_17.py                  # all three h11 values
  python3 scan_expand_h15_17.py --h11 15         # just h11=15
  python3 scan_expand_h15_17.py --h11 16 17      # h11=16,17

Output: results/scan_expand_h15_17.csv  +  results/scan_expand_h15_17.log (tee)
"""

import sys
import csv
import time
import argparse
import cytools as cy
import numpy as np
from cytools.config import enable_experimental_features
enable_experimental_features()

# ── Import scan function from the main scanner ──
from scan_chi6_h0 import scan_polytope

LIMIT = 1000
SKIP = 100  # first 100 already scanned in v2


def main():
    parser = argparse.ArgumentParser(description='B-19: Expand scan at h11=15-17')
    parser.add_argument('--h11', type=int, nargs='+', default=[15, 16, 17],
                        help='h11 values to scan (default: 15 16 17)')
    parser.add_argument('--limit', type=int, default=LIMIT,
                        help='Max polytopes to fetch per h11 (default: 1000)')
    parser.add_argument('--skip', type=int, default=SKIP,
                        help='Skip first N already-scanned (default: 100)')
    parser.add_argument('--out', default='results/scan_expand_h15_17.csv',
                        help='Output CSV path')
    args = parser.parse_args()

    print("=" * 72)
    print("  B-19: EXPAND SCAN — h11=15–17, limit=1000")
    print(f"  Scanning polytopes {args.skip}..{args.limit} for each h11")
    print("=" * 72)

    t_start = time.time()
    all_results = []
    all_hits = []

    for h11_val in args.h11:
        h21_val = h11_val + 3
        print(f"\n{'═' * 60}")
        print(f"  h11={h11_val}, h21={h21_val} — fetching up to {args.limit} polytopes...")
        print(f"{'═' * 60}")

        t_h11 = time.time()
        try:
            polys = list(cy.fetch_polytopes(
                h11=h11_val, h21=h21_val, lattice='N', limit=args.limit
            ))
        except Exception as e:
            print(f"  ERROR fetching: {e}")
            continue

        total = len(polys)
        start_idx = min(args.skip, total)
        print(f"  Fetched {total} polytopes. Scanning indices {start_idx}..{total-1} "
              f"({total - start_idx} new)")

        for idx in range(start_idx, total):
            p = polys[idx]
            result = scan_polytope(p, idx, h11_val, h21_val)
            result['h11_val'] = h11_val
            result['h21_val'] = h21_val
            result['poly_idx'] = idx
            all_results.append(result)

            status = result['status']
            if status == 'ok':
                max_h0 = result['max_h0']
                n_chi3 = result['n_chi3']
                fav_tag = '' if result.get('favorable', True) else ' [NF]'
                tag = ""
                if max_h0 >= 3:
                    tag = " ★★★ HIT ★★★"
                    all_hits.append(result)
                elif max_h0 >= 2:
                    tag = " (h⁰=2)"
                print(f"  poly {idx:4d}: n_toric={result['n_toric']:2d}, "
                      f"h11_eff={result.get('h11_eff', '?'):2}, "
                      f"{n_chi3:4d} χ=3 bundles, max h⁰={max_h0}{tag}{fav_tag}")
            elif status == 'c2_mismatch':
                print(f"  poly {idx:4d}: SKIP (c2 mismatch)")
            else:
                print(f"  poly {idx:4d}: {status}")

        dt = time.time() - t_h11
        n_done = total - start_idx
        ok_h11 = [r for r in all_results if r.get('h11_val') == h11_val and r['status'] == 'ok']
        hits_h11 = [r for r in all_hits if r.get('h11_val') == h11_val]
        print(f"\n  h11={h11_val}: {n_done} scanned, {len(ok_h11)} ok, "
              f"{len(hits_h11)} hits (h⁰≥3) — {dt:.0f}s ({dt/max(n_done,1):.1f}s/poly)")

    # ── Save CSV ──
    ok_results = [r for r in all_results if r['status'] == 'ok']
    with open(args.out, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'h11', 'h21', 'poly_idx', 'favorable', 'h11_eff', 'n_toric',
            'n_chi3', 'n_computed', 'max_h0', 'h0_3_count', 'status'
        ])
        for r in ok_results:
            writer.writerow([
                r['h11_val'], r['h21_val'], r['poly_idx'],
                r.get('favorable', True), r.get('h11_eff', ''),
                r.get('n_toric', ''), r.get('n_chi3', 0),
                r.get('n_computed', 0), r.get('max_h0', 0),
                r.get('h0_3_count', 0), r['status']
            ])

    # ── Summary ──
    elapsed = time.time() - t_start
    print(f"\n{'═' * 72}")
    print(f"  B-19 SUMMARY")
    print(f"{'═' * 72}")
    print(f"  Total scanned: {len(all_results)}")
    print(f"  OK: {len(ok_results)}")
    print(f"  Hits (h⁰≥3): {len(all_hits)}")
    print(f"  Saved to: {args.out}")
    print(f"  Elapsed: {elapsed:.0f}s ({elapsed/60:.1f} min)")

    if all_hits:
        print(f"\n  Top hits by max h⁰:")
        all_hits.sort(key=lambda x: -x['max_h0'])
        for h in all_hits[:20]:
            print(f"    h11={h['h11_val']}, poly {h['poly_idx']}: "
                  f"max h⁰={h['max_h0']}, {h['h0_3_count']} with h⁰≥3")

    print(f"\n  Next: run tier1_screen.py on {args.out}")
    print(f"{'═' * 72}")


if __name__ == '__main__':
    main()
