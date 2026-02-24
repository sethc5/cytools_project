#!/usr/bin/env python3
"""
auto_scan.py — Fully automated scan-to-analysis pipeline.

Replaces the 6-script manual workflow:
  scan_fast → tier1_screen → tier15_screen → tier2_screen → pipeline → fiber_analysis

with a SINGLE command:

    python auto_scan.py --h11 19 --workers 8 --top 100

Pipeline stages (per polytope):

  Stage 0 (T0.25):  Early-termination h⁰≥3 check       (~0.08s/poly)
  Stage 1 (deep):   Full bundle count + clean bundles    (~2-30s/poly)
                     + dP/K3 divisor classification
                     + Swiss cheese check
                     + K3 + elliptic fibration count
  Stage 2 (fiber):  Kodaira classification + gauge alg   (~1-5s/poly)

Flow:
  1. Fetch all χ=-6 polytopes at given h¹¹
  2. Run Stage 0 on ALL polytopes (parallel, fast)
  3. Rank by max_h0 descending, take top N
  4. Run Stage 1 on top N (parallel, expensive)
  5. Run Stage 2 on anything with ≥1 elliptic fibration
  6. Score, rank, output CSV + JSON

Checkpoint/resume:
  Saves progress to results/auto_{h11}.checkpoint.json after each polytope.
  On restart, skips already-completed polytopes automatically.

Usage:
    python auto_scan.py --h11 19                         # defaults
    python auto_scan.py --h11 19 20 --workers 14         # multi-h11
    python auto_scan.py --h11 17 --top 50 --skip-t025    # skip T0.25 (use existing)
    python auto_scan.py --h11 15 --top 0                 # top=0 means ALL passes
    python auto_scan.py --h11 18 --resume                # resume from checkpoint
"""

import argparse
import csv
import json
import multiprocessing as mp
import time
from datetime import datetime
from pathlib import Path

import numpy as np

# ══════════════════════════════════════════════════════════════════
#  Constants
# ══════════════════════════════════════════════════════════════════

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

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

# Scoring weights (same as pipeline.py — 26-point scale)
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
#  Stage 0: T0.25 fast pre-filter (parallel)
# ══════════════════════════════════════════════════════════════════

def _stage0_worker(args):
    """T0.25: early-termination h⁰≥3 check. Runs in subprocess."""
    vert, poly_idx, h11_val = args
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
            return {'poly_idx': poly_idx, 'status': 'skip', 'max_h0': 0}

        # Adaptive search range
        if h11_eff <= 15:
            mc, mnz = 3, 3
        elif h11_eff <= 20:
            mc, mnz = 2, 3
        else:
            mc, mnz = 2, 2

        bundles = find_chi3_bundles(intnums, c2, h11_eff, mc, mnz)
        if not bundles:
            return {'poly_idx': poly_idx, 'status': 'skip', 'max_h0': 0,
                    'n_chi3': 0, 'favorable': h11_eff == cyobj.h11()}

        _precomp = precompute_vertex_data(pts, ray_indices)
        max_h0 = 0
        n_computed = 0

        for D_basis, chi in bundles:
            D_toric = basis_to_toric(D_basis, div_basis, n_toric)
            if chi > 0:
                h0 = compute_h0_koszul(pts, ray_indices, D_toric,
                                       _precomp=_precomp, min_h0=3)
            else:
                D_neg = basis_to_toric(-D_basis, div_basis, n_toric)
                h0 = compute_h0_koszul(pts, ray_indices, D_neg,
                                       _precomp=_precomp, min_h0=3)
            n_computed += 1
            if h0 > max_h0:
                max_h0 = h0
            if h0 >= 3:
                break  # Early termination

        return {
            'poly_idx': poly_idx,
            'status': 'pass' if max_h0 >= 3 else 'skip',
            'max_h0': max_h0,
            'n_chi3': len(bundles),
            'favorable': h11_eff == cyobj.h11(),
            'h11_eff': h11_eff,
        }
    except Exception as e:
        return {'poly_idx': poly_idx, 'status': 'error', 'max_h0': 0,
                'error': str(e)[:100]}


# ══════════════════════════════════════════════════════════════════
#  Stage 1: Deep analysis (parallel)
# ══════════════════════════════════════════════════════════════════

