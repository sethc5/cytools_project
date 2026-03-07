#!/usr/bin/env python3
"""
monad_scan_top37.py — LP monad bundle scan over all 37 T4-verified top-tier entries.

Generalizes champion_monads_lp.py from h26/P11670 to every entry in the top-37
(sm_score≥80, tier_reached='T4' in cy_landscape_v6.db).

Algorithm
---------
For each entry (h11, poly_idx):
  1. Structural pre-check: compare κ_max vs c2_max. If provably obstructed
     (kappa_max * n_B * k_max^2 / 2 >> c2_max for all k), record quickly and skip LP.
  2. Phase 1: Sample N random SU(4) monad configs (c1=0 by construction),
     filter to χ(V) = ±3 candidates.
  3. Phase 2: Run LP gradient optimization to find J in Kähler cone with
     μ(b_i,J) < 0 ∀i  AND  μ(c_j,J) > 0 ∀j  (slope stability).
  4. For slope-feasible candidates: rough D3 tadpole check.
  5. Save per-entry JSON result; checkpoint/resume so long runs survive restarts.

Priority order: h11_eff=19 entries first (h22/P682, h23/P36, h21/P9085),
then h11_eff=20 (h25/P860), then remaining by ascending h11_eff.

Usage
-----
  python monad_scan_top37.py [--n-sample 500000] [--k-max 3] [--rank 4]
                             [--n-starts 20] [--alpha 10.0]
                             [--skip 26:11670]        # skip specific entries
                             [--only-priority]        # only h11_eff≤20 entries
                             [--structural-only]      # skip LP, just pre-checks
"""

from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from typing import Optional

import numpy as np
from scipy.optimize import minimize

# ─── Paths ─────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
SUMMARY_JSON = os.path.join(RESULTS_DIR, "monad_scan_top37_summary.json")

# ─── Top-37 T4 entries (h11, poly_idx, sm_score, h11_eff, n_clean, has_SM, has_GUT)
# Ordered by h11_eff ascending (priority) then by score descending.
# h26/P11670 is included so the checkpoint logic can record it as "already done".
TOP37: list[tuple[int, int, int, int, int, int, int]] = [
    # (h11, poly_idx, score, h11_eff, n_clean, has_SM, has_GUT)
    # ── h11_eff = 19 (highest priority) ──────────────────────────────────────
    (22, 682,   85, 19, 84, 1, 1),   # PRIORITY-1
    (23, 36,    81, 19, 60, 0, 0),   # PRIORITY-2
    (21, 9085,  80, 19, 66, 0, 0),   # PRIORITY-3
    # ── h11_eff = 20 ─────────────────────────────────────────────────────────
    (25, 860,   81, 20, 24, 1, 1),   # PRIORITY-4
    # ── h11_eff = 22 ─────────────────────────────────────────────────────────
    (24, 868,   87, 22, 24, 1, 1),
    # ── h11_eff = 24 ─────────────────────────────────────────────────────────
    (27, 4102,  87, 24, 22, 1, 1),
    (27, 9192,  87, 24, 22, 1, 1),
    (29, 8423,  87, 24, 30, 1, 1),
    (27, 45013, 85, 24, 12, 1, 1),
    (27, 9133,  85, 24, 22, 1, 1),
    (28, 6642,  85, 24, 30, 1, 1),
    (29, 13253, 83, 24, 20, 1, 1),
    (27, 2317,  82, 24, 24, 1, 1),
    (28, 33,    82, 24, 20, 0, 0),
    (28, 718,   82, 24, 22, 0, 0),
    (28, 5473,  82, 24, 26, 1, 1),
    (27, 39352, 81, 24, 12, 1, 1),
    (27, 27537, 81, 24, 16, 1, 1),
    (28, 33562, 80, 24, 28, 1, 1),
    (28, 1937,  80, 24, 20, 1, 1),
    (29, 6575,  80, 24, 22, 1, 1),
    (29, 6577,  80, 24, 22, 1, 1),
    (27, 26021, 80, 24, 20, 1, 1),
    (27, 28704, 80, 24, 20, 1, 1),
    # ── h11_eff = 25 ─────────────────────────────────────────────────────────
    (25, 8995,  80, 25, 24, 1, 1),
    (25, 18950, 80, 25, 22, 1, 1),
    # ── h11_eff = 26 ─────────────────────────────────────────────────────────
    (24, 272,   80, 26, 24, 0, 0),
    (26, 30513, 80, 26, 22, 1, 1),
    (24, 44004, 80, 27, 26, 1, 1),
    # ── h11_eff = 27 ─────────────────────────────────────────────────────────
    (25, 5449,  80, 27, 26, 1, 1),
    (25, 7867,  81, 27, 18, 1, 1),
    # ── h11_eff = 28 ─────────────────────────────────────────────────────────
    (25, 46481, 85, 28, 22, 1, 1),
    (24, 45873, 85, 26, 22, 1, 1),
    (25, 38242, 80, 28, 24, 1, 1),
    (26, 315,   80, 28, 32, 1, 1),
    (26, 11871, 80, 28, 26, 1, 1),
    # ── champion (already scanned, 0 LP-feasible) ────────────────────────────
    (26, 11670, 89, 28, 22, 1, 1),   # DONE — skip by default
]

