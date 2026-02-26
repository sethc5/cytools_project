#!/usr/bin/env python3
"""db_utils_v3.py — SQLite database layer for pipeline v3.

Fresh database (cy_landscape_v3.db) with expanded schema for
physics-driven scoring. Not a migration from v2 — clean start.

Schema notes:
  - polytopes: one row per (h11, poly_idx), progressively enriched T0→T3
  - fibrations: one row per fibration per polytope (same as v2)
  - scan_log: audit trail for batch runs
  - Monotonic columns use MAX(existing, new) on upsert to prevent clobber

Usage:
    from db_utils_v3 import LandscapeDB

    db = LandscapeDB()                           # opens cy_landscape_v3.db
    db = LandscapeDB("path/to/other.db")         # custom path

    db.upsert_polytope(h11=15, poly_idx=61, max_h0=6, sm_score=72, ...)
    db.add_fibration(h11=15, poly_idx=61, fiber_type='F15', ...)
    db.log_scan(h11=15, tier='T05', machine='dell5', n_polytopes=5000, ...)

    rows = db.query("SELECT * FROM polytopes WHERE sm_score > 50")
    db.close()
"""

import sqlite3
import os
import json
import datetime
from pathlib import Path

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "cy_landscape_v3.db")


# ══════════════════════════════════════════════════════════════════
#  Schema DDL
# ══════════════════════════════════════════════════════════════════

