#!/usr/bin/env python3
"""
tangency_scan.py v3 — Tiered complexity scan of chi=-6 CY3s for chi(L)=3 tangency.

Three tiers of analysis, each adding depth:

  TIER 1 — CORE BASELINE
    Triangulate, Kähler cone, chi at t=1 on all rays, t* along best ray,
    integer search near best ray only.  O(n_rays) chi evals + 1 root-find.

  TIER 2 — BOUNDARY ANALYSIS
    + For each Mori wall: identify face rays, find t* on best face ray,
    edge search on promising faces.  Adds O(n_mori × few) root-finds.

  TIER 3 — EXHAUSTIVE INTEGER SEARCH
    + Integer search near ALL rays at multiple scales with perturbations.
    Adds O(n_rays × n_scales × 2*h11) chi evals.

Usage:
    python tangency_scan.py --tier 1 --limit 10       # fast profiling
    python tangency_scan.py --tier 2 --limit 10       # boundary analysis
    python tangency_scan.py --tier 3 --limit 1000     # full scan
"""

import argparse
import csv
import gc
import sys
import time
from itertools import combinations

import numpy as np

try:
    from cytools import fetch_polytopes
    from cytools.config import enable_experimental_features
    enable_experimental_features()
except ImportError:
    print("ERROR: CYTools not installed. See https://cy.tools for setup.")
    sys.exit(1)

try:
    from scipy.optimize import brentq
except ImportError:
    print("ERROR: scipy not installed. Run: pip install scipy")
    sys.exit(1)


# ============================================================================
# HRR INDEX COMPUTATION
# ============================================================================

def chi_line_bundle(n_vec, intnums, c2_vals, n_toric):
    """Compute chi(X, O(D)) via HRR index theorem on CY3.

    chi(X, L) = (1/6) kappa_{abc} n^a n^b n^c + (1/12) c2_a n^a
    """
    n = np.array(n_vec, dtype=float)
    if len(n) < n_toric:
        n = np.pad(n, (0, n_toric - len(n)))
    elif len(n) > n_toric:
        n = n[:n_toric]

    cubic = 0.0
    for (a, b, c), kval in intnums.items():
        if max(a, b, c) >= n_toric:
            continue
        if a == b == c:
            cubic += kval * n[a] ** 3
        elif a == b:
            cubic += 3 * kval * n[a] ** 2 * n[c]
        elif b == c:
            cubic += 3 * kval * n[a] * n[b] ** 2
        elif a == c:
            cubic += 3 * kval * n[a] ** 2 * n[b]
        else:
            cubic += 6 * kval * n[a] * n[b] * n[c]
    cubic /= 6.0

    c2 = np.array(c2_vals, dtype=float)
    if len(c2) < n_toric:
        c2 = np.pad(c2, (0, n_toric - len(c2)))
    linear = np.dot(c2[:n_toric], n[:n_toric]) / 12.0

    return cubic + linear


def basis_to_toric(basis_vec, div_basis, n_toric):
    """Convert basis-coordinate vector to toric-coordinate vector.

    Handles both forms of div_basis:
      - 1D index array: div_basis[a] = toric index for basis element a
      - 2D matrix: div_basis[a] = toric coefficients for basis element a
    """
    basis_vec = np.asarray(basis_vec, dtype=float)
    db = np.asarray(div_basis)
    if db.ndim == 2:
        return basis_vec @ db.astype(float)
    else:
        toric_vec = np.zeros(n_toric)
        for a, val in enumerate(basis_vec):
            idx = int(db[a])
            if 0 <= idx < n_toric:
                toric_vec[idx] = val
        return toric_vec


def find_t_star(ray_toric, intnums, c2_vals, n_toric, target=3.0):
    """Find t > 0 where chi(t * ray) = target. Returns t or None."""
    def f(t):
        return chi_line_bundle(t * ray_toric, intnums, c2_vals, n_toric) - target

    test_ts = np.concatenate([
        np.linspace(0.01, 1.0, 50),
        np.linspace(1.0, 5.0, 20),
        np.linspace(5.0, 20.0, 10),
    ])
    try:
        vals = [f(t) for t in test_ts]
        for j in range(len(vals) - 1):
            if vals[j] * vals[j + 1] < 0:
                return brentq(f, test_ts[j], test_ts[j + 1],
                              xtol=1e-12, maxiter=200)
    except Exception:
        pass
    return None


