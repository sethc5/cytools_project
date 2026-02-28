#!/usr/bin/env python3
"""
pipeline_v6.py — Physics-driven scan pipeline v6.

Iterates on v5 pipeline. Same 4-tier architecture, same DB, same compute
functions. Changes:
  1. Fixed import path: archive/v2/ (v5 pointed at non-existent v2/)
  2. v6 scoring weights (audit-validated on 501K polytopes)
  3. source_file tag → pipeline_v6.py

4-tier architecture:
  T0   (0.1s)   Geometry + intersection algebra    kills ~85%
  T1   (0.5s)   Bundle screening                   kills ~70%
  T2   (3-30s)  Deep physics + scoring             top ~1K
  T3   (30s+)   Full phenomenology + tri stability  top ~50

v6 scoring changes from v5:
  - tadpole_ok 5→0: dead (100% pass for χ=-6)
  - lvs_binary 5→0: near-dead (96.1%), merged into lvs_quality
  - lvs_quality 10→15: 7-tier grading
  - mori_blowdown 5→2: near-dead (99.7%), keeps fraction grading
  - yukawa_hierarchy 27→30: THE key discriminator, extended brackets
  - vol_hierarchy 5→7: better graded
  - bundle_quality 0→3: NEW conjunction of depth + rate
  Total: 100 pts, 0 stranded.

Inherited from v5:
  - first_clean_at fix (v5.2): T2 worker tracks bundle index
  - MONOTONIC_MAX rescore (v5.2): post-upsert rescore from merged DB row
  - compute_tri_stability (v5.0): c₂/κ hash stability in T3
  - rank_sweet_spot (v5.0): 3 pts for Yukawa rank 140-159
  - Graded mori_blowdown (v5.0): fraction-based, now capped at 2 pts
  - --limit CLI (v5.1): KS fetch limit with auto-adjust in deep mode

Execution modes:
  --ladder --h11 13 30     T0 only, fast landscape mapping
  --scan   --h11 19        Full T0→T2 for one h11
  --scan   --h11 28 --limit 10000   Scan first 10K polytopes at h11=28
  --deep   --top 50        T3 on top candidates (includes fiber + tri stability)
  --rescore                Recompute SM scores from existing data

All results written to cy_landscape_v4.db (shared with v4/v5) in real time.
"""

import argparse
import json
import multiprocessing as mp
import socket
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

# ── Fix import path BEFORE anything else ─────────────────────────
# v5's cy_compute_v5.py adds 'v2/' to sys.path, but the actual
# location is 'archive/v2/'. We add the correct path first so
# the import succeeds regardless of v5's broken path.
import sys
import os
_v6_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_v6_dir)
_archive_v2_dir = os.path.join(_project_root, 'archive', 'v2')
if _archive_v2_dir not in sys.path:
    sys.path.insert(0, _archive_v2_dir)

# Now safe to import v6 modules (which import v5 which imports v2)
if _v6_dir not in sys.path:
    sys.path.insert(0, _v6_dir)

from db_utils_v6 import LandscapeDB
from cy_compute_v6 import (
    # v2 re-exports
    find_chi3_bundles,
    find_chi3_bundles_capped,
    compute_h0_koszul, precompute_vertex_data,
    basis_to_toric, compute_D3, count_fibrations,
    clear_poly_cache,
    # v3 compute functions
    analyze_intersection_algebra,
    compute_lvs_score,
    compute_yukawa_texture,
    analyze_mori_cone,
    classify_divisors,
    compute_sm_score,
    check_triangulation_stability,
    check_instanton_divisor,
    # v5 new
    compute_tri_stability,
)

SOURCE_FILE = 'pipeline_v6.py'

# ══════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════

RESULTS_DIR = Path(_v6_dir) / "results"
RESULTS_DIR.mkdir(exist_ok=True)

RECEIPTS_DIR = Path(_v6_dir) / "receipts"
RECEIPTS_DIR.mkdir(exist_ok=True)

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
RED = "\033[91m"

# ── Thresholds (carried from v4→v5, data-driven) ──
EFF_MAX = 22        # Skip h11_eff > 22
GAP_MIN = 2         # Min gap for priority track
H0_MIN_T1 = 5       # Bundle screening threshold
AUT_MAX = 4         # Skip |Aut| > 4
YUK_MIN_FRAC = 0.5  # Skip if yukawa_rank < h11_eff * this

# ── Worker timeout ──
T1_BUDGET_SEC = 2.0   # Time budget for adaptive T1 clean counting
T1_WALL_SEC = 120     # Hard wall-time per T1 polytope
T1_BUNDLE_CAP = 500   # Max chi=3 bundles to find at T1


# ══════════════════════════════════════════════════════════════════
#  T0: Geometry + Intersection Algebra (~0.1s/poly)
# ══════════════════════════════════════════════════════════════════

def _t0_worker(args):
    """Compute geometry fingerprint + intersection algebra.

    Returns dict with identity + geometry + intersection fields + skip_reason.
    """
    vert, poly_idx, h11_val = args
    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()

        p = Polytope(vert)
        tri = p.triangulate()
        cy = tri.get_cy()

        h11 = cy.h11()
        h21 = cy.h21()
        chi = 2 * (h11 - h21)
        div_basis = [int(x) for x in cy.divisor_basis()]
        h11_eff = len(div_basis)
        gap = h11 - h11_eff
        favorable = (h11_eff == h11)

        try:
            aut_order = len(p.automorphisms())
        except Exception:
            aut_order = 1

        # Pre-filter (geometry)
        skip_reason = None
        if abs(chi) != 6:
            skip_reason = f'chi={chi}!=±6'
        elif h11_eff > EFF_MAX:
            skip_reason = f'eff={h11_eff}>{EFF_MAX}'
        elif gap < GAP_MIN and h11_eff >= 15:
            skip_reason = f'gap={gap}<{GAP_MIN},eff={h11_eff}'
        elif aut_order > AUT_MAX:
            skip_reason = f'|Aut|={aut_order}>{AUT_MAX}'

        result = {
            'poly_idx': poly_idx,
            'h11': h11, 'h21': h21, 'chi': chi,
            'h11_eff': h11_eff, 'gap': gap,
            'favorable': favorable,
            'aut_order': aut_order,
            'skip_reason': skip_reason,
            'status': 'skip' if skip_reason else 'pass',
        }

        # Collect intersection algebra data for passing polytopes
        if skip_reason is None:
            intnums = dict(cy.intersection_numbers(in_basis=True))
            c2 = np.array(cy.second_chern_class(in_basis=True), dtype=float)
            t05_data = analyze_intersection_algebra(cy, h11_eff, intnums, c2)
            result.update(t05_data)

        return result
    except Exception as e:
        return {
            'poly_idx': poly_idx, 'h11': h11_val,
            'status': 'error',
            'skip_reason': f'error: {str(e)[:80]}',
        }


