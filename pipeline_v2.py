#!/usr/bin/env python3
"""
pipeline_v2.py — Data-driven scan pipeline (Finding 14).

Replaces auto_scan.py with gap-aware triage from 30-query DB analysis.
Key changes:
  1. T0 pre-filter (~0.1s/poly): compute h11_eff, skip eff>=16 / gap<2 / |Aut|>=4
  2. T0.25 gate raised: h0 >= 5 (was >= 3)
  3. Ranking by gap DESC (not max_h0)
  4. Swiss cheese computed but NOT gated on
  5. Results written to cy_landscape.db in real time

Pipeline stages:
  T0   (0.1s):  h11_eff + gap + symmetry pre-filter     kills ~90%
  T0.25 (0.5s): Early-termination h0>=5 check            kills ~70% of remainder
  T1   (3-30s): Full bundle count + divisors + fibrations
  T2   (1-5s):  Kodaira fiber classification + gauge algebra

Expected runtimes:
  h19 (~244K polytopes): ~3-4h
  h20 (~490K polytopes): ~5-6h

Usage:
    python pipeline_v2.py --h11 19                       # default
    python pipeline_v2.py --h11 19 20 -w 14              # multi-h11
    python pipeline_v2.py --h11 18 --resume              # resume from checkpoint
    python pipeline_v2.py --h11 17 --skip-t0             # skip T0 (use DB data)
    python pipeline_v2.py --h11 18 --gap-min 3 --top 500 # custom thresholds
"""

import argparse
import csv
import json
import multiprocessing as mp
import socket
import subprocess
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    from db_utils import LandscapeDB
    HAS_DB = True
except ImportError:
    HAS_DB = False

# ══════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

RECEIPTS_DIR = Path("receipts")
RECEIPTS_DIR.mkdir(exist_ok=True)

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
PASS = f"{GREEN}✓{RESET}"
FAIL = f"{RED}✗{RESET}"
STAR = f"{YELLOW}★{RESET}"

# ── T0 pre-filter thresholds (Finding 14, speed-optimized for large scans) ──
EFF_MAX = 15       # Skip eff > 15 (clean rate drops; favorable h16+ are known-good but slow)
GAP_MIN = 2        # Minimum gap = h11 - h11_eff for priority track
H0_MIN_T025 = 5    # Skip h⁰ < 5 (h⁰=3-4 exist but marginal; speed > completeness)
AUT_MAX = 3        # Skip |Aut| >= 4 (rare clean bundles, expensive to compute)

# Scoring weights (26-point scale, same as auto_scan.py)
SCORE_WEIGHTS = {
    'chi_neg6': 3,
    'three_gen': 3,
    'h0_ge3_exists': 3,
    'clean_bundles': 5,
    'max_h0': 2,
    'swiss_cheese': 3,
    'k3_fibs': 2,
    'ell_fibs': 2,
    'dp_divisors': 1,
    'd3_diversity': 1,
    'h11_tractable': 1,
}
MAX_SCORE = sum(SCORE_WEIGHTS.values())  # 26


# ══════════════════════════════════════════════════════════════════
#  T0: Ultra-fast pre-filter (0.1s/poly)
# ══════════════════════════════════════════════════════════════════

def _t0_worker(args):
    """T0: compute h11_eff, gap, |Aut| — ultra-fast pre-filter.

    Returns:
        dict with h11_eff, gap, aut_order, skip_reason (if any)
    """
    vert, poly_idx, h11_val = args
    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()

        p = Polytope(vert)

        # ── h11_eff (fast: just triangulate + divisor_basis) ──
        tri = p.triangulate()
        cyobj = tri.get_cy()
        div_basis = [int(x) for x in cyobj.divisor_basis()]
        h11_eff = len(div_basis)
        h11 = cyobj.h11()
        h21 = cyobj.h21()
        gap = h11 - h11_eff
        favorable = (h11_eff == h11)

        # ── Automorphism order (cheap for polytopes) ──
        try:
            aut_order = len(p.automorphisms())
        except Exception:
            aut_order = 1  # Assume trivial on failure

        # ── Pre-filter decisions ──
        skip_reason = None
        if h11_eff > EFF_MAX:
            skip_reason = f'eff={h11_eff}>={EFF_MAX+1}'
        elif gap < GAP_MIN and h11_eff >= 15:
            # Low gap + high eff → very unlikely to yield clean bundles
            skip_reason = f'gap={gap}<{GAP_MIN},eff={h11_eff}'
        elif aut_order >= AUT_MAX + 1:
            skip_reason = f'|Aut|={aut_order}>={AUT_MAX+1}'

        return {
            'poly_idx': poly_idx,
            'h11': h11,
            'h21': h21,
            'h11_eff': h11_eff,
            'gap': gap,
            'favorable': favorable,
            'aut_order': aut_order,
            'skip_reason': skip_reason,
            'status': 'skip' if skip_reason else 'pass',
        }

    except Exception as e:
        return {
            'poly_idx': poly_idx,
            'h11': h11_val,
            'status': 'error',
            'skip_reason': f'error: {str(e)[:80]}',
            'h11_eff': None,
            'gap': None,
            'aut_order': None,
        }


# ══════════════════════════════════════════════════════════════════
#  T0.25: Fast h⁰ check with early termination (0.5s/poly)
# ══════════════════════════════════════════════════════════════════