def _stage1_worker(args):
    """Full deep analysis: clean bundles + divisors + Swiss cheese + fibrations.

    Merges T1 + T1.5 + T2 + pipeline scoring into one pass.
    """
    vert, poly_idx, h11_val, scan_max_h0 = args
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

        # ── Swiss cheese (pipeline-style manual contraction) ──
        has_swiss = False
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
                best_tau = swiss_hits[0][1]
                best_ratio = swiss_hits[0][3]
        except Exception:
            pass

        # ── Fibrations ──
        n_k3, n_ell = count_fibrations(p)

        # ── Score (26-point) ──
        chi = -6  # We only scan chi=-6
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
            'n_chi3': n_chi3,
            'max_h0': max_h0,
            'h0_ge3': h0_ge3,
            'n_clean': n_clean,
            'd3_unique': len(d3_unique),
            'n_dp': n_dp,
            'dp_types': dp_types,
            'n_k3_div': n_k3_div,
            'n_rigid': n_rigid,
            'has_swiss': has_swiss,
            'best_tau': best_tau,
            'best_ratio': best_ratio,
            'n_k3': n_k3,
            'n_ell': n_ell,
            'score': score,
            'elapsed': elapsed,
        }
    except Exception as e:
        return {'poly_idx': poly_idx, 'status': 'error',
                'error': str(e)[:200]}


# ══════════════════════════════════════════════════════════════════
#  Stage 2: Fiber analysis (sequential — uses full polytope object)
# ══════════════════════════════════════════════════════════════════

def run_stage2(polytope, poly_idx, h11_val):
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
#  Checkpoint management
# ══════════════════════════════════════════════════════════════════

def checkpoint_path(h11):
    return RESULTS_DIR / f"auto_h{h11}.checkpoint.json"


def load_checkpoint(h11):
    """Load checkpoint if it exists."""
    path = checkpoint_path(h11)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def save_checkpoint(h11, data):
    """Save progress checkpoint."""
    path = checkpoint_path(h11)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)


# ══════════════════════════════════════════════════════════════════
#  Output
# ══════════════════════════════════════════════════════════════════

def save_results_csv(h11, results):
    """Save final ranked results to CSV."""
    path = RESULTS_DIR / f"auto_h{h11}.csv"
    if not results:
        return

    fields = ['rank', 'poly_idx', 'score', 'n_clean', 'max_h0', 'n_chi3',
              'n_dp', 'has_swiss', 'best_tau', 'n_k3', 'n_ell',
              'd3_unique', 'h11_eff', 'favorable',
              'n_fibers', 'has_SM', 'has_GUT', 'best_gauge', 'elapsed']

    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for i, r in enumerate(results, 1):
            row = {**r, 'rank': i}
            w.writerow(row)
    return path


