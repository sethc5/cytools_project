import cytools as cy
import numpy as np

def analyze_fibration():
    print("Analyzing Fibration Structure of Polytope 40 (h11=20, h21=20)")
    
    # Fetch the polytope
    polys = cy.fetch_polytopes(h11=20, h21=20, lattice="N", limit=1)
    if not polys:
        print("Polytope not found!")
        return
        
    p = polys[0]
    print(f"Polytope: {p}")
    print(f"h11: {p.h11(lattice='N')}, h21: {p.h21(lattice='N')}, chi: {p.chi(lattice='N')}")
    
    # Check for fibrations
    print("\nChecking for fibrations...")
    
    verts = p.vertices()
    print("\nVertices:")
    print(verts)
    
    pts = p.points()
    print(f"\nNumber of points: {len(pts)}")
    
    dual_p = p.dual()
    dual_pts = dual_p.points()
    print(f"Number of dual points: {len(dual_pts)}")
    
    print("\nLooking for K3 fibrations (1D reflexive subpolytopes in M)...")
    k3_fibrations = []
    for pt in dual_pts:
        if np.all(pt == 0):
            continue
        neg_pt = -pt
        dual_pts_tuples = [tuple(x) for x in dual_pts]
        if tuple(neg_pt) in dual_pts_tuples:
            gcd = np.gcd.reduce(np.abs(pt))
            if gcd == 1:
                for val in pt:
                    if val != 0:
                        if val > 0:
                            k3_fibrations.append(pt)
                        break
                        
    print(f"Found {len(k3_fibrations)} K3 fibration structures!")
    for f in k3_fibrations:
        print(f"Base P^1 direction in M: {f}")
        
    print("\nLooking for elliptic fibrations (2D reflexive subpolytopes in M)...")
    # We can check if any pairs of K3 fibrations generate a 2D reflexive subpolytope.
    # A 2D reflexive subpolytope in M corresponds to an elliptic fibration.
    # Let's check all pairs of K3 fibrations.
    
    elliptic_fibrations = []
    for i in range(len(k3_fibrations)):
        for j in range(i+1, len(k3_fibrations)):
            v1 = k3_fibrations[i]
            v2 = k3_fibrations[j]
            
            # The 2D subspace is spanned by v1 and v2.
            # Let's find all points in dual_pts that lie in this subspace.
            # A point p is in the subspace if p = a*v1 + b*v2 for some real a, b.
            # Since v1, v2 are linearly independent, we can solve for a, b.
            
            subspace_pts = []
            for pt in dual_pts:
                # Check if pt is in the span of v1, v2
                # We can do this by checking if the rank of [v1, v2, pt] is 2.
                mat = np.vstack([v1, v2, pt])
                if np.linalg.matrix_rank(mat) == 2:
                    subspace_pts.append(pt)
                    
            # Now we need to check if subspace_pts forms a 2D reflexive polytope.
            # A 2D reflexive polytope has exactly one interior point (the origin).
            # Let's just count the number of points.
            # The 16 reflexive polygons have between 4 and 10 points.
            if 4 <= len(subspace_pts) <= 10:
                # It's very likely a reflexive polygon!
                elliptic_fibrations.append((v1, v2, len(subspace_pts)))
                
    print(f"Found {len(elliptic_fibrations)} candidate elliptic fibration structures!")
    for f in elliptic_fibrations:
        print(f"Base P^2 (or F_n) directions in M: {f[0]} and {f[1]} (Polygon points: {f[2]})")
        
    # Write the results to a file
    with open("fibration_results.txt", "w") as f:
        f.write("Fibration Analysis of Polytope 40 (20/20)\n")
        f.write("=========================================\n\n")
        f.write(f"h11: {p.h11(lattice='N')}, h21: {p.h21(lattice='N')}, chi: {p.chi(lattice='N')}\n\n")
        f.write(f"Found {len(k3_fibrations)} K3 fibration structures!\n")
        for k3 in k3_fibrations:
            f.write(f"Base P^1 direction in M: {k3}\n")
        f.write(f"\nFound {len(elliptic_fibrations)} candidate elliptic fibration structures!\n")
        for ef in elliptic_fibrations:
            f.write(f"Base directions in M: {ef[0]} and {ef[1]} (Polygon points: {ef[2]})\n")

if __name__ == '__main__':
    analyze_fibration()
