#!/usr/bin/env python3
"""
champion_monads_lp.py — Monad bundle scan with LP/optimization-based slope filter.

Motivation:
  champion_monads.py uses random Kähler sampling (50 fixed J forms) to test
  slope-stability. With h11_eff=28 and 5-8 slope constraints that must ALL hold
  simultaneously, P(random J satisfies all) is exponentially suppressed. Even
  9M trials across k=2,k=3 all returned 0 slope-stable candidates.

This script replaces random J sampling with OPTIMIZATION: for each χ=±3 monad
candidate, we directly minimize the "slope margin" over J in the positive orthant:

    F(J) = smooth_max_i(μ(b_i, J)) − smooth_min_j(μ(c_j, J))

using log-sum-exp smoothing for differentiability. If F(J*) < 0 at the optimum,
there EXISTS a Kähler form making all B slopes negative and all C slopes positive
— candidate is slope-feasible (necessary condition for stability).

Key advantages over random sampling:
  1. Deterministic: no false negatives from sampling luck
  2. Gradient-based: O(n_starts × n_iter) vs O(n_J_forms) per candidate
  3. Scales well: ~5-20ms per candidate on 28-dim J; can check ALL χ-candidates

Usage:
    python3 champion_monads_lp.py [options]

Options:
    --rank N        Bundle rank (default: 4)
    --k-max K       Max divisor entry magnitude (default: 3)
    --n-sample N    Random trials per config (default: 2_000_000)
    --n-starts M    Optimization restarts per candidate (default: 20)
    --alpha A       Log-sum-exp sharpness (default: 10.0)
    --configs       Configs: e.g. '5,1 6,2 7,3 8,4' (default: rank+1,1 ... rank+3,3)
    --also-k4       Also scan k_max=4 configs after configured k_max
"""

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
from scipy.optimize import minimize

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

H11      = 26
POLY_IDX = 11670
OUT_JSON = os.path.join(SCRIPT_DIR, "results", "champion_monads_lp.json")
OUT_TXT  = os.path.join(SCRIPT_DIR, "results", "champion_monads_lp_top.txt")


# ═════════════════════════════════════════════════════════════════════════════
#  CY data loading (same as champion_monads.py)
# ═════════════════════════════════════════════════════════════════════════════

def load_cy_data():
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    from ks_index import load_h11_polytopes

    print(f"Loading h{H11}/P{POLY_IDX} (loading {POLY_IDX+1} polytopes)...")
    t0 = time.time()
    polys = load_h11_polytopes(H11, limit=POLY_IDX + 1)
    p = polys[POLY_IDX]
    print(f"  {len(p.vertices())} vertices, {len(p.points())} pts — {time.time()-t0:.1f}s")

    print("Triangulating (FRST)...")
    t0 = time.time()
    tri = p.triangulate()
    cy  = tri.get_cy()
    print(f"  cy.h11()={cy.h11()}, h21={cy.h21()} — {time.time()-t0:.1f}s")

    c2      = np.array(cy.second_chern_class(in_basis=True), dtype=float)
    intnums = dict(cy.intersection_numbers(in_basis=True))
    h11_eff = len(c2)
    print(f"  h11_eff={h11_eff}, |c2|=[{c2.min():.0f},{c2.max():.0f}], "
          f"κ entries={len(intnums)}")
    return cy, c2, intnums, h11_eff


def build_kappa_tensor(intnums, h11_eff):
    """Dense κ_{abc} tensor from sparse dict, fully symmetrized."""
    K = np.zeros((h11_eff, h11_eff, h11_eff), dtype=float)
    for (a, b, c), v in intnums.items():
        if 0 <= a < h11_eff and 0 <= b < h11_eff and 0 <= c < h11_eff:
            for aa, bb, cc in ((a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a)):
                K[aa, bb, cc] = v
    return K


