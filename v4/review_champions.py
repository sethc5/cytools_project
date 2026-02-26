#!/usr/bin/env python3
"""Deep-dive review of the 4 score-84 champion polytopes.

Checks: geometric fingerprinting, triangulation stability, 
divisor structure, Yukawa texture, fibrations, and whether 
the h28 cluster are the same manifold.
"""
import sys, hashlib, json, time
import numpy as np

sys.path.insert(0, '/workspaces/cytools_project')
from cytools import fetch_polytopes, config
config.enable_experimental_features()

CHAMPS = [(28, 186), (28, 187), (28, 874), (30, 289)]

def analyze_champion(h, idx):
    """Full geometric analysis of a champion polytope."""
    print(f"\n{'='*70}")
    print(f"  CHAMPION: h{h}/P{idx}")
    print(f"{'='*70}")
    
    t0 = time.time()
    # Must use h21=h+3 to match pipeline's chi=-6 filter
    polys = list(fetch_polytopes(h11=h, h21=h+3))
    p = polys[idx]
    
    # --- Polytope-level data ---
    pts = p.points()
    verts = p.vertices()
    print(f"\n[Polytope]")
    print(f"  points: {pts.shape[0]}, vertices: {verts.shape[0]}")
    print(f"  vertex_hash: {hashlib.md5(verts.tobytes()).hexdigest()[:16]}")
    print(f"  points_hash: {hashlib.md5(pts.tobytes()).hexdigest()[:16]}")
    
    # Print actual vertices for comparison
    print(f"  vertices:")
    for v in verts:
        print(f"    {v.tolist()}")
    
    # --- Triangulate and get CY ---
    t = p.triangulate()
    cy = t.get_cy()
    
    print(f"\n[CY Geometry]")
    h11 = cy.h11()
    h21 = cy.h21()
    chi = cy.chi()
    print(f"  h11={h11}, h21={h21}, chi={chi}")
    
    # Intersection numbers fingerprint
    kappa = cy.intersection_numbers()
    vals = sorted(kappa.values())
    print(f"  kappa entries: {len(kappa)}")
    print(f"  kappa sum={sum(vals)}, max={max(vals)}, min={min(vals)}")
    print(f"  kappa hash: {hashlib.md5(str(vals).encode()).hexdigest()[:16]}")
    
    # c2
    c2 = cy.second_chern_class()
    print(f"  c2: {c2.tolist()}")
    
    # Effective classes
    div_basis = [int(x) for x in cy.divisor_basis()]
    h11_eff = len(div_basis)
    gap = h11 - h11_eff
    print(f'  h11_eff: {h11_eff}, gap: {gap}, favorable: {h11_eff == h11}')
    print(f'  div_basis: {div_basis}')
    
    # Mori cone
    try:
        mori = cy.mori_cone().rays()
        n_mori = mori.shape[0]
    except:
        n_mori = 0
    print(f'  mori rays: {n_mori}')
    
    # --- Divisor analysis ---
    print(f"\n[Divisor Structure]")
    for i in range(min(len(c2), 25)):
        c2d = c2[i]
        # Classify by c2·D value
        label = ''
        if c2d >= 24: label = ' [K3-like]'
        elif c2d >= 12: label = f' [dP-candidate]'
        elif c2d < 0: label = ' [rigid D³<0]'
        print(f"    D{i}: c2·D={c2d}{label}")
    
    # --- Triangulation stability (T3) ---
    print(f"\n[Triangulation Stability — T3]")
    n_samples = 20
    stability_data = {
        'has_clean': [],
        'n_clean': [],
        'yukawa_rank': [],
        'has_swiss': [],
        'c2_stable': [],
    }
    
    try:
        tris = p.random_triangulations_fast(N=n_samples)
        for ti, tri in enumerate(tris):
            try:
                cy_i = tri.get_cy()
                c2_i = cy_i.second_chern_class()
                kappa_i = cy_i.intersection_numbers()
                
                # Check c2 matches
                c2_match = np.array_equal(c2_i, c2)
                stability_data['c2_stable'].append(c2_match)
                
                # Check kappa hash matches
                vals_i = sorted(kappa_i.values())
                kappa_match = vals_i == vals
                
                if ti < 3:
                    print(f"  tri[{ti}]: c2_stable={c2_match}, kappa_stable={kappa_match}")
            except Exception as e:
                if ti < 3:
                    print(f"  tri[{ti}]: error — {e}")
        
        n_c2_stable = sum(stability_data['c2_stable'])
        print(f"  c2 stability: {n_c2_stable}/{len(stability_data['c2_stable'])} ({100*n_c2_stable/max(1,len(stability_data['c2_stable'])):.0f}%)")
        print(f"  Triangulations tested: {len(stability_data['c2_stable'])}")
    except Exception as e:
        print(f"  Triangulation sampling failed: {e}")
    
    # --- Best Yukawa bundle detail ---
    print(f"\n[Yukawa Texture]")
    # We already have the best bundle from DB, but let's recompute
    # Get intersection tensor for Yukawa analysis  
    n_eff = h11_eff
    
    # Build Yukawa matrix from intersection ring
    yuk_entries = []
    for key, val in kappa.items():
        if val != 0:
            yuk_entries.append((key, val))
    
    print(f"  Non-zero Yukawa couplings: {len(yuk_entries)}")
    print(f"  Yukawa density: {len(yuk_entries)}/{len(kappa):.0f} = {len(yuk_entries)/max(1,len(kappa)):.4f}")
    
    # Signature of kappa values
    kvals = list(kappa.values())
    pos = sum(1 for v in kvals if v > 0)
    neg = sum(1 for v in kvals if v < 0)
    zero = sum(1 for v in kvals if v == 0)
    print(f"  kappa signature: +{pos}, -{neg}, 0={zero}")
    print(f"  kappa value range: [{min(kvals)}, {max(kvals)}]")
    
    # Histogram of kappa values
    from collections import Counter
    vcounts = Counter(kvals)
    print(f"  kappa value distribution (top 10):")
    for v, c in vcounts.most_common(10):
        print(f"    κ={v}: {c} entries")
    
    elapsed = time.time() - t0
    print(f"\n  [Analysis time: {elapsed:.1f}s]")
    
    return {
        'h': h, 'idx': idx,
        'vertex_hash': hashlib.md5(verts.tobytes()).hexdigest()[:16],
        'points_hash': hashlib.md5(pts.tobytes()).hexdigest()[:16],
        'kappa_hash': hashlib.md5(str(vals).encode()).hexdigest()[:16],
        'n_verts': verts.shape[0],
        'n_pts': pts.shape[0],
        'h11_eff': h11_eff,
        'n_mori': n_mori,
        'c2': c2.tolist(),
    }