# ══════════════════════════════════════════════════════════════════
#  T1: Bundle Screening (~0.5s/poly)
# ══════════════════════════════════════════════════════════════════

def _t1_worker(args):
    """Bundle screening with adaptive depth + wall-time limit.

    Finds χ=±3 bundles (capped), computes h⁰ with early-exit, then
    counts clean bundles within a time budget.  Hard wall-time limit
    prevents any single polytope from blocking a worker >2 min.
    """
    vert, poly_idx, h11_val = args
    t0 = time.time()
    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()

        p = Polytope(vert)
        tri = p.triangulate()
        cy = tri.get_cy()

        pts = np.array(p.points(), dtype=int)
        n_toric = pts.shape[0]
        ray_indices = list(range(1, n_toric))
        div_basis = [int(x) for x in cy.divisor_basis()]
        h11_eff = len(div_basis)
        intnums = dict(cy.intersection_numbers(in_basis=True))
        c2 = np.array(cy.second_chern_class(in_basis=True), dtype=float)

        if not np.all(pts[0] == 0) or len(c2) != h11_eff:
            return {'poly_idx': poly_idx, 'status': 'skip',
                    'max_h0': 0, 'n_chi3': 0}

        # Adaptive search parameters
        if h11_eff <= 15:
            mc, mnz = 3, 3
        elif h11_eff <= 20:
            mc, mnz = 2, 3
        else:
            mc, mnz = 2, 2

        bundles = find_chi3_bundles_capped(intnums, c2, h11_eff, mc, mnz,
                                           cap=T1_BUNDLE_CAP)
        n_chi3 = len(bundles)

        if not bundles:
            return {'poly_idx': poly_idx, 'status': 'skip',
                    'max_h0': 0, 'n_chi3': 0}

        _precomp = precompute_vertex_data(pts, ray_indices)
        max_h0 = 0
        h0_ge3 = 0
        n_clean_est = 0
        first_clean_at = -1
        timed_out = False
        n_checked = 0
        t_budget_start = time.time()

        for idx, (D_basis, chi_val) in enumerate(bundles):
            # Budget check (after first clean hit)
            if n_clean_est > 0 and (time.time() - t_budget_start) > T1_BUDGET_SEC:
                break

            # Wall-time check every 10 bundles
            if idx % 10 == 0 and idx > 0:
                if (time.time() - t0) > T1_WALL_SEC:
                    timed_out = True
                    break

            D_toric = basis_to_toric(D_basis, div_basis, n_toric)

            if chi_val > 0:
                h0 = compute_h0_koszul(pts, ray_indices, D_toric,
                                       _precomp=_precomp, min_h0=H0_MIN_T1)
            else:
                D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
                h0 = compute_h0_koszul(pts, ray_indices, D_neg,
                                       _precomp=_precomp, min_h0=H0_MIN_T1)

            if h0 < 0:
                continue
            n_checked += 1
            if h0 > max_h0:
                max_h0 = h0
            if h0 >= 3:
                h0_ge3 += 1

            # Clean check: h⁰ = 3 AND h³ = 0
            if h0 == 3 and abs(abs(chi_val) - 3.0) < 0.01:
                if chi_val > 0:
                    D_dual = basis_to_toric(-D_basis, div_basis, n_toric)
                else:
                    D_dual = D_toric
                h3 = compute_h0_koszul(pts, ray_indices, D_dual,
                                       _precomp=_precomp)
                if h3 == 0:
                    n_clean_est += 1
                    if first_clean_at < 0:
                        first_clean_at = idx

        passed = max_h0 >= H0_MIN_T1 or n_clean_est > 0

        status = 'timeout' if timed_out else ('pass' if passed else 'skip')

        return {
            'poly_idx': poly_idx,
            'status': status,
            'max_h0': max_h0,
            'h0_ge3': h0_ge3,
            'n_chi3': n_chi3,
            'n_clean_est': n_clean_est,
            'first_clean_at': first_clean_at,
            'n_checked': n_checked,
            'elapsed': time.time() - t0,
        }
    except Exception as e:
        return {'poly_idx': poly_idx, 'status': 'error',
                'max_h0': 0, 'n_chi3': 0,
                'error': str(e)[:100]}


# ══════════════════════════════════════════════════════════════════
#  T2: Deep Physics (3-30s/poly)
# ══════════════════════════════════════════════════════════════════

