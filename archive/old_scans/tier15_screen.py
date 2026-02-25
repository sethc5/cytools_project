#!/usr/bin/env python3
"""
tier15_screen.py — Tier 1.5 intermediate screener.

Two phases, run independently or together:

  Phase A (~2s/polytope): Add fibration count (K3 + elliptic) to Tier 1 data.
      Filters: must have at least 1 K3 or elliptic fibration.

  Phase B (~5-30s/polytope): Capped bundle probe.
      Searches first 300 χ=3 bundles, computes h⁰ via Koszul,
      counts how many have h⁰=3 with h³=0.
      Cheap proxy for the full T2 clean count.

Input:  results/tier1_screen_results.csv (or scan log directly)
Output: results/tier15_screen_results.csv

Usage:
  python3 tier15_screen.py                        # both phases, top 337
  python3 tier15_screen.py --phase a              # fibrations only  
  python3 tier15_screen.py --phase b              # bundle probe only
  python3 tier15_screen.py --top 100 --min-h0 5   # filter by scan h⁰
  python3 tier15_screen.py --skip-t2              # exclude polytopes already in T2 CSV
  python3 tier15_screen.py --h11 17 --poly 63     # single polytope mode

Reference: MATH_SPEC.md §4-5, FRAMEWORK.md §1-2.
"""

import sys
import csv
import re
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
    count_fibrations,
    precompute_vertex_data,
)

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
STAR = "\033[93m★\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ══════════════════════════════════════════════════════════════════
#  Input readers
# ══════════════════════════════════════════════════════════════════

def read_tier1_csv(csv_path, top_n=500, min_h0=3):
    """Read Tier 1 results."""
    candidates = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            max_h0 = int(row['max_h0'])
            if max_h0 < min_h0:
                continue
            candidates.append({
                'h11': int(row['h11']),
                'poly_idx': int(row['poly_idx']),
                'favorable': row['favorable'] == 'True',
                'tier1_score': int(row['screen_score']),
                'max_h0_scan': max_h0,
                'n_dp': int(row['n_dp']),
                'has_swiss': row['has_swiss'] == 'True',
            })
    return candidates[:top_n]


def read_tier2_csv(csv_path):
    """Read T2 CSV to get already-screened polytope set."""
    done = set()
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                done.add((int(row['h11']), int(row['poly_idx'])))
    except FileNotFoundError:
        pass
    return done


def parse_scan_log(log_path, min_h0=3):
    """Parse scan log directly (alternative to Tier 1 CSV)."""
    candidates = []
    current_h11 = None
    with open(log_path, 'r') as f:
        for line in f:
            m = re.match(r'\s+h11=(\d+),\s+h21=(\d+)', line)
            if m:
                current_h11 = int(m.group(1))
                continue
            m = re.match(r'\s+poly\s+(\d+):.*max h⁰=(\d+)', line)
            if m and current_h11 is not None:
                poly_idx = int(m.group(1))
                max_h0 = int(m.group(2))
                is_nf = '[NF]' in line
                if max_h0 >= min_h0:
                    candidates.append({
                        'h11': current_h11,
                        'poly_idx': poly_idx,
                        'max_h0_scan': max_h0,
                        'favorable': not is_nf,
                        'tier1_score': -1,
                        'n_dp': -1,
                        'has_swiss': None,
                    })
    candidates.sort(key=lambda x: (-x['max_h0_scan'], x['h11']))
    return candidates


# ══════════════════════════════════════════════════════════════════
#  Combined screening function
# ══════════════════════════════════════════════════════════════════

