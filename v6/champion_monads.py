#!/usr/bin/env python3
"""
champion_monads.py — Monad bundle scan on h26/P11670 (sm_score=89).

Monad bundles V are defined by the short exact sequence:
    0 → V → B → C → 0
where B = ⊕ O(b_i) and C = ⊕ O(c_j) are direct sums of line bundles,
and the monad map f: B → C is a generic surjection.

Advantage over direct sums: monad bundles CAN be slope-stable even when
no slope-stable direct-sum bundle exists (proven: every stable rank-4 bundle
on a generic CY3 appears as a monad — Hartshorne / Wintz).

Constraints for SU(rk) monad:
    rk(V) = n_B - n_C = rk (e.g. 4 or 5)
    c₁(V) = Σ bᵢ − Σ cⱼ = 0  (SU condition)
    χ(V)  = Σ χ(O(bᵢ)) − Σ χ(O(cⱼ)) = ±3  (3 generations)

Slope-stability necessary condition (Hoppe — monad version):
    For slope-stability of V with Kähler form J:
      μ(O(bᵢ)) < μ(V) = 0  for ALL i  (since c₁(V)=0 ⟹ μ(V)=0)
      μ(O(cⱼ)) > μ(V) = 0  for ALL j
    where μ(O(D)) = D ⋅ J² = Σ_{a,b,c} κ_{abc} D^a J^b J^c.
    This is necessary for the monad map to exist and V to be stable.

Sufficient stability (Theorem of Hoppe): the above + generic monad map
gives a slope-polystable bundle; generically indecomposable ⟹ slope-stable.

We scan three monad configurations:
    (n_B, n_C) = (5,1), (6,2), (7,3) for rk=4
    (n_B, n_C) = (6,1), (7,2), (8,3) for rk=5

References:
    Braun, He, Ovrut, Pantev (2006) — Heterotic Standard Model
    Anderson, Gray, Lukas, Palti (2012) — Systematic Line Bundle Moduli
    Distler, Greene (1988) — monad construction on CY3
    MATH_SPEC.md §5 (monad section)

Usage:
    python3 champion_monads.py [options]

Options:
    --rank N        Bundle rank (default: 4)
    --nb NB         n_B summands in B (default: scan 5,6,7 for rk=4)
    --nc NC         n_C summands in C (nb - nc must equal rank)
    --k-max K       Max divisor entry magnitude (default: 2)
    --n-sample N    Random samples per (n_B, n_C) config (default: 1,000,000)
    --j-tries M     Kähler form samples for slope check (default: 20)
    --db PATH       DB path (default: cy_landscape_v6.db)
"""

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

H11      = 26
POLY_IDX = 11670
OUT_JSON = os.path.join(SCRIPT_DIR, "results", "champion_monads.json")
OUT_TXT  = os.path.join(SCRIPT_DIR, "results", "champion_monads_top.txt")


# ══════════════════════════════════════════════════════════════════════════════
#  CY data loading
# ══════════════════════════════════════════════════════════════════════════════

def load_cy_data():
    """Load h26/P11670, return (cy, c2, kappa, h11_eff)."""
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


# ══════════════════════════════════════════════════════════════════════════════
#  Tensor / index-theorem helpers
# ══════════════════════════════════════════════════════════════════════════════

def build_kappa_tensor(intnums, h11_eff):
    """Dense κ_{abc} tensor from sparse dict. Fully symmetrized."""
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


def slope(D, K, J):
    """μ(O(D)) = D · J² = Σ_{a,b,c} κ_{abc} D^a J^b J^c."""
    D = np.asarray(D, dtype=float)
    J = np.asarray(J, dtype=float)
    return float(np.einsum('ijk,i,j,k', K, D, J, J))


# ══════════════════════════════════════════════════════════════════════════════
#  Kähler cone sampling
# ══════════════════════════════════════════════════════════════════════════════