def _t025_worker(args):
    """T0.25: early-termination h⁰≥5 check. Identical to auto_scan Stage 0
    except h⁰ threshold raised to 5."""
    vert, poly_idx, h11_val, h11_eff_known = args
    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()
        from cy_compute import (
            find_chi3_bundles, compute_h0_koszul,
            basis_to_toric, precompute_vertex_data,
        )

        p = Polytope(vert)
        tri = p.triangulate()
        cyobj = tri.get_cy()
        pts = np.array(p.points(), dtype=int)
        n_toric = pts.shape[0]
        ray_indices = list(range(1, n_toric))
        div_basis = [int(x) for x in cyobj.divisor_basis()]
        h11_eff = len(div_basis)
        intnums = dict(cyobj.intersection_numbers(in_basis=True))
        c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

        if not np.all(pts[0] == 0) or len(c2) != h11_eff:
            return {'poly_idx': poly_idx, 'status': 'skip', 'max_h0': 0,
                    'n_chi3': 0}

        # Adaptive search range
        if h11_eff <= 15:
            mc, mnz = 3, 3
        elif h11_eff <= 20:
            mc, mnz = 2, 3
        else:
            mc, mnz = 2, 2

        bundles = find_chi3_bundles(intnums, c2, h11_eff, mc, mnz)
        n_chi3 = len(bundles)

        if not bundles:
            return {'poly_idx': poly_idx, 'status': 'skip', 'max_h0': 0,
                    'n_chi3': 0}

        _precomp = precompute_vertex_data(pts, ray_indices)
        max_h0 = 0

        for D_basis, chi in bundles:
            D_toric = basis_to_toric(D_basis, div_basis, n_toric)
            if chi > 0:
                h0 = compute_h0_koszul(pts, ray_indices, D_toric,
                                       _precomp=_precomp, min_h0=H0_MIN_T025)
            else:
                D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
                h0 = compute_h0_koszul(pts, ray_indices, D_neg,
                                       _precomp=_precomp, min_h0=H0_MIN_T025)
            if h0 > max_h0:
                max_h0 = h0
            if h0 >= H0_MIN_T025:
                break  # Early termination

        return {
            'poly_idx': poly_idx,
            'status': 'pass' if max_h0 >= H0_MIN_T025 else 'skip',
            'max_h0': max_h0,
            'n_chi3': n_chi3,
        }
    except Exception as e:
        return {'poly_idx': poly_idx, 'status': 'error', 'max_h0': 0,
                'n_chi3': 0, 'error': str(e)[:100]}


# ══════════════════════════════════════════════════════════════════
#  T1: Deep analysis (full bundles + divisors + fibrations)
# ══════════════════════════════════════════════════════════════════

def _t1_worker(args):
    """Full deep analysis: clean bundles + divisors + Swiss cheese + fibrations.

    Same as auto_scan._stage1_worker but also computes sym_order.
    """
    vert, poly_idx, h11_val, scan_max_h0, gap = args
    t0 = time.time()

    try:
        from cytools import Polytope
        from cytools.config import enable_experimental_features
        enable_experimental_features()
        from cy_compute import (
            find_chi3_bundles, compute_h0_koszul, compute_D3,
            basis_to_toric, precompute_vertex_data,
            count_fibrations,
        )

        p = Polytope(vert)
        tri = p.triangulate()
        cyobj = tri.get_cy()
        pts = np.array(p.points(), dtype=int)
        n_toric = pts.shape[0]
        ray_indices = list(range(1, n_toric))
        div_basis = [int(x) for x in cyobj.divisor_basis()]
        h11 = cyobj.h11()
        h21 = cyobj.h21()
        h11_eff = len(div_basis)
        is_favorable = (h11_eff == h11)
        intnums = dict(cyobj.intersection_numbers(in_basis=True))
        c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

        if not np.all(pts[0] == 0) or len(c2) != h11_eff:
            return {'poly_idx': poly_idx, 'status': 'data_fail'}

        # ── Bundle search ──
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
            if h0 == 3 and abs(chi_val - 3.0) < 0.01:
                D_neg_toric = basis_to_toric(-D_basis, div_basis, n_toric)
                h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric,
                                       _precomp=_precomp)
                if h3 == 0:
                    n_clean += 1
                    d3 = compute_D3(D_basis, intnums)
                    d3_values.append(d3)

        d3_unique = sorted(set(d3_values))

        # ── Divisor classification ──
        n_dp = 0
        dp_types = []
        n_k3_div = 0
        n_rigid = 0

        for a_idx in range(h11_eff):
            D3 = intnums.get((a_idx, a_idx, a_idx), 0)
            c2D = c2[a_idx]
            if D3 > 0 and c2D > 0:
                dp_n = 9 - D3
                if 0 <= dp_n <= 8:
                    n_dp += 1
                    dp_types.append(dp_n)
                n_rigid += 1
            elif D3 == 0 and c2D > 0:
                n_k3_div += 1
            elif D3 < 0:
                n_rigid += 1

        # ── Swiss cheese (computed, NOT gated on — Finding 14d) ──
        has_swiss = False
        n_swiss = 0
        best_tau = 0.0
        best_ratio = 1.0
        try:
            kc = cyobj.toric_kahler_cone()
            tip = np.array(kc.tip_of_stretched_cone(1.0), dtype=float)
            s = 10  # scale factor
            swiss_hits = []
            for a_small in range(h11_eff):
                t2 = tip * s
                t2[a_small] = tip[a_small]
                V2 = sum(val * t2[i]*t2[j]*t2[k]
                         for (i,j,k), val in intnums.items()) / 6.0
                tau2 = sum(val * t2[j]*t2[k]
                           for (i,j,k), val in intnums.items()
                           if a_small in (i,j,k)) / 2.0
                if V2 > 100 and tau2 > 0:
                    ratio = tau2 / V2**(2.0/3.0)
                    if ratio < 0.1:
                        swiss_hits.append((a_small, tau2, V2, ratio))
            if swiss_hits:
                swiss_hits.sort(key=lambda x: x[3])
                has_swiss = True
                n_swiss = len(swiss_hits)
                best_tau = swiss_hits[0][1]
                best_ratio = swiss_hits[0][3]
        except Exception:
            pass

        # ── Fibrations ──
        n_k3, n_ell = count_fibrations(p)

        # ── Score (26-point) ──
        chi = -6
        score = 0
        score += 3 if chi == -6 else 0
        score += 3 if abs(chi) // 2 == 3 else 0
        score += 3 if h0_ge3 > 0 else 0
        score += 5 if n_clean > 0 else 0
        score += 2 if max_h0 >= 3 else 0
        score += 3 if has_swiss else 0
        score += 2 if n_k3 >= 1 else 0
        score += 2 if n_ell >= 1 else 0
        score += 1 if n_dp >= 1 else 0
        score += 1 if len(d3_unique) >= 10 else 0
        score += 1 if h11 <= 18 else 0

        elapsed = time.time() - t0

        return {
            'poly_idx': poly_idx,
            'status': 'ok',
            'h11': h11,
            'h21': h21,
            'h11_eff': h11_eff,
            'favorable': is_favorable,
            'gap': h11 - h11_eff,
            'n_chi3': n_chi3,
            'max_h0': max_h0,
            'h0_ge3': h0_ge3,
            'n_clean': n_clean,
            'd3_unique': len(d3_unique),
            'd3_values': d3_unique[:20],  # Keep top 20 for DB
            'n_dp': n_dp,
            'dp_types': dp_types,
            'n_k3_div': n_k3_div,
            'n_rigid': n_rigid,
            'has_swiss': has_swiss,
            'n_swiss': n_swiss,
            'best_tau': best_tau,
            'best_ratio': best_ratio,
            'n_k3': n_k3,
            'n_ell': n_ell,
            'score': score,
            'h0_dist': dict(h0_dist),
            'elapsed': elapsed,
        }
    except Exception as e:
        return {'poly_idx': poly_idx, 'status': 'error',
                'error': str(e)[:200]}


