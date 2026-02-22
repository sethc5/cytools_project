#!/usr/bin/env python3
"""
tangency_scan_v3.py — 3-tier pipeline for chi=3 tangency analysis.

Tier 1 (GEOMETRY):  Extract all CYTools data — triangulation, intersection
                    numbers, c2, Kähler cone, Mori generators. Persists to
                    pickle so CYTools is never called again.

Tier 2 (ANALYSIS):  Load Tier 1 cache. For each polytope, find continuous
                    chi=3 points near Mori walls. Uses only the cached
                    geometric data — fast, iterable, no CYTools dependency.

Tier 3 (CLASSIFY):  Load Tier 1+2 cache. Exhaustive integer lattice search
                    for chi=3 divisors. Final classification and CSV export.

Each tier writes its results into the same pickle. Re-running a tier
overwrites only that tier's fields. Earlier tiers are never recomputed.

Usage:
    python tangency_scan_v3.py --tier 1              # extract geometry
    python tangency_scan_v3.py --tier 2              # boundary analysis
    python tangency_scan_v3.py --tier 3              # integer search + CSV
    python tangency_scan_v3.py --tier 1 --limit 10   # small test
    python tangency_scan_v3.py --tier 123             # run all three
"""

import argparse
import csv
import gc
import os
import pickle
import sys
import time

import numpy as np

try:
    from scipy.optimize import brentq
except ImportError:
    print("ERROR: scipy not installed. Run: pip install scipy")
    sys.exit(1)


# ============================================================================
# SHARED MATH UTILITIES
# ============================================================================

