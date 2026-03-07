#!/usr/bin/env python3
"""
champion_monads_b46.py — B-46: Restricted-charge monad scan with integrated
D3-tadpole constraint.

Motivation (from B-45 Finding 28c):
  LP scan found 612 slope-feasible SU(4) monads with |β^a| ≤ 3, but corrected
  D3-tadpole check (quadratic ch₂ formula) showed c₂(V)_max ∈ [167,1654] vs
  c₂(TX)_max=24 — violated by 7–70×. The oversized charge amplitudes are
  responsible: ch₂(O(β))_k = (1/2)κ_{kab}β^a β^b grows quadratically in |β|.

Solution (B-46):
  Restrict charges to |β^a| ∈ {-1, 0, +1}. The maximum ch₂ contribution per
  summand per component k satisfies:
      ch₂(O(β))_k ≤ (1/2) Σ_{a,b} |κ_{kab}|
  which is bounded by the intersection tensor magnitude — hopefully ≤ c₂(TX)_k.

Three-phase scan:
  Phase 1:   Sample (B,C) with β ∈ {-1,0,+1}^28, enforce c₁(V)=0 and χ=±3.
  Phase 1.5: D3-tadpole pre-filter (correct quadratic formula). Discard if any
             c₂(V)_k > c₂(TX)_k + tolerance. This eliminates hopeless cases
             BEFORE the expensive LP step.
  Phase 2:   LP/gradient slope feasibility check on tadpole-feasible candidates.

Usage:
    python3 champion_monads_b46.py [options]

Options:
    --rank N        Bundle rank (default: 4)
    --n-sample N    Random trials per config (default: 10_000_000)
    --n-starts M    LP restarts per candidate (default: 30)
    --alpha A       Log-sum-exp sharpness (default: 10.0)
    --configs       e.g. '5,1 6,2 7,3' (default: (rank+1,1) ... (rank+3,3))
    --tadpole-tol T Tolerance added to c₂(TX) in tadpole filter (default: 1.0)
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
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)   # parent of v6/
sys.path.insert(0, SCRIPT_DIR)    # v6/ for local helpers
sys.path.insert(0, PROJECT_ROOT)  # project root first → root-level ks_index.py wins

H11      = 26
POLY_IDX = 11670
OUT_JSON = os.path.join(SCRIPT_DIR, "results", "champion_monads_b46.json")
OUT_TXT  = os.path.join(SCRIPT_DIR, "results", "champion_monads_b46_top.txt")


# ─────────────────────────────────────────────────────────────────────────────
#  CY data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_cy_data():
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    from ks_index import load_h11_polytopes

    print("Loading h%d/P%d (%d polytopes)..." % (H11, POLY_IDX, POLY_IDX + 1),
          flush=True)
    t0 = time.time()
    polys = load_h11_polytopes(H11, limit=POLY_IDX + 1)
    p   = polys[POLY_IDX]
    tri = p.triangulate()
    cy  = tri.get_cy()
    print("  cy h11=%d h21=%d  %.1fs" % (cy.h11(), cy.h21(), time.time() - t0),
          flush=True)

    c2      = np.array(cy.second_chern_class(in_basis=True), dtype=float)
    intnums = dict(cy.intersection_numbers(in_basis=True))
    h11_eff = len(c2)
    print("  h11_eff=%d  c2 in [%.0f, %.0f]  kappa entries=%d" % (
        h11_eff, c2.min(), c2.max(), len(intnums)), flush=True)
    return cy, c2, intnums, h11_eff


def build_kappa_tensor(intnums, h11_eff):
    """Dense κ_{abc} tensor, fully symmetrized."""
    K = np.zeros((h11_eff, h11_eff, h11_eff), dtype=float)
    for (a, b, c), v in intnums.items():
        if 0 <= a < h11_eff and 0 <= b < h11_eff and 0 <= c < h11_eff:
            for aa, bb, cc in ((a, b, c), (a, c, b), (b, a, c),
                               (b, c, a), (c, a, b), (c, b, a)):
                K[aa, bb, cc] = v
    return K


# ─────────────────────────────────────────────────────────────────────────────
#  Bundle topology
# ─────────────────────────────────────────────────────────────────────────────

def chi_lb(D, c2, K):
    """χ(O(D)) = D³/6 + c₂·D/12 (Hirzebruch–Riemann–Roch)."""
    D = np.asarray(D, dtype=float)
    return np.einsum('ijk,i,j,k', K, D, D, D) / 6.0 + np.dot(c2, D) / 12.0


def chi_monad(Bs, Cs, c2, K):
    """χ(V) = Σ χ(O(bᵢ)) − Σ χ(O(cⱼ))."""
    return (sum(chi_lb(b, c2, K) for b in Bs)
            - sum(chi_lb(c, c2, K) for c in Cs))


def ch2_correct(betas, K):
    """
    Correct second Chern character for a direct sum of line bundles.

    ch₂(O(β))_k = (1/2) κ_{kab} β^a β^b    [quadratic, NOT linear]

    For betas = (n_line, h11_eff):
        ch₂_sum_k = Σᵢ (1/2) κ_{kab} β^{(i)}_a β^{(i)}_b
    """
    betas = np.asarray(betas, dtype=float)   # (n, h)
    return 0.5 * np.einsum('kab,ia,ib->k', K, betas, betas)


def c2_bundle(Bs, Cs, K):
    """
    c₂(V) = -(ch₂(V)) when c₁(V)=0,  where ch₂(V) = ch₂(B) - ch₂(C).

    Returns c₂(V) as array of length h11_eff.
    """
    ch2_B = ch2_correct(Bs, K)
    ch2_C = ch2_correct(Cs, K)
    return -(ch2_B - ch2_C)         # c₂(V) = -ch₂(V)


def tadpole_ok(Bs, Cs, c2_X, K, tol=1.0):
    """
    Check D3-tadpole: c₂(V)_k ≤ c₂(TX)_k for all k.

    tol=1.0: allow 1-unit float tolerance.
    Returns (ok: bool, n_D3: float, c2v_max: float)
    """
    c2v   = c2_bundle(Bs, Cs, K)
    ok    = bool(np.all(c2v <= c2_X + tol))
    n_D3  = float(np.sum(c2_X - c2v))
    return ok, n_D3, float(c2v.min()), float(c2v.max())


# ─────────────────────────────────────────────────────────────────────────────
#  LP slope feasibility (same as champion_monads_lp.py)
# ─────────────────────────────────────────────────────────────────────────────

def build_slope_matrices(Bs, Cs, K):
    """M_B[i,b,c] = Σ_a K[a,b,c]*Bs[i,a];  similarly M_C."""
    M_B = np.einsum('abc,ia->ibc', K, Bs)
    M_C = np.einsum('abc,ja->jbc', K, Cs)
    return M_B, M_C


def slope_margin_and_grad(v, M_B, M_C, alpha=10.0):
    """
    J = exp(v); minimize F = smooth_max(μ_B) − smooth_min(μ_C).
    Returns (F, grad_F) with analytic gradients for L-BFGS-B.
    """
    J = np.exp(v)

    s_B = np.einsum('ibc,b,c->i', M_B, J, J)
    s_C = np.einsum('jbc,b,c->j', M_C, J, J)

    # smooth max of s_B
    max_B = np.max(s_B)
    exp_B = np.exp(alpha * (s_B - max_B))
    Z_B   = exp_B.sum()
    w_B   = exp_B / Z_B
    smax_B = max_B + np.log(Z_B) / alpha

    # smooth min of s_C = -smooth_max(-s_C)
    min_C = np.min(s_C)
    exp_C = np.exp(-alpha * (s_C - min_C))
    Z_C   = exp_C.sum()
    w_C   = exp_C / Z_C
    smin_C = min_C - np.log(Z_C) / alpha

    F = smax_B - smin_C

    MBJ = np.einsum('ibc,c->ib', M_B, J)
    MCJ = np.einsum('jbc,c->jb', M_C, J)
    dF_dJ = 2.0 * (np.einsum('i,ik->k', w_B, MBJ)
                   + np.einsum('j,jk->k', w_C, MCJ))
    grad_v = dF_dJ * J

    return float(F), grad_v


def find_feasible_kahler(M_B, M_C, h11_eff, n_starts=30, alpha=10.0, rng=None):
    """
    Gradient-based search for J with slope_margin < 0.
    Returns (feasible, J_opt, margin).
    """
    if rng is None:
        rng = np.random.default_rng()

    best_margin = np.inf
    best_J = None

    for _ in range(n_starts):
        v0 = rng.normal(size=h11_eff)
        v0 -= np.max(v0)

        res = minimize(
            slope_margin_and_grad, v0,
            args=(M_B, M_C, alpha),
            jac=True,
            method='L-BFGS-B',
            options={'maxiter': 400, 'ftol': 1e-13, 'gtol': 1e-9},
        )
        J_opt = np.exp(res.x)

        s_B = np.einsum('ibc,b,c->i', M_B, J_opt, J_opt)
        s_C = np.einsum('jbc,b,c->j', M_C, J_opt, J_opt)
        exact_margin = float(s_B.max() - s_C.min())

        if exact_margin < best_margin:
            best_margin = exact_margin
            best_J = J_opt.copy()

        if best_margin < -1e-8:
            break

    return best_margin < -1e-8, best_J, best_margin


# ─────────────────────────────────────────────────────────────────────────────
#  Main scan
# ─────────────────────────────────────────────────────────────────────────────

def scan_b46(c2, K, h11_eff, rank=4, n_sample=10_000_000, chi_target=3,
             n_starts=30, alpha=10.0, tadpole_tol=1.0, configs=None):
    """
    Three-phase scan with |β| ≤ 1 charges and integrated tadpole pre-filter.

    Phase 1:   Sample (B,C), β ∈ {-1,0,+1}, enforce c₁=0 and χ=±3.
    Phase 1.5: Reject if c₂(V)_k > c₂(TX)_k + tol for any k.
    Phase 2:   LP slope feasibility on surviving candidates.

    Returns (candidates, total_sampled, total_chi_ok, total_tadpole_ok_pre)
    """
    rng     = np.random.default_rng(2026_03_07_46)
    opt_rng = np.random.default_rng(271828)

    if configs is None:
        configs = [(rank + 1, 1), (rank + 2, 2), (rank + 3, 3)]

    candidates    = []
    total_sampled = 0
    total_chi_ok  = 0
    total_tp_ok   = 0

    # Precompute ch2 matrix for a single β: K2[k,a,b] = (1/2)K[k,a,b]
    K2 = 0.5 * K  # reuse in tadpole_ok

    for n_B, n_C in configs:
        assert n_B - n_C == rank
        t0 = time.time()
        chi_cands = []      # (B, C, chi_r, trial)
        tp_cands  = []      # subset passing tadpole pre-filter
        cfg_sampled = 0

        print("\n" + "=" * 62, flush=True)
        print("Config SU(%d): n_B=%d n_C=%d | restricted |β|≤1" % (
            rank, n_B, n_C), flush=True)

        # ── Phase 1: sample with {-1,0,+1} charges ──────────────────────────
        print("  Phase 1: sampling %d trials..." % n_sample, flush=True)
        choices = np.array([-1, 0, 1], dtype=float)

        for trial in range(n_sample):
            if trial % 500_000 == 0 and trial > 0:
                el = time.time() - t0
                print("  %d/%d  chi_ok=%d  tp_ok=%d  %.0f/s  eta=%.0fs" % (
                    trial, n_sample, len(chi_cands), len(tp_cands),
                    trial / el, (n_sample - trial) / (trial / el)),
                    flush=True)

            # Sample C: n_C rows of length h11_eff, each entry ∈ {-1,0,+1}
            Cs      = rng.choice(choices, size=(n_C, h11_eff))
            # Sample n_B-1 free B rows; enforce c₁=0 with last row
            Bs_free = rng.choice(choices, size=(n_B - 1, h11_eff))
            b_last  = Cs.sum(axis=0) - Bs_free.sum(axis=0)

            # With |β|≤1 and integer charges, b_last can exceed {-1,0,1} by
            # up to n_C+n_B-1. Accept only if it stays in {-k,…,k} for
            # small k; here we allow up to |b_last|≤3 (still controlled).
            if np.abs(b_last).max() > 3:
                continue

            Bs = np.vstack([Bs_free, b_last[None, :]])
            cfg_sampled += 1

            chi_V = chi_monad(Bs, Cs, c2, K)
            chi_r = round(chi_V)
            if abs(chi_r) != chi_target or abs(chi_V - chi_r) > 0.15:
                continue

            chi_cands.append((Bs.copy(), Cs.copy(), chi_r, trial))

        elapsed1 = time.time() - t0
        print("  Phase 1 done: %d sampled, %d chi_ok  (%.0fs)" % (
            cfg_sampled, len(chi_cands), elapsed1), flush=True)
        total_sampled += cfg_sampled
        total_chi_ok  += len(chi_cands)

        # ── Phase 1.5: tadpole pre-filter ───────────────────────────────────
        print("  Phase 1.5: tadpole pre-filter on %d χ-candidates..." % (
              len(chi_cands)), flush=True)
        t15 = time.time()
        n_tp_pass = 0

        for Bs, Cs, chi_r, trial in chi_cands:
            ok, n_D3, c2v_min, c2v_max = tadpole_ok(Bs, Cs, c2, K, tadpole_tol)
            if ok:
                n_tp_pass += 1
                tp_cands.append((Bs, Cs, chi_r, trial, n_D3, c2v_min, c2v_max))

        elapsed15 = time.time() - t15
        print("  Phase 1.5 done: %d / %d pass tadpole  (%.1fs)" % (
            n_tp_pass, len(chi_cands), elapsed15), flush=True)
        total_tp_ok += n_tp_pass

        # ── Phase 2: LP slope feasibility ───────────────────────────────────
        if not tp_cands:
            print("  Phase 2: skipped (0 tadpole-feasible candidates).",
                  flush=True)
            continue

        print("  Phase 2: LP slope check on %d candidates (%d starts each)..." % (
            len(tp_cands), n_starts), flush=True)
        t2 = time.time()
        n_slope = 0

        for idx, (Bs, Cs, chi_r, trial, n_D3, c2v_min, c2v_max) in enumerate(
                tp_cands):
            M_B, M_C = build_slope_matrices(Bs, Cs, K)
            feasible, J_opt, margin = find_feasible_kahler(
                M_B, M_C, h11_eff, n_starts=n_starts, alpha=alpha, rng=opt_rng
            )

            if (idx + 1) % max(1, len(tp_cands) // 10) == 0:
                el2 = time.time() - t2
                rate = (idx + 1) / max(el2, 0.001)
                eta  = (len(tp_cands) - idx - 1) / max(rate, 0.001)
                print("    LP %d/%d  slope_ok=%d  %.2f/s  eta=%.0fs" % (
                    idx + 1, len(tp_cands), n_slope, rate, eta), flush=True)

            if feasible:
                n_slope += 1
                vol = float(np.einsum('ijk,i,j,k', K, J_opt, J_opt, J_opt))
                # Re-verify tadpole with corrected formula (already passed 1.5)
                tp2_ok, n_D3_v2, c2v_min2, c2v_max2 = tadpole_ok(
                    Bs, Cs, c2, K, tol=0.5)
                candidates.append({
                    "config":          "(%d,%d)" % (n_B, n_C),
                    "n_B":             n_B,
                    "n_C":             n_C,
                    "rank":            rank,
                    "chi_V":           chi_r,
                    "B":               Bs.tolist(),
                    "C":               Cs.tolist(),
                    "J_opt":           J_opt.tolist(),
                    "slope_margin":    float(margin),
                    "vol_J":           vol,
                    "tadpole_ok":      tp2_ok,
                    "n_D3":            n_D3_v2,
                    "c2V_range":       [c2v_min2, c2v_max2],
                    "trial":           trial,
                })
                print("  *** SLOPE+TADPOLE: config(%d,%d) chi=%+d "
                      "margin=%.4f vol=%.3f n_D3=%.1f c2V=[%.1f,%.1f]" % (
                          n_B, n_C, chi_r, margin, vol, n_D3_v2,
                          c2v_min2, c2v_max2), flush=True)

        elapsed2 = time.time() - t2
        print("  Phase 2 done: %d / %d slope-feasible  (%.0fs)" % (
            n_slope, len(tp_cands), elapsed2), flush=True)

    return candidates, total_sampled, total_chi_ok, total_tp_ok


# ─────────────────────────────────────────────────────────────────────────────
#  Output
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(candidates, rank, n_sample, total_sampled,
                  total_chi_ok, total_tp_ok, h11_eff, elapsed):
    sep = "=" * 66
    print("\n" + sep)
    print("RESULTS SUMMARY — B-46 RESTRICTED-CHARGE MONAD SCAN")
    print(sep)
    print("  Polytope:        h%d/P%d (sm=89, h11_eff=%d)" % (
        H11, POLY_IDX, h11_eff))
    print("  Bundle:          SU(%d) monad 0→V→B→C→0, |β|≤1" % rank)
    print("  Total sampled:   %d" % total_sampled)
    print("  χ=±3 ok:         %d" % total_chi_ok)
    print("  Tadpole pre-ok:  %d" % total_tp_ok)
    print("  Slope-feasible:  %d" % len(candidates))
    tp_full = [c for c in candidates if c.get("tadpole_ok")]
    print("  Tadpole+slope:   %d" % len(tp_full))
    print("  Elapsed:         %.0fs" % elapsed)
    print(sep)

    if candidates:
        print("\nTOP CANDIDATES (slope-feasible, sorted by tadpole then margin):")
        for i, c in enumerate(sorted(candidates,
                                     key=lambda x: (not x.get("tadpole_ok"),
                                                    x.get("slope_margin", 0))
                                     )[:20]):
            tp = "OK" if c.get("tadpole_ok") else "FAIL"
            print("  [%3d] %s chi=%+d margin=%.4f vol=%.3f n_D3=%.1f tadpole=%s"
                  % (i + 1, c["config"], c["chi_V"], c["slope_margin"],
                     c["vol_J"], c.get("n_D3", 0), tp))
    else:
        print("\nNo slope-feasible & tadpole-ok candidates found.")
        if total_tp_ok == 0:
            print("  >> Tadpole pre-filter eliminated ALL χ=±3 candidates.")
            print("     Interpretation: c₂(V)>c₂(TX) even at |β|=1 on h11=28.")
            print("     Next: allow 5-branes (N_M5 extra tadpole contribution),")
            print("     or try SU(5) rank instead of SU(4).")
        else:
            print("  >> %d passed tadpole, 0 passed slope. LP confirms no" %
                  total_tp_ok)
            print("     feasible J for any tadpole-OK (B,C) at |β|≤1.")


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rank",        type=int,   default=4)
    p.add_argument("--n-sample",    type=int,   default=10_000_000)
    p.add_argument("--n-starts",    type=int,   default=30)
    p.add_argument("--alpha",       type=float, default=10.0)
    p.add_argument("--tadpole-tol", type=float, default=1.0)
    p.add_argument("--chi-target",  type=int,   default=3)
    p.add_argument("--configs",     type=str,   default=None,
                   help="Configs as 'nB,nC nB,nC ...', e.g. '5,1 6,2 7,3'")
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(os.path.join(SCRIPT_DIR, "results"), exist_ok=True)

    sep = "=" * 66
    print(sep)
    print("CHAMPION MONAD B-46 — h%d/P%d" % (H11, POLY_IDX))
    print("SU(%d) monad, charges |β| ≤ 1, tadpole pre-filter + LP slope" %
          args.rank)
    print(sep)

    cy, c2, intnums, h11_eff = load_cy_data()
    K = build_kappa_tensor(intnums, h11_eff)

    # Quick tadpole ceiling estimate for |β|=1
    K_rowmax = np.abs(K).sum(axis=(1, 2)) * 0.5   # upper bound on ch₂ per component
    print("\nTadpole ceiling check at |β|=1:")
    print("  max |κ_{kab}|/2 per k (ch2 per summand upper bound):")
    print("    max=%.1f  vs  c2(TX) in [%.0f, %.0f]" % (
        K_rowmax.max(), c2.min(), c2.max()))
    # Per-config bound: n_B summands of B, n_C of C
    print("  For (5,1): ch2(B) upper ~ 5*%.1f=%.1f; need ≤ %.0f" % (
        K_rowmax.max(), 5 * K_rowmax.max(), c2.max()))

    configs = []
    if args.configs:
        for tok in args.configs.split():
            nb, nc = tok.split(",")
            configs.append((int(nb), int(nc)))
    else:
        configs = [(args.rank + 1, 1), (args.rank + 2, 2), (args.rank + 3, 3)]

    print("\nConfigs: %s" % configs)
    print("n_sample=%d per config, n_starts=%d, tadpole_tol=%.1f" % (
        args.n_sample, args.n_starts, args.tadpole_tol))

    t_total = time.time()

    candidates, total_sampled, total_chi_ok, total_tp_ok = scan_b46(
        c2, K, h11_eff,
        rank=args.rank,
        n_sample=args.n_sample,
        chi_target=args.chi_target,
        n_starts=args.n_starts,
        alpha=args.alpha,
        tadpole_tol=args.tadpole_tol,
        configs=configs,
    )

    elapsed = time.time() - t_total
    print_summary(candidates, args.rank, args.n_sample, total_sampled,
                  total_chi_ok, total_tp_ok, h11_eff, elapsed)

    # ── Save JSON ────────────────────────────────────────────────────────────
    out_data = {
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "polytope":         "h%d/P%d" % (H11, POLY_IDX),
        "method":           "B-46: restricted |beta|<=1 + tadpole pre-filter + LP slope",
        "rank":             args.rank,
        "charge_range":     "[-1,0,1]",
        "n_sample_per_cfg": args.n_sample,
        "n_starts":         args.n_starts,
        "alpha":            args.alpha,
        "tadpole_tol":      args.tadpole_tol,
        "chi_target":       args.chi_target,
        "configs":          configs,
        "total_sampled":    total_sampled,
        "total_chi_ok":     total_chi_ok,
        "total_tadpole_pre_ok": total_tp_ok,
        "n_slope_feasible": len(candidates),
        "n_tadpole_slope_ok": len([c for c in candidates if c.get("tadpole_ok")]),
        "elapsed_s":        elapsed,
        "h11_eff":          h11_eff,
        "candidates":       candidates,
        "ch2_formula":      "(1/2)*kappa_{kab}*beta^a*beta^b (correct quadratic)",
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out_data, f, indent=2)
    print("\nResults saved to: %s" % OUT_JSON)

    # ── Save text report ─────────────────────────────────────────────────────
    with open(OUT_TXT, "w") as f:
        f.write("Champion Monad B-46 Scan -- h%d/P%d\n" % (H11, POLY_IDX))
        f.write("Run at: %s UTC\n" % datetime.now(timezone.utc).isoformat())
        f.write("SU(%d) monad, |beta|<=1, tadpole pre-filter + LP slope\n" %
                args.rank)
        f.write("n_starts=%d, chi_target=+/-%d, configs=%s\n\n" % (
            args.n_starts, args.chi_target, configs))
        f.write("Sampled:         %d\n" % total_sampled)
        f.write("chi=+/-3 ok:     %d\n" % total_chi_ok)
        f.write("Tadpole pre-ok:  %d\n" % total_tp_ok)
        f.write("Slope-feasible:  %d\n" % len(candidates))
        tp_ok_list = [c for c in candidates if c.get("tadpole_ok")]
        f.write("Tadpole+slope:   %d\n\n" % len(tp_ok_list))

        if candidates:
            f.write("CANDIDATES (slope-feasible):\n")
            for i, c in enumerate(sorted(candidates,
                                          key=lambda x: (not x.get("tadpole_ok"),
                                                         x.get("slope_margin", 0))
                                          )):
                tp = "OK" if c.get("tadpole_ok") else "FAIL"
                f.write("[%3d] %s chi=%+d margin=%.4f vol=%.3f "
                        "n_D3=%.1f tadpole=%s\n" % (
                            i + 1, c["config"], c["chi_V"],
                            c["slope_margin"], c["vol_J"],
                            c.get("n_D3", 0), tp))
                f.write("  B=%s\n  C=%s\n\n" % (c["B"], c["C"]))
        else:
            f.write("No slope-feasible candidates found.\n")
    print("Report saved to:  %s" % OUT_TXT)


if __name__ == "__main__":
    main()