SCHEMA_SQL = """
-- Main table: one row per polytope, keyed by (h11, poly_idx).
-- Columns grouped by tier. NULL = "not yet computed."

CREATE TABLE IF NOT EXISTS polytopes (
    -- ── Identity (always present) ──
    h11             INTEGER NOT NULL,
    poly_idx        INTEGER NOT NULL,
    h21             INTEGER,
    chi             INTEGER,           -- Euler number = 2*(h11 - h21)

    -- ── T0: geometry fingerprint (~0.05s) ──
    favorable       INTEGER,           -- boolean: 0/1
    h11_eff         INTEGER,           -- effective Picard rank
    gap             INTEGER,           -- h11 - h11_eff
    aut_order       INTEGER,           -- polytope automorphism group order

    -- ── T05: intersection algebra (~0.1s) [NEW] ──
    yukawa_rank     INTEGER,           -- nonzero κ_{ijk} entries in basis
    yukawa_density  REAL,              -- nonzero / total possible triples
    chi_over_24     REAL,              -- D3-brane tadpole bound
    c2_all_positive INTEGER,           -- boolean: c₂·D ≥ 0 for all basis D
    c2_vector       TEXT,              -- JSON: c₂ values per basis divisor
    kappa_signature TEXT,              -- Hessian eigenvalue signature "(p,q)"
    volume_form_type TEXT,             -- swiss_cheese | fibered | generic
    n_kappa_entries INTEGER,           -- total κ_{ijk} entries (inc. zero)

    -- ── T1: bundle screening (~0.5s) ──
    n_chi3          INTEGER,           -- # of χ=±3 bundles found
    n_computed      INTEGER,           -- # bundles with h⁰ computed
    max_h0          INTEGER,           -- max h⁰ seen (screening, may be approx)
    h0_ge3          INTEGER,           -- # bundles with h⁰ ≥ 3
    n_clean_est     INTEGER,           -- time-budgeted clean bundle estimate
    first_clean_at  INTEGER,           -- bundle index of first clean hit

    -- ── T2: deep physics (3-30s) ──
    -- Bundle census
    n_bundles_checked INTEGER,         -- total bundles enumerated
    n_clean         INTEGER,           -- confirmed h⁰=3, h³=0 bundles
    max_h0_t2       INTEGER,           -- max h⁰ from full search
    h0_distribution TEXT,              -- JSON: {"0": 100, "1": 50, "3": 12, ...}

    -- Divisor classification
    n_dp            INTEGER,           -- # del Pezzo divisors
    dp_types        TEXT,              -- pipe-separated: "dP6|dP7|dP8"
    n_k3_div        INTEGER,           -- # K3-like divisors
    n_rigid         INTEGER,           -- # rigid divisors

    -- Swiss cheese / LVS
    has_swiss       INTEGER,           -- boolean: 0/1
    n_swiss         INTEGER,           -- # Swiss cheese structures
    best_swiss_tau  REAL,              -- smallest τ for Swiss cheese
    best_swiss_ratio REAL,             -- τ / V^{2/3} ratio
    lvs_score       REAL,              -- best τ/V^{2/3} ratio (smaller=better)
    best_small_div  INTEGER,           -- index of best small divisor
    volume_hierarchy REAL,             -- V_big / V_small ratio

    -- Yukawa texture (per clean bundle)
    yukawa_texture_rank INTEGER,       -- rank of best Yukawa matrix
    yukawa_hierarchy REAL,             -- max/min eigenvalue ratio
    yukawa_zeros    INTEGER,           -- texture zeros in Y matrix
    best_yukawa_bundle TEXT,           -- JSON: divisor class of best Yukawa

    -- Mori cone
    n_mori_rays     INTEGER,           -- # Mori cone generators
    n_dp_contract   INTEGER,           -- # del Pezzo contracting curves

    -- Fibrations
    n_k3_fib        INTEGER,           -- # K3 fibrations
    n_ell_fib       INTEGER,           -- # elliptic fibrations
    n_fibers        INTEGER,           -- total fibrations analyzed (gauge)
    has_SM          INTEGER,           -- boolean: contains SM gauge group
    has_GUT         INTEGER,           -- boolean: has SU(5) GUT
    best_gauge      TEXT,              -- best gauge algebra string

    -- D³ statistics
    d3_min          REAL,
    d3_max          REAL,
    d3_n_distinct   INTEGER,
    d3_clean_values TEXT,              -- JSON array of D³ for clean bundles

    -- Composite scores
    sm_score        INTEGER,           -- 0-100 physics composite score
    screen_score    INTEGER,           -- legacy v2-compat score (26-pt)

    -- ── T3: full phenomenology (30s+) ──
    n_triangulations INTEGER,          -- # triangulations tested
    props_stable    INTEGER,           -- boolean: properties stable across tris
    n_flux_vacua_est REAL,             -- log₁₀ estimated flux vacua
    has_instanton_div INTEGER,         -- boolean: suitable rigid dP for LVS
    orientifold_ok  INTEGER,           -- boolean: GLSM admits viable orientifold

    -- ── Meta ──
    poly_hash       TEXT,              -- sha256[:16] of sorted vertex matrix
    tier_reached    TEXT,              -- highest tier: T0, T05, T1, T2, T3
    last_updated    TEXT,              -- ISO timestamp
    source_file     TEXT,              -- script that produced this row
    status          TEXT,              -- ok, skip, fail, timeout, error
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
    tier            TEXT,              -- T0, T05, T1, T2, T3
    mode            TEXT,              -- ladder, scan, deep, rescore
    machine         TEXT,
    script          TEXT,
    n_polytopes     INTEGER,
    n_pass          INTEGER,
    elapsed_s       REAL,
    started_at      TEXT,
    finished_at     TEXT,
    thresholds      TEXT,              -- JSON of threshold values used
    notes           TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_poly_h11
    ON polytopes(h11);
CREATE INDEX IF NOT EXISTS idx_poly_tier
    ON polytopes(tier_reached);
CREATE INDEX IF NOT EXISTS idx_poly_nclean
    ON polytopes(n_clean);
CREATE INDEX IF NOT EXISTS idx_poly_sm_score
    ON polytopes(sm_score);
CREATE INDEX IF NOT EXISTS idx_poly_maxh0
    ON polytopes(max_h0);
CREATE INDEX IF NOT EXISTS idx_poly_yukawa
    ON polytopes(yukawa_rank);
CREATE INDEX IF NOT EXISTS idx_poly_lvs
    ON polytopes(lvs_score);
CREATE INDEX IF NOT EXISTS idx_poly_voltype
    ON polytopes(volume_form_type);
CREATE INDEX IF NOT EXISTS idx_fib_poly
    ON fibrations(h11, poly_idx);
"""


