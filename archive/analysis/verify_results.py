#!/usr/bin/env python3
"""
verify_results.py — Spot-check contributed Tier 2 results.

Re-runs a random sample of polytopes from a T2 CSV and compares the
recomputed values against the claimed results.  Deterministic: same
polytope + same CYTools version = same numbers.

Fields verified (must match exactly):
  - clean_h0_3   (exact h⁰=3, h³=0 bundle count)
  - h0_ge3       (bundles with h⁰ ≥ 3)
  - max_h0       (maximum h⁰ seen)
  - n_chi3       (total χ=±3 bundles found)
  - n_k3_fib     (K3 fibration count)
  - n_ell_fib    (elliptic fibration count)

Usage:
  python3 verify_results.py results/tier2_full_results.csv          # 5 random
  python3 verify_results.py results/tier2_full_results.csv -n 10    # 10 random
  python3 verify_results.py results/tier2_full_results.csv --all    # every row
  python3 verify_results.py results/tier2_full_results.csv --row 3  # specific row

Exit codes:
  0  All checks passed
  1  One or more mismatches detected
  2  Input error (file not found, bad CSV, etc.)

Requires: CYTools, numpy  (same environment as tier2_screen.py)
"""

import sys
import csv
import random
import argparse
import time

# ── Import the actual screening function from our pipeline ──
try:
    from tier2_screen import screen_polytope_deep
except ImportError:
    print("ERROR: Cannot import tier2_screen.py. Run from the project root.")
    sys.exit(2)

# Fields that must match exactly between claimed and recomputed
EXACT_FIELDS = [
    'clean_h0_3',
    'h0_ge3',
    'max_h0',
    'n_chi3',
    'n_k3_fib',
    'n_ell_fib',
]

# ANSI
BOLD  = "\033[1m"
GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
PASS  = f"{GREEN}✓{RESET}"
FAIL  = f"{RED}✗{RESET}"


def load_csv(path):
    """Load T2 results CSV and return list of dicts with integer fields."""
    rows = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def verify_row(row, verbose=True):
    """
    Re-run T2 screening on one polytope and compare against claimed values.
    Returns (passed: bool, mismatches: dict).
    """
    h11 = int(row['h11'])
    pidx = int(row['poly_idx'])

    if verbose:
        print(f"\n  Verifying h11={h11}, poly {pidx} ...", flush=True)

    result = screen_polytope_deep(h11, pidx, verbose=False)

    if result['status'] != 'ok':
        if verbose:
            print(f"    {FAIL} Screening failed: {result.get('status')} "
                  f"— {result.get('error', '')}")
        return False, {'_error': result.get('status')}

    mismatches = {}
    for field in EXACT_FIELDS:
        claimed = int(row.get(field, -1))
        actual = int(result.get(field, -1))
        if claimed != actual:
            mismatches[field] = {'claimed': claimed, 'actual': actual}

    passed = len(mismatches) == 0

    if verbose:
        if passed:
            print(f"    {PASS} All {len(EXACT_FIELDS)} fields match "
                  f"(clean={result['clean_h0_3']}, max_h⁰={result['max_h0']}, "
                  f"K3={result['n_k3_fib']}, ell={result['n_ell_fib']})")
        else:
            print(f"    {FAIL} {BOLD}{len(mismatches)} mismatch(es){RESET}:")
            for field, vals in mismatches.items():
                print(f"       {field}: claimed={vals['claimed']}, "
                      f"actual={vals['actual']}")

    return passed, mismatches


def main():
    parser = argparse.ArgumentParser(
        description='Verify contributed Tier 2 results by re-running a sample')
    parser.add_argument('csv', help='Path to T2 results CSV')
    parser.add_argument('-n', type=int, default=5,
                        help='Number of random rows to verify (default: 5)')
    parser.add_argument('--all', action='store_true',
                        help='Verify every row (slow — ~3min/polytope)')
    parser.add_argument('--row', type=int, default=None,
                        help='Verify a specific row number (1-indexed)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducible sampling')
    args = parser.parse_args()

    # Load CSV
    try:
        rows = load_csv(args.csv)
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.csv}")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Cannot parse CSV: {e}")
        sys.exit(2)

    if not rows:
        print("ERROR: CSV is empty")
        sys.exit(2)

    print("=" * 68)
    print("  VERIFY RESULTS — Spot-check contributed T2 data")
    print("=" * 68)
    print(f"  Source: {args.csv} ({len(rows)} rows)")

    # Select rows to verify
    if args.row is not None:
        idx = args.row - 1
        if idx < 0 or idx >= len(rows):
            print(f"ERROR: Row {args.row} out of range (1..{len(rows)})")
            sys.exit(2)
        sample = [rows[idx]]
        print(f"  Mode: single row #{args.row}")
    elif args.all:
        sample = rows
        print(f"  Mode: ALL {len(rows)} rows (this will take a while)")
    else:
        n = min(args.n, len(rows))
        if args.seed is not None:
            random.seed(args.seed)
        sample = random.sample(rows, n)
        print(f"  Mode: {n} random rows"
              + (f" (seed={args.seed})" if args.seed else ""))

    # Verify
    t0 = time.time()
    n_pass = 0
    n_fail = 0
    failures = []

    for i, row in enumerate(sample):
        h11 = int(row['h11'])
        pidx = int(row['poly_idx'])
        passed, mismatches = verify_row(row, verbose=True)
        if passed:
            n_pass += 1
        else:
            n_fail += 1
            failures.append((h11, pidx, mismatches))

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'═' * 68}")
    total = n_pass + n_fail
    if n_fail == 0:
        print(f"  {PASS} {BOLD}ALL {total} VERIFIED{RESET} "
              f"— results match ({elapsed:.0f}s)")
    else:
        print(f"  {FAIL} {BOLD}{n_fail}/{total} FAILED{RESET} ({elapsed:.0f}s)")
        print(f"\n  Failed polytopes:")
        for h11, pidx, mm in failures:
            fields = ", ".join(f"{k}: {v['claimed']}→{v['actual']}"
                               for k, v in mm.items() if k != '_error')
            if '_error' in mm:
                fields = f"error: {mm['_error']}"
            print(f"    h11={h11}, poly {pidx}: {fields}")
    print(f"{'═' * 68}")

    sys.exit(1 if n_fail > 0 else 0)


if __name__ == '__main__':
    main()
