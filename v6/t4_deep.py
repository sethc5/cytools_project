#!/usr/bin/env python3
"""
t4_deep.py — T4 deep triangulation analysis on top 37 (sm_score >= 80).

Runs 500 triangulation samples per polytope (vs 50 at T3) and
100 c₂/κ stability samples (vs 20 at T3).

Uses multiprocessing.Pool to process all 37 in parallel.
Output: t4_results.db — ready for merge into production DB.

Usage (from v6/ directory):
    python3 t4_deep.py [--workers 14] [--tri-samples 500] [--stab-samples 100]
    python3 t4_deep.py --dry-run  # just prints the 37 candidates
"""

import argparse
import json
import multiprocessing as mp
import os
import sqlite3
import sys
import time
from datetime import datetime

# ── Path setup ────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)      # v6/
sys.path.insert(0, PROJECT_ROOT)    # project root (for ks_index)

# ── Top 37 candidates (sm_score >= 80, all T3-verified) ──────────
# Format: (h11, poly_idx, sm_score_at_T3)
CANDIDATES = [
    (26, 11670, 89),
    (24,   868, 87),
    (29,  8423, 87),
    (27,  4102, 87),
    (27,  9192, 87),
    (22,   682, 85),
    (28,  6642, 85),
    (24, 45873, 85),
    (25, 46481, 85),
    (27, 45013, 85),
    (27,  9133, 85),
    (29, 13253, 83),
    (28,  5473, 82),
    (27,  2317, 82),
    (28,    33, 82),
    (28,   718, 82),
    (23,    36, 81),
    (27, 39352, 81),
    (25,  7867, 81),
    (25,   860, 81),
    (27, 27537, 81),
    (26,   315, 80),
    (26, 30513, 80),
    (27, 26021, 80),
    (28, 33562, 80),
    (25, 18950, 80),
    (24,   272, 80),
    (25,  8995, 80),
    (25,  5449, 80),
    (29,  6577, 80),
    (29,  6575, 80),
    (24, 44004, 80),
    (26, 11871, 80),
    (21,  9085, 80),
    (27, 28704, 80),
    (25, 38242, 80),
    (28,  1937, 80),
]


def _worker(args):
    """Process one polytope: load, run deep tri analysis, return result dict."""
    h11, poly_idx, old_score, tri_samples, stab_samples = args

    result = {
        'h11': h11, 'poly_idx': poly_idx, 'old_sm_score': old_score,
        'status': 'error', 'error': None,
        'n_triangulations': None, 'props_stable': None,
        'tri_n_tested': None, 'tri_c2_stable_frac': None,
        'tri_kappa_stable_frac': None,
        'new_sm_score': None, 'elapsed': 0.0,
    }
    t0 = time.time()

    try:
        import numpy as np
        from cytools.config import enable_experimental_features
        enable_experimental_features()

        # Import compute functions
        from cy_compute_v6 import (
            check_triangulation_stability,
            compute_tri_stability,
            compute_sm_score,
        )
        from ks_index import load_h11_polytopes

        # Load polytope from local chi6 file
        polys = load_h11_polytopes(h11, limit=poly_idx + 1)
        if poly_idx >= len(polys):
            result['error'] = f'poly_idx={poly_idx} out of range (n={len(polys)})'
            return result
        p = polys[poly_idx]

        # T4: deeper triangulation stability (10x T3)
        tri_info = check_triangulation_stability(p, n_samples=tri_samples)
        result['n_triangulations'] = tri_info['n_triangulations']
        result['props_stable'] = tri_info['props_stable']

        # T4: deeper c₂/κ hash stability (5x T3)
        tri_stab = compute_tri_stability(p, n_samples=stab_samples)
        result['tri_n_tested'] = tri_stab['tri_n_tested']
        result['tri_c2_stable_frac'] = tri_stab['tri_c2_stable_frac']
        result['tri_kappa_stable_frac'] = tri_stab['tri_kappa_stable_frac']

        result['status'] = 'ok'

    except Exception as e:
        result['error'] = str(e)[:200]

    result['elapsed'] = time.time() - t0
    return result


