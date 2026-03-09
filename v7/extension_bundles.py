#!/usr/bin/env python3
"""
extension_bundles.py — B-50: Extension bundle construction on h22/P682

Extension bundles: short exact sequences
    0 → L₁ → V → E → 0
where L₁ = O(α) is a line bundle and E is a rank-(r-1) bundle.

For SU(4) target we use:
    0 → O(α) → V → E → 0   r=4
    E = O(β₁) ⊕ O(β₂) ⊕ O(β₃)   (rank-3 direct sum, most general tractable case)

This is strictly more general than monads: a monad 0→V→B→C→0 is an extension
with E = ker(B→C). Extensions avoid the monad c₂ growth because:
    c₂(V) = c₂(L₁) + c₂(E) + [extension class contribution]
The extension class H¹(X, E⊗L₁*) controls whether V is non-split.

Algorithm
---------
Phase 1: Sample random α ∈ Z^{h11_eff}, β₁,β₂,β₃ ∈ Z^{h11_eff}
  Constraints:
    (a) c₁(V) = 0  →  α + β₁ + β₂ + β₃ = 0 (sum of all c₁)
    (b) χ(V) = ±3  →  Σ χ(O(βᵢ)) + χ(O(α)) computed via HRR
    (c) D3-tadpole pre-filter (correct quadratic ch₂ formula)

Phase 2: LP slope stability
  V slope-stable w.r.t. J if all quotients Q have μ(Q,J) > μ(V,J).
  For direct-sum E: check each summand L₁, O(βᵢ) separately:
    μ(O(α),J) < μ(V,J) < μ(O(βᵢ),J)   for all i  (Hoppe criterion approx.)
  For non-split V: use standard slope condition via HN filtration.
  Approximation: treat as μ(O(α)) and μ(O(βᵢ)) vs avg μ(V) = 0 (since c₁=0).

Phase 3: Extension class existence check
  Ext¹(E, L₁) = H¹(X, E⊗L₁*) must be non-zero.
  Using Koszul/cohomCalg: approximate with χ(O(βᵢ−α)) ≠ 0, dim bound.

Usage:
    python3 v7/extension_bundles.py [--poly H11:IDX] [--n-sample N]
                                     [--k-max K] [--n-starts M] [--rank R]

Options:
    --poly         H11:IDX (default: 22:682)
    --n-sample N   random trials (default: 5_000_000)
    --k-max K      max |charge component| (default: 2)
    --n-starts M   LP restarts per candidate (default: 20)
    --rank R       bundle rank (default: 4)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
V6_DIR       = os.path.join(PROJECT_ROOT, "v6")
sys.path.insert(0, V6_DIR)
sys.path.insert(0, PROJECT_ROOT)

os.makedirs(os.path.join(SCRIPT_DIR, "results"), exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
#  CY loader (web fallback)
# ─────────────────────────────────────────────────────────────────────────────

def load_cy(h11, poly_idx):
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    print(f"Loading h{h11}/P{poly_idx} ...", flush=True)
    t0 = time.time()
    try:
        from ks_index import load_h11_polytopes
        polys = load_h11_polytopes(h11, limit=poly_idx + 1)
        p = polys[poly_idx]
    except Exception:
        from cytools import fetch_polytopes
        print("  (local KS unavailable — fetching from web ...)", flush=True)
        polys = fetch_polytopes(h11=h11, chi=-6, limit=poly_idx + 1, timeout=300)
        p = polys[poly_idx]
    tri = p.triangulate()
    cy  = tri.get_cy()
    print(f"  h11={cy.h11()} h21={cy.h21()}  {time.time()-t0:.1f}s", flush=True)
    c2      = np.array(cy.second_chern_class(in_basis=True), dtype=float)
    intnums = dict(cy.intersection_numbers(in_basis=True))
    h11_eff = len(c2)
    # Load Kähler cone rays (toric approximation)
    print("  Loading Kähler cone rays ...", flush=True)
    kc_rays = np.array(cy.toric_kahler_cone().rays(), dtype=float)
    kc_rays = kc_rays[:, :h11_eff]  # trim to basis dimension
    print(f"  h11_eff={h11_eff}  c2 ∈ [{c2.min():.0f},{c2.max():.0f}]"
          f"  κ entries={len(intnums)}  kc_rays={kc_rays.shape}", flush=True)
    return cy, c2, intnums, h11_eff, kc_rays


def build_kappa_tensor(intnums, h11_eff):
    K = np.zeros((h11_eff, h11_eff, h11_eff), dtype=float)
    for (a, b, c), v in intnums.items():
        if 0 <= a < h11_eff and 0 <= b < h11_eff and 0 <= c < h11_eff:
            for aa, bb, cc in [(a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a)]:
                K[aa, bb, cc] = v
    return K

# ─────────────────────────────────────────────────────────────────────────────
#  Bundle arithmetic
# ─────────────────────────────────────────────────────────────────────────────

def chi_lb(D, c2, K):
    """χ(O(D)) = D³/6 + c₂·D/12  (Hirzebruch-Riemann-Roch)."""
    D = np.asarray(D, dtype=float)
    return np.einsum('ijk,i,j,k', K, D, D, D) / 6.0 + np.dot(c2, D) / 12.0


def ch2_lb(beta, K):
    """ch₂(O(β))_k = ½ κ_{kab} β^a β^b  (correct quadratic formula)."""
    beta = np.asarray(beta, dtype=float)
    return 0.5 * np.einsum('kab,a,b->k', K, beta, beta)


def c2_extension(alpha, betas, K):
    """
    c₂(V) for extension 0→O(α)→V→O(β₁)⊕...⊕O(βₙ)→0.

    Derivation (using additivity of Chern character on exact sequences):
      ch(V) = ch(O(α)) + ch(O(β₁)) + ... + ch(O(βₙ))
      ch₂(V) = ½κ_{kab}[α^aα^b + Σᵢ βᵢ^aβᵢ^b]
    And for SU(r) (c₁(V)=0):  c₂(V) = −ch₂(V).
    Hence:
      c₂(V)_k = −½ κ_{kab} [α^aα^b + Σᵢ βᵢ^aβᵢ^b]

    This is verified against the Whitney formula (c₂ from Chern classes):
      c₂(V) = c₁(L₁)·c₁(E) + c₂(E)  [Whitney for extension]
             = α·(Σβᵢ) + Σᵢ<ⱼ βᵢ·βⱼ  [= α·(−α) + Σᵢ<ⱼ βᵢ·βⱼ]
    Both give the same result after substituting α = −Σβᵢ.
    """
    ch2_total = ch2_lb(alpha, K) + sum(ch2_lb(b, K) for b in betas)
    return -ch2_total   # c₂(V) = −ch₂(V) for SU(r)


def tadpole_delta(alpha, betas, c2_TX, K):
    """
    Compute Δn_D3 = Σ_k [c₂(V)_k − c₂(TX)_k] (scalar tadpole excess).

    Physical interpretation (heterotic M-theory on CY3):
      n_M5 = −Δn_D3   (without H-flux)
    • Δn_D3 ≤ 0  → n_M5 ≥ 0 : tadpole satisfied by M5-branes alone (ideal)
    • Δn_D3 > 0  → need |H-flux|² ≥ Δn_D3 (as in B-49)
    The component-wise check c₂(V)_k ≤ c₂(TX)_k is too strict because the
    Bianchi identity is integrated against the Kähler form J (a single scalar),
    not checked per-divisor. We use the scalar Δn_D3 consistent with B-49.

    NOTE: κ_{kab} has large NEGATIVE entries for the k-components where
    c₂(TX)_k < 0 (diagnostic on h22/P682 shows max|κ_kab| up to 14 for k=18).
    These make ch₂(O(β))_k < 0 for those components, driving c₂(V)_k > 0 and
    violating component-wise bounds — but the scalar Δn_D3 can still be small.
    """
    c2_V = c2_extension(alpha, betas, K)
    delta = float((c2_V - c2_TX).sum())
    return delta, c2_V


# ─────────────────────────────────────────────────────────────────────────────
#  Slope stability for extension  0 → O(α) → V → ⊕O(βᵢ) → 0
# ─────────────────────────────────────────────────────────────────────────────
#
# Slope stability criterion (necessary, from extension sub-bundle structure):
#   For generic non-split extension with c₁(V)=0, the ONLY guaranteed
#   sub-line-bundle of V is O(α) (the inclusion in the SES). Slope stability
#   requires μ(O(α), J) < μ(V, J) = 0, i.e., κ_{abc} α^a J^b J^c < 0.
#
# We sample J from the actual Kähler cone (using kc_rays) and check that
# at least one sample satisfies μ(O(α), J) < 0 with vol(J) > 0.
# This is necessary for slope stability and approximates the full criterion.
#
# NOTE: The positive orthant exp(v) is NOT the Kähler cone for this CY3.
# (Kähler cone tip is e.g. (48, 9, 28, −12, ...) with negative components.)

def sample_kahler_j(kc_rays, n_rays_to_use, rng):
    """
    Sample a random J from the interior of the Kähler cone.
    J = Σ λᵢ rᵢ  with λᵢ ~ Exp(1), rᵢ chosen randomly from kc_rays.
    This gives a valid interior point J with vol(J) > 0.
    """
    n = kc_rays.shape[0]
    k = min(n_rays_to_use, n)
    idx = rng.choice(n, size=k, replace=False)
    lam = rng.exponential(size=k)
    J   = kc_rays[idx].T @ lam
    return J


def mu_lb(alpha, K, J):
    """μ(O(α), J) = κ_{abc} α^a J^b J^c  (unnormalized slope, sign-correct)."""
    M = np.einsum('abc,a->bc', K, np.asarray(alpha, dtype=float))
    return float(J @ M @ J)


def find_feasible_kahler_ext(alpha, K, kc_rays, h11_eff, n_starts=20,
                              n_rays_to_use=None):
    """
    Find J in the Kähler cone such that μ(O(α), J) < 0.

    Returns (feasible, J_best, mu_best):
      feasible: bool — True if any sample satisfies μ(O(α), J) < 0
      J_best:   the best (most negative μ(O(α))) J found
      mu_best:  the best μ(O(α)) value (most negative = best)
    """
    if n_rays_to_use is None:
        n_rays_to_use = min(h11_eff + 2, kc_rays.shape[0])

    rng    = np.random.default_rng()
    M_a    = np.einsum('abc,a->bc', K, np.asarray(alpha, dtype=float))

    best_mu = np.inf
    best_J  = None

    for _ in range(n_starts):
        J = sample_kahler_j(kc_rays, n_rays_to_use, rng)
        mu_a = float(J @ M_a @ J)
        if mu_a < best_mu:
            best_mu = mu_a
            best_J  = J.copy()
        if best_mu < 0:
            break   # found a feasible point early

    feasible = best_mu < 0
    return feasible, best_J, best_mu


def vol_of_j(J, K):
    """CY3 holomorphic volume ∫ J³ = κ_{abc} J^a J^b J^c."""
    return float(np.einsum('ijk,i,j,k', K, J, J, J))


# ─────────────────────────────────────────────────────────────────────────────
#  Ext¹ existence estimate
# ─────────────────────────────────────────────────────────────────────────────

def ext1_chi_estimate(betas, alpha, c2, K):
    """
    Rough estimate of Ext¹(E, O(α)) = H¹(X, E ⊗ O(−α)).
    By Serre duality on CY3: h¹ = h² = ...; use χ as proxy.
    χ(E ⊗ O(−α)) = Σᵢ χ(O(βᵢ − α)).
    If |χ| > 0, the Ext group is non-trivial (extension can exist).
    """
    return sum(chi_lb(np.asarray(b) - np.asarray(alpha), c2, K) for b in betas)


# ─────────────────────────────────────────────────────────────────────────────
#  Main scan
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="B-50: Extension bundle scan")
    parser.add_argument("--poly",      default="22:682")
    parser.add_argument("--n-sample",  type=int, default=5_000_000)
    parser.add_argument("--k-max",     type=int, default=2)
    parser.add_argument("--n-starts",  type=int, default=20)
    parser.add_argument("--rank",      type=int, default=4)
    parser.add_argument("--max-delta", type=float, default=200.0,
                        help="Max scalar Δn_D3 = Σ[c₂(V)-c₂(TX)] to accept "
                             "(analogous to B-49 flux threshold; 0=ideal, "
                             "53=best monad, 200=generous)")
    args = parser.parse_args()

    h11, poly_idx = [int(x) for x in args.poly.split(":")]
    rank    = args.rank
    k_max   = args.k_max
    n_samp  = args.n_sample
    n_start = args.n_starts
    max_d   = args.max_delta
    r_E     = rank - 1   # rank of E (the quotient bundle)

    out_json = os.path.join(SCRIPT_DIR, "results",
                            f"ext_bundles_{h11}_{poly_idx}.json")
    out_txt  = os.path.join(SCRIPT_DIR, "results",
                            f"ext_bundles_{h11}_{poly_idx}.txt")

    t_start = time.time()
    print("=" * 68)
    print(f"B-50: EXTENSION BUNDLE SCAN — h{h11}/P{poly_idx}")
    print(f"Bundle: 0 → O(α) → V → O(β₁)⊕...⊕O(β{r_E}) → 0  [SU({rank})]")
    print("=" * 68)

    cy, c2_TX, intnums, h11_eff, kc_rays = load_cy(h11, poly_idx)
    K = build_kappa_tensor(intnums, h11_eff)

    print(f"\nGeometry: h11_eff={h11_eff}  h21={cy.h21()}")
    print(f"c₂(TX) range: [{c2_TX.min():.0f}, {c2_TX.max():.0f}]")

    # Pre-check: if even a single-summand α with |α|≤k_max saturates c2,
    # |β|≤k_max will also be obstructed.
    kappa_max_half = 0.5 * np.abs(np.einsum('kab->k', K)).max()
    ch2_per_summand_max = kappa_max_half * k_max**2
    print(f"\nTadpole ceiling (k_max={k_max}):")
    print(f"  max ch₂ per summand ≈ {ch2_per_summand_max:.1f}")
    print(f"  For {rank} summands: total ch₂ ≤ {rank * ch2_per_summand_max:.1f}"
          f"  vs  c₂(TX)_max = {c2_TX.max():.0f}")
    # Note: extension bundles may have cancellation between summands

    print(f"Scan: n_sample={n_samp:,}  k_max={k_max}  n_starts={n_start}  max_Δ={max_d}")
    print(f"Charges: α ∈ [-{k_max},{k_max}]^{h11_eff}, "
          f"β₁..β{r_E} ∈ [-{k_max},{k_max}]^{h11_eff} with Σ=−α")
    print(f"Tadpole: scalar Δn_D3 = Σ[c₂(V)_k − c₂(TX)_k] ≤ {max_d}")
    print(f"  (Δ≤0=ideal; Δ≤53=as good as best B-49 monad; Δ≤200=generous)")

    rng = np.random.default_rng(2026_03_09)

    n_chi_ok      = 0
    n_tadpole_ok  = 0
    n_slope_ok    = 0
    n_ext1_ok     = 0
    candidates    = []

    REPORT_EVERY = max(1, n_samp // 20)

    print(f"\n{'='*60}")
    print(f"Phase 1+2: Sampling + tadpole pre-filter + LP slope")
    print(f"{'='*60}")

    for trial in range(n_samp):
        if trial % REPORT_EVERY == 0 and trial > 0:
            elapsed = time.time() - t_start
            rate    = trial / elapsed
            eta     = (n_samp - trial) / rate if rate > 0 else 0
            print(f"  {trial:,}/{n_samp:,}  chi_ok={n_chi_ok}"
                  f"  tp_ok={n_tadpole_ok}  slope_ok={n_slope_ok}"
                  f"  {rate:.0f}/s  eta={eta:.0f}s", flush=True)

        # Sample α freely
        alpha = rng.integers(-k_max, k_max + 1, size=h11_eff)

        # Sample β₁..β_{r_E-1} freely, set β_{r_E} = −α − Σβ₁..β_{r_E-1}
        free_betas = rng.integers(-k_max, k_max + 1, size=(r_E - 1, h11_eff))
        last_beta  = -alpha - free_betas.sum(axis=0)

        # Check |last_beta| ≤ k_max + small slack (2*k_max to avoid extreme outliers)
        if np.abs(last_beta).max() > 2 * k_max:
            continue

        betas = list(free_betas) + [last_beta]

        # (a) χ(V) = χ(O(α)) + Σχ(O(βᵢ)) = ±3
        chi_V = round(chi_lb(alpha, c2_TX, K)
                      + sum(chi_lb(b, c2_TX, K) for b in betas))
        if abs(chi_V) != 3:
            continue
        n_chi_ok += 1

        # (b) D3-tadpole scalar check
        delta_d3, c2_V = tadpole_delta(alpha, betas, c2_TX, K)
        if delta_d3 > max_d:
            continue
        n_tadpole_ok += 1

        # (c) Slope stability: find J in KC with μ(O(α), J) < 0
        feasible, J_opt, mu_a_best = find_feasible_kahler_ext(
            alpha, K, kc_rays, h11_eff, n_starts=n_start)
        if not feasible:
            continue
        n_slope_ok += 1

        # (d) Ext¹ existence estimate
        ext1_chi = ext1_chi_estimate(betas, alpha, c2_TX, K)
        ext1_nonzero = (abs(round(ext1_chi)) > 0)
        if ext1_nonzero:
            n_ext1_ok += 1

        vol_J      = vol_of_j(J_opt, K)
        mu_betas   = [mu_lb(b, K, J_opt) for b in betas]

        candidates.append({
            "trial":       trial,
            "chi_V":       int(chi_V),
            "alpha":       alpha.tolist(),
            "betas":       [b.tolist() for b in betas],
            "c2V":         c2_V.tolist(),
            "c2V_max":     float(c2_V.max()),
            "delta_n_d3":  float(delta_d3),
            "tadpole_ideal": delta_d3 <= 0,
            "mu_alpha_best": float(mu_a_best),
            "slope_feasible": True,
            "vol_J":       vol_J,
            "mu_betas":    mu_betas,
            "ext1_chi":    float(ext1_chi),
            "ext1_nonzero": ext1_nonzero,
        })

        print(f"  *** CANDIDATE [{len(candidates)}] trial={trial}"
              f" chi={chi_V:+d} Δ={delta_d3:.1f} mu(α)={mu_a_best:.3f}"
              f" vol={vol_J:.3f} ext1_chi={ext1_chi:.0f}", flush=True)

    elapsed = time.time() - t_start
    n_ideal = sum(1 for c in candidates if c["tadpole_ideal"])
    print(f"\n{'='*68}")
    print(f"RESULTS SUMMARY — B-50 EXTENSION BUNDLE SCAN")
    print(f"{'='*68}")
    print(f"  Polytope:       h{h11}/P{poly_idx}")
    print(f"  Bundle:         0 → O(α) → V → ⊕O(βᵢ) → 0   SU({rank}), |charges|≤{k_max}")
    print(f"  Total sampled:  {n_samp:,}")
    print(f"  χ=±3 ok:        {n_chi_ok:,}")
    print(f"  Δn_D3 ≤ {max_d:.0f}:    {n_tadpole_ok:,}")
    print(f"  Slope-feasible: {n_slope_ok:,}")
    print(f"  Ext¹ non-zero:  {n_ext1_ok:,}")
    print(f"    of which Δ≤0 (ideal): {n_ideal}")
    print(f"  Elapsed:        {elapsed:.0f}s")
    print(f"{'='*68}")

    if candidates:
        print(f"\nTop candidates (sorted by Δn_D3 then by μ(α) sign):")
        for c in sorted(candidates, key=lambda x: (x["delta_n_d3"], x["mu_alpha_best"]))[:15]:
            tp_str  = "Δ≤0✓" if c["tadpole_ideal"] else f"Δ={c['delta_n_d3']:.0f}"
            ext_str = "ext1✓" if c["ext1_nonzero"] else "ext1?"
            print(f"  [{c['trial']:7d}] χ={c['chi_V']:+d}"
                  f"  {tp_str}  μ(α)={c['mu_alpha_best']:.3f}"
                  f"  vol={c['vol_J']:.3f}  {ext_str}")
    else:
        print("\nNo slope-feasible extension bundle candidates found.")
        if n_tadpole_ok == 0:
            print(f"  >> Scalar Δn_D3 > {max_d:.0f} for all χ=±3 candidates.")
            print(f"     Extension bundles at |β|≤{k_max} have large tadpole excess.")
            print(f"     Try --max-delta {int(max_d*2)} or --k-max {k_max+1}.")
        elif n_slope_ok == 0:
            print("  >> Tadpole passed but no slope-feasible J found.")
            print("     μ(O(α), J) > 0 for all tested J ∈ Kähler cone.")

    # Save
    out = {
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "polytope":     f"h{h11}/P{poly_idx}",
        "h11":          h11,
        "poly_idx":     poly_idx,
        "h11_eff":      h11_eff,
        "h21":          cy.h21(),
        "rank":         rank,
        "k_max":        k_max,
        "max_delta":    max_d,
        "n_sample":     n_samp,
        "n_starts":     n_start,
        "n_chi_ok":     n_chi_ok,
        "n_tadpole_ok": n_tadpole_ok,
        "n_slope_ok":   n_slope_ok,
        "n_ext1_ok":    n_ext1_ok,
        "n_ideal":      n_ideal,
        "elapsed_s":    elapsed,
        "candidates":   candidates,
    }
    with open(out_json, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults: {out_json}")

    with open(out_txt, "w") as f:
        f.write(f"B-50 Extension Bundle Scan — h{h11}/P{poly_idx}\n")
        f.write(f"Run: {datetime.now(timezone.utc).isoformat()} UTC\n")
        f.write(f"{'='*60}\n")
        f.write(f"Bundle: 0 → O(α) → V → ⊕O(βᵢ) → 0  SU({rank}), k_max={k_max}\n")
        f.write(f"Tadpole: scalar Δn_D3 ≤ {max_d:.0f} (Δ≤0=ideal, ≤53=as monad-B49, ≤200=generous)\n\n")
        f.write(f"Sampled:           {n_samp:,}\n")
        f.write(f"χ=±3 ok:           {n_chi_ok:,}\n")
        f.write(f"Δn_D3 ≤ {max_d:.0f} ok:  {n_tadpole_ok:,}\n")
        f.write(f"Slope-feasible:    {n_slope_ok:,}\n")
        f.write(f"Ext¹ non-zero:     {n_ext1_ok:,}\n")
        f.write(f"  of which Δ≤0:   {n_ideal}\n")
        f.write(f"Elapsed:           {elapsed:.0f}s\n\n")
        if candidates:
            f.write("CANDIDATES (sorted by Δn_D3, then slope margin):\n")
            for i, c in enumerate(sorted(candidates, key=lambda x: (x["delta_n_d3"], x["mu_alpha_best"]))):
                f.write(f"[{i+1:3d}] trial={c['trial']} chi={c['chi_V']:+d}"
                        f" Δ={c['delta_n_d3']:.1f}"
                        f" mu_alpha={c['mu_alpha_best']:.3f} vol={c['vol_J']:.3f}"
                        f" c2V_max={c['c2V_max']:.1f}"
                        f" ext1={'yes' if c['ext1_nonzero'] else 'no'}\n")
                f.write(f"     α={c['alpha']}\n")
                f.write(f"     β={c['betas']}\n\n")
        else:
            f.write("No candidates found.\n")
    print(f"Report:  {out_txt}")


if __name__ == "__main__":
    main()
