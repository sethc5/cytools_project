#!/usr/bin/env python3
"""merge_receipts.py — Ingest pipeline v2 receipts into cy_landscape.db.

Run this on the local machine after pulling receipt JSONs from
a remote Codespace or Hetzner run.

Usage:
    python merge_receipts.py                        # merge all unmerged
    python merge_receipts.py receipts/v2_h17_*.json # specific files
    python merge_receipts.py --dry-run              # preview only
    python merge_receipts.py --list                 # show receipt inventory
"""

import argparse
import glob
import json
import sys
from datetime import datetime
from pathlib import Path

from db_utils import LandscapeDB

RECEIPTS_DIR = Path("receipts")
MERGED_LOG = RECEIPTS_DIR / ".merged"


def load_merged_set():
    """Return set of receipt filenames already merged."""
    if MERGED_LOG.exists():
        return set(MERGED_LOG.read_text().strip().splitlines())
    return set()


def mark_merged(receipt_name):
    """Append receipt name to the merged log."""
    with open(MERGED_LOG, 'a') as f:
        f.write(receipt_name + '\n')


def merge_one(db, receipt_path, dry_run=False):
    """Merge a single receipt JSON into the database.

    Returns (n_t0, n_t1, n_t2, n_fibs) counts of rows upserted.
    """
    with open(receipt_path) as f:
        receipt = json.load(f)

    h11 = receipt['h11']
    receipt_name = receipt.get('receipt_name', Path(receipt_path).name)

    # ── T0 rows (compact polytope metadata) ──
    t0_data = receipt.get('t0', [])
    n_t0 = 0
    if t0_data and not dry_run:
        rows = []
        for r in t0_data:
            rows.append({
                'h11': r.get('h11', h11),
                'poly_idx': r['poly_idx'],
                'h21': r.get('h21'),
                'chi': -6,
                'h11_eff': r.get('h11_eff'),
                'favorable': r.get('favorable'),
                'sym_order': r.get('aut_order'),
                'tier_reached': 'T0',
                'source_file': f'receipt:{receipt_name}',
                'status': r.get('status'),
                'error': r.get('skip_reason'),
            })
        db.upsert_polytopes_batch(rows)
        n_t0 = len(rows)

    # ── T1 rows (deep analysis) ──
    t1_data = receipt.get('t1', [])
    n_t1 = 0
    for r in t1_data:
        if dry_run:
            n_t1 += 1
            continue

        dp_str = '|'.join(str(d) for d in r.get('dp_types', []))
        d3_str = json.dumps(r.get('d3_values', []))
        h0_str = json.dumps(r.get('h0_dist', {}))

        db.upsert_polytope(r.get('h11', h11), r['poly_idx'],
            h21=r.get('h21'),
            chi=-6,
            h11_eff=r.get('h11_eff'),
            favorable=r.get('favorable'),
            n_chi3=r.get('n_chi3'),
            n_computed=r.get('n_chi3'),
            max_h0=r.get('max_h0'),
            n_dp=r.get('n_dp'),
            dp_types=dp_str,
            n_k3_div=r.get('n_k3_div'),
            n_rigid=r.get('n_rigid'),
            has_swiss=r.get('has_swiss'),
            n_swiss=r.get('n_swiss'),
            best_swiss_tau=r.get('best_tau'),
            best_swiss_ratio=r.get('best_ratio'),
            n_bundles_checked=r.get('n_chi3'),
            n_clean=r.get('n_clean'),
            max_h0_t2=r.get('max_h0'),
            h0_ge3=r.get('h0_ge3'),
            n_k3_fib=r.get('n_k3'),
            n_ell_fib=r.get('n_ell'),
            d3_n_distinct=r.get('d3_unique'),
            d3_clean_values=d3_str,
            h0_distribution=h0_str,
            screen_score=r.get('score'),
            tier_reached='T1' if r.get('n_clean', 0) == 0 else 'T2+',
            source_file=f'receipt:{receipt_name}',
            status=r.get('status'),
        )
        n_t1 += 1

    # ── T2 rows (fiber analysis) ──
    t2_data = receipt.get('t2', [])
    n_t2 = 0
    n_fibs = 0
    for r in t2_data:
        poly_idx = r['poly_idx']
        fibs = r.get('fibrations', [])
        has_sm = any(f.get('contains_SM') for f in fibs)
        has_gut = any(f.get('has_SU5_GUT') for f in fibs)
        best_gauge = r.get('best_gauge', '')

        if not dry_run:
            db.upsert_polytope(h11, poly_idx,
                n_fibers=len(fibs),
                has_SM=has_sm,
                has_GUT=has_gut,
                best_gauge=best_gauge,
                tier_reached='T2+',
                source_file=f'receipt:{receipt_name}',
            )
            for fib in fibs:
                db.add_fibration(h11, poly_idx, **fib)
                n_fibs += 1

        n_t2 += 1

    # ── Log scan ──
    if not dry_run:
        counts = receipt.get('counts', {})
        db.log_scan(
            h11=h11,
            tier='T2+',
            machine=receipt.get('machine', 'unknown'),
            script='pipeline_v2.py',
            n_polytopes=counts.get('fetched', 0),
            n_screened=counts.get('t1_analyzed', 0),
            n_passed=counts.get('with_clean', 0),
            notes=f"merged from {receipt_name}",
        )
        mark_merged(receipt_name)

    return n_t0, n_t1, n_t2, n_fibs


