#!/usr/bin/env python3
"""consolidate_db.py — One-time ingestion of all scattered CSVs/JSONs into cy_landscape.db.

Reads every results file and upserts into the unified SQLite database.
Deeper tiers overwrite shallower data when columns overlap.

Processing order (shallow → deep, so deeper data wins):
  1. scan_h*.csv            (T0.25 — bulk scans for h15-h17)
  2. tier025_h18*.csv       (T0.25 — h18 screening)
  3. tier1_screen_results   (T1 — divisor + Swiss cheese)
  4. tier1_h18.csv          (T1 — h18 Hetzner batch)
  5. tier15_screen_results  (T1.5 — 300-bundle probe)
  6. tier2_full_results     (T2 — full bundle search)
  7. auto_h*.csv            (T2+ — deep pipeline runs with gauge)
  8. chi6_tier1_scan.csv    (T1 — early chi=-6 scan)
  9. fiber_h*.json          (fibration child records)

Usage:
    python3 consolidate_db.py                    # populate cy_landscape.db
    python3 consolidate_db.py --db other.db      # custom path
    python3 consolidate_db.py --dry-run          # count rows, don't write
"""

import csv
import json
import os
import sys
import glob
import argparse
import time

from db_utils import LandscapeDB

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


# ══════════════════════════════════════════════════════════════════
#  CSV Readers — one per format
# ══════════════════════════════════════════════════════════════════

def _safe_int(val, default=None):
    """Convert to int, returning default on failure."""
    if val is None or val == '' or val == '-1':
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val, default=None):
    if val is None or val == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_bool(val):
    """Convert string to int boolean (0/1) for SQLite."""
    if val is None or val == '':
        return None
    if isinstance(val, bool):
        return int(val)
    return 1 if str(val).lower() in ('true', '1', 'yes') else 0