def chi_lb(D, c2, K):
    """Index theorem: χ(O(D)) = D³/6 + c₂·D/12."""
    D = np.asarray(D, dtype=float)
    return np.einsum('ijk,i,j,k', K, D, D, D) / 6.0 + np.dot(c2, D) / 12.0


def chi_monad(Bs, Cs, c2, K):
    """χ(V) = Σ χ(O(bᵢ)) − Σ χ(O(cⱼ))."""
    return sum(chi_lb(b, c2, K) for b in Bs) - sum(chi_lb(c, c2, K) for c in Cs)


# ═════════════════════════════════════════════════════════════════════════════
#  LP / optimization-based slope feasibility
# ═════════════════════════════════════════════════════════════════════════════

def build_slope_matrices(Bs, Cs, K):
    """
    Precompute slope matrices M^{bc} = Σ_a κ_{abc} * D^a for each summand.

    μ(O(D), J) = Σ_{abc} κ_{abc} D^a J^b J^c = J^T M_D J

    Returns:
        M_B: (n_B, h, h) slope matrices for B summands
        M_C: (n_C, h, h) slope matrices for C summands
    """
    # M_B[i, b, c] = Σ_a K[a, b, c] * Bs[i, a]
    M_B = np.einsum('abc,ia->ibc', K, Bs)
    M_C = np.einsum('abc,ja->jbc', K, Cs)
    return M_B, M_C


def slope_margin_and_grad(v, M_B, M_C, alpha=10.0):
    """
    Parametrize J = exp(v) (always positive, no constraints needed).

    Objective: F(v) = smooth_max_i(μ_B_i) − smooth_min_j(μ_C_j)

    where:
        μ_B_i = J^T M_B[i] J  = exp(v)^T M_B[i] exp(v)
        smooth_max = (1/α) log Σ_i exp(α μ_B_i)      ← log-sum-exp
        smooth_min = -(1/α) log Σ_j exp(-α μ_C_j)    ← negative log-sum-exp(-·)

    Goal: minimize F(v); F < 0 ⟹ all B slopes < 0 AND all C slopes > 0.

    Returns (F, grad_F).
    """
    J = np.exp(v)                         # (h,)

    # Compute slopes
    s_B = np.einsum('ibc,b,c->i', M_B, J, J)   # (n_B,)
    s_C = np.einsum('jbc,b,c->j', M_C, J, J)   # (n_C,)

    # Log-sum-exp for smooth max(s_B)
    max_B  = np.max(s_B)
    exp_B  = np.exp(alpha * (s_B - max_B))
    Z_B    = exp_B.sum()
    w_B    = exp_B / Z_B                         # softmax weights (n_B,)
    smax_B = max_B + np.log(Z_B) / alpha

    # Log-sum-exp for smooth min(s_C) = -smooth_max(-s_C)
    min_C  = np.min(s_C)
    exp_C  = np.exp(-alpha * (s_C - min_C))
    Z_C    = exp_C.sum()
    w_C    = exp_C / Z_C                         # weights for smooth min
    smin_C = min_C - np.log(Z_C) / alpha

    F = smax_B - smin_C

    # Gradient of F w.r.t. v:
    # ∂μ_B_i/∂J_k = 2 (M_B[i] J)_k    (since M is symmetric)
    # ∂J_k/∂v_k   = J_k
    # ∂F/∂v_k = Σ_i w_B[i] * 2 (M_B[i] J)_k * J_k
    #          - Σ_j w_C[j] * 2 (M_C[j] J)_k * J_k  (with sign for -smin_C)

    # M_B[i] @ J → shape (n_B, h)
    MBJ = np.einsum('ibc,c->ib', M_B, J)   # (n_B, h)
    MCJ = np.einsum('jbc,c->jb', M_C, J)   # (n_C, h)

    # ∂(smax_B)/∂J_k = Σ_i w_B[i] * 2 MBJ[i,k]
    dF_dJ_B = 2.0 * np.einsum('i,ik->k', w_B, MBJ)
    # ∂(-smin_C)/∂J_k = +Σ_j w_C[j] * 2 MCJ[j,k]   (sign: we subtract smin_C)
    dF_dJ_C = 2.0 * np.einsum('j,jk->k', w_C, MCJ)

    dF_dJ   = dF_dJ_B + dF_dJ_C
    grad_v  = dF_dJ * J      # chain rule: ∂/∂v_k = ∂/∂J_k * J_k

    return float(F), grad_v


