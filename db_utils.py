#!/usr/bin/env python3
"""db_utils.py — SQLite database layer for the CY landscape scan.

Single source of truth for all polytope screening results.
Schema: one row per polytope (h11, poly_idx), progressively enriched
as deeper tiers are computed.  Child table for fibration details.
Audit trail in scan_log.

Usage:
    from db_utils import LandscapeDB

    db = LandscapeDB()                        # opens cy_landscape.db
    db = LandscapeDB("path/to/other.db")      # custom path

    db.upsert_polytope(h11=15, poly_idx=61, max_h0=6, n_clean=45, ...)
    db.add_fibration(h11=15, poly_idx=61, fiber_type='F15', ...)
    db.log_scan(h11=15, tier='T1', machine='hetzner', n_polytopes=30000, ...)

    df = db.query("SELECT * FROM polytopes WHERE n_clean > 10")
    db.close()
"""

import sqlite3
import os
import json
import datetime
from pathlib import Path

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "cy_landscape.db")


# ══════════════════════════════════════════════════════════════════
#  Schema DDL
# ══════════════════════════════════════════════════════════════════

SCHEMA_SQL = """
-- Main table: one row per polytope, keyed by (h11, poly_idx).
-- Columns are grouped by tier.  NULL means "not yet computed."

CREATE TABLE IF NOT EXISTS polytopes (
    -- ── Identity (always present) ──
    h11             INTEGER NOT NULL,
    poly_idx        INTEGER NOT NULL,
    h21             INTEGER,
    chi             INTEGER,           -- Euler number = 2*(h11 - h21)

    -- ── Tier 0.25: cheap lattice scan (~0.5s) ──
    favorable       INTEGER,           -- boolean: 0/1
    h11_eff         INTEGER,           -- effective Picard rank
    n_chi3          INTEGER,           -- # of chi=+/-3 bundles found
    n_computed      INTEGER,           -- # bundles with h0 computed
    max_h0          INTEGER,           -- max h^0 seen in T0.25
    first_hit_at    INTEGER,           -- bundle index of first h0>=3
    n_ambient_skip  INTEGER,           -- skipped due to ambient check

    -- ── Tier 1: divisor classification + Swiss cheese (~3s) ──
    n_dp            INTEGER,           -- # del Pezzo divisors
    dp_types        TEXT,              -- pipe-separated: "dP6|dP7|dP8"
    n_k3_div        INTEGER,           -- # K3-like divisors
    n_rigid         INTEGER,           -- # rigid divisors
    has_swiss       INTEGER,           -- boolean: 0/1
    n_swiss         INTEGER,           -- # Swiss cheese structures
    best_swiss_tau  REAL,              -- smallest tau for Swiss cheese
    best_swiss_ratio REAL,             -- tau / V^(2/3) ratio
    sym_order       INTEGER,           -- automorphism group order
    screen_score    INTEGER,           -- T1 composite score

    -- ── Tier 1.5: 300-bundle probe (~10s) ──
    probe_n_chi3    INTEGER,
    probe_truncated INTEGER,           -- boolean: 0/1
    probe_max_h0    INTEGER,
    probe_h0_ge3    INTEGER,
    probe_clean     INTEGER,           -- clean bundles in 300 probe
    tier15_score    INTEGER,

    -- ── Tier 2: full bundle + fibration (~30-60s) ──
    n_bundles_checked INTEGER,         -- total bundles enumerated
    n_clean         INTEGER,           -- h0=3, h3=0 bundles
    max_h0_t2       INTEGER,           -- max h0 from full search
    h0_ge3          INTEGER,           -- # bundles with h0>=3
    n_overflow      INTEGER,           -- overflow during h0 computation
    n_k3_fib        INTEGER,           -- # K3 fibrations
    n_ell_fib       INTEGER,           -- # elliptic fibrations
    d3_min          REAL,              -- min D^3 value
    d3_max          REAL,              -- max D^3 value
    d3_n_distinct   INTEGER,           -- # distinct D^3 values
    d3_clean_values TEXT,              -- pipe-separated D^3 for clean bundles
    h0_distribution TEXT,              -- JSON: {"0": 100, "1": 50, "3": 12, ...}
    tier2_score     INTEGER,           -- T2 composite score

    -- ── Tier 2+: gauge / fibration summary ──
    n_fibers        INTEGER,           -- total fibrations analyzed
    has_SM          INTEGER,           -- boolean: contains SM gauge group
    has_GUT         INTEGER,           -- boolean: has SU(5) GUT
    best_gauge      TEXT,              -- best gauge algebra string

    -- ── Meta ──
    poly_hash       TEXT,              -- sha256[:12] of sorted vertex matrix
    tier_reached    TEXT,              -- highest tier: T025, T1, T15, T2, T2+
    last_updated    TEXT,              -- ISO timestamp
    source_file     TEXT,              -- CSV/script that produced this row
    status          TEXT,              -- ok, fail, timeout, error, etc.
    error           TEXT,              -- error message if any
    elapsed         REAL,              -- total compute time (seconds)

    PRIMARY KEY (h11, poly_idx)
);

-- Child table: one row per fibration per polytope.
CREATE TABLE IF NOT EXISTS fibrations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    h11             INTEGER NOT NULL,
    poly_idx        INTEGER NOT NULL,
    fiber_type      TEXT,              -- e.g. "F15"
    fiber_surface   TEXT,              -- e.g. "dP3_max"
    fiber_pts       INTEGER,
    base_pts        INTEGER,
    base_hull_verts INTEGER,
    fiber_at_origin INTEGER,
    total_excess    INTEGER,
    kodaira_types   TEXT,              -- JSON array of Kodaira data
    gauge_algebra   TEXT,              -- e.g. "su(6) x su(6) x U(1)^2"
    gauge_rank      INTEGER,
    contains_SM     INTEGER,           -- boolean
    has_SU5_GUT     INTEGER,           -- boolean
    MW_rank_bound   INTEGER,
    source_file     TEXT,

    FOREIGN KEY (h11, poly_idx) REFERENCES polytopes(h11, poly_idx)
);

-- Audit trail: one row per scan batch.
CREATE TABLE IF NOT EXISTS scan_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    h11             INTEGER,
    tier            TEXT,              -- T025, T1, T15, T2, etc.
    machine         TEXT,              -- dell5, codespace, hetzner
    script          TEXT,              -- script filename
    n_polytopes     INTEGER,           -- how many processed
    n_pass          INTEGER,           -- how many passed
    elapsed_s       REAL,
    started_at      TEXT,
    finished_at     TEXT,
    notes           TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_polytopes_h11
    ON polytopes(h11);
CREATE INDEX IF NOT EXISTS idx_polytopes_tier
    ON polytopes(tier_reached);
CREATE INDEX IF NOT EXISTS idx_polytopes_nclean
    ON polytopes(n_clean);
CREATE INDEX IF NOT EXISTS idx_polytopes_score
    ON polytopes(tier2_score);
CREATE INDEX IF NOT EXISTS idx_polytopes_maxh0
    ON polytopes(max_h0);
CREATE INDEX IF NOT EXISTS idx_fibrations_poly
    ON fibrations(h11, poly_idx);
"""