# ══════════════════════════════════════════════════════════════════
#  T2: Fiber analysis (Kodaira + gauge algebra)
# ══════════════════════════════════════════════════════════════════

def run_t2(polytope, poly_idx, h11_val):
    """Kodaira fiber classification + gauge algebra. Returns dict."""
    try:
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
    """Batch upsert T0 results into database."""
    rows = []
    for r in results:
        rows.append({
            'h11': h11,
            'poly_idx': r['poly_idx'],
            'h21': r.get('h21', h11 + 3),
            'chi': -6,
            'h11_eff': r.get('h11_eff'),
            'favorable': r.get('favorable'),
            'sym_order': r.get('aut_order'),
            'tier_reached': 'T0',
            'source_file': 'pipeline_v2.py',
            'status': r.get('status'),
            'error': r.get('skip_reason'),
        })
    db.upsert_polytopes_batch(rows)


def db_upsert_t025(db, h11, results):
    """Batch upsert T0.25 results."""
    rows = []
    for r in results:
        rows.append({
            'h11': h11,
            'poly_idx': r['poly_idx'],
            'max_h0': r.get('max_h0'),
            'n_chi3': r.get('n_chi3'),
            'tier_reached': 'T025',
            'source_file': 'pipeline_v2.py',
            'status': r.get('status'),
        })
    db.upsert_polytopes_batch(rows)


def db_upsert_t1(db, r):
    """Upsert a single T1 result (called after each polytope completes)."""
    dp_str = '|'.join(str(d) for d in r.get('dp_types', []))
    d3_str = json.dumps(r.get('d3_values', []))
    h0_str = json.dumps(r.get('h0_dist', {}))
    db.upsert_polytope(r['h11'], r['poly_idx'],
        h21=r.get('h21'),
        chi=-6,
        h11_eff=r.get('h11_eff'),
        favorable=r.get('favorable'),
        n_chi3=r.get('n_chi3'),
        n_computed=r.get('n_chi3'),
        max_h0=r.get('max_h0'),
        n_dp=r.get('n_dp'),
        dp_types=dp_str,
        n_k3_div=r.get('n_k3_div'),
        n_rigid=r.get('n_rigid'),
        has_swiss=r.get('has_swiss'),
        n_swiss=r.get('n_swiss'),
        best_swiss_tau=r.get('best_tau'),
        best_swiss_ratio=r.get('best_ratio'),
        n_bundles_checked=r.get('n_chi3'),
        n_clean=r.get('n_clean'),
        max_h0_t2=r.get('max_h0'),
        h0_ge3=r.get('h0_ge3'),
        n_k3_fib=r.get('n_k3'),
        n_ell_fib=r.get('n_ell'),
        d3_n_distinct=r.get('d3_unique'),
        d3_clean_values=d3_str,
        h0_distribution=h0_str,
        screen_score=r.get('score'),
        tier_reached='T1' if r.get('n_clean', 0) == 0 else 'T2+',
        source_file='pipeline_v2.py',
        status=r.get('status'),
    )


def db_upsert_t2(db, h11, poly_idx, fiber_result):
    """Upsert T2 fiber results."""
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
        tier_reached='T2+',
        source_file='pipeline_v2.py',
    )

    # Add individual fibrations
    for fib in fibs:
        db.add_fibration(h11, poly_idx, **fib)


# ══════════════════════════════════════════════════════════════════
#  Checkpoint management
# ══════════════════════════════════════════════════════════════════

def checkpoint_path(h11):
    return RESULTS_DIR / f"v2_h{h11}.checkpoint.json"


def load_checkpoint(h11):
    path = checkpoint_path(h11)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def save_checkpoint(h11, data):
    path = checkpoint_path(h11)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


# ══════════════════════════════════════════════════════════════════
#  Output
# ══════════════════════════════════════════════════════════════════

def save_results_csv(h11, results):
    """Save final ranked results to CSV."""
    path = RESULTS_DIR / f"v2_h{h11}.csv"
    if not results:
        return path

    fields = ['rank', 'poly_idx', 'score', 'gap', 'h11_eff', 'n_clean',
              'max_h0', 'n_chi3', 'n_dp', 'has_swiss', 'best_tau',
              'n_k3', 'n_ell', 'd3_unique', 'favorable',
              'n_fibers', 'has_SM', 'has_GUT', 'best_gauge', 'elapsed']

    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for i, r in enumerate(results, 1):
            row = {**r, 'rank': i}
            w.writerow(row)
    return path


def _git_hash():
    """Return short git hash or 'unknown'."""
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return 'unknown'