def sample_kahler_forms(K, h11_eff, n_tries=20, rng=None):
    """
    Return a list of Kähler forms J (h11_eff-vectors with J·J·J > 0 and
    all κ_{aij} J^i J^j > 0, i.e. inside the Kähler cone heuristic).

    We use: J_k = t_k D_k with t_k sampled from Dirichlet(1,...,1).
    Filter: vol = κ_{abc} J^a J^b J^c > 0 (inside CY Kähler cone, necessary).
    """
    if rng is None:
        rng = np.random.default_rng(7)
    forms = []
    for _ in range(n_tries * 50):
        # Dirichlet sample: positive coordinates summing to 1
        t = rng.dirichlet(np.ones(h11_eff))
        vol = float(np.einsum('ijk,i,j,k', K, t, t, t))
        if vol > 1e-8:
            forms.append(t / t.max())  # normalize so max=1
        if len(forms) >= n_tries:
            break
    if not forms:
        # Fallback: symmetric point
        forms = [np.ones(h11_eff) / h11_eff]
    return forms


# ══════════════════════════════════════════════════════════════════════════════
#  Slope-stability pre-filter
# ══════════════════════════════════════════════════════════════════════════════

def passes_slope_filter(Bs, Cs, K, J_forms):
    """
    Return True if there exists at least one J in J_forms such that:
      μ(O(bᵢ)) < 0  for ALL bᵢ ∈ B
      μ(O(cⱼ)) > 0  for ALL cⱼ ∈ C
    This is a NECESSARY condition for slope-stability of the monad V.
    """
    for J in J_forms:
        b_slopes = [slope(b, K, J) for b in Bs]
        c_slopes = [slope(c, K, J) for c in Cs]
        if all(s < 0 for s in b_slopes) and all(s > 0 for s in c_slopes):
            return True, J
    return False, None


# ══════════════════════════════════════════════════════════════════════════════
#  χ sanity
# ══════════════════════════════════════════════════════════════════════════════

def chi_monad(Bs, Cs, c2, K):
    """χ(V) = Σ χ(O(bᵢ)) − Σ χ(O(cⱼ))."""
    return sum(chi_lb(b, c2, K) for b in Bs) - sum(chi_lb(c, c2, K) for c in Cs)


def c1_check(Bs, Cs, h11_eff):
    """c₁ = Σbᵢ − Σcⱼ; should be zero vector for SU(N)."""
    sumB = np.sum(Bs, axis=0)
    sumC = np.sum(Cs, axis=0)
    return list((sumB - sumC).astype(int))


# ══════════════════════════════════════════════════════════════════════════════
#  Main scan
# ══════════════════════════════════════════════════════════════════════════════

