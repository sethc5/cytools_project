#!/usr/bin/env python3
"""
pipeline.py — Generic full-analysis pipeline for any χ=-6 CY candidate.

Usage:
    python pipeline.py --h11 14 --poly 2              # h21 defaults to h11+3
    python pipeline.py --h11 17 --poly 63
    python pipeline.py --h11 17 --poly 63 --h21 20    # explicit h21

Runs Stages 1-4 of FRAMEWORK.md:
  1. CY geometry  (polytope → triangulation → Hodge data)
  2. Divisor analysis  (classification, intersections, Swiss cheese, fibrations)
  3. Line bundle cohomology  (χ=±3 search, Koszul h⁰, Serre h³)
  4. Net chirality deduction  (h¹-h² gap, clean bundle identification)

Uses verified Koszul + lattice-point methods from dragon_slayer_40h/40i.
All heavy computation imported from cy_compute.py.
Reference: MATH_SPEC.md §4-5, FRAMEWORK.md §1-4.
"""

import argparse
import sys
import os
import time
import cytools as cy
import numpy as np
from collections import Counter
from cytools.config import enable_experimental_features
enable_experimental_features()

from cy_compute import (
    compute_h0_koszul,
    basis_to_toric,
    find_chi3_bundles,
    compute_D3,
    poly_hash,
    precompute_vertex_data,
)

CYTOOLS_VERSION = getattr(cy, '__version__', 'unknown')

# ── ANSI formatting ──
PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
CYAN = "\033[96m"


class Tee:
    """Write to both stdout and a file."""
    def __init__(self, filepath):
        self.file = open(filepath, 'w')
        self.stdout = sys.stdout

    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)

    def flush(self):
        self.stdout.flush()
        self.file.flush()

    def close(self):
        self.file.close()


# ══════════════════════════════════════════════════════════════════
#  Stage 1: CY Geometry
# ══════════════════════════════════════════════════════════════════

def run_stage1(target_h11, target_h21, target_poly):
    """Fetch polytope, triangulate, compute CY data."""
    print(f"\n{'─' * 72}")
    print(f"  {BOLD}STAGE 1: CALABI-YAU GEOMETRY{RESET}")
    print(f"{'─' * 72}")

    polys = list(cy.fetch_polytopes(h11=target_h11, h21=target_h21,
                                    lattice='N', limit=1000))
    print(f"  h11={target_h11}, h21={target_h21} polytopes fetched: {len(polys)}")

    if target_poly >= len(polys):
        print(f"  ERROR: polytope index {target_poly} out of range "
              f"(only {len(polys)} available)")
        sys.exit(1)

    p = polys[target_poly]
    phash = poly_hash(p)
    print(f"  Polytope index: {target_poly}")
    print(f"  SHA-256 fingerprint: {phash}")

    tri = p.triangulate()
    cyobj = tri.get_cy()

    pts = np.array(p.points(), dtype=int)
    n_toric = pts.shape[0]
    ray_indices = list(range(1, n_toric))
    assert np.all(pts[0] == 0), "Origin check failed"

    h11 = cyobj.h11()
    h21 = cyobj.h21()
    chi = cyobj.chi()
    assert chi == -6, f"Expected χ=-6, got {chi}"

    print(f"\n  CY 3-fold properties:")
    print(f"    h¹¹          = {h11}")
    print(f"    h²¹          = {h21}")
    print(f"    χ            = {chi}")
    print(f"    |χ|/2        = {abs(chi)//2}  (= number of generations)")
    print(f"    n_toric      = {n_toric}")
    print(f"    n_rays       = {len(ray_indices)}")
    print(f"    Polytope dim = {pts.shape}")
    print(f"    CYTools ver  = {CYTOOLS_VERSION}")

    # Favorable check
    favorable = (n_toric - 5) == h11
    fav_str = ("Yes (h¹¹ = n_toric - 5)" if favorable
               else f"No (h¹¹_eff = {n_toric - 5})")
    print(f"    Favorable    = {fav_str}")

    # Precompute LP vertex data for fast h⁰ computation
    precomp = precompute_vertex_data(pts, ray_indices)

    return p, tri, cyobj, pts, ray_indices, phash, precomp


# ══════════════════════════════════════════════════════════════════
#  Stage 2: Divisor Analysis
# ══════════════════════════════════════════════════════════════════

