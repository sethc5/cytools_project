import cytools as cy
import numpy as np

polys = cy.fetch_polytopes(h11=2, lattice="N", limit=1)
poly1 = polys[0]
v1 = poly1.vertices()

v2 = np.array([
    [ 1,  0,  0,  0],
    [ 0,  1,  0,  0],
    [-1, -1,  0,  0],
    [ 0,  0,  1,  0],
    [ 0,  0,  0,  1],
    [ 0,  0, -1, -1]
])

# Let's check if v1 and v2 are isomorphic as polytopes
poly2 = cy.Polytope(v2)
print("Are they isomorphic?", poly1.is_isomorphic(poly2))

# Let's check the points of poly1
print("Points of poly1:")
print(poly1.points())

# Let's check the points of poly2
print("Points of poly2:")
print(poly2.points())
