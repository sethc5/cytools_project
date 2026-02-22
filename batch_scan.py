#!/usr/bin/env python3
"""
batch_scan.py — Tier 1 scan of all chi=+-6 CY3 manifolds in the KS database.

Fetches polytopes from the Kreuzer-Skarke database with |chi|=6, runs Tier 1
analysis on each manifold, and exports results to a CSV file.

Usage:
    python batch_scan.py                      # scan chi=-6 manifolds (default)
    python batch_scan.py --chi 6              # scan chi=+6 manifolds
    python batch_scan.py --limit 500          # fetch up to 500 polytopes
    python batch_scan.py --output results.csv

Requires: cytools, numpy
"""

import argparse
import csv
import sys
import time

import numpy as np

try:
    from cytools import fetch_polytopes
except ImportError:
    print("ERROR: CYTools not installed. See https://cy.tools for setup.")
    sys.exit(1)

# Import Tier 1 from scan_manifold
from scan_manifold import run_tier1


def scan_ks_chi6(chi_val=-6, limit=1000, output_path="chi6_tier1_scan.csv",
                 favorable_only=False, verbose=True):
    """Scan chi=chi_val manifolds in KS database."""

    if verbose:
        print(f"{'='*72}")
        print(f"  BATCH SCAN: chi={chi_val} MANIFOLDS FROM KS DATABASE")
        print(f"{'='*72}")
        fav_str = " (favorable only)" if favorable_only else ""
        print(f"\n  Fetching up to {limit} polytopes{fav_str}...")

    # Fetch polytopes
    t_fetch_start = time.time()
    try:
        polytopes = fetch_polytopes(
            chi=chi_val, lattice="N", limit=limit, timeout=180,
            favorable=True if favorable_only else None,
        )
        if not isinstance(polytopes, list):
            polytopes = list(polytopes)
    except Exception as e:
        print(f"  ERROR fetching polytopes: {e}")
        return []

    t_fetch = time.time() - t_fetch_start
    if verbose:
        print(f"  Fetched {len(polytopes)} polytopes in {t_fetch:.1f}s")

    # Run Tier 1 on each
    all_results = []
    t_start = time.time()
    n_success = 0
    n_error = 0

    for poly_idx, p in enumerate(polytopes):
        poly_id = f"poly_{poly_idx}"
        row = {
            "poly_id": poly_id,
            "h11": None, "h21": None, "chi": None,
            "n_vertices": len(p.vertices()),
            "n_points": len(p.points()),
            "is_favorable": None,
            "tier1_score": None,
            "tier1_max": None,
            "n_rigid_dP": None,
            "n_K3": None,
            "n_intnums": None,
            "n_kahler_walls": None,
            "n_mori_generators": None,
            "vol_tip": None,
            "k_ratio": None,
            "h11_quotient": None,
            "gl_order": None,
            "error": None,
        }

        try:
            # Triangulate and construct CY3
            t = p.triangulate()
            try:
                cy = t.get_cy()
            except Exception as e:
                if "non-favorable" in str(e).lower() or "experimental" in str(e).lower():
                    row["error"] = "non-favorable"
                    row["is_favorable"] = False
                    # Still record h11/h21 from polytope if possible
                    try:
                        tv = t.get_toric_variety()
                        row["h11"] = tv.h11()
                        row["h21"] = tv.h21()
                        row["chi"] = 2 * (tv.h11() - tv.h21())
                    except Exception:
                        pass
                    n_error += 1
                    if verbose:
                        print(f"  [{poly_idx+1}/{len(polytopes)}] {poly_id}: "
                              f"SKIP (non-favorable)")
                    all_results.append(row)
                    continue
                else:
                    raise

            row["is_favorable"] = True
            h11 = cy.h11()
            h21 = cy.h21()
            row["h11"] = h11
            row["h21"] = h21
            row["chi"] = 2 * (h11 - h21)

            # GL symmetry order
            try:
                gl = len(p.automorphisms())
            except Exception:
                gl = None
            row["gl_order"] = gl

            # Run Tier 1
            score, total, results = run_tier1(cy, p, verbose=False)

            row["tier1_score"] = score
            row["tier1_max"] = total
            row["n_rigid_dP"] = results.get("n_rigid_dP", 0)
            row["n_K3"] = results.get("n_K3", 0)
            row["n_intnums"] = results.get("n_intnums", 0)
            row["n_kahler_walls"] = results.get("n_kahler_walls", 0)
            row["n_mori_generators"] = results.get("n_mori_generators", 0)
            row["vol_tip"] = results.get("vol_tip", 0)
            row["k_ratio"] = results.get("k_ratio")
            row["h11_quotient"] = results.get("h11_quotient")

            n_success += 1

            if verbose:
                status = f"{score}/{total}"
                flags = []
                if row["n_rigid_dP"] and row["n_rigid_dP"] > 10:
                    flags.append(f"{row['n_rigid_dP']}dP")
                if gl and gl >= 6:
                    flags.append(f"GL={gl}")
                flag_str = f"  [{', '.join(flags)}]" if flags else ""
                print(f"  [{poly_idx+1}/{len(polytopes)}] {poly_id}: "
                      f"h11={h11}, h21={h21}, T1={status}{flag_str}")

        except Exception as e:
            row["error"] = str(e)[:200]
            n_error += 1
            if verbose:
                print(f"  [{poly_idx+1}/{len(polytopes)}] {poly_id}: ERROR: {e}")

        all_results.append(row)

    elapsed = time.time() - t_start

    # Write CSV
    if all_results:
        fieldnames = list(all_results[0].keys())
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        if verbose:
            print(f"\n  Results written to {output_path}")

    # Summary
    n_perfect = sum(1 for r in all_results
                    if r["tier1_score"] is not None
                    and r["tier1_score"] == r["tier1_max"])

    if verbose:
        print(f"\n{'='*72}")
        print(f"  BATCH SCAN SUMMARY")
        print(f"{'='*72}")
        print(f"  Total polytopes fetched: {len(polytopes)}")
        print(f"  Successful Tier 1 scans: {n_success}")
        print(f"  Skipped/errors: {n_error}")
        print(f"  Perfect Tier 1 score: {n_perfect}")
        print(f"  Elapsed: {elapsed:.1f}s")

        # h11 distribution
        h11_dist = {}
        for r in all_results:
            h = r.get("h11")
            if h is not None:
                h11_dist[h] = h11_dist.get(h, 0) + 1
        if h11_dist:
            print(f"\n  h11 distribution:")
            for h11, cnt in sorted(h11_dist.items()):
                print(f"    h11={h11:>3}: {cnt} polytopes")

        # Top candidates
        scored = [r for r in all_results if r["tier1_score"] is not None]
        if scored:
            scored.sort(key=lambda r: (-r["tier1_score"],
                                       -(r["n_rigid_dP"] or 0),
                                       -(r["gl_order"] or 0)))
            print(f"\n  Top 15 candidates:")
            print(f"  {'ID':>12} | {'h11':>3} | {'h21':>3} | {'T1':>5} | "
                  f"{'dP':>4} | {'GL':>4} | {'walls':>5} | {'Mori':>5} | {'Vol':>8}")
            for r in scored[:15]:
                gl_str = str(r["gl_order"]) if r["gl_order"] else "?"
                vol_str = f"{r['vol_tip']:.0f}" if r["vol_tip"] else "?"
                walls = str(r["n_kahler_walls"]) if r["n_kahler_walls"] else "?"
                mori = str(r["n_mori_generators"]) if r["n_mori_generators"] else "?"
                print(f"  {r['poly_id']:>12} | "
                      f"{r['h11'] or '?':>3} | {r['h21'] or '?':>3} | "
                      f"{r['tier1_score']}/{r['tier1_max']:>2} | "
                      f"{r['n_rigid_dP'] or 0:>4} | {gl_str:>4} | "
                      f"{walls:>5} | {mori:>5} | {vol_str:>8}")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Batch Tier 1 scan of chi=+-6 CY3 manifolds from KS database",
    )
    parser.add_argument("--chi", type=int, default=-6,
                        help="Euler characteristic to scan (default: -6)")
    parser.add_argument("--limit", type=int, default=1000,
                        help="Max polytopes to fetch (default: 1000)")
    parser.add_argument("--favorable-only", action="store_true",
                        help="Only scan favorable polytopes")
    parser.add_argument("--output", "-o", type=str, default="chi6_tier1_scan.csv",
                        help="Output CSV path (default: chi6_tier1_scan.csv)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress verbose output")
    args = parser.parse_args()

    scan_ks_chi6(
        chi_val=args.chi,
        limit=args.limit,
        output_path=args.output,
        favorable_only=args.favorable_only,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