def build_t4_db(results, out_db):
    """Write T4 results to a SQLite DB for merge into production."""
    if os.path.exists(out_db):
        os.remove(out_db)
    conn = sqlite3.connect(out_db)
    conn.execute("""
        CREATE TABLE t4_results (
            h11         INTEGER NOT NULL,
            poly_idx    INTEGER NOT NULL,
            old_sm_score INTEGER,
            new_sm_score INTEGER,
            n_triangulations INTEGER,
            props_stable INTEGER,
            tri_n_tested INTEGER,
            tri_c2_stable_frac REAL,
            tri_kappa_stable_frac REAL,
            status      TEXT,
            error       TEXT,
            elapsed     REAL,
            run_at      TEXT,
            PRIMARY KEY (h11, poly_idx)
        )
    """)
    ts = datetime.utcnow().isoformat()
    for r in results:
        conn.execute("""
            INSERT OR REPLACE INTO t4_results VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            r['h11'], r['poly_idx'], r['old_sm_score'], r.get('new_sm_score'),
            r['n_triangulations'], r['props_stable'],
            r['tri_n_tested'], r['tri_c2_stable_frac'], r['tri_kappa_stable_frac'],
            r['status'], r.get('error'), r['elapsed'], ts,
        ))
    conn.commit()
    conn.close()
    sz = os.path.getsize(out_db) // 1024
    print(f"\nWrote {out_db} ({sz} KB, {len(results)} rows)")


def print_summary(results):
    ok = [r for r in results if r['status'] == 'ok']
    err = [r for r in results if r['status'] != 'ok']
    print(f"\n{'='*60}")
    print(f"T4 RESULTS: {len(ok)}/{len(results)} succeeded, {len(err)} errors")
    print(f"{'='*60}")
    print(f"\n{'h11/Pidx':18s} {'old_sm':>6s} {'n_tri':>6s} {'stable':>7s} "
          f"{'c2_fr':>6s} {'kp_fr':>6s} {'t(s)':>6s}")
    print('-' * 60)
    for r in sorted(results, key=lambda x: -(x['old_sm_score'] or 0)):
        label = f"h{r['h11']}/P{r['poly_idx']}"
        if r['status'] == 'ok':
            print(f"{label:18s} {r['old_sm_score']:>6d} "
                  f"{r['n_triangulations']:>6d} "
                  f"{str(r['props_stable']):>7s} "
                  f"{r['tri_c2_stable_frac']:>6.3f} "
                  f"{r['tri_kappa_stable_frac']:>6.3f} "
                  f"{r['elapsed']:>6.1f}")
        else:
            print(f"{label:18s} {'ERROR':>6s} -- {r.get('error', '')[:40]}")
    if err:
        print(f"\nErrors ({len(err)}):")
        for r in err:
            print(f"  h{r['h11']}/P{r['poly_idx']}: {r.get('error')}")


def main():
    parser = argparse.ArgumentParser(description='T4 deep triangulation on top 37')
    parser.add_argument('--workers', type=int, default=14)
    parser.add_argument('--tri-samples', type=int, default=500,
                        help='Triangulations per polytope (default 500, T3 used 50)')
    parser.add_argument('--stab-samples', type=int, default=100,
                        help='c2/kappa stability samples (default 100, T3 used 20)')
    parser.add_argument('--out-db', default='t4_results.db')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print candidates and exit')
    parser.add_argument('--subset', type=int, default=0,
                        help='Only process top N candidates (0=all 37)')
    args = parser.parse_args()

    candidates = CANDIDATES[:args.subset] if args.subset > 0 else CANDIDATES

    print(f"T4 Deep Triangulation Analysis")
    print(f"  Candidates: {len(candidates)}")
    print(f"  Workers:    {args.workers}")
    print(f"  Tri samples:  {args.tri_samples} (T3 used 50 — {args.tri_samples//50}x deeper)")
    print(f"  Stab samples: {args.stab_samples} (T3 used 20 — {args.stab_samples//20}x deeper)")
    print(f"  Output DB:  {args.out_db}")
    print(f"  Started:    {datetime.utcnow().isoformat()}")
    print()

    if args.dry_run:
        print("Candidates:")
        for h11, idx, sm in candidates:
            print(f"  h{h11}/P{idx}: sm_score={sm}")
        return

    # Build worker args
    worker_args = [
        (h11, idx, sm, args.tri_samples, args.stab_samples)
        for h11, idx, sm in candidates
    ]

    t_start = time.time()
    results = []

    print(f"Processing {len(worker_args)} polytopes with {args.workers} workers...")
    with mp.Pool(processes=args.workers) as pool:
        for i, res in enumerate(pool.imap_unordered(_worker, worker_args)):
            elapsed = time.time() - t_start
            label = f"h{res['h11']}/P{res['poly_idx']}"
            if res['status'] == 'ok':
                print(f"  [{i+1:2d}/{len(worker_args)}] {label:18s}  "
                      f"n_tri={res['n_triangulations']:4d}  "
                      f"c2_stable={res['tri_c2_stable_frac']:.2f}  "
                      f"kappa_stable={res['tri_kappa_stable_frac']:.2f}  "
                      f"({res['elapsed']:.0f}s)  "
                      f"[wall {elapsed:.0f}s]")
            else:
                print(f"  [{i+1:2d}/{len(worker_args)}] {label:18s}  ERROR: {res.get('error', '')[:60]}")
            results.append(res)

    total = time.time() - t_start
    print(f"\nTotal wall time: {total:.1f}s ({total/60:.1f}m)")

    print_summary(results)
    build_t4_db(results, args.out_db)

    print(f"\nMerge with:  python3 v6/merge_t4_results.py --results v6/{args.out_db}")
    print(f"Done: {datetime.utcnow().isoformat()}")


if __name__ == '__main__':
    main()
