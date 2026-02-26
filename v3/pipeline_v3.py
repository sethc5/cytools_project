#!/usr/bin/env python3
"""
pipeline_v3.py — Physics-driven scan pipeline.

4-tier architecture with continuous scoring:
  T0   (0.1s)   Geometry + intersection algebra    kills ~85%
  T1   (0.5s)   Bundle screening                   kills ~70%
  T2   (3-30s)  Deep physics + scoring             top ~1K
  T3   (30s+)   Full phenomenology + fibers        top ~50

T05 was merged into T0 (intersection algebra data collected but its
Yukawa-density filter never killed a single polytope in h11=13-18 scans).
Fiber analysis moved from T2 to T3 (91% of polytopes have SM gauge
groups, so it wastes compute during scan — verify on T3 shortlist only).

Execution modes:
  --ladder --h11 13 30     T0 only, fast landscape mapping
  --scan   --h11 19        Full T0→T2 for one h11
  --deep   --top 50        T3 on top candidates (includes fiber analysis)
  --rescore                Recompute SM scores from existing data

All results written to cy_landscape_v3.db in real time.
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

# ── Local imports ────────────────────────────────────────────────
import sys
import os
_v3_dir = os.path.dirname(os.path.abspath(__file__))
if _v3_dir not in sys.path:
    sys.path.insert(0, _v3_dir)

from db_utils_v3 import LandscapeDB
from cy_compute_v3 import (
    # v2 re-exports
    find_chi3_bundles,
    compute_h0_koszul, precompute_vertex_data,
    basis_to_toric, compute_D3, count_fibrations,
    clear_poly_cache,
    # v3 new
    analyze_intersection_algebra,
    compute_lvs_score,
    compute_yukawa_texture,
    analyze_mori_cone,
    classify_divisors,
    compute_sm_score,
    check_triangulation_stability,
    check_instanton_divisor,
)


# ══════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════

RESULTS_DIR = Path(_v3_dir) / "results"
RESULTS_DIR.mkdir(exist_ok=True)

RECEIPTS_DIR = Path(_v3_dir) / "receipts"
RECEIPTS_DIR.mkdir(exist_ok=True)

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
RED = "\033[91m"

# ── Thresholds (carried from v2, data-driven) ──
EFF_MAX = 20        # Skip h11_eff > 20
GAP_MIN = 2         # Min gap for priority track
H0_MIN_T1 = 5       # Bundle screening threshold
AUT_MAX = 4         # Skip |Aut| > 4
YUK_MIN_FRAC = 0.5  # Skip if yukawa_rank < h11_eff * this

# ── Worker timeout ──
T1_BUDGET_SEC = 2.0   # Time budget for adaptive T1 clean counting


# ══════════════════════════════════════════════════════════════════
#  T0: Geometry + Intersection Algebra (~0.1s/poly)
#  Merged from T0+T05: intersection data is collected but the
#  Yukawa-density filter was removed (killed 0% in h11=13-18).
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
        # (cheap: ~0.05s extra, eliminates entire T05 pass)
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


# T05 worker removed — intersection algebra merged into T0.
# The T05 Yukawa-density filter killed 0% of polytopes across h11=13-18
# (yukawa_rank/h11_eff ratio always ≥ 2.0), so it was pure overhead.


# ══════════════════════════════════════════════════════════════════
#  T1: Bundle Screening (~0.5s/poly)
# ══════════════════════════════════════════════════════════════════

def _t1_worker(args):
    """Bundle screening with adaptive depth.

    Finds χ=±3 bundles, computes h⁰ with early-exit, then
    counts clean bundles within a time budget.
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

        bundles = find_chi3_bundles(intnums, c2, h11_eff, mc, mnz)
        n_chi3 = len(bundles)

        if not bundles:
            return {'poly_idx': poly_idx, 'status': 'skip',
                    'max_h0': 0, 'n_chi3': 0}

        _precomp = precompute_vertex_data(pts, ray_indices)
        max_h0 = 0
        h0_ge3 = 0
        n_clean_est = 0
        first_clean_at = -1
        t_budget_start = time.time()

        for idx, (D_basis, chi_val) in enumerate(bundles):
            # Time budget check (after first clean hit)
            if n_clean_est > 0 and (time.time() - t_budget_start) > T1_BUDGET_SEC:
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
            if h0 > max_h0:
                max_h0 = h0
            if h0 >= 3:
                h0_ge3 += 1

            # Clean check: h⁰ = 3 AND h³ = 0
            if h0 == 3 and abs(abs(chi_val) - 3.0) < 0.01:
                # For chi > 0: h0(D)=3, need h3(D)=h0(-D)=0
                # For chi < 0: h0(-D)=3, need h3(-D)=h0(D)=0
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

        return {
            'poly_idx': poly_idx,
            'status': 'pass' if passed else 'skip',
            'max_h0': max_h0,
            'h0_ge3': h0_ge3,
            'n_chi3': n_chi3,
            'n_clean_est': n_clean_est,
            'first_clean_at': first_clean_at,
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

    Returns a rich dict with all T2 fields + sm_score.
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
        best_clean_D = None  # Track best clean bundle for Yukawa

        for D_basis, chi_val in bundles:
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
                # For chi > 0: h0(D)=3, need h3(D)=h0(-D)=0
                # For chi < 0: h0(-D)=3, need h3(-D)=h0(D)=0
                if chi_val > 0:
                    D_dual = basis_to_toric(-D_basis, div_basis, n_toric)
                else:
                    D_dual = D_toric
                h3 = compute_h0_koszul(pts, ray_indices, D_dual,
                                       _precomp=_precomp)
                if h3 == 0:
                    n_clean += 1
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

        # ── SM Score ──
        result['chi_over_24'] = chi / 24.0
        # c2_all_positive needed for scoring; full T05 analysis already in DB
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
        # Import fiber_analysis from v2
        _v2_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'v2')
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
            'source_file': 'pipeline_v3.py',
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
            'source_file': 'pipeline_v3.py',
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
        # T05 fields (c2_all_positive, chi_over_24 re-asserted; rest preserved from T05)
        c2_all_positive=r.get('c2_all_positive'),
        chi_over_24=r.get('chi_over_24'),
        # Score
        sm_score=r.get('sm_score'),
        # Meta
        tier_reached='T2',
        source_file='pipeline_v3.py',
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
    print(f"\n{'═'*72}")
    print(f"  {BOLD}PIPELINE v3 (PHYSICS-DRIVEN){RESET}  "
          f"mode={mode}  |  h¹¹={h11_range}  |  {n_workers} workers")
    print(f"  {DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"  {DIM}EFF_MAX={EFF_MAX}  GAP_MIN={GAP_MIN}  "
          f"H0_MIN={H0_MIN_T1}  AUT_MAX={AUT_MAX}{RESET}")
    if n_polys:
        print(f"  {DIM}{n_polys:,} polytopes{RESET}")
    print(f"{'═'*72}\n")