def save_results_json(h11, results, meta):
    """Save full results with metadata to JSON."""
    path = RESULTS_DIR / f"auto_h{h11}.json"
    out = {
        'h11': h11,
        'meta': meta,
        'results': results,
    }
    with open(path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    return path


# ══════════════════════════════════════════════════════════════════
#  Progress display
# ══════════════════════════════════════════════════════════════════

def fmt_time(secs):
    """Format seconds to human-readable."""
    if secs < 60:
        return f"{secs:.0f}s"
    elif secs < 3600:
        return f"{secs/60:.1f}m"
    else:
        return f"{secs/3600:.1f}h"


def print_header(h11, n_polys, n_workers):
    print(f"\n{'═'*72}")
    print(f"  {BOLD}AUTO-SCAN PIPELINE{RESET}  "
          f"h¹¹ = {h11}  |  {n_polys:,} polytopes  |  {n_workers} workers")
    print(f"  {DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{'═'*72}\n")


def print_stage_header(name, n_items):
    print(f"\n  {'─'*56}")
    print(f"  {BOLD}{name}{RESET}  ({n_items:,} polytopes)")
    print(f"  {'─'*56}")


def print_stage0_progress(done, total, n_pass, elapsed):
    """Print T0.25 progress (called periodically)."""
    rate = done / elapsed if elapsed > 0 else 0
    eta = (total - done) / rate if rate > 0 else 0
    pct = 100 * done / total if total > 0 else 0
    bar_w = 30
    filled = int(bar_w * done / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_w - filled)
    print(f"\r    {bar} {pct:5.1f}%  "
          f"{done:,}/{total:,}  {n_pass} pass  "
          f"{rate:.1f}/s  ETA {fmt_time(eta)}  ", end='', flush=True)


# ══════════════════════════════════════════════════════════════════
#  Main pipeline orchestrator
# ══════════════════════════════════════════════════════════════════

def run_pipeline(h11, workers=4, top_n=200, skip_t025=False, resume=False,
                 t025_csv=None, verbose=False):
    """Run full automated pipeline for one h¹¹ value.

    Args:
        h11: Hodge number h¹¹
        workers: number of parallel workers
        top_n: max polytopes for deep analysis (0=all passes)
        skip_t025: skip T0.25, load from existing CSV
        resume: resume from checkpoint
        t025_csv: path to existing T0.25 CSV to load
        verbose: print detailed output
    """
    import cytools as cy
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    h21 = h11 + 3
    t_start = time.time()

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
        return

    print_header(h11, n_polys, workers)

    # ════════════════════════════════════════════════════════════
    #  STAGE 0: T0.25 fast pre-filter
    # ════════════════════════════════════════════════════════════

    t025_results = {}  # poly_idx -> result dict

    if ckpt and 't025' in ckpt:
        # Resume from checkpoint
        t025_results = {r['poly_idx']: r for r in ckpt['t025']}
        print(f"  {GREEN}Resumed{RESET}: {len(t025_results):,} T0.25 results from checkpoint.")

    elif skip_t025 and t025_csv:
        # Load from existing CSV (scan_h*.csv or tier025_h*.csv)
        print(f"  Loading T0.25 from {t025_csv}...")
        with open(t025_csv) as f:
            reader = csv.DictReader(f)
            for row in reader:
                idx = int(row.get('poly_idx', row.get('index', -1)))
                if idx >= 0:
                    mh = int(row.get('max_h0', 0))
                    # Normalize status: scan_h*.csv uses 'ok', we use 'pass'
                    raw_status = row.get('status', 'pass')
                    status = 'pass' if (raw_status in ('ok', 'pass') and mh >= 3) else 'skip'
                    t025_results[idx] = {
                        'poly_idx': idx,
                        'status': status,
                        'max_h0': mh,
                    }
        n_pass = sum(1 for r in t025_results.values() if r['status'] == 'pass')
        print(f"  Loaded {len(t025_results):,} entries, {n_pass:,} passes.")

    elif skip_t025:
        # Skip T0.25, send everything to Stage 1 (not recommended for large h11)
        print(f"  {YELLOW}WARNING{RESET}: Skipping T0.25, all {n_polys:,} go to Stage 1.")
        for i in range(n_polys):
            t025_results[i] = {'poly_idx': i, 'status': 'pass', 'max_h0': 99}

    if not t025_results:
        # Run T0.25
        print_stage_header("STAGE 0: T0.25 Pre-filter", n_polys)

        # Prepare work items
        work = []
        for i, p in enumerate(polys):
            vert = np.array(p.points(), dtype=int).tolist()
            work.append((vert, i, h11))

        t0 = time.time()
        n_pass = 0
        n_done = 0

        with mp.Pool(workers) as pool:
            for result in pool.imap_unordered(_stage0_worker, work,
                                              chunksize=max(1, len(work) // (workers * 20))):
                t025_results[result['poly_idx']] = result
                n_done += 1
                if result.get('status') == 'pass':
                    n_pass += 1

                # Progress every 100 or 2%
                if n_done % max(1, n_polys // 50) == 0 or n_done == n_polys:
                    print_stage0_progress(n_done, n_polys, n_pass,
                                         time.time() - t0)

        elapsed_t025 = time.time() - t0
        print()  # newline after progress bar
        print(f"    Done: {n_pass:,}/{n_polys:,} pass "
              f"({100*n_pass/n_polys:.1f}%) in {fmt_time(elapsed_t025)} "
              f"({n_polys/elapsed_t025:.1f} poly/s)")

        # Save checkpoint
        save_checkpoint(h11, {
            't025': list(t025_results.values()),
            'stage': 't025_done',
            'timestamp': datetime.now().isoformat(),
        })

    # ════════════════════════════════════════════════════════════
    #  Select top-N for deep analysis
    # ════════════════════════════════════════════════════════════

    passes = [r for r in t025_results.values()
              if r.get('status') == 'pass']
    passes.sort(key=lambda r: r.get('max_h0', 0), reverse=True)

    if top_n > 0 and len(passes) > top_n:
        selected = passes[:top_n]
        print(f"\n  Selected top {top_n} of {len(passes):,} passes "
              f"(max_h0 cutoff: {selected[-1].get('max_h0', '?')})")
    else:
        selected = passes
        print(f"\n  All {len(selected):,} passes selected for deep analysis.")

    # ════════════════════════════════════════════════════════════
    #  STAGE 1: Deep analysis
    # ════════════════════════════════════════════════════════════

    stage1_results = {}

    if ckpt and 'stage1' in ckpt:
        stage1_results = {r['poly_idx']: r for r in ckpt['stage1']}
        print(f"  {GREEN}Resumed{RESET}: {len(stage1_results):,} Stage 1 results from checkpoint.")

    # Filter out already-done
    todo_s1 = [s for s in selected if s['poly_idx'] not in stage1_results]

    if todo_s1:
        print_stage_header("STAGE 1: Deep Analysis", len(todo_s1))

        work = []
        for s in todo_s1:
            idx = s['poly_idx']
            vert = np.array(polys[idx].points(), dtype=int).tolist()
            work.append((vert, idx, h11, s.get('max_h0', 0)))

        t0 = time.time()
        n_done = 0
        total_s1 = len(work)

        # Use imap for ordered progress with periodic checkpointing
        with mp.Pool(workers) as pool:
            for result in pool.imap_unordered(_stage1_worker, work,
                                              chunksize=1):
                stage1_results[result['poly_idx']] = result
                n_done += 1

                # Brief progress line
                idx = result['poly_idx']
                status = result.get('status', '?')
                elapsed_i = result.get('elapsed', 0)
                rate = n_done / (time.time() - t0)
                eta = (total_s1 - n_done) / rate if rate > 0 else 0

                if status == 'ok':
                    sc = result.get('score', 0)
                    nc = result.get('n_clean', 0)
                    nel = result.get('n_ell', 0)
                    sw = 'SC' if result.get('has_swiss') else '--'
                    tag = f"{STAR} " if sc >= 25 else "  "
                    print(f"    {tag}P{idx:<6d} score={sc}/26  "
                          f"clean={nc:<4d} ell={nel:<3d} {sw}  "
                          f"[{elapsed_i:.1f}s]  "
                          f"({n_done}/{total_s1}, ETA {fmt_time(eta)})")
                else:
                    print(f"    {DIM}  P{idx:<6d} {status}{RESET}  "
                          f"({n_done}/{total_s1})")

                # Checkpoint every 25 polytopes
                if n_done % 25 == 0:
                    save_checkpoint(h11, {
                        't025': list(t025_results.values()),
                        'stage1': list(stage1_results.values()),
                        'stage': 'stage1_partial',
                        'timestamp': datetime.now().isoformat(),
                    })

        elapsed_s1 = time.time() - t0
        print(f"\n    Stage 1 complete: {n_done} polytopes in {fmt_time(elapsed_s1)}")

        # Save checkpoint
        save_checkpoint(h11, {
            't025': list(t025_results.values()),
            'stage1': list(stage1_results.values()),
            'stage': 'stage1_done',
            'timestamp': datetime.now().isoformat(),
        })

    # ════════════════════════════════════════════════════════════
    #  STAGE 2: Fiber analysis (on polytopes with elliptic fibs)
    # ════════════════════════════════════════════════════════════

    # Collect Stage 1 results with elliptic fibrations
    fiber_candidates = [
        r for r in stage1_results.values()
        if r.get('status') == 'ok' and r.get('n_ell', 0) >= 1
    ]
    fiber_candidates.sort(key=lambda r: r.get('score', 0), reverse=True)

    stage2_results = {}

    if ckpt and 'stage2' in ckpt:
        stage2_results = {r['poly_idx']: r for r in ckpt['stage2']}
        print(f"  {GREEN}Resumed{RESET}: {len(stage2_results):,} Stage 2 results from checkpoint.")

    todo_s2 = [c for c in fiber_candidates if c['poly_idx'] not in stage2_results]

    if todo_s2:
        print_stage_header("STAGE 2: Fiber Classification", len(todo_s2))

        for i, cand in enumerate(todo_s2, 1):
            idx = cand['poly_idx']
            t0 = time.time()
            result = run_stage2(polys[idx], idx, h11)
            elapsed_i = time.time() - t0

            stage2_results[idx] = result
            nf = result.get('n_fibrations', 0)
            sm_count = sum(1 for f in result.get('fibrations', [])
                          if f.get('contains_SM'))
            gut_count = sum(1 for f in result.get('fibrations', [])
                           if f.get('has_SU5_GUT'))
            best_ga = ''
            if result.get('fibrations'):
                best = max(result['fibrations'],
                          key=lambda f: f.get('gauge_rank', 0))
                best_ga = best.get('gauge_algebra', '')[:40]

            sm_tag = f" {STAR}SM" if sm_count > 0 else ""
            gut_tag = f" {STAR}GUT" if gut_count > 0 else ""

            print(f"    P{idx:<6d} {nf} fibs  {sm_count} SM  "
                  f"{gut_count} GUT{sm_tag}{gut_tag}  [{elapsed_i:.1f}s]  "
                  f"({i}/{len(todo_s2)})")
            if best_ga:
                print(f"           {DIM}best: {best_ga}{RESET}")

        # Save checkpoint
        save_checkpoint(h11, {
            't025': list(t025_results.values()),
            'stage1': list(stage1_results.values()),
            'stage2': list(stage2_results.values()),
            'stage': 'stage2_done',
            'timestamp': datetime.now().isoformat(),
        })

    # ════════════════════════════════════════════════════════════
    #  Final ranking and output
    # ════════════════════════════════════════════════════════════

    print(f"\n{'═'*72}")
    print(f"  {BOLD}RESULTS SUMMARY — h¹¹ = {h11}{RESET}")
    print(f"{'═'*72}")

    # Merge Stage 1 + Stage 2
    final = []
    for r in stage1_results.values():
        if r.get('status') != 'ok':
            continue
        idx = r['poly_idx']
        entry = dict(r)

        # Add fiber data if available
        s2 = stage2_results.get(idx)
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

    # Sort by score desc, then n_clean desc, then n_ell desc
    final.sort(key=lambda r: (
        r.get('score', 0),
        r.get('n_clean', 0),
        r.get('n_ell', 0),
    ), reverse=True)

    # ── Summary table ──
    n_26 = sum(1 for r in final if r.get('score', 0) == 26)
    n_25 = sum(1 for r in final if r.get('score', 0) == 25)
    n_23 = sum(1 for r in final if r.get('score', 0) == 23)
    n_sm = sum(1 for r in final if r.get('has_SM'))
    n_gut = sum(1 for r in final if r.get('has_GUT'))
    max_clean = max((r.get('n_clean', 0) for r in final), default=0)
    max_ell = max((r.get('n_ell', 0) for r in final), default=0)
    max_tau = max((r.get('best_tau', 0) for r in final if r.get('has_swiss')),
                  default=0)

    print(f"\n  Polytopes scanned (T0.25):  {n_polys:,}")
    print(f"  T0.25 passes:               {len(passes):,} "
          f"({100*len(passes)/n_polys:.1f}%)")
    print(f"  Deep-analyzed (Stage 1):     {len(final):,}")
    print(f"  Fiber-analyzed (Stage 2):    {len(stage2_results):,}")
    print()
    print(f"  Score 26/26 (perfect):       {n_26}")
    print(f"  Score 25/26:                 {n_25}")
    print(f"  Score 23/26:                 {n_23}")
    print(f"  SM gauge group (SU3×SU2×U1): {n_sm}")
    print(f"  SU(5) GUT candidates:        {n_gut}")
    print(f"  Max clean bundles:           {max_clean}")
    print(f"  Max elliptic fibrations:     {max_ell}")
    print(f"  Max Swiss cheese τ:          {max_tau:.1f}")

    # ── Top 20 table ──
    show = min(20, len(final))
    if show > 0:
        print(f"\n  {BOLD}Top {show} Candidates:{RESET}")
        print(f"  {'Rank':>4s}  {'Poly':>6s}  {'Score':>5s}  {'Clean':>5s}  "
              f"{'h0':>3s}  {'dP':>2s}  {'SC':>2s}  {'τ':>8s}  "
              f"{'K3':>3s}  {'Ell':>3s}  {'SM':>3s}  {'GUT':>3s}  Gauge")
        print(f"  {'─'*4}  {'─'*6}  {'─'*5}  {'─'*5}  "
              f"{'─'*3}  {'─'*2}  {'─'*2}  {'─'*8}  "
              f"{'─'*3}  {'─'*3}  {'─'*3}  {'─'*3}  {'─'*30}")

        for i, r in enumerate(final[:show], 1):
            idx = r['poly_idx']
            sc = r.get('score', 0)
            nc = r.get('n_clean', 0)
            mh = r.get('max_h0', 0)
            dp = r.get('n_dp', 0)
            sw = 'Y' if r.get('has_swiss') else '-'
            tau = f"{r.get('best_tau', 0):.0f}" if r.get('has_swiss') else '-'
            nk = r.get('n_k3', 0)
            ne = r.get('n_ell', 0)
            sm = '★' if r.get('has_SM') else '-'
            gut = '★' if r.get('has_GUT') else '-'
            ga = r.get('best_gauge', '')[:30]

            star = f"{STAR}" if sc >= 25 else " "
            print(f"  {star}{i:3d}  P{idx:<5d}  {sc:>2d}/26  "
                  f"{nc:>5d}  {mh:>3d}  {dp:>2d}  {sw:>2s}  {tau:>8s}  "
                  f"{nk:>3d}  {ne:>3d}  {sm:>3s}  {gut:>3s}  {ga}")

    # ── Save outputs ──
    elapsed_total = time.time() - t_start
    meta = {
        'h11': h11,
        'h21': h21,
        'n_polytopes': n_polys,
        'n_passes': len(passes),
        'n_deep': len(final),
        'n_fiber': len(stage2_results),
        'workers': workers,
        'top_n': top_n,
        'elapsed_total': elapsed_total,
        'timestamp': datetime.now().isoformat(),
    }

    csv_path = save_results_csv(h11, final)
    json_path = save_results_json(h11, final, meta)

    print(f"\n  {GREEN}Saved:{RESET}")
    print(f"    CSV:  {csv_path}")
    print(f"    JSON: {json_path}")
    print(f"    Checkpoint: {checkpoint_path(h11)}")
    print(f"\n  Total time: {fmt_time(elapsed_total)}")
    print(f"{'═'*72}\n")

    return final


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Automated scan-to-analysis pipeline for χ=-6 CY3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_scan.py --h11 19              # scan h11=19, default settings
  python auto_scan.py --h11 19 20 -w 14     # multi-h11, 14 workers
  python auto_scan.py --h11 17 --top 50     # deep-analyze top 50 only
  python auto_scan.py --h11 18 --resume     # resume from checkpoint
  python auto_scan.py --h11 15 --top 0      # analyze ALL passes (small h11)
""")
    parser.add_argument('--h11', type=int, nargs='+', required=True,
                        help='h¹¹ values to scan (space-separated)')
    parser.add_argument('-w', '--workers', type=int,
                        default=max(1, mp.cpu_count() - 1),
                        help=f'Parallel workers (default: {max(1, mp.cpu_count()-1)})')
    parser.add_argument('--top', type=int, default=200,
                        help='Max polytopes for deep analysis (0=all, default: 200)')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from checkpoint')
    parser.add_argument('--skip-t025', action='store_true',
                        help='Skip T0.25, use existing CSV (--t025-csv)')
    parser.add_argument('--t025-csv', type=str, default=None,
                        help='Path to existing T0.25 CSV')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    # Run for each h11
    all_results = {}
    for h in args.h11:
        # Look for existing T0.25 CSV if skip_t025 but no explicit path
        t025_path = args.t025_csv
        if args.skip_t025 and not t025_path:
            default_path = RESULTS_DIR / f"tier025_h{h}.csv"
            if default_path.exists():
                t025_path = str(default_path)
            else:
                # Also try scan_h{h}.csv
                alt_path = RESULTS_DIR / f"scan_h{h}.csv"
                if alt_path.exists():
                    t025_path = str(alt_path)

        results = run_pipeline(
            h11=h,
            workers=args.workers,
            top_n=args.top,
            skip_t025=args.skip_t025,
            resume=args.resume,
            t025_csv=t025_path,
            verbose=args.verbose,
        )
        if results:
            all_results[h] = results

    # Multi-h11 summary
    if len(all_results) > 1:
        print(f"\n{'═'*72}")
        print(f"  {BOLD}MULTI-H11 SUMMARY{RESET}")
        print(f"{'═'*72}")
        for h, results in sorted(all_results.items()):
            n26 = sum(1 for r in results if r.get('score', 0) == 26)
            nsm = sum(1 for r in results if r.get('has_SM'))
            mc = max((r.get('n_clean', 0) for r in results), default=0)
            print(f"  h¹¹={h:3d}: {len(results):5d} analyzed, "
                  f"{n26:4d}×26/26, {nsm:4d} SM, max_clean={mc}")
        print(f"{'═'*72}\n")


if __name__ == '__main__':
    main()