# ══════════════════════════════════════════════════════════════════
#  Database class
# ══════════════════════════════════════════════════════════════════

class LandscapeDB:
    """SQLite wrapper for the v3 CY landscape database."""

    # All valid column names in polytopes table (for safe upsert)
    POLYTOPE_COLUMNS = {
        'h11', 'poly_idx', 'h21', 'chi',
        # T0
        'favorable', 'h11_eff', 'gap', 'aut_order',
        # T05
        'yukawa_rank', 'yukawa_density', 'chi_over_24',
        'c2_all_positive', 'c2_vector', 'kappa_signature',
        'volume_form_type', 'n_kappa_entries',
        # T1
        'n_chi3', 'n_computed', 'max_h0', 'h0_ge3',
        'n_clean_est', 'first_clean_at',
        # T2 — bundles
        'n_bundles_checked', 'n_clean', 'max_h0_t2', 'h0_distribution',
        # T2 — divisors
        'n_dp', 'dp_types', 'n_k3_div', 'n_rigid',
        # T2 — Swiss/LVS
        'has_swiss', 'n_swiss', 'best_swiss_tau', 'best_swiss_ratio',
        'lvs_score', 'best_small_div', 'volume_hierarchy',
        # T2 — Yukawa texture
        'yukawa_texture_rank', 'yukawa_hierarchy', 'yukawa_zeros',
        'best_yukawa_bundle',
        # T2 — Mori
        'n_mori_rays', 'n_dp_contract',
        # T2 — fibrations
        'n_k3_fib', 'n_ell_fib', 'n_fibers',
        'has_SM', 'has_GUT', 'best_gauge',
        # T2 — D³
        'd3_min', 'd3_max', 'd3_n_distinct', 'd3_clean_values',
        # Scores
        'sm_score', 'screen_score',
        # T3
        'n_triangulations', 'props_stable', 'n_flux_vacua_est',
        'has_instanton_div', 'orientifold_ok',
        # Meta
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

    # Columns that must never decrease on re-scan
    MONOTONIC_MAX = {
        'max_h0', 'n_clean', 'n_bundles_checked',
        'max_h0_t2', 'h0_ge3', 'n_chi3', 'n_computed',
        'n_clean_est', 'yukawa_rank', 'n_kappa_entries',
        'sm_score',
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
        Monotonic columns (max_h0, n_clean, etc.) use MAX to prevent clobber.
        Automatically sets last_updated timestamp and computes chi from h21.
        """
        kwargs['h11'] = h11
        kwargs['poly_idx'] = poly_idx
        kwargs['last_updated'] = datetime.datetime.now().isoformat()

        # Compute derived fields
        if 'h21' in kwargs and kwargs['h21'] is not None:
            if 'chi' not in kwargs:
                kwargs['chi'] = 2 * (h11 - kwargs['h21'])
            if 'chi_over_24' not in kwargs:
                kwargs['chi_over_24'] = kwargs['chi'] / 24.0
        if 'h11_eff' in kwargs and kwargs['h11_eff'] is not None:
            if 'gap' not in kwargs:
                kwargs['gap'] = h11 - kwargs['h11_eff']

        # Filter to valid columns, convert types
        data = {}
        for k, v in kwargs.items():
            if k not in self.POLYTOPE_COLUMNS or v is None:
                continue
            if isinstance(v, bool):
                data[k] = int(v)
            elif isinstance(v, (dict, list)):
                data[k] = json.dumps(v)
            else:
                data[k] = v

        cols = list(data.keys())
        placeholders = ", ".join("?" for _ in cols)
        col_names = ", ".join(cols)

        # ON CONFLICT: update columns, MAX for monotonic metrics
        update_parts = []
        for c in cols:
            if c in ('h11', 'poly_idx'):
                continue
            if c in self.MONOTONIC_MAX:
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

            # Derived fields
            h21 = row.get('h21')
            if h21 is not None and 'chi' not in row:
                row['chi'] = 2 * (h11 - h21)
            h11_eff = row.get('h11_eff')
            if h11_eff is not None and 'gap' not in row:
                row['gap'] = h11 - h11_eff

            # Filter + convert
            data = {}
            for k, v in row.items():
                if k not in self.POLYTOPE_COLUMNS or v is None:
                    continue
                if isinstance(v, bool):
                    data[k] = int(v)
                elif isinstance(v, (dict, list)):
                    data[k] = json.dumps(v)
                else:
                    data[k] = v

            cols = list(data.keys())
            placeholders = ", ".join("?" for _ in cols)
            col_names = ", ".join(cols)

            update_parts = []
            for c in cols:
                if c in ('h11', 'poly_idx'):
                    continue
                if c in self.MONOTONIC_MAX:
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
        """Add a fibration record. Deduplicates by (h11, poly_idx, fiber_type, gauge_algebra)."""
        kwargs['h11'] = h11
        kwargs['poly_idx'] = poly_idx

        for k, v in kwargs.items():
            if isinstance(v, bool):
                kwargs[k] = int(v)
            elif isinstance(v, (dict, list)):
                kwargs[k] = json.dumps(v)

        data = {k: v for k, v in kwargs.items()
                if k in self.FIBRATION_COLUMNS and v is not None}

        existing = self._conn.execute(
            "SELECT id FROM fibrations WHERE h11=? AND poly_idx=? "
            "AND fiber_type=? AND gauge_algebra=?",
            (h11, poly_idx, data.get('fiber_type'), data.get('gauge_algebra'))
        ).fetchone()
        if existing:
            return

        cols = list(data.keys())
        placeholders = ", ".join("?" for _ in cols)
        col_names = ", ".join(cols)
        self._conn.execute(
            f"INSERT INTO fibrations ({col_names}) VALUES ({placeholders})",
            [data[c] for c in cols]
        )
        self._conn.commit()

    def log_scan(self, h11, tier, mode='scan', machine='unknown', **kwargs):
        """Record a scan batch in the audit trail."""
        kwargs['h11'] = h11
        kwargs['tier'] = tier
        kwargs['mode'] = mode
        kwargs['machine'] = machine
        kwargs['finished_at'] = datetime.datetime.now().isoformat()

        valid_cols = {'h11', 'tier', 'mode', 'machine', 'script',
                      'n_polytopes', 'n_pass', 'elapsed_s',
                      'started_at', 'finished_at', 'thresholds', 'notes'}
        data = {k: v for k, v in kwargs.items() if k in valid_cols}
        if isinstance(data.get('thresholds'), dict):
            data['thresholds'] = json.dumps(data['thresholds'])

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
        """Run SQL query, return list of dicts."""
        cursor = self._conn.execute(sql, params or [])
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def query_df(self, sql, params=None):
        """Run SQL query, return pandas DataFrame."""
        import pandas as pd
        return pd.read_sql_query(sql, self._conn, params=params)

    def get_polytope(self, h11, poly_idx):
        """Get a single polytope row as dict, or None."""
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

    # ── Leaderboards ──────────────────────────────────────────

    def leaderboard(self, limit=20, min_score=0):
        """Top polytopes by sm_score."""
        return self.query(
            "SELECT h11, poly_idx, h11_eff, gap, sm_score, "
            "n_clean, max_h0, yukawa_rank, lvs_score, "
            "volume_form_type, has_SM, best_gauge, tier_reached "
            "FROM polytopes "
            "WHERE COALESCE(sm_score, 0) >= ? "
            "ORDER BY COALESCE(sm_score, 0) DESC LIMIT ?",
            (min_score, limit)
        )

    def coverage(self):
        """Polytope count and tier distribution per h11."""
        return self.query(
            "SELECT h11, COUNT(*) as n_total, "
            "SUM(CASE WHEN tier_reached='T0' THEN 1 ELSE 0 END) as n_t0, "
            "SUM(CASE WHEN tier_reached='T05' THEN 1 ELSE 0 END) as n_t05, "
            "SUM(CASE WHEN tier_reached='T1' THEN 1 ELSE 0 END) as n_t1, "
            "SUM(CASE WHEN tier_reached='T2' THEN 1 ELSE 0 END) as n_t2, "
            "SUM(CASE WHEN tier_reached='T3' THEN 1 ELSE 0 END) as n_t3, "
            "MAX(sm_score) as best_score, MAX(n_clean) as best_clean, "
            "MAX(max_h0) as best_h0, "
            "SUM(CASE WHEN n_clean > 0 THEN 1 ELSE 0 END) as n_with_clean, "
            "AVG(yukawa_density) as avg_yukawa_density "
            "FROM polytopes GROUP BY h11 ORDER BY h11"
        )

    def needs_tier(self, target_tier, h11=None, limit=500):
        """Find polytopes that haven't reached target_tier yet.

        Returns polytopes ordered by best available score.
        """
        tier_order = {'T0': 0, 'T05': 1, 'T1': 2, 'T2': 3, 'T3': 4}
        target_val = tier_order.get(target_tier, 3)
        below = [t for t, v in tier_order.items() if v < target_val]
        if not below:
            return []

        placeholders = ", ".join("?" for _ in below)
        h11_clause = "AND h11 = ?" if h11 else ""
        params = below + ([h11] if h11 else []) + [limit]

        return self.query(
            f"SELECT h11, poly_idx, tier_reached, "
            f"COALESCE(sm_score, 0) as score "
            f"FROM polytopes "
            f"WHERE (tier_reached IS NULL OR tier_reached IN ({placeholders})) "
            f"{h11_clause} "
            f"ORDER BY score DESC LIMIT ?",
            params
        )

    def landscape_summary(self):
        """Quick overview of the full landscape."""
        return self.query(
            "SELECT h11, COUNT(*) as n, "
            "SUM(CASE WHEN status='skip' THEN 1 ELSE 0 END) as n_skip, "
            "SUM(CASE WHEN n_clean > 0 THEN 1 ELSE 0 END) as n_clean_any, "
            "MAX(sm_score) as top_score, "
            "AVG(CASE WHEN yukawa_rank > 0 THEN yukawa_density END) as avg_yuk, "
            "SUM(CASE WHEN volume_form_type='swiss_cheese' THEN 1 ELSE 0 END) as n_swiss, "
            "SUM(CASE WHEN has_SM=1 THEN 1 ELSE 0 END) as n_sm "
            "FROM polytopes GROUP BY h11 ORDER BY h11"
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
        return f"<LandscapeDB v3: {self.db_path} ({total} polytopes)>"


# ══════════════════════════════════════════════════════════════════
#  CLI: quick status
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB

    if not os.path.exists(db_path):
        print(f"Creating new v3 database: {db_path}")
        db = LandscapeDB(db_path)
        print("  Tables created.")
    else:
        db = LandscapeDB(db_path)
        print(f"Database: {db_path}")
        s = db.stats()
        print(f"  Polytopes: {s['total_polytopes']}")
        print(f"  Fibrations: {s['total_fibrations']}")
        print(f"  Scan log entries: {s['total_scans']}")

        cov = db.coverage()
        if cov:
            print(f"\n  {'h11':>4} {'total':>7} {'T0':>5} {'T05':>5} "
                  f"{'T1':>5} {'T2':>5} {'T3':>5} {'score':>6} {'clean':>6}")
            for r in cov:
                print(f"  {r['h11']:>4} {r['n_total']:>7} "
                      f"{r['n_t0'] or 0:>5} {r['n_t05'] or 0:>5} "
                      f"{r['n_t1'] or 0:>5} {r['n_t2'] or 0:>5} "
                      f"{r['n_t3'] or 0:>5} "
                      f"{r['best_score'] or '-':>6} "
                      f"{r['best_clean'] or '-':>6}")

        lb = db.leaderboard(limit=10)
        if lb:
            print(f"\n  Top 10 by SM score:")
            for r in lb:
                print(f"    h{r['h11']}/P{r['poly_idx']}: "
                      f"score={r['sm_score']}, clean={r['n_clean']}, "
                      f"yuk={r['yukawa_rank']}, lvs={r['lvs_score']}, "
                      f"type={r['volume_form_type']}, gauge={r['best_gauge']}")

    db.close()
