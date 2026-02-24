#!/usr/bin/env python3
"""Scan automorphism groups across all 3-generation candidates.
Run on Codespace where CYTools is available."""

import cytools as cy
import json
import time
from collections import Counter

# Load our top candidates from auto_scan results
candidates = []
for h, fn in [(15, "results/auto_h15.json"), (16, "results/auto_h16.json"), (17, "results/auto_h17.json")]:
    with open(fn) as f:
        data = json.load(f)
    for r in data["results"]:
        if r["n_clean"] >= 1:
            candidates.append((h, r["poly_idx"], r["score"], r["n_clean"], r["n_ell"]))

print(f"Total candidates with clean h0=3 bundles: {len(candidates)}")
print()

# Sort by clean count descending
candidates.sort(key=lambda x: -x[3])

# Cache polytopes by h-value
poly_cache = {}
results = []
t0 = time.time()

for h, pidx, score, nclean, nell in candidates:
    if h not in poly_cache:
        print(f"  Fetching h11={h} polytopes...", flush=True)
        poly_cache[h] = list(cy.fetch_polytopes(h11=h, h21=h+3, lattice="N", limit=50000))
        print(f"    got {len(poly_cache[h])}")

    polys = poly_cache[h]
    if pidx >= len(polys):
        continue

    p = polys[pidx]
    try:
        auts = p.automorphisms()
        naut = len(auts)
    except Exception:
        naut = -1

    results.append((h, pidx, score, nclean, nell, naut))

    if naut > 1:
        print(f"  *** h{h}/P{pidx}: |Aut| = {naut}, score={score}, clean={nclean}, ell={nell}")

elapsed = time.time() - t0
print(f"\nDone scanning candidates in {elapsed:.0f}s")

# Summary
print(f"\n{'='*60}")
print(f"  AUTOMORPHISM GROUP SUMMARY")
print(f"{'='*60}")
print(f"Total polytopes checked: {len(results)}")

nontrivial = [(h,p,s,c,e,a) for h,p,s,c,e,a in results if a > 1]
print(f"Nontrivial |Aut| > 1: {len(nontrivial)}")

if nontrivial:
    print(f"\nPolytopes with nontrivial automorphism groups:")
    header = f"  {'h11':>4} {'Poly':>6} {'Score':>7} {'Clean':>6} {'Ell':>4} {'|Aut|':>6}"
    print(header)
    print(f"  {'-'*len(header)}")
    for h,p,s,c,e,a in sorted(nontrivial, key=lambda x: -x[5]):
        print(f"  {h:4d} P{p:>5d} {s:>5d}/26 {c:>6d} {e:>4d} {a:>6d}")
else:
    print("\nAll candidates have trivial automorphism group (|Aut| = 1)")

# Distribution
aut_counts = Counter(a for _,_,_,_,_,a in results)
print(f"\nAutomorphism group size distribution:")
for size in sorted(aut_counts.keys()):
    print(f"  |Aut| = {size}: {aut_counts[size]} polytopes")

# Also check: what about ALL polytopes with |Aut| > 1 at each h-value?
# Cross-reference with their max_h0
print(f"\n{'='*60}")
print(f"  SYMMETRY vs h0: ALL POLYTOPES")
print(f"{'='*60}")

import csv

for h in [15, 16, 17]:
    # Load scan CSV for max_h0 data
    scan_data = {}
    with open(f"results/scan_h{h}.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pidx = int(row["poly_idx"])
            max_h0 = int(row["max_h0"])
            h0_3 = int(row["h0_3_count"])
            scan_data[pidx] = (max_h0, h0_3)

    # Check all polytopes for automorphisms
    polys = poly_cache[h]
    big_aut = []
    for i, p in enumerate(polys):
        try:
            a = len(p.automorphisms())
            if a > 1:
                mh0, h03 = scan_data.get(i, (0, 0))
                big_aut.append((i, a, mh0, h03))
        except Exception:
            pass

    print(f"\nh{h}: {len(big_aut)} polytopes with |Aut| > 1 (out of {len(polys)})")
    if big_aut:
        print(f"  {'Poly':>6} {'|Aut|':>6} {'max_h0':>7} {'h0=3_ct':>8}")
        for pidx, a, mh0, h03 in sorted(big_aut, key=lambda x: -x[1]):
            marker = " <-- h0>=3!" if mh0 >= 3 else ""
            print(f"  P{pidx:>5d} {a:>6d} {mh0:>7d} {h03:>8d}{marker}")
