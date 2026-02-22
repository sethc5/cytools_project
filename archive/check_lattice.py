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

# Let's find the linear relations
M1 = np.vstack((v1, np.ones(6)))
M2 = np.vstack((v2, np.ones(6)))

print("Rank of v1:", np.linalg.matrix_rank(v1))
print("Rank of v2:", np.linalg.matrix_rank(v2))

# Let's check the volume of the simplices
import itertools
for indices in itertools.combinations(range(6), 4):
    mat1 = v1[list(indices)]
    mat2 = v2[list(indices)]
    det1 = np.linalg.det(mat1)
    det2 = np.linalg.det(mat2)
    if det1 != 0 or det2 != 0:
        print(f"Indices {indices}: det1={det1}, det2={det2}")
        break