def find_edge_chi3(ra_toric, rb_toric, intnums, c2_vals, n_toric, target=3.0):
    """Find s in (0,1) where chi(s*ra + (1-s)*rb) = target."""
    def f(s):
        D = s * ra_toric + (1.0 - s) * rb_toric
        return chi_line_bundle(D, intnums, c2_vals, n_toric) - target

    test_ss = np.linspace(0.0, 1.0, 15)
    try:
        vals = [f(s) for s in test_ss]
        for j in range(len(vals) - 1):
            if vals[j] * vals[j + 1] < 0:
                return brentq(f, test_ss[j], test_ss[j + 1],
                              xtol=1e-12, maxiter=200)
    except Exception:
        pass
    return None


# ============================================================================
# INTEGER POINT CLASSIFIER
# ============================================================================

def classify_integer_point(D_basis, mori_gens):
    """Classify an integer divisor by its Mori pairing.
    Returns (min_mori, category) where category is 'ample'/'nef'/'near_miss'/'outside'.
    """
    pairings = mori_gens @ D_basis
    min_mori = int(round(np.min(pairings)))
    if min_mori > 0:
        return min_mori, "ample"
    elif min_mori == 0:
        return min_mori, "nef"
    elif min_mori >= -1:
        return min_mori, "near_miss"
    else:
        return min_mori, "outside"


# ============================================================================
# TIERED ANALYSIS
# ============================================================================