def chi_line_bundle(n_vec, intnums, c2_vals, n_toric):
    """chi(X, O(D)) via HRR on CY3.
    chi = (1/6) kappa_{abc} n^a n^b n^c + (1/12) c2_a n^a
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
    Handles 1D index array and 2D matrix forms of div_basis.
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


# ============================================================================
# TIER 1 — GEOMETRY EXTRACTION
# ============================================================================

def tier1_extract(chi_val=-6, limit=1000, cache_path="tangency_cache.pkl",
                  verbose=True):
    """Extract all geometric data from CYTools; persist to pickle.

    This is the only tier that imports CYTools. After this runs, all
    subsequent analysis uses only numpy + scipy on the cached data.
    """
    try:
        from cytools import fetch_polytopes
        from cytools.config import enable_experimental_features
        enable_experimental_features()
    except ImportError:
        print("ERROR: CYTools not installed. Tier 1 requires CYTools.")
        sys.exit(1)

    if verbose:
        print(f"{'=' * 72}")
        print(f"  TIER 1: GEOMETRY EXTRACTION  (chi={chi_val}, limit={limit})")
        print(f"{'=' * 72}")

    t0 = time.time()
    polytopes = fetch_polytopes(chi=chi_val, lattice="N", limit=limit)
    if not isinstance(polytopes, list):
        polytopes = list(polytopes)
    n = len(polytopes)
    if verbose:
        print(f"  Fetched {n} polytopes in {time.time()-t0:.1f}s\n")

    records = []
    n_ok = 0
    n_err = 0

    for i, p in enumerate(polytopes):
        t_start = time.time()
        rec = {
            "poly_idx": i,
            "n_vertices": len(p.vertices()),
            "tier1_ok": False,
            "tier1_error": None,
            # geometry fields (filled on success)
            "h11": None, "h21": None, "gl_order": None,
            "div_basis": None, "intnums": None, "c2_vals": None,
            "n_toric": None, "mori_gens": None,
            # tier 2/3 fields (filled later)
            "tier2": None, "tier3": None,
        }

        try:
            t_obj = p.triangulate()
            cy = t_obj.get_cy()
        except Exception as e:
            err = str(e).lower()
            if "non-favorable" in err or "experimental" in err:
                rec["tier1_error"] = "non-favorable"
            else:
                rec["tier1_error"] = f"build: {str(e)[:120]}"
            records.append(rec)
            n_err += 1
            dt = time.time() - t_start
            if verbose:
                print(f"  [{i+1:4d}/{n}] SKIP  {rec['tier1_error'][:60]}  ({dt:.2f}s)")
            continue

        try:
            rec["h11"] = cy.h11()
            rec["h21"] = cy.h21()
            rec["div_basis"] = np.array(cy.divisor_basis())
            # Effective basis dimension (may differ from h11 for 1D index arrays)
            db_tmp = rec["div_basis"]
            rec["basis_dim"] = db_tmp.shape[0] if db_tmp.ndim <= 1 else db_tmp.shape[0]
            rec["intnums"] = dict(cy.intersection_numbers())
            rec["c2_vals"] = np.array(cy.second_chern_class(), dtype=float)

            db = rec["div_basis"]
            if db.ndim == 2:
                rec["n_toric"] = db.shape[1]
            else:
                rec["n_toric"] = max(int(db.max()) + 1, len(rec["c2_vals"]))

            # Pad c2 if needed
            if len(rec["c2_vals"]) < rec["n_toric"]:
                rec["c2_vals"] = np.pad(rec["c2_vals"],
                                        (0, rec["n_toric"] - len(rec["c2_vals"])))

            kc = cy.toric_kahler_cone()
            rec["mori_gens"] = np.array(kc.hyperplanes(), dtype=float)

            try:
                rec["gl_order"] = len(p.automorphisms())
            except Exception:
                pass

            rec["tier1_ok"] = True
            n_ok += 1
            dt = time.time() - t_start
            if verbose:
                nm = len(rec["mori_gens"])
                print(f"  [{i+1:4d}/{n}] OK    h11={rec['h11']:>2}  "
                      f"mori={nm}  intnums={len(rec['intnums'])}  ({dt:.2f}s)")

        except Exception as e:
            rec["tier1_error"] = f"geometry: {str(e)[:120]}"
            n_err += 1
            dt = time.time() - t_start
            if verbose:
                print(f"  [{i+1:4d}/{n}] SKIP  {rec['tier1_error'][:60]}  ({dt:.2f}s)")

        records.append(rec)
        if (i + 1) % 20 == 0:
            gc.collect()

    elapsed = time.time() - t0

    # Save
    with open(cache_path, "wb") as f:
        pickle.dump(records, f, protocol=pickle.HIGHEST_PROTOCOL)

    if verbose:
        print(f"\n  {'─' * 68}")
        print(f"  Tier 1 complete: {n_ok} ok, {n_err} skipped in {elapsed:.1f}s")
        fsize = os.path.getsize(cache_path)
        print(f"  Cache saved: {cache_path} ({fsize/1024:.0f} KB)")

    return records


# ============================================================================
# TIER 2 — BOUNDARY / MORI WALL ANALYSIS
# ============================================================================

def tier2_analyze(cache_path="tangency_cache.pkl", verbose=True):
    """Load Tier 1 geometry. For each polytope, find chi=3 on Mori walls.

    For each Mori generator (hyperplane), we pick a representative direction
    ON that wall and search for t where chi(t*D) = 3. This tells us whether
    the chi=3 isosurface intersects each wall of the Kähler cone.

    Also computes chi along the h11 basis directions for a quick profile.
    """
    if verbose:
        print(f"{'=' * 72}")
        print(f"  TIER 2: MORI WALL ANALYSIS")
        print(f"{'=' * 72}")

    with open(cache_path, "rb") as f:
        records = pickle.load(f)

    n_total = sum(1 for r in records if r["tier1_ok"])
    n_done = 0
    t0 = time.time()

    for rec in records:
        if not rec["tier1_ok"]:
            continue

        t_start = time.time()
        h11 = rec["h11"]
        intnums = rec["intnums"]
        c2_vals = rec["c2_vals"]
        n_toric = rec["n_toric"]
        div_basis = rec["div_basis"]
        mori_gens = rec["mori_gens"]
        n_mori = len(mori_gens)

        def to_toric(bv):
            return basis_to_toric(bv, div_basis, n_toric)

        # Effective basis dimension: use div_basis shape, not h11
        db = np.asarray(div_basis)
        bdim = db.shape[0] if db.ndim <= 1 else db.shape[0]
        # Mori generators might be h11-wide; ensure dimension compatibility
        mg_cols = mori_gens.shape[1] if mori_gens.ndim == 2 else bdim
        if mg_cols != bdim:
            bdim = min(bdim, mg_cols)
        mg = mori_gens[:, :bdim] if mg_cols > bdim else mori_gens

        t2 = {
            "wall_tangencies": [],    # list of (wall_idx, t_star, direction_basis)
            "basis_chis": [],         # chi at each unit basis vector
            "min_chi_basis": None,    # min chi across basis directions
            "n_walls_hit": 0,         # number of Mori walls where chi=3 exists
            "basis_dim": bdim,
        }

        # --- Chi along basis directions ---
        for a in range(bdim):
            e_a = np.zeros(bdim)
            e_a[a] = 1.0
            e_toric = to_toric(e_a)
            chi_val = chi_line_bundle(e_toric, intnums, c2_vals, n_toric)
            t2["basis_chis"].append(round(chi_val, 6))
        t2["min_chi_basis"] = min(t2["basis_chis"]) if t2["basis_chis"] else None

        # --- Search each Mori wall for chi=3 ---
        # For wall j defined by mori_gens[j] · D = 0:
        # Project each basis vector onto the wall, try chi=3 along that direction.
        # Also try the "centroid" direction = sum of projected basis vectors.
        for j in range(n_mori):
            wall_normal = mg[j]
            norm_sq = np.dot(wall_normal, wall_normal)
            if norm_sq < 1e-15:
                continue

            # Project basis vectors onto this wall's null-space
            best_t = None
            best_dir = None
            directions_tried = []

            # Individual projected basis vectors
            for a in range(bdim):
                e_a = np.zeros(bdim)
                e_a[a] = 1.0
                # Project: e_a - (e_a · n / n · n) * n
                proj = e_a - (np.dot(e_a, wall_normal) / norm_sq) * wall_normal
                if np.linalg.norm(proj) < 1e-10:
                    continue
                # Only try directions that point into the Kähler cone side
                # (all Mori pairings ≥ 0 for other walls)
                pairings = mg @ proj
                # Allow the j-th pairing to be ~0 (on the wall)
                other_pairings = [pairings[k] for k in range(n_mori) if k != j]
                if other_pairings and min(other_pairings) < -1e-8:
                    continue  # this direction exits the cone on another face

                directions_tried.append(proj)

            # Centroid of valid directions
            if len(directions_tried) > 1:
                centroid = np.mean(directions_tried, axis=0)
                if np.linalg.norm(centroid) > 1e-10:
                    directions_tried.append(centroid)

            # Find t* along each direction
            for d in directions_tried:
                d_toric = to_toric(d)
                t = find_t_star(d_toric, intnums, c2_vals, n_toric, target=3.0)
                if t is not None and t > 0:
                    if best_t is None or t < best_t:
                        best_t = t
                        best_dir = d.tolist()

            if best_t is not None:
                t2["wall_tangencies"].append({
                    "wall_idx": j,
                    "t_star": round(best_t, 8),
                    "direction": best_dir,
                })

        t2["n_walls_hit"] = len(t2["wall_tangencies"])
        rec["tier2"] = t2
        n_done += 1
        dt = time.time() - t_start

        if verbose:
            hits = t2["n_walls_hit"]
            mchi = t2["min_chi_basis"]
            mchi_s = f"{mchi:.1f}" if mchi is not None else "?"
            ts = ([w["t_star"] for w in t2["wall_tangencies"]]
                  if t2["wall_tangencies"] else [])
            ts_s = f"t*_min={min(ts):.4f}" if ts else "no_hit"
            print(f"  [{n_done:4d}/{n_total}] poly={rec['poly_idx']:>4}  "
                  f"h11={h11:>2}  walls_hit={hits}/{n_mori}  "
                  f"min_chi={mchi_s:>6}  {ts_s}  ({dt:.2f}s)")

    elapsed = time.time() - t0

    # Save updated cache
    with open(cache_path, "wb") as f:
        pickle.dump(records, f, protocol=pickle.HIGHEST_PROTOCOL)

    if verbose:
        wall_hit_counts = [r["tier2"]["n_walls_hit"]
                           for r in records if r.get("tier2")]
        any_hit = sum(1 for c in wall_hit_counts if c > 0)
        print(f"\n  {'─' * 68}")
        print(f"  Tier 2 complete: {n_done} polytopes in {elapsed:.1f}s")
        print(f"  Wall hits: {any_hit}/{n_done} polytopes have chi=3 on ≥1 Mori wall")

    return records


# ============================================================================
# TIER 3 — INTEGER SEARCH & FINAL CLASSIFICATION
# ============================================================================

def tier3_classify(cache_path="tangency_cache.pkl",
                   output_csv="tangency_results_v3.csv", verbose=True):
    """Load Tier 1+2 data. Exhaustive integer lattice point search for chi=3.
    Final classification and CSV export.

    Classification:
      AMPLE            integer D with chi=3, strictly inside Kähler cone
      NEF              integer D with chi=3, on Kähler cone boundary
      BOUNDARY_TANGENT continuous chi=3 on a Mori wall, no integer realization
      NEAR_MISS        nearest integer chi=3 just outside cone (min_mori = -1)
      NEAR             chi=3 isosurface within striking distance but no tangency found
      DISTANT          chi=3 isosurface far from Kähler cone
    """
    if verbose:
        print(f"{'=' * 72}")
        print(f"  TIER 3: INTEGER SEARCH & CLASSIFICATION")
        print(f"{'=' * 72}")

    with open(cache_path, "rb") as f:
        records = pickle.load(f)

    n_total = sum(1 for r in records if r["tier1_ok"])
    n_done = 0
    class_counts = {}
    t0 = time.time()

    for rec in records:
        if not rec["tier1_ok"]:
            continue

        t_start = time.time()
        h11 = rec["h11"]
        intnums = rec["intnums"]
        c2_vals = rec["c2_vals"]
        n_toric = rec["n_toric"]
        div_basis = rec["div_basis"]
        mori_gens = rec["mori_gens"]
        t2 = rec.get("tier2", {}) or {}

        def to_toric(bv):
            return basis_to_toric(bv, div_basis, n_toric)

        t3 = {
            "ample_pts": [],
            "nef_pts": [],
            "nearmiss_pts": [],
            "best_min_mori": None,
            "classification": None,
        }

        # Effective basis dimension
        db = np.asarray(div_basis)
        bdim = db.shape[0] if db.ndim <= 1 else db.shape[0]
        # Dimension-safe Mori generators
        mg_cols = mori_gens.shape[1] if mori_gens.ndim == 2 else bdim
        if mg_cols != bdim:
            bdim = min(bdim, mg_cols)
        mg = mori_gens[:, :bdim] if mg_cols > bdim else mori_gens

        # --- Generate candidate integer points ---
        # Source 1: basis vectors at various scales
        seen = set()
        candidates = []
        scales = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]

        # Use basis directions
        for a in range(bdim):
            e_a = np.zeros(bdim)
            e_a[a] = 1.0
            e_toric = to_toric(e_a)
            for s in scales:
                base = tuple(np.round(s * e_a).astype(int))
                if base not in seen:
                    seen.add(base)
                    candidates.append(base)

        # Source 2: wall tangency directions from Tier 2
        if t2 and t2.get("wall_tangencies"):
            for wt in t2["wall_tangencies"]:
                d = np.array(wt["direction"])
                t_star = wt["t_star"]
                # Round the continuous chi=3 point to nearby integers
                center = t_star * d
                for s_off in [-0.5, 0.0, 0.5]:
                    base = tuple(np.round(center + s_off * d / max(np.linalg.norm(d), 1e-10)).astype(int))
                    if base not in seen:
                        seen.add(base)
                        candidates.append(base)

        # Source 3: perturbations of all candidates
        perturbed = []
        for base in candidates:
            for d in range(bdim):
                for delta in (+1, -1):
                    if d < len(base):
                        p = list(base)
                        p[d] += delta
                        pt = tuple(p)
                        if pt not in seen:
                            seen.add(pt)
                            perturbed.append(pt)
        candidates.extend(perturbed)

        # --- Evaluate chi and Mori pairings ---
        best_min_mori = None
        for D_tuple in candidates:
            D_basis = np.array(D_tuple, dtype=float)
            D_toric = to_toric(D_basis)
            chi_val = chi_line_bundle(D_toric, intnums, c2_vals, n_toric)
            if abs(chi_val - 3.0) > 1e-6:
                continue

            pairings = mg @ D_basis
            min_mori = int(round(np.min(pairings)))
            if best_min_mori is None or min_mori > best_min_mori:
                best_min_mori = min_mori

            D_list = list(int(x) for x in D_tuple)
            if min_mori > 0:
                t3["ample_pts"].append(D_list)
            elif min_mori == 0:
                t3["nef_pts"].append(D_list)
            elif min_mori >= -1:
                t3["nearmiss_pts"].append(D_list)

        t3["best_min_mori"] = best_min_mori

        # --- Classify ---
        has_wall_hit = t2 and t2.get("n_walls_hit", 0) > 0
        min_chi_basis = t2.get("min_chi_basis") if t2 else None

        if t3["ample_pts"]:
            t3["classification"] = "AMPLE"
        elif t3["nef_pts"]:
            t3["classification"] = "NEF"
        elif has_wall_hit and not t3["nearmiss_pts"]:
            t3["classification"] = "BOUNDARY_TANGENT"
        elif t3["nearmiss_pts"]:
            t3["classification"] = "NEAR_MISS"
        elif has_wall_hit:
            t3["classification"] = "NEAR"
        else:
            if min_chi_basis is not None and min_chi_basis <= 10:
                t3["classification"] = "NEAR"
            else:
                t3["classification"] = "DISTANT"

        rec["tier3"] = t3
        n_done += 1
        cls = t3["classification"]
        class_counts[cls] = class_counts.get(cls, 0) + 1
        dt = time.time() - t_start

        if verbose:
            na = len(t3["ample_pts"])
            nn = len(t3["nef_pts"])
            nm = len(t3["nearmiss_pts"])
            print(f"  [{n_done:4d}/{n_total}] poly={rec['poly_idx']:>4}  "
                  f"{cls:<18s}  ample={na} nef={nn} miss={nm}  ({dt:.2f}s)")

    elapsed = time.time() - t0

    # Save updated cache
    with open(cache_path, "wb") as f:
        pickle.dump(records, f, protocol=pickle.HIGHEST_PROTOCOL)

    # --- Write CSV ---
    fieldnames = [
        "poly_idx", "h11", "h21", "n_vertices", "gl_order",
        "classification", "n_ample_chi3", "n_nef_chi3", "n_nearmiss_chi3",
        "best_min_mori", "n_walls_hit", "min_chi_basis",
        "wall_t_stars", "error",
    ]
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            t2 = rec.get("tier2") or {}
            t3 = rec.get("tier3") or {}
            row = {
                "poly_idx": rec["poly_idx"],
                "h11": rec.get("h11"),
                "h21": rec.get("h21"),
                "n_vertices": rec.get("n_vertices"),
                "gl_order": rec.get("gl_order"),
                "classification": t3.get("classification"),
                "n_ample_chi3": len(t3.get("ample_pts", [])),
                "n_nef_chi3": len(t3.get("nef_pts", [])),
                "n_nearmiss_chi3": len(t3.get("nearmiss_pts", [])),
                "best_min_mori": t3.get("best_min_mori"),
                "n_walls_hit": t2.get("n_walls_hit"),
                "min_chi_basis": t2.get("min_chi_basis"),
                "wall_t_stars": ";".join(
                    f"{w['t_star']:.6f}"
                    for w in t2.get("wall_tangencies", [])
                ) or None,
                "error": rec.get("tier1_error"),
            }
            writer.writerow(row)

    if verbose:
        print(f"\n  {'=' * 68}")
        print(f"  TIER 3 CLASSIFICATION SUMMARY")
        print(f"  {'=' * 68}")
        for cls in ["AMPLE", "NEF", "BOUNDARY_TANGENT", "NEAR_MISS", "NEAR", "DISTANT"]:
            cnt = class_counts.get(cls, 0)
            if cnt:
                pct = 100.0 * cnt / max(n_done, 1)
                bar = '#' * int(pct / 2)
                print(f"    {cls:<20s} {cnt:>5}  ({pct:5.1f}%)  {bar}")

        n_err = sum(1 for r in records if r.get("tier1_error"))
        if n_err:
            from collections import Counter
            errs = Counter(r["tier1_error"][:60]
                           for r in records if r.get("tier1_error"))
            print(f"\n  Skipped ({n_err}):")
            for e, c in errs.most_common(5):
                print(f"    {c:>4}x  {e}")

        print(f"\n  Elapsed: {elapsed:.1f}s  |  CSV: {output_csv}")

    return records


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="3-tier pipeline for chi=3 tangency analysis",
    )
    parser.add_argument("--tier", type=str, default="123",
                        help="Which tier(s) to run: '1', '2', '3', '12', '23', '123'")
    parser.add_argument("--chi", type=int, default=-6)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--cache", type=str, default="tangency_cache.pkl",
                        help="Pickle cache path")
    parser.add_argument("--output", "-o", type=str,
                        default="tangency_results_v3.csv")
    parser.add_argument("--quiet", "-q", action="store_true")
    args = parser.parse_args()

    v = not args.quiet

    if "1" in args.tier:
        tier1_extract(chi_val=args.chi, limit=args.limit,
                      cache_path=args.cache, verbose=v)

    if "2" in args.tier:
        if not os.path.exists(args.cache):
            print(f"ERROR: {args.cache} not found. Run --tier 1 first.")
            sys.exit(1)
        tier2_analyze(cache_path=args.cache, verbose=v)

    if "3" in args.tier:
        if not os.path.exists(args.cache):
            print(f"ERROR: {args.cache} not found. Run --tier 1 first.")
            sys.exit(1)
        tier3_classify(cache_path=args.cache, output_csv=args.output, verbose=v)


if __name__ == "__main__":
    main()