def _t2_worker(args):
    """Full deep analysis: bundles + divisors + LVS + Yukawa + Mori + fibrations.

    Returns a rich dict with all T2 fields + sm_score (v6 weights).
    """
    vert, poly_idx, h11_val = args
    t0 = time.time()

    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()

        p = Polytope(vert)
        tri = p.triangulate()
        cy = tri.get_cy()

        pts = np.array(p.points(), dtype=int)
        n_toric = pts.shape[0]
        ray_indices = list(range(1, n_toric))
        div_basis = [int(x) for x in cy.divisor_basis()]
        h11 = cy.h11()
        h21 = cy.h21()
        chi = 2 * (h11 - h21)
        h11_eff = len(div_basis)
        intnums = dict(cy.intersection_numbers(in_basis=True))
        c2 = np.array(cy.second_chern_class(in_basis=True), dtype=float)

        if not np.all(pts[0] == 0) or len(c2) != h11_eff:
            return {'poly_idx': poly_idx, 'status': 'data_fail'}

        # ── Full bundle census ──
        if h11_eff <= 15:
            mc, mnz = 3, 3
        elif h11_eff <= 20:
            mc, mnz = 2, 3
        else:
            mc, mnz = 2, 2

        bundles = find_chi3_bundles(intnums, c2, h11_eff, mc, mnz)
        n_chi3 = len(bundles)

        _precomp = precompute_vertex_data(pts, ray_indices)
        max_h0 = 0
        h0_ge3 = 0
        n_clean = 0
        d3_values = []
        h0_dist = Counter()
        best_clean_D = None
        first_clean_at = -1  # v5.2 fix: track first clean bundle index

        for idx, (D_basis, chi_val) in enumerate(bundles):
            D_toric = basis_to_toric(D_basis, div_basis, n_toric)

            if chi_val > 0:
                h0 = compute_h0_koszul(pts, ray_indices, D_toric,
                                       _precomp=_precomp)
            else:
                D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
                h0 = compute_h0_koszul(pts, ray_indices, D_neg,
                                       _precomp=_precomp)

            if h0 < 0:
                continue
            h0_dist[h0] += 1
            if h0 > max_h0:
                max_h0 = h0
            if h0 >= 3:
                h0_ge3 += 1

            if h0 == 3 and abs(abs(chi_val) - 3.0) < 0.01:
                if chi_val > 0:
                    D_dual = basis_to_toric(-D_basis, div_basis, n_toric)
                else:
                    D_dual = D_toric
                h3 = compute_h0_koszul(pts, ray_indices, D_dual,
                                       _precomp=_precomp)
                if h3 == 0:
                    n_clean += 1
                    if first_clean_at < 0:
                        first_clean_at = idx
                    d3 = compute_D3(D_basis, intnums)
                    d3_values.append(d3)
                    if best_clean_D is None:
                        best_clean_D = D_basis.copy()

        d3_unique = sorted(set(d3_values))

        # ── Divisor classification ──
        div_info = classify_divisors(intnums, c2, h11_eff)

        # ── LVS compatibility ──
        lvs_info = compute_lvs_score(cy, h11_eff)

        # ── Yukawa texture (on best clean bundle) ──
        yuk_info = {'yukawa_texture_rank': 0, 'yukawa_hierarchy': 0.0,
                     'yukawa_zeros': 0}
        if best_clean_D is not None:
            yuk_info = compute_yukawa_texture(best_clean_D, intnums, h11_eff)

        # ── Mori cone ──
        mori_info = analyze_mori_cone(cy, h11_eff, intnums, c2)

        # ── Fibrations ──
        n_k3, n_ell = count_fibrations(p)

        # ── Assemble result ──
        result = {
            'poly_idx': poly_idx,
            'h11': h11, 'h21': h21, 'chi': chi,
            'h11_eff': h11_eff,
            'favorable': int(h11_eff == h11),
            'gap': h11 - h11_eff,
            'status': 'ok',
            # Bundles
            'n_chi3': n_chi3,
            'n_bundles_checked': n_chi3,
            'n_clean': n_clean,
            'first_clean_at': first_clean_at,
            'max_h0': max_h0,
            'max_h0_t2': max_h0,
            'h0_ge3': h0_ge3,
            'h0_distribution': dict(h0_dist),
            'd3_n_distinct': len(d3_unique),
            'd3_clean_values': d3_unique[:20],
            'd3_min': min(d3_values) if d3_values else None,
            'd3_max': max(d3_values) if d3_values else None,
            # Divisors
            **div_info,
            # LVS
            **lvs_info,
            # Yukawa texture
            **yuk_info,
            'best_yukawa_bundle': (best_clean_D.tolist()
                                   if best_clean_D is not None else None),
            # Mori
            **mori_info,
            # Fibrations
            'n_k3_fib': n_k3,
            'n_ell_fib': n_ell,
            # Timing
            'elapsed': time.time() - t0,
        }

        # ── SM Score (v6 weights) ──
        result['chi_over_24'] = chi / 24.0
        result['c2_all_positive'] = int(np.all(c2[:h11_eff] >= 0))
        result['sm_score'] = compute_sm_score(result)

        return result

    except Exception as e:
        return {'poly_idx': poly_idx, 'status': 'error',
                'error': str(e)[:200]}


# ══════════════════════════════════════════════════════════════════
#  T2+: Fiber Analysis (gauge algebra)
# ══════════════════════════════════════════════════════════════════

def _fiber_worker(args):
    """Multiprocessing-safe fiber analysis worker."""
    vert, poly_idx, h11_val = args
    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()

        p = Polytope(vert)
        return _run_fiber_analysis(p, poly_idx, h11_val)
    except Exception as e:
        return {'poly_idx': poly_idx, 'n_fibrations': 0,
                'error': str(e)[:200]}


def _run_fiber_analysis(polytope, poly_idx, h11_val):
    """Kodaira fiber classification → gauge algebra."""
    try:
        _v2_dir = os.path.join(_project_root, 'archive', 'v2')
        if _v2_dir not in sys.path:
            sys.path.insert(0, _v2_dir)
        from fiber_analysis import analyze_polytope
        result = analyze_polytope(polytope, h11=h11_val, verbose=False)
        result['poly_idx'] = poly_idx
        return result
    except Exception as e:
        return {'poly_idx': poly_idx, 'n_fibrations': 0,
                'error': str(e)[:200]}


# ══════════════════════════════════════════════════════════════════
#  Database integration
# ══════════════════════════════════════════════════════════════════

def db_upsert_t0(db, h11, results):
    """Batch upsert T0 results (includes intersection algebra data)."""
    rows = []
    for r in results:
        row = {
            'h11': h11,
            'poly_idx': r['poly_idx'],
            'h21': r.get('h21'),
            'chi': r.get('chi'),
            'h11_eff': r.get('h11_eff'),
            'gap': r.get('gap'),
            'favorable': r.get('favorable'),
            'aut_order': r.get('aut_order'),
            'tier_reached': 'T0',
            'source_file': SOURCE_FILE,
            'status': r.get('status'),
            'error': r.get('skip_reason'),
        }
        # Intersection algebra data (merged from T05)
        if r.get('yukawa_rank') is not None:
            row.update({
                'yukawa_rank': r.get('yukawa_rank'),
                'yukawa_density': r.get('yukawa_density'),
                'c2_all_positive': r.get('c2_all_positive'),
                'c2_vector': r.get('c2_vector'),
                'kappa_signature': r.get('kappa_signature'),
                'volume_form_type': r.get('volume_form_type'),
                'n_kappa_entries': r.get('n_kappa_entries'),
            })
        rows.append(row)
    db.upsert_polytopes_batch(rows)


