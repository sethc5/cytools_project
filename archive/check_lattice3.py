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

# Find the transformation matrix from v2 to v1
# v1 = v2 * A
# A = v2^-1 * v1
# We need to pick 4 linearly independent rows
idx = [0, 1, 3, 4]
mat2 = v2[idx]
mat1 = v1[idx]
A = np.linalg.inv(mat2) @ mat1
print("Transformation matrix A:")
print(A)
print("Determinant of A:", np.linalg.det(A))

# Check if v2 @ A == v1
print("v2 @ A:")
print(v2 @ A)
print("v1:")
print(v1)