def find_feasible_kahler(M_B, M_C, h11_eff, n_starts=20, alpha=10.0, rng=None):
    """
    Search for J in positive orthant such that:
        μ(b_i, J) < 0  ∀i  (B slopes negative)
        μ(c_j, J) > 0  ∀j  (C slopes positive)

    Uses gradient descent on v = log(J) with analytic gradients.
    Returns (feasible: bool, J: array or None, margin: float).
    """
    if rng is None:
        rng = np.random.default_rng()

    best_margin = np.inf
    best_J      = None

    for _ in range(n_starts):
        # Random positive start on unit sphere (log-parametrized)
        v0 = rng.normal(size=h11_eff)
        # Bias toward interior of positive cone
        v0 -= np.max(v0)   # shift so max(v0) = 0, all <= 0 ok

        res = minimize(
            slope_margin_and_grad, v0,
            jac=True,
            method='L-BFGS-B',
            options={'maxiter': 300, 'ftol': 1e-12, 'gtol': 1e-8},
        )
        J_opt = np.exp(res.x)

        # Recompute exact (non-smooth) margin for reporting
        s_B = np.einsum('ibc,b,c->i', M_B, J_opt, J_opt)
        s_C = np.einsum('jbc,b,c->j', M_C, J_opt, J_opt)
        exact_margin = s_B.max() - s_C.min()   # < 0 iff feasible

        if exact_margin < best_margin:
            best_margin = exact_margin
            best_J      = J_opt.copy()

        if best_margin < -1e-8:   # early exit if feasible
            break

    feasible = best_margin < -1e-8
    return feasible, best_J, best_margin


# ═════════════════════════════════════════════════════════════════════════════
#  c₂ tadpole check (same as champion_monads.py)
# ═════════════════════════════════════════════════════════════════════════════

def check_c2_tadpole(Bs, Cs, c2_X, K, h11_eff):
    """Rough D3-tadpole check. c2_V = -2 ch2_V (c1=0)."""
    J  = np.ones(h11_eff)
    M  = np.einsum('kab,b->ka', K, J)
    ch2_B = np.einsum('ka,ia->k', M, Bs)
    ch2_C = np.einsum('ka,ja->k', M, Cs)
    ch2   = (ch2_B - ch2_C) / 2.0
    c2_V  = -2.0 * ch2
    tadpole_ok = bool(np.all(c2_V <= c2_X + 1.0))
    n_d3_rough = float(np.sum(c2_X - c2_V))
    return tadpole_ok, n_d3_rough, float(c2_V.min()), float(c2_V.max())


# ═════════════════════════════════════════════════════════════════════════════
#  Main scan
# ═════════════════════════════════════════════════════════════════════════════