def db_upsert_t1(db, h11, results):
    """Batch upsert T1 results."""
    rows = []
    for r in results:
        rows.append({
            'h11': h11,
            'poly_idx': r['poly_idx'],
            'max_h0': r.get('max_h0'),
            'h0_ge3': r.get('h0_ge3'),
            'n_chi3': r.get('n_chi3'),
            'n_clean_est': r.get('n_clean_est'),
            'first_clean_at': r.get('first_clean_at'),
            'tier_reached': 'T1',
            'source_file': SOURCE_FILE,
            'status': r.get('status'),
            'elapsed': r.get('elapsed'),
        })
    db.upsert_polytopes_batch(rows)


def db_upsert_t2(db, r, auto_commit=True):
    """Upsert a single T2 result."""
    dp_str = '|'.join(str(d) for d in r.get('dp_types', []))
    h0_str = json.dumps(r.get('h0_distribution', {}))
    d3_str = json.dumps(r.get('d3_clean_values', []))

    db.upsert_polytope(r['h11'], r['poly_idx'],
        auto_commit=auto_commit,
        h21=r.get('h21'),
        chi=r.get('chi'),
        h11_eff=r.get('h11_eff'),
        gap=r.get('gap'),
        favorable=r.get('favorable'),
        # Bundles
        n_chi3=r.get('n_chi3'),
        n_bundles_checked=r.get('n_bundles_checked'),
        n_clean=r.get('n_clean'),
        first_clean_at=r.get('first_clean_at'),
        max_h0=r.get('max_h0'),
        max_h0_t2=r.get('max_h0_t2'),
        h0_ge3=r.get('h0_ge3'),
        h0_distribution=h0_str,
        d3_n_distinct=r.get('d3_n_distinct'),
        d3_clean_values=d3_str,
        d3_min=r.get('d3_min'),
        d3_max=r.get('d3_max'),
        # Divisors
        n_dp=r.get('n_dp'),
        dp_types=dp_str,
        n_k3_div=r.get('n_k3_div'),
        n_rigid=r.get('n_rigid'),
        # LVS
        has_swiss=r.get('has_swiss'),
        n_swiss=r.get('n_swiss'),
        best_swiss_tau=r.get('best_swiss_tau'),
        best_swiss_ratio=r.get('best_swiss_ratio'),
        lvs_score=r.get('lvs_score'),
        best_small_div=r.get('best_small_div'),
        volume_hierarchy=r.get('volume_hierarchy'),
        # Yukawa
        yukawa_texture_rank=r.get('yukawa_texture_rank'),
        yukawa_hierarchy=r.get('yukawa_hierarchy'),
        yukawa_zeros=r.get('yukawa_zeros'),
        best_yukawa_bundle=(json.dumps(r['best_yukawa_bundle'])
                            if r.get('best_yukawa_bundle') is not None
                            else None),
        # Mori
        n_mori_rays=r.get('n_mori_rays'),
        n_dp_contract=r.get('n_dp_contract'),
        # Fibrations
        n_k3_fib=r.get('n_k3_fib'),
        n_ell_fib=r.get('n_ell_fib'),
        # T05 fields (re-asserted)
        c2_all_positive=r.get('c2_all_positive'),
        chi_over_24=r.get('chi_over_24'),
        # Score
        sm_score=r.get('sm_score'),
        # Meta
        tier_reached='T2',
        source_file=SOURCE_FILE,
        status=r.get('status'),
        elapsed=r.get('elapsed'),
    )


def db_upsert_fiber(db, h11, poly_idx, fiber_result):
    """Upsert gauge algebra results from fiber analysis."""
    fibs = fiber_result.get('fibrations', [])
    has_sm = any(f.get('contains_SM') for f in fibs)
    has_gut = any(f.get('has_SU5_GUT') for f in fibs)
    best_gauge = ''
    if fibs:
        best = max(fibs, key=lambda f: f.get('gauge_rank', 0), default={})
        best_gauge = best.get('gauge_algebra', '')

    db.upsert_polytope(h11, poly_idx,
        n_fibers=len(fibs),
        has_SM=has_sm,
        has_GUT=has_gut,
        best_gauge=best_gauge,
    )

    for fib in fibs:
        db.add_fibration(h11, poly_idx, **fib)


# ══════════════════════════════════════════════════════════════════
#  Display helpers
# ══════════════════════════════════════════════════════════════════

def fmt_time(secs):
    if secs < 60:
        return f"{secs:.0f}s"
    elif secs < 3600:
        return f"{secs/60:.1f}m"
    else:
        return f"{secs/3600:.1f}h"


def print_header(mode, h11_range, n_polys, n_workers):
    print(f"\n{'='*72}")
    print(f"  {BOLD}PIPELINE v6 (PHYSICS-DRIVEN){RESET}  "
          f"mode={mode}  |  h11={h11_range}  |  {n_workers} workers")
    print(f"  {DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"  {DIM}EFF_MAX={EFF_MAX}  GAP_MIN={GAP_MIN}  "
          f"H0_MIN={H0_MIN_T1}  AUT_MAX={AUT_MAX}  "
          f"T1_WALL={T1_WALL_SEC}s  T1_CAP={T1_BUNDLE_CAP}{RESET}")
    if n_polys:
        print(f"  {DIM}{n_polys:,} polytopes{RESET}")
    print(f"{'='*72}\n")


def print_progress(done, total, n_pass, elapsed, label="pass"):
    rate = done / elapsed if elapsed > 0 else 0
    eta = (total - done) / rate if rate > 0 else 0
    pct = 100 * done / total if total > 0 else 0
    bar_w = 30
    filled = int(bar_w * done / total) if total > 0 else 0
    bar = '#' * filled + '-' * (bar_w - filled)
    print(f"\r    [{bar}] {pct:5.1f}%  "
          f"{done:,}/{total:,}  {n_pass} {label}  "
          f"{rate:.1f}/s  ETA {fmt_time(eta)}  ", end='', flush=True)