def print_progress(done, total, n_pass, elapsed, label="pass"):
    rate = done / elapsed if elapsed > 0 else 0
    eta = (total - done) / rate if rate > 0 else 0
    pct = 100 * done / total if total > 0 else 0
    bar_w = 30
    filled = int(bar_w * done / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_w - filled)
    print(f"\r    {bar} {pct:5.1f}%  "
          f"{done:,}/{total:,}  {n_pass} {label}  "
          f"{rate:.1f}/s  ETA {fmt_time(eta)}  ", end='', flush=True)


# ══════════════════════════════════════════════════════════════════
#  Rescore mode
# ══════════════════════════════════════════════════════════════════

def run_rescore(db):
    """Recompute SM scores for all polytopes with T2 data."""
    rows = db.query(
        "SELECT * FROM polytopes WHERE tier_reached IN ('T2', 'T3')")
    print(f"  Rescoring {len(rows)} polytopes...")
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
#  Ladder mode: T0 + T05 only
# ══════════════════════════════════════════════════════════════════

def run_ladder(h11_start, h11_end, workers=4, db=None):
    """Run T0+T05 across h11 range. Fast landscape mapping."""
    import cytools as ct
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    for h11 in range(h11_start, h11_end + 1):
        h21 = h11 + 3
        t_h11_start = time.time()

        print(f"\n  {'─'*56}")
        print(f"  {BOLD}h¹¹ = {h11}{RESET}")

        # Fetch polytopes
        try:
            polys = list(ct.fetch_polytopes(h11=h11, h21=h21))
        except Exception as e:
            print(f"    {RED}Fetch failed: {e}{RESET}")
            continue

        n_polys = len(polys)
        if n_polys == 0:
            print(f"    No polytopes at h¹¹={h11}, h²¹={h21}")
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
                       script='pipeline_v3.py',
                       n_polytopes=n_polys, n_pass=len(t0_pass),
                       elapsed_s=t0_elapsed)

        if not t0_pass:
            continue

        # Summary (intersection algebra data already in T0 results)
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