def analyze_polytope(p, poly_idx, tier=3):
    """Analyze one polytope for chi=3 tangency with Kähler cone.

    tier=1: Core baseline — chi on rays + t* on best ray + integer search near best
    tier=2: + Mori wall boundary analysis + face edge search
    tier=3: + Exhaustive integer search near ALL rays

    Returns dict with results and per-tier timing.
    """
    row = {
        "poly_idx": poly_idx,
        "h11": None, "h21": None,
        "n_vertices": len(p.vertices()),
        "gl_order": None,
        "n_rays": None,
        "n_mori": None,
        "classification": None,
        "n_ample_chi3": 0,
        "n_nef_chi3": 0,
        "n_nearmiss_chi3": 0,
        "best_min_mori": None,
        "t_star_best": None,
        "min_chi_on_rays": None,
        "best_ray_idx": None,
        # Tier 2 fields
        "n_face_tangent_rays": 0,
        "n_face_tangent_edges": 0,
        "t_star_face": None,
        "saturated_faces": 0,
        # Timing
        "t_setup": None,
        "t_tier1": None,
        "t_tier2": None,
        "t_tier3": None,
        "error": None,
    }

    # ==========================================================
    # SETUP: Triangulate, CY3, geometric data
    # ==========================================================
    t0_setup = time.time()

    try:
        t_obj = p.triangulate()
    except Exception as e:
        row["error"] = f"triangulation: {str(e)[:100]}"
        return row

    try:
        cy = t_obj.get_cy()
    except Exception as e:
        err = str(e).lower()
        if "non-favorable" in err or "experimental" in err:
            row["error"] = "non-favorable"
        else:
            row["error"] = f"get_cy: {str(e)[:100]}"
        return row

    h11 = cy.h11()
    h21 = cy.h21()
    row["h11"] = h11
    row["h21"] = h21

    try:
        row["gl_order"] = len(p.automorphisms())
    except Exception:
        pass

    try:
        div_basis = cy.divisor_basis()
        intnums = cy.intersection_numbers()
        c2_vals = np.array(cy.second_chern_class(), dtype=float)
    except Exception as e:
        row["error"] = f"geometry: {str(e)[:100]}"
        return row

    db = np.asarray(div_basis)
    if db.ndim == 2:
        n_toric = db.shape[1]
    else:
        n_toric = max(int(db.max()) + 1, len(c2_vals))
    if len(c2_vals) < n_toric:
        c2_vals = np.pad(c2_vals, (0, n_toric - len(c2_vals)))

    def to_toric(bv):
        return basis_to_toric(bv, div_basis, n_toric)

    try:
        kc = cy.toric_kahler_cone()
        kc_rays = np.array(kc.rays(), dtype=float)
        mori_gens = np.array(kc.hyperplanes(), dtype=float)
    except Exception as e:
        row["error"] = f"kahler_cone: {str(e)[:100]}"
        return row

    n_rays = len(kc_rays)
    n_mori = len(mori_gens)
    row["n_rays"] = n_rays
    row["n_mori"] = n_mori
    if n_rays == 0:
        row["error"] = "no_kahler_rays"
        return row

    row["t_setup"] = round(time.time() - t0_setup, 4)

    # ==========================================================
    # TIER 1: Core — chi on all rays, t* on best, integer search near best
    # ==========================================================
    t0_t1 = time.time()

    # Compute chi(ray) at t=1 for every ray — cheap, one eval each
    ray_chis = np.zeros(n_rays)
    for i, ray_basis in enumerate(kc_rays):
        ray_toric = to_toric(ray_basis)
        ray_chis[i] = chi_line_bundle(ray_toric, intnums, c2_vals, n_toric)

    row["min_chi_on_rays"] = round(float(np.min(ray_chis)), 6)

    # Best ray = closest chi to 3 at t=1
    best_idx = int(np.argmin(np.abs(ray_chis - 3.0)))
    row["best_ray_idx"] = best_idx

    # Find t* along the best ray only
    best_ray_toric = to_toric(kc_rays[best_idx])
    t_star = find_t_star(best_ray_toric, intnums, c2_vals, n_toric, target=3.0)
    if t_star is not None:
        row["t_star_best"] = round(t_star, 8)

    # Integer search near the best ray
    ample_pts = []
    nef_pts = []
    nearmiss_pts = []
    best_min_mori = None
    seen = set()

    scales_t1 = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
    best_ray_basis = kc_rays[best_idx]

    for s in scales_t1:
        base = tuple(np.round(s * best_ray_basis).astype(int))
        candidates = [base]
        for d in range(h11):
            p1 = list(base); p1[d] += 1; candidates.append(tuple(p1))
            m1 = list(base); m1[d] -= 1; candidates.append(tuple(m1))

        for D_tuple in candidates:
            if D_tuple in seen:
                continue
            seen.add(D_tuple)
            D_basis = np.array(D_tuple, dtype=float)
            D_toric = to_toric(D_basis)
            chi_val = chi_line_bundle(D_toric, intnums, c2_vals, n_toric)
            if abs(chi_val - 3.0) > 1e-6:
                continue
            mm, cat = classify_integer_point(D_basis, mori_gens)
            if best_min_mori is None or mm > best_min_mori:
                best_min_mori = mm
            if cat == "ample":
                ample_pts.append(D_tuple)
            elif cat == "nef":
                nef_pts.append(D_tuple)
            elif cat == "near_miss":
                nearmiss_pts.append(D_tuple)

    row["n_ample_chi3"] = len(ample_pts)
    row["n_nef_chi3"] = len(nef_pts)
    row["n_nearmiss_chi3"] = len(nearmiss_pts)
    row["best_min_mori"] = best_min_mori
    row["t_tier1"] = round(time.time() - t0_t1, 4)

    if tier < 2:
        # Tier 1 classification
        if ample_pts:
            row["classification"] = "AMPLE"
        elif nef_pts:
            row["classification"] = "NEF"
        elif nearmiss_pts:
            row["classification"] = "NEAR_MISS"
        elif t_star is not None:
            row["classification"] = "CONTINUOUS_TANGENT"
        else:
            row["classification"] = "DISTANT" if ray_chis.min() > 10 else "NEAR"
        return row

    # ==========================================================
    # TIER 2: Boundary — Mori wall analysis + face edge search
    # ==========================================================
    t0_t2 = time.time()

    # For each Mori wall, find the face rays and check for chi=3
    ray_pairings = kc_rays @ mori_gens.T  # (n_rays, n_mori)
    tangent_face_set = set()
    face_tangent_count = 0
    best_t_face = None

    for wall_j in range(n_mori):
        # Rays on this face: D · C_j ≈ 0
        face_ray_idxs = [i for i in range(n_rays)
                         if abs(ray_pairings[i, wall_j]) < 1e-10]
        if not face_ray_idxs:
            continue

        # Pick the face ray whose chi is closest to 3
        best_face_ray = min(face_ray_idxs, key=lambda i: abs(ray_chis[i] - 3.0))
        best_face_chi = ray_chis[best_face_ray]

        # Only root-find if chi is in a reasonable range
        if best_face_chi < 50:
            r_toric = to_toric(kc_rays[best_face_ray])
            t = find_t_star(r_toric, intnums, c2_vals, n_toric, target=3.0)
            if t is not None:
                face_tangent_count += 1
                tangent_face_set.add(wall_j)
                if best_t_face is None or t < best_t_face:
                    best_t_face = t

    # Edge search on promising faces
    n_edge_tangent = 0
    for wall_j in range(n_mori):
        face_ray_idxs = [i for i in range(n_rays)
                         if abs(ray_pairings[i, wall_j]) < 1e-10]
        if len(face_ray_idxs) < 2:
            continue
        # Skip faces where all rays have chi far from 3
        face_chis = [ray_chis[i] for i in face_ray_idxs]
        if min(face_chis) > 15:
            continue
        # Rank by chi proximity to 3; top 5 rays → max 10 pairs
        ranked = sorted(face_ray_idxs, key=lambda i: abs(ray_chis[i] - 3.0))
        for a_idx, b_idx in list(combinations(ranked[:5], 2)):
            ra_t = to_toric(kc_rays[a_idx])
            rb_t = to_toric(kc_rays[b_idx])
            s = find_edge_chi3(ra_t, rb_t, intnums, c2_vals, n_toric)
            if s is not None and 0.01 < s < 0.99:
                n_edge_tangent += 1
                tangent_face_set.add(wall_j)

    row["n_face_tangent_rays"] = face_tangent_count
    row["n_face_tangent_edges"] = n_edge_tangent
    row["t_star_face"] = round(best_t_face, 8) if best_t_face is not None else None
    row["saturated_faces"] = len(tangent_face_set)
    row["t_tier2"] = round(time.time() - t0_t2, 4)

    if tier < 3:
        # Tier 2 classification
        if ample_pts:
            row["classification"] = "AMPLE"
        elif nef_pts:
            row["classification"] = "NEF"
        elif face_tangent_count > 0 or n_edge_tangent > 0:
            row["classification"] = "BOUNDARY_TANGENT"
        elif nearmiss_pts:
            row["classification"] = "NEAR_MISS"
        elif t_star is not None:
            row["classification"] = "INTERIOR_ONLY"
        else:
            row["classification"] = "DISTANT" if ray_chis.min() > 10 else "NEAR"
        return row

    # ==========================================================
    # TIER 3: Exhaustive integer search near ALL rays
    # ==========================================================
    t0_t3 = time.time()

    scales_t3 = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]

    for ray_idx, ray_basis in enumerate(kc_rays):
        if ray_idx == best_idx:
            continue  # already searched in tier 1
        for s in scales_t3:
            base = tuple(np.round(s * ray_basis).astype(int))
            candidates = [base]
            for d in range(h11):
                p1 = list(base); p1[d] += 1; candidates.append(tuple(p1))
                m1 = list(base); m1[d] -= 1; candidates.append(tuple(m1))

            for D_tuple in candidates:
                if D_tuple in seen:
                    continue
                seen.add(D_tuple)
                D_basis = np.array(D_tuple, dtype=float)
                D_toric = to_toric(D_basis)
                chi_val = chi_line_bundle(D_toric, intnums, c2_vals, n_toric)
                if abs(chi_val - 3.0) > 1e-6:
                    continue
                mm, cat = classify_integer_point(D_basis, mori_gens)
                if best_min_mori is None or mm > best_min_mori:
                    best_min_mori = mm
                if cat == "ample":
                    ample_pts.append(D_tuple)
                elif cat == "nef":
                    nef_pts.append(D_tuple)
                elif cat == "near_miss":
                    nearmiss_pts.append(D_tuple)

    # Update counts after exhaustive search
    row["n_ample_chi3"] = len(ample_pts)
    row["n_nef_chi3"] = len(nef_pts)
    row["n_nearmiss_chi3"] = len(nearmiss_pts)
    row["best_min_mori"] = best_min_mori
    row["t_tier3"] = round(time.time() - t0_t3, 4)

    # Tier 3 classification
    if ample_pts:
        row["classification"] = "AMPLE"
    elif nef_pts:
        row["classification"] = "NEF"
    elif face_tangent_count > 0 or n_edge_tangent > 0:
        row["classification"] = "BOUNDARY_TANGENT"
    elif nearmiss_pts:
        row["classification"] = "NEAR_MISS"
    elif t_star is not None:
        row["classification"] = "INTERIOR_ONLY"
    else:
        row["classification"] = "DISTANT" if ray_chis.min() > 10 else "NEAR"

    return row


