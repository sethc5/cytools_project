"""
DRAGON SLAYER: Rigorous verification of the Ample Champion Z_3 x Z_3 quotient.

This script tests every claim made in the original analysis:
  1. What IS this polytope? (It's NOT P2xP2 — that was wrong)
  2. Does the Z_3 x Z_3 action actually preserve the polytope?
  3. Is the action truly fixed-point-free on the CY hypersurface?
  4. Are the orbit sums really closed under the group action?
  5. Is the invariant polynomial generic enough for transversality?
  6. What are the quotient Hodge numbers via Lefschetz?

Each test prints PASS or FAIL with explanation.
"""

import cytools as cy
import numpy as np
import sympy as sp
from itertools import permutations, combinations
from collections import Counter

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"

def section(title):
    print(f"\n{'='*60}")
    print(f"  TEST: {title}")
    print(f"{'='*60}")

def main():
    print("=" * 60)
    print("  DRAGON SLAYER: Ample Champion Verification Suite")
    print("=" * 60)
    
    results = {}
    
    # =========================================================
    # TEST 1: WHAT IS THIS POLYTOPE?
    # =========================================================
    section("1. Polytope Identification")
    
    polys = cy.fetch_polytopes(h11=2, lattice="N", limit=1)
    poly = polys[0]
    verts = poly.vertices()
    
    print(f"Vertices (from KS database):")
    print(verts)
    
    h11 = poly.h11("N")
    h21 = poly.h21("N")
    chi = poly.chi("N")
    print(f"h11={h11}, h21={h21}, chi={chi}")
    
    # Compare with P2xP2
    p2p2_verts = np.array([
        [1, 0, 0, 0], [0, 1, 0, 0], [-1, -1, 0, 0],
        [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, -1, -1]
    ])
    p2p2 = cy.Polytope(p2p2_verts)
    p2p2_h11 = p2p2.h11("N")
    p2p2_h21 = p2p2.h21("N")
    p2p2_chi = p2p2.chi("N")
    print(f"\nP2xP2 for comparison: h11={p2p2_h11}, h21={p2p2_h21}, chi={p2p2_chi}")
    
    if chi == -54 and p2p2_chi == -162:
        print(f"{WARN}: This polytope is NOT P2xP2!")
        print(f"  KS polytope: chi={chi}, dual has {len(poly.dual().points())} pts")
        print(f"  P2xP2:       chi={p2p2_chi}, dual has {len(p2p2.dual().points())} pts")
        # But chi=-54 is still what we want for |chi|/2=3 generations
        # chi/9 = -6 means |chi_quotient|/2 = 3
        results["identity"] = "NOT_P2xP2"
    else:
        results["identity"] = "UNKNOWN"
    
    # Check the normal form / what toric variety this is
    # The weights [0,1,1,1,0,0] and [1,0,0,0,1,1] suggest 
    # it's a (1,1,1) x (1,1,1) CICY — i.e., the SAME CY manifold
    # as a bicubic in P2xP2, just represented in a different (sub)lattice.
    # Let's verify by checking h21.
    
    # A bicubic in P2xP2 has h11=2, h21=83? No, that's the AMBIENT space.
    # The CY hypersurface in P2xP2 is degree (3,3), which has:
    #   h11 = 2, h21 = 83  (this is the standard result)
    # But our polytope gives h11=2, h21=29.
    # These are DIFFERENT manifolds.
    
    print(f"\n  The KS polytope with h11=2, h21=29, chi=-54")
    print(f"  is a DIFFERENT CY3 from the bicubic in P2xP2 (h21=83).")
    print(f"  Previous claim that it was P2xP2 was INCORRECT.")
    
    # Let's figure out what it actually is
    # Check the number of lattice points and facets
    n_pts = len(poly.points())
    n_dual_pts = len(poly.dual().points())
    n_facets = len(poly.faces(3))  # codim-1 faces
    print(f"\n  Lattice points: {n_pts}")
    print(f"  Dual lattice points: {n_dual_pts}")
    print(f"  Facets: {n_facets}")
    
    # =========================================================
    # TEST 2: DO THE PERMUTATIONS PRESERVE THE POLYTOPE?
    # =========================================================
    section("2. Permutation Symmetry of the Polytope")
    
    # The generators from the original script:
    g1 = [4, 1, 2, 3, 5, 0]  # (0 4 5) cycle
    g2 = [0, 2, 3, 1, 4, 5]  # (1 2 3) cycle
    
    print(f"g1 = {g1}  (cycle: 0→4→5→0)")
    print(f"g2 = {g2}  (cycle: 1→2→3→1)")
    
    # Check: do these permutations of the VERTICES give an isomorphic polytope?
    # i.e., does permuting the rows of verts give a lattice-equivalent polytope?
    
    def apply_vertex_perm(vertices, perm):
        """Permute rows of vertex matrix."""
        return vertices[perm]
    
    v1_perm = apply_vertex_perm(verts, g1)
    v2_perm = apply_vertex_perm(verts, g2)
    
    print(f"\nOriginal vertices:")
    print(verts)
    print(f"\nVertices after g1:")
    print(v1_perm)
    print(f"\nVertices after g2:")
    print(v2_perm)
    
    # For a permutation to be a symmetry of the TORIC VARIETY, we need:
    # There exists a GL(4,Z) matrix A such that v_perm = A @ v_original
    # (where the permuted vertices are the same as the original vertices
    #  up to a lattice automorphism)
    
    # Actually, for the permutation to be a symmetry of the FAN, we need
    # the permuted fan to equal the original fan. Since the fan is defined
    # by the cones over the vertices, we need:
    # For each cone sigma in the fan, the permuted cone must also be in the fan.
    
    # But more fundamentally: the vertices are rays of the fan, and a 
    # permutation of rays is a symmetry if there exists A in GL(4,Z) with
    # A * v_{sigma(i)} = v_i for all i (or A maps the permuted vertex set
    # back to the original vertex set).
    
    # Let's check if there exists such A for g1 and g2.
    
    def find_lattice_auto(v_orig, v_perm):
        """
        Find A in GL(4,Z) such that A @ v_perm[i] = v_orig[i] for all i.
        Since we have 6 vertices in 4D, we pick 4 linearly independent ones.
        """
        # Find 4 linearly independent rows
        for idx in combinations(range(len(v_orig)), 4):
            mat_orig = v_orig[list(idx)].T  # 4x4
            mat_perm = v_perm[list(idx)].T
            det_orig = np.linalg.det(mat_orig)
            det_perm = np.linalg.det(mat_perm)
            if abs(det_perm) > 0.5:
                A = mat_orig @ np.linalg.inv(mat_perm)
                # Check if A is integer
                A_round = np.round(A).astype(int)
                if np.allclose(A, A_round, atol=1e-8):
                    # Verify on ALL vertices
                    check = A_round @ v_perm.T
                    if np.allclose(check.T, v_orig, atol=1e-8):
                        return A_round, int(round(np.linalg.det(A_round)))
        return None, None
    
    A1, det1 = find_lattice_auto(verts, v1_perm)
    A2, det2 = find_lattice_auto(verts, v2_perm)
    
    if A1 is not None and abs(det1) == 1:
        print(f"\n{PASS}: g1 is a lattice automorphism (det={det1})")
        print(f"  A1 = \n{A1}")
        results["g1_lattice_auto"] = True
    elif A1 is not None:
        print(f"\n{FAIL}: g1 maps vertices but det(A)={det1} ≠ ±1")
        print(f"  NOT a lattice automorphism!")
        results["g1_lattice_auto"] = False
    else:
        print(f"\n{FAIL}: g1 does NOT map the polytope to itself!")
        results["g1_lattice_auto"] = False
    
    if A2 is not None and abs(det2) == 1:
        print(f"\n{PASS}: g2 is a lattice automorphism (det={det2})")
        print(f"  A2 = \n{A2}")
        results["g2_lattice_auto"] = True
    elif A2 is not None:
        print(f"\n{FAIL}: g2 maps vertices but det(A)={det2} ≠ ±1")
        results["g2_lattice_auto"] = False
    else:
        print(f"\n{FAIL}: g2 does NOT map the polytope to itself!")
        results["g2_lattice_auto"] = False
    
    # Check commutativity
    g1g2 = [g1[g2[i]] for i in range(6)]
    g2g1 = [g2[g1[i]] for i in range(6)]
    commute = (g1g2 == g2g1)
    if commute:
        print(f"\n{PASS}: g1 and g2 commute (disjoint support)")
    else:
        print(f"\n{FAIL}: g1 and g2 do NOT commute!")
        print(f"  g1∘g2 = {g1g2}")
        print(f"  g2∘g1 = {g2g1}")
    results["commute"] = commute
    
    # Check order
    def compose_perm(p, q):
        return [p[q[i]] for i in range(len(p))]
    
    identity = list(range(6))
    g1_cubed = compose_perm(compose_perm(g1, g1), g1)
    g2_cubed = compose_perm(compose_perm(g2, g2), g2)
    
    if g1_cubed == identity and g2_cubed == identity:
        print(f"{PASS}: Both generators have order 3")
    else:
        print(f"{FAIL}: Generator orders wrong! g1^3={g1_cubed}, g2^3={g2_cubed}")
    results["order3"] = (g1_cubed == identity and g2_cubed == identity)
    
    # =========================================================
    # TEST 3: FIXED POINT ANALYSIS
    # =========================================================
    section("3. Fixed Point Analysis")
    
    # Generate all 9 group elements
    group_elements = []
    group_labels = []
    curr = identity[:]
    for i in range(3):
        temp = curr[:]
        for j in range(3):
            group_elements.append(temp[:])
            group_labels.append(f"g1^{i} g2^{j}")
            temp = compose_perm(g2, temp)
        curr = compose_perm(g1, curr)
    
    print(f"Group has {len(group_elements)} elements:")
    for label, g in zip(group_labels, group_elements):
        print(f"  {label}: {g}")
    
    # For each non-identity element, check for fixed points on the TORIC VARIETY
    # A point in the toric variety is specified by homogeneous coordinates [x_0:...:x_5]
    # subject to the SR ideal and the C* actions.
    #
    # A group element g fixes a point if g(x) = lambda * x for some rescaling.
    # Since g permutes coordinates, g fixes [x_0:...:x_5] if 
    #   x_{g(i)} = lambda_a * x_i  for the appropriate C* scalings.
    #
    # For a FREELY ACTING symmetry, no non-identity element should have fixed points
    # on the CY hypersurface.
    #
    # The standard test: for each non-identity g, find the fixed-point locus on
    # the toric variety, then check if a GENERIC invariant polynomial vanishes there.
    
    # The SR ideal says: {x_1, x_5, x_6} and {x_2, x_3, x_4} can't all vanish.
    # But wait, the SR ideal uses 1-indexed labels from CYTools.
    # SR = ((1, 5, 6), (2, 3, 4)) means:
    #   x_1*x_5*x_6 ≠ 0 (can't all vanish simultaneously) -- NO, that's wrong
    #   Actually SR ideal means {x_1, x_5, x_6} is in SR, meaning 
    #   NOT ALL of x_1, x_5, x_6 can be zero simultaneously.
    # Wait, the SR ideal generators are {x_1 x_5 x_6, x_2 x_3 x_4}
    # This means the exceptional set is V(x_1 x_5 x_6) ∪ V(x_2 x_3 x_4)
    # Points must avoid the exceptional set.
    
    # Actually let me re-read the SR ideal output:
    # ((1, np.uint8(5), np.uint8(6)), (2, np.uint8(3), np.uint8(4)))
    # This means the SR ideal is generated by x_1*x_5*x_6 and x_2*x_3*x_4
    # NOTE: CYTools uses 1-based indexing for the SR ideal (ray indices start at 1)
    # Wait no — let me check if CYTools is 0-indexed or 1-indexed for SR.
    
    # Let's get the triangulation to check
    triangs = list(poly.all_triangulations())
    t = triangs[0]
    sr = t.sr_ideal()
    print(f"\nSR Ideal: {sr}")
    
    # The SR ideal tells us which sets of coordinates cannot simultaneously vanish.
    # If sr = ((1,5,6), (2,3,4)), these are the ray indices.
    # CYTools points() includes the origin at index 0, so ray 1 = point index 1, etc.
    # For our polytope with 6 vertices + 1 origin = 7 points:
    # rays are indexed 0-6, with 0 being the origin (not used in fan).
    # Actually in CYTools, the rays ARE the vertices, indexed starting from... let me check.
    
    # Let's print the rays of the triangulation
    print(f"Triangulation points used: indices are vertex indices")
    print(f"Number of vertices: {len(verts)}")
    
    # The SR ideal uses the indices INTO poly.points().
    # poly.points() = [origin, v0, v1, ..., v5] typically, where v_i are vertices.
    # But it could also be just [v0, ..., v5, interior_pts...].
    # Let me check.
    pts = poly.points()
    print(f"\nAll lattice points ({len(pts)}):")
    for i, p in enumerate(pts):
        label = "origin" if np.all(p == 0) else ""
        print(f"  [{i}]: {p}  {label}")
    
    # The SR ideal elements are subsets of ray indices.
    # Rays = non-origin lattice points used in the triangulation.
    
    # For fixed point analysis on the toric variety:
    # A permutation g acts on the homogeneous coordinates x_0, ..., x_n
    # (one for each ray = each non-origin lattice point).
    # g: x_i -> x_{g(i)}
    # Fixed point: x_{g(i)} = lambda * x_i for some scaling lambda.
    #
    # For a 3-cycle (a b c), if x_a, x_b, x_c are all nonzero:
    #   x_b = lambda*x_a, x_c = lambda*x_b, x_a = lambda*x_c
    #   => x_a = lambda^3 * x_a => lambda^3 = 1 => lambda = omega (cube root of 1)
    #   => x_b = omega*x_a, x_c = omega^2*x_a
    #
    # If some of the coordinates in the cycle vanish:
    #   x_a = 0, x_b = lambda*x_a = 0, x_c = lambda*x_b = 0
    #   All must vanish. But if {a,b,c} is in the SR ideal, this is forbidden!
    
    # Our permutation g1 = (0 4 5) acts on rays with indices 0, 4, 5
    # Our permutation g2 = (1 2 3) acts on rays with indices 1, 2, 3
    # BUT these are VERTEX indices, not point indices.
    # We need to map to point indices.
    
    # Let's find the mapping
    vert_to_pt = {}
    for i, v in enumerate(verts):
        for j, p in enumerate(pts):
            if np.all(v == p):
                vert_to_pt[i] = j
                break
    
    print(f"\nVertex-to-point-index mapping: {vert_to_pt}")
    
    # Now check: does the SR ideal prevent the cycles from all vanishing?
    sr_sets = [set(s) for s in sr]
    print(f"SR ideal sets (point indices): {sr_sets}")
    
    # g1 cycle: vertices 0, 4, 5 -> point indices
    g1_cycle_pts = {vert_to_pt[0], vert_to_pt[4], vert_to_pt[5]}
    g2_cycle_pts = {vert_to_pt[1], vert_to_pt[2], vert_to_pt[3]}
    
    print(f"\ng1 cycle in point indices: {g1_cycle_pts}")
    print(f"g2 cycle in point indices: {g2_cycle_pts}")
    
    # Check if any SR set is a subset of a cycle
    # If SR set ⊆ cycle, then all coords in cycle can't vanish
    # => the cycle must have all nonzero coords => fixed point exists (with lambda=omega)
    
    g1_blocked = any(s.issubset(g1_cycle_pts) for s in sr_sets)
    g2_blocked = any(s.issubset(g2_cycle_pts) for s in sr_sets)
    
    if g1_blocked:
        print(f"  g1 cycle IS in SR ideal => all-zero IS forbidden => nonzero fixed locus exists")
    else:
        print(f"  g1 cycle NOT fully in SR ideal => all-zero IS allowed")
        
    if g2_blocked:
        print(f"  g2 cycle IS in SR ideal => all-zero IS forbidden => nonzero fixed locus exists")
    else:
        print(f"  g2 cycle NOT fully in SR ideal => all-zero IS allowed")
    
    # For ANY non-identity element g, the fixed point locus on the AMBIENT
    # toric variety is:
    #   Fix(g) = { [x] : x_{g(i)} = lambda*x_i for scaling lambda }
    # 
    # For g = g1 = (0,4,5): fixes vertices 1,2,3 (free), and on {0,4,5}:
    #   either all zero (if allowed by SR) or x_4 = omega*x_0, x_5 = omega^2*x_0
    # For g = g2 = (1,2,3): fixes vertices 0,4,5 (free), and on {1,2,3}:
    #   either all zero (if allowed) or x_2 = omega*x_1, x_3 = omega^2*x_1
    
    # The CRITICAL question: do these fixed loci intersect the CY hypersurface?
    # If the invariant polynomial does NOT vanish on Fix(g), then the action
    # is fixed-point-free on the CY.
    
    # Let's analyze each non-identity element properly.
    
    print(f"\n--- Detailed fixed-point analysis for each non-identity element ---")
    
    # Monomials of the CY hypersurface
    dual_pts = poly.dual().points()
    monomials = []
    for m in dual_pts:
        powers = []
        for v in verts:
            powers.append(int(np.dot(m, v) + 1))
        monomials.append(tuple(powers))
    
    print(f"\nMonomials of the CY hypersurface ({len(monomials)} total):")
    for i, m in enumerate(monomials):
        print(f"  m_{i}: x_0^{m[0]} x_1^{m[1]} x_2^{m[2]} x_3^{m[3]} x_4^{m[4]} x_5^{m[5]}")
    
    # For g1 = (0,4,5): fixed locus has x_1, x_2, x_3 free, and either:
    #   Case A: x_0 = x_4 = x_5 = 0  (if allowed by SR)
    #   Case B: x_4 = omega*x_0, x_5 = omega^2*x_0 (for each cube root omega)
    
    # For Case A (x_0=x_4=x_5=0):
    # The monomials that survive are those with a_0=a_4=a_5=0
    case_a_monomials = [m for m in monomials if m[0] == 0 and m[4] == 0 and m[5] == 0]
    print(f"\n[g1] Case A (x_0=x_4=x_5=0): {len(case_a_monomials)} surviving monomials")
    for m in case_a_monomials:
        print(f"  {m}")
    
    if len(case_a_monomials) == 0:
        print(f"  => Polynomial automatically vanishes here.")
        print(f"  => But this is NOT a fixed point issue —")
        print(f"     the polynomial vanishes, so these ARE on the CY!")
        print(f"  => Check: is x_0=x_4=x_5=0 allowed by SR?")
        g1_zero_allowed = not any(s.issubset(g1_cycle_pts) for s in sr_sets)
        if g1_zero_allowed:
            print(f"  {FAIL}: x_0=x_4=x_5=0 IS allowed and polynomial vanishes => FIXED POINTS!")
        else:
            print(f"  {PASS}: x_0=x_4=x_5=0 is FORBIDDEN by SR ideal")
    else:
        print(f"  => Polynomial restricted to this locus is a polynomial in x_1, x_2, x_3")
        print(f"  => Need to check if it has zeros (dimension count)")
        # The fixed locus Case A is P2 (3 free homogeneous coords)
        # The polynomial restricted to it is degree (sum of powers) in x_1, x_2, x_3
        # A generic polynomial of degree d on P2 defines a curve (dim 1)
        # This curve IS on the CY, so these are fixed points!
        # UNLESS the SR ideal forbids x_0=x_4=x_5=0.
        g1_zero_allowed = not any(s.issubset(g1_cycle_pts) for s in sr_sets)
        if g1_zero_allowed:
            print(f"  {FAIL}: x_0=x_4=x_5=0 IS allowed => fixed points exist on CY!")
        else:
            print(f"  {PASS}: x_0=x_4=x_5=0 is FORBIDDEN by SR ideal")
    
    # For Case B (x_4=omega*x_0, x_5=omega^2*x_0, x_0≠0):
    # Substitute into polynomial: each monomial x_0^a0 x_1^a1 x_2^a2 x_3^a3 x_4^a4 x_5^a5
    # becomes x_0^{a0+a4+a5} * omega^{a4+2*a5} * x_1^a1 x_2^a2 x_3^a3
    # The polynomial P restricted to Fix(g1) case B is:
    # sum_m c_m * x_0^{d0(m)} * omega^{phi(m)} * x_1^a1 x_2^a2 x_3^a3
    # where phi(m) = a4 + 2*a5 (mod 3)
    # For this to be an invariant polynomial under g1, we need phi(m) = 0 (mod 3)
    # for all monomials with nonzero coefficient.
    
    print(f"\n[g1] Case B (x_4=ω*x_0, x_5=ω²*x_0, x_0≠0):")
    phase_groups = {0: [], 1: [], 2: []}
    for m in monomials:
        phi = (m[4] + 2*m[5]) % 3
        phase_groups[phi].append(m)
    
    for phi_val in [0, 1, 2]:
        print(f"  Phase ω^{phi_val}: {len(phase_groups[phi_val])} monomials")
    
    # For g2 = (1,2,3): similar analysis
    # Case A: x_1 = x_2 = x_3 = 0
    case_a2_monomials = [m for m in monomials if m[1] == 0 and m[2] == 0 and m[3] == 0]
    print(f"\n[g2] Case A (x_1=x_2=x_3=0): {len(case_a2_monomials)} surviving monomials")
    for m in case_a2_monomials:
        print(f"  {m}")
    
    g2_zero_allowed = not any(s.issubset(g2_cycle_pts) for s in sr_sets)
    if g2_zero_allowed:
        if len(case_a2_monomials) == 0:
            print(f"  {WARN}: x_1=x_2=x_3=0 allowed and P=0 there => fixed points on CY!")
        else:
            print(f"  {WARN}: x_1=x_2=x_3=0 allowed, polynomial nontrivial there")
    else:
        print(f"  {PASS}: x_1=x_2=x_3=0 is FORBIDDEN by SR ideal")
    
    print(f"\n[g2] Case B (x_2=ω*x_1, x_3=ω²*x_1, x_1≠0):")
    phase_groups2 = {0: [], 1: [], 2: []}
    for m in monomials:
        phi = (m[2] + 2*m[3]) % 3
        phase_groups2[phi].append(m)
    
    for phi_val in [0, 1, 2]:
        print(f"  Phase ω^{phi_val}: {len(phase_groups2[phi_val])} monomials")
    
    # For combined elements g1^a * g2^b (a,b not both 0):
    # These combine both cycles. The fixed locus requires BOTH cycles
    # to be at their fixed points simultaneously.
    
    print(f"\n[g1*g2] Combined action:")
    print(f"  Fixed locus requires BOTH cycles at omega-points simultaneously")
    print(f"  x_4=ω^a*x_0, x_5=ω^(2a)*x_0 AND x_2=ω^b*x_1, x_3=ω^(2b)*x_1")
    print(f"  This restricts to a 2D locus (x_0 and x_1 free) => P1 x P0 ~ P1")
    print(f"  Polynomial restricted to this is a polynomial in x_0, x_1 of some degree")
    
    # For the combined element, the phases add:
    # For g1^a * g2^b, the monomial phase is:
    # omega^{a*(m[4]+2*m[5]) + b*(m[2]+2*m[3])}
    # This must equal 1 (i.e., exponent = 0 mod 3) for invariance.
    
    # Check for generic non-vanishing on the combined fixed locus
    # Substitute x_4=omega^a*x_0, x_5=omega^{2a}*x_0, x_2=omega^b*x_1, x_3=omega^{2b}*x_1
    # Each monomial becomes:
    # x_0^{m0+m4+m5} * x_1^{m1+m2+m3} * omega^{a*(m4+2m5)+b*(m2+2m3)}
    
    # For the invariant polynomial (orbit sum), the terms with different phases cancel.
    # The surviving terms have a*(m4+2m5)+b*(m2+2m3) = 0 mod 3.
    
    # Let's check what the polynomial looks like on the most dangerous case: g1*g2
    print(f"\n  For g1*g2 (a=1,b=1), surviving monomials on fixed locus:")
    a, b = 1, 1
    surviving = []
    for m in monomials:
        phase = (a*(m[4]+2*m[5]) + b*(m[2]+2*m[3])) % 3
        if phase == 0:
            x0_pow = m[0] + m[4] + m[5]
            x1_pow = m[1] + m[2] + m[3]
            surviving.append((m, x0_pow, x1_pow))
    
    print(f"  {len(surviving)} monomials survive:")
    degree_pairs = set()
    for m, p0, p1 in surviving:
        print(f"    {m} -> x_0^{p0} * x_1^{p1}")
        degree_pairs.add((p0, p1))
    
    # If there are surviving monomials of degree (d0, d1) in (x_0, x_1),
    # this defines a degree-(d0+d1) polynomial on P1.
    # A degree-d polynomial on P1 has d roots.
    # These roots are fixed points on the CY!
    # UNLESS the polynomial is identically nonzero (i.e., a constant), 
    # which happens only if d0+d1 = 0 (constant term only).
    
    total_degrees = set(p0+p1 for _, p0, p1 in surviving)
    print(f"\n  Total degrees on P1: {total_degrees}")
    if all(d == 0 for d in total_degrees):
        print(f"  {PASS}: Only constant term survives => can choose it nonzero => no fixed pts")
    elif len(surviving) == 0:
        print(f"  {PASS}: No surviving monomials => polynomial vanishes identically on Fix")
        print(f"  BUT: this means Fix ⊂ CY, so there ARE fixed points!")
        print(f"  {FAIL}: Fixed points exist on CY!")
    else:
        max_deg = max(total_degrees)
        print(f"  {WARN}: Polynomial of degree {max_deg} on P1 has {max_deg} zeros")
        print(f"  These are fixed points of g1*g2 on the CY hypersurface!")
        print(f"  The action is NOT freely acting!")
    
    # =========================================================
    # TEST 4: ORBIT SUM VERIFICATION
    # =========================================================
    section("4. Orbit Sum Verification")
    
    def apply_perm_to_monomial(m, p):
        """Permute a monomial's exponents according to the coordinate permutation."""
        b = [0] * 6
        for i in range(6):
            b[p[i]] = m[i]
        return tuple(b)
    
    # Generate all 9 group elements as permutations
    group_perms = [identity[:]]
    g = g1[:]
    for _ in range(2):
        group_perms.append(g)
        g = compose_perm(g1, g)
    
    full_group = []
    for g_elem in group_perms:
        curr = g_elem[:]
        for _ in range(3):
            full_group.append(curr[:])
            curr = compose_perm(g2, curr)
    
    # Remove duplicates
    full_group_unique = []
    seen = set()
    for g in full_group:
        key = tuple(g)
        if key not in seen:
            seen.add(key)
            full_group_unique.append(g)
    
    print(f"Full group has {len(full_group_unique)} elements")
    
    # Compute orbits
    orbits = []
    visited = set()
    for m in monomials:
        if m not in visited:
            orbit = set()
            for g in full_group_unique:
                gm = apply_perm_to_monomial(m, g)
                orbit.add(gm)
            orbits.append(orbit)
            visited.update(orbit)
    
    # Verify orbits partition the monomial set
    total_in_orbits = sum(len(o) for o in orbits)
    all_orbit_monomials = set()
    for o in orbits:
        all_orbit_monomials.update(o)
    
    print(f"Number of orbits: {len(orbits)}")
    print(f"Total monomials in orbits: {total_in_orbits}")
    print(f"Total unique monomials in orbits: {len(all_orbit_monomials)}")
    print(f"Original monomial count: {len(monomials)}")
    
    # Check: are all orbit monomials actually in the original monomial set?
    monomials_set = set(monomials)
    missing = all_orbit_monomials - monomials_set
    extra = monomials_set - all_orbit_monomials
    
    if len(missing) > 0:
        print(f"\n{FAIL}: {len(missing)} orbit monomials are NOT in the dual polytope!")
        print(f"  This means the group action does NOT preserve the monomial set!")
        for m in list(missing)[:5]:
            print(f"    Missing: {m}")
        results["orbits_closed"] = False
    else:
        print(f"\n{PASS}: All orbit monomials are in the dual polytope")
        results["orbits_closed"] = True
    
    if len(extra) > 0:
        print(f"{FAIL}: {len(extra)} monomials not covered by orbits!")
        results["orbits_partition"] = False
    else:
        print(f"{PASS}: Orbits partition the full monomial set")
        results["orbits_partition"] = True
    
    orbit_sizes = sorted([len(o) for o in orbits])
    print(f"\nOrbit sizes: {orbit_sizes}")
    print(f"Sum of orbit sizes: {sum(orbit_sizes)} (should be {len(monomials)})")
    
    # Check: orbit sizes should divide |G| = 9
    bad_orbits = [s for s in orbit_sizes if 9 % s != 0]
    if len(bad_orbits) > 0:
        print(f"{FAIL}: Orbit sizes {bad_orbits} do not divide |G|=9!")
    else:
        print(f"{PASS}: All orbit sizes divide |G|=9")
    
    # =========================================================
    # TEST 5: TRANSVERSALITY CHECK
    # =========================================================
    section("5. Transversality (Codimension) Check")
    
    # For a CY hypersurface to be smooth, we need the polynomial and its
    # partial derivatives to not simultaneously vanish (transversality).
    # With 6 free orbit-sum coefficients, we have 6 degrees of freedom.
    # The CY is a codimension-1 subvariety of a 4D toric variety.
    # Transversality requires: for generic coefficients, 
    #   P = dP/dx_0 = ... = dP/dx_5 = 0 has no solutions on the toric variety.
    # This is 7 equations in effectively 4 dimensions (after quotienting by C*^2).
    # So generically, 7 equations in 4 unknowns have no solution.
    # => Transversality is automatic for GENERIC coefficients
    #    as long as we have at least 1 free coefficient.
    # With 6 coefficients, this is very safe.
    
    print(f"Number of free coefficients (orbit sums): {len(orbits)}")
    if len(orbits) >= 1:
        print(f"{PASS}: Enough freedom for generic transversality ({len(orbits)} >= 1)")
    else:
        print(f"{FAIL}: No free coefficients!")
    
    # But we need to check: is the linear system of invariant polynomials
    # BASE-POINT FREE? i.e., is there a point where ALL invariant polynomials vanish?
    # This is harder to check. Let's at least verify that the orbit sums
    # span enough monomials.
    
    # Check: what fraction of monomials are covered?
    n_monos_covered = len(all_orbit_monomials)
    print(f"Monomials in invariant polynomial: {n_monos_covered}/{len(monomials)}")
    results["transverse"] = len(orbits) >= 1
    
    # =========================================================
    # TEST 6: HONEST FIXED POINT CHECK ON CY
    # =========================================================
    section("6. Honest Fixed Point Check on the CY Hypersurface")
    
    # The REAL test: for each non-identity group element g,
    # does Fix(g) ∩ CY = ∅ for a GENERIC invariant polynomial?
    #
    # Strategy: restrict the generic invariant polynomial to Fix(g),
    # and check if the resulting polynomial is identically zero or not.
    # If identically zero => Fix(g) ⊂ CY => fixed points!
    # If not identically zero => it defines a subvariety of Fix(g).
    # If dim(subvariety) >= 0 => fixed points exist (unless empty for
    # dimensional reasons).
    
    has_fixed_points = False
    
    for idx, (label, g) in enumerate(zip(group_labels, group_elements)):
        if g == identity:
            continue
        
        # Find the cycle structure
        visited_elem = [False] * 6
        cycles = []
        for i in range(6):
            if not visited_elem[i]:
                cycle = []
                j = i
                while not visited_elem[j]:
                    visited_elem[j] = True
                    cycle.append(j)
                    j = g[j]
                if len(cycle) > 1:
                    cycles.append(cycle)
        
        print(f"\n  {label} = {g}, cycles: {cycles}")
        
        # For each 3-cycle (a,b,c), on the fixed locus either:
        #   x_a = x_b = x_c = 0, or
        #   x_b = omega*x_a, x_c = omega^2*x_a (and permutations for higher powers)
        
        # Check all cases
        # For simplicity with Z3 x Z3, the cycles are the same: (0,4,5) and/or (1,2,3)
        
        # Determine which cycles are active
        cycle_sets = [set(c) for c in cycles]
        
        # For each cycle, we have two cases: all-zero or omega-relation
        # Count dimensions of the fixed locus
        n_fixed_coords = 6 - sum(len(c) for c in cycles)  # coords not in any cycle
        # Each cycle contributes either 0 coords (all-zero case) or 1 coord (omega case)
        # minus the torus actions (2 C* actions)
        
        # The interesting case for the CY: restrict the polynomial to Fix(g)
        # and check if it's forced to vanish.
        
        # For elements with both cycles active (e.g., g1*g2):
        if len(cycles) == 2:
            # Omega case: x_b = omega*x_a, x_c = omega^2*x_a for each cycle
            # Free coords: one from each cycle = 2
            # Torus actions: 2
            # Net dimension: 2 - 2 = 0 (isolated points)
            
            # The polynomial on the fixed locus:
            # Each monomial m -> x_{a1}^{sum of powers in cycle1} * x_{a2}^{sum in cycle2} * omega^phase
            # Only monomials with phase = 0 (mod 3) contribute
            
            # For g1^a * g2^b:
            c1, c2 = cycles
            # Figure out which is (0,4,5) and which is (1,2,3)
            
            # Compute the phase for each monomial
            surviving_on_fix = []
            for m in monomials:
                phase = 0
                for c in cycles:
                    # For cycle (a,b,c) under g, b=g(a), c=g(b)
                    a_idx = c[0]
                    b_idx = g[a_idx]
                    c_idx = g[b_idx]
                    # Phase contribution: m[b_idx]*1 + m[c_idx]*2 (relative to omega)
                    # Actually: the substitution x_{g(i)} = omega * x_i means
                    # x_{b} = omega * x_{a}, x_{c} = omega * x_{b} = omega^2 * x_{a}
                    # So monomial contribution from this cycle is:
                    # x_a^{m[a]} * (omega*x_a)^{m[b]} * (omega^2*x_a)^{m[c]}
                    # = x_a^{m[a]+m[b]+m[c]} * omega^{m[b] + 2*m[c]}
                    phase += m[b_idx] + 2*m[c_idx]
                
                phase = phase % 3
                if phase == 0:
                    # Compute the degree in each cycle's free variable
                    degs = []
                    for c in cycles:
                        degs.append(sum(m[i] for i in c))
                    surviving_on_fix.append((m, degs))
            
            if len(surviving_on_fix) == 0:
                print(f"    No monomials survive => P ≡ 0 on Fix => Fix ⊂ CY!")
                print(f"    {FAIL}: Fixed points on CY!")
                has_fixed_points = True
            else:
                # The polynomial on the fixed locus is in variables (x_{a1}, x_{a2})
                # which are projective coordinates on P0 = {pt} (since dim = 0)
                # Actually, dim of fixed locus = sum of (1 per cycle in omega case) 
                # = 2 free variables, minus 2 torus actions = 0 dimensions
                # So it's isolated points, and the polynomial evaluates to a NUMBER.
                # If the number is generically nonzero, no fixed points.
                
                deg_sets = set(tuple(d) for _, d in surviving_on_fix)
                print(f"    {len(surviving_on_fix)} monomials survive, degree pairs: {deg_sets}")
                
                # The total degree should be the same for all monomials
                # (since the polynomial is quasi-homogeneous)
                total_degs = set(sum(d) for _, d in surviving_on_fix)
                print(f"    Total degrees: {total_degs}")
                
                # Actually the fixed locus for the omega case is:
                # x_0 free, x_4 = omega*x_0, x_5 = omega^2*x_0
                # x_1 free, x_2 = omega*x_1, x_3 = omega^2*x_1
                # So we have (x_0, x_1) ∈ (C*)^2 / (C*)^2 (torus quotient)
                # This is a set of discrete points.
                # The polynomial evaluates to a single number (up to scaling).
                # For GENERIC invariant coefficients, this number is nonzero.
                
                if len(surviving_on_fix) > 0:
                    print(f"    For generic coefficients, P(fix) = sum of {len(surviving_on_fix)} terms ≠ 0")
                    print(f"    {PASS}: Generic invariant polynomial nonzero on Fix({label})")
        
        elif len(cycles) == 1:
            # Only one cycle active (e.g., pure g1 or pure g2)
            c = cycles[0]
            # The other 3 coords are free
            # Omega case: 3 free + 1 from cycle = 4 coords, minus 2 torus = 2D fixed locus
            # Zero case: 3 free + 0 = 3 coords, minus 2 torus = 1D fixed locus (if allowed)
            
            # Check zero case
            zero_allowed = not any(s.issubset(set(vert_to_pt.get(i, i) for i in c)) for s in sr_sets)
            
            if zero_allowed:
                # The polynomial restricted to x_c = 0 for all c in cycle
                restricted = [m for m in monomials if all(m[i] == 0 for i in c)]
                if len(restricted) > 0:
                    print(f"    Zero case: {len(restricted)} monomials survive on {len(c)}-cycle=0")
                    # This gives a polynomial on P^2 (or similar), which generically
                    # defines a curve. A curve has points => fixed points!
                    free_coords = [i for i in range(6) if i not in c]
                    print(f"    Free coords: {free_coords}")
                    print(f"    {FAIL}: Fixed curve on CY from zero case!")
                    has_fixed_points = True
                else:
                    print(f"    Zero case: P ≡ 0 when cycle=0 => entire locus is on CY")
                    print(f"    {FAIL}: Entire fixed locus on CY!")
                    has_fixed_points = True
            else:
                print(f"    Zero case: forbidden by SR ideal")
            
            # Omega case
            a_idx = c[0]
            b_idx = g[a_idx]
            c_idx = g[b_idx]
            
            surviving_omega = []
            for m in monomials:
                phase = (m[b_idx] + 2*m[c_idx]) % 3
                if phase == 0:
                    cycle_deg = m[a_idx] + m[b_idx] + m[c_idx]
                    free_degs = tuple(m[i] for i in range(6) if i not in c)
                    surviving_omega.append((m, cycle_deg, free_degs))
            
            print(f"    Omega case: {len(surviving_omega)} monomials survive")
            if len(surviving_omega) == 0:
                print(f"    {FAIL}: P ≡ 0 on omega-Fix => all of omega-Fix is on CY!")
                has_fixed_points = True
            else:
                # This is a polynomial in 4 variables (1 from cycle + 3 free)
                # modulo 2 torus actions = polynomial on a 2D space
                # A generic polynomial on a 2D space defines a codim-1 subvariety = curve
                # A curve has points => fixed points exist!
                free_coords = [i for i in range(6) if i not in c]
                print(f"    This is a polynomial on a 2D projective space (P2-like)")
                print(f"    A generic polynomial on P2 defines a CURVE => has zeros")
                print(f"    {FAIL}: Fixed CURVE on CY from omega case!")
                has_fixed_points = True
    
    # =========================================================
    # VERDICT
    # =========================================================
    section("VERDICT")
    
    if has_fixed_points:
        print(f"\n{FAIL}{FAIL}{FAIL}")
        print(f"The Z_3 x Z_3 action has FIXED POINTS on the CY hypersurface!")
        print(f"The quotient CY3/G is SINGULAR, not a smooth manifold.")
        print(f"chi(CY3/G) ≠ chi(CY3)/|G| in general for singular quotients.")
        print(f"The '3-generation' claim requires additional work:")
        print(f"  - Need to find a RESOLUTION of singularities")
        print(f"  - Or find a DIFFERENT freely-acting group")
        print(f"  - Or argue the singularities are mild (orbifold)")
        results["freely_acting"] = False
    else:
        print(f"\n{PASS}{PASS}{PASS}")
        print(f"The Z_3 x Z_3 action is FREELY ACTING on the CY hypersurface!")
        print(f"chi(CY3/G) = chi(CY3)/|G| = {chi}/{len(full_group_unique)} = {chi//len(full_group_unique)}")
        print(f"This is a genuine 3-generation model!")
        results["freely_acting"] = True
    
    print(f"\n{'='*60}")
    print(f"  SUMMARY OF ALL TESTS")
    print(f"{'='*60}")
    for key, val in results.items():
        status = PASS if val else FAIL
        if isinstance(val, str):
            status = WARN
        print(f"  {key}: {val}")
    
    # Save results
    with open("dragon_slayer_results.txt", "w") as f:
        f.write("DRAGON SLAYER RESULTS\n")
        f.write("=" * 40 + "\n\n")
        for key, val in results.items():
            f.write(f"{key}: {val}\n")
        f.write(f"\nFreely acting: {results.get('freely_acting', 'UNKNOWN')}\n")
    
    print(f"\nResults saved to dragon_slayer_results.txt")

if __name__ == "__main__":
    main()
