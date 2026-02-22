import cytools as cy
import numpy as np

verts = np.array([
    [ 1,  0,  0,  0],
    [ 0,  1,  0,  0],
    [-1, -1,  0,  0],
    [ 0,  0,  1,  0],
    [ 0,  0,  0,  1],
    [ 0,  0, -1, -1]
])
poly = cy.Polytope(verts)
dual = poly.dual()
print(f"Number of points in dual polytope: {len(dual.points())}")
