import cytools as cy
polys = cy.fetch_polytopes(h11=2, lattice="N", limit=1)
poly = polys[0]
print(f"h11={poly.h11('N')}, h21={poly.h21('N')}, chi={poly.chi('N')}")