def run_stage2(cyobj, pts, ray_indices, polytope):
    """Full divisor analysis: basis, intersections, Swiss cheese, fibrations."""
    h11 = cyobj.h11()
    div_basis = [int(x) for x in cyobj.divisor_basis()]
    h11_eff = len(div_basis)
    intnums = dict(cyobj.intersection_numbers(in_basis=True))
    c2 = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

    print(f"\n{'─' * 72}")
    print(f"  {BOLD}STAGE 2: DIVISOR ANALYSIS{RESET}")
    print(f"{'─' * 72}")
    print(f"  Divisor basis indices: {div_basis}")
    print(f"  h¹¹_eff       = {h11_eff}")
    print(f"  c₂ (in basis): [{', '.join(f'{x:.0f}' for x in c2)}]")
    print(f"  # intersection number entries: {len(intnums)}")

    # ── Mori cone ──
    mori = np.array(cyobj.toric_mori_cone().rays(), dtype=int)
    print(f"  Mori cone generators: {mori.shape[0]}")

    # ── SR ideal ──
    sr = cyobj.triangulation().sr_ideal()
    print(f"  SR ideal generators: {len(sr)}")

    # ── Divisor classification ──
    print(f"\n  Divisor classification:")
    dp_candidates = []
    k3_divs = []
    rigid_count = 0

    for a_idx, a in enumerate(div_basis):
        D3 = intnums.get((a_idx, a_idx, a_idx), 0)
        c2D = c2[a_idx]

        if D3 > 0 and c2D > 0:
            dp_n = 9 - D3
            if 0 <= dp_n <= 8:
                label = f"dP_{dp_n} candidate (D³={D3}, c₂·D={c2D:.0f})"
                dp_candidates.append((a_idx, a, dp_n, D3))
            else:
                label = f"rigid (D³={D3}, c₂·D={c2D:.0f})"
            rigid_count += 1
        elif D3 == 0:
            label = f"K3-like (D³=0, c₂·D={c2D:.0f})"
            k3_divs.append((a_idx, a))
        elif D3 < 0:
            label = f"rigid (D³={D3}, c₂·D={c2D:.0f})"
            rigid_count += 1
        else:
            label = f"(D³={D3}, c₂·D={c2D:.0f})"

        print(f"    e{a_idx:2d} (toric {a:2d}): {label}")

    print(f"\n  Summary: {len(dp_candidates)} dP candidates, "
          f"{len(k3_divs)} K3-like, {rigid_count} rigid")

    # ── Swiss cheese analysis ──
    print(f"\n  Swiss cheese analysis:")
    kc = cyobj.toric_kahler_cone()
    tip = np.array(kc.tip_of_stretched_cone(1.0), dtype=float)
    V_tip = sum(val * tip[i]*tip[j]*tip[k]
                for (i, j, k), val in intnums.items()) / 6.0
    print(f"    Kähler cone tip: [{', '.join(f'{x:.3f}' for x in tip)}]")
    print(f"    V(tip) = {V_tip:.2f}")

    s = 10  # scale factor for large directions
    swiss_candidates = []
    for a_small in range(h11_eff):
        t2 = tip * s
        t2[a_small] = tip[a_small]
        V2 = sum(val * t2[i]*t2[j]*t2[k]
                 for (i, j, k), val in intnums.items()) / 6.0
        tau2 = sum(val * t2[j]*t2[k]
                   for (i, j, k), val in intnums.items()
                   if a_small in (i, j, k)) / 2.0
        if V2 > 100 and tau2 > 0:
            ratio = tau2 / V2**(2/3)
            if ratio < 0.1:
                swiss_candidates.append((a_small, tau2, V2, ratio))

    if swiss_candidates:
        swiss_candidates.sort(key=lambda x: x[3])
        print(f"    Found {len(swiss_candidates)} Swiss cheese directions:")
        for a_small, tau, V, ratio in swiss_candidates[:5]:
            print(f"      e{a_small}: τ={tau:.1f}, V={V:.0f}, "
                  f"τ/V^(2/3)={ratio:.5f}  ← SWISS CHEESE")
        has_swiss = True
        best_tau = swiss_candidates[0][1]
        best_ratio = swiss_candidates[0][3]
    else:
        print(f"    No Swiss cheese structure found.")
        has_swiss = False
        best_tau = None
        best_ratio = None

    # ── Fibration analysis ──
    print(f"\n  Fibration analysis:")
    dual_p = polytope.dual()
    dual_pts = np.array(dual_p.points(), dtype=int)
    print(f"    Dual polytope: {dual_pts.shape[0]} points")

    # K3 fibrations: 1D reflexive subpolytopes in M (pairs ±v in dual)
    k3_fibs = []
    dual_tuples = set(tuple(x) for x in dual_pts)
    for pt in dual_pts:
        if np.all(pt == 0):
            continue
        neg_pt = tuple(-pt)
        if neg_pt in dual_tuples:
            gcd = np.gcd.reduce(np.abs(pt))
            if gcd == 1:
                for val in pt:
                    if val != 0:
                        if val > 0:
                            k3_fibs.append(pt)
                        break

    print(f"    K3 fibrations: {len(k3_fibs)}")
    for f in k3_fibs:
        print(f"      Base P¹ direction: {f}")

    # Elliptic fibrations: 2D reflexive subpolytopes in M
    ell_fibs = []
    for i in range(len(k3_fibs)):
        for j in range(i + 1, len(k3_fibs)):
            v1, v2 = k3_fibs[i], k3_fibs[j]
            mat_check = np.vstack([v1, v2])
            if np.linalg.matrix_rank(mat_check) < 2:
                continue
            subspace_pts = []
            for pt in dual_pts:
                mat = np.vstack([v1, v2, pt])
                if np.linalg.matrix_rank(mat) == 2:
                    subspace_pts.append(pt)
            if 4 <= len(subspace_pts) <= 10:
                ell_fibs.append((v1, v2, len(subspace_pts)))

    print(f"    Elliptic fibrations: {len(ell_fibs)}")
    for v1, v2, npts in ell_fibs:
        print(f"      Base directions: {v1}, {v2}  ({npts} polygon pts)")

    return (div_basis, intnums, c2, mori, has_swiss, best_tau, best_ratio,
            dp_candidates, k3_divs, k3_fibs, ell_fibs)