def write_receipt(h11, t_start, elapsed_total,
                  n_polys, t0_results, t025_results,
                  t1_results, t2_results, final,
                  thresholds):
    """Write a self-contained JSON receipt to receipts/.

    This is the primary data transport mechanism — works without a DB.
    merge_receipts.py ingests these into cy_landscape.db on the local machine.
    """
    hostname = socket.gethostname()
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    receipt_name = f"v2_h{h11}_{ts}_{hostname}.json"
    receipt_path = RECEIPTS_DIR / receipt_name

    # ── Tier counts ──
    n_t0_pass = sum(1 for r in t0_results.values() if r['status'] == 'pass')
    n_t025_pass = sum(1 for r in t025_results.values()
                      if r.get('status') == 'pass')

    # ── Collect T1 results (the heavy payload) ──
    t1_rows = []
    for r in t1_results.values():
        if r.get('status') != 'ok':
            continue
        # Serializable copy — strip numpy, keep only JSON-safe types
        row = {}
        for k, v in r.items():
            if isinstance(v, (np.integer, np.int64)):
                row[k] = int(v)
            elif isinstance(v, (np.floating, np.float64)):
                row[k] = float(v)
            elif isinstance(v, np.ndarray):
                row[k] = v.tolist()
            elif isinstance(v, dict):
                row[k] = {str(kk): int(vv) if isinstance(vv, (np.integer,)) else vv
                          for kk, vv in v.items()}
            else:
                row[k] = v
        t1_rows.append(row)

    # ── Collect T2 results ──
    t2_rows = []
    for idx, r in t2_results.items():
        entry = {'poly_idx': idx}
        fibs = r.get('fibrations', [])
        entry['n_fibrations'] = len(fibs)
        entry['has_SM'] = any(f.get('contains_SM') for f in fibs)
        entry['has_GUT'] = any(f.get('has_SU5_GUT') for f in fibs)
        # Keep fibration details for merge
        safe_fibs = []
        for f in fibs:
            sf = {}
            for k, v in f.items():
                if isinstance(v, (np.integer,)):
                    sf[k] = int(v)
                elif isinstance(v, (np.floating,)):
                    sf[k] = float(v)
                elif isinstance(v, np.ndarray):
                    sf[k] = v.tolist()
                else:
                    sf[k] = v
            safe_fibs.append(sf)
        entry['fibrations'] = safe_fibs
        if fibs:
            best = max(fibs, key=lambda f: f.get('gauge_rank', 0), default={})
            entry['best_gauge'] = best.get('gauge_algebra', '')
        t2_rows.append(entry)

    # ── T0 pass list (compact: just idx + key fields) ──
    t0_compact = []
    for r in t0_results.values():
        t0_compact.append({
            'poly_idx': r['poly_idx'],
            'h11': int(r.get('h11', h11)),
            'h21': int(r.get('h21', h11 + 3)),
            'h11_eff': int(r['h11_eff']) if r.get('h11_eff') is not None else None,
            'gap': int(r['gap']) if r.get('gap') is not None else None,
            'favorable': bool(r['favorable']) if r.get('favorable') is not None else None,
            'aut_order': int(r['aut_order']) if r.get('aut_order') is not None else None,
            'status': r['status'],
            'skip_reason': r.get('skip_reason'),
        })

    # ── Build receipt ──
    receipt = {
        'version': 2,
        'receipt_name': receipt_name,
        'h11': h11,
        'machine': hostname,
        'git_hash': _git_hash(),
        'started': datetime.fromtimestamp(t_start).isoformat(),
        'finished': datetime.now().isoformat(),
        'elapsed_seconds': round(elapsed_total, 1),
        'thresholds': thresholds,
        'counts': {
            'fetched': n_polys,
            't0_total': len(t0_results),
            't0_pass': n_t0_pass,
            't025_pass': n_t025_pass,
            't1_analyzed': len(t1_rows),
            't2_analyzed': len(t2_rows),
            'with_clean': sum(1 for r in t1_rows if r.get('n_clean', 0) > 0),
            'with_SM': sum(1 for r in t2_rows if r.get('has_SM')),
            'with_GUT': sum(1 for r in t2_rows if r.get('has_GUT')),
            'max_clean': max((r.get('n_clean', 0) for r in t1_rows), default=0),
        },
        't0': t0_compact,
        't1': t1_rows,
        't2': t2_rows,
    }

    with open(receipt_path, 'w') as f:
        json.dump(receipt, f, indent=2, default=str)

    return receipt_path


# ══════════════════════════════════════════════════════════════════
#  Progress display
# ══════════════════════════════════════════════════════════════════

def fmt_time(secs):
    if secs < 60:
        return f"{secs:.0f}s"
    elif secs < 3600:
        return f"{secs/60:.1f}m"
    else:
        return f"{secs/3600:.1f}h"


def print_header(h11, n_polys, n_workers):
    print(f"\n{'═'*72}")
    print(f"  {BOLD}PIPELINE v2 (GAP-AWARE){RESET}  "
          f"h¹¹ = {h11}  |  {n_polys:,} polytopes  |  {n_workers} workers")
    print(f"  {DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"  {DIM}EFF_MAX={EFF_MAX}  GAP_MIN={GAP_MIN}  "
          f"H0_MIN={H0_MIN_T025}  AUT_MAX={AUT_MAX}{RESET}")
    print(f"{'═'*72}\n")


def print_stage_header(name, n_items):
    print(f"\n  {'─'*56}")
    print(f"  {BOLD}{name}{RESET}  ({n_items:,} polytopes)")
    print(f"  {'─'*56}")


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
#  Main pipeline orchestrator
# ══════════════════════════════════════════════════════════════════

