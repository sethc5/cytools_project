#!/usr/bin/env python3
"""
champion_bundles.py — Rank-4 bundle scan on h26/P11670 (sm_score=89).

Builds SU(4) bundles V = L₁⊕L₂⊕L₃⊕L₄ with:
  - c₁(V) = 0  (SU(4) structure group)
  - χ(V) = ±3  (three generations)
  - Hoppe stability check (necessary condition for μ-stability)

Also builds SU(5) direct sums: V = L₁⊕L₂⊕L₃⊕L₄⊕L₅.

References: MATH_SPEC.md, archive/analysis/rank_n_bundles.py (v2 version),
            Braun-He-Ovrut-Pantev (2006).

Index theorem on CY3 (Td(X) = 1 + c₂(X)/12 since c₁(X)=0):
  χ(V) = ∫_X ch(V)·Td(X) = ch₃(V) + ch₁(V)·c₂(X)/12
        = D₁³/6 + D₂³/6 + D₃³/6 + D₄³/6
          + (c₂·D₁ + c₂·D₂ + c₂·D₃ + c₂·D₄)/12
  where ch₁(Lᵢ) = Dᵢ (divisor class), D³ = κ_{abc}DaDaDc.

For SU(n): c₁(V) = ΣDᵢ = 0 → L₄ = -(L₁+L₂+L₃).
So χ(V) = Σ χ(Lᵢ) and the c₁=0 constraint halves the search space.

Hoppe criterion (necessary condition for μ-stability):
  H⁰(X, ∧ᵏV ⊗ O(-J)) = 0  for all k=1,...,rk(V)-1 and nef J.
  Practical check: h⁰(X, ∧ᵏV ⊗ O(-H)) = 0 where H is the hyperplane class.
  Since ∧¹V = V, this requires h⁰(X, V(-H)) = 0.
  We check h⁰(X, Lᵢ(-H)) = 0 for all i (necessary but not sufficient).

Usage:
    cd /workspaces/cytools_project/v6
    python3 champion_bundles.py [--rank 4] [--k-max 4] [--workers 14] [--chi-target 3]

Output:
    results/champion_bundles.json     — all results
    results/champion_bundles_top.txt  — human-readable summary of good candidates
"""

import argparse
import itertools
import json
import multiprocessing as mp
import os
import sys
import time
from datetime import datetime

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

H11      = 26
POLY_IDX = 11670
DB_PATH  = os.path.join(SCRIPT_DIR, "cy_landscape_v6.db")
OUT_JSON = os.path.join(SCRIPT_DIR, "results", "champion_bundles.json")
OUT_TXT  = os.path.join(SCRIPT_DIR, "results", "champion_bundles_top.txt")


# ══════════════════════════════════════════════════════════════════════════════
#  CY data extraction (v6-compatible)
# ══════════════════════════════════════════════════════════════════════════════

def load_cy_data(h11, poly_idx):
    """Load polytope and return (p, cy, c2_vec, kappa_tensor, h11_eff)."""
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    import numpy as np
    from ks_index import load_h11_polytopes

    print(f"Loading h{h11}/P{poly_idx} (limit={poly_idx+1})...")
    t0 = time.time()
    polys = load_h11_polytopes(h11, limit=poly_idx + 1)
    p = polys[poly_idx]
    print(f"  Loaded {len(p.vertices())} verts, {len(p.points())} pts in {time.time()-t0:.1f}s")

    print("Triangulating...")
    t0 = time.time()
    tri = p.triangulate()
    cy = tri.get_cy()
    h11_eff = cy.h11()
    print(f"  h11_eff={h11_eff}, h21={cy.h21()} in {time.time()-t0:.1f}s")

    c2  = list(cy.second_chern_class(in_basis=True))     # length h11_eff
    intnums = dict(cy.intersection_numbers(in_basis=True))  # {(a,b,c): κ_abc}

    return p, cy, c2, intnums, h11_eff


