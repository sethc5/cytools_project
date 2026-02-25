#!/usr/bin/env python3
"""Get GLSM charge matrix and compute sigma action on Picard lattice."""
import numpy as np
from cy_compute import fetch_polytopes_cached

polys = fetch_polytopes_cached(16, 19, limit=50000)
p = polys[329]
pts = np.array(p.points(), dtype=int)
tri = p.triangulate()
cy = tri.get_cy()

div_basis = list(cy.divisor_basis())
print("Basis (toric indices):", div_basis)

# Manual linear relations from toric geometry:
# For each m in M = Z^4: sum_{rho} <m, v_rho> D_rho ~ 0
# v_rho = pts[rho] for rho = 1..18 (skip origin at 0)
rays = pts[1:]  # (18, 4)
n_rays = rays.shape[0]

# Relation matrix L: L[i][rho] = v_rho[i], for i=0..3, rho=0..17
# sum_rho L[i][rho] D_{rho+1} ~ 0 for each i
L = rays.T  # (4, 18)
print("\nLinear relation matrix L (4 x 18):")
print(L)

# Non-basis toric divisor indices
basis_set = set(int(b) for b in div_basis)
nonbasis_toric = sorted(set(range(1, 19)) - basis_set)
print("\nNon-basis toric indices:", nonbasis_toric)

# Convert to ray indices (0-based within rays)
basis_ray = [int(b) - 1 for b in div_basis]
nonbasis_ray = [t - 1 for t in nonbasis_toric]
print("Non-basis ray indices:", nonbasis_ray)

# Express non-basis divisors in terms of basis:
# From L @ D ~ 0 (where D is the 18-vector of toric divisor coefficients):
# L_B @ D_B + L_N @ D_N = 0
# D_N = -(L_N)^{-1} L_B @ D_B  (when L_N is square and invertible)

L_B = L[:, basis_ray]  # (4, 14)
L_N = L[:, nonbasis_ray]  # (4, 4)

print("\nL_N (4x4 for non-basis):")
print(L_N)
print("det(L_N) =", np.linalg.det(L_N))

if abs(np.linalg.det(L_N)) > 0.5:
    # D_N = -inv(L_N) @ L_B @ D_B
    inv_L_N = np.linalg.inv(L_N).astype(float)
    M_NB = -inv_L_N @ L_B  # (4, 14): D_nonbasis = M_NB @ D_basis
    print("\nM_NB (non-basis = M_NB @ basis):")
    print(np.round(M_NB, 4))

    # Check integrality
    M_NB_int = np.round(M_NB).astype(int)
    print("\nM_NB (integer):")
    print(M_NB_int)

    # For each non-basis divisor, give the expression
    for k, nb_toric in enumerate(nonbasis_toric):
        coeffs = M_NB_int[k]
        terms = []
        for a, c in enumerate(coeffs):
            if c != 0:
                terms.append("(%+d)*D_%d" % (c, div_basis[a]))
        print("  D_%d ~ %s" % (nb_toric, " + ".join(terms) if terms else "0"))

    # Now compute sigma action on basis
    # sigma permutes rays: ray_perm[j] = k means sigma(v_j) = v_k
    auts = p.automorphisms()
    sigma = None
    for g in auts:
        if not np.allclose(g, np.eye(g.shape[0])):
            sigma = g.astype(int)
            break

    new_pts = (sigma @ pts.T).T
    ray_perm = np.full(pts.shape[0], -1, dtype=int)
    for j in range(pts.shape[0]):
        for k in range(pts.shape[0]):
            if np.allclose(new_pts[j], pts[k]):
                ray_perm[j] = k
                break

    # Build sigma action matrix on Pic(X) in basis coordinates
    # For each basis divisor e_a (toric b_a):
    #   sigma(D_{b_a}) = D_{ray_perm[b_a]}
    #   If ray_perm[b_a] is a basis toric index: trivial
    #   If ray_perm[b_a] is a non-basis toric index: use M_NB to express in basis

    basis_inv = {int(b): i for i, b in enumerate(div_basis)}
    nonbasis_inv = {t: i for i, t in enumerate(nonbasis_toric)}

    sigma_matrix = np.zeros((len(div_basis), len(div_basis)), dtype=int)
    for a, b in enumerate(div_basis):
        target = ray_perm[int(b)]
        if int(target) in basis_inv:
            j = basis_inv[int(target)]
            sigma_matrix[a, j] = 1  # row a, column j: sigma(e_a) = e_j
        elif int(target) in nonbasis_inv:
            k = nonbasis_inv[int(target)]
            # sigma(e_a) = D_{target} = sum_a' M_NB[k][a'] * e_{a'}
            sigma_matrix[a, :] = M_NB_int[k, :]
        else:
            print("ERROR: target %d not in basis or non-basis!" % target)

    print("\nSigma action matrix on Pic(X) (14x14):")
    print("  sigma(e_a) = sum_b S[a,b] e_b")
    print(sigma_matrix)

    # Verify: sigma^2 = identity
    s2 = sigma_matrix @ sigma_matrix
    print("\nSigma^2 =", "Identity" if np.allclose(s2, np.eye(len(div_basis))) else "NOT Identity!")
    if not np.allclose(s2, np.eye(len(div_basis))):
        print(s2)

    # Eigenvalues
    eigvals = np.linalg.eigvalsh(sigma_matrix.astype(float))
    print("\nEigenvalues of sigma:", np.sort(np.round(eigvals, 2)))
    n_plus = np.sum(np.round(eigvals) == 1)
    n_minus = np.sum(np.round(eigvals) == -1)
    print("dim(+1 eigenspace) = %d, dim(-1 eigenspace) = %d" % (n_plus, n_minus))

else:
    print("L_N is singular, need different approach")
