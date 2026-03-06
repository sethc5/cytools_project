#!/usr/bin/env python3
"""
merge_t4_results.py — Merge T4 deep triangulation results into production DB.

Reads t4_results.db (from t4_deep.py) and updates polytopes in
cy_landscape_v6.db with deeper n_triangulations, props_stable, and
tri stability fractions. Updates tier_reached to 'T4'.

Usage:
    python3 v6/merge_t4_results.py [--results v6/t4_results.db] [--prod v6/cy_landscape_v6.db]
"""

import argparse
import os
import sqlite3
from datetime import datetime


def merge(results_db, prod_db):
    if not os.path.exists(results_db):
        print(f"ERROR: {results_db} not found")
        return

    src = sqlite3.connect(results_db)
    dst = sqlite3.connect(prod_db)

    rows = src.execute("""
        SELECT h11, poly_idx, n_triangulations, props_stable,
               tri_n_tested, tri_c2_stable_frac, tri_kappa_stable_frac,
               old_sm_score, new_sm_score, status, elapsed
        FROM t4_results
        WHERE status = 'ok'
        ORDER BY h11, poly_idx
    """).fetchall()

    print(f"T4 merge: {len(rows)} successful rows from {results_db}")
    print(f"Target:   {prod_db}")
    print()

    updated = 0
    score_jumps = []

    for r in rows:
        (h11, poly_idx, n_tri, props_stable,
         tri_tested, tri_c2, tri_kappa,
         old_score, new_score, status, elapsed) = r

        # Fetch current production row
        cur = dst.execute(
            "SELECT sm_score, n_triangulations, tier_reached FROM polytopes "
            "WHERE h11=? AND poly_idx=?", (h11, poly_idx)
        ).fetchone()

        if cur is None:
            print(f"  SKIP h{h11}/P{poly_idx}: not in production DB")
            continue

        cur_score, cur_n_tri, cur_tier = cur

        # Only update if T4 ran more triangulations
        if n_tri is not None and (cur_n_tri is None or n_tri > cur_n_tri):
            dst.execute("""
                UPDATE polytopes SET
                    n_triangulations = ?,
                    props_stable     = ?,
                    tri_n_tested     = ?,
                    tri_c2_stable_frac   = ?,
                    tri_kappa_stable_frac = ?,
                    tier_reached     = 'T4',
                    last_updated     = ?
                WHERE h11=? AND poly_idx=?
            """, (n_tri, props_stable, tri_tested, tri_c2, tri_kappa,
                  datetime.utcnow().isoformat(), h11, poly_idx))
            updated += 1

            # Track score changes
            if new_score is not None and new_score != cur_score:
                score_jumps.append((h11, poly_idx, cur_score, new_score))
                dst.execute("UPDATE polytopes SET sm_score=? WHERE h11=? AND poly_idx=?",
                            (new_score, h11, poly_idx))

    dst.commit()
    src.close()
    dst.close()

    print(f"Updated {updated}/{len(rows)} polytopes → tier T4")

    if score_jumps:
        print(f"\nScore changes ({len(score_jumps)}):")
        for h11, idx, old, new in score_jumps:
            delta = (new or 0) - (old or 0)
            arrow = "▲" if delta > 0 else "▼"
            print(f"  h{h11}/P{idx}: {old} → {new} ({arrow}{abs(delta):+d})")
    else:
        print("\nNo score changes at T4 (scores are stable)")

    # Final leaderboard
    dst2 = sqlite3.connect(prod_db)
    lb = dst2.execute("""
        SELECT h11, poly_idx, sm_score, tier_reached, n_triangulations, tri_c2_stable_frac
        FROM polytopes WHERE sm_score >= 80
        ORDER BY sm_score DESC, n_triangulations DESC LIMIT 40
    """).fetchall()
    print(f"\nPost-T4 leaderboard (sm_score >= 80):")
    print(f"  {'label':18s} {'sm':>4s} {'tier':>4s} {'n_tri':>6s} {'c2_fr':>6s}")
    for r in lb:
        label = f"h{r[0]}/P{r[1]}"
        print(f"  {label:18s} {r[2]:>4d} {r[3]:>4s} {(r[4] or 0):>6d} {(r[5] or 0.0):>6.3f}")

    t4_count = dst2.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T4'").fetchone()[0]
    print(f"\nTotal T4: {t4_count}")
    dst2.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='t4_results.db')
    parser.add_argument('--prod', default='cy_landscape_v6.db')
    args = parser.parse_args()

    # Resolve paths relative to v6/ dir
    v6_dir = os.path.dirname(os.path.abspath(__file__))
    results = args.results if os.path.isabs(args.results) else os.path.join(v6_dir, os.path.basename(args.results))
    prod = args.prod if os.path.isabs(args.prod) else os.path.join(v6_dir, os.path.basename(args.prod))

    merge(results, prod)


if __name__ == '__main__':
    main()