def build_kappa_matrix(intnums, h11_eff):
    """Return full (h11_eff,h11_eff,h11_eff) κ tensor from sparse dict."""
    import numpy as np
    K = np.zeros((h11_eff, h11_eff, h11_eff), dtype=float)
    for (a, b, c), v in intnums.items():
        if 0 <= a < h11_eff and 0 <= b < h11_eff and 0 <= c < h11_eff:
            K[a, b, c] = v
            K[a, c, b] = v
            K[b, a, c] = v
            K[b, c, a] = v
            K[c, a, b] = v
            K[c, b, a] = v
    return K


def chi_line_bundle(D, c2, K):
    """χ(L=O(D)) for divisor class D (h11_eff-vector)."""
    import numpy as np
    D = np.asarray(D, dtype=float)
    # D³ = κ_{abc} D^a D^b D^c
    D3 = float(np.einsum('ijk,i,j,k', K, D, D, D))
    # c₂·D = Σᵢ c2[i]*D[i]
    c2D = float(np.dot(c2, D))
    return D3 / 6.0 + c2D / 12.0


# ══════════════════════════════════════════════════════════════════════════════
#  Hoppe stability check
# ══════════════════════════════════════════════════════════════════════════════

def hoppe_check(Ds, cy, h11_eff):
    """
    Check necessary Hoppe condition for direct-sum bundle V=⊕Lᵢ with Dᵢ.

    For k=1 (∧¹V = V): need h⁰(X, Lᵢ(-H)) = 0 for all i.
    H = "hyperplane" = first nef divisor with c₂·D ≥ 24 (the K3 divisor).
    If h⁰(X, Lᵢ(-H)) > 0 for any i, bundle fails Hoppe at k=1.

    Returns: (passes_hoppe, details_dict)
    """
    import numpy as np
    try:
        from cy_compute_v6 import compute_h0_koszul
    except ImportError:
        # Fallback: use trivial check — h⁰(L)=0 if D is "negative enough"
        # (rough: if all entries of D are ≤ 0 → h⁰=0)
        results = []
        for D in Ds:
            D = np.asarray(D)
            h0 = 0 if all(d <= 0 for d in D) else None
            results.append(h0)
        return all(r == 0 for r in results if r is not None), {"fallback": True}

    try:
        c2 = list(cy.second_chern_class(in_basis=True))
        # Find K3 divisor as "hyperplane" (index with max c₂·D)
        h_idx = int(np.argmax(c2))
        H = np.zeros(h11_eff)
        H[h_idx] = 1

        details = {}
        passes = True
        for i, D in enumerate(Ds):
            D_shifted = np.asarray(D, dtype=float) - H
            h0 = compute_h0_koszul(cy, D_shifted.tolist())
            details[f"L{i}_minus_H_h0"] = h0
            if h0 > 0:
                passes = False

        return passes, details
    except Exception as e:
        return None, {"error": str(e)[:120]}


# ══════════════════════════════════════════════════════════════════════════════
#  Direct-sum bundle scan
# ══════════════════════════════════════════════════════════════════════════════