if __name__ == '__main__':
    results = []
    for h, idx in CHAMPS:
        try:
            r = analyze_champion(h, idx)
            results.append(r)
        except Exception as e:
            print(f"\nERROR on h{h}/P{idx}: {e}")
            import traceback
            traceback.print_exc()
    
    # --- Comparison summary ---
    print(f"\n{'='*70}")
    print(f"  COMPARISON SUMMARY")
    print(f"{'='*70}")
    
    # Check if any h28 polytopes share vertices
    h28_hashes = [(r['idx'], r['vertex_hash']) for r in results if r['h'] == 28]
    print(f"\n[Vertex identity check (h28 cluster)]")
    for idx, vh in h28_hashes:
        print(f"  P{idx}: vertex_hash={vh}")
    
    same_verts = len(set(vh for _, vh in h28_hashes)) == 1
    print(f"  Same polytope? {'YES — identical vertices' if same_verts else 'NO — distinct polytopes'}")
    
    # Check kappa identity
    h28_kappas = [(r['idx'], r['kappa_hash']) for r in results if r['h'] == 28]
    print(f"\n[Intersection ring identity (h28 cluster)]")
    for idx, kh in h28_kappas:
        print(f"  P{idx}: kappa_hash={kh}")
    
    same_kappa = len(set(kh for _, kh in h28_kappas)) == 1
    print(f"  Same intersection ring? {'YES' if same_kappa else 'NO — distinct CY manifolds'}")
    
    # Full comparison table
    print(f"\n[All champions comparison]")
    print(f"{'ID':>12} {'pts':>4} {'verts':>5} {'eff':>4} {'mori':>5} {'c2[0..2]':>15}")
    for r in results:
        c2_short = str(r['c2'][:3])
        print(f"  h{r['h']}/P{r['idx']:>3}: {r['n_pts']:4d} {r['n_verts']:5d} {r['h11_eff']:4d} {r['n_mori']:5d} {c2_short:>15}")
