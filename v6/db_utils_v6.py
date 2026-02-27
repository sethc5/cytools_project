#!/usr/bin/env python3
"""db_utils_v6.py — Database layer for pipeline v6.

Thin wrapper around v5's LandscapeDB. Same schema, same DB file
(v4/cy_landscape_v4.db). v5 already has the tri_stability migration.

Usage:
    from db_utils_v6 import LandscapeDB

    db = LandscapeDB()
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

from db_utils_v5 import LandscapeDB, DEFAULT_DB, SCHEMA_SQL  # noqa: E402,F401

__all__ = ['LandscapeDB', 'DEFAULT_DB', 'SCHEMA_SQL']