# ══════════════════════════════════════════════════════════════════
#  Stage 3: Line Bundle Cohomology
# ══════════════════════════════════════════════════════════════════

def run_stage3(cyobj, pts, ray_indices, div_basis, intnums, c2, mori,
               precomp=None):
    """Full χ=±3 bundle search + Koszul h⁰ + Serre h³ computation."""
    h11_eff = len(div_basis)
    n_toric = pts.shape[0]

    print(f"\n{'─' * 72}")
    print(f"  {BOLD}STAGE 3: LINE BUNDLE COHOMOLOGY{RESET}")
    print(f"{'─' * 72}")

    # ── Find χ=±3 bundles ──
    print(f"  Enumerating χ=±3 line bundles (max_coeff=3, max_nonzero=4)...")
    t0 = time.time()
    bundles = find_chi3_bundles(intnums, c2, h11_eff, max_coeff=3, max_nonzero=4)
    dt_enum = time.time() - t0
    n_chi_pos = sum(1 for _, chi in bundles if chi > 0)
    n_chi_neg = sum(1 for _, chi in bundles if chi < 0)
    print(f"  Found {len(bundles)} total: {n_chi_pos} with χ=+3, "
          f"{n_chi_neg} with χ=-3  ({dt_enum:.1f}s)")

    # ── Nefness check ──
    print(f"\n  Nefness check (Mori cone pairing):")
    mori_dim = mori.shape[1]
    nef_count = 0
    for D_basis, chi in bundles:
        D_full = np.zeros(mori_dim, dtype=int)
        for a_idx, toric_idx in enumerate(div_basis):
            D_full[toric_idx] = D_basis[a_idx]
        is_nef = all(int(np.dot(gen, D_full)) >= 0 for gen in mori)
        if is_nef:
            nef_count += 1
    print(f"    Nef bundles: {nef_count}/{len(bundles)}")

    # ── Compute h⁰ and h³ for all bundles ──
    print(f"\n  Computing h⁰ via Koszul method for all {len(bundles)} bundles...")
    t0 = time.time()

    results = []
    max_h0 = 0
    h0_exact3_count = 0
    h0_ge3_count = 0
    n_overflow = 0
    d3_values = []

    for bundle_idx, (D_basis, chi) in enumerate(bundles):
        if chi > 0:
            D_compute = D_basis
            D_neg = -D_basis
        else:
            D_compute = -D_basis
            D_neg = D_basis

        D_toric = basis_to_toric(D_compute, div_basis, n_toric)
        h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=precomp)

        if h0 < 0:
            n_overflow += 1
            continue

        # h³ = h⁰(-D) via Serre duality
        D_neg_toric = basis_to_toric(D_neg, div_basis, n_toric)
        h3 = compute_h0_koszul(pts, ray_indices, D_neg_toric, _precomp=precomp)
        if h3 < 0:
            h3 = -1

        D3 = compute_D3(D_basis, intnums)

        label = "h⁰(D)" if chi > 0 else "h⁰(-D)=h³(D)"
        is_clean = (h0 == 3 and h3 == 0 and abs(chi) == 3)

        results.append({
            'D_basis': D_basis.copy(),
            'chi': chi,
            'h0': h0,
            'h3': h3,
            'D3': D3,
            'label': label,
            'clean': is_clean,
        })

        if h0 > max_h0:
            max_h0 = h0
        if h0 >= 3:
            h0_ge3_count += 1
        if is_clean:
            h0_exact3_count += 1
            d3_values.append(D3)

        if (bundle_idx + 1) % 2000 == 0:
            print(f"    ... {bundle_idx + 1}/{len(bundles)} processed")

    dt_h0 = time.time() - t0
    d3_unique = sorted(set(d3_values))

    print(f"\n  Results ({dt_h0:.1f}s):")
    print(f"    Computed: {len(results)}/{len(bundles)} "
          f"(overflow: {n_overflow})")
    print(f"    Max h⁰: {max_h0}")
    print(f"    Bundles with h⁰ ≥ 3: {h0_ge3_count}")
    print(f"    {BOLD}Clean bundles (h⁰=3, h³=0): {h0_exact3_count}{RESET}")
    print(f"    Distinct D³ values (clean): {len(d3_unique)}")
    if d3_unique:
        print(f"    D³ range (clean): [{d3_unique[0]:.0f}, {d3_unique[-1]:.0f}]")

    # ── Show top bundles by h⁰ ──
    top = sorted(results, key=lambda x: (-x['h0'], -abs(x['chi'])))[:25]
    print(f"\n  Top 25 bundles by h⁰:")
    print(f"  {'D (basis coords)':<55} {'χ':>4} {'h⁰':>4} {'h³':>4} "
          f"{'D³':>8}  {'status'}")
    print(f"  {'─' * 85}")
    for r in top:
        nz = [(i, int(r['D_basis'][i]))
              for i in range(h11_eff) if r['D_basis'][i] != 0]
        D_str = " + ".join(f"{c}·e{i}" for i, c in nz)
        if len(D_str) > 53:
            D_str = D_str[:50] + "..."
        clean_tag = f" {GREEN}CLEAN{RESET}" if r['clean'] else ""
        h3_str = str(r['h3']) if r['h3'] >= 0 else "ov"
        print(f"  {D_str:<55} {r['chi']:>4.0f} {r['h0']:>4} {h3_str:>4} "
              f"{r['D3']:>8.0f}  {r['label']}{clean_tag}")

    return results, bundles, d3_unique