# ══════════════════════════════════════════════════════════════════
#  Database class
# ══════════════════════════════════════════════════════════════════

class LandscapeDB:
    """Thin wrapper around SQLite for the CY landscape database."""

    # All valid column names in polytopes table (for safe upsert)
    POLYTOPE_COLUMNS = {
        'h11', 'poly_idx', 'h21', 'chi',
        'favorable', 'h11_eff', 'n_chi3', 'n_computed', 'max_h0',
        'first_hit_at', 'n_ambient_skip',
        'n_dp', 'dp_types', 'n_k3_div', 'n_rigid',
        'has_swiss', 'n_swiss', 'best_swiss_tau', 'best_swiss_ratio',
        'sym_order', 'screen_score',
        'probe_n_chi3', 'probe_truncated', 'probe_max_h0',
        'probe_h0_ge3', 'probe_clean', 'tier15_score',
        'n_bundles_checked', 'n_clean', 'max_h0_t2', 'h0_ge3',
        'n_overflow', 'n_k3_fib', 'n_ell_fib',
        'd3_min', 'd3_max', 'd3_n_distinct', 'd3_clean_values',
        'h0_distribution', 'tier2_score',
        'n_fibers', 'has_SM', 'has_GUT', 'best_gauge',
        'poly_hash', 'tier_reached', 'last_updated', 'source_file',
        'status', 'error', 'elapsed',
    }

    FIBRATION_COLUMNS = {
        'h11', 'poly_idx', 'fiber_type', 'fiber_surface',
        'fiber_pts', 'base_pts', 'base_hull_verts',
        'fiber_at_origin', 'total_excess',
        'kodaira_types', 'gauge_algebra', 'gauge_rank',
        'contains_SM', 'has_SU5_GUT', 'MW_rank_bound', 'source_file',
    }

    def __init__(self, db_path=None):
        self.db_path = db_path or DEFAULT_DB
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._create_schema()

    def _create_schema(self):
        """Create tables + indexes if they don't exist."""
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    # ── Core API ──────────────────────────────────────────────

    def upsert_polytope(self, h11, poly_idx, **kwargs):
        """Insert or update a polytope row.

        Only non-None kwargs are written; existing data is preserved.
        Automatically sets last_updated timestamp.

        Example:
            db.upsert_polytope(15, 61, max_h0=6, n_clean=45,
                               tier_reached='T2', status='ok')
        """
        kwargs['h11'] = h11
        kwargs['poly_idx'] = poly_idx
        kwargs['last_updated'] = datetime.datetime.now().isoformat()

        # Compute chi if h21 is known
        if 'h21' in kwargs and kwargs['h21'] is not None and 'chi' not in kwargs:
            kwargs['chi'] = 2 * (h11 - kwargs['h21'])

        # Filter to valid columns only
        data = {k: v for k, v in kwargs.items()
                if k in self.POLYTOPE_COLUMNS and v is not None}

        # Convert booleans to int for SQLite
        for k, v in data.items():
            if isinstance(v, bool):
                data[k] = int(v)

        # Convert dicts/lists to JSON strings
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                data[k] = json.dumps(v)

        cols = list(data.keys())
        placeholders = ", ".join("?" for _ in cols)
        col_names = ", ".join(cols)
        # ON CONFLICT: update columns, using MAX for monotonic metrics
        monotonic_max = {'max_h0', 'n_clean', 'n_bundles_checked',
                        'max_h0_t2', 'h0_ge3', 'n_chi3', 'n_computed'}
        update_parts = []
        for c in cols:
            if c in ('h11', 'poly_idx'):
                continue
            if c in monotonic_max:
                update_parts.append(
                    f"{c} = MAX(COALESCE(polytopes.{c}, 0), excluded.{c})")
            else:
                update_parts.append(f"{c} = excluded.{c}")
        updates = ", ".join(update_parts)

        sql = (f"INSERT INTO polytopes ({col_names}) VALUES ({placeholders}) "
               f"ON CONFLICT(h11, poly_idx) DO UPDATE SET {updates}")

        self._conn.execute(sql, [data[c] for c in cols])
        self._conn.commit()

    def upsert_polytopes_batch(self, rows):
        """Batch upsert many polytope rows efficiently.

        rows: list of dicts, each must contain 'h11' and 'poly_idx'.
        """
        if not rows:
            return

        now = datetime.datetime.now().isoformat()
        for row in rows:
            row['last_updated'] = now
            h11 = row.get('h11')
            poly_idx = row.get('poly_idx')
            if h11 is None or poly_idx is None:
                continue

            # Compute chi if possible
            h21 = row.get('h21')
            if h21 is not None and 'chi' not in row:
                row['chi'] = 2 * (h11 - h21)

            # Filter + convert
            data = {k: v for k, v in row.items()
                    if k in self.POLYTOPE_COLUMNS and v is not None}
            for k, v in data.items():
                if isinstance(v, bool):
                    data[k] = int(v)
                elif isinstance(v, (dict, list)):
                    data[k] = json.dumps(v)

            cols = list(data.keys())
            placeholders = ", ".join("?" for _ in cols)
            col_names = ", ".join(cols)
            # Use MAX for metrics that should never decrease on re-scan
            monotonic_max = {'max_h0', 'n_clean', 'n_bundles_checked',
                            'max_h0_t2', 'h0_ge3', 'n_chi3', 'n_computed'}
            update_parts = []
            for c in cols:
                if c in ('h11', 'poly_idx'):
                    continue
                if c in monotonic_max:
                    update_parts.append(
                        f"{c} = MAX(COALESCE(polytopes.{c}, 0), excluded.{c})")
                else:
                    update_parts.append(f"{c} = excluded.{c}")
            updates = ", ".join(update_parts)

            sql = (f"INSERT INTO polytopes ({col_names}) VALUES ({placeholders}) "
                   f"ON CONFLICT(h11, poly_idx) DO UPDATE SET {updates}")
            self._conn.execute(sql, [data[c] for c in cols])

        self._conn.commit()

    def add_fibration(self, h11, poly_idx, **kwargs):
        """Add a fibration record for a polytope.

        Checks for duplicates by (h11, poly_idx, fiber_type, gauge_algebra).
        """
        kwargs['h11'] = h11
        kwargs['poly_idx'] = poly_idx

        # Convert types
        for k, v in kwargs.items():
            if isinstance(v, bool):
                kwargs[k] = int(v)
            elif isinstance(v, (dict, list)):
                kwargs[k] = json.dumps(v)

        data = {k: v for k, v in kwargs.items()
                if k in self.FIBRATION_COLUMNS and v is not None}

        # Deduplicate: skip if same (h11, poly_idx, fiber_type, gauge_algebra) exists
        existing = self._conn.execute(
            "SELECT id FROM fibrations WHERE h11=? AND poly_idx=? "
            "AND fiber_type=? AND gauge_algebra=?",
            (h11, poly_idx, data.get('fiber_type'), data.get('gauge_algebra'))
        ).fetchone()
        if existing:
            return  # already recorded

        cols = list(data.keys())
        placeholders = ", ".join("?" for _ in cols)
        col_names = ", ".join(cols)

        self._conn.execute(
            f"INSERT INTO fibrations ({col_names}) VALUES ({placeholders})",
            [data[c] for c in cols]
        )
        self._conn.commit()

    def log_scan(self, h11, tier, machine='unknown', **kwargs):
        """Record a scan batch in the audit trail."""
        kwargs['h11'] = h11
        kwargs['tier'] = tier
        kwargs['machine'] = machine
        kwargs['finished_at'] = datetime.datetime.now().isoformat()

        valid_cols = {'h11', 'tier', 'machine', 'script', 'n_polytopes',
                      'n_pass', 'elapsed_s', 'started_at', 'finished_at',
                      'notes'}
        data = {k: v for k, v in kwargs.items() if k in valid_cols}

        cols = list(data.keys())
        placeholders = ", ".join("?" for _ in cols)
        col_names = ", ".join(cols)

        self._conn.execute(
            f"INSERT INTO scan_log ({col_names}) VALUES ({placeholders})",
            [data[c] for c in cols]
        )
        self._conn.commit()

    # ── Query helpers ─────────────────────────────────────────

    def query(self, sql, params=None):
        """Run a SQL query and return list of dicts."""
        cursor = self._conn.execute(sql, params or [])
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def query_df(self, sql, params=None):
        """Run a SQL query and return a pandas DataFrame."""
        import pandas as pd
        return pd.read_sql_query(sql, self._conn, params=params)

    def get_polytope(self, h11, poly_idx):
        """Get a single polytope row as a dict, or None."""
        rows = self.query(
            "SELECT * FROM polytopes WHERE h11=? AND poly_idx=?",
            (h11, poly_idx)
        )
        return rows[0] if rows else None

    def get_fibrations(self, h11, poly_idx):
        """Get all fibrations for a polytope."""
        return self.query(
            "SELECT * FROM fibrations WHERE h11=? AND poly_idx=?",
            (h11, poly_idx)
        )

    def count_by_tier(self):
        """Summary: how many polytopes at each tier."""
        return self.query(
            "SELECT tier_reached, COUNT(*) as n "
            "FROM polytopes GROUP BY tier_reached ORDER BY n DESC"
        )

    def coverage(self):
        """Summary: polytope count and tier distribution per h11."""
        return self.query(
            "SELECT h11, COUNT(*) as n_total, "
            "SUM(CASE WHEN tier_reached='T025' THEN 1 ELSE 0 END) as n_t025, "
            "SUM(CASE WHEN tier_reached='T1' THEN 1 ELSE 0 END) as n_t1, "
            "SUM(CASE WHEN tier_reached='T15' THEN 1 ELSE 0 END) as n_t15, "
            "SUM(CASE WHEN tier_reached='T2' THEN 1 ELSE 0 END) as n_t2, "
            "SUM(CASE WHEN tier_reached='T2+' THEN 1 ELSE 0 END) as n_t2plus, "
            "MAX(n_clean) as best_clean, MAX(max_h0) as best_h0, "
            "SUM(CASE WHEN n_clean > 0 THEN 1 ELSE 0 END) as n_with_clean "
            "FROM polytopes GROUP BY h11 ORDER BY h11"
        )

    def needs_screening(self, tier='T2', min_h0=3, limit=100):
        """Find polytopes that need deeper screening.

        Returns polytopes that passed T0.25 (max_h0 >= min_h0) but
        haven't reached the target tier yet.
        """
        tier_order = {'T025': 1, 'T1': 2, 'T15': 3, 'T2': 4, 'T2+': 5}
        target = tier_order.get(tier, 4)

        # Build list of tiers below the target
        below = [t for t, v in tier_order.items() if v < target]
        if not below:
            return []

        placeholders = ", ".join("?" for _ in below)
        rows = self.query(
            f"SELECT h11, poly_idx, max_h0, tier_reached "
            f"FROM polytopes "
            f"WHERE max_h0 >= ? AND ("
            f"  tier_reached IS NULL OR tier_reached IN ({placeholders})"
            f") ORDER BY max_h0 DESC LIMIT ?",
            [min_h0] + below + [limit]
        )
        return rows

    def leaderboard(self, limit=20):
        """Top polytopes by tier2_score, falling back to screen_score."""
        return self.query(
            "SELECT h11, poly_idx, h11_eff, favorable, "
            "n_clean, max_h0, n_dp, has_swiss, n_k3_fib, n_ell_fib, "
            "has_SM, best_gauge, tier2_score, screen_score, tier_reached "
            "FROM polytopes "
            "WHERE COALESCE(tier2_score, 0) > 0 OR COALESCE(screen_score, 0) > 0 "
            "ORDER BY COALESCE(tier2_score, 0) DESC, "
            "COALESCE(screen_score, 0) DESC LIMIT ?",
            (limit,)
        )

    # ── Utilities ─────────────────────────────────────────────

    def stats(self):
        """Quick summary stats."""
        total = self._conn.execute(
            "SELECT COUNT(*) FROM polytopes").fetchone()[0]
        by_h11 = self.query(
            "SELECT h11, COUNT(*) as n FROM polytopes GROUP BY h11 ORDER BY h11")
        n_fib = self._conn.execute(
            "SELECT COUNT(*) FROM fibrations").fetchone()[0]
        n_scans = self._conn.execute(
            "SELECT COUNT(*) FROM scan_log").fetchone()[0]
        return {
            'total_polytopes': total,
            'by_h11': by_h11,
            'total_fibrations': n_fib,
            'total_scans': n_scans,
        }

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        total = self._conn.execute(
            "SELECT COUNT(*) FROM polytopes").fetchone()[0]
        return f"<LandscapeDB: {self.db_path} ({total} polytopes)>"