# ═══════════════════════════════════════════════════════════════════════════
#  CY data loading
# ═══════════════════════════════════════════════════════════════════════════

def load_cy_data(h11: int, poly_idx: int):
    """Load CY3 data for a KS polytope.  Returns (cy, c2, intnums_dict, h11_eff).

    Tries the local ks_index first (fast); falls back to ct.fetch_polytopes
    (internet download, ~6 poly/s) if the local index is absent.
    """
    import cytools as ct
    from cytools.config import enable_experimental_features
    enable_experimental_features()

    print(f"  Loading h{h11}/P{poly_idx} ({poly_idx+1} polys) ...", flush=True)
    t0 = time.time()

    # ── Try local index first ──────────────────────────────────────────────
    p = None
    try:
        from ks_index import load_h11_polytopes
        polys = load_h11_polytopes(h11, limit=poly_idx + 1)
        p = polys[poly_idx]
        print(f"  [local index] loaded in {time.time()-t0:.1f}s", flush=True)
    except FileNotFoundError:
        pass

    # ── Fallback: fetch from KS website ───────────────────────────────────
    if p is None:
        print(f"  [local index missing — fetching from KS website] ...", flush=True)
        polys = ct.fetch_polytopes(h11=h11, chi=-6,
                                   limit=poly_idx + 1, as_list=True)
        if len(polys) <= poly_idx:
            raise ValueError(f"Only {len(polys)} polytopes returned; "
                             f"poly_idx={poly_idx} out of range")
        p = polys[poly_idx]
        print(f"  [fetched {len(polys)} polys in {time.time()-t0:.1f}s]", flush=True)

    print(f"  {len(p.vertices())} vertices — {time.time()-t0:.1f}s. Triangulating ...",
          flush=True)

    t1  = time.time()
    tri = p.triangulate()
    cy  = tri.get_cy()
    print(f"  cy.h11()={cy.h11()}, h21={cy.h21()} — {time.time()-t1:.1f}s", flush=True)

    c2      = np.array(cy.second_chern_class(in_basis=True), dtype=float)
    intnums = dict(cy.intersection_numbers(in_basis=True))
    h11_eff = len(c2)
    print(f"  h11_eff={h11_eff}  c2=[{c2.min():.0f},{c2.max():.0f}]  "
          f"κ entries={len(intnums)}", flush=True)
    return cy, c2, intnums, h11_eff


def build_kappa_tensor(intnums: dict, h11_eff: int) -> np.ndarray:
    """Dense κ_{abc} tensor from CYTools sparse dict, fully symmetrized."""
    K = np.zeros((h11_eff, h11_eff, h11_eff), dtype=float)
    for (a, b, c), v in intnums.items():
        if 0 <= a < h11_eff and 0 <= b < h11_eff and 0 <= c < h11_eff:
            for aa, bb, cc in ((a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a)):
                K[aa, bb, cc] = v
    return K


# ═══════════════════════════════════════════════════════════════════════════
#  Monad arithmetic
# ═══════════════════════════════════════════════════════════════════════════

