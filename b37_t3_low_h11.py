#!/usr/bin/env python3
"""
b37_t3_low_h11.py — B-37: Run T3 on low-h¹¹ entries (h≤19) scoring ≥70.

Mirrors run_deep() in pipeline_v6.py but filtered to h11≤MAX_H11, tier=T2.

Usage:
    python3 b37_t3_low_h11.py [--min-score 70] [--max-h11 19] [--workers 4]
"""
import argparse
import sys
import os
import time
import numpy as np

# ── path setup ───────────────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
_v6_dir = os.path.join(_here, 'v6')
for p in [_v6_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from db_utils_v6 import LandscapeDB
from cy_compute_v6 import (
    compute_sm_score,
    check_triangulation_stability,
    check_instanton_divisor,
    compute_tri_stability,
    clear_poly_cache,
)

import cytools as ct
from cytools.config import enable_experimental_features
enable_experimental_features()

# ── fibre analysis (mirrors pipeline_v6._run_fiber_analysis) ─────────────────
def _run_fiber_analysis(polytope, poly_idx, h11_val):
    """Kodaira fiber classification → gauge algebra."""
    try:
        pts = polytope.points().tolist()
        sys.path.insert(0, os.path.join(_here, 'archive', 'v2'))
        from fiber_analysis import analyze_polytope
        result = analyze_polytope(pts, poly_idx=poly_idx, h11=h11_val)
        return result
    except Exception as e:
        return {'fibrations': [], 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='B-37: T3 for low-h11 T2 entries')
    parser.add_argument('--min-score', type=int, default=70)
    parser.add_argument('--max-h11', type=int, default=19)
    parser.add_argument('--db', type=str, default='v6/cy_landscape_v6.db')
    parser.add_argument('--ks-limit', type=int, default=1000)
    args = parser.parse_args()

    db_path = os.path.join(_here, args.db)
    db = LandscapeDB(db_path)

    # Find T2 candidates in h11≤max_h11 with score≥min_score
    candidates = db.query(
        "SELECT h11, poly_idx, sm_score FROM polytopes "
        "WHERE h11 <= ? AND sm_score >= ? AND tier_reached = 'T2' "
        "ORDER BY sm_score DESC",
        (args.max_h11, args.min_score)
    )
    if not candidates:
        print(f"No T2 candidates at h11≤{args.max_h11} with score≥{args.min_score}")
        return

    print(f"\n=== B-37 T3 deep analysis: {len(candidates)} candidates ===")
    for i, c in enumerate(candidates):
        print(f"  [{i+1}/{len(candidates)}] h{c['h11']}/P{c['poly_idx']} score={c['sm_score']}")
    print()

    results = []
    for i, cand in enumerate(candidates):
        h11       = cand['h11']
        idx       = cand['poly_idx']
        old_score = cand['sm_score']
        t_start   = time.time()

        print(f"\n[{i+1}/{len(candidates)}] h{h11}/P{idx} (score={old_score})")
        try:
            # Load polytope
            fetch_limit = max(args.ks_limit, idx + 1)
            polys = list(ct.fetch_polytopes(h11=h11, h21=h11+3, limit=fetch_limit))
            if idx >= len(polys):
                print(f"  ERROR: poly_idx={idx} but only {len(polys)} returned")
                continue
            p = polys[idx]

            # Fiber analysis
            fiber_result = _run_fiber_analysis(p, idx, h11)
            fibs = fiber_result.get('fibrations', [])
            has_sm  = any(f.get('contains_SM') for f in fibs)
            has_gut = any(f.get('has_SU5_GUT') for f in fibs)
            best_gauge = ''
            if fibs:
                best = max(fibs, key=lambda f: f.get('gauge_rank', 0), default={})
                best_gauge = best.get('gauge_algebra', '')
            print(f"  Fibers: {len(fibs)}, SM={'yes' if has_sm else 'no'}, "
                  f"GUT={'yes' if has_gut else 'no'}")
            if best_gauge:
                print(f"  Best gauge: {best_gauge}")

            # Triangulation stability (v4 property-level)
            tri_info = check_triangulation_stability(p, n_samples=50)
            print(f"  Triangulations: {tri_info['n_triangulations']} tested, "
                  f"stable={tri_info['props_stable']}")

            # v5 c₂/κ hash stability
            tri_stab = compute_tri_stability(p, n_samples=20)
            print(f"  Tri stability: {tri_stab['tri_n_tested']} tested, "
                  f"c2_stable={tri_stab['tri_c2_stable_frac']:.2f}, "
                  f"kappa_stable={tri_stab['tri_kappa_stable_frac']:.2f}")

            # Instanton divisor check
            try:
                tri    = p.triangulate()
                cy     = tri.get_cy()
                h11_eff = len(cy.divisor_basis())
                intnums = dict(cy.intersection_numbers(in_basis=True))
                c2      = np.array(cy.second_chern_class(in_basis=True), dtype=float)
                has_inst = check_instanton_divisor(intnums, c2, h11_eff)
                print(f"  Instanton divisor: {'yes' if has_inst else 'no'}")
            except Exception as e:
                has_inst = False
                print(f"  Instanton divisor: error ({e})")

            # Update DB to T3
            db.upsert_polytope(h11, idx,
                n_fibers=len(fibs),
                has_SM=has_sm,
                has_GUT=has_gut,
                best_gauge=best_gauge,
                n_triangulations=tri_info['n_triangulations'],
                props_stable=tri_info['props_stable'],
                has_instanton_div=has_inst,
                tri_n_tested=tri_stab['tri_n_tested'],
                tri_c2_stable_frac=tri_stab['tri_c2_stable_frac'],
                tri_kappa_stable_frac=tri_stab['tri_kappa_stable_frac'],
                tier_reached='T3',
                source_file='b37_t3_low_h11.py',
            )

            # Add fibration records
            for fib in fibs:
                db.add_fibration(h11, idx, **fib)

            # Rescore with fiber data now in DB
            row = db.query("SELECT * FROM polytopes WHERE h11=? AND poly_idx=?",
                           (h11, idx))
            if row:
                new_score = compute_sm_score(row[0])
                if new_score != old_score:
                    db.upsert_polytope(h11, idx, sm_score=new_score)
                    print(f"  Score: {old_score} -> {new_score}")
                else:
                    print(f"  Score unchanged: {old_score}")

            elapsed = time.time() - t_start
            print(f"  -> DB updated to T3 ({elapsed:.1f}s)")
            results.append({'h11': h11, 'idx': idx, 'score': old_score,
                            'has_sm': has_sm, 'has_gut': has_gut, 'fibs': len(fibs)})

        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback; traceback.print_exc()

    clear_poly_cache()

    print(f"\n=== B-37 T3 complete: {len(results)}/{len(candidates)} done ===")
    for r in results:
        print(f"  h{r['h11']}/P{r['idx']} score={r['score']} "
              f"SM={'Y' if r['has_sm'] else 'N'} "
              f"GUT={'Y' if r['has_gut'] else 'N'} fibs={r['fibs']}")

    # Post-run summary
    print("\n=== Low-h11 landscape summary ===")
    rows = db.query("""
        SELECT h11, COUNT(*) as n_scored, MAX(sm_score) as max_score,
               SUM(CASE WHEN sm_score >= 70 THEN 1 ELSE 0 END) as n_ge70,
               SUM(CASE WHEN sm_score >= 75 THEN 1 ELSE 0 END) as n_ge75,
               MAX(tier_reached) as max_tier
        FROM polytopes WHERE h11 <= 19 AND sm_score IS NOT NULL
        GROUP BY h11 ORDER BY h11
    """, ())
    print(f"{'h11':>4} {'n_scored':>9} {'max':>5} {'n≥70':>5} {'n≥75':>5} {'max_tier':>9}")
    for r in rows:
        print(f"h{r['h11']:02d}  {r['n_scored']:>9,}  {r['max_score']:>5}  "
              f"{r['n_ge70']:>5}  {r['n_ge75']:>5}  {r['max_tier']:>9}")

if __name__ == '__main__':
    main()