def run_scan(h11, workers=4, top_n=500, db=None, resume=False):
    """Full T0→T2 scan for a single h¹¹ value.

    If resume=True and db is available, skips T0→T1 and picks up T2
    from polytopes that passed T1 but haven't reached T2 yet.
    """
    import cytools as ct
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    h21 = h11 + 3
    t_start = time.time()

    # Fetch
    polys = list(ct.fetch_polytopes(h11=h11, h21=h21))
    n_polys = len(polys)
    if n_polys == 0:
        print(f"  No polytopes at h¹¹={h11}")
        return

    print_header('scan' + (' (resume)' if resume else ''),
                 str(h11), n_polys, workers)

    # ── Resume path: skip straight to T2 using DB state ──
    if resume and db:
        # Find polytopes at T1 that haven't reached T2
        need_t2 = db.query(
            "SELECT poly_idx, COALESCE(n_clean_est, 0) as n_clean_est, "
            "COALESCE(max_h0, 0) as max_h0 "
            "FROM polytopes WHERE h11=? AND tier_reached='T1' "
            "AND status='pass' ORDER BY n_clean_est DESC, max_h0 DESC",
            (h11,)
        )
        if not need_t2:
            print(f"  Resume: no T1 polytopes pending T2 at h¹¹={h11}")
            # Fall through to check if full re-scan needed
        else:
            if top_n > 0:
                need_t2 = need_t2[:top_n]
            print(f"  Resume: {len(need_t2)} polytopes need T2")
            _run_t2_parallel(polys, need_t2, h11, workers, db)
            clear_poly_cache()
            return

    # ── T0 (geometry + intersection algebra, merged from T0+T05) ──
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
                   script='pipeline_v3.py',
                   n_polytopes=n_polys,
                   n_pass=len(t0_pass_list),
                   elapsed_s=t0_elapsed)

    if not t0_pass_list:
        print(f"  No polytopes passed T0.")
        return

    # ── T1 (T05 merged into T0 — no separate pass needed) ──
    print(f"\n  T1: bundle screening ({len(t0_pass_list):,} polytopes)")
    t1_start = time.time()
    t1_args = [(np.array(polys[r['poly_idx']].points(), dtype=int).tolist(),
                r['poly_idx'], h11)
               for r in t0_pass_list]

    with mp.Pool(workers) as pool:
        t1_results = pool.map(_t1_worker, t1_args, chunksize=10)

    t1_pass_list = [r for r in t1_results if r['status'] == 'pass']
    t1_elapsed = time.time() - t1_start
    print(f"    {len(t1_pass_list):,}/{len(t0_pass_list):,} pass "
          f"({100*len(t1_pass_list)/max(1,len(t0_pass_list)):.1f}%), "
          f"{t1_elapsed:.1f}s")

    if db:
        db_upsert_t1(db, h11, t1_results)
        db.log_scan(h11, 'T1', mode='scan',
                   machine=socket.gethostname(),
                   script='pipeline_v3.py',
                   n_polytopes=len(t0_pass_list),
                   n_pass=len(t1_pass_list),
                   elapsed_s=t1_elapsed)

    if not t1_pass_list:
        print(f"  No polytopes passed T1.")
        return

    # Rank by estimated clean count (desc), then max_h0
    t1_ranked = sorted(t1_pass_list,
                      key=lambda r: (r.get('n_clean_est', 0),
                                    r.get('max_h0', 0)),
                      reverse=True)
    if top_n > 0:
        t1_ranked = t1_ranked[:top_n]

    # ── T2 (parallel) ──
    _run_t2_parallel(polys, t1_ranked, h11, workers, db)

    total_elapsed = time.time() - t_start
    print(f"\n  {'═'*56}")
    print(f"  Total: {fmt_time(total_elapsed)}  ({n_polys:,} polytopes)")
    print(f"  {'═'*56}")

    clear_poly_cache()