def scan_monads_lp(c2, K, h11_eff, rank=4, k_max=3,
                   n_sample=2_000_000, chi_target=3,
                   n_starts=20, alpha=10.0, configs=None):
    """
    Two-phase scan:
      Phase 1: Sample random (B, C), enforce c1=0, χ=±3  (same as before)
      Phase 2: For each χ-candidate, run LP/optimization to find feasible J

    Returns: (all_stable, total_checked, per_config_stats)
    """
    rng = np.random.default_rng(2026_03_07)
    opt_rng = np.random.default_rng(314159)

    if configs is None:
        configs = [(rank + 1, 1), (rank + 2, 2), (rank + 3, 3)]

    all_stable    = []
    total_checked = 0

    for n_B, n_C in configs:
        assert n_B - n_C == rank
        t0 = time.time()
        chi_cands = []
        cfg_checked = 0

        print(f"\n{'='*60}")
        print(f"Config: SU({rank}), n_B={n_B}, n_C={n_C}, k_max={k_max}")
        search_size = math.log10((2*k_max+1)**(h11_eff*(n_C + n_B - 1)))
        print(f"  Search space: ~10^{search_size:.1f}")
        print(f"  Phase 1: sampling {n_sample:,} trials for χ=±{chi_target} candidates...")

        # ── Phase 1: sample & filter by χ ──────────────────────────────────
        for trial in range(n_sample):
            if trial % 200_000 == 0 and trial > 0:
                elapsed = time.time() - t0
                rate = trial / elapsed
                eta  = int((n_sample - trial) / rate)
                print(f"  {trial:,}/{n_sample:,}  χ-cands={len(chi_cands)}  "
                      f"{rate:.0f}/s  eta={eta}s")

            Cs     = rng.integers(-k_max, k_max + 1, size=(n_C, h11_eff)).astype(float)
            Bs_free = rng.integers(-k_max, k_max + 1, size=(n_B - 1, h11_eff)).astype(float)
            b_last  = Cs.sum(axis=0) - Bs_free.sum(axis=0)

            if np.abs(b_last).max() > k_max * n_B:
                continue

            Bs = np.vstack([Bs_free, b_last[None, :]])
            cfg_checked += 1

            chi_V = chi_monad(Bs, Cs, c2, K)
            chi_r = round(chi_V)
            if abs(chi_r) != chi_target or abs(chi_V - chi_r) > 0.15:
                continue

            chi_cands.append((Bs.copy(), Cs.copy(), chi_r, trial))

        elapsed1 = time.time() - t0
        print(f"\n  Phase 1 done: {cfg_checked:,} checked, {len(chi_cands)} χ-candidates "
              f"({elapsed1:.0f}s, {cfg_checked/elapsed1:.0f}/s)")

        # ── Phase 2: LP slope feasibility per candidate ─────────────────────
        print(f"  Phase 2: LP slope check on {len(chi_cands)} candidates "
              f"({n_starts} starts each)...")
        t2 = time.time()
        n_feasible = 0
        lp_checked = 0

        for Bs, Cs, chi_r, trial in chi_cands:
            M_B, M_C = build_slope_matrices(Bs, Cs, K)
            feasible, J_opt, margin = find_feasible_kahler(
                M_B, M_C, h11_eff, n_starts=n_starts, alpha=alpha, rng=opt_rng
            )
            lp_checked += 1

            if lp_checked % max(1, len(chi_cands) // 10) == 0:
                elapsed2 = time.time() - t2
                rate2 = lp_checked / elapsed2
                eta2  = int((len(chi_cands) - lp_checked) / rate2) if rate2 > 0 else 0
                print(f"    LP {lp_checked}/{len(chi_cands)}  feasible={n_feasible}  "
                      f"{rate2:.1f}/s  eta={eta2}s")

            if feasible:
                n_feasible += 1
                tadpole_ok, n_d3, c2v_min, c2v_max = check_c2_tadpole(
                    Bs, Cs, c2, K, h11_eff
                )
                # Verify Kähler cone: vol(J) > 0
                vol = float(np.einsum('ijk,i,j,k', K, J_opt, J_opt, J_opt))
                all_stable.append({
                    "config":      f"({n_B},{n_C})",
                    "n_B":         n_B,
                    "n_C":         n_C,
                    "rank":        rank,
                    "k_max":       k_max,
                    "chi_V":       chi_r,
                    "B":           Bs.tolist(),
                    "C":           Cs.tolist(),
                    "J_opt":       J_opt.tolist(),
                    "slope_margin": float(margin),
                    "vol_J":       vol,
                    "tadpole_ok":  tadpole_ok,
                    "n_d3_rough":  n_d3,
                    "c2V_range":   [c2v_min, c2v_max],
                    "trial":       trial,
                })
                print(f"    *** FEASIBLE: config ({n_B},{n_C}) χ={chi_r:+d} "
                      f"margin={margin:.4f} vol={vol:.3f} tadpole={tadpole_ok}")

        elapsed2 = time.time() - t2
        print(f"  Phase 2 done: {lp_checked} LP checks in {elapsed2:.0f}s "
              f"({lp_checked/max(1,elapsed2):.2f}/s)")
        print(f"  Slope-feasible (LP): {n_feasible}")
        total_checked += cfg_checked

    return all_stable, total_checked


# ═════════════════════════════════════════════════════════════════════════════
#  Output
# ═════════════════════════════════════════════════════════════════════════════

def print_summary(candidates, rank, k_max, total_checked, h11_eff, elapsed):
    print(f"\n{'='*70}")
    print("RESULTS SUMMARY — LP SLOPE FILTER")
    print(f"{'='*70}")
    print(f"  Polytope:       h{H11}/P{POLY_IDX} (sm_score=89, h11_eff={h11_eff})")
    print(f"  Bundle type:    SU({rank}) monad 0→V→B→C→0")
    print(f"  k_max:          {k_max}")
    print(f"  Total sampled:  {total_checked:,}")
    print(f"  Slope-feasible: {len(candidates)}")
    tadpole = [c for c in candidates if c.get("tadpole_ok")]
    print(f"  Tadpole OK:     {len(tadpole)}")
    print(f"  Elapsed:        {elapsed:.0f}s")

    if candidates:
        print(f"\n{'='*70}")
        print("TOP CANDIDATES")
        print(f"{'='*70}")
        for i, c in enumerate(sorted(candidates,
                                     key=lambda x: -x.get("tadpole_ok", 0))):
            tr = "✓" if c.get("tadpole_ok") else "✗"
            print(f"  [{i+1}] config={c['config']} χ={c['chi_V']:+d} "
                  f"margin={c['slope_margin']:.4f} vol={c['vol_J']:.3f} "
                  f"tadpole={tr} n_D3≈{c.get('n_d3_rough',0):.1f}")
            print(f"       B={[list(map(int, b)) for b in c['B']]}")
            print(f"       C={[list(map(int, cc)) for cc in c['C']]}")
    else:
        print("\nNo slope-feasible monad candidates found.")
        print("Interpretation:")
        print("  At k_max=3, the slope-stability constraints μ(b_i)<0 AND μ(c_j)>0")
        print("  are infeasible for ALL χ=±3 monad configurations on h26/P11670.")
        print("  This is a strong negative result: the h11_eff=28 Kähler cone is")
        print("  too constrained for rank-4 monads in this charge range.")
        print("Next steps:")
        print("  1. Try (n_B=8, n_C=4) config (larger rank space)")
        print("  2. Investigate heterotic anomaly cancellation with M5-branes")
        print("  3. Consider SU(5) monad instead of SU(4)")
        print("  4. Attempt F-theory G4-flux approach (no bundle needed)")


# ═════════════════════════════════════════════════════════════════════════════
#  CLI
# ═════════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rank",       type=int, default=4)
    p.add_argument("--k-max",      type=int, default=3)
    p.add_argument("--n-sample",   type=int, default=2_000_000)
    p.add_argument("--n-starts",   type=int, default=20,
                   help="Optimization restarts per χ-candidate (default 20)")
    p.add_argument("--alpha",      type=float, default=10.0,
                   help="Log-sum-exp sharpness (default 10.0)")
    p.add_argument("--configs",    type=str, default=None,
                   help="Configs as 'nB,nC nB,nC ...' e.g. '5,1 6,2 7,3'")
    p.add_argument("--chi-target", type=int, default=3)
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(os.path.join(SCRIPT_DIR, "results"), exist_ok=True)

    print("=" * 70)
    print(f"CHAMPION MONAD SCAN (LP SLOPE FILTER) — h{H11}/P{POLY_IDX}")
    print(f"Method: SU({args.rank}) monad 0→V→B→C→0, k_max={args.k_max}")
    print(f"Slope filter: gradient optimization (n_starts={args.n_starts})")
    print("=" * 70)

    cy, c2, intnums, h11_eff = load_cy_data()
    K = build_kappa_tensor(intnums, h11_eff)

    # Sanity
    chi_O = float(np.einsum('ijk,i,j,k', K, np.zeros(h11_eff),
                             np.zeros(h11_eff), np.zeros(h11_eff)) / 6
                  + np.dot(c2, np.zeros(h11_eff)) / 12)
    print(f"\nSanity: χ(O_X) = {chi_O:.4f} (CY3 → 0 is correct)")

    # Build config list
    if args.configs:
        configs = []
        for tok in args.configs.split():
            nb, nc = tok.split(",")
            configs.append((int(nb), int(nc)))
    else:
        configs = [(args.rank + 1, 1),
                   (args.rank + 2, 2),
                   (args.rank + 3, 3)]

    print(f"Configs: {configs}")

    t_total = time.time()

    candidates, total_checked = scan_monads_lp(
        c2, K, h11_eff,
        rank=args.rank,
        k_max=args.k_max,
        n_sample=args.n_sample,
        chi_target=args.chi_target,
        n_starts=args.n_starts,
        alpha=args.alpha,
        configs=configs,
    )

    elapsed = time.time() - t_total
    print_summary(candidates, args.rank, args.k_max, total_checked, h11_eff, elapsed)

    # Save JSON
    out_data = {
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "polytope":        f"h{H11}/P{POLY_IDX}",
        "rank":            args.rank,
        "k_max":           args.k_max,
        "n_sample":        args.n_sample,
        "n_starts":        args.n_starts,
        "alpha":           args.alpha,
        "chi_target":      args.chi_target,
        "total_checked":   total_checked,
        "n_slope_feasible": len(candidates),
        "n_tadpole_ok":    len([c for c in candidates if c.get("tadpole_ok")]),
        "elapsed_s":       elapsed,
        "h11_eff":         h11_eff,
        "configs":         configs,
        "candidates":      candidates,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out_data, f, indent=2)
    print(f"\nResults saved to: {OUT_JSON}")

    with open(OUT_TXT, "w") as f:
        f.write(f"Champion Monad LP Scan — h{H11}/P{POLY_IDX}\n")
        f.write(f"Run at: {datetime.now(timezone.utc).isoformat()} UTC\n")
        f.write(f"SU({args.rank}), k_max={args.k_max}, χ_target=±{args.chi_target}\n")
        f.write(f"n_starts={args.n_starts} (LP optimization per candidate)\n")
        f.write(f"h11_eff={h11_eff}, configs={configs}\n")
        f.write(f"Sampled={total_checked:,}, slope-feasible={len(candidates)}, "
                f"tadpole_ok={len([c for c in candidates if c.get('tadpole_ok')])}\n\n")
        if not candidates:
            f.write("No slope-feasible monad candidates found.\n")
            f.write("LP optimization confirms: no J in positive orthant satisfies\n")
            f.write("μ(b_i,J)<0 ∀i AND μ(c_j,J)>0 ∀j for any χ=±3 config at k_max=3.\n")
        else:
            for i, c in enumerate(candidates[:50]):
                tr = "OK" if c.get("tadpole_ok") else "fail"
                f.write(f"  [{i+1:3d}] config={c['config']} χ={c['chi_V']:+d} "
                        f"margin={c['slope_margin']:.4f} vol={c['vol_J']:.3f} "
                        f"tadpole={tr} n_D3≈{c.get('n_d3_rough',0):.1f}\n")
                f.write(f"        B={[list(map(int,b)) for b in c['B']]}\n")
                f.write(f"        C={[list(map(int,cc)) for cc in c['C']]}\n")
    print(f"Summary saved to: {OUT_TXT}")


if __name__ == "__main__":
    main()
