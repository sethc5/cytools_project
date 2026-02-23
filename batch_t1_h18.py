#!/usr/bin/env python3
"""batch_t1_h18.py — Run T1 screening on all h11=18 T0.25 pass candidates.

Reads tier025_h18*.csv files (30K+ polytopes with max_h0>=1),
runs fast T1 checks (del Pezzo classification + Swiss cheese + symmetry)
on all favorable polytopes in parallel.

Uses the "fast path" — max_h0 is already known from T0.25 scan, so
we skip the expensive bundle recomputation.

~2-5s per polytope × 30K / 14 workers ≈ 1-2 hours on Hetzner.

Usage:
    python3 batch_t1_h18.py [--min-h0 3] [--workers 14] [--resume]
    python3 batch_t1_h18.py --all          # include non-favorable too
"""

import csv
import sys
import os
import argparse
import time
import concurrent.futures
import signal

import cytools as cy
import numpy as np
from cytools.config import enable_experimental_features
enable_experimental_features()

# ══════════════════════════════════════════════════════════════════
#  Input CSVs
# ══════════════════════════════════════════════════════════════════

T025_CSVS = [
    "results/tier025_h18.csv",
    "results/tier025_h18_off100000.csv",
]

OUT_CSV = "results/tier1_h18.csv"

FIELDNAMES = [
    'h11', 'h21', 'poly_idx', 'favorable', 'h11_eff',
    'max_h0_025', 'n_chi3_025',
    'n_dp', 'dp_types', 'n_k3_div', 'n_rigid',
    'has_swiss', 'n_swiss', 'best_swiss_tau', 'best_swiss_ratio',
    'sym_order',
    'screen_score', 'elapsed', 'status', 'error',
]

PASS_sym = "\033[92m✓\033[0m"
FAIL_sym = "\033[91m✗\033[0m"
STAR_sym = "\033[93m★\033[0m"
BOLD     = "\033[1m"
RESET    = "\033[0m"


# ══════════════════════════════════════════════════════════════════
#  Load candidates
# ══════════════════════════════════════════════════════════════════

def load_candidates(min_h0=3, include_nonfav=False):
    seen = set()
    candidates = []
    for csv_path in T025_CSVS:
        if not os.path.exists(csv_path):
            print(f"  [warn] Not found: {csv_path}", flush=True)
            continue
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                if row['status'] != 'pass':
                    continue
                poly_idx = int(row['poly_idx'])
                if poly_idx in seen:
                    continue
                seen.add(poly_idx)
                max_h0 = int(row['max_h0'])
                if max_h0 < min_h0:
                    continue
                favorable = row['favorable'] == 'True'
                if not favorable and not include_nonfav:
                    continue
                candidates.append({
                    'h11': int(row['h11']),
                    'h21': int(row['h21']),
                    'poly_idx': poly_idx,
                    'favorable': favorable,
                    'h11_eff': int(row['h11_eff']),
                    'max_h0_025': max_h0,
                    'n_chi3_025': int(row['n_chi3']),
                })
    # Sort by max_h0 desc — screens best candidates first
    candidates.sort(key=lambda x: (-x['max_h0_025'], x['poly_idx']))
    return candidates


# ══════════════════════════════════════════════════════════════════
#  T1 screen for a single polytope
# ══════════════════════════════════════════════════════════════════