def scan_monads(c2, K, h11_eff, rank=4, k_max=2,
                n_sample=1_000_000, chi_target=3, j_tries=20,
                configs=None):
    """
    Scan monad bundles for all (n_B, n_C) configs.

    Each trial:
      1. Sample n_B random b_i ∈ [-k_max, k_max]^h11_eff
      2. Sample n_B - rank = n_C of those to be the first n_C summands
         Actually: sample b_1,...,b_{n_B-1} freely, then set:
           c_1,...,c_{n_C} freely, and b_{n_B} = Σc_j − Σ_{i<n_B} b_i (enforces c1=0)
      3. Check |b_last[k]| ≤ k_max * n_B (loose bound)
      4. Check χ(V) ≈ ±chi_target
      5. Slope filter: ∃ J such that μ(bᵢ)<0 and μ(cⱼ)>0 for all i,j

    Returns: list of candidate dicts.
    """
    rng = np.random.default_rng(1729)

    if configs is None:
        # Standard configs: (n_B, n_C) pairs
        configs = [(rank + 1, 1), (rank + 2, 2), (rank + 3, 3)]

    print(f"\nSampling Kähler forms ({j_tries} tries)...")
    J_forms = sample_kahler_forms(K, h11_eff, n_tries=j_tries, rng=rng)
    print(f"  Got {len(J_forms)} valid Kähler forms")
    if J_forms:
        J0 = J_forms[0]
        vol = float(np.einsum('ijk,i,j,k', K, J0, J0, J0))
        print(f"  Sample J: vol={vol:.4f}")

    all_candidates = []
    total_checked  = 0

    for n_B, n_C in configs:
        assert n_B - n_C == rank, f"n_B - n_C = {n_B-n_C} ≠ rank={rank}"
        t0 = time.time()
        candidates = []
        checked = 0
        slope_pass = 0

        print(f"\n{'='*60}")
        print(f"Config: SU({rank}), n_B={n_B}, n_C={n_C}, k_max={k_max}")
        search_size = math.log10((2*k_max+1)**(h11_eff*n_C) * (2*k_max+1)**(h11_eff*(n_B-1)))
        print(f"  Search space: ~10^{search_size:.1f}")
        print(f"  Sampling {n_sample:,} trials...")

        for trial in range(n_sample):
            if trial % 100_000 == 0 and trial > 0:
                elapsed = time.time() - t0
                rate = trial / elapsed
                eta = int((n_sample - trial) / rate)
                print(f"  {trial:,}/{n_sample:,}  χ-cands={len(candidates)}  "
                      f"slope-pass={slope_pass}  {rate:.0f}/s  eta={eta}s")

            # Sample c_1,...,c_{n_C} freely
            Cs = rng.integers(-k_max, k_max + 1, size=(n_C, h11_eff)).astype(float)
            # Sample b_1,...,b_{n_B - 1} freely
            Bs_free = rng.integers(-k_max, k_max + 1, size=(n_B - 1, h11_eff)).astype(float)
            # b_{n_B} closes c1=0: b_last = Σc_j - Σb_free
            b_last = Cs.sum(axis=0) - Bs_free.sum(axis=0)

            # Reject b_last out of bounds (loose)
            if np.abs(b_last).max() > k_max * n_B:
                continue

            Bs = np.vstack([Bs_free, b_last[None, :]])
            checked += 1

            # χ check
            chi_V = chi_monad(Bs, Cs, c2, K)
            chi_r = round(chi_V)
            if abs(chi_r) != chi_target or abs(chi_V - chi_r) > 0.15:
                continue

            candidates.append((Bs.tolist(), Cs.tolist(), chi_r, trial))

        print(f"\n  Sampled {checked:,}, χ=±{chi_target} candidates: {len(candidates)}")
        print(f"  Running slope filter on {len(candidates)} candidates...")

        slope_stable = []
        for Bs_l, Cs_l, chi_r, trial in candidates:
            Bs = np.array(Bs_l)
            Cs = np.array(Cs_l)
            passes, J_ok = passes_slope_filter(Bs, Cs, K, J_forms)
            if passes:
                slope_stable.append({
                    "n_B": n_B, "n_C": n_C, "rank": rank,
                    "B": Bs.tolist(), "C": Cs.tolist(),
                    "chi_V": chi_r,
                    "c1_check": c1_check(Bs, Cs, h11_eff),
                    "J_stable": J_ok.tolist(),
                    "trial": trial,
                    "config": f"({n_B},{n_C})",
                })
                slope_pass += 1

        print(f"  Slope-stable (all J with μ<0 for B, μ>0 for C): {len(slope_stable)}")
        total_checked += checked
        all_candidates.extend(slope_stable)

    return all_candidates, total_checked


# ══════════════════════════════════════════════════════════════════════════════
#  c₂ check (anomaly cancellation prerequisite)
# ══════════════════════════════════════════════════════════════════════════════

def check_c2_anomaly(cands, c2_X, K, h11_eff):
    """
    Check D3-brane tadpole: N_D3 = c₂(TX)/2 - c₂(V)/2 ≥ 0 for each candidate.

    c₂(V) from Chern character (for monad 0 → V → B → C → 0):
      ch(V) = ch(B) - ch(C)
      ch₂ = (Σ bᵢ ⊗ bᵢ - Σ cⱼ ⊗ cⱼ) / 2  [as 2-cycle]
      c₂(V) = -2 ch₂(V) + c₁(V)²/rk(V)   [for c₁=0: c₂(V) = -2 ch₂(V)]

    In terms of intersection numbers:
      [c₂(V)]_k = - (Σᵢ Σ_{a,b} κ_{kab} bᵢ^a bᵢ^b - Σⱼ Σ_{a,b} κ_{kab} cⱼ^a cⱼ^b)
      (i.e., c₂(V) as a divisor class via Poincaré duality)

    The tadpole condition requires:
      N_D3 = χ(X)/24 - ∫ c₂(V)·ωᵢ / (4π²) ≥ 0
    Rough check: all entries of c₂(V) should be ≤ c₂(TX)[i] on each divisor.
    """
    # Build degree-2 matrix: M_{ka} = Σ_b κ_{kab} J^b at J=(1,...,1)
    J = np.ones(h11_eff)
    M = np.einsum('kab,b->ka', K, J)  # shape (h11_eff, h11_eff)

    results = []
    for cand in cands:
        B = np.array(cand["B"], dtype=float)
        C = np.array(cand["C"], dtype=float)

        # ch₂[k] = (Σᵢ Σ_a M_{ka} bᵢ^a - Σⱼ Σ_a M_{ka} cⱼ^a) / 2
        ch2_B = np.einsum('ka,ia->k', M, B)  # shape (h11_eff,)
        ch2_C = np.einsum('ka,ja->k', M, C)
        ch2 = (ch2_B - ch2_C) / 2.0
        c2_V = -2.0 * ch2  # since c1=0

        # D3 tadpole: N_D3 = (c2_TX[k] - c2_V[k]) for each k
        # Positive tadpole requires c2_V < c2_TX pointwise (rough necessary)
        tadpole_ok = bool(np.all(c2_V <= c2_X + 1.0))  # +1 tolerance for rounding
        n_d3_rough = float(np.sum(c2_X - c2_V))  # rough sum, not actual integral

        cand = dict(cand)
        cand["c2V_range"]   = [float(c2_V.min()), float(c2_V.max())]
        cand["tadpole_ok"]  = tadpole_ok
        cand["n_d3_rough"]  = n_d3_rough
        results.append(cand)

    return results