# ══════════════════════════════════════════════════════════════════
#  Rescore mode
# ══════════════════════════════════════════════════════════════════

def run_rescore(db):
    """Recompute SM scores for all polytopes with T2 data (v6 weights)."""
    rows = db.query(
        "SELECT * FROM polytopes WHERE tier_reached IN ('T2', 'T3')")
    print(f"  Rescoring {len(rows)} polytopes with v6 weights...")
    updated = 0
    for row in rows:
        new_score = compute_sm_score(row)
        old_score = row.get('sm_score') or 0
        if new_score != old_score:
            db.upsert_polytope(row['h11'], row['poly_idx'],
                               sm_score=new_score)
            updated += 1
    print(f"  Updated {updated} scores (of {len(rows)} total)")


# ══════════════════════════════════════════════════════════════════
#  Ladder mode: T0 only
# ══════════════════════════════════════════════════════════════════

def run_ladder(h11_start, h11_end, workers=4, db=None, ks_limit=1000):
    """Run T0 across h11 range. Fast landscape mapping."""
    import cytools as ct
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    for h11 in range(h11_start, h11_end + 1):
        h21 = h11 + 3
        t_h11_start = time.time()

        print(f"\n  {'─'*56}")
        print(f"  {BOLD}h11 = {h11}{RESET}")

        try:
            polys = list(ct.fetch_polytopes(h11=h11, h21=h21, limit=ks_limit))
        except Exception as e:
            print(f"    {RED}Fetch failed: {e}{RESET}")
            continue

        n_polys = len(polys)
        if n_polys == 0:
            print(f"    No polytopes at h11={h11}, h21={h21}")
            continue

        print(f"  {n_polys:,} polytopes")

        # ── T0 ──
        print(f"\n    T0: geometry + intersection algebra...")
        t0_start = time.time()
        t0_args = [(np.array(p.points(), dtype=int).tolist(), idx, h11)
                   for idx, p in enumerate(polys)]

        with mp.Pool(workers) as pool:
            t0_results = pool.map(_t0_worker, t0_args, chunksize=50)

        t0_pass = [r for r in t0_results if r['status'] == 'pass']
        t0_elapsed = time.time() - t0_start
        print(f"    T0: {len(t0_pass):,}/{n_polys:,} pass "
              f"({100*len(t0_pass)/n_polys:.1f}%), {t0_elapsed:.1f}s")

        if db:
            db_upsert_t0(db, h11, t0_results)
            db.log_scan(h11, 'T0', mode='ladder',
                       machine=socket.gethostname(),
                       script=SOURCE_FILE,
                       n_polytopes=n_polys, n_pass=len(t0_pass),
                       elapsed_s=t0_elapsed)

        if not t0_pass:
            continue

        total_elapsed = time.time() - t_h11_start
        vf_counts = Counter(r.get('volume_form_type', 'unknown')
                          for r in t0_pass)
        vf_str = ", ".join(f"{k}={v}" for k, v in vf_counts.most_common())
        print(f"    Volume forms: {vf_str}")

        yuk_ranks = [r['yukawa_rank'] for r in t0_pass
                    if r.get('yukawa_rank') is not None]
        if yuk_ranks:
            print(f"    Yukawa rank: "
                  f"mean={np.mean(yuk_ranks):.1f}, "
                  f"max={max(yuk_ranks)}, "
                  f"min={min(yuk_ranks)}")

        print(f"    Total: {total_elapsed:.1f}s")

        clear_poly_cache()


# ══════════════════════════════════════════════════════════════════
#  Scan mode: T0 → T2 for one h11
# ══════════════════════════════════════════════════════════════════