def screen_poly(cand):
    h11     = cand['h11']
    h21     = cand['h21']
    poly_idx = cand['poly_idx']
    t0 = time.time()

    result = dict(cand)
    result.update({
        'n_dp': 0, 'dp_types': '', 'n_k3_div': 0, 'n_rigid': 0,
        'has_swiss': False, 'n_swiss': 0,
        'best_swiss_tau': '', 'best_swiss_ratio': '',
        'sym_order': 1,
        'screen_score': 0, 'elapsed': 0.0,
        'status': 'FAIL', 'error': '',
    })

    try:
        # ── Fetch + triangulate ──
        polys = list(cy.fetch_polytopes(
            h11=h11, h21=h21, lattice='N',
            limit=max(poly_idx + 5, 100)
        ))
        if poly_idx >= len(polys):
            result['error'] = f'idx_oob ({len(polys)})'
            result['elapsed'] = time.time() - t0
            return result

        p = polys[poly_idx]
        tri = p.triangulate()
        cyobj = tri.get_cy()

        pts = np.array(p.points(), dtype=int)
        n_toric = pts.shape[0]
        div_basis = [int(x) for x in cyobj.divisor_basis()]
        h11_eff = len(div_basis)

        intnums = dict(cyobj.intersection_numbers(in_basis=True))
        c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

        if len(c2) != h11_eff:
            result['error'] = 'c2_mismatch'
            result['elapsed'] = time.time() - t0
            return result

        # ── CHECK 1: Divisor classification (dP + K3-like) ──
        dp_divisors = []
        k3_divisors = []
        rigid_count = 0
        for a_idx in range(h11_eff):
            D3  = intnums.get((a_idx, a_idx, a_idx), 0)
            c2D = c2[a_idx]
            if D3 > 0 and c2D > 0:
                dp_n = 9 - int(D3)
                if 0 <= dp_n <= 8:
                    dp_divisors.append(f"dP{dp_n}")
                rigid_count += 1
            elif D3 == 0 and float(c2D) > 0:
                k3_divisors.append(a_idx)
            else:
                rigid_count += 1

        result['n_dp']     = len(dp_divisors)
        result['dp_types'] = "|".join(dp_divisors)
        result['n_k3_div'] = len(k3_divisors)
        result['n_rigid']  = rigid_count

        # ── CHECK 2: Swiss cheese ──
        try:
            kc  = cyobj.toric_kahler_cone()
            tip = np.array(kc.tip_of_stretched_cone(1.0), dtype=float)
            s   = 10
            swiss_hits = []
            for a_small in range(h11_eff):
                t2 = tip * s
                t2[a_small] = tip[a_small]
                V2  = sum(val * t2[i]*t2[j]*t2[k]
                          for (i,j,k), val in intnums.items()) / 6.0
                tau2 = sum(val * t2[j]*t2[k]
                           for (i,j,k), val in intnums.items()
                           if a_small in (i,j,k)) / 2.0
                if V2 > 100 and tau2 > 0:
                    ratio = tau2 / V2**(2/3)
                    if ratio < 0.1:
                        swiss_hits.append((tau2, V2, ratio))

            result['has_swiss'] = len(swiss_hits) > 0
            result['n_swiss']   = len(swiss_hits)
            if swiss_hits:
                best = min(swiss_hits, key=lambda x: x[2])
                result['best_swiss_tau']   = f"{best[0]:.1f}"
                result['best_swiss_ratio'] = f"{best[2]:.5f}"
        except Exception as e:
            result['error'] = f'swiss:{str(e)[:60]}'

        # ── CHECK 3: Symmetry order ──
        try:
            # Use SIGALRM to bound automorphism computation to 8s
            def _timeout_handler(signum, frame):
                raise TimeoutError("automorphisms timeout")
            old = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(8)
            try:
                auts = p.automorphisms()
                sym_order = len(auts)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old)
            result['sym_order'] = sym_order
        except Exception:
            result['sym_order'] = -1   # timed out or failed

        # ── Score ──
        score = 0
        h0 = cand['max_h0_025']
        if h0 >= 10:   score += 15
        elif h0 >= 5:  score += 10
        elif h0 >= 3:  score += 6

        score += min(result['n_dp'], 5) * 2
        score += 10 if result['has_swiss'] else 0
        sym = result['sym_order']
        if sym > 1:
            score += min(sym - 1, 5)

        result['screen_score'] = score
        result['elapsed'] = time.time() - t0
        result['status']  = 'ok'

    except Exception as e:
        result['error']   = str(e)[:120]
        result['elapsed'] = time.time() - t0

    return result


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Batch T1 screen for h11=18 T0.25 passes")
    parser.add_argument('--min-h0',  type=int, default=3,
                        help='Minimum max_h0 from T0.25 scan (default: 3)')
    parser.add_argument('--workers', type=int, default=14,
                        help='Parallel workers (default: 14)')
    parser.add_argument('--all', action='store_true',
                        help='Include non-favorable polytopes')
    parser.add_argument('--resume', action='store_true',
                        help='Skip poly_idx already in output CSV')
    args = parser.parse_args()

    candidates = load_candidates(
        min_h0=args.min_h0,
        include_nonfav=getattr(args, 'all', False),
    )

    # Resume: skip already done
    done = set()
    if args.resume and os.path.exists(OUT_CSV):
        with open(OUT_CSV) as f:
            for row in csv.DictReader(f):
                done.add(int(row['poly_idx']))
        before = len(candidates)
        candidates = [c for c in candidates if c['poly_idx'] not in done]
        print(f"  [resume] Skipping {len(done)} done; {len(candidates)} remaining", flush=True)

    print("=" * 72, flush=True)
    print(f"  TIER 1 BATCH SCREEN  h11=18  (T0.25 pass pool)", flush=True)
    print(f"  Candidates : {len(candidates)}  (min_h0>={args.min_h0})", flush=True)
    print(f"  Workers    : {args.workers}", flush=True)
    print(f"  Output     : {OUT_CSV}", flush=True)
    print("=" * 72, flush=True)
    print(f"  {'poly_idx':>8}  {'max_h0':>6}  {'n_dp':>4}  {'swiss':>5}  "
          f"{'sym':>4}  {'score':>5}  {'time':>6}  dp_types", flush=True)
    print(f"  {'-'*8}  {'-'*6}  {'-'*4}  {'-'*5}  {'-'*4}  {'-'*5}  {'-'*6}  --------", flush=True)

    write_header = not (args.resume and os.path.exists(OUT_CSV))
    f_out   = open(OUT_CSV, 'a' if args.resume else 'w', newline='')
    writer  = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
    if write_header:
        writer.writeheader()

    t_global = time.time()
    n_done   = 0
    n_swiss  = 0
    n_dp3    = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(screen_poly, c): c for c in candidates}
        for fut in concurrent.futures.as_completed(futs):
            try:
                r = fut.result()
            except Exception as e:
                c = futs[fut]
                r = dict(c)
                r.update({'status': 'exc', 'error': str(e)[:80], 'elapsed': 0.0,
                           'n_dp': 0, 'dp_types': '', 'n_k3_div': 0, 'n_rigid': 0,
                           'has_swiss': False, 'n_swiss': 0,
                           'best_swiss_tau': '', 'best_swiss_ratio': '',
                           'sym_order': -1, 'screen_score': 0})

            n_done += 1
            if r.get('has_swiss'):   n_swiss += 1
            if r.get('n_dp', 0) >= 3: n_dp3  += 1

            row = {k: r.get(k, '') for k in FIELDNAMES}
            writer.writerow(row)
            f_out.flush()

            swiss_tag = STAR_sym if r.get('has_swiss') else '    '
            err_note  = f"  ERR:{r['error'][:35]}" if r.get('error') else ''
            dp_str    = r.get('dp_types', '')[:20]
            print(f"  {r['poly_idx']:>8}  {r['max_h0_025']:>6}  {r['n_dp']:>4}  "
                  f"{swiss_tag}  {r['sym_order']:>4}  {r['screen_score']:>5}  "
                  f"{r['elapsed']:>5.1f}s  {dp_str}{err_note}", flush=True)

    f_out.close()
    elapsed_total = time.time() - t_global

    print(flush=True)
    print("=" * 72, flush=True)
    print(f"  DONE — {n_done} screened in {elapsed_total:.0f}s", flush=True)
    print(f"  Swiss cheese : {n_swiss} ({100*n_swiss/max(n_done,1):.1f}%)", flush=True)
    print(f"  n_dp >= 3    : {n_dp3}  ({100*n_dp3/max(n_done,1):.1f}%)", flush=True)
    print(flush=True)

    # Top 20 by score
    rows = []
    with open(OUT_CSV) as f:
        for row in csv.DictReader(f):
            if row['status'] == 'ok':
                rows.append(row)
    rows.sort(key=lambda r: (-int(r['screen_score']), -int(r['max_h0_025'])))
    print(f"  TOP 20 by screen_score:", flush=True)
    print(f"  {'poly_idx':>8}  {'score':>5}  {'max_h0':>6}  {'n_dp':>4}  "
          f"{'swiss':>5}  {'sym':>4}  dp_types", flush=True)
    for r in rows[:20]:
        swiss = STAR_sym if r['has_swiss'] == 'True' else '    '
        print(f"  {r['poly_idx']:>8}  {r['screen_score']:>5}  {r['max_h0_025']:>6}  "
              f"{r['n_dp']:>4}  {swiss}  {r['sym_order']:>4}  {r['dp_types'][:30]}", flush=True)


if __name__ == '__main__':
    main()