def list_receipts():
    """Print inventory of all receipts and their merge status."""
    merged = load_merged_set()
    files = sorted(RECEIPTS_DIR.glob("v2_h*.json"))

    if not files:
        print("No receipts found in receipts/")
        return

    print(f"\n{'Receipt':<55s}  {'Status':>8s}  {'h11':>4s}  {'T1':>5s}  "
          f"{'Clean':>5s}  {'SM':>4s}  {'Time':>8s}")
    print("─" * 100)

    for f in files:
        name = f.name
        status = "MERGED" if name in merged else "NEW"
        try:
            with open(f) as fh:
                r = json.load(fh)
            h11 = r.get('h11', '?')
            c = r.get('counts', {})
            t1 = c.get('t1_analyzed', 0)
            clean = c.get('with_clean', 0)
            sm = c.get('with_SM', 0)
            elapsed = r.get('elapsed_seconds', 0)
            time_str = f"{elapsed:.0f}s" if elapsed < 60 else f"{elapsed/60:.1f}m"
        except Exception:
            h11 = '?'
            t1 = clean = sm = 0
            time_str = '?'

        marker = "  " if status == "MERGED" else "→ "
        print(f"{marker}{name:<53s}  {status:>8s}  {h11:>4}  {t1:>5}  "
              f"{clean:>5}  {sm:>4}  {time_str:>8s}")

    n_new = sum(1 for f in files if f.name not in merged)
    print(f"\n  {len(files)} receipts total, {n_new} unmerged")


def main():
    parser = argparse.ArgumentParser(
        description="Merge pipeline v2 receipts into cy_landscape.db",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('files', nargs='*',
                        help='Receipt JSON files (default: all unmerged in receipts/)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview merge without writing to DB')
    parser.add_argument('--force', action='store_true',
                        help='Re-merge already-merged receipts')
    parser.add_argument('--list', action='store_true',
                        help='Show receipt inventory')

    args = parser.parse_args()

    if args.list:
        list_receipts()
        return

    # Collect receipt files
    if args.files:
        receipt_files = []
        for pattern in args.files:
            receipt_files.extend(glob.glob(pattern))
    else:
        # All unmerged in receipts/
        merged = load_merged_set()
        receipt_files = [
            str(f) for f in sorted(RECEIPTS_DIR.glob("v2_h*.json"))
            if f.name not in merged or args.force
        ]

    if not receipt_files:
        print("No receipts to merge. Use --list to see inventory.")
        return

    print(f"\n{'=' * 60}")
    print(f"  Merging {len(receipt_files)} receipt(s) into cy_landscape.db")
    if args.dry_run:
        print(f"  ** DRY RUN — no changes will be written **")
    print(f"{'=' * 60}\n")

    db = None if args.dry_run else LandscapeDB()

    total = {'t0': 0, 't1': 0, 't2': 0, 'fibs': 0}

    for rpath in receipt_files:
        name = Path(rpath).name
        try:
            n_t0, n_t1, n_t2, n_fibs = merge_one(db, rpath, dry_run=args.dry_run)
            total['t0'] += n_t0
            total['t1'] += n_t1
            total['t2'] += n_t2
            total['fibs'] += n_fibs
            print(f"  ✓ {name}: T0={n_t0}, T1={n_t1}, T2={n_t2}, fibs={n_fibs}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    print(f"\n{'=' * 60}")
    print(f"  Totals: T0={total['t0']}, T1={total['t1']}, "
          f"T2={total['t2']}, fibrations={total['fibs']}")
    if args.dry_run:
        print(f"  (dry run — nothing written)")
    print(f"{'=' * 60}\n")

    if db:
        db.close()


if __name__ == '__main__':
    main()
