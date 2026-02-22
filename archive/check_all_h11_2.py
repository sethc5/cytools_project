import cytools as cy
polys = cy.fetch_polytopes(h11=2, lattice="N")
for i, p in enumerate(polys):
    if p.h21("N") == 29:
        print(f"Polytope {i}: h11={p.h11('N')}, h21={p.h21('N')}, chi={p.chi('N')}, dual_pts={len(p.dual().points())}")