def read_scan_csv(csv_path):
    """Read scan_h*.csv (T0.25 bulk scans for h15-h17).

    Columns: h11,h21,poly_idx,favorable,h11_eff,n_chi3,n_computed,
             max_h0,h0_3_count,status
    """
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'h11': int(r['h11']),
                'poly_idx': int(r['poly_idx']),
                'h21': _safe_int(r.get('h21')),
                'favorable': _safe_bool(r.get('favorable')),
                'h11_eff': _safe_int(r.get('h11_eff')),
                'n_chi3': _safe_int(r.get('n_chi3')),
                'n_computed': _safe_int(r.get('n_computed')),
                'max_h0': _safe_int(r.get('max_h0')),
                'tier_reached': 'T025',
                'status': r.get('status', 'ok'),
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_tier025_csv(csv_path):
    """Read tier025_h18*.csv.

    Columns: h11,h21,poly_idx,favorable,h11_eff,n_chi3,n_computed,
             max_h0,first_hit_at,n_ambient_skip,status
    """
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get('status') not in ('pass', 'fail', 'ok', 'nf'):
                continue  # skip header dupes or malformed
            rows.append({
                'h11': int(r['h11']),
                'poly_idx': int(r['poly_idx']),
                'h21': _safe_int(r.get('h21')),
                'favorable': _safe_bool(r.get('favorable')),
                'h11_eff': _safe_int(r.get('h11_eff')),
                'n_chi3': _safe_int(r.get('n_chi3')),
                'n_computed': _safe_int(r.get('n_computed')),
                'max_h0': _safe_int(r.get('max_h0')),
                'first_hit_at': _safe_int(r.get('first_hit_at')),
                'n_ambient_skip': _safe_int(r.get('n_ambient_skip')),
                'tier_reached': 'T025',
                'status': r.get('status', 'ok'),
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_tier1_screen_csv(csv_path):
    """Read tier1_screen_results.csv.

    Columns: rank,h11,poly_idx,favorable,screen_score,clean_h0_3,h0_ge3,
             max_h0,n_dp,n_k3,has_swiss,best_tau,best_ratio,sym_order,
             n_chi3,elapsed_s
    """
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'h11': int(r['h11']),
                'poly_idx': int(r['poly_idx']),
                'favorable': _safe_bool(r.get('favorable')),
                'screen_score': _safe_int(r.get('screen_score')),
                'n_clean': _safe_int(r.get('clean_h0_3')),
                'h0_ge3': _safe_int(r.get('h0_ge3')),
                'max_h0': _safe_int(r.get('max_h0')),
                'n_dp': _safe_int(r.get('n_dp')),
                'n_k3_div': _safe_int(r.get('n_k3')),
                'has_swiss': _safe_bool(r.get('has_swiss')),
                'best_swiss_tau': _safe_float(r.get('best_tau')),
                'best_swiss_ratio': _safe_float(r.get('best_ratio')),
                'sym_order': _safe_int(r.get('sym_order')),
                'n_chi3': _safe_int(r.get('n_chi3')),
                'elapsed': _safe_float(r.get('elapsed_s')),
                'tier_reached': 'T1',
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_tier1_h18_csv(csv_path):
    """Read tier1_h18.csv (Hetzner batch T1 for h18).

    Columns: h11,h21,poly_idx,favorable,h11_eff,max_h0_025,n_chi3_025,
             n_dp,dp_types,n_k3_div,n_rigid,has_swiss,n_swiss,
             best_swiss_tau,best_swiss_ratio,sym_order,screen_score,
             elapsed,status,error
    """
    rows = []
    if not os.path.exists(csv_path):
        return rows
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'h11': int(r['h11']),
                'poly_idx': int(r['poly_idx']),
                'h21': _safe_int(r.get('h21')),
                'favorable': _safe_bool(r.get('favorable')),
                'h11_eff': _safe_int(r.get('h11_eff')),
                'max_h0': _safe_int(r.get('max_h0_025')),
                'n_dp': _safe_int(r.get('n_dp')),
                'dp_types': r.get('dp_types', ''),
                'n_k3_div': _safe_int(r.get('n_k3_div')),
                'n_rigid': _safe_int(r.get('n_rigid')),
                'has_swiss': _safe_bool(r.get('has_swiss')),
                'n_swiss': _safe_int(r.get('n_swiss')),
                'best_swiss_tau': _safe_float(r.get('best_swiss_tau')),
                'best_swiss_ratio': _safe_float(r.get('best_swiss_ratio')),
                'sym_order': _safe_int(r.get('sym_order')),
                'screen_score': _safe_int(r.get('screen_score')),
                'elapsed': _safe_float(r.get('elapsed')),
                'status': r.get('status', ''),
                'error': r.get('error', ''),
                'tier_reached': 'T1',
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_tier15_csv(csv_path):
    """Read tier15_screen_results.csv.

    Columns: rank,h11,poly_idx,favorable,h11_eff,tier15_score,
             probe_n_chi3,probe_truncated,probe_max_h0,probe_h0_ge3,
             probe_clean,n_k3_fib,n_ell_fib,elapsed_s
    """
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'h11': int(r['h11']),
                'poly_idx': int(r['poly_idx']),
                'favorable': _safe_bool(r.get('favorable')),
                'h11_eff': _safe_int(r.get('h11_eff')),
                'tier15_score': _safe_int(r.get('tier15_score')),
                'probe_n_chi3': _safe_int(r.get('probe_n_chi3')),
                'probe_truncated': _safe_bool(r.get('probe_truncated')),
                'probe_max_h0': _safe_int(r.get('probe_max_h0')),
                'probe_h0_ge3': _safe_int(r.get('probe_h0_ge3')),
                'probe_clean': _safe_int(r.get('probe_clean')),
                'n_k3_fib': _safe_int(r.get('n_k3_fib')),
                'n_ell_fib': _safe_int(r.get('n_ell_fib')),
                'elapsed': _safe_float(r.get('elapsed_s')),
                'tier_reached': 'T15',
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_tier2_csv(csv_path):
    """Read tier2_full_results.csv.

    Columns: rank,h11,poly_idx,favorable,h11_eff,tier2_score,
             clean_h0_3,h0_ge3,max_h0,n_chi3,n_k3_fib,n_ell_fib,
             d3_min,d3_max,d3_n_distinct,d3_clean_values,n_overflow,elapsed_s
    """
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'h11': int(r['h11']),
                'poly_idx': int(r['poly_idx']),
                'favorable': _safe_bool(r.get('favorable')),
                'h11_eff': _safe_int(r.get('h11_eff')),
                'tier2_score': _safe_int(r.get('tier2_score')),
                'n_clean': _safe_int(r.get('clean_h0_3')),
                'h0_ge3': _safe_int(r.get('h0_ge3')),
                'max_h0': _safe_int(r.get('max_h0')),
                'max_h0_t2': _safe_int(r.get('max_h0')),
                'n_chi3': _safe_int(r.get('n_chi3')),
                'n_k3_fib': _safe_int(r.get('n_k3_fib')),
                'n_ell_fib': _safe_int(r.get('n_ell_fib')),
                'd3_min': _safe_float(r.get('d3_min')),
                'd3_max': _safe_float(r.get('d3_max')),
                'd3_n_distinct': _safe_int(r.get('d3_n_distinct')),
                'd3_clean_values': r.get('d3_clean_values', ''),
                'n_overflow': _safe_int(r.get('n_overflow')),
                'elapsed': _safe_float(r.get('elapsed_s')),
                'tier_reached': 'T2',
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_auto_csv(csv_path, h11_val):
    """Read auto_h*.csv (deep pipeline runs with gauge analysis).

    Columns: rank,poly_idx,score,n_clean,max_h0,n_chi3,n_dp,has_swiss,
             best_tau,n_k3,n_ell,d3_unique,h11_eff,favorable,
             n_fibers,has_SM,has_GUT,best_gauge,elapsed
    """
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'h11': h11_val,
                'poly_idx': int(r['poly_idx']),
                'h21': h11_val + 3,  # chi=-6 → h21 = h11 + 3
                'tier2_score': _safe_int(r.get('score')),
                'n_clean': _safe_int(r.get('n_clean')),
                'max_h0': _safe_int(r.get('max_h0')),
                'max_h0_t2': _safe_int(r.get('max_h0')),
                'n_chi3': _safe_int(r.get('n_chi3')),
                'n_dp': _safe_int(r.get('n_dp')),
                'has_swiss': _safe_bool(r.get('has_swiss')),
                'best_swiss_tau': _safe_float(r.get('best_tau')),
                'n_k3_fib': _safe_int(r.get('n_k3')),
                'n_ell_fib': _safe_int(r.get('n_ell')),
                'd3_clean_values': r.get('d3_unique', ''),
                'h11_eff': _safe_int(r.get('h11_eff')),
                'favorable': _safe_bool(r.get('favorable')),
                'n_fibers': _safe_int(r.get('n_fibers')),
                'has_SM': _safe_bool(r.get('has_SM')),
                'has_GUT': _safe_bool(r.get('has_GUT')),
                'best_gauge': r.get('best_gauge', ''),
                'elapsed': _safe_float(r.get('elapsed')),
                'tier_reached': 'T2+',
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_chi6_tier1_csv(csv_path):
    """Read chi6_tier1_scan.csv (early exploratory scan).

    Columns: poly_id,h11,h21,chi,n_vertices,n_points,is_favorable,
             tier1_score,tier1_max,...
    poly_id is a string like "poly_0" — extract the integer suffix.
    """
    rows = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Skip empty / malformed rows
            h11 = _safe_int(r.get('h11'))
            if h11 is None:
                continue
            # poly_id is "poly_0", "poly_1", etc.
            poly_id_str = r.get('poly_id', '0')
            poly_idx = _safe_int(poly_id_str.replace('poly_', ''), 0)
            rows.append({
                'h11': h11,
                'poly_idx': poly_idx,
                'h21': _safe_int(r.get('h21')),
                'chi': _safe_int(r.get('chi')),
                'favorable': _safe_bool(r.get('is_favorable')),
                'screen_score': _safe_int(r.get('tier1_score')),
                'sym_order': _safe_int(r.get('gl_order')),
                'tier_reached': 'T1',
                'status': 'ok' if not r.get('error') else r['error'],
                'source_file': os.path.basename(csv_path),
            })
    return rows


def read_fiber_json(json_path):
    """Read fiber_h*_P*.json and return (polytope_update, fibration_rows)."""
    with open(json_path) as f:
        data = json.load(f)

    h11 = data['h11']
    poly_idx = data['poly_idx']
    source = os.path.basename(json_path)

    poly_update = {
        'h11': h11,
        'poly_idx': poly_idx,
        'n_fibers': data.get('n_fibrations', 0),
        'source_file': source,
    }

    # Check for SM/GUT in any fibration
    any_sm = False
    any_gut = False

    fib_rows = []
    for fib in data.get('fibrations', []):
        any_sm = any_sm or fib.get('contains_SM', False)
        any_gut = any_gut or fib.get('has_SU5_GUT', False)

        fib_rows.append({
            'h11': h11,
            'poly_idx': poly_idx,
            'fiber_type': fib.get('fiber_type'),
            'fiber_surface': fib.get('fiber_surface'),
            'fiber_pts': fib.get('fiber_pts'),
            'base_pts': fib.get('base_pts'),
            'base_hull_verts': fib.get('base_hull_vertices'),
            'fiber_at_origin': fib.get('fiber_at_origin'),
            'total_excess': fib.get('total_excess'),
            'kodaira_types': json.dumps(fib.get('kodaira_types', [])),
            'gauge_algebra': fib.get('gauge_algebra'),
            'gauge_rank': fib.get('gauge_rank'),
            'contains_SM': _safe_bool(fib.get('contains_SM')),
            'has_SU5_GUT': _safe_bool(fib.get('has_SU5_GUT')),
            'MW_rank_bound': fib.get('MW_rank_bound'),
            'source_file': source,
        })

    if any_sm:
        poly_update['has_SM'] = 1
    if any_gut:
        poly_update['has_GUT'] = 1
    if fib_rows:
        # Best gauge from first fibration with SM
        sm_fibs = [f for f in data.get('fibrations', []) if f.get('contains_SM')]
        if sm_fibs:
            poly_update['best_gauge'] = sm_fibs[0].get('gauge_algebra', '')

    return poly_update, fib_rows


# ══════════════════════════════════════════════════════════════════
#  Main consolidation
# ══════════════════════════════════════════════════════════════════

def consolidate(db_path=None, dry_run=False):
    """Read all result files and populate the database."""
    t0 = time.time()

    if dry_run:
        print("DRY RUN — counting rows only, no database writes.\n")

    db = LandscapeDB(db_path) if not dry_run else None
    total_upserted = 0
    total_fibs = 0

    def ingest(label, rows, tier):
        nonlocal total_upserted
        n = len(rows)
        if n == 0:
            return
        print(f"  {label}: {n} rows (tier={tier})")
        if not dry_run:
            db.upsert_polytopes_batch(rows)
        total_upserted += n

    # ── 1. scan_h*.csv (T0.25 bulk scans) ──
    print("═" * 60)
    print("Phase 1: T0.25 bulk scans")
    print("═" * 60)
    for csv_path in sorted(glob.glob(os.path.join(RESULTS_DIR, "scan_h*.csv"))):
        rows = read_scan_csv(csv_path)
        ingest(os.path.basename(csv_path), rows, 'T025')

    # ── 2. tier025_h18*.csv ──
    print()
    for csv_path in sorted(glob.glob(os.path.join(RESULTS_DIR, "tier025_h18*.csv"))):
        rows = read_tier025_csv(csv_path)
        ingest(os.path.basename(csv_path), rows, 'T025')

    # ── 3. chi6_tier1_scan.csv (early scan, T1 level) ──
    print(f"\n{'═' * 60}")
    print("Phase 2: T1 screening")
    print("═" * 60)
    chi6_path = os.path.join(RESULTS_DIR, "chi6_tier1_scan.csv")
    if os.path.exists(chi6_path):
        rows = read_chi6_tier1_csv(chi6_path)
        ingest("chi6_tier1_scan.csv", rows, 'T1')

    # ── 4. tier1_screen_results.csv ──
    t1_path = os.path.join(RESULTS_DIR, "tier1_screen_results.csv")
    if os.path.exists(t1_path):
        rows = read_tier1_screen_csv(t1_path)
        ingest("tier1_screen_results.csv", rows, 'T1')

    # ── 5. tier1_h18.csv (Hetzner batch) ──
    t1h18_path = os.path.join(RESULTS_DIR, "tier1_h18.csv")
    if os.path.exists(t1h18_path):
        rows = read_tier1_h18_csv(t1h18_path)
        ingest("tier1_h18.csv", rows, 'T1')

    # ── 6. tier15_screen_results.csv ──
    print(f"\n{'═' * 60}")
    print("Phase 3: T1.5 probe")
    print("═" * 60)
    t15_path = os.path.join(RESULTS_DIR, "tier15_screen_results.csv")
    if os.path.exists(t15_path):
        rows = read_tier15_csv(t15_path)
        ingest("tier15_screen_results.csv", rows, 'T15')

    # ── 7. tier2_full_results.csv ──
    print(f"\n{'═' * 60}")
    print("Phase 4: T2 full bundle search")
    print("═" * 60)
    t2_path = os.path.join(RESULTS_DIR, "tier2_full_results.csv")
    if os.path.exists(t2_path):
        rows = read_tier2_csv(t2_path)
        ingest("tier2_full_results.csv", rows, 'T2')

    # ── 8. auto_h*.csv (deep pipeline with gauge) ──
    print(f"\n{'═' * 60}")
    print("Phase 5: T2+ deep pipeline (auto_h*)")
    print("═" * 60)
    for csv_path in sorted(glob.glob(os.path.join(RESULTS_DIR, "auto_h*.csv"))):
        # Skip checkpoint files
        if 'checkpoint' in csv_path:
            continue
        basename = os.path.basename(csv_path)
        # Extract h11 from filename: auto_h14.csv → 14
        h11_str = basename.replace('auto_h', '').replace('.csv', '')
        try:
            h11_val = int(h11_str)
        except ValueError:
            print(f"  [warn] Can't parse h11 from {basename}, skipping")
            continue
        rows = read_auto_csv(csv_path, h11_val)
        ingest(basename, rows, 'T2+')

    # ── 9. fiber_h*.json (fibration child records) ──
    print(f"\n{'═' * 60}")
    print("Phase 6: Fibration details (fiber_h*.json)")
    print("═" * 60)
    for json_path in sorted(glob.glob(os.path.join(RESULTS_DIR, "fiber_h*.json"))):
        basename = os.path.basename(json_path)
        try:
            poly_update, fib_rows = read_fiber_json(json_path)
        except Exception as e:
            print(f"  [warn] {basename}: {e}")
            continue

        print(f"  {basename}: 1 polytope update + {len(fib_rows)} fibrations")
        if not dry_run:
            db.upsert_polytope(**poly_update)
            for fib in fib_rows:
                h11 = fib.pop('h11')
                pidx = fib.pop('poly_idx')
                db.add_fibration(h11, pidx, **fib)
        total_fibs += len(fib_rows)

    # ── Summary ──
    elapsed = time.time() - t0
    print(f"\n{'═' * 60}")
    print(f"DONE in {elapsed:.1f}s")
    print(f"  Total polytope rows upserted: {total_upserted}")
    print(f"  Total fibration records: {total_fibs}")

    if not dry_run:
        s = db.stats()
        print(f"\n  Database: {db.db_path}")
        print(f"  Unique polytopes: {s['total_polytopes']}")
        print(f"  Fibrations: {s['total_fibrations']}")
        print(f"  Scan log entries: {s['total_scans']}")

        # Coverage summary
        cov = db.coverage()
        if cov:
            print(f"\n  Coverage by h11:")
            print(f"    {'h11':>4} {'total':>7} {'T025':>6} {'T1':>5} "
                  f"{'T15':>5} {'T2':>5} {'T2+':>5} {'best_n_clean':>12}")
            for r in cov:
                print(f"    {r['h11']:>4} {r['n_total']:>7} "
                      f"{r['n_t025'] or 0:>6} {r['n_t1'] or 0:>5} "
                      f"{r['n_t15'] or 0:>5} {r['n_t2'] or 0:>5} "
                      f"{r['n_t2plus'] or 0:>5} "
                      f"{r['best_clean'] or '-':>12}")

        db.close()
    else:
        print(f"\n  (dry run — no database created)")


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate all result CSVs into SQLite")
    parser.add_argument("--db", default=None, help="Database path (default: cy_landscape.db)")
    parser.add_argument("--dry-run", action="store_true", help="Count rows only")
    args = parser.parse_args()

    consolidate(db_path=args.db, dry_run=args.dry_run)
