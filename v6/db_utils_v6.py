#!/usr/bin/env python3
"""db_utils_v6.py — Database layer for pipeline v6.

Thin wrapper around v5's LandscapeDB. Points at v6's own database copy
(v6/cy_landscape_v6.db) so the original v4 DB is untouched.

Usage:
    from db_utils_v6 import LandscapeDB

    db = LandscapeDB()                 # opens v6/cy_landscape_v6.db
    db = LandscapeDB('path/to/other')  # custom path
    db.upsert_polytope(h11=15, poly_idx=61, sm_score=72, ...)
    db.close()
"""

import sys
import os

# Ensure v5 is importable
_v6_dir = os.path.dirname(os.path.abspath(__file__))
_v5_dir = os.path.join(os.path.dirname(_v6_dir), 'v5')
if _v5_dir not in sys.path:
    sys.path.insert(0, _v5_dir)

from db_utils_v5 import LandscapeDB as _LandscapeDB_v5, SCHEMA_SQL  # noqa: E402,F401

# v6 uses its own DB copy so the original v4 DB stays untouched
DEFAULT_DB = os.path.join(_v6_dir, 'cy_landscape_v6.db')


class LandscapeDB(_LandscapeDB_v5):
    """v6 LandscapeDB — same as v5 but defaults to v6/cy_landscape_v6.db."""

    def __init__(self, db_path=None):
        super().__init__(db_path or DEFAULT_DB)

    def __repr__(self):
        total = self._conn.execute(
            "SELECT COUNT(*) FROM polytopes").fetchone()[0]
        return f"<LandscapeDB v6: {self.db_path} ({total} polytopes)>"


__all__ = ['LandscapeDB', 'DEFAULT_DB', 'SCHEMA_SQL']