def chi_lb(D: np.ndarray, c2: np.ndarray, K: np.ndarray) -> float:
    """Hirzebruch-Riemann-Roch: χ(O(D)) = D³/6 + c2·D/12."""
    D3  = float(np.einsum('ijk,i,j,k', K, D, D, D))
    c2D = float(np.dot(c2, D))
    return D3 / 6.0 + c2D / 12.0


def chi_monad(Bs: np.ndarray, Cs: np.ndarray,
              c2: np.ndarray, K: np.ndarray) -> float:
    """χ(V) = Σ_i χ(O(b_i)) − Σ_j χ(O(c_j))  by Whitney sum on the SES."""
    return (sum(chi_lb(b, c2, K) for b in Bs)
            - sum(chi_lb(c, c2, K) for c in Cs))


def slope(D: np.ndarray, J: np.ndarray, K: np.ndarray) -> float:
    """μ(O(D),J) = (J²·D) = Σ_{ab} κ_{ab?} J_a J_b D_c  (cup-product slope)."""
    return float(np.einsum('ijk,i,j,k->', K,
                           J[:, None, None] * J[None, :, None],
                           D[None, None, :]).sum())


# ═══════════════════════════════════════════════════════════════════════════
#  LP slope-feasibility (gradient optimization)
# ═══════════════════════════════════════════════════════════════════════════

def build_slope_matrices(Bs: np.ndarray, Cs: np.ndarray,
                         K: np.ndarray):
    """Pre-compute M_B[i,b,c] = Σ_a κ_{abc} b_i_a   (and M_C similarly)."""
    n_B, h = Bs.shape
    n_C    = Cs.shape[0]
    M_B = np.einsum('abc,ib->iac', K, Bs)   # (n_B, h, h)  → μ_B[i] = J @ M_B[i] @ J
    M_C = np.einsum('abc,ib->iac', K, Cs)
    return M_B, M_C


def slope_margin_and_grad(v: np.ndarray, M_B: np.ndarray, M_C: np.ndarray,
                          alpha: float = 10.0):
    """
    Objective: slope_margin = max_i μ(b_i,J) − min_j μ(c_j,J)  with J=exp(v).
    We want margin < 0  ↔  feasible.
    Use log-sum-exp smooth approximation; return (F, grad_F) for L-BFGS-B.
    """
    J = np.exp(v)
    # μ_B[i] = J @ M_B[i] @ J,  μ_C[j] = J @ M_C[j] @ J
    mu_B = np.array([J @ M_B[i] @ J for i in range(M_B.shape[0])])
    mu_C = np.array([J @ M_C[j] @ J for j in range(M_C.shape[0])])

    # smooth max of μ_B
    shift_B   = mu_B.max()
    exp_B     = np.exp(alpha * (mu_B - shift_B))
    Z_B       = exp_B.sum()
    sm_max_B  = shift_B + np.log(Z_B) / alpha   # smooth-max μ_B
    w_B       = exp_B / Z_B                      # weights

    # smooth min of μ_C  =  −smooth_max(−μ_C)
    shift_C   = (-mu_C).max()
    exp_C     = np.exp(alpha * (-mu_C - shift_C))
    Z_C       = exp_C.sum()
    sm_min_C  = -(shift_C + np.log(Z_C) / alpha)
    w_C       = exp_C / Z_C

    F = sm_max_B - sm_min_C   # want F < 0

    # gradient w.r.t. v (chain rule: ∂/∂v_k = ∂/∂J_k * J_k)
    grad_muB_J = np.array([2.0 * (M_B[i] @ J) for i in range(M_B.shape[0])])  # (n_B,h)
    grad_muC_J = np.array([2.0 * (M_C[j] @ J) for j in range(M_C.shape[0])])

    grad_F_J = w_B @ grad_muB_J + w_C @ grad_muC_J   # (h,)
    grad_F_v = grad_F_J * J                            # chain rule

    return float(F), grad_F_v