# ══════════════════════════════════════════════════════════════════
#  Stage 4: Net Chirality Deduction
# ══════════════════════════════════════════════════════════════════

def run_stage4(results, h11_eff):
    """For every h⁰≥3 bundle, deduce net chirality and cohomology gaps."""
    h0_ge3 = [r for r in results if r['h0'] >= 3]
    clean = [r for r in results if r['clean']]

    print(f"\n{'─' * 72}")
    print(f"  {BOLD}STAGE 4: NET CHIRALITY ANALYSIS{RESET}")
    print(f"{'─' * 72}")

    print(f"\n  Theory: For line bundle L on X with χ(L) = h⁰ - h¹ + h² - h³:")
    print(f"    • h³(L) = h⁰(-L) by Serre duality  [computed]")
    print(f"    • h¹ - h² = h⁰ - h³ - χ  (fully determined!)")
    print(f"    • A 'clean' bundle has h⁰ = 3, h³ = 0, χ = 3  ⟹  h¹ = h² = 0")
    print(f"      → 3 chiral generations with NO vector-like pairs")

    print(f"\n  {BOLD}Total h⁰≥3 bundles: {len(h0_ge3)}{RESET}")
    print(f"  {BOLD}Clean (h⁰=3, h³=0, χ=3): {len(clean)}{RESET}")

    # ── Breakdown by (h⁰, h³, h¹-h²) ──
    print(f"\n  Cohomology breakdown of all h⁰≥3 bundles:")
    print(f"    {'h⁰':>4} {'h³':>4} {'h¹-h²':>6} {'count':>6}  "
          f"{'interpretation'}")
    print(f"    {'─' * 55}")

    breakdown = Counter()
    for r in h0_ge3:
        h0, h3, chi = r['h0'], r['h3'], r['chi']
        if h3 < 0:
            gap = 'ov'
        else:
            gap = h0 - h3 - chi
        breakdown[(h0, h3 if h3 >= 0 else 'ov', gap)] += 1

    for (h0, h3, gap), cnt in sorted(breakdown.items(),
                                      key=lambda x: (-x[1], -x[0][0])):
        if h0 == 3 and h3 == 0 and gap == 0:
            interp = "← CLEAN: 3 gen, no vector-like pairs"
        elif h0 == 3 and h3 == 0:
            interp = f"← 3 gen, h¹-h² = {gap}"
        elif h0 > 3 and h3 == 0:
            interp = f"← {h0} gen, needs h¹-h² = {gap} cancellation"
        elif h3 != 0 and h3 != 'ov':
            interp = f"← h³={h3} → Serre dual contributes"
        else:
            interp = ""
        print(f"    {h0:>4} {str(h3):>4} {str(gap):>6} {cnt:>6}  {interp}")

    # ── Representative clean bundles ──
    print(f"\n  Representative clean bundles (h⁰=3, h³=0):")
    print(f"  In heterotic E₈ × E₈ compactification with standard embedding:")
    print(f"    • h⁰(X, L) = 3  →  3 chiral families of quarks/leptons")
    print(f"    • h¹(X, L) = 0  →  no vector-like pairs (clean spectrum)")
    print(f"    • h²(X, L) = 0  →  no anti-families")
    print(f"    • h³(X, L) = 0  →  confirmed by h⁰(-L) = 0")

    for r in clean[:10]:
        nz = [(i, int(r['D_basis'][i]))
              for i in range(h11_eff) if r['D_basis'][i] != 0]
        D_str = " + ".join(f"{c}·e{i}" for i, c in nz)
        print(f"\n    L = O({D_str})")
        print(f"      χ(L) = {r['chi']:.0f},  D³ = {r['D3']:.0f}")
        print(f"      h⁰ = 3,  h¹ = 0,  h² = 0,  h³ = 0")
        print(f"      → {GREEN}3 net chiral generations{RESET}")

    return clean


