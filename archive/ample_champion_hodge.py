import numpy as np
import cytools
import sympy as sp
from itertools import combinations

def main():
    print("--- Ample Champion Hodge Number & Transversality Test ---")
    # Polytope 40 from the Kreuzer-Skarke list (h11=2, h21=29, chi=-54)
    # It is P2 x P2
    verts = np.array([
        [ 1,  0,  0,  0],
        [ 0,  1,  0,  0],
        [-1, -1,  0,  0],
        [ 0,  0,  1,  0],
        [ 0,  0,  0,  1],
        [ 0,  0, -1, -1]
    ])
    poly = cytools.Polytope(verts)
    
    # Get the dual polytope points (monomials)
    dual_pts = poly.dual().points()
    print(f"Number of monomials (dual points): {len(dual_pts)}")
    
    # The symmetry generators
    # g1: (0 4 5) -> wait, in the previous script we used specific permutations.
    # Let's read the previous script to get the exact permutations.