# ============================================================================
# MAIN SCAN
# ============================================================================

FIELDNAMES = [
    "poly_idx", "h11", "h21", "n_vertices", "gl_order",
    "n_rays", "n_mori",
    "classification", "n_ample_chi3", "n_nef_chi3", "n_nearmiss_chi3",
    "best_min_mori", "t_star_best", "min_chi_on_rays", "best_ray_idx",
    "n_face_tangent_rays", "n_face_tangent_edges",
    "t_star_face", "saturated_faces",
    "t_setup", "t_tier1", "t_tier2", "t_tier3",
    "error",
]


def run_tangency_scan(chi_val=-6, limit=1000, tier=3,
                      output_path=None, verbose=True):
    """Scan chi=-6 polytopes with specified analysis tier."""
    if output_path is None:
        output_path = f"tangency_scan_t{tier}.csv"

    if verbose:
        print(f"{'=' * 72}")
        print(f"  TANGENCY SCAN v3  |  TIER {tier}  |  chi={chi_val}")
        print(f"{'=' * 72}")
        tier_desc = {
            1: "Core: chi on rays + t* best ray + integer near best",
            2: "Core + Mori wall boundary search + face edge search",
            3: "Core + Boundary + exhaustive integer search (all rays)",
        }
        print(f"  {tier_desc.get(tier, '?')}")
        print(f"\n  Fetching up to {limit} polytopes...")

    t_fetch_start = time.time()
    try:
        polytopes = fetch_polytopes(chi=chi_val, lattice="N", limit=limit)
        if not isinstance(polytopes, list):
            polytopes = list(polytopes)
    except Exception as e:
        print(f"  ERROR fetching polytopes: {e}")
        return []

    t_fetch = time.time() - t_fetch_start
    n_total = len(polytopes)
    if verbose:
        print(f"  Fetched {n_total} polytopes in {t_fetch:.1f}s")
        print(f"  {'─' * 68}")

    all_results = []
    class_counts = {}
    n_success = 0
    n_skip = 0
    t_start = time.time()
    timing_sums = {"setup": 0, "t1": 0, "t2": 0, "t3": 0}

    for poly_idx, p_obj in enumerate(polytopes):
        t0 = time.time()

        try:
            row = analyze_polytope(p_obj, poly_idx, tier=tier)
        except Exception as e:
            row = {k: None for k in FIELDNAMES}
            row["poly_idx"] = poly_idx
            row["n_vertices"] = len(p_obj.vertices())
            row["error"] = f"unhandled: {str(e)[:100]}"

        all_results.append(row)
        dt = time.time() - t0

        # Accumulate tier timings
        if row.get("t_setup") is not None:
            timing_sums["setup"] += row["t_setup"]
        if row.get("t_tier1") is not None:
            timing_sums["t1"] += row["t_tier1"]
        if row.get("t_tier2") is not None:
            timing_sums["t2"] += row["t_tier2"]
        if row.get("t_tier3") is not None:
            timing_sums["t3"] += row["t_tier3"]

        if row.get("error"):
            n_skip += 1
            if verbose:
                print(f"  [{poly_idx+1:4d}/{n_total}] SKIP  {row['error'][:60]}  ({dt:.1f}s)")
        else:
            n_success += 1
            cls = row["classification"]
            class_counts[cls] = class_counts.get(cls, 0) + 1
            if verbose:
                timing = ""
                if row.get("t_setup") is not None:
                    timing += f"S={row['t_setup']:.2f}"
                if row.get("t_tier1") is not None:
                    timing += f" T1={row['t_tier1']:.2f}"
                if row.get("t_tier2") is not None:
                    timing += f" T2={row['t_tier2']:.2f}"
                if row.get("t_tier3") is not None:
                    timing += f" T3={row['t_tier3']:.2f}"
                flags = []
                if row["n_ample_chi3"]:
                    flags.append(f"amp={row['n_ample_chi3']}")
                if row["n_nef_chi3"]:
                    flags.append(f"nef={row['n_nef_chi3']}")
                if row["n_nearmiss_chi3"]:
                    flags.append(f"miss={row['n_nearmiss_chi3']}")
                detail = f"  [{', '.join(flags)}]" if flags else ""
                print(f"  [{poly_idx+1:4d}/{n_total}] {cls:<18s} "
                      f"h11={row['h11']:>2} r={row['n_rays']:>4} "
                      f"min_χ={row['min_chi_on_rays']:>6.1f} "
                      f"{timing}{detail}  ({dt:.1f}s)")

        if (poly_idx + 1) % 10 == 0:
            gc.collect()

    elapsed = time.time() - t_start

    # --- Write CSV ---
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_results)

    # --- Summary ---
    if verbose:
        print(f"\n  {'=' * 68}")
        print(f"  TANGENCY SCAN v3 TIER {tier} — SUMMARY")
        print(f"  {'=' * 68}")
        print(f"  Total polytopes:       {n_total}")
        print(f"  Analyzed:              {n_success}")
        print(f"  Skipped:               {n_skip}")
        print(f"  Elapsed:               {elapsed:.1f}s "
              f"({elapsed/max(n_total,1):.2f}s/polytope)")

        # Tier timing breakdown
        print(f"\n  TIMING BREAKDOWN (sum across {n_success} polytopes):")
        print(f"  {'─'*48}")
        total_timed = sum(timing_sums.values())
        for label, key in [("Setup (triangulate+CY3+cone)", "setup"),
                           ("Tier 1 (chi rays + best t*)", "t1"),
                           ("Tier 2 (Mori walls + edges)", "t2"),
                           ("Tier 3 (exhaustive integer)", "t3")]:
            val = timing_sums[key]
            if val > 0:
                pct = 100.0 * val / max(total_timed, 1e-9)
                bar = '#' * int(pct / 2)
                print(f"    {label:<35s} {val:6.1f}s  ({pct:5.1f}%)  {bar}")
        if n_success > 0:
            print(f"    {'Avg per polytope':<35s} "
                  f"{total_timed/n_success:.3f}s")

        # Classification breakdown
        print(f"\n  CLASSIFICATION BREAKDOWN:")
        print(f"  {'─'*48}")
        for cls in ["AMPLE", "NEF", "BOUNDARY_TANGENT", "NEAR_MISS",
                     "INTERIOR_ONLY", "CONTINUOUS_TANGENT", "NEAR", "DISTANT"]:
            cnt = class_counts.get(cls, 0)
            if cnt:
                pct = 100.0 * cnt / max(n_success, 1)
                bar = '#' * int(pct / 2)
                print(f"    {cls:<20s} {cnt:>5}  ({pct:5.1f}%)  {bar}")

        # Error breakdown
        error_rows = [r for r in all_results if r.get("error")]
        if error_rows:
            from collections import Counter
            err_counts = Counter(r["error"][:60] for r in error_rows)
            print(f"\n  ERRORS ({len(error_rows)} total):")
            for err, cnt in err_counts.most_common(5):
                print(f"    {cnt:>4}x  {err}")

        # h11 distribution
        h11_dist = {}
        for r in all_results:
            if r.get("h11") and not r.get("error"):
                h11_dist[r["h11"]] = h11_dist.get(r["h11"], 0) + 1
        if h11_dist:
            print(f"\n  h11 distribution:")
            for h, c in sorted(h11_dist.items()):
                print(f"    h11={h:>3}: {c}")

        print(f"\n  Results saved to: {output_path}")

    return all_results


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Scan chi=-6 CY3s for chi=3 tangency (v3, tiered)",
    )
    parser.add_argument("--chi", type=int, default=-6,
                        help="Euler characteristic (default: -6)")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Max polytopes to fetch (default: 1000)")
    parser.add_argument("--tier", type=int, default=3, choices=[1, 2, 3],
                        help="Analysis tier: 1=core, 2=+boundary, 3=+exhaustive")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output CSV path (default: tangency_scan_t{tier}.csv)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress verbose output")
    args = parser.parse_args()

    run_tangency_scan(
        chi_val=args.chi,
        limit=args.limit,
        tier=args.tier,
        output_path=args.output or f"tangency_scan_t{args.tier}.csv",
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