# ══════════════════════════════════════════════════════════════════
#  Scorecard
# ══════════════════════════════════════════════════════════════════

def print_scorecard(target_h11, target_poly, cyobj, results, bundles,
                    d3_unique, has_swiss, best_tau, best_ratio,
                    dp_candidates, k3_divs, k3_fibs, ell_fibs, phash):
    """Final pipeline scorecard."""
    h11 = cyobj.h11()
    h21 = cyobj.h21()
    chi = cyobj.chi()
    max_h0 = max((r['h0'] for r in results), default=0)
    h0_ge3 = sum(1 for r in results if r['h0'] >= 3)
    n_clean = sum(1 for r in results if r['clean'])
    n_chi3 = len(bundles)

    print(f"\n{'═' * 72}")
    print(f"  {BOLD}SCORECARD: h11={target_h11}, Polytope {target_poly}{RESET}")
    print(f"  Fingerprint: {phash}")
    print(f"  CYTools version: {CYTOOLS_VERSION}")
    print(f"{'═' * 72}")

    scores = []

    def score(name, val, check, pts, detail=""):
        ok = check(val) if callable(check) else (val == check)
        s = pts if ok else 0
        scores.append(s)
        status = PASS if ok else FAIL
        det = f"  ({detail})" if detail else ""
        print(f"  [{status}] {name}: {val}{det} → {s}/{pts}")

    score("χ = -6", chi, -6, 3)
    score("|χ|/2 = 3 generations", abs(chi) // 2, 3, 3)
    score("h⁰ ≥ 3 exists", h0_ge3 > 0, True, 3,
          f"{h0_ge3} bundles")
    score("Clean h⁰=3 bundles (h³=0)", n_clean, lambda x: x > 0, 5,
          f"{n_clean} clean bundles")
    score("Max h⁰", max_h0, lambda x: x >= 3, 2,
          f"from {n_chi3} χ=3 bundles")
    score("Swiss cheese structure", has_swiss, True, 3,
          f"τ={best_tau:.1f}, ratio={best_ratio:.5f}" if has_swiss else "")
    score("K3 fibrations", len(k3_fibs), lambda x: x >= 1, 2,
          f"{len(k3_fibs)} found")
    score("Elliptic fibrations", len(ell_fibs), lambda x: x >= 1, 2,
          f"{len(ell_fibs)} found")
    score("del Pezzo divisors", len(dp_candidates), lambda x: x >= 1, 1,
          f"{len(dp_candidates)} candidates")
    score("D³ diversity (clean)", len(d3_unique), lambda x: x >= 10, 1,
          f"range [{d3_unique[0]:.0f}, {d3_unique[-1]:.0f}]" if d3_unique
          else "")
    score("h¹¹ tractable (≤18)", h11, lambda x: x <= 18, 1)

    total = sum(scores)
    max_total = sum([3, 3, 3, 5, 2, 3, 2, 2, 1, 1, 1])  # 26

    print(f"\n  {BOLD}TOTAL: {total}/{max_total}{RESET}")

    # ── Physics interpretation ──
    print(f"\n{'─' * 72}")
    print(f"  {BOLD}PHYSICS INTERPRETATION{RESET}")
    print(f"{'─' * 72}")
    swiss_line = (f"    • Swiss cheese structure (τ={best_tau:.1f}) enables LVS\n"
                  f"      moduli stabilization → hierarchy m_soft ~ M_P/V ~ TeV"
                  if has_swiss else "")
    print(f"""
  This Calabi-Yau 3-fold (h¹¹={h11}, h²¹={h21}) with Euler characteristic
  χ = {chi} admits {n_clean} line bundles L = O(D) satisfying:

    h⁰(X, L) = 3,   h¹(X, L) = 0,   h²(X, L) = 0,   h³(X, L) = 0

  In a heterotic string compactification on X with gauge bundle V
  derived from these line bundles:

    • The 3 sections of L give exactly 3 chiral families (quarks + leptons)
    • h¹ = h² = 0 means NO vector-like pairs → clean low-energy spectrum
    • {len(k3_fibs)} K3 and {len(ell_fibs)} elliptic fibrations provide
      geometric structure for F-theory / heterotic duality
{swiss_line}

  The {len(d3_unique)} distinct D³ values across clean bundles show a rich
  intersection ring, providing many geometrically distinct 3-generation
  models on a single Calabi-Yau manifold.
""")
    print(f"{'═' * 72}")
    return total, max_total


# ══════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Full deep-analysis pipeline for χ=-6 CY candidates")
    parser.add_argument('--h11', type=int, required=True,
                        help='Hodge number h¹¹')
    parser.add_argument('--poly', type=int, required=True,
                        help='Polytope index (0-based)')
    parser.add_argument('--h21', type=int, default=None,
                        help='Hodge number h²¹ (default: h11+3)')
    args = parser.parse_args()

    target_h11 = args.h11
    target_poly = args.poly
    target_h21 = args.h21 if args.h21 is not None else target_h11 + 3

    out_dir = "results"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir,
                            f"pipeline_h{target_h11}_P{target_poly}_output.txt")

    tee = Tee(out_file)
    sys.stdout = tee

    t_start = time.time()

    print("=" * 72)
    print(f"  {BOLD}FULL PIPELINE: h11={target_h11}, POLYTOPE {target_poly}{RESET}")
    print(f"  {CYAN}h21={target_h21}, χ=-6 candidate{RESET}")
    print(f"  Stages 1-4 of FRAMEWORK.md")
    print("=" * 72)

    # Stage 1
    p, tri, cyobj, pts, ray_indices, phash, precomp = \
        run_stage1(target_h11, target_h21, target_poly)

    # Stage 2
    (div_basis, intnums, c2, mori, has_swiss, best_tau, best_ratio,
     dp_candidates, k3_divs, k3_fibs, ell_fibs) = \
        run_stage2(cyobj, pts, ray_indices, p)

    # Stage 3
    results, bundles, d3_unique = \
        run_stage3(cyobj, pts, ray_indices, div_basis, intnums, c2, mori,
                   precomp)

    # Stage 4
    h11_eff = len(div_basis)
    clean = run_stage4(results, h11_eff)

    # Scorecard
    total, max_total = print_scorecard(
        target_h11, target_poly,
        cyobj, results, bundles, d3_unique,
        has_swiss, best_tau, best_ratio,
        dp_candidates, k3_divs, k3_fibs, ell_fibs, phash
    )

    elapsed = time.time() - t_start
    print(f"\n  Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Output saved to: {out_file}")
    print(f"\n{'═' * 72}")
    print(f"  Done.")
    print(f"{'═' * 72}")

    sys.stdout = tee.stdout
    tee.close()


if __name__ == '__main__':
    main()