def screen_polytope_15(h11_val, poly_idx, phase='both', verbose=True):
    """
    Run Tier 1.5 screening on a single polytope.
    
    phase='a': fibration only (~2s)
    phase='b': bundle probe only (~5-30s)
    phase='both': both phases
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
        return {'status': 'idx_oob'}

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
        'poly_idx': poly_idx,
        'h11_eff': h11_eff,
        'favorable': is_favorable,
    }

    # ── Phase A: Fibrations ──
    if phase in ('a', 'both'):
        t_a = time.time()
        n_k3, n_ell = count_fibrations(p)
        result['n_k3_fib'] = n_k3
        result['n_ell_fib'] = n_ell
        result['phase_a_time'] = time.time() - t_a

        if verbose:
            tag = f" {PASS}" if (n_k3 + n_ell) > 0 else f" {FAIL}"
            print(f"    [A] Fibrations: {n_k3} K3, {n_ell} elliptic{tag} "
                  f"({result['phase_a_time']:.1f}s)")
    else:
        result['n_k3_fib'] = -1
        result['n_ell_fib'] = -1

    # ── Phase B: Bundle probe ──
    if phase in ('b', 'both'):
        t_b = time.time()

        # Adapt search range
        if h11_eff <= 13:
            max_coeff, max_nonzero = 3, 3  # cap nonzero at 3 for speed
        elif h11_eff <= 16:
            max_coeff, max_nonzero = 3, 3
        elif h11_eff <= 20:
            max_coeff, max_nonzero = 2, 3
        else:
            max_coeff, max_nonzero = 2, 2

        bundles = find_chi3_bundles_capped(
            intnums, c2, h11_eff, max_coeff, max_nonzero, cap=300
        )
        truncated = (len(bundles) >= 300)

        # Precompute vertex data for fast h⁰ (~30× faster bounding box)
        _precomp = precompute_vertex_data(pts, ray_indices)

        # Compute h⁰ for the probed bundles
        max_h0 = 0
        h0_ge3 = 0
        clean_count = 0

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
                h0_ge3 += 1
                # Check h³=0 for h⁰=3, χ=+3
                if h0 == 3 and abs(chi_val - 3.0) < 0.01:
                    D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
                    h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric,
                                           _precomp=_precomp)
                    if h3 == 0:
                        clean_count += 1

        result['probe_n_chi3'] = len(bundles)
        result['probe_truncated'] = truncated
        result['probe_max_h0'] = max_h0
        result['probe_h0_ge3'] = h0_ge3
        result['probe_clean'] = clean_count
        result['phase_b_time'] = time.time() - t_b

        if verbose:
            trunc = "+" if truncated else ""
            tag = f" {PASS}" if clean_count > 0 else f" {FAIL}"
            print(f"    [B] Bundle probe: {len(bundles)}{trunc} searched, "
                  f"max h⁰={max_h0}, {h0_ge3} with h⁰≥3, "
                  f"{BOLD}{clean_count} clean{RESET}{tag} "
                  f"({result['phase_b_time']:.1f}s)")
    else:
        result['probe_n_chi3'] = -1
        result['probe_truncated'] = False
        result['probe_max_h0'] = -1
        result['probe_h0_ge3'] = -1
        result['probe_clean'] = -1

    # ── Composite score ──
    score = 0

    # Bundle probe quality
    if result['probe_clean'] > 10:
        score += 15
    elif result['probe_clean'] > 3:
        score += 10
    elif result['probe_clean'] > 0:
        score += 5

    # h⁰≥3 abundance from probe
    score += min(result.get('probe_h0_ge3', 0), 10)

    # Fibrations
    if result['n_k3_fib'] > 0:
        score += min(result['n_k3_fib'], 3) * 2
    if result['n_ell_fib'] > 0:
        score += min(result['n_ell_fib'], 3) * 2

    # Simplicity
    if h11_eff <= 14:
        score += 3
    elif h11_eff <= 16:
        score += 2
    elif h11_eff <= 18:
        score += 1

    result['tier15_score'] = score

    elapsed = time.time() - t0
    result['elapsed'] = elapsed

    if verbose:
        print(f"    T1.5 score: {BOLD}{score}/49{RESET} ({elapsed:.1f}s)")

    return result


# ══════════════════════════════════════════════════════════════════
#  Output
# ══════════════════════════════════════════════════════════════════

def print_ranked_table(results):
    """Print ranked comparison table."""
    if not results:
        print("\n  No successful screenings.")
        return

    results.sort(key=lambda x: (-x['tier15_score'], -x.get('probe_clean', 0)))

    print(f"\n{'═' * 100}")
    print(f"  TIER 1.5 RANKED RESULTS — {len(results)} candidates")
    print(f"{'═' * 100}")
    print(f"  {'Rk':>3} {'h11':>3} {'poly':>4} {'NF':>2} {'T1.5':>4} "
          f"{'probed':>6} {'maxh⁰':>5} {'h⁰≥3':>5} {'clean':>5} "
          f"{'K3':>2} {'ell':>3} {'time':>5}")
    print(f"  {'─' * 85}")

    for rank, r in enumerate(results, 1):
        nf = "NF" if not r['favorable'] else "  "
        trunc = "+" if r.get('probe_truncated') else " "
        pc = r.get('probe_clean', -1)
        marker = ""
        if pc >= 10:
            marker = f" {STAR}{STAR}{STAR}"
        elif pc >= 3:
            marker = f" {STAR}{STAR}"
        elif pc >= 1:
            marker = f" {STAR}"

        print(f"  {rank:>3} {r['h11']:>3} {r['poly_idx']:>4} {nf:>2} "
              f"{r['tier15_score']:>4} "
              f"{r.get('probe_n_chi3', -1):>5}{trunc} "
              f"{r.get('probe_max_h0', -1):>5} "
              f"{r.get('probe_h0_ge3', -1):>5} "
              f"{pc:>5} "
              f"{r.get('n_k3_fib', -1):>2} {r.get('n_ell_fib', -1):>3} "
              f"{r['elapsed']:>4.0f}s{marker}")

        # Print top 50 then summary
        if rank == 50 and len(results) > 55:
            remaining = len(results) - 50
            n_clean_rest = sum(1 for x in results[50:] if x.get('probe_clean', 0) > 0)
            print(f"  {'':>3} ... {remaining} more ({n_clean_rest} with clean bundles) ...")
            break

    # Summary
    n_with_clean = sum(1 for r in results if r.get('probe_clean', 0) > 0)
    n_with_fib = sum(1 for r in results
                     if r.get('n_k3_fib', 0) > 0 or r.get('n_ell_fib', 0) > 0)
    n_both = sum(1 for r in results
                 if r.get('probe_clean', 0) > 0 and
                 (r.get('n_k3_fib', 0) > 0 or r.get('n_ell_fib', 0) > 0))
    total_clean = sum(r.get('probe_clean', 0) for r in results)
    n_t2_worthy = sum(1 for r in results if r.get('probe_clean', 0) >= 3)

    print(f"\n  Summary:")
    print(f"    With any clean h⁰=3 bundles (probe):  {n_with_clean}/{len(results)}")
    print(f"    Total clean bundles found (probe):     {total_clean}")
    print(f"    With K3/ell fibrations:                {n_with_fib}/{len(results)}")
    print(f"    Clean + fibrations:                    {n_both}/{len(results)}")
    print(f"    T2-worthy (≥3 clean in probe):         {n_t2_worthy}/{len(results)} "
          f"← promote to Tier 2")
    if results:
        best = results[0]
        print(f"    Best overall: h11={best['h11']}, poly {best['poly_idx']} "
              f"(T1.5={best['tier15_score']}, {best.get('probe_clean', '?')} clean)")


def save_csv(results, csv_path):
    """Save results to CSV, merging with any existing file (no duplicates)."""
    import os

    FIELDNAMES = [
        'rank', 'h11', 'poly_idx', 'favorable', 'h11_eff',
        'tier15_score',
        'probe_n_chi3', 'probe_truncated', 'probe_max_h0',
        'probe_h0_ge3', 'probe_clean',
        'n_k3_fib', 'n_ell_fib',
        'elapsed_s'
    ]

    def result_to_row(r):
        return {
            'h11': r['h11'], 'poly_idx': r['poly_idx'],
            'favorable': r['favorable'], 'h11_eff': r['h11_eff'],
            'tier15_score': r['tier15_score'],
            'probe_n_chi3': r.get('probe_n_chi3', -1),
            'probe_truncated': r.get('probe_truncated', False),
            'probe_max_h0': r.get('probe_max_h0', -1),
            'probe_h0_ge3': r.get('probe_h0_ge3', -1),
            'probe_clean': r.get('probe_clean', -1),
            'n_k3_fib': r.get('n_k3_fib', -1),
            'n_ell_fib': r.get('n_ell_fib', -1),
            'elapsed_s': f"{r['elapsed']:.1f}"
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

    # Sort by tier15_score desc, then probe_clean desc
    merged = sorted(existing.values(),
                    key=lambda x: (-int(x['tier15_score']),
                                  -int(x['probe_clean'])))

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


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Tier 1.5 intermediate screener')
    parser.add_argument('--csv', default='results/tier1_screen_results.csv',
                        help='Tier 1 CSV (or use --scan-log)')
    parser.add_argument('--scan-log', default=None,
                        help='Read scan log directly instead of T1 CSV')
    parser.add_argument('--top', type=int, default=500,
                        help='Max candidates to process')
    parser.add_argument('--min-h0', type=int, default=3,
                        help='Minimum scan max h⁰ to include')
    parser.add_argument('--phase', choices=['a', 'b', 'both'], default='both',
                        help='Which phases to run')
    parser.add_argument('--skip-t2', action='store_true',
                        help='Skip polytopes already in T2 results')
    parser.add_argument('--h11', type=int, default=None)
    parser.add_argument('--poly', type=int, default=None)
    args = parser.parse_args()

    print("=" * 76)
    print("  TIER 1.5 INTERMEDIATE SCREENER")
    if args.phase == 'a':
        print("  Phase A only: fibration count")
    elif args.phase == 'b':
        print("  Phase B only: capped bundle probe (300 bundles)")
    else:
        print("  Phase A: fibrations + Phase B: capped bundle probe (300 bundles)")
    print("=" * 76)

    # ── Single polytope mode ──
    if args.h11 is not None and args.poly is not None:
        print(f"\n  Screening h11={args.h11}, polytope {args.poly}...\n")
        result = screen_polytope_15(args.h11, args.poly, phase=args.phase,
                                     verbose=True)
        if result['status'] != 'ok':
            print(f"\n  FAILED: {result.get('status')}")
        return

    # ── Batch mode ──
    if args.scan_log:
        print(f"\n  Reading scan log: {args.scan_log}")
        candidates = parse_scan_log(args.scan_log, min_h0=args.min_h0)
    else:
        print(f"\n  Reading Tier 1 results: {args.csv}")
        candidates = read_tier1_csv(args.csv, top_n=args.top * 2,
                                     min_h0=args.min_h0)

    # Optionally skip T2-done polytopes
    if args.skip_t2:
        t2_done = read_tier2_csv('results/tier2_screen_results.csv')
        before = len(candidates)
        candidates = [c for c in candidates
                      if (c['h11'], c['poly_idx']) not in t2_done]
        print(f"  Skipping {before - len(candidates)} polytopes already in T2")

    candidates = candidates[:args.top]
    print(f"  {len(candidates)} candidates to screen "
          f"(min h⁰={args.min_h0}, phase={args.phase})")

    if not candidates:
        print("  No candidates to screen.")
        return

    # ── Screen ──
    results = []
    t_total = time.time()

    for i, cand in enumerate(candidates):
        h11 = cand['h11']
        pidx = cand['poly_idx']
        nf_tag = "" if cand['favorable'] else " [NF]"
        scan_h0 = cand['max_h0_scan']

        print(f"\n  [{i+1}/{len(candidates)}] h11={h11}, poly {pidx} "
              f"(scan h⁰={scan_h0}{nf_tag})")

        result = screen_polytope_15(h11, pidx, phase=args.phase, verbose=True)
        if result['status'] == 'ok':
            result['max_h0_scan'] = scan_h0
            result['tier1_score'] = cand.get('tier1_score', -1)
            results.append(result)
        else:
            print(f"    FAILED: {result.get('status')}")

    elapsed_total = time.time() - t_total

    # ── Results ──
    print_ranked_table(results)

    csv_path = "results/tier15_screen_results.csv"
    save_csv(results, csv_path)

    print(f"\n  Total time: {elapsed_total:.0f}s ({elapsed_total/60:.1f} min)")


if __name__ == '__main__':
    main()