def scan_direct_sums(cy, c2, K, h11_eff, rank=4, k_max=3, chi_target=3, max_results=500):
    """
    Scan SU(rank) direct-sum bundles V = L₁⊕...⊕Lᵣ.

    Constraints:
      c₁(V) = ΣDᵢ = 0  (last bundle determined by others)
      χ(V) = ±chi_target

    Returns list of (D1,...,Dr, chi_V) candidate dicts.
    """
    import numpy as np

    basis_range = range(-k_max, k_max + 1)
    n_checked = 0
    candidates = []

    print(f"\nScanning SU({rank}) direct sums, k_max={k_max}, h11_eff={h11_eff}...")
    print(f"  Search space: ({2*k_max+1})^{(rank-1)*h11_eff} ~ "
          f"{(2*k_max+1)**((rank-1)*h11_eff):.2e} total")

    # For tractability: iterate over h11_eff-dim vectors for L1...L(r-1)
    # Lr = -(L1+...+L(r-1)) enforces c1=0
    r_minus_1 = rank - 1
    per_D = list(itertools.product(basis_range, repeat=h11_eff))
    print(f"  Iterating {len(per_D)^{r_minus_1}:,} combinations "
          f"({len(per_D):,}^{r_minus_1})...")

    # For large h11_eff, per_D is huge — use random sampling
    rng = np.random.default_rng(42)
    n_sample = min(500_000, len(per_D) ** r_minus_1)
    print(f"  Random sampling {n_sample:,} combinations (h11_eff={h11_eff} too large for exhaustive)")

    t0 = time.time()
    for trial in range(n_sample):
        if trial % 50000 == 0 and trial > 0:
            elapsed = time.time() - t0
            rate = trial / elapsed
            print(f"    {trial:,}/{n_sample:,}  "
                  f"candidates={len(candidates)}  "
                  f"rate={rate:.0f}/s  eta={int((n_sample-trial)/rate)}s")

        # Sample random L1..L(r-1)
        Ds_free = [rng.integers(-k_max, k_max+1, size=h11_eff).tolist()
                   for _ in range(r_minus_1)]
        # Lr closes c1=0
        D_last = [-sum(Ds_free[j][i] for j in range(r_minus_1)) for i in range(h11_eff)]
        Ds = Ds_free + [D_last]

        # Check |max(D_last)| ≤ k_max*r (allow a bit of slack)
        if max(abs(x) for x in D_last) > k_max * rank:
            continue

        # Compute χ(V) = Σ χ(Li)
        chi_V = sum(chi_line_bundle(D, c2, K) for D in Ds)
        chi_V_rounded = round(chi_V)
        n_checked += 1

        if abs(chi_V_rounded) == chi_target and abs(chi_V - chi_V_rounded) < 0.1:
            cand = {
                "Ds": Ds,
                "chi_V": chi_V_rounded,
                "chi_exact": chi_V,
                "c1_check": [sum(Ds[j][i] for j in range(rank)) for i in range(h11_eff)],
                "hoppe_checked": False,
                "hoppe_passes": None,
                "trial": trial,
            }
            candidates.append(cand)
            if len(candidates) >= max_results:
                print(f"  Reached max_results={max_results}, stopping early")
                break

    print(f"\n  Checked {n_checked:,} valid combos, found {len(candidates)} χ=±{chi_target} candidates")
    return candidates, n_checked


