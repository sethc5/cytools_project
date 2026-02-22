import cytools as cy
import numpy as np
import itertools

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

for indices in itertools.combinations(range(6), 4):
    mat1 = v1[list(indices)]
    mat2 = v2[list(indices)]
    det1 = np.linalg.det(mat1)
    det2 = np.linalg.det(mat2)
    if det1 != 0 or det2 != 0:
        print(f"Indices {indices}: det1={det1}, det2={det2}")
