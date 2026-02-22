import cytools as cy
import numpy as np

polys = cy.fetch_polytopes(h11=2, lattice="N", limit=1)
poly1 = polys[0]

verts2 = np.array([
    [ 1,  0,  0,  0],
    [ 0,  1,  0,  0],
    [-1, -1,  0,  0],
    [ 0,  0,  1,  0],
    [ 0,  0,  0,  1],
    [ 0,  0, -1, -1]
])
poly2 = cy.Polytope(verts2)

print(f"poly1 points: {len(poly1.points())}")
print(f"poly2 points: {len(poly2.points())}")
print(f"poly1 dual points: {len(poly1.dual().points())}")
print(f"poly2 dual points: {len(poly2.dual().points())}")