def run_scan(h11, workers=4, top_n=500, db=None, resume=False, ks_limit=1000):
    """Full T0→T2 scan for a single h11 value."""
    import cytools as ct
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    h21 = h11 + 3
    t_start = time.time()

    polys = list(ct.fetch_polytopes(h11=h11, h21=h21, limit=ks_limit))
    n_polys = len(polys)
    if n_polys == 0:
        print(f"  No polytopes at h11={h11}")
        return

    print_header('scan' + (' (resume)' if resume else ''),
                 str(h11), n_polys, workers)

    # ── Resume path: skip straight to T2 using DB state ──
    if resume and db:
        need_t2 = db.query(
            "SELECT poly_idx, COALESCE(n_clean_est, 0) as n_clean_est, "
            "COALESCE(max_h0, 0) as max_h0 "
            "FROM polytopes WHERE h11=? AND tier_reached='T1' "
            "AND status='pass' ORDER BY n_clean_est DESC, max_h0 DESC",
            (h11,)
        )
        if not need_t2:
            print(f"  Resume: no T1 polytopes pending T2 at h11={h11}")
        else:
            if top_n > 0:
                need_t2 = need_t2[:top_n]
            print(f"  Resume: {len(need_t2)} polytopes need T2")
            _run_t2_parallel(polys, need_t2, h11, workers, db)
            clear_poly_cache()
            return

    # ── T0 ──
    print(f"  T0: geometry + intersection algebra ({n_polys:,} polytopes)")
    t0_start = time.time()
    t0_args = [(np.array(p.points(), dtype=int).tolist(), idx, h11)
               for idx, p in enumerate(polys)]

    with mp.Pool(workers) as pool:
        t0_results = pool.map(_t0_worker, t0_args, chunksize=50)

    t0_pass_list = [r for r in t0_results if r['status'] == 'pass']
    t0_elapsed = time.time() - t0_start
    print(f"    {len(t0_pass_list):,}/{n_polys:,} pass "
          f"({100*len(t0_pass_list)/n_polys:.1f}%), "
          f"{n_polys/t0_elapsed:.0f} poly/s, {t0_elapsed:.1f}s")

    if db:
        db_upsert_t0(db, h11, t0_results)
        db.log_scan(h11, 'T0', mode='scan',
                   machine=socket.gethostname(),
                   script=SOURCE_FILE,
                   n_polytopes=n_polys,
                   n_pass=len(t0_pass_list),
                   elapsed_s=t0_elapsed)

    if not t0_pass_list:
        print(f"  No polytopes passed T0.")
        return

    # ── T1 (gap-priority scheduling) ──
    t0_pass_sorted = sorted(t0_pass_list,
                            key=lambda r: r.get('gap', 0), reverse=True)
    gap_hi = sum(1 for r in t0_pass_sorted if r.get('gap', 0) >= 5)
    gap_lo = sum(1 for r in t0_pass_sorted if r.get('gap', 0) <= 2)
    print(f"\n  T1: bundle screening ({len(t0_pass_sorted):,} polytopes, "
          f"gap>=5: {gap_hi}, gap<=2: {gap_lo})")
    t1_start = time.time()
    t1_args = [(np.array(polys[r['poly_idx']].points(), dtype=int).tolist(),
                r['poly_idx'], h11)
               for r in t0_pass_sorted]

    t1_results = []
    n_t1_pass = 0
    n_t1_timeout = 0
    n_t1_done = 0
    n_total = len(t1_args)
    with mp.Pool(workers) as pool:
        for t1r in pool.imap_unordered(_t1_worker, t1_args, chunksize=1):
            t1_results.append(t1r)
            n_t1_done += 1
            if t1r.get('status') == 'pass':
                n_t1_pass += 1
            elif t1r.get('status') == 'timeout':
                n_t1_timeout += 1
            if n_t1_done == 1 or n_t1_done % 20 == 0 or n_t1_done == n_total:
                elapsed = time.time() - t1_start
                rate = n_t1_done / max(elapsed, 0.1)
                eta = (n_total - n_t1_done) / max(rate, 0.001)
                print(f"    T1 progress: {n_t1_done}/{n_total} "
                      f"({n_t1_pass} pass, {n_t1_timeout} timeout) "
                      f"{elapsed:.0f}s elapsed, ETA {eta:.0f}s", flush=True)

    t1_pass_list = [r for r in t1_results
                    if r['status'] == 'pass' or
                    (r['status'] == 'timeout' and
                     (r.get('n_clean_est', 0) > 0 or r.get('max_h0', 0) >= H0_MIN_T1))]
    t1_elapsed = time.time() - t1_start
    n_t1_timeouts = sum(1 for r in t1_results if r.get('status') == 'timeout')
    print(f"    {len(t1_pass_list):,}/{len(t0_pass_sorted):,} pass "
          f"({100*len(t1_pass_list)/max(1,len(t0_pass_sorted)):.1f}%), "
          f"{n_t1_timeouts} timeout, {t1_elapsed:.1f}s")

    if db:
        db_upsert_t1(db, h11, t1_results)
        db.log_scan(h11, 'T1', mode='scan',
                   machine=socket.gethostname(),
                   script=SOURCE_FILE,
                   n_polytopes=len(t0_pass_sorted),
                   n_pass=len(t1_pass_list),
                   elapsed_s=t1_elapsed)

    if not t1_pass_list:
        print(f"  No polytopes passed T1.")
        return

    t1_ranked = sorted(t1_pass_list,
                      key=lambda r: (r.get('n_clean_est', 0),
                                    r.get('max_h0', 0)),
                      reverse=True)
    if top_n > 0:
        t1_ranked = t1_ranked[:top_n]

    # ── T2 (parallel) ──
    _run_t2_parallel(polys, t1_ranked, h11, workers, db)

    total_elapsed = time.time() - t_start
    print(f"\n  {'='*56}")
    print(f"  Total: {fmt_time(total_elapsed)}  ({n_polys:,} polytopes)")
    print(f"  {'='*56}")

    clear_poly_cache()


def _run_t2_parallel(polys, ranked_list, h11, workers, db):
    """Run T2 in parallel with progress reporting.

    Includes v5.2 MONOTONIC_MAX post-upsert rescore: after all T2 upserts,
    reads merged DB rows and recomputes scores to prevent drift when
    monotonic columns keep MAX but sm_score was overwritten.
    """
    n_todo = len(ranked_list)
    print(f"\n  T2: deep physics ({n_todo:,} polytopes, {workers} workers)")
    t2_start = time.time()

    t2_args = [(np.array(polys[r['poly_idx']].points(), dtype=int).tolist(),
                r['poly_idx'], h11)
               for r in ranked_list]

    t2_results = {}
    n_with_clean = 0

    with mp.Pool(workers) as pool:
        for i, t2r in enumerate(pool.imap_unordered(_t2_worker, t2_args)):
            if t2r.get('status') == 'ok':
                idx = t2r['poly_idx']
                t2_results[idx] = t2r
                if t2r.get('n_clean', 0) > 0:
                    n_with_clean += 1
                if db:
                    db_upsert_t2(db, t2r, auto_commit=False)

            if (i + 1) % 10 == 0 or i == n_todo - 1:
                if db:
                    db.commit()
                print_progress(i + 1, n_todo, n_with_clean,
                              time.time() - t2_start, "with clean")

    print()  # newline after progress bar
    t2_elapsed = time.time() - t2_start

    print(f"    {len(t2_results):,} analyzed, "
          f"{n_with_clean} with clean bundles, "
          f"{t2_elapsed:.1f}s")

    # ── Post-upsert rescore (v5.2 MONOTONIC_MAX fix) ──
    # MONOTONIC_MAX columns (n_clean, yukawa_rank, etc.) keep the MAX of
    # old + new values, but sm_score is always overwritten. Recompute
    # scores from the merged DB rows so they reflect MAX-preserved metrics.
    if db and t2_results:
        n_rescored = 0
        for idx in t2_results:
            row = db.get_polytope(h11, idx)
            if row:
                new_score = compute_sm_score(dict(row))
                old_score = row['sm_score'] or 0
                if new_score != old_score:
                    db.upsert_polytope(h11, idx,
                                       sm_score=new_score,
                                       auto_commit=False)
                    n_rescored += 1
        if n_rescored > 0:
            db.commit()
            print(f"    Rescored {n_rescored} polytopes "
                  f"(MONOTONIC_MAX merge fix)")

    # Score summary (use DB-corrected scores)
    if db and t2_results:
        scores = []
        for idx in t2_results:
            row = db.get_polytope(h11, idx)
            if row and row['sm_score']:
                scores.append(row['sm_score'])
        scores.sort(reverse=True)
    else:
        scores = sorted([r['sm_score'] for r in t2_results.values()
                        if r.get('sm_score')], reverse=True)
    if scores:
        print(f"    SM scores: top={scores[0]}, "
              f"median={scores[len(scores)//2]}, "
              f"mean={sum(scores)/len(scores):.1f}")

    if db:
        db.log_scan(h11, 'T2', mode='scan',
                   machine=socket.gethostname(),
                   script=SOURCE_FILE,
                   n_polytopes=n_todo,
                   n_pass=n_with_clean,
                   elapsed_s=t2_elapsed,
                   thresholds={'EFF_MAX': EFF_MAX, 'GAP_MIN': GAP_MIN,
                              'H0_MIN_T1': H0_MIN_T1, 'AUT_MAX': AUT_MAX,
                              'YUK_MIN_FRAC': YUK_MIN_FRAC,
                              'T1_WALL_SEC': T1_WALL_SEC,
                              'T1_BUNDLE_CAP': T1_BUNDLE_CAP},
                   notes=f"scan T2. top_score={scores[0] if scores else 0}")


