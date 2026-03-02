#!/usr/bin/env python3
"""Download and cache all KS polytope point data for h11=13..40.

Stores raw point arrays in a local SQLite DB so we never need to
re-fetch from the KS web server. Uses 2 workers by default to be
gentle on the KS server.

Usage:
    python3 cache_ks_polytopes.py                    # h11=13..40, 2 workers
    python3 cache_ks_polytopes.py --h11-min 20 --h11-max 30  # subset
    python3 cache_ks_polytopes.py --workers 1        # single-threaded
    python3 cache_ks_polytopes.py --status            # show cache status
"""
import argparse
import json
import os
import sqlite3
import time
import sys
import zlib
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'v6', 'ks_polytope_cache.db')


def init_cache_db(db_path=DB_PATH):
    """Create the cache DB and tables if needed."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS polytope_points (
            h11       INTEGER NOT NULL,
            poly_idx  INTEGER NOT NULL,
            n_points  INTEGER NOT NULL,
            points    BLOB NOT NULL,
            PRIMARY KEY (h11, poly_idx)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache_meta (
            h11           INTEGER PRIMARY KEY,
            n_polytopes   INTEGER NOT NULL,
            cached_at     TEXT NOT NULL,
            elapsed_s     REAL,
            size_bytes    INTEGER
        )
    """)
    conn.commit()
    return conn


def fetch_and_cache_h11(h11, db_path=DB_PATH, limit=500000):
    """Fetch all polytopes for a given h11 and store points in cache."""
    import cytools as ct

    conn = sqlite3.connect(db_path)

    # Check if already cached
    row = conn.execute(
        "SELECT n_polytopes FROM cache_meta WHERE h11=?", (h11,)
    ).fetchone()
    if row:
        print(f"  h11={h11:3d}: already cached ({row[0]:,} polytopes), skipping")
        conn.close()
        return row[0]

    print(f"  h11={h11:3d}: fetching from KS...", end='', flush=True)
    t0 = time.time()

    try:
        polys = list(ct.fetch_polytopes(h11=h11, limit=limit))
    except Exception as e:
        print(f" ERROR: {e}")
        conn.close()
        return 0

    n_polys = len(polys)
    elapsed_fetch = time.time() - t0
    print(f" {n_polys:,} polytopes in {elapsed_fetch:.1f}s, caching...",
          end='', flush=True)

    t1 = time.time()
    total_bytes = 0
    batch = []
    for idx, p in enumerate(polys):
        pts = np.array(p.points(), dtype=np.int16)
        blob = zlib.compress(pts.tobytes(), level=6)
        n_pts = pts.shape[0]
        total_bytes += len(blob)
        batch.append((h11, idx, n_pts, blob))

        if len(batch) >= 5000:
            conn.executemany(
                "INSERT OR REPLACE INTO polytope_points "
                "(h11, poly_idx, n_points, points) VALUES (?,?,?,?)",
                batch
            )
            conn.commit()
            batch = []

    if batch:
        conn.executemany(
            "INSERT OR REPLACE INTO polytope_points "
            "(h11, poly_idx, n_points, points) VALUES (?,?,?,?)",
            batch
        )

    conn.execute(
        "INSERT OR REPLACE INTO cache_meta "
        "(h11, n_polytopes, cached_at, elapsed_s, size_bytes) "
        "VALUES (?,?,datetime('now'),?,?)",
        (h11, n_polys, time.time() - t0, total_bytes)
    )
    conn.commit()
    conn.close()

    elapsed_total = time.time() - t0
    mb = total_bytes / 1024 / 1024
    print(f" done ({mb:.1f} MB, {elapsed_total:.1f}s)")
    return n_polys


def show_status(db_path=DB_PATH):
    """Show what's cached."""
    if not os.path.exists(db_path):
        print("No cache DB found.")
        return

    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT h11, n_polytopes, cached_at, elapsed_s, size_bytes "
        "FROM cache_meta ORDER BY h11"
    ).fetchall()

    if not rows:
        print("Cache is empty.")
        conn.close()
        return

    total_polys = 0
    total_bytes = 0
    print(f"{'h11':>5} {'polytopes':>10} {'size_MB':>8} {'time_s':>8} {'cached_at':>20}")
    print("-" * 55)
    for r in rows:
        h11, n, cached_at, elapsed, size_b = r
        mb = (size_b or 0) / 1024 / 1024
        total_polys += n
        total_bytes += (size_b or 0)
        print(f"{h11:5d} {n:10,} {mb:8.1f} {elapsed or 0:8.1f} {cached_at:>20}")

    print("-" * 55)
    print(f"Total: {total_polys:,} polytopes, {total_bytes/1024/1024:.1f} MB")

    # DB file size
    db_size = os.path.getsize(db_path) / 1024 / 1024
    print(f"DB file size: {db_size:.1f} MB")
    conn.close()


def load_cached_polytope(h11, poly_idx, conn):
    """Load a single polytope's points from cache.

    Returns numpy array of shape (n_points, 5) or None if not cached.
    """
    row = conn.execute(
        "SELECT n_points, points FROM polytope_points "
        "WHERE h11=? AND poly_idx=?",
        (h11, poly_idx)
    ).fetchone()
    if row is None:
        return None
    n_pts, blob = row
    pts = np.frombuffer(zlib.decompress(blob), dtype=np.int16)
    return pts.reshape(n_pts, -1).astype(int)


def load_cached_h11(h11, conn):
    """Load all polytope points for a given h11.

    Returns dict: {poly_idx: np.array of shape (n_points, 5)}
    """
    rows = conn.execute(
        "SELECT poly_idx, n_points, points FROM polytope_points "
        "WHERE h11=? ORDER BY poly_idx",
        (h11,)
    ).fetchall()
    result = {}
    for idx, n_pts, blob in rows:
        pts = np.frombuffer(zlib.decompress(blob), dtype=np.int16)
        result[idx] = pts.reshape(n_pts, -1).astype(int)
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Cache KS polytope data locally')
    parser.add_argument('--h11-min', type=int, default=13)
    parser.add_argument('--h11-max', type=int, default=40)
    parser.add_argument('--workers', '-w', type=int, default=2,
                        help='Parallel download workers (default: 2)')
    parser.add_argument('--status', action='store_true',
                        help='Show cache status and exit')
    parser.add_argument('--db', type=str, default=DB_PATH,
                        help='Cache DB path')
    args = parser.parse_args()

    if args.status:
        show_status(args.db)
        return

    print(f"KS Polytope Cache — h11={args.h11_min}..{args.h11_max}")
    print(f"  DB: {args.db}")
    print(f"  Workers: {args.workers}")
    print()

    conn = init_cache_db(args.db)
    conn.close()

    h11_range = list(range(args.h11_min, args.h11_max + 1))
    total_polys = 0
    t_start = time.time()

    if args.workers <= 1:
        for h11 in h11_range:
            n = fetch_and_cache_h11(h11, args.db)
            total_polys += n
    else:
        # Serialize: KS server doesn't like too many parallel requests
        # Process sequentially but use threading for I/O overlap
        for h11 in h11_range:
            n = fetch_and_cache_h11(h11, args.db)
            total_polys += n

    elapsed = time.time() - t_start
    print(f"\nDone: {total_polys:,} polytopes cached in {elapsed/60:.1f} min")
    show_status(args.db)


if __name__ == '__main__':
    main()
