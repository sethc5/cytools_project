#!/usr/bin/env python3
"""rescue_t1_skips.py — Re-run T1 on previously-skipped polytopes.

After fixing the min_h0 bug (min_h0=5 → min_h0=3), polytopes that had
clean bundles (h0=3) but no h0≥5 bundles were silently dropped. This
script re-runs T1 on those skipped polytopes and promotes any new passes
to T2.

Usage:
    python3 rescue_t1_skips.py --h11 28 -w 16
    python3 rescue_t1_skips.py --all -w 16
"""
import sys, os, time, argparse, socket
import multiprocessing as mp
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
_v6_dir = os.path.join(os.path.dirname(_here) if os.path.basename(_here) != 'v6' else _here)
# Ensure v6 is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v6'))

from v6.pipeline_v6 import (
    _t1_worker, _t2_worker, _run_t2_parallel,
    db_upsert_t1, db_upsert_t2,
    H0_MIN_T1, compute_sm_score
)
from v6.db_utils_v6 import LandscapeDB


def rescue_h11(h11, workers, db):
    """Re-run T1 on skipped polytopes for a given h11, then T2 on new passes."""
    import cytools as ct
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    # Get T1 skips from DB
    skips = db.query(
        "SELECT poly_idx FROM polytopes "
        "WHERE h11=? AND tier_reached='T1' AND status='skip'",
        (h11,)
    )
    n_skips = len(skips)
    if n_skips == 0:
        print(f"  h11={h11}: no T1 skips to rescue")
        return 0

    skip_indices = {r['poly_idx'] for r in skips}

    # Load polytopes
    h21 = h11 + 3
    polys = list(ct.fetch_polytopes(h11=h11, h21=h21, limit=200000))
    n_polys = len(polys)
    print(f"\n  h11={h11}: {n_skips} T1 skips to rescue "
          f"({n_polys} KS polytopes loaded)")

    # Build T1 args only for skipped polytopes
    t1_args = []
    for idx in skip_indices:
        if idx < len(polys):
            pts = np.array(polys[idx].points(), dtype=int).tolist()
            t1_args.append((pts, idx, h11))

    if not t1_args:
        print(f"  h11={h11}: no valid polytopes found")
        return 0

    # Re-run T1
    print(f"  Re-running T1 on {len(t1_args)} polytopes with {workers} workers...")
    t1_start = time.time()

    t1_results = []
    n_pass = 0
    n_new_clean = 0
    n_done = 0
    n_total = len(t1_args)

    with mp.Pool(workers) as pool:
        for t1r in pool.imap_unordered(_t1_worker, t1_args, chunksize=1):
            t1_results.append(t1r)
            n_done += 1
            if t1r.get('status') == 'pass' or (
                t1r.get('status') == 'timeout' and
                (t1r.get('n_clean_est', 0) > 0 or t1r.get('max_h0', 0) >= H0_MIN_T1)
            ):
                n_pass += 1
                if t1r.get('n_clean_est', 0) > 0 and t1r.get('max_h0', 0) < H0_MIN_T1:
                    n_new_clean += 1  # purely rescued by clean-bundle fix

            if n_done == 1 or n_done % 50 == 0 or n_done == n_total:
                elapsed = time.time() - t1_start
                rate = n_done / max(elapsed, 0.1)
                eta = (n_total - n_done) / max(rate, 0.001)
                print(f"    T1 rescue: {n_done}/{n_total} "
                      f"({n_pass} pass, {n_new_clean} clean-only) "
                      f"{elapsed:.0f}s elapsed, ETA {eta:.0f}s", flush=True)

    t1_elapsed = time.time() - t1_start

    # Filter to passes
    t1_pass_list = [r for r in t1_results
                    if r['status'] == 'pass' or
                    (r['status'] == 'timeout' and
                     (r.get('n_clean_est', 0) > 0 or r.get('max_h0', 0) >= H0_MIN_T1))]

    print(f"    T1 rescue done: {len(t1_pass_list)}/{n_total} now pass "
          f"({n_new_clean} purely from clean fix), {t1_elapsed:.1f}s")

    # Update DB with new T1 results
    db_upsert_t1(db, h11, t1_results)
    db.commit()

    if not t1_pass_list:
        print(f"  h11={h11}: no new passes after rescue")
        return 0

    # Sort by quality for T2
    t1_ranked = sorted(t1_pass_list,
                       key=lambda r: (r.get('n_clean_est', 0),
                                      r.get('max_h0', 0)),
                       reverse=True)

    # Run T2 on newly-passing polytopes
    _run_t2_parallel(polys, t1_ranked, h11, workers, db)

    return len(t1_pass_list)


def main():
    parser = argparse.ArgumentParser(description="Rescue T1-skipped polytopes")
    parser.add_argument('--h11', type=int, help="Specific h11 to rescue")
    parser.add_argument('--all', action='store_true',
                        help="Rescue all h11 levels with T1 skips")
    parser.add_argument('-w', '--workers', type=int, default=16)
    parser.add_argument('--min-skips', type=int, default=10,
                        help="Min T1 skips to bother rescuing (for --all)")
    args = parser.parse_args()

    if not args.h11 and not args.all:
        parser.error("Specify --h11 N or --all")

    db = LandscapeDB()
    print(f"  DB: {db}")

    t_start = time.time()
    total_rescued = 0

    if args.h11:
        total_rescued = rescue_h11(args.h11, args.workers, db)
    else:
        # Get all h11 levels with T1 skips, ordered by skip count
        levels = db.query(
            "SELECT h11, COUNT(*) as n_skip "
            "FROM polytopes WHERE tier_reached='T1' AND status='skip' "
            "GROUP BY h11 HAVING n_skip >= ? "
            "ORDER BY n_skip DESC",
            (args.min_skips,)
        )
        print(f"  {len(levels)} h11 levels with >= {args.min_skips} T1 skips")
        for row in levels:
            h11, n_skip = row['h11'], row['n_skip']
            print(f"\n{'='*60}")
            n = rescue_h11(h11, args.workers, db)
            total_rescued += n

    total_time = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"  RESCUE COMPLETE: {total_rescued} polytopes rescued, "
          f"{total_time:.1f}s total")
    db.close()


if __name__ == '__main__':
    main()