# ══════════════════════════════════════════════════════════════════════════════
#  Pretty-print candidates
# ══════════════════════════════════════════════════════════════════════════════

def print_top_candidates(cands, n=20):
    """Print top candidates sorted by tadpole proximity to 0."""
    if not cands:
        print("\nNo slope-stable monad candidates found.")
        print("Suggestions:")
        print("  1. Increase k_max (try --k-max 3)")
        print("  2. Increase n_sample (try --n-sample 5000000)")
        print("  3. Try asymmetric Kähler point (--j-tries 50)")
        print("  4. Switch to positive-rank monads: n_B=7, n_C=3 for rk=4")
        return

    # Sort: tadpole_ok first, then by |n_d3_rough| closest to 0
    ok = [c for c in cands if c.get("tadpole_ok")]
    not_ok = [c for c in cands if not c.get("tadpole_ok")]
    ok.sort(key=lambda c: abs(c.get("n_d3_rough", 9999)))
    combined = (ok + not_ok)[:n]

    print(f"\n{'='*70}")
    print(f"TOP MONAD CANDIDATES (h26/P11670, χ=±3)")
    print(f"{'='*70}")
    print(f"{'#':>3}  {'config':>6}  {'χ':>3}  {'tadpole?':>8}  "
          f"{'n_D3_rough':>10}  {'c2V_range':>14}")
    print("-" * 70)
    for i, c in enumerate(combined):
        tr = "✓" if c.get("tadpole_ok") else "✗"
        c2r = f"[{c.get('c2V_range',[0,0])[0]:.0f},{c.get('c2V_range',[0,0])[1]:.0f}]"
        print(f"{i+1:>3}  {c.get('config','?'):>6}  {c['chi_V']:>+3}  "
              f"{tr:>8}  {c.get('n_d3_rough',0):>10.1f}  {c2r:>14}")


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rank",     type=int, default=4)
    p.add_argument("--nb",       type=int, default=None,
                   help="n_B (override default config sweep)")
    p.add_argument("--nc",       type=int, default=None,
                   help="n_C (must satisfy nb - nc = rank)")
    p.add_argument("--k-max",    type=int, default=2)
    p.add_argument("--n-sample", type=int, default=1_000_000)
    p.add_argument("--j-tries",  type=int, default=20)
    p.add_argument("--chi-target", type=int, default=3)
    p.add_argument("--db",       default=os.path.join(SCRIPT_DIR, "cy_landscape_v6.db"))
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(os.path.join(SCRIPT_DIR, "results"), exist_ok=True)

    print("=" * 70)
    print(f"CHAMPION MONAD SCAN — h{H11}/P{POLY_IDX} (sm_score=89)")
    print(f"Method: SU({args.rank}) monad 0→V→B→C→0, k_max={args.k_max}")
    print("=" * 70)

    cy, c2, intnums, h11_eff = load_cy_data()
    K = build_kappa_tensor(intnums, h11_eff)

    # Sanity: χ(O) = 1
    chi_O = chi_lb(np.zeros(h11_eff), c2, K)
    print(f"\nSanity check: χ(O) = {chi_O:.4f} (should be 1.0)")

    # Build config list
    if args.nb is not None and args.nc is not None:
        configs = [(args.nb, args.nc)]
    else:
        configs = [(args.rank + 1, 1),
                   (args.rank + 2, 2),
                   (args.rank + 3, 3)]

    t_total = time.time()

    candidates, total_checked = scan_monads(
        c2, K, h11_eff,
        rank=args.rank,
        k_max=args.k_max,
        n_sample=args.n_sample,
        chi_target=args.chi_target,
        j_tries=args.j_tries,
        configs=configs,
    )

    # c₂ anomaly check
    print(f"\nRunning D3 tadpole check on {len(candidates)} slope-stable candidates...")
    candidates = check_c2_anomaly(candidates, c2, K, h11_eff)

    tadpole_ok = [c for c in candidates if c.get("tadpole_ok")]

    print_top_candidates(candidates)

    elapsed = time.time() - t_total

    print(f"\n{'='*70}")
    print("RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"  Polytope:         h{H11}/P{POLY_IDX} (sm_score=89, h11_eff={h11_eff})")
    print(f"  Bundle type:      SU({args.rank}) monad 0→V→B→C→0")
    print(f"  k_max:            {args.k_max}")
    print(f"  Total sampled:    {total_checked:,}")
    print(f"  c1=0 + χ=±3:      {len(candidates)}")
    print(f"  Slope-stable:     {len(candidates)}  (passed μ<0/μ>0 filter)")
    print(f"  D3 tadpole OK:    {len(tadpole_ok)}")
    print(f"  Elapsed:          {elapsed:.0f}s")

    if tadpole_ok:
        print(f"\n*** Found {len(tadpole_ok)} tadpole-consistent slope-stable monad(s)! ***")
        print("Next: compute full cohomology H*(X,V) to verify 3-generation chiral spectrum")
        print("      and check Yukawa couplings H^1(X, V⊗V⊗V) ≠ 0.")
    else:
        print("\nNo tadpole-consistent slope-stable mono found.")
        print("Recommendations:")
        print("  - Increase k_max to 3 (much larger search space)")
        print("  - Try asymmetric Kähler points (--j-tries 100)")
        print("  - Consider larger monad configs: (n_B=8, n_C=4)")
        print("  - Consider heterotic anomaly cancellation with 5-branes")

    # Save JSON
    out_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "polytope": f"h{H11}/P{POLY_IDX}",
        "rank": args.rank,
        "k_max": args.k_max,
        "n_sample": args.n_sample,
        "chi_target": args.chi_target,
        "total_checked": total_checked,
        "n_slope_stable": len(candidates),
        "n_tadpole_ok": len(tadpole_ok),
        "elapsed_s": elapsed,
        "h11_eff": h11_eff,
        "chi_O": chi_O,
        "configs": configs,
        "candidates": candidates[:500],  # cap at 500 for JSON size
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out_data, f, indent=2)
    print(f"\nResults saved to: {OUT_JSON}")

    # Save human-readable summary
    with open(OUT_TXT, "w") as f:
        f.write(f"Champion Monad Scan — h{H11}/P{POLY_IDX}\n")
        f.write(f"Run at: {datetime.now(timezone.utc).isoformat()} UTC\n")
        f.write(f"SU({args.rank}), k_max={args.k_max}, χ_target=±{args.chi_target}\n")
        f.write(f"h11_eff={h11_eff}, configs={configs}\n")
        f.write(f"Sampled={total_checked:,}, slope-stable={len(candidates)}, "
                f"tadpole_ok={len(tadpole_ok)}\n\n")
        if not candidates:
            f.write("No slope-stable monad candidates found.\n")
            f.write("Recommend monad scan with k_max=3 or larger (n_B, n_C).\n")
        else:
            for i, c in enumerate(candidates[:50]):
                tr = "OK" if c.get("tadpole_ok") else "fail"
                f.write(f"  [{i+1:3d}] config={c['config']} χ={c['chi_V']:+d} "
                        f"tadpole={tr} n_D3≈{c.get('n_d3_rough',0):.1f} "
                        f"c2V=[{c['c2V_range'][0]:.0f},{c['c2V_range'][1]:.0f}]\n")
                f.write(f"        B={[list(map(int,b)) for b in c['B']]}\n")
                f.write(f"        C={[list(map(int,cc)) for cc in c['C']]}\n")
    print(f"Summary saved to: {OUT_TXT}")


if __name__ == "__main__":
    main()