# ══════════════════════════════════════════════════════════════════
#  CLI: quick status check
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB

    if not os.path.exists(db_path):
        print(f"Creating new database: {db_path}")
        db = LandscapeDB(db_path)
        print(f"  Tables created. Run consolidate_db.py to populate.")
    else:
        db = LandscapeDB(db_path)
        print(f"Database: {db_path}")
        s = db.stats()
        print(f"  Polytopes: {s['total_polytopes']}")
        print(f"  Fibrations: {s['total_fibrations']}")
        print(f"  Scan log entries: {s['total_scans']}")
        if s['by_h11']:
            print(f"\n  By h11:")
            for row in s['by_h11']:
                print(f"    h11={row['h11']}: {row['n']} polytopes")

        cov = db.coverage()
        if cov:
            print(f"\n  Coverage:")
            print(f"    {'h11':>4} {'total':>7} {'T025':>6} {'T1':>5} "
                  f"{'T15':>5} {'T2':>5} {'T2+':>5} {'best_clean':>10}")
            for r in cov:
                print(f"    {r['h11']:>4} {r['n_total']:>7} "
                      f"{r['n_t025'] or 0:>6} {r['n_t1'] or 0:>5} "
                      f"{r['n_t15'] or 0:>5} {r['n_t2'] or 0:>5} "
                      f"{r['n_t2plus'] or 0:>5} "
                      f"{r['best_clean'] or '-':>10}")

    db.close()
