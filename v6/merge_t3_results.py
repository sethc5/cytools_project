#!/usr/bin/env python3
"""Merge T3 results from Codespace back into local canonical DB.

Usage:
    # After downloading t3_results.db from Codespace:
    python3 v6/merge_t3_results.py [--results v6/t3_results.db] [--db v6/cy_landscape_v6.db]
"""
import sqlite3, argparse, time, os, sys

MONOTONIC_MAX = {
    'max_h0', 'n_clean', 'n_bundles_checked', 'max_h0_t2', 'h0_ge3',
    'n_chi3', 'n_computed', 'n_clean_est', 'yukawa_rank', 'n_kappa_entries',
    'tier_reached',
}

def merge(results_db: str, local_db: str, dry_run: bool = False):
    if not os.path.exists(results_db):
        sys.exit(f"ERROR: results DB not found: {results_db}")
    if not os.path.exists(local_db):
        sys.exit(f"ERROR: local DB not found: {local_db}")

    con = sqlite3.connect(local_db, timeout=60)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(f"ATTACH DATABASE '{results_db}' AS r")

    cols = [row[1] for row in con.execute("PRAGMA table_info(polytopes)")]
    non_pk = [c for c in cols if c not in ('h11', 'poly_idx')]

    update_parts = []
    for c in non_pk:
        if c in MONOTONIC_MAX:
            if c == 'tier_reached':
                update_parts.append(
                    "tier_reached = NULLIF(MAX(COALESCE(tier_reached,''), "
                    "COALESCE(excluded.tier_reached,'')), '')"
                )
            else:
                update_parts.append(
                    f"{c} = MAX(COALESCE({c},0), COALESCE(excluded.{c},0))"
                )
        else:
            update_parts.append(f"{c} = COALESCE(excluded.{c}, {c})")

    col_list = ', '.join(cols)
    updates = ', '.join(update_parts)
    sql = (
        f"INSERT INTO polytopes ({col_list}) "
        f"SELECT {col_list} FROM r.polytopes WHERE 1=1 "
        f"ON CONFLICT(h11, poly_idx) DO UPDATE SET {updates}"
    )

    # Show what we're about to merge
    incoming = con.execute("SELECT COUNT(*) FROM r.polytopes WHERE tier_reached='T3'").fetchone()[0]
    inc_all = con.execute("SELECT COUNT(*) FROM r.polytopes").fetchone()[0]
    print(f"Merging {inc_all} rows ({incoming} T3) from {results_db}")

    # Pre-merge leaderboard stats
    pre_t3 = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T3'").fetchone()[0]
    pre_scored = con.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score IS NOT NULL").fetchone()[0]
    pre_max = con.execute("SELECT MAX(sm_score) FROM polytopes").fetchone()[0]
    pre80 = con.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score >= 80").fetchone()[0]
    print(f"Pre-merge:  T3={pre_t3}  scored={pre_scored}  max={pre_max}  >=80: {pre80}")

    if dry_run:
        print("(dry-run — no changes written)")
        con.close()
        return

    t0 = time.time()
    con.execute("BEGIN")
    con.execute(sql)

    # Merge fibrations — strip auto-generated 'id', deduplicate on (h11, poly_idx, fiber_type)
    # Bug fix: result DBs assign id starting at 1; INSERT OR IGNORE with id silently drops
    # everything when those ids already exist in the main DB.  Solution: exclude id column
    # and check for existing (h11, poly_idx, fiber_type) tuples before inserting.
    all_fib_cols = [row[1] for row in con.execute("PRAGMA table_info(fibrations)")]
    fib_cols = [c for c in all_fib_cols if c != 'id']  # exclude auto-pk
    col_idx = {c: i for i, c in enumerate(all_fib_cols)}
    fib_list = ', '.join(fib_cols)
    fib_ph = ', '.join(['?'] * len(fib_cols))
    new_fibs_raw = con.execute("SELECT * FROM r.fibrations").fetchall()
    if new_fibs_raw:
        existing = {
            row for row in con.execute("SELECT h11, poly_idx, fiber_type FROM fibrations")
        }
        to_insert = []
        for row in new_fibs_raw:
            key = (row[col_idx['h11']], row[col_idx['poly_idx']], row[col_idx['fiber_type']])
            if key not in existing:
                existing.add(key)  # prevent duplicate within batch
                to_insert.append(tuple(row[col_idx[c]] for c in fib_cols))
        if to_insert:
            con.executemany(
                f"INSERT INTO fibrations ({fib_list}) VALUES ({fib_ph})",
                to_insert
            )
        print(f"  Fibrations: {len(new_fibs_raw)} in file, {len(to_insert)} new inserted")

    con.execute("COMMIT")
    elapsed = time.time() - t0

    # Post-merge stats
    post_t3 = con.execute("SELECT COUNT(*) FROM polytopes WHERE tier_reached='T3'").fetchone()[0]
    post_scored = con.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score IS NOT NULL").fetchone()[0]
    post_max = con.execute("SELECT MAX(sm_score) FROM polytopes").fetchone()[0]
    post80 = con.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score >= 80").fetchone()[0]
    print(f"Post-merge: T3={post_t3}  scored={post_scored}  max={post_max}  >=80: {post80}")
    print(f"Elapsed: {elapsed:.1f}s")

    # Show newly T3 rows
    new_t3_rows = con.execute("""
        SELECT h11, poly_idx, sm_score, has_SM, has_GUT, best_gauge, n_clean
        FROM polytopes WHERE tier_reached='T3' AND sm_score IS NOT NULL
        ORDER BY sm_score DESC LIMIT 30
    """).fetchall()
    print("\nT3-verified leaderboard:")
    for r in new_t3_rows:
        sm_str = 'SM+GUT' if (r[3] and r[4]) else ('SM' if r[3] else ('no-SM' if r[3] is not None else '?'))
        gauge = (str(r[5])[:30] + '…') if r[5] and len(str(r[5])) > 30 else (r[5] or '')
        print(f"  h{r[0]}/P{r[1]:6d}  score={r[2]}  n_clean={r[6]:3d}  [{sm_str}]  {gauge}")

    con.close()
    print("\nDone. Run `git add -u && git commit` to save the updated DB pointer.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge T3 Codespace results into local DB')
    parser.add_argument('--results', default='v6/t3_results.db',
                        help='Path to t3_results.db from Codespace')
    parser.add_argument('--db', default='v6/cy_landscape_v6.db',
                        help='Path to local canonical DB')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be merged without writing')
    args = parser.parse_args()
    merge(args.results, args.db, dry_run=args.dry_run)