# ══════════════════════════════════════════════════════════════════
#  Deep mode: T3 on top candidates
# ══════════════════════════════════════════════════════════════════

def run_deep(top_n=50, db=None, ks_limit=1000):
    """Run T3 (full phenomenology + fiber + tri stability) on top candidates.

    Inherited from v5: runs compute_tri_stability() on each candidate.
    """
    candidates = db.leaderboard(limit=top_n, min_score=1)
    if not candidates:
        print("  No candidates with SM score > 0")
        return

    import cytools as ct
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    print(f"\n  T3: deep analysis on {len(candidates)} top candidates")

    for i, cand in enumerate(candidates):
        h11 = cand['h11']
        idx = cand['poly_idx']
        old_score = cand.get('sm_score', 0)

        print(f"\n    [{i+1}/{len(candidates)}] h{h11}/P{idx} "
              f"(score={old_score})")

        try:
            fetch_limit = max(ks_limit, idx + 1)
            polys = list(ct.fetch_polytopes(h11=h11, h21=h11+3, limit=fetch_limit))
            p = polys[idx]

            # Fiber analysis
            fiber_result = _run_fiber_analysis(p, idx, h11)
            fibs = fiber_result.get('fibrations', [])
            has_sm = any(f.get('contains_SM') for f in fibs)
            has_gut = any(f.get('has_SU5_GUT') for f in fibs)
            best_gauge = ''
            if fibs:
                best = max(fibs, key=lambda f: f.get('gauge_rank', 0), default={})
                best_gauge = best.get('gauge_algebra', '')
            print(f"      Fibers: {len(fibs)} found, "
                  f"SM={'yes' if has_sm else 'no'}, "
                  f"GUT={'yes' if has_gut else 'no'}")
            if best_gauge:
                print(f"      Best gauge: {best_gauge}")

            # Triangulation stability (v4 property-level check)
            tri_info = check_triangulation_stability(p, n_samples=50)
            print(f"      Triangulations: {tri_info['n_triangulations']} tested, "
                  f"stable={tri_info['props_stable']}")

            # v5: c₂ / κ hash stability
            tri_stab = compute_tri_stability(p, n_samples=20)
            print(f"      Tri stability: {tri_stab['tri_n_tested']} tested, "
                  f"c2_stable={tri_stab['tri_c2_stable_frac']:.2f}, "
                  f"kappa_stable={tri_stab['tri_kappa_stable_frac']:.2f}")

            # Instanton divisor
            tri = p.triangulate()
            cy = tri.get_cy()
            h11_eff = len(cy.divisor_basis())
            intnums = dict(cy.intersection_numbers(in_basis=True))
            c2 = np.array(cy.second_chern_class(in_basis=True), dtype=float)
            has_inst = check_instanton_divisor(intnums, c2, h11_eff)
            print(f"      Instanton divisor: {'yes' if has_inst else 'no'}")

            # Update DB
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
                source_file=SOURCE_FILE,
            )

            # Rescore with fiber data now available
            row = db.query("SELECT * FROM polytopes WHERE h11=? AND poly_idx=?",
                          (h11, idx))
            if row:
                new_score = compute_sm_score(row[0])
                if new_score != old_score:
                    db.upsert_polytope(h11, idx, sm_score=new_score)
                    print(f"      Score: {old_score} -> {new_score}")

            for fib in fibs:
                db.add_fibration(h11, idx, **fib)

        except Exception as e:
            print(f"      Error: {e}")

    clear_poly_cache()


# ══════════════════════════════════════════════════════════════════
#  Fiber pass (gauge algebra classification on top-N DB candidates)
# ══════════════════════════════════════════════════════════════════

