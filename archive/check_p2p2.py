import cytools as cy
import numpy as np
verts2 = np.array([
    [ 1,  0,  0,  0],
    [ 0,  1,  0,  0],
    [-1, -1,  0,  0],
    [ 0,  0,  1,  0],
    [ 0,  0,  0,  1],
    [ 0,  0, -1, -1]
])
poly2 = cy.Polytope(verts2)
print(f"P2xP2: h11={poly2.h11('N')}, h21={poly2.h21('N')}, chi={poly2.chi('N')}")