def _run_t2_parallel(polys, ranked_list, h11, workers, db):
    """Run T2 in parallel with progress reporting + fiber analysis.

    Args:
        polys: full list of CYTools polytope objects for this h11
        ranked_list: list of dicts with 'poly_idx' key, ordered by priority
        h11: the h11 value
        workers: number of parallel workers
        db: LandscapeDB instance (or None)
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

            # Batch commit + progress every 10 or at end
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

    # Score summary
    scores = sorted([r['sm_score'] for r in t2_results.values()
                    if r.get('sm_score')], reverse=True)
    if scores:
        print(f"    SM scores: top={scores[0]}, "
              f"median={scores[len(scores)//2]}, "
              f"mean={sum(scores)/len(scores):.1f}")

    if db:
        db.log_scan(h11, 'T2', mode='scan',
                   machine=socket.gethostname(),
                   script='pipeline_v3.py',
                   n_polytopes=n_todo,
                   n_pass=n_with_clean,
                   elapsed_s=t2_elapsed,
                   thresholds={'EFF_MAX': EFF_MAX, 'GAP_MIN': GAP_MIN,
                              'H0_MIN_T1': H0_MIN_T1, 'AUT_MAX': AUT_MAX,
                              'YUK_MIN_FRAC': YUK_MIN_FRAC},
                   notes=f"scan T2. top_score={scores[0] if scores else 0}")

    # Fiber analysis deferred to T3 (--deep).
    # 91% of polytopes have SM gauge groups, so running fibers during scan
    # wastes compute on confirming the obvious. Verify on T3 shortlist only.


# ══════════════════════════════════════════════════════════════════
#  Deep mode: T3 on top candidates (includes fiber analysis)
# ══════════════════════════════════════════════════════════════════

def run_deep(top_n=50, db=None):
    """Run T3 (full phenomenology + fiber analysis) on top candidates."""
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
            polys = list(ct.fetch_polytopes(h11=h11, h21=h11+3))
            p = polys[idx]

            # Fiber analysis (moved here from T2 scan — saves compute)
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

            # Triangulation stability
            tri_info = check_triangulation_stability(p, n_samples=50)
            print(f"      Triangulations: {tri_info['n_triangulations']} tested, "
                  f"stable={tri_info['props_stable']}")

            # Instanton divisor
            tri = p.triangulate()
            cy = tri.get_cy()
            h11_eff = len(cy.divisor_basis())
            intnums = dict(cy.intersection_numbers(in_basis=True))
            c2 = np.array(cy.second_chern_class(in_basis=True), dtype=float)
            has_inst = check_instanton_divisor(intnums, c2, h11_eff)
            print(f"      Instanton divisor: {'yes' if has_inst else 'no'}")

            # Update DB (fiber + T3 data)
            db.upsert_polytope(h11, idx,
                n_fibers=len(fibs),
                has_SM=has_sm,
                has_GUT=has_gut,
                best_gauge=best_gauge,
                n_triangulations=tri_info['n_triangulations'],
                props_stable=tri_info['props_stable'],
                has_instanton_div=has_inst,
                tier_reached='T3',
            )

            # Rescore with fiber data now available
            row = db.query("SELECT * FROM polytopes WHERE h11=? AND poly_idx=?",
                          (h11, idx))
            if row:
                new_score = compute_sm_score(row[0])
                if new_score != old_score:
                    db.upsert_polytope(h11, idx, sm_score=new_score)
                    print(f"      Score: {old_score} → {new_score}")

            for fib in fibs:
                db.add_fibration(h11, idx, **fib)

        except Exception as e:
            print(f"      Error: {e}")

    clear_poly_cache()


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Pipeline v3: physics-driven CY landscape scan')

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--ladder', action='store_true',
                     help='T0 only, fast landscape mapping')
    mode.add_argument('--scan', action='store_true',
                     help='Full T0→T2 for specified h11 values')
    mode.add_argument('--deep', action='store_true',
                     help='T3 on top candidates (fiber + stability + rescore)')
    mode.add_argument('--rescore', action='store_true',
                     help='Recompute SM scores from existing T2 data')

    parser.add_argument('--h11', type=int, nargs='+',
                       help='h11 values (1 for scan, 2 for ladder range)')
    parser.add_argument('-w', '--workers', type=int, default=4,
                       help='Number of parallel workers')
    parser.add_argument('--top', type=int, default=500,
                       help='Max polytopes for T2 (scan) or T3 (deep)')
    parser.add_argument('--db', type=str, default=None,
                       help='Database path (default: v3/cy_landscape_v3.db)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from checkpoint')

    args = parser.parse_args()

    # Open DB
    db = LandscapeDB(args.db) if args.db else LandscapeDB()
    print(f"  DB: {db}")

    try:
        if args.rescore:
            run_rescore(db)

        elif args.ladder:
            if not args.h11 or len(args.h11) < 2:
                parser.error("--ladder requires --h11 START END")
            run_ladder(args.h11[0], args.h11[1], workers=args.workers, db=db)

        elif args.scan:
            if not args.h11:
                parser.error("--scan requires --h11")
            for h11 in args.h11:
                run_scan(h11, workers=args.workers, top_n=args.top,
                        db=db, resume=args.resume)

        elif args.deep:
            run_deep(top_n=args.top, db=db)

    finally:
        db.close()


if __name__ == '__main__':
    main()