def run_fiber_pass(top_n=100, workers=4, db=None, ks_limit=1000,
                  unclassified_only=True):
    """Run _fiber_worker on top-N scored polytopes, update DB with gauge algebra.

    Args:
        top_n: Number of top-scored candidates to classify.
        workers: Number of parallel workers.
        db: LandscapeDB instance.
        ks_limit: KS fetch limit per query (must be > poly_idx).
        unclassified_only: If True, skip polytopes that already have n_fibers set.
    """
    import cytools as ct

    # Query candidates from DB
    if unclassified_only:
        sql = """SELECT h11, poly_idx, sm_score, n_k3_fib, n_fibers
                 FROM polytopes
                 WHERE sm_score IS NOT NULL AND sm_score > 0
                   AND (n_fibers IS NULL OR n_fibers = 0)
                 ORDER BY sm_score DESC
                 LIMIT ?"""
    else:
        sql = """SELECT h11, poly_idx, sm_score, n_k3_fib, n_fibers
                 FROM polytopes
                 WHERE sm_score IS NOT NULL AND sm_score > 0
                 ORDER BY sm_score DESC
                 LIMIT ?"""

    candidates = db.query(sql, (top_n,))
    if not candidates:
        print("  No candidates found.")
        return

    print(f"\n{'='*68}")
    print(f"  FIBER PASS — gauge algebra  |  {len(candidates)} candidates  |  "
          f"{workers} workers")
    label = 'unclassified only' if unclassified_only else 'all'
    print(f"  top_n={top_n}  ({label})")
    print(f"{'='*68}")

    # Group by h11 to minimise KS fetches
    from collections import defaultdict
    by_h11 = defaultdict(list)
    for row in candidates:
        by_h11[row['h11']].append(row)

    t_start = time.time()
    total_done = 0
    total_sm = 0
    total_gut = 0
    errors = 0

    for h11, rows in sorted(by_h11.items()):
        max_idx = max(r['poly_idx'] for r in rows)
        fetch_limit = max(ks_limit, max_idx + 1)
        print(f"\n  h{h11}: {len(rows)} candidates (fetching {fetch_limit} polytopes)")

        try:
            polys = list(ct.fetch_polytopes(h11=h11, h21=h11+3,
                                             limit=fetch_limit))
        except Exception as e:
            print(f"    KS fetch error: {e}")
            errors += len(rows)
            continue

        # Build worker args: (vertices, poly_idx, h11)
        worker_args = []
        for row in rows:
            idx = row['poly_idx']
            if idx >= len(polys):
                print(f"    idx={idx} out of range (fetched {len(polys)}), skip")
                errors += 1
                continue
            verts = polys[idx].vertices().tolist()
            worker_args.append((verts, idx, h11))

        if not worker_args:
            continue

        # Run fiber workers in parallel
        with mp.Pool(processes=min(workers, len(worker_args))) as pool:
            results = pool.map(_fiber_worker, worker_args)

        for fiber_result in results:
            idx = fiber_result.get('poly_idx')
            if fiber_result.get('error'):
                print(f"    P{idx}: error — {fiber_result['error'][:80]}")
                errors += 1
                continue

            fibs = fiber_result.get('fibrations', [])
            has_sm = any(f.get('contains_SM') for f in fibs)
            has_gut = any(f.get('has_SU5_GUT') for f in fibs)
            best_gauge = ''
            if fibs:
                best = max(fibs, key=lambda f: f.get('gauge_rank', 0))
                best_gauge = best.get('gauge_algebra', '')

            db_upsert_fiber(db, h11, idx, fiber_result)
            total_done += 1
            if has_sm:
                total_sm += 1
            if has_gut:
                total_gut += 1
            sm_tag = ' SM' if has_sm else ''
            gut_tag = ' GUT' if has_gut else ''
            gauge_tag = f' [{best_gauge}]' if best_gauge else ''
            print(f"    P{idx}: {len(fibs)} fibers{sm_tag}{gut_tag}{gauge_tag}")

        db.conn.commit()

    elapsed = time.time() - t_start
    print(f"\n  {'='*60}")
    print(f"  Done: {total_done}/{len(candidates)} classified, "
          f"{total_sm} SM, {total_gut} GUT, {errors} errors, "
          f"{elapsed:.0f}s")
    print(f"  {'='*60}")


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline v6: physics-driven CY landscape scan')

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--ladder', action='store_true',
                     help='T0 only, fast landscape mapping')
    mode.add_argument('--scan', action='store_true',
                     help='Full T0->T2 for specified h11 values')
    mode.add_argument('--deep', action='store_true',
                     help='T3 on top candidates (fiber + stability + rescore)')
    mode.add_argument('--rescore', action='store_true',
                     help='Recompute SM scores from existing T2 data (v6 weights)')
    mode.add_argument('--fiber', action='store_true',
                     help='Run Kodaira fiber/gauge-algebra classification on top-N '
                          'scored polytopes. Populates has_SM, has_GUT, best_gauge, '
                          'n_fibers. Use --top N to control candidate count.')

    parser.add_argument('--h11', type=int, nargs='+',
                       help='h11 values (1 for scan, 2 for ladder range)')
    parser.add_argument('-w', '--workers', type=int, default=4,
                       help='Number of parallel workers')
    parser.add_argument('--top', type=int, default=500,
                       help='Max polytopes for T2 (scan) or T3 (deep)')
    parser.add_argument('--db', type=str, default=None,
                       help='Database path (default: v4/cy_landscape_v4.db)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from checkpoint')
    parser.add_argument('--limit', type=int, default=1000,
                       help='KS fetch limit per (h11,h21) query (default: 1000). '
                            'The KS database has 10K-50K+ polytopes per h11 at chi=-6. '
                            'Use --limit 5000 to scan 5x deeper.')
    parser.add_argument('--gap-min', type=int, default=None,
                       help='Override GAP_MIN threshold (default: 2). '
                            'Use --gap-min 0 to include favorable (gap=0) polytopes.')
    parser.add_argument('--eff-max', type=int, default=None,
                       help='Override EFF_MAX threshold (default: 22). '
                            'Use --eff-max 30 for gap=0 probes at high h11.')

    args = parser.parse_args()

    # Apply CLI overrides to globals
    global GAP_MIN, EFF_MAX
    if args.gap_min is not None:
        GAP_MIN = args.gap_min
        print(f"  GAP_MIN overridden to {GAP_MIN}")
    if args.eff_max is not None:
        EFF_MAX = args.eff_max
        print(f"  EFF_MAX overridden to {EFF_MAX}")

    # Open DB
    db = LandscapeDB(args.db) if args.db else LandscapeDB()
    print(f"  DB: {db}")

    try:
        if args.rescore:
            run_rescore(db)

        elif args.ladder:
            if not args.h11 or len(args.h11) < 2:
                parser.error("--ladder requires --h11 START END")
            run_ladder(args.h11[0], args.h11[1], workers=args.workers,
                      db=db, ks_limit=args.limit)

        elif args.scan:
            if not args.h11:
                parser.error("--scan requires --h11")
            if len(args.h11) == 2 and args.h11[1] > args.h11[0]:
                h11_list = list(range(args.h11[0], args.h11[1] + 1))
            else:
                h11_list = args.h11
            for h11 in h11_list:
                run_scan(h11, workers=args.workers, top_n=args.top,
                        db=db, resume=args.resume, ks_limit=args.limit)

        elif args.deep:
            run_deep(top_n=args.top, db=db, ks_limit=args.limit)

        elif args.fiber:
            run_fiber_pass(top_n=args.top, workers=args.workers,
                           db=db, ks_limit=args.limit)

    finally:
        db.close()


if __name__ == '__main__':
    main()