def find_feasible_kahler(M_B: np.ndarray, M_C: np.ndarray, h11_eff: int,
                         n_starts: int = 20, alpha: float = 10.0,
                         rng: Optional[np.random.Generator] = None):
    """
    Run L-BFGS-B optimizer from n_starts random starts to minimise slope_margin.
    Returns (feasible, J_opt, best_margin).
    """
    if rng is None:
        rng = np.random.default_rng()

    best_F  = np.inf
    best_J  = np.ones(h11_eff)

    V_MAX = 3.0   # cap v so exp(v) ≤ e^3 ≈ 20; prevents overflow in J^3

    for _ in range(n_starts):
        v0  = rng.uniform(-1.0, 1.0, size=h11_eff)
        bounds = [(-V_MAX, V_MAX)] * h11_eff
        res = minimize(slope_margin_and_grad, v0,
                       args=(M_B, M_C, alpha),
                       jac=True,
                       method='L-BFGS-B',
                       bounds=bounds,
                       options={'maxiter': 300, 'ftol': 1e-12, 'gtol': 1e-8})
        J_opt = np.exp(res.x)
        # Recompute exact (non-smooth) margin
        s_B = np.einsum('ibc,b,c->i', M_B, J_opt, J_opt)
        s_C = np.einsum('jbc,b,c->j', M_C, J_opt, J_opt)
        exact_margin = float(s_B.max() - s_C.min())
        if exact_margin < best_F:
            best_F = exact_margin
            best_J = J_opt.copy()
        if best_F < -1e-8:
            break

    return best_F < -1e-8, best_J, float(best_F)


# ═══════════════════════════════════════════════════════════════════════════
#  D3-tadpole check
# ═══════════════════════════════════════════════════════════════════════════

def check_c2_tadpole(Bs: np.ndarray, Cs: np.ndarray,
                     c2_X: np.ndarray, K: np.ndarray, h11_eff: int):
    """Rough D3-tadpole check (same proxy as champion_monads_lp.py).

    Uses J=ones as a proxy Kähler form to compute a linear ch2 estimator:
      ch2[k] = (Σ_i Σ_{a,b} κ_{kab} J_b B_{ia} - Σ_j Σ_{a,b} κ_{kab} J_b C_{ja}) / 2
    Then c2(V) = -2·ch2, and tadpole OK iff c2(V) ≤ c2(TX) + 1.
    Returns (ok, n_d3_rough, c2V_min, c2V_max).
    """
    J        = np.ones(h11_eff)
    M        = np.einsum('kab,b->ka', K, J)      # (h, h)
    ch2_B    = np.einsum('ka,ia->k', M, Bs)      # (h,)
    ch2_C    = np.einsum('ka,ja->k', M, Cs)      # (h,)
    ch2      = (ch2_B - ch2_C) / 2.0
    c2_V     = -2.0 * ch2
    tadpole_ok = bool(np.all(c2_V <= c2_X + 1.0))
    n_d3_rough = float(np.sum(c2_X - c2_V))
    return tadpole_ok, n_d3_rough, float(c2_V.min()), float(c2_V.max())


# ═══════════════════════════════════════════════════════════════════════════
#  Structural obstruction pre-check (no full LP required)
# ═══════════════════════════════════════════════════════════════════════════