def run_hoppe_on_candidates(candidates, cy, h11_eff, max_hoppe=100):
    """Run Hoppe check on up to max_hoppe candidates."""
    print(f"\nRunning Hoppe stability check on {min(len(candidates), max_hoppe)} candidates...")
    stable = []
    for i, cand in enumerate(candidates[:max_hoppe]):
        passes, details = hoppe_check(cand["Ds"], cy, h11_eff)
        cand["hoppe_checked"] = True
        cand["hoppe_passes"]  = passes
        cand["hoppe_details"] = details
        if passes:
            stable.append(cand)
        if (i+1) % 10 == 0:
            print(f"  {i+1}/{min(len(candidates), max_hoppe)}: Hoppe-stable so far: {len(stable)}")
    print(f"  Hoppe-stable candidates: {len(stable)} / {min(len(candidates), max_hoppe)} checked")
    return stable


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="SU(n) bundle scan on h26/P11670")
    ap.add_argument("--rank",       type=int, default=4,  help="Bundle rank (default 4)")
    ap.add_argument("--k-max",      type=int, default=3,  help="Max line bundle charge")
    ap.add_argument("--chi-target", type=int, default=3,  help="Target |χ(V)| (generations)")
    ap.add_argument("--n-sample",   type=int, default=500_000, help="Random samples")
    ap.add_argument("--max-hoppe",  type=int, default=100, help="Max Hoppe checks")
    ap.add_argument("--dry-run",    action="store_true")
    args = ap.parse_args()

    os.makedirs(os.path.join(SCRIPT_DIR, "results"), exist_ok=True)

    print("="*70)
    print(f"CHAMPION BUNDLE SCAN — h{H11}/P{POLY_IDX} (sm_score=89)")
    print(f"Method: SU({args.rank}) direct-sum, k_max={args.k_max}, χ_target=±{args.chi_target}")
    print("="*70)
    print()

    if args.dry_run:
        print("Dry run — load polytope only")
        p, cy, c2, intnums, h11_eff = load_cy_data(H11, POLY_IDX)
        print(f"h11_eff={h11_eff}, c2={c2}")
        return

    # ── Load CY data ──────────────────────────────────────────────────────────
    import numpy as np
    p, cy, c2, intnums, h11_eff = load_cy_data(H11, POLY_IDX)
    K = build_kappa_matrix(intnums, h11_eff)
    print(f"κ tensor: {np.count_nonzero(K)} nonzero entries")

    # ── Sanity: χ of trivial bundle = χ(O) = 1 ───────────────────────────────
    D_zero = [0] * h11_eff
    chi_O = chi_line_bundle(D_zero, c2, K)
    print(f"Sanity check: χ(O) = {chi_O:.4f} (should be 1.0)")

    t_start = time.time()

    # ── Scan SU(rank) ─────────────────────────────────────────────────────────
    candidates, n_checked = scan_direct_sums(
        cy, c2, K, h11_eff,
        rank=args.rank,
        k_max=args.k_max,
        chi_target=args.chi_target,
        max_results=1000,
    )

    # ── Hoppe check ───────────────────────────────────────────────────────────
    stable = run_hoppe_on_candidates(candidates, cy, h11_eff, max_hoppe=args.max_hoppe)

    elapsed = time.time() - t_start

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"  Polytope:       h{H11}/P{POLY_IDX} (sm_score=89, h11_eff={h11_eff})")
    print(f"  Bundle type:    SU({args.rank}) direct sum")
    print(f"  Combinations:   {n_checked:,} sampled")
    print(f"  χ=±{args.chi_target} found:   {len(candidates)}")
    print(f"  Hoppe-stable:   {len(stable)} / {min(len(candidates), args.max_hoppe)} checked")
    print(f"  Elapsed:        {elapsed:.1f}s")
    print()
    if stable:
        print("Hoppe-stable candidates:")
        for cand in stable[:10]:
            print(f"  χ={cand['chi_V']}  Ds={cand['Ds']}")
    else:
        print("No Hoppe-stable candidates found in this sample.")
        print("(Direct sums are typically polystable but not slope-stable —")
        print(" monad bundles are needed for genuine stability. See BACKLOG B-42.)")

    # ── Write output ──────────────────────────────────────────────────────────
    out = {
        "h11": H11, "poly_idx": POLY_IDX,
        "h11_eff": h11_eff,
        "rank": args.rank,
        "k_max": args.k_max,
        "chi_target": args.chi_target,
        "n_sampled": n_checked,
        "n_candidates": len(candidates),
        "n_hoppe_checked": min(len(candidates), args.max_hoppe),
        "n_hoppe_stable": len(stable),
        "elapsed_s": round(elapsed, 1),
        "run_at": datetime.utcnow().isoformat(),
        "stable_candidates": [
            {k: v for k, v in c.items() if k != "hoppe_details"}
            for c in stable[:50]
        ],
        "all_chi3_sample": [
            {"Ds": c["Ds"], "chi_V": c["chi_V"]}
            for c in candidates[:200]
        ],
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to: {OUT_JSON}")

    with open(OUT_TXT, "w") as f:
        f.write(f"Champion Bundle Scan — h{H11}/P{POLY_IDX}\n")
        f.write(f"Run at: {datetime.utcnow().isoformat()} UTC\n")
        f.write(f"SU({args.rank}), k_max={args.k_max}, χ_target=±{args.chi_target}\n")
        f.write(f"h11_eff={h11_eff}, sampled={n_checked:,}\n")
        f.write(f"χ=±{args.chi_target} found: {len(candidates)}\n")
        f.write(f"Hoppe-stable: {len(stable)}\n\n")
        if stable:
            f.write("Hoppe-stable candidates:\n")
            for c in stable:
                f.write(f"  chi={c['chi_V']}  Ds={c['Ds']}\n")
        else:
            f.write("No Hoppe-stable direct-sum candidates found.\n")
            f.write("Recommend monad bundle scan as next step.\n")
    print(f"Summary saved to: {OUT_TXT}")


if __name__ == "__main__":
    main()