def run_pipeline(h11, workers=4, top_n=500, skip_t0=False, resume=False,
                 gap_min=None, eff_max=None, h0_min=None, aut_max=None,
                 verbose=False):
    """Run gap-aware pipeline for one h¹¹ value.

    Args:
        h11: Hodge number h¹¹
        workers: number of parallel workers
        top_n: max polytopes for T1 deep analysis (0=all passes)
        skip_t0: skip T0, load from DB
        resume: resume from checkpoint
        gap_min: override GAP_MIN threshold
        eff_max: override EFF_MAX threshold
        h0_min: override H0_MIN_T025 threshold
        aut_max: override AUT_MAX threshold
        verbose: print detailed output
    """
    global EFF_MAX, GAP_MIN, H0_MIN_T025, AUT_MAX
    if gap_min is not None:
        GAP_MIN = gap_min
    if eff_max is not None:
        EFF_MAX = eff_max
    if h0_min is not None:
        H0_MIN_T025 = h0_min
    if aut_max is not None:
        AUT_MAX = aut_max

    import cytools as cy
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    h21 = h11 + 3
    t_start = time.time()

    # ── Open database (optional — works without it) ──
    db = None
    if HAS_DB:
        try:
            db = LandscapeDB()
        except Exception as e:
            print(f"  {YELLOW}DB unavailable ({e}) — receipt-only mode{RESET}")

    # ── Load checkpoint ──
    ckpt = load_checkpoint(h11) if resume else None

    # ── Fetch polytopes ──
    print(f"  Fetching h¹¹={h11}, h²¹={h21} polytopes...", end='', flush=True)
    polys = list(cy.fetch_polytopes(h11=h11, h21=h21, lattice='N',
                                     limit=1_000_000))
    n_polys = len(polys)
    print(f" {n_polys:,} found.")

    if n_polys == 0:
        print(f"  No polytopes found for h11={h11}. Skipping.")
        if db:
            db.close()
        return

    print_header(h11, n_polys, workers)

    # ════════════════════════════════════════════════════════════
    #  T0: Ultra-fast pre-filter
    # ════════════════════════════════════════════════════════════

    t0_results = {}  # poly_idx -> result dict

    if ckpt and 't0' in ckpt:
        t0_results = {r['poly_idx']: r for r in ckpt['t0']}
        print(f"  {GREEN}Resumed{RESET}: {len(t0_results):,} T0 results from checkpoint.")

    elif skip_t0 and db:
        # Load from database for existing data
        existing = db.query("""
            SELECT poly_idx, h11_eff, favorable, sym_order
            FROM polytopes WHERE h11 = ?
        """, (h11,))
        for row in existing:
            idx = row['poly_idx']
            h11_eff = row['h11_eff']
            gap = h11 - h11_eff if h11_eff is not None else 0
            t0_results[idx] = {
                'poly_idx': idx,
                'h11': h11,
                'h21': h21,
                'h11_eff': h11_eff,
                'gap': gap,
                'favorable': bool(row['favorable']),
                'aut_order': row['sym_order'] or 1,
                'status': 'pass',  # Will re-filter below
                'skip_reason': None,
            }
            # Apply pre-filter
            if h11_eff is not None and h11_eff > EFF_MAX:
                t0_results[idx]['status'] = 'skip'
                t0_results[idx]['skip_reason'] = f'eff={h11_eff}'
            elif gap < GAP_MIN and (h11_eff or 99) >= 15:
                t0_results[idx]['status'] = 'skip'
                t0_results[idx]['skip_reason'] = f'gap={gap}'
            elif (row['sym_order'] or 1) >= AUT_MAX + 1:
                t0_results[idx]['status'] = 'skip'
                t0_results[idx]['skip_reason'] = f'|Aut|={row["sym_order"]}'

        n_pass = sum(1 for r in t0_results.values() if r['status'] == 'pass')
        print(f"  Loaded {len(t0_results):,} T0 from DB, {n_pass:,} pass.")

    if not t0_results:
        print_stage_header("T0: Pre-filter (h11_eff + gap + |Aut|)", n_polys)

        work = []
        for i, p in enumerate(polys):
            vert = np.array(p.points(), dtype=int).tolist()
            work.append((vert, i, h11))

        t0_time = time.time()
        n_pass = 0
        n_done = 0
        skip_counts = Counter()

        with mp.Pool(workers) as pool:
            for result in pool.imap_unordered(_t0_worker, work,
                                              chunksize=max(1, len(work) // (workers * 20))):
                t0_results[result['poly_idx']] = result
                n_done += 1
                if result['status'] == 'pass':
                    n_pass += 1
                elif result.get('skip_reason'):
                    reason = result['skip_reason'].split(':')[0].split('=')[0]
                    skip_counts[reason] += 1

                if n_done % max(1, n_polys // 50) == 0 or n_done == n_polys:
                    print_progress(n_done, n_polys, n_pass,
                                   time.time() - t0_time, "pass")

        elapsed_t0 = time.time() - t0_time
        n_skip = n_polys - n_pass
        print()
        print(f"    Done: {n_pass:,}/{n_polys:,} pass "
              f"({100*n_pass/n_polys:.1f}%) in {fmt_time(elapsed_t0)} "
              f"({n_polys/elapsed_t0:.1f} poly/s)")
        print(f"    Filtered: {n_skip:,} skipped — ", end='')
        for reason, count in skip_counts.most_common():
            print(f"{reason}={count:,} ", end='')
        print()

        # ── Gap distribution of passes ──
        gap_dist = Counter()
        eff_dist = Counter()
        for r in t0_results.values():
            if r['status'] == 'pass':
                gap_dist[r.get('gap', 0)] += 1
                eff_dist[r.get('h11_eff', 0)] += 1

        print(f"\n    Gap distribution of {n_pass:,} passes:")
        for gap in sorted(gap_dist.keys()):
            bar = '#' * min(50, gap_dist[gap] * 50 // max(gap_dist.values()))
            print(f"      gap={gap:>2}  {gap_dist[gap]:>6}  {bar}")

        # ── Write T0 to database ──
        if db:
            db_upsert_t0(db, h11, t0_results.values())

        # ── Save checkpoint ──
        save_checkpoint(h11, {
            't0': list(t0_results.values()),
            'stage': 't0_done',
            'timestamp': datetime.now().isoformat(),
        })

    # ════════════════════════════════════════════════════════════
    #  T0.25: Fast h⁰ check on T0 passes
    # ════════════════════════════════════════════════════════════

    t0_passes = [r for r in t0_results.values() if r['status'] == 'pass']

    # Sort by gap DESC for optimal triage (best candidates first)
    t0_passes.sort(key=lambda r: (r.get('gap', 0), r.get('h11_eff', 99)),
                   reverse=True)

    t025_results = {}

    if ckpt and 't025' in ckpt:
        t025_results = {r['poly_idx']: r for r in ckpt['t025']}
        print(f"  {GREEN}Resumed{RESET}: {len(t025_results):,} T0.25 results from checkpoint.")

    # Filter out already-done
    todo_t025 = [r for r in t0_passes if r['poly_idx'] not in t025_results]

    if todo_t025:
        print_stage_header(f"T0.25: h⁰ ≥ {H0_MIN_T025} check", len(todo_t025))

        work = []
        for r in todo_t025:
            idx = r['poly_idx']
            vert = np.array(polys[idx].points(), dtype=int).tolist()
            work.append((vert, idx, h11, r.get('h11_eff', h11)))

        t025_time = time.time()
        n_pass = sum(1 for r in t025_results.values() if r.get('status') == 'pass')
        n_done = 0

        with mp.Pool(workers) as pool:
            for result in pool.imap_unordered(_t025_worker, work,
                                              chunksize=max(1, len(work) // (workers * 20))):
                t025_results[result['poly_idx']] = result
                n_done += 1
                if result.get('status') == 'pass':
                    n_pass += 1

                if n_done % max(1, len(todo_t025) // 50) == 0 or n_done == len(todo_t025):
                    print_progress(n_done, len(todo_t025), n_pass,
                                   time.time() - t025_time, "pass")

        elapsed_t025 = time.time() - t025_time
        total_pass = sum(1 for r in t025_results.values() if r.get('status') == 'pass')
        print()
        print(f"    Done: {total_pass:,}/{len(t0_passes):,} pass "
              f"({100*total_pass/len(t0_passes):.1f}%) in {fmt_time(elapsed_t025)}")

        # ── Write T0.25 results to database ──
        if db:
            db_upsert_t025(db, h11, t025_results.values())

        # ── Save checkpoint ──
        save_checkpoint(h11, {
            't0': list(t0_results.values()),
            't025': list(t025_results.values()),
            'stage': 't025_done',
            'timestamp': datetime.now().isoformat(),
        })

    # ════════════════════════════════════════════════════════════
    #  Select top-N for T1 deep analysis
    #  Rank by: gap DESC, n_chi3 DESC, max_h0 DESC
    # ════════════════════════════════════════════════════════════

    passes = [r for r in t025_results.values() if r.get('status') == 'pass']

    # Enrich with T0 data (gap, eff)
    for r in passes:
        t0_data = t0_results.get(r['poly_idx'], {})
        r['gap'] = t0_data.get('gap', 0)
        r['h11_eff'] = t0_data.get('h11_eff', h11)

    # Sort by gap DESC, then n_chi3 DESC, then max_h0 DESC
    passes.sort(key=lambda r: (
        r.get('gap', 0),
        r.get('n_chi3', 0),
        r.get('max_h0', 0),
    ), reverse=True)

    if top_n > 0 and len(passes) > top_n:
        selected = passes[:top_n]
        print(f"\n  Selected top {top_n} of {len(passes):,} passes "
              f"(gap cutoff: {selected[-1].get('gap', '?')})")
    else:
        selected = passes
        print(f"\n  All {len(selected):,} passes selected for T1 analysis.")

    # ════════════════════════════════════════════════════════════
    #  T1: Deep analysis
    # ════════════════════════════════════════════════════════════

    t1_results = {}

    if ckpt and 't1' in ckpt:
        t1_results = {r['poly_idx']: r for r in ckpt['t1']}
        print(f"  {GREEN}Resumed{RESET}: {len(t1_results):,} T1 results from checkpoint.")

    todo_t1 = [s for s in selected if s['poly_idx'] not in t1_results]

    if todo_t1:
        print_stage_header("T1: Deep Analysis (bundles + divisors + fibers)", len(todo_t1))

        work = []
        for s in todo_t1:
            idx = s['poly_idx']
            vert = np.array(polys[idx].points(), dtype=int).tolist()
            work.append((vert, idx, h11, s.get('max_h0', 0), s.get('gap', 0)))

        t1_time = time.time()
        n_done = 0
        total_t1 = len(work)

        with mp.Pool(workers) as pool:
            for result in pool.imap_unordered(_t1_worker, work, chunksize=1):
                t1_results[result['poly_idx']] = result
                n_done += 1

                # Write to DB immediately
                if result.get('status') == 'ok' and db:
                    db_upsert_t1(db, result)

                # Progress
                idx = result['poly_idx']
                status = result.get('status', '?')
                elapsed_i = result.get('elapsed', 0)
                rate = n_done / (time.time() - t1_time)
                eta = (total_t1 - n_done) / rate if rate > 0 else 0

                if status == 'ok':
                    sc = result.get('score', 0)
                    nc = result.get('n_clean', 0)
                    gap = result.get('gap', 0)
                    nel = result.get('n_ell', 0)
                    sw = 'SC' if result.get('has_swiss') else '--'
                    tag = f"{STAR} " if nc > 0 else "  "
                    print(f"    {tag}P{idx:<6d} gap={gap} score={sc}/26  "
                          f"clean={nc:<4d} ell={nel:<3d} {sw}  "
                          f"[{elapsed_i:.1f}s]  "
                          f"({n_done}/{total_t1}, ETA {fmt_time(eta)})")
                else:
                    print(f"    {DIM}  P{idx:<6d} {status}{RESET}  "
                          f"({n_done}/{total_t1})")

                # Checkpoint every 25 polytopes
                if n_done % 25 == 0:
                    save_checkpoint(h11, {
                        't0': list(t0_results.values()),
                        't025': list(t025_results.values()),
                        't1': list(t1_results.values()),
                        'stage': 't1_partial',
                        'timestamp': datetime.now().isoformat(),
                    })

        elapsed_t1 = time.time() - t1_time
        print(f"\n    T1 complete: {n_done} polytopes in {fmt_time(elapsed_t1)}")

        save_checkpoint(h11, {
            't0': list(t0_results.values()),
            't025': list(t025_results.values()),
            't1': list(t1_results.values()),
            'stage': 't1_done',
            'timestamp': datetime.now().isoformat(),
        })

    # ════════════════════════════════════════════════════════════
    #  T2: Fiber analysis (on polytopes with elliptic fibs)
    # ════════════════════════════════════════════════════════════

    fiber_candidates = [
        r for r in t1_results.values()
        if r.get('status') == 'ok' and r.get('n_ell', 0) >= 1
    ]
    fiber_candidates.sort(key=lambda r: (r.get('gap', 0), r.get('score', 0)),
                          reverse=True)

    t2_results = {}

    if ckpt and 't2' in ckpt:
        t2_results = {r['poly_idx']: r for r in ckpt['t2']}
        print(f"  {GREEN}Resumed{RESET}: {len(t2_results):,} T2 results from checkpoint.")

    todo_t2 = [c for c in fiber_candidates if c['poly_idx'] not in t2_results]

    if todo_t2:
        print_stage_header("T2: Fiber Classification", len(todo_t2))

        for i, cand in enumerate(todo_t2, 1):
            idx = cand['poly_idx']
            t0_f = time.time()
            result = run_t2(polys[idx], idx, h11)
            elapsed_i = time.time() - t0_f

            t2_results[idx] = result

            # Write to DB immediately
            if db:
                db_upsert_t2(db, h11, idx, result)

            nf = result.get('n_fibrations', 0)
            fibs = result.get('fibrations', [])
            sm_count = sum(1 for f in fibs if f.get('contains_SM'))
            gut_count = sum(1 for f in fibs if f.get('has_SU5_GUT'))
            best_ga = ''
            if fibs:
                best = max(fibs, key=lambda f: f.get('gauge_rank', 0))
                best_ga = best.get('gauge_algebra', '')[:40]

            sm_tag = f" {STAR}SM" if sm_count > 0 else ""
            gut_tag = f" {STAR}GUT" if gut_count > 0 else ""

            print(f"    P{idx:<6d} {nf} fibs  {sm_count} SM  "
                  f"{gut_count} GUT{sm_tag}{gut_tag}  [{elapsed_i:.1f}s]  "
                  f"({i}/{len(todo_t2)})")
            if best_ga:
                print(f"           {DIM}best: {best_ga}{RESET}")

        save_checkpoint(h11, {
            't0': list(t0_results.values()),
            't025': list(t025_results.values()),
            't1': list(t1_results.values()),
            't2': list(t2_results.values()),
            'stage': 't2_done',
            'timestamp': datetime.now().isoformat(),
        })

    # ════════════════════════════════════════════════════════════
    #  Final ranking and output
    # ════════════════════════════════════════════════════════════

    print(f"\n{'═'*72}")
    print(f"  {BOLD}RESULTS SUMMARY — h¹¹ = {h11} (Pipeline v2){RESET}")
    print(f"{'═'*72}")

    # Merge T1 + T2
    final = []
    for r in t1_results.values():
        if r.get('status') != 'ok':
            continue
        idx = r['poly_idx']
        entry = dict(r)

        s2 = t2_results.get(idx)
        if s2 and s2.get('n_fibrations', 0) > 0:
            fibs = s2.get('fibrations', [])
            entry['n_fibers'] = len(fibs)
            entry['has_SM'] = any(f.get('contains_SM') for f in fibs)
            entry['has_GUT'] = any(f.get('has_SU5_GUT') for f in fibs)
            best_fib = max(fibs, key=lambda f: f.get('gauge_rank', 0),
                          default={})
            entry['best_gauge'] = best_fib.get('gauge_algebra', '')
        else:
            entry['n_fibers'] = 0
            entry['has_SM'] = False
            entry['has_GUT'] = False
            entry['best_gauge'] = ''

        final.append(entry)

    # Sort by gap DESC, score DESC, n_clean DESC
    final.sort(key=lambda r: (
        r.get('gap', 0),
        r.get('score', 0),
        r.get('n_clean', 0),
    ), reverse=True)

    # ── Summary stats ──
    n_26 = sum(1 for r in final if r.get('score', 0) == 26)
    n_25 = sum(1 for r in final if r.get('score', 0) == 25)
    n_sm = sum(1 for r in final if r.get('has_SM'))
    n_gut = sum(1 for r in final if r.get('has_GUT'))
    n_with_clean = sum(1 for r in final if r.get('n_clean', 0) > 0)
    max_clean = max((r.get('n_clean', 0) for r in final), default=0)
    max_ell = max((r.get('n_ell', 0) for r in final), default=0)

    n_t0_total = len(t0_results)
    n_t0_pass = sum(1 for r in t0_results.values() if r['status'] == 'pass')
    n_t025_pass = sum(1 for r in t025_results.values() if r.get('status') == 'pass')

    print(f"\n  Polytopes fetched:           {n_polys:,}")
    print(f"  T0 passes:                   {n_t0_pass:,}/{n_t0_total:,} "
          f"({100*n_t0_pass/n_t0_total:.1f}%)")
    print(f"  T0.25 passes (h⁰≥{H0_MIN_T025}):       {n_t025_pass:,}/{n_t0_pass:,} "
          f"({100*n_t025_pass/n_t0_pass:.1f}%)" if n_t0_pass > 0 else "")
    print(f"  T1 deep-analyzed:            {len(final):,}")
    print(f"  T2 fiber-analyzed:           {len(t2_results):,}")
    print()
    print(f"  Score 26/26 (perfect):       {n_26}")
    print(f"  Score 25/26:                 {n_25}")
    print(f"  With clean bundles:          {n_with_clean}")
    print(f"  SM gauge group:              {n_sm}")
    print(f"  SU(5) GUT candidates:        {n_gut}")
    print(f"  Max clean bundles:           {max_clean}")
    print(f"  Max elliptic fibrations:     {max_ell}")

    # ── Gap breakdown ──
    gap_summary = Counter()
    for r in final:
        gap_summary[r.get('gap', 0)] += 1
    print(f"\n  Gap distribution of T1 results:")
    for gap in sorted(gap_summary.keys(), reverse=True):
        n_clean_at_gap = sum(1 for r in final
                            if r.get('gap', 0) == gap and r.get('n_clean', 0) > 0)
        print(f"    gap={gap}  N={gap_summary[gap]:>4}  "
              f"with_clean={n_clean_at_gap}")

    # ── Top 20 table ──
    show = min(20, len(final))
    if show > 0:
        print(f"\n  {BOLD}Top {show} Candidates:{RESET}")
        print(f"  {'Rank':>4s}  {'Poly':>6s}  {'Gap':>3s}  {'Eff':>3s}  "
              f"{'Score':>5s}  {'Clean':>5s}  {'h0':>3s}  "
              f"{'dP':>2s}  {'SC':>2s}  {'K3':>3s}  {'Ell':>3s}  "
              f"{'SM':>3s}  Gauge")
        print(f"  {'─'*4}  {'─'*6}  {'─'*3}  {'─'*3}  "
              f"{'─'*5}  {'─'*5}  {'─'*3}  "
              f"{'─'*2}  {'─'*2}  {'─'*3}  {'─'*3}  "
              f"{'─'*3}  {'─'*30}")

        for i, r in enumerate(final[:show], 1):
            idx = r['poly_idx']
            gap = r.get('gap', 0)
            eff = r.get('h11_eff', 0)
            sc = r.get('score', 0)
            nc = r.get('n_clean', 0)
            mh = r.get('max_h0', 0)
            dp = r.get('n_dp', 0)
            sw = 'Y' if r.get('has_swiss') else '-'
            nk = r.get('n_k3', 0)
            ne = r.get('n_ell', 0)
            sm = '★' if r.get('has_SM') else '-'
            ga = r.get('best_gauge', '')[:30]

            star = f"{STAR}" if nc > 0 else " "
            print(f"  {star}{i:3d}  P{idx:<5d}  {gap:>3d}  {eff:>3d}  "
                  f"{sc:>2d}/26  {nc:>5d}  {mh:>3d}  "
                  f"{dp:>2d}  {sw:>2s}  {nk:>3d}  {ne:>3d}  "
                  f"{sm:>3s}  {ga}")

    # ── Save outputs ──
    elapsed_total = time.time() - t_start
    csv_path = save_results_csv(h11, final)

    # ── Write receipt (always — this is the primary data transport) ──
    thresholds = {
        'EFF_MAX': EFF_MAX,
        'GAP_MIN': GAP_MIN,
        'H0_MIN_T025': H0_MIN_T025,
        'AUT_MAX': AUT_MAX,
        'top_n': top_n,
        'workers': workers,
    }
    receipt_path = write_receipt(
        h11, t_start, elapsed_total,
        n_polys, t0_results, t025_results,
        t1_results, t2_results, final,
        thresholds,
    )

    # Log scan in DB (if available)
    hostname = socket.gethostname()
    if db:
        db.log_scan(
            h11=h11,
            tier='T2+',
            machine=hostname,
            script='pipeline_v2.py',
            n_polytopes=n_polys,
            n_screened=len(final),
            n_passed=n_with_clean,
            notes=(f"v2 gap-aware: T0={n_t0_pass}/{n_polys}, "
                   f"T025={n_t025_pass}/{n_t0_pass}, T1={len(final)}, "
                   f"T2={len(t2_results)}, max_clean={max_clean}, "
                   f"elapsed={fmt_time(elapsed_total)}"),
        )

    print(f"\n  {GREEN}Saved:{RESET}")
    print(f"    Receipt: {receipt_path}")
    print(f"    CSV:     {csv_path}")
    if db:
        print(f"    DB:      cy_landscape.db ({len(final)} rows updated)")
    else:
        print(f"    DB:      {YELLOW}skipped (not available){RESET}")
    print(f"    Checkpoint: {checkpoint_path(h11)}")
    print(f"\n  Total time: {fmt_time(elapsed_total)}")
    print(f"{'═'*72}\n")

    if db:
        db.close()
    return final


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline v2: gap-aware CY3 scan (Finding 14)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Based on 30-query database analysis of 74,819 polytopes (Finding 14).
Key insight: gap = h11 - h11_eff is the strongest predictor of clean bundles.

Examples:
  python pipeline_v2.py --h11 19                  # scan h11=19
  python pipeline_v2.py --h11 19 20 -w 14         # multi-h11
  python pipeline_v2.py --h11 18 --resume          # resume from checkpoint
  python pipeline_v2.py --h11 18 --gap-min 3       # stricter gap filter
  python pipeline_v2.py --h11 17 --top 0           # analyze ALL passes
""")
    parser.add_argument('--h11', type=int, nargs='+', required=True,
                        help='h¹¹ values to scan')
    parser.add_argument('-w', '--workers', type=int,
                        default=max(1, mp.cpu_count() - 1),
                        help=f'Parallel workers (default: {max(1, mp.cpu_count()-1)})')
    parser.add_argument('--top', type=int, default=500,
                        help='Max polytopes for T1 analysis (0=all, default: 500)')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from checkpoint')
    parser.add_argument('--skip-t0', action='store_true',
                        help='Skip T0, load from database')
    parser.add_argument('--gap-min', type=int, default=None,
                        help=f'Minimum gap threshold (default: {GAP_MIN})')
    parser.add_argument('--eff-max', type=int, default=None,
                        help=f'Maximum h11_eff threshold (default: {EFF_MAX})')
    parser.add_argument('--h0-min', type=int, default=None,
                        help=f'Minimum h0 for T0.25 (default: {H0_MIN_T025})')
    parser.add_argument('--aut-max', type=int, default=None,
                        help=f'Maximum |Aut| (default: {AUT_MAX})')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    all_results = {}
    for h in args.h11:
        results = run_pipeline(
            h11=h,
            workers=args.workers,
            top_n=args.top,
            skip_t0=args.skip_t0,
            resume=args.resume,
            gap_min=args.gap_min,
            eff_max=args.eff_max,
            h0_min=args.h0_min,
            aut_max=args.aut_max,
            verbose=args.verbose,
        )
        if results:
            all_results[h] = results

    # Multi-h11 summary
    if len(all_results) > 1:
        print(f"\n{'═'*72}")
        print(f"  {BOLD}MULTI-H11 SUMMARY (Pipeline v2){RESET}")
        print(f"{'═'*72}")
        for h, results in sorted(all_results.items()):
            n_clean = sum(1 for r in results if r.get('n_clean', 0) > 0)
            nsm = sum(1 for r in results if r.get('has_SM'))
            mc = max((r.get('n_clean', 0) for r in results), default=0)
            max_gap = max((r.get('gap', 0) for r in results), default=0)
            print(f"  h¹¹={h:3d}: {len(results):5d} analyzed, "
                  f"{n_clean:4d} with clean, {nsm:4d} SM, "
                  f"max_clean={mc}, max_gap={max_gap}")
        print(f"{'═'*72}\n")


if __name__ == '__main__':
    main()
