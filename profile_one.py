#!/usr/bin/env python3
"""Profile each step on a single polytope."""
import time, sys, numpy as np
from cytools import fetch_polytopes
from cytools.config import enable_experimental_features
enable_experimental_features()

def flush(msg):
    print(msg, flush=True)

t0 = time.time()
polytopes = list(fetch_polytopes(chi=-6, lattice="N", limit=1))
p = polytopes[0]
flush(f"1. FETCH:          {time.time()-t0:.3f}s")

t1 = time.time()
tri = p.triangulate()
cy = tri.get_cy()
flush(f"2. TRI+CY:         {time.time()-t1:.3f}s  h11={cy.h11()}")

t2 = time.time()
db = np.asarray(cy.divisor_basis())
flush(f"3. DIV_BASIS:      {time.time()-t2:.3f}s  shape={db.shape}")

t3 = time.time()
intnums = cy.intersection_numbers()
flush(f"4. INTNUMS:        {time.time()-t3:.3f}s  entries={len(intnums)}")

t4 = time.time()
c2 = np.array(cy.second_chern_class(), dtype=float)
flush(f"5. C2:             {time.time()-t4:.3f}s  len={len(c2)}")

t5 = time.time()
kc = cy.toric_kahler_cone()
flush(f"6. KAHLER_CONE:    {time.time()-t5:.3f}s")

t6 = time.time()
hyps = np.array(kc.hyperplanes(), dtype=float)
flush(f"7. HYPERPLANES:    {time.time()-t6:.3f}s  n_mori={len(hyps)}")

# Skip rays() — it's the expensive one. Use hyperplanes only.
flush(f"\n   Skipping kc.rays() — too slow for h11={cy.h11()}")
flush(f"   Strategy: use MORI generators (hyperplanes) directly\n")

# Test chi computation speed on Mori generators
if db.ndim == 2:
    n_toric = db.shape[1]
    def to_toric(bv):
        return np.asarray(bv, dtype=float) @ db.astype(float)
else:
    n_toric = max(int(db.max()) + 1, len(c2))
    def to_toric(bv):
        v = np.zeros(n_toric)
        for a, val in enumerate(bv):
            v[int(db[a])] = val
        return v

c2v = c2.copy()
if len(c2v) < n_toric:
    c2v = np.pad(c2v, (0, n_toric - len(c2v)))

def chi_lb(n_vec):
    n = np.array(n_vec, dtype=float)
    if len(n) < n_toric: n = np.pad(n, (0, n_toric - len(n)))
    cubic = 0.0
    for (a,b,c), kval in intnums.items():
        if max(a,b,c) >= n_toric: continue
        if a==b==c: cubic += kval * n[a]**3
        elif a==b: cubic += 3*kval*n[a]**2*n[c]
        elif b==c: cubic += 3*kval*n[a]*n[b]**2
        elif a==c: cubic += 3*kval*n[a]**2*n[b]
        else: cubic += 6*kval*n[a]*n[b]*n[c]
    return cubic/6 + np.dot(c2v[:n_toric], n[:n_toric])/12

# Chi on each Mori generator
t7 = time.time()
mori_chis = []
for h in hyps:
    ht = to_toric(h)
    mori_chis.append(chi_lb(ht))
flush(f"8. CHI on {len(hyps)} Mori gens: {time.time()-t7:.3f}s")
flush(f"   chi range: [{min(mori_chis):.2f}, {max(mori_chis):.2f}]")

# brentq on each Mori direction
from scipy.optimize import brentq
t8 = time.time()
test_ts = np.linspace(0.01, 5.0, 30)
n_found = 0
for h in hyps:
    ht = to_toric(h)
    def f(t, _ht=ht): return chi_lb(t * _ht) - 3.0
    try:
        vals = [f(t) for t in test_ts]
        for j in range(len(vals)-1):
            if vals[j]*vals[j+1] < 0:
                brentq(f, test_ts[j], test_ts[j+1], xtol=1e-10)
                n_found += 1
                break
    except: pass
flush(f"9. BRENTQ on {len(hyps)} Mori: {time.time()-t8:.3f}s  found={n_found}")

# Integer search near identity
t9 = time.time()
n_chi3 = 0
search_range = range(-3, 4)
h11 = cy.h11()
if h11 > 10:  # Limit search for high h11
    search_range = range(-1, 3)
count = 0
for coords in np.ndindex(*([len(list(search_range))] * min(h11, 6))):
    D = np.array([list(search_range)[c] for c in coords] + [0]*(h11 - min(h11,6)), dtype=float)
    if np.all(D == 0): continue
    Dt = to_toric(D)
    chi = chi_lb(Dt)
    count += 1
    if abs(chi - 3.0) < 1e-6:
        pairings = hyps @ D
        min_mori = int(round(np.min(pairings)))
        n_chi3 += 1
        if n_chi3 <= 5:
            flush(f"   FOUND chi=3: D={D[:6]}... min_mori={min_mori}")
flush(f"10. INT SEARCH ({count} pts): {time.time()-t9:.3f}s  chi=3 found={n_chi3}")

flush(f"\nTOTAL: {time.time()-t0:.3f}s")