def structural_obstruction_check(K: np.ndarray, c2: np.ndarray,
                                 h11_eff: int, rank: int = 4,
                                 k_max: int = 3) -> dict:
    """
    Estimate whether the D3 tadpole is structurally blocked.

    The worst-case ch2(V)_k ≤ n_B * k_max² * κ_max_k / 2  (positive only).
    If this exceeds c2_X_k for ALL k, no monad can satisfy tadpole.

    Returns dict with keys: kappa_max, c2_max, n_B_typical, bound, likely_obstructed.
    """
    n_B = rank + 1   # minimum n_B for SU(rank) monad

    # max |κ_{kab}| per k:  κ_max_k = max_{a,b} |K[k,a,b]|
    kappa_max_per  = np.abs(K).max(axis=(1, 2))           # (h11_eff,)
    kappa_max      = float(kappa_max_per.max())
    c2_max         = float(c2.max())
    c2_min         = float(c2.min())

    # For each k: the tightest bound is n_B * k_max² * kappa_max_per[k] / 2
    ch2V_worst     = n_B * k_max**2 * kappa_max_per / 2.0  # (h11_eff,)
    # Tadpole margin per component: c2[k] - ch2V_worst[k]
    margin_per     = c2 - ch2V_worst
    # Likely obstructed if margin is negative for ALL k (no slack anywhere)
    likely_obstructed = bool(np.all(margin_per < 0))

    # Tighter: minimum over k of (c2[k] / ch2V_worst[k])
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.where(ch2V_worst > 0, c2 / ch2V_worst, np.inf)
    tadpole_ratio = float(ratio.min())  # < 1 means obstructed on that component

    return {
        "kappa_max":         kappa_max,
        "kappa_max_per_k":   kappa_max_per.tolist(),
        "c2_max":            c2_max,
        "c2_min":            c2_min,
        "c2":                c2.tolist(),
        "ch2V_worst_per_k":  ch2V_worst.tolist(),
        "margin_per_k":      margin_per.tolist(),
        "tadpole_ratio_min": tadpole_ratio,
        "likely_obstructed": likely_obstructed,
        "n_B_min":           n_B,
        "k_max":             k_max,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  Phase-1 + Phase-2 scan (per entry)
# ═══════════════════════════════════════════════════════════════════════════

def scan_monads_lp(c2: np.ndarray, K: np.ndarray, h11_eff: int,
                   rank: int = 4, k_max: int = 3,
                   n_sample: int = 500_000, chi_target: int = 3,
                   n_starts: int = 20, alpha: float = 10.0,
                   configs=None, seed: int = 20260307):
    """
    Phase 1: sample monad charges (c1=0, χ=±chi_target).
    Phase 2: LP slope-feasibility on χ-candidates.
    Returns (candidates_list, total_phase1_checked).
    """
    rng     = np.random.default_rng(seed)
    opt_rng = np.random.default_rng(314159)

    if configs is None:
        configs = [(rank + 1, 1), (rank + 2, 2), (rank + 3, 3)]

    all_stable    = []
    total_checked = 0

    for n_B, n_C in configs:
        assert n_B - n_C == rank
        t0        = time.time()
        chi_cands = []
        cfg_checked = 0

        print(f"\n{'='*60}")
        print(f"  Config: SU({rank}), n_B={n_B}, n_C={n_C}, k_max={k_max}")
        log10_space = (2 * k_max + 1) ** (h11_eff * (n_B + n_C - 1))
        if log10_space > 0:
            log10_space = math.log10(log10_space)
        print(f"  Search space: ~10^{log10_space:.1f}")
        print(f"  Phase 1: {n_sample:,} trials for χ=±{chi_target} ...", flush=True)

        # ── Phase 1 ──────────────────────────────────────────────────────────
        for trial in range(n_sample):
            if trial % 200_000 == 0 and trial > 0:
                elapsed = time.time() - t0
                rate    = trial / elapsed
                eta     = int((n_sample - trial) / rate)
                print(f"  {trial:,}/{n_sample:,}  χ-cands={len(chi_cands)}  "
                      f"{rate:.0f}/s  eta={eta}s", flush=True)

            Cs      = rng.integers(-k_max, k_max + 1, size=(n_C, h11_eff)).astype(float)
            Bs_free = rng.integers(-k_max, k_max + 1, size=(n_B - 1, h11_eff)).astype(float)
            b_last  = Cs.sum(axis=0) - Bs_free.sum(axis=0)

            if np.abs(b_last).max() > k_max * n_B:
                continue

            Bs        = np.vstack([Bs_free, b_last[None, :]])
            cfg_checked += 1

            chi_V = chi_monad(Bs, Cs, c2, K)
            chi_r = round(chi_V)
            if abs(chi_r) != chi_target or abs(chi_V - chi_r) > 0.15:
                continue

            chi_cands.append((Bs.copy(), Cs.copy(), chi_r, trial))

        elapsed1 = time.time() - t0
        print(f"  Phase 1 done: {cfg_checked:,} valid, {len(chi_cands)} χ-cands "
              f"({elapsed1:.0f}s)", flush=True)

        # ── Phase 2 ──────────────────────────────────────────────────────────
        print(f"  Phase 2: LP on {len(chi_cands)} candidates "
              f"({n_starts} starts each) ...", flush=True)
        t2         = time.time()
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
                rate2    = lp_checked / elapsed2
                eta2     = int((len(chi_cands) - lp_checked) / max(rate2, 1e-9))
                print(f"    LP {lp_checked}/{len(chi_cands)}  feasible={n_feasible} "
                      f"{rate2:.1f}/s  eta={eta2}s", flush=True)

            if feasible:
                n_feasible += 1
                tadpole_ok, n_d3, c2v_min, c2v_max = check_c2_tadpole(
                    Bs, Cs, c2, K, h11_eff
                )
                vol = float(np.einsum('ijk,i,j,k', K, J_opt, J_opt, J_opt))
                all_stable.append({
                    "config":        f"({n_B},{n_C})",
                    "n_B":           n_B,
                    "n_C":           n_C,
                    "rank":          rank,
                    "k_max":         k_max,
                    "chi_V":         chi_r,
                    "B":             Bs.tolist(),
                    "C":             Cs.tolist(),
                    "J_opt":         J_opt.tolist(),
                    "slope_margin":  float(margin),
                    "vol_J":         vol,
                    "tadpole_ok":    tadpole_ok,
                    "n_d3_rough":    n_d3,
                    "c2V_range":     [c2v_min, c2v_max],
                    "trial":         trial,
                })
                tr = "✓" if tadpole_ok else "✗"
                print(f"  *** FEASIBLE: ({n_B},{n_C}) χ={chi_r:+d} "
                      f"margin={margin:.4f} vol={vol:.3f} tadpole={tr} "
                      f"n_D3≈{n_d3:.1f}", flush=True)

        elapsed2 = time.time() - t2
        print(f"  Phase 2 done: {lp_checked} LP checks in {elapsed2:.0f}s. "
              f"Slope-feasible: {n_feasible}", flush=True)
        total_checked += cfg_checked

    return all_stable, total_checked


# ═══════════════════════════════════════════════════════════════════════════
#  Per-entry checkpoint
# ═══════════════════════════════════════════════════════════════════════════

def entry_result_path(h11: int, poly_idx: int) -> str:
    return os.path.join(RESULTS_DIR, f"monad_scan_top37_{h11}_{poly_idx}.json")


def load_entry_result(h11: int, poly_idx: int) -> Optional[dict]:
    p = entry_result_path(h11, poly_idx)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


def save_entry_result(result: dict) -> None:
    p = entry_result_path(result["h11"], result["poly_idx"])
    with open(p, "w") as f:
        json.dump(result, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rank",            type=int,   default=4)
    p.add_argument("--k-max",           type=int,   default=3)
    p.add_argument("--n-sample",        type=int,   default=500_000,
                   help="Phase-1 samples per entry (default 500K)")
    p.add_argument("--n-starts",        type=int,   default=20,
                   help="LP restarts per χ-candidate (default 20)")
    p.add_argument("--alpha",           type=float, default=10.0)
    p.add_argument("--chi-target",      type=int,   default=3)
    p.add_argument("--configs",         type=str,   default=None,
                   help="Override configs, e.g. '5,1 6,2'")
    p.add_argument("--skip",            type=str,   default="26:11670",
                   help="Comma-separated h11:poly_idx pairs to skip "
                        "(default: '26:11670', already done)")
    p.add_argument("--only-priority",   action="store_true",
                   help="Only scan h11_eff≤20 entries (the 4 priority entries)")
    p.add_argument("--structural-only", action="store_true",
                   help="Only compute structural obstruction bounds, no LP")
    p.add_argument("--resume",          action="store_true",
                   help="Skip entries that already have a result JSON (default: True)")
    p.add_argument("--force",           action="store_true",
                   help="Re-run even if result JSON exists")
    p.add_argument("--entry",           type=str,   default=None,
                   help="Only run this entry, e.g. '22:682'")
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Parse skip set
    skip_set: set[tuple[int, int]] = set()
    if args.skip:
        for tok in args.skip.split(","):
            tok = tok.strip()
            if ":" in tok:
                h, p = tok.split(":")
                skip_set.add((int(h), int(p)))

    # Parse --entry override
    only_entry: Optional[tuple[int, int]] = None
    if args.entry:
        h, p = args.entry.split(":")
        only_entry = (int(h), int(p))

    # Parse configs override
    configs = None
    if args.configs:
        configs = []
        for tok in args.configs.split():
            nb, nc = tok.split(",")
            configs.append((int(nb), int(nc)))

    # Filter entries
    entries = list(TOP37)
    if only_entry:
        entries = [e for e in entries if (e[0], e[1]) == only_entry]
    elif args.only_priority:
        entries = [e for e in entries if e[3] <= 20]

    print("=" * 70)
    print("MONAD SCAN — TOP-37 T4 ENTRIES")
    print(f"Method:       SU({args.rank}) monad, k_max={args.k_max}, "
          f"n_sample={args.n_sample:,}")
    print(f"LP:           {args.n_starts} starts × L-BFGS-B, α={args.alpha}")
    print(f"Entries:      {len(entries)} (skip={skip_set})")
    print(f"Structural:   {'only' if args.structural_only else '+LP'}")
    print(f"Priority (h11_eff≤20): "
          f"{sum(1 for e in entries if e[3]<=20)} entries")
    print("=" * 70)

    all_summary: list[dict] = []
    t_global = time.time()

    for idx, (h11, poly_idx, score, h11_eff, n_clean, has_sm, has_gut) in enumerate(entries):
        tag = f"h{h11}/P{poly_idx}"
        print(f"\n{'#'*70}")
        print(f"[{idx+1}/{len(entries)}] {tag}  score={score}  "
              f"h11_eff={h11_eff}  n_clean={n_clean}  "
              f"has_SM={has_sm}  has_GUT={has_gut}")
        print(f"{'#'*70}")

        # Skip?
        if (h11, poly_idx) in skip_set:
            print(f"  SKIPPED (in skip list)")
            all_summary.append({
                "h11": h11, "poly_idx": poly_idx, "score": score,
                "h11_eff": h11_eff, "status": "skipped",
                "n_slope_feasible": 0, "n_tadpole_ok": 0,
            })
            continue

        # Checkpoint resume
        if not args.force:
            existing = load_entry_result(h11, poly_idx)
            if existing is not None:
                print(f"  RESUMING from checkpoint: "
                      f"slope_feasible={existing.get('n_slope_feasible',0)}, "
                      f"tadpole_ok={existing.get('n_tadpole_ok',0)}")
                all_summary.append({
                    "h11": h11, "poly_idx": poly_idx, "score": score,
                    "h11_eff": h11_eff, "status": "resumed",
                    "n_slope_feasible": existing.get("n_slope_feasible", 0),
                    "n_tadpole_ok":     existing.get("n_tadpole_ok", 0),
                    "structural":       existing.get("structural", {}),
                    "candidates":       existing.get("candidates", []),
                })
                continue

        # Load CY data
        t_entry = time.time()
        try:
            cy, c2, intnums, h11_eff_actual = load_cy_data(h11, poly_idx)
        except Exception as exc:
            print(f"  ERROR loading {tag}: {exc}")
            result = {
                "h11": h11, "poly_idx": poly_idx, "score": score,
                "h11_eff": h11_eff, "h11_eff_actual": None,
                "status": "load_error", "error": str(exc),
                "n_slope_feasible": 0, "n_tadpole_ok": 0,
                "candidates": [],
            }
            save_entry_result(result)
            all_summary.append(result)
            continue

        K = build_kappa_tensor(intnums, h11_eff_actual)
        print(f"  h11_eff_actual={h11_eff_actual}  "
              f"κ_max={np.abs(K).max():.2f}  "
              f"c2_max={c2.max():.2f}  c2_min={c2.min():.2f}")

        # Structural pre-check
        struct = structural_obstruction_check(
            K, c2, h11_eff_actual, rank=args.rank, k_max=args.k_max
        )
        print(f"  Structural: κ_max={struct['kappa_max']:.2f}  "
              f"c2_max={struct['c2_max']:.2f}  "
              f"tadpole_ratio_min={struct['tadpole_ratio_min']:.3f}  "
              f"likely_obstructed={struct['likely_obstructed']}")

        result_base = {
            "h11":             h11,
            "poly_idx":        poly_idx,
            "score":           score,
            "h11_eff":         h11_eff,
            "h11_eff_actual":  h11_eff_actual,
            "n_clean":         n_clean,
            "has_SM":          has_sm,
            "has_GUT":         has_gut,
            "rank":            args.rank,
            "k_max":           args.k_max,
            "n_sample":        args.n_sample,
            "chi_target":      args.chi_target,
            "structural":      struct,
            "timestamp":       datetime.now(timezone.utc).isoformat(),
        }

        if args.structural_only:
            result = {**result_base,
                      "status": "structural_only",
                      "n_slope_feasible": 0,
                      "n_tadpole_ok": 0,
                      "candidates": []}
            save_entry_result(result)
            all_summary.append({**result_base,
                                 "status": "structural_only",
                                 "n_slope_feasible": 0,
                                 "n_tadpole_ok": 0})
            continue

        # Full LP scan
        candidates, total_checked = scan_monads_lp(
            c2, K, h11_eff_actual,
            rank=args.rank,
            k_max=args.k_max,
            n_sample=args.n_sample,
            chi_target=args.chi_target,
            n_starts=args.n_starts,
            alpha=args.alpha,
            configs=configs,
            seed=20260307 + poly_idx,
        )

        n_tadpole_ok    = sum(1 for c in candidates if c.get("tadpole_ok"))
        elapsed_entry   = time.time() - t_entry

        status = "done"
        if struct["likely_obstructed"] and len(candidates) == 0:
            status = "obstructed"
        elif len(candidates) > 0:
            status = "feasible"

        result = {
            **result_base,
            "status":           status,
            "n_phase1_checked": total_checked,
            "n_slope_feasible": len(candidates),
            "n_tadpole_ok":     n_tadpole_ok,
            "elapsed_s":        elapsed_entry,
            "candidates":       candidates,
        }
        save_entry_result(result)

        all_summary.append({
            "h11": h11, "poly_idx": poly_idx, "score": score,
            "h11_eff": h11_eff_actual, "status": status,
            "n_slope_feasible": len(candidates),
            "n_tadpole_ok": n_tadpole_ok,
            "structural": struct,
            "candidates": candidates,
        })

        print(f"\n  {tag} done in {elapsed_entry:.0f}s  "
              f"slope_feasible={len(candidates)}  "
              f"tadpole_ok={n_tadpole_ok}  status={status}")

        # Running summary
        n_feasible_so_far = sum(1 for e in all_summary if e.get("n_slope_feasible", 0) > 0)
        print(f"  Running total: {n_feasible_so_far} entries with ≥1 feasible monad")

    # ── Global summary ──────────────────────────────────────────────────────
    elapsed_total = time.time() - t_global
    print(f"\n{'='*70}")
    print("GLOBAL SUMMARY")
    print(f"{'='*70}")
    feasible_entries = [e for e in all_summary if e.get("n_slope_feasible", 0) > 0]
    tadpole_entries  = [e for e in all_summary if e.get("n_tadpole_ok", 0) > 0]

    print(f"  Total entries processed:  {len(all_summary)}")
    print(f"  Entries with ≥1 slope-feasible monad: {len(feasible_entries)}")
    print(f"  Entries with ≥1 tadpole-OK monad:     {len(tadpole_entries)}")
    print(f"  Total time: {elapsed_total:.0f}s ({elapsed_total/60:.1f} min)")

    if feasible_entries:
        print(f"\n  TOP PROSPECTS:")
        for e in sorted(feasible_entries,
                        key=lambda x: -x.get("n_tadpole_ok", 0)):
            print(f"    h{e['h11']}/P{e['poly_idx']}  score={e['score']}  "
                  f"h11_eff={e['h11_eff']}  "
                  f"slope_feasible={e['n_slope_feasible']}  "
                  f"tadpole_ok={e['n_tadpole_ok']}")
    else:
        print("\n  No slope-feasible monads found in any T4 entry.")
        print("  → D3-tadpole obstruction appears structural across all h11_eff≥19.")
        print("  → Recommend: F-theory Weierstrass route or spectral cover construction.")

    # Save summary JSON
    summary_data = {
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "rank":             args.rank,
        "k_max":            args.k_max,
        "n_sample":         args.n_sample,
        "n_starts":         args.n_starts,
        "chi_target":       args.chi_target,
        "elapsed_s":        elapsed_total,
        "n_entries":        len(all_summary),
        "n_feasible":       len(feasible_entries),
        "n_tadpole_ok":     len(tadpole_entries),
        "entries":          all_summary,
    }
    with open(SUMMARY_JSON, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"\n  Summary saved to: {SUMMARY_JSON}")


if __name__ == "__main__":
    main()
