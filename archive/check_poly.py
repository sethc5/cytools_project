import cytools as cy
polys = cy.fetch_polytopes(h11=2, lattice="N", limit=1)
poly = polys[0]
print(poly.vertices())
print(f"h11={poly.h11()}, h21={poly.h21()}, chi={poly.chi()}")
