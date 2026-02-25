#!/usr/bin/env python3
"""
rank_n_bundles.py — Stage 5: Higher-rank vector bundle construction & analysis.

Builds rank-n vector bundles on CY 3-folds from constituent line bundles,
computes their Chern characters, chiral indices, and checks stability.

Two construction methods:
  (B) Direct sum:  V = L₁ ⊕ L₂ ⊕ ... ⊕ Lₙ   (abelian gauge group)
  (A) Monad:       0 → V → B → C → 0          (non-abelian gauge group)
      where B = ⊕ O(bᵢ), C = ⊕ O(cⱼ), rk(V) = rk(B) - rk(C)

Key formulas (CY 3-fold, c₁(X) = 0, Td(X) = 1 + c₂(X)/12):

  For a line bundle L = O(D):
    ch(L) = (1,  D,  D²/2,  D³/6)       [rk, ch₁, ch₂, ch₃]
    χ(L)  = D³/6 + c₂·D/12

  For a direct sum V = ⊕ᵢ Lᵢ:
    ch(V) = Σᵢ ch(Lᵢ)
    χ(V)  = Σᵢ χ(Lᵢ)

  For a monad 0 → V → B → C → 0:
    ch(V) = ch(B) - ch(C)
    χ(V)  = χ(B) - χ(C)

  Index theorem on CY3:
    χ(V) = ∫ ch(V)·Td(X) = ch₃(V) + rk(V)·c₂(X)/12  [wait, not quite]

  More precisely:
    χ(V) = ∫_X [ch₀·Td₃ + ch₁·Td₂ + ch₂·Td₁ + ch₃·Td₀]
    Td₀ = 1, Td₁ = c₁(X)/2 = 0, Td₂ = (c₁²+c₂)/12 = c₂(X)/12, Td₃ = c₁c₂/24 = 0
    So: χ(V) = ch₃(V) + ch₁(V)·c₂(X)/12

  For 3 families:  χ(V) = ±3

  Stability (necessary condition for HYM):
    μ(V) = c₁(V)·J²/rk(V) where J is Kähler form
    V is μ-stable iff for every proper coherent subsheaf F ⊂ V with 0 < rk(F) < rk(V):
      μ(F) < μ(V)

  For SU(n) structure group: c₁(V) = 0, so μ(V) = 0
    Stability ⟺ no subsheaf with μ(F) ≥ 0

Reference: MATH_SPEC.md, FRAMEWORK.md §5, Braun-He-Ovrut-Pantev (2006)
"""

import numpy as np
from itertools import combinations, product
from cy_compute import (
    compute_chi, compute_chi_batch, build_intnum_tensor,
    basis_to_toric, count_lattice_points, compute_h0_koszul,
    extract_cy_data, fetch_polytopes_cached
)


# ══════════════════════════════════════════════════════════════════
#  Chern character computation
# ══════════════════════════════════════════════════════════════════

def chern_character_line_bundle(D_basis, intnums, h11_eff):
    """Compute Chern character of a line bundle L = O(D).

    ch(L) = (1, D, D²/2, D³/6) where:
      ch₀ = rk = 1
      ch₁ = c₁ = D             (h11-dim vector)
      ch₂ = c₁²/2 = D²/2      (scalar: ∫ D·D·J summed? No — ch₂ is a 2-form class)

    Actually for the index theorem we only need the integrated versions:
      ∫ ch₃ = D³/6
      ∫ ch₁·Td₂ = ∫ D·c₂(X)/12 = c₂·D/12

    So we return the components needed for χ computation:
      ch = (rk, c₁_vec, D²_scalar, D³_scalar)

    But for building monad bundles, we need the full Chern character as
    differential form classes. On a CY3 with basis {e_a}, the cohomology
    ring is:
      H⁰ ≅ R (rank)
      H² ≅ R^h11 (divisor classes)  
      H⁴ ≅ R^h11 (curve classes, dual to H²)
      H⁶ ≅ R (point class)

    For practical computation we need:
      ch₃ = D³/6  (a number, integrated over X)
      ch₁·c₂ = c₂·D  (a number)

    Returns dict with:
      'rk': int
      'c1': ndarray (h11,) — first Chern class in basis coords
      'D3': float — D³ = κ_{ijk} D_i D_j D_k
      'c2D': float — c₂·D
      'chi': float — χ(L) = D³/6 + c₂·D/12
    """
    D = np.asarray(D_basis, dtype=np.float64)
    D3 = 0.0
    for (i, j, k), val in intnums.items():
        D3 += D[i] * D[j] * D[k] * val

    return {
        'rk': 1,
        'c1': D.copy(),
        'D3': D3,
    }


def chern_data_line_bundle(D_basis, intnums, c2, h11_eff):
    """Full Chern data for a line bundle, including χ.

    Returns dict with rk, c1, D3, c2D, chi.
    """
    D = np.asarray(D_basis, dtype=np.float64)
    D3 = 0.0
    for (i, j, k), val in intnums.items():
        D3 += D[i] * D[j] * D[k] * val
    c2D = np.dot(D[:h11_eff], c2[:h11_eff])
    chi = D3 / 6.0 + c2D / 12.0

    return {
        'rk': 1,
        'c1': D.copy(),
        'D3': D3,
        'c2D': c2D,
        'chi': chi,
    }


# ══════════════════════════════════════════════════════════════════
#  Direct sum bundles  V = L₁ ⊕ L₂ ⊕ ... ⊕ Lₙ
# ══════════════════════════════════════════════════════════════════

def direct_sum_chi(line_bundle_divisors, intnums, c2, h11_eff):
    """Compute χ(V) for a direct sum V = ⊕ᵢ O(Dᵢ).

    By additivity: χ(V) = Σᵢ χ(O(Dᵢ)).

    Args:
        line_bundle_divisors: list of (h11,) arrays, one per summand
        intnums: basis-indexed intersection numbers dict
        c2: basis-indexed second Chern class array
        h11_eff: effective h11

    Returns:
        float: χ(V) = Σ χ(Lᵢ)
    """
    total_chi = 0.0
    for D in line_bundle_divisors:
        total_chi += compute_chi(D, intnums, c2, h11_eff)
    return total_chi


def direct_sum_chern_data(line_bundle_divisors, intnums, c2, h11_eff):
    """Full Chern data for a direct sum bundle.

    For V = L₁ ⊕ ... ⊕ Lₙ:
      rk(V) = n
      c₁(V) = Σ c₁(Lᵢ) = Σ Dᵢ
      ch(V) = Σ ch(Lᵢ)
      χ(V) = Σ χ(Lᵢ)

    Also computes:
      c₂(V) = Σ_{i<j} Dᵢ·Dⱼ  (as an element of H⁴, but we store ∫c₂·J data)
      c₃(V) = Σ_{i<j<k} Dᵢ·Dⱼ·Dₖ  (number)

    Returns dict.
    """
    n = len(line_bundle_divisors)
    divisors = [np.asarray(D, dtype=np.float64) for D in line_bundle_divisors]

    # c₁(V) = Σ Dᵢ
    c1_V = sum(divisors)

    # χ(V) = Σ χ(Lᵢ)
    total_chi = 0.0
    per_bundle_chi = []
    for D in divisors:
        chi_i = compute_chi(D, intnums, c2, h11_eff)
        per_bundle_chi.append(chi_i)
        total_chi += chi_i

    # c₁(V)³
    c1_cubed = 0.0
    for (i, j, k), val in intnums.items():
        c1_cubed += c1_V[i] * c1_V[j] * c1_V[k] * val

    # c₂·c₁(V)
    c2_c1V = np.dot(c1_V[:h11_eff], c2[:h11_eff])

    # c₃(V) = Σ_{i<j<k} Dᵢ·Dⱼ·Dₖ (triple intersection)
    c3_V = 0.0
    if n >= 3:
        for a, b, c in combinations(range(n), 3):
            Da, Db, Dc = divisors[a], divisors[b], divisors[c]
            # Dₐ·D_b·D_c = Σ κ_{ijk} Da_i Db_j Dc_k
            trip = 0.0
            for (i, j, k), val in intnums.items():
                # Need full symmetrization since κ is stored with i≤j≤k
                trip += _symmetrized_triple(Da, Db, Dc, i, j, k, val)
            c3_V += trip

    return {
        'rk': n,
        'c1': c1_V,
        'c1_cubed': c1_cubed,
        'c2_c1V': c2_c1V,
        'c3': c3_V,
        'chi': total_chi,
        'per_bundle_chi': per_bundle_chi,
        'divisors': [D.copy() for D in divisors],
        'is_SU': np.allclose(c1_V, 0),   # SU(n) iff c₁ = 0
    }


def _symmetrized_triple(Da, Db, Dc, i, j, k, val):
    """Compute Da_? · Db_? · Dc_? · κ_{ijk} with proper symmetrization.

    The intersection tensor κ is stored with i≤j≤k, each entry appearing once.
    For three DIFFERENT divisors Da, Db, Dc, we need:
      Σ_{all perms} Da_{perm(i)} Db_{perm(j)} Dc_{perm(k)} · κ_{ijk}

    But since κ_{ijk} is already the symmetrized value (CYTools stores it
    as the coefficient of the monomial D_i·D_j·D_k in the cubic form),
    and our compute_chi uses it as-is with D_i*D_j*D_k, we need to be
    careful about the multiplicity.

    For i=j=k: κ appears once, monomial is D_i³. For Da·Db·Dc:
      contribution = Da_i·Db_i·Dc_i · val  (only 1 assignment)

    For i=j<k: κ appears once, monomial is D_i²·D_k. For Da·Db·Dc:
      need to sum over which of Da,Db,Dc gets which index.
      There are 3 ways to assign (i,i,k) to (a,b,c):
        Da_i·Db_i·Dc_k + Da_i·Db_k·Dc_i + Da_k·Db_i·Dc_i

    For i<j=k: similar, 3 permutations.

    For i<j<k: all distinct, 6 permutations:
      Da_i·Db_j·Dc_k + Da_i·Db_k·Dc_j + Da_j·Db_i·Dc_k + 
      Da_j·Db_k·Dc_i + Da_k·Db_i·Dc_j + Da_k·Db_j·Dc_i
    """
    if i == j == k:
        return Da[i] * Db[i] * Dc[i] * val
    elif i == j:  # i=j < k
        return (Da[i]*Db[i]*Dc[k] + Da[i]*Db[k]*Dc[i] + Da[k]*Db[i]*Dc[i]) * val
    elif j == k:  # i < j=k
        return (Da[i]*Db[j]*Dc[j] + Da[j]*Db[i]*Dc[j] + Da[j]*Db[j]*Dc[i]) * val
    else:  # i < j < k
        return (Da[i]*Db[j]*Dc[k] + Da[i]*Db[k]*Dc[j] +
                Da[j]*Db[i]*Dc[k] + Da[j]*Db[k]*Dc[i] +
                Da[k]*Db[i]*Dc[j] + Da[k]*Db[j]*Dc[i]) * val


# ══════════════════════════════════════════════════════════════════
#  Monad bundles:  0 → V → B → C → 0
# ══════════════════════════════════════════════════════════════════

def monad_chi(B_divisors, C_divisors, intnums, c2, h11_eff):
    """Compute χ(V) for a monad bundle 0 → V → B → C → 0.

    By the long exact sequence: χ(V) = χ(B) - χ(C).

    Args:
        B_divisors: list of (h11,) arrays for the B = ⊕ O(bᵢ) summands
        C_divisors: list of (h11,) arrays for the C = ⊕ O(cⱼ) summands
        intnums, c2, h11_eff: CY geometry data

    Returns:
        float: χ(V)
    """
    chi_B = sum(compute_chi(D, intnums, c2, h11_eff) for D in B_divisors)
    chi_C = sum(compute_chi(D, intnums, c2, h11_eff) for D in C_divisors)
    return chi_B - chi_C


def monad_chern_data(B_divisors, C_divisors, intnums, c2, h11_eff):
    """Full Chern data for a monad bundle 0 → V → B → C → 0.

    ch(V) = ch(B) - ch(C), so:
      rk(V) = rk(B) - rk(C)
      c₁(V) = c₁(B) - c₁(C) = Σbᵢ - Σcⱼ
      χ(V) = χ(B) - χ(C) = Σχ(O(bᵢ)) - Σχ(O(cⱼ))

    For SU(n) structure group: need c₁(V) = 0, i.e. Σbᵢ = Σcⱼ.

    Returns dict with monad-specific data.
    """
    B_data = direct_sum_chern_data(B_divisors, intnums, c2, h11_eff)
    C_data = direct_sum_chern_data(C_divisors, intnums, c2, h11_eff)

    rk_V = B_data['rk'] - C_data['rk']
    c1_V = B_data['c1'] - C_data['c1']
    chi_V = B_data['chi'] - C_data['chi']

    return {
        'rk': rk_V,
        'c1': c1_V,
        'chi': chi_V,
        'chi_B': B_data['chi'],
        'chi_C': C_data['chi'],
        'B_divisors': [D.copy() for D in B_divisors],
        'C_divisors': [D.copy() for D in C_divisors],
        'rk_B': B_data['rk'],
        'rk_C': C_data['rk'],
        'is_SU': np.allclose(c1_V, 0),
        'per_bundle_chi_B': B_data['per_bundle_chi'],
        'per_bundle_chi_C': C_data['per_bundle_chi'],
    }


# ══════════════════════════════════════════════════════════════════
#  Monad scanner — find rank-n monads with χ(V) = ±3
# ══════════════════════════════════════════════════════════════════

def scan_direct_sum_bundles(intnums, c2, h11_eff, target_chi=3,
                            rank=4, max_coeff=3, max_nonzero=3,
                            require_SU=True, cap=1000):
    """Find direct sum bundles V = ⊕ Lᵢ with |χ(V)| = target_chi.

    For SU(n) structure group, require c₁(V) = Σ Dᵢ = 0.

    Strategy: build rank-n bundles from line bundles with small coefficients.
    Since χ(⊕Lᵢ) = Σχ(Lᵢ), we first find all line bundles with χ in a
    useful range, then search for rank-n subsets that sum to ±target_chi
    (and c₁ = 0 if SU(n) required).

    Args:
        intnums, c2, h11_eff: CY geometry data
        target_chi: target |χ(V)| (default 3 for 3 generations)
        rank: rank of the bundle (4 for SU(4), 5 for SU(5))
        max_coeff: max absolute coefficient in divisor basis
        max_nonzero: max nonzero entries per line bundle divisor
        require_SU: if True, require c₁(V) = 0
        cap: max number of results

    Returns:
        list of dicts with bundle data
    """
    T = build_intnum_tensor(intnums, h11_eff)
    c2_arr = np.asarray(c2, dtype=np.float64)

    # Step 1: enumerate all line bundles with |coeffs| ≤ max_coeff
    #         and compute their χ values
    coeff_range = list(range(-max_coeff, max_coeff + 1))
    indices = list(range(h11_eff))

    line_bundles = []  # list of (D_basis, chi) tuples

    for n_nz in range(1, min(max_nonzero + 1, h11_eff + 1)):
        for chosen in combinations(indices, n_nz):
            all_coeffs = list(product(coeff_range, repeat=n_nz))
            N = len(all_coeffs)

            D_batch = np.zeros((N, h11_eff), dtype=np.float64)
            for row, coeffs in enumerate(all_coeffs):
                for idx, c in zip(chosen, coeffs):
                    D_batch[row, idx] = c

            # Remove zero rows
            nonzero_mask = np.any(D_batch != 0, axis=1)
            D_batch = D_batch[nonzero_mask]
            if len(D_batch) == 0:
                continue

            chi_vals = compute_chi_batch(D_batch, T, c2_arr, h11_eff)

            for row_idx in range(len(D_batch)):
                chi_val = chi_vals[row_idx]
                if abs(chi_val) < 50:  # reasonable range for summands
                    line_bundles.append((D_batch[row_idx].astype(int).copy(),
                                       float(chi_val)))

    # Also include the trivial bundle O(0) with χ = 0
    # (needed as a summand for SU(n) with c₁=0 constraint)
    # Actually O(0) has χ = 0 which doesn't help, skip it.

    print(f"  Found {len(line_bundles)} candidate line bundles (|χ| < 50)")

    # Step 2: for each rank-n combination of line bundles, check:
    #   (a) Σ χ(Lᵢ) = ±target_chi
    #   (b) if require_SU: Σ Dᵢ = 0
    #
    # This is combinatorially expensive for large pools. Use a smarter approach:
    # For rank-4 SU(4): need 4 line bundles with Σχᵢ = ±3 and ΣDᵢ = 0.
    # Group by (chi, D) and use a partition approach.

    if require_SU:
        return _scan_SU_direct_sum(line_bundles, intnums, c2, h11_eff,
                                   target_chi, rank, cap)
    else:
        return _scan_any_direct_sum(line_bundles, intnums, c2, h11_eff,
                                    target_chi, rank, cap)


def _scan_any_direct_sum(line_bundles, intnums, c2, h11_eff,
                          target_chi, rank, cap):
    """Find rank-n direct sums with |χ| = target_chi (no SU constraint)."""
    results = []
    n_lb = len(line_bundles)

    # For small pools, try all combinations
    if n_lb > 500:
        print(f"  Pool too large ({n_lb}) for brute-force, sampling...")
        # Random sampling approach
        rng = np.random.default_rng(42)
        for _ in range(cap * 100):
            idxs = rng.choice(n_lb, size=rank, replace=True)
            divisors = [line_bundles[i][0] for i in idxs]
            chis = [line_bundles[i][1] for i in idxs]
            total = sum(chis)
            if abs(abs(total) - target_chi) < 0.01:
                data = direct_sum_chern_data(divisors, intnums, c2, h11_eff)
                results.append(data)
                if len(results) >= cap:
                    break
        return results

    # Exhaustive for small pools
    for combo in combinations(range(n_lb), rank):
        chis = [line_bundles[i][1] for i in combo]
        total = sum(chis)
        if abs(abs(total) - target_chi) < 0.01:
            divisors = [line_bundles[i][0] for i in combo]
            data = direct_sum_chern_data(divisors, intnums, c2, h11_eff)
            results.append(data)
            if len(results) >= cap:
                break

    return results


def _scan_SU_direct_sum(line_bundles, intnums, c2, h11_eff,
                         target_chi, rank, cap):
    """Find rank-n SU(n) direct sums: c₁=0 and |χ|=target_chi.

    Uses a meet-in-the-middle approach for rank-4:
      Split into pairs, compute (partial_c1, partial_chi) for each pair,
      then find complementary pairs.

    For rank-5 or higher, falls back to sampling.
    """
    results = []
    n_lb = len(line_bundles)

    if rank == 5 and n_lb <= 2000:
        # Meet-in-the-middle for rank 5: pairs (2) + triples (3)
        print(f"  Meet-in-the-middle search (rank {rank}, {n_lb} line bundles)...")

        # Build pair_index
        pair_index = {}
        for i in range(n_lb):
            for j in range(i, n_lb):
                Di, chi_i = line_bundles[i]
                Dj, chi_j = line_bundles[j]
                c1_pair = Di + Dj
                chi_pair = chi_i + chi_j
                store_key = (tuple(c1_pair.astype(int)), round(chi_pair, 4))
                if store_key not in pair_index:
                    pair_index[store_key] = []
                pair_index[store_key].append((i, j))

        # Use a smaller pool for triples to keep memory reasonable
        # Filter to single-nonzero line bundles for the triple half
        small_lb = [(D, chi) for D, chi in line_bundles
                    if np.count_nonzero(D) <= 1]
        if len(small_lb) < 10:
            small_lb = line_bundles[:min(100, n_lb)]
        n_small = len(small_lb)
        print(f"  Using {n_small} line bundles for triples...")

        triple_index = {}
        for i in range(n_small):
            for j in range(i, n_small):
                for k in range(j, n_small):
                    Di, chi_i = small_lb[i]
                    Dj, chi_j = small_lb[j]
                    Dk, chi_k = small_lb[k]
                    c1_trip = Di + Dj + Dk
                    chi_trip = chi_i + chi_j + chi_k
                    key = (tuple(c1_trip.astype(int)), round(chi_trip, 4))
                    if key not in triple_index:
                        triple_index[key] = []
                    triple_index[key].append((i, j, k))

        # Match: pair + triple must cancel (c₁=0, χ=±target)
        found = set()
        for (c1_p, chi_p), pairs in pair_index.items():
            for t in [target_chi, -target_chi]:
                c1_need = tuple(-x for x in c1_p)
                chi_need = round(t - chi_p, 4)
                triple_key = (c1_need, chi_need)
                if triple_key in triple_index:
                    for i, j in pairs:
                        for k, l, m in triple_index[triple_key]:
                            quint = tuple(sorted([
                                tuple(line_bundles[i][0]),
                                tuple(line_bundles[j][0]),
                                tuple(small_lb[k][0]),
                                tuple(small_lb[l][0]),
                                tuple(small_lb[m][0]),
                            ]))
                            if quint in found:
                                continue
                            found.add(quint)

                            divisors = [line_bundles[i][0], line_bundles[j][0],
                                       small_lb[k][0], small_lb[l][0], small_lb[m][0]]
                            data = direct_sum_chern_data(
                                divisors, intnums, c2, h11_eff)
                            if data['is_SU'] and abs(abs(data['chi']) - target_chi) < 0.01:
                                results.append(data)
                                if len(results) >= cap:
                                    return results
        return results

    elif rank == 4 and n_lb <= 2000:
        # Meet-in-the-middle: enumerate all pairs, index by (-c₁, target_chi - chi)
        print(f"  Meet-in-the-middle search (rank {rank}, {n_lb} line bundles)...")
        pair_index = {}  # key = (tuple(-c1_pair), target-chi_pair) → list of (i,j)

        for i in range(n_lb):
            for j in range(i, n_lb):
                Di, chi_i = line_bundles[i]
                Dj, chi_j = line_bundles[j]
                c1_pair = Di + Dj
                chi_pair = chi_i + chi_j

                # We need the OTHER pair to have c1 = -c1_pair and chi = target - chi_pair
                key_pos = (tuple(-c1_pair), target_chi - chi_pair)
                key_neg = (tuple(-c1_pair), -target_chi - chi_pair)

                # Store THIS pair for lookup by complementary pairs
                store_key = (tuple(c1_pair.astype(int)), round(chi_pair, 4))
                if store_key not in pair_index:
                    pair_index[store_key] = []
                pair_index[store_key].append((i, j))

        # Now find matching pairs
        found = set()
        for key, pairs in pair_index.items():
            c1_tup, chi_val = key
            # Need complement: c1 = -c1_tup, chi = ±target - chi_val
            for t in [target_chi, -target_chi]:
                comp_key = (tuple(-np.array(c1_tup)), round(t - chi_val, 4))
                if comp_key in pair_index:
                    for i, j in pairs:
                        for k, l in pair_index[comp_key]:
                            # Avoid double-counting: require sorted indices
                            quad = tuple(sorted([i, j, k, l]))
                            if quad in found:
                                continue
                            found.add(quad)

                            divisors = [line_bundles[q][0] for q in quad]
                            data = direct_sum_chern_data(
                                divisors, intnums, c2, h11_eff)
                            if data['is_SU'] and abs(abs(data['chi']) - target_chi) < 0.01:
                                results.append(data)
                                if len(results) >= cap:
                                    return results
        return results

    # Fallback: random sampling for large pools or high rank
    print(f"  Random sampling (rank {rank}, {n_lb} line bundles)...")
    rng = np.random.default_rng(42)
    attempts = 0
    max_attempts = cap * 10000

    while len(results) < cap and attempts < max_attempts:
        attempts += 1
        # Pick (rank-1) bundles, then try to solve for the last one
        idxs = rng.choice(n_lb, size=rank, replace=True)
        divisors = [line_bundles[i][0] for i in idxs]
        chis = [line_bundles[i][1] for i in idxs]

        c1_sum = sum(divisors)
        chi_sum = sum(chis)

        if np.allclose(c1_sum, 0) and abs(abs(chi_sum) - target_chi) < 0.01:
            data = direct_sum_chern_data(divisors, intnums, c2, h11_eff)
            results.append(data)

    return results


def _enumerate_line_bundles(intnums, c2, h11_eff, max_coeff, max_nonzero,
                             chi_bound=100, include_trivial=True):
    """Enumerate candidate line bundles with |χ| < chi_bound.

    Returns list of (D_basis_int, chi_float) tuples.
    """
    coeff_range = list(range(-max_coeff, max_coeff + 1))
    indices = list(range(h11_eff))
    line_bundles = []

    if include_trivial:
        D = np.zeros(h11_eff, dtype=np.float64)
        chi_val = compute_chi(D, intnums, c2, h11_eff)
        line_bundles.append((np.zeros(h11_eff, dtype=int), float(chi_val)))

    for n_nz in range(1, min(max_nonzero + 1, h11_eff + 1)):
        for chosen in combinations(indices, n_nz):
            all_coeffs = list(product(coeff_range, repeat=n_nz))
            for coeffs in all_coeffs:
                if all(c == 0 for c in coeffs):
                    continue
                D = np.zeros(h11_eff, dtype=np.float64)
                for idx, c in zip(chosen, coeffs):
                    D[idx] = c
                chi_val = compute_chi(D, intnums, c2, h11_eff)
                if abs(chi_val) < chi_bound:
                    line_bundles.append((D.astype(int).copy(), float(chi_val)))

    return line_bundles


def scan_monad_bundles(intnums, c2, h11_eff, target_chi=3,
                       rk_B=5, rk_C=1, max_coeff=3, max_nonzero=2,
                       require_SU=True, cap=500):
    """Find monad bundles 0 → V → B → C → 0 with |χ(V)| = target_chi.

    For rank-4 V:  rk_B=5, rk_C=1  (most common in literature)
                   rk_B=6, rk_C=2  (also viable)

    SU(n) constraint: c₁(V) = c₁(B) - c₁(C) = 0 ⟹ Σbᵢ = Σcⱼ.

    Strategy (pair + triple meet-in-the-middle for rk_B=5):
      1. Build a SMALL pool of line bundles (max_nonzero=1)
      2. Build pair_index and triple_index from this pool
      3. For each C, find B = pair + triple such that:
         c₁(pair) + c₁(triple) = c₁(C)
         χ(pair) + χ(triple) - χ(C) = ±target_chi

    Args:
        rk_B: rank of B (number of line bundle summands)
        rk_C: rank of C (usually 1 or 2)
        max_coeff, max_nonzero: search bounds for constituent line bundles

    Returns:
        list of dicts with monad data
    """
    # Use a small pool (max_nonzero=1) for the B decomposition search
    # to keep combinatorics tractable. Use the full pool for C choices.
    small_pool = _enumerate_line_bundles(
        intnums, c2, h11_eff, max_coeff=max_coeff,
        max_nonzero=1, include_trivial=True)
    full_pool = _enumerate_line_bundles(
        intnums, c2, h11_eff, max_coeff=max_coeff,
        max_nonzero=max_nonzero, include_trivial=True)

    print(f"  {len(small_pool)} small-pool, {len(full_pool)} full-pool line bundles")

    results = []
    found_keys = set()  # deduplicate

    if rk_C == 1 and rk_B == 5 and require_SU:
        results = _scan_monad_5_1_SU(
            small_pool, full_pool, intnums, c2, h11_eff,
            target_chi, cap)

    elif rk_C == 2 and rk_B == 6 and require_SU:
        results = _scan_monad_6_2_SU(
            small_pool, full_pool, intnums, c2, h11_eff,
            target_chi, cap)

    else:
        # Fallback: simple patterns
        results = _scan_monad_simple(
            full_pool, intnums, c2, h11_eff,
            target_chi, rk_B, rk_C, require_SU, cap)

    return results


def _scan_monad_5_1_SU(small_pool, full_pool, intnums, c2, h11_eff,
                        target_chi, cap):
    """Meet-in-the-middle for rk_B=5, rk_C=1, SU(4) monads.

    Decompose B = pair(2) + triple(3).
    For each C, for each pair, look up complementary triple.
    """
    print(f"  Building pair + triple indices (pool={len(small_pool)})...")
    n_sp = len(small_pool)

    # Build pair_index: key = (c1_tuple, round(chi,4)) → list of (i,j) pairs
    pair_index = {}
    for i in range(n_sp):
        for j in range(i, n_sp):
            Di, chi_i = small_pool[i]
            Dj, chi_j = small_pool[j]
            c1 = tuple(map(int, Di + Dj))
            chi = round(chi_i + chi_j, 4)
            key = (c1, chi)
            if key not in pair_index:
                pair_index[key] = []
            pair_index[key].append((i, j))

    # Build triple_index: key = (c1_tuple, round(chi,4)) → list of (i,j,k) triples
    triple_index = {}
    for i in range(n_sp):
        for j in range(i, n_sp):
            for k in range(j, n_sp):
                Di, chi_i = small_pool[i]
                Dj, chi_j = small_pool[j]
                Dk, chi_k = small_pool[k]
                c1 = tuple(map(int, Di + Dj + Dk))
                chi = round(chi_i + chi_j + chi_k, 4)
                key = (c1, chi)
                if key not in triple_index:
                    triple_index[key] = []
                triple_index[key].append((i, j, k))

    print(f"  Pair index: {len(pair_index)} keys, "
          f"Triple index: {len(triple_index)} keys")

    results = []
    found_keys = set()

    # For each C from the FULL pool
    for c_idx, (Dc, chi_c) in enumerate(full_pool):
        if len(results) >= cap:
            break

        c1_C = tuple(map(int, Dc))

        for sign in [+1, -1]:
            target_chi_B = chi_c + sign * target_chi

            # For each pair in pair_index, look up complementary triple
            for (c1_p, chi_p), pairs in pair_index.items():
                # Need triple with c1 = c1_C - c1_p and chi = target_chi_B - chi_p
                c1_need = tuple(c1_C[a] - c1_p[a] for a in range(h11_eff))
                chi_need = round(target_chi_B - chi_p, 4)
                triple_key = (c1_need, chi_need)

                if triple_key in triple_index:
                    for i, j in pairs:
                        for k, l, m in triple_index[triple_key]:
                            # Build the monad
                            B_divs = [small_pool[x][0] for x in [i, j, k, l, m]]
                            C_divs = [Dc.copy()]

                            # Deduplicate by sorted divisor tuples
                            dedup_key = (
                                tuple(sorted(tuple(map(int, d)) for d in B_divs)),
                                tuple(tuple(map(int, d)) for d in C_divs)
                            )
                            if dedup_key in found_keys:
                                continue
                            found_keys.add(dedup_key)

                            data = monad_chern_data(
                                B_divs, C_divs, intnums, c2, h11_eff)
                            if data['is_SU'] and abs(abs(data['chi']) - target_chi) < 0.01:
                                results.append(data)
                                if len(results) >= cap:
                                    return results

    return results


def _scan_monad_6_2_SU(small_pool, full_pool, intnums, c2, h11_eff,
                        target_chi, cap):
    """Meet-in-the-middle for rk_B=6, rk_C=2, SU(4) monads.

    Split B into 3+3 halves. For each C pair, match B halves.
    """
    print(f"  Building triple index for B (pool={len(small_pool)})...")
    n_sp = len(small_pool)

    # Build triple_index from small pool
    triple_index = {}
    for i in range(n_sp):
        for j in range(i, n_sp):
            for k in range(j, n_sp):
                Di, chi_i = small_pool[i]
                Dj, chi_j = small_pool[j]
                Dk, chi_k = small_pool[k]
                c1 = tuple(map(int, Di + Dj + Dk))
                chi = round(chi_i + chi_j + chi_k, 4)
                key = (c1, chi)
                if key not in triple_index:
                    triple_index[key] = []
                triple_index[key].append((i, j, k))

    print(f"  Triple index: {len(triple_index)} keys")

    results = []
    found_keys = set()
    n_fp = len(full_pool)

    # For each C pair from full pool
    for ci in range(n_fp):
        if len(results) >= cap:
            break
        for cj in range(ci, n_fp):
            if len(results) >= cap:
                break

            Dc1, chi_c1 = full_pool[ci]
            Dc2, chi_c2 = full_pool[cj]
            c1_C = tuple(map(int, Dc1 + Dc2))
            chi_C = chi_c1 + chi_c2

            for sign in [+1, -1]:
                target_chi_B = chi_C + sign * target_chi

                # Split B into triple1 + triple2
                # For each triple1, look up complementary triple2
                for (c1_t1, chi_t1), triples1 in triple_index.items():
                    c1_need = tuple(c1_C[a] - c1_t1[a] for a in range(h11_eff))
                    chi_need = round(target_chi_B - chi_t1, 4)
                    t2_key = (c1_need, chi_need)

                    if t2_key in triple_index:
                        for i1, j1, k1 in triples1:
                            for i2, j2, k2 in triple_index[t2_key]:
                                B_divs = [small_pool[x][0] for x in
                                         [i1, j1, k1, i2, j2, k2]]
                                C_divs = [Dc1.copy(), Dc2.copy()]

                                dedup_key = (
                                    tuple(sorted(tuple(map(int, d)) for d in B_divs)),
                                    tuple(sorted(tuple(map(int, d)) for d in C_divs))
                                )
                                if dedup_key in found_keys:
                                    continue
                                found_keys.add(dedup_key)

                                data = monad_chern_data(
                                    B_divs, C_divs, intnums, c2, h11_eff)
                                if data['is_SU'] and abs(abs(data['chi']) - target_chi) < 0.01:
                                    results.append(data)
                                    if len(results) >= cap:
                                        return results

    return results


def _scan_monad_simple(full_pool, intnums, c2, h11_eff,
                       target_chi, rk_B, rk_C, require_SU, cap):
    """Fallback simple monad scanner: try identical B copies and variants."""
    results = []
    lb_by_c1 = {}
    for idx, (D, chi) in enumerate(full_pool):
        key = tuple(D)
        if key not in lb_by_c1:
            lb_by_c1[key] = []
        lb_by_c1[key].append((idx, chi))

    for c_idx, (Dc, chi_c) in enumerate(full_pool):
        if len(results) >= cap:
            break

        if require_SU:
            # Try identical B: rk_B copies of O(Dc/rk_B)
            if all(d % rk_B == 0 for d in Dc):
                b_div = Dc // rk_B
                b_key = tuple(b_div)
                if b_key in lb_by_c1:
                    for _, chi_b in lb_by_c1[b_key]:
                        chi_V = rk_B * chi_b - chi_c
                        if abs(abs(chi_V) - target_chi) < 0.01:
                            B_divs = [b_div.copy() for _ in range(rk_B)]
                            C_divs = [Dc.copy()]
                            data = monad_chern_data(
                                B_divs, C_divs, intnums, c2, h11_eff)
                            results.append(data)
                            if len(results) >= cap:
                                return results
        else:
            for b_idx, (Db, chi_b) in enumerate(full_pool):
                chi_V = rk_B * chi_b - chi_c
                if abs(abs(chi_V) - target_chi) < 0.01:
                    B_divs = [Db.copy() for _ in range(rk_B)]
                    C_divs = [Dc.copy()]
                    data = monad_chern_data(
                        B_divs, C_divs, intnums, c2, h11_eff)
                    results.append(data)
                    if len(results) >= cap:
                        return results

    return results


# ══════════════════════════════════════════════════════════════════
#  Stability checks
# ══════════════════════════════════════════════════════════════════

def check_slope_stability_necessary(bundle_data, cyobj, h11_eff):
    """Necessary condition for slope stability of a direct sum.

    A direct sum V = L₁ ⊕ ... ⊕ Lₙ is NEVER stable (each Lᵢ is a
    sub-bundle). However, checking slope of each summand is useful for
    monads, where the Hoppe criterion applies.

    For an SU(n) bundle (μ(V) = 0), stability requires μ(F) < 0 for
    all proper sub-bundles F. For a monad V, the "obvious" sub-bundles
    are rank-1 quotients of B restricted to V.

    This function checks the simpler necessary condition:
      For SU(n): the individual summand slopes should be compatible 
      with stability after deformation.

    Returns dict with stability analysis.
    """
    try:
        tip = cyobj.toric_kahler_cone().tip_of_stretched_cone(1.0)
    except Exception:
        return {'stable': 'unknown', 'reason': 'no Kähler cone tip'}

    if tip is None or len(tip) == 0:
        return {'stable': 'unknown', 'reason': 'empty Kähler cone tip'}

    tip = np.array(tip, dtype=float)
    intnums = dict(cyobj.intersection_numbers(in_basis=True))

    # Compute μ(V) = c₁(V)·J²/rk(V) where J = Σ tᵢ eᵢ
    c1_V = bundle_data['c1']
    rk_V = bundle_data['rk']

    # c₁·J² = Σ_{a,b,c} c1_a t_b t_c κ_{abc}
    mu_V = 0.0
    for (a, b, c), val in intnums.items():
        mu_V += c1_V[a] * tip[b] * tip[c] * val

    mu_V /= rk_V

    result = {
        'mu_V': mu_V,
        'is_SU': bundle_data.get('is_SU', False),
    }

    # For direct sums, compute slope of each summand
    if 'divisors' in bundle_data:
        summand_slopes = []
        for D in bundle_data['divisors']:
            mu_i = 0.0
            for (a, b, c), val in intnums.items():
                mu_i += D[a] * tip[b] * tip[c] * val
            summand_slopes.append(mu_i)
        result['summand_slopes'] = summand_slopes
        result['stable'] = False  # direct sums are never stable
        result['reason'] = 'direct sum is always decomposable (polystable at best)'

        # Check if polystable: all summand slopes equal
        if len(set(round(s, 6) for s in summand_slopes)) == 1:
            result['polystable'] = True
        else:
            result['polystable'] = False

    return result


def check_hoppe_criterion(monad_data, cyobj, h11_eff,
                          pts, ray_indices, div_basis, n_toric, _precomp=None):
    """Hoppe criterion for monad stability (necessary condition).

    For a monad 0 → V → B → C → 0 on a CY3 X:

    V is μ-stable if H⁰(X, ∧ᵖV ⊗ L) = 0 for certain L.

    Simplified Hoppe criterion for SU(n) bundles (c₁=0):
      V is stable iff H⁰(X, ∧ᵖV) = 0 for 1 ≤ p ≤ rk(V)-1.

    For a rank-4 SU(4) monad, need:
      H⁰(X, V) = 0       (p=1)
      H⁰(X, ∧²V) = 0     (p=2)
      H⁰(X, ∧³V) = 0     (p=3, but ∧³V ≅ V* for SU(4))

    For V = ker(f: B → C), we can compute H⁰(V) from the long exact
    sequence:
      0 → H⁰(V) → H⁰(B) → H⁰(C) → H¹(V) → ...

    If f is surjective on global sections: H⁰(V) = ker(H⁰(B) → H⁰(C)).

    For ∧²V: much harder, requires spectral sequence computation.
    We implement the H⁰(V) check here as a first filter.

    Returns dict with stability analysis.
    """
    result = {'checks': {}}

    # Check H⁰(V) = 0 via H⁰(B) and H⁰(C)
    h0_B_total = 0
    h0_B_parts = []
    for D in monad_data['B_divisors']:
        D_toric = basis_to_toric(D, div_basis, n_toric)
        h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=_precomp)
        h0_B_parts.append(h0)
        h0_B_total += h0

    h0_C_total = 0
    h0_C_parts = []
    for D in monad_data['C_divisors']:
        D_toric = basis_to_toric(D, div_basis, n_toric)
        h0 = compute_h0_koszul(pts, ray_indices, D_toric, _precomp=_precomp)
        h0_C_parts.append(h0)
        h0_C_total += h0

    result['h0_B'] = h0_B_total
    result['h0_B_parts'] = h0_B_parts
    result['h0_C'] = h0_C_total
    result['h0_C_parts'] = h0_C_parts

    # Necessary condition: if H⁰(B) = 0, then H⁰(V) = 0 (good)
    # If H⁰(B) > 0 and H⁰(C) ≥ H⁰(B), the map might be surjective → H⁰(V) = 0
    # If H⁰(B) > H⁰(C), then dim(ker) ≥ H⁰(B) - H⁰(C) > 0 → H⁰(V) ≠ 0 → unstable

    if h0_B_total == 0:
        result['checks']['H0_V'] = 'pass'
        result['checks']['H0_V_reason'] = 'H⁰(B) = 0 ⟹ H⁰(V) = 0'
    elif h0_B_total <= h0_C_total:
        result['checks']['H0_V'] = 'likely_pass'
        result['checks']['H0_V_reason'] = (
            f'H⁰(B)={h0_B_total} ≤ H⁰(C)={h0_C_total}, '
            f'map could be injective ⟹ H⁰(V) = 0 possible')
    else:
        result['checks']['H0_V'] = 'fail'
        result['checks']['H0_V_reason'] = (
            f'H⁰(B)={h0_B_total} > H⁰(C)={h0_C_total}, '
            f'dim ker(H⁰(B)→H⁰(C)) ≥ {h0_B_total - h0_C_total} > 0 '
            f'⟹ H⁰(V) ≠ 0 ⟹ unstable')

    # Overall assessment
    fails = [k for k, v in result['checks'].items()
             if isinstance(v, str) and v == 'fail']
    passes = [k for k, v in result['checks'].items()
              if isinstance(v, str) and v == 'pass']

    if fails:
        result['stable'] = False
        result['reason'] = f"Failed: {', '.join(fails)}"
    elif len(passes) == len(result['checks']) // 2:  # only check keys, not reasons
        result['stable'] = 'likely'
        result['reason'] = 'Passed available Hoppe checks (∧²V not yet tested)'
    else:
        result['stable'] = 'inconclusive'
        result['reason'] = 'Some checks inconclusive'

    return result


# ══════════════════════════════════════════════════════════════════
#  Wedge product computation for ∧²V
# ══════════════════════════════════════════════════════════════════

def wedge2_direct_sum_chi(line_bundle_divisors, intnums, c2, h11_eff):
    """Compute χ(∧²V) for V = L₁ ⊕ ... ⊕ Lₙ.

    ∧²(L₁ ⊕ ... ⊕ Lₙ) = ⊕_{i<j} (Lᵢ ⊗ Lⱼ)

    So χ(∧²V) = Σ_{i<j} χ(Lᵢ ⊗ Lⱼ) = Σ_{i<j} χ(O(Dᵢ + Dⱼ))

    For Higgs doublet counting in heterotic models:
      n_Higgs = h¹(X, ∧²V)

    Returns (chi_wedge2, per_pair_chi) where per_pair_chi[k] = χ(Lᵢ⊗Lⱼ).
    """
    divisors = [np.asarray(D, dtype=np.float64) for D in line_bundle_divisors]
    n = len(divisors)

    total_chi = 0.0
    per_pair = []

    for i in range(n):
        for j in range(i + 1, n):
            D_sum = divisors[i] + divisors[j]
            chi_ij = compute_chi(D_sum, intnums, c2, h11_eff)
            per_pair.append(((i, j), float(chi_ij)))
            total_chi += chi_ij

    return total_chi, per_pair


def wedge2_monad_chi(monad_data, intnums, c2, h11_eff):
    """Estimate χ(∧²V) for a monad V.

    For a short exact sequence 0 → V → B → C → 0, we have:
      ∧²V embeds in ∧²B, and there's an exact sequence involving
      V ⊗ C and ∧²C. The full computation requires:
        0 → ∧²V → V ⊗ B/V → ... (complicated)

    Simpler: use the Chern character approach.
      ch(∧²V) can be computed from ch(V):
        ch₀(∧²V) = C(n,2) where n = rk(V)
        ch₁(∧²V) = (n-1)·ch₁(V)  [= (n-1)·c₁(V)]
        For SU(n): ch₁(∧²V) = 0

      χ(∧²V) = ∫ ch(∧²V)·Td(X) = ch₃(∧²V) + ch₁(∧²V)·c₂(X)/12

    For SU(n): ch₁(∧²V) = 0, so χ(∧²V) = ch₃(∧²V).

    Computing ch₃(∧²V) requires knowing c₁, c₂, c₃ of V:
      ch₃(∧²V) = (n-2)·ch₃(V) - ch₁(V)·ch₂(V) + ...

    This is getting complicated. For now, return the computation using
    the B and C data when available (since we know their line bundle structure).

    For a monad 0 → V → B → C → 0:
      ∧²(SES) gives: 0 → ∧²V → V⊗B → S²C ⊕ V⊗C⊗... → ...
    This requires detailed Chern character algebra.

    PLACEHOLDER: return None until we implement the full computation.
    """
    # TODO: implement full ∧²V Chern character computation for monads
    return None


# ══════════════════════════════════════════════════════════════════
#  Top-level analysis function
# ══════════════════════════════════════════════════════════════════

def analyze_rank_n_bundles(cy_data, target_chi=3, max_coeff=2,
                           max_nonzero=2, verbose=True):
    """Run full Stage 5 analysis on a CY manifold.

    Searches for:
      1. Direct sum bundles (Option B) — test infrastructure
      2. Monad bundles (Option A) — physics-relevant

    Args:
        cy_data: dict from extract_cy_data()
        target_chi: target |χ(V)| (default 3)
        max_coeff: max coefficient magnitude in divisor search
        max_nonzero: max nonzero entries per divisor
        verbose: print progress
    
    Returns:
        dict with all Stage 5 results
    """
    intnums = cy_data['intnums']
    c2 = cy_data['c2']
    h11_eff = cy_data['h11_eff']
    cyobj = cy_data['cyobj']
    pts = cy_data['pts']
    ray_indices = cy_data['ray_indices']
    div_basis = cy_data['div_basis']
    n_toric = cy_data['n_toric']

    results = {
        'direct_sum': {},
        'monad': {},
    }

    # ── Option B: Direct sum bundles ──
    if verbose:
        print("\n═══ Stage 5B: Direct Sum Bundles ═══")

    for rank in [4, 5]:
        if verbose:
            print(f"\n  --- Rank {rank} (SU({rank})) ---")

        ds_bundles = scan_direct_sum_bundles(
            intnums, c2, h11_eff,
            target_chi=target_chi, rank=rank,
            max_coeff=max_coeff, max_nonzero=max_nonzero,
            require_SU=True, cap=100
        )

        if verbose:
            print(f"  Found {len(ds_bundles)} SU({rank}) direct sum bundles with |χ|={target_chi}")

        # Compute ∧²V for Higgs counting
        for bd in ds_bundles:
            chi_w2, pairs = wedge2_direct_sum_chi(
                bd['divisors'], intnums, c2, h11_eff)
            bd['chi_wedge2'] = chi_w2
            bd['wedge2_pairs'] = pairs

        # Stability analysis
        for bd in ds_bundles:
            stab = check_slope_stability_necessary(bd, cyobj, h11_eff)
            bd['stability'] = stab

        results['direct_sum'][rank] = ds_bundles

        if verbose and ds_bundles:
            print(f"  Top 5 by |χ(∧²V)|:")
            sorted_ds = sorted(ds_bundles, key=lambda x: abs(x.get('chi_wedge2', 0)),
                              reverse=True)
            for i, bd in enumerate(sorted_ds[:5]):
                divs_str = ' ⊕ '.join(
                    f"O({list(map(int, d))})" for d in bd['divisors'])
                c1_str = list(map(int, bd['c1']))
                print(f"    [{i+1}] χ={bd['chi']:.0f}, "
                      f"χ(∧²V)={bd.get('chi_wedge2', '?'):.1f}, "
                      f"c₁={c1_str}")
                print(f"         {divs_str}")

    # ── Option A: Monad bundles ──
    if verbose:
        print("\n═══ Stage 5A: Monad Bundles ═══")

    for rk_B, rk_C in [(5, 1), (6, 2)]:
        rk_V = rk_B - rk_C
        if verbose:
            print(f"\n  --- Monad: 0 → V(rk {rk_V}) → B(rk {rk_B}) → C(rk {rk_C}) → 0 ---")

        monad_bundles = scan_monad_bundles(
            intnums, c2, h11_eff,
            target_chi=target_chi, rk_B=rk_B, rk_C=rk_C,
            max_coeff=max_coeff, max_nonzero=max_nonzero,
            require_SU=True, cap=100
        )

        if verbose:
            print(f"  Found {len(monad_bundles)} SU({rk_V}) monad bundles with |χ|={target_chi}")

        # Hoppe stability check for monads
        from cy_compute import precompute_vertex_data
        try:
            _precomp = precompute_vertex_data(pts, ray_indices)
        except Exception:
            _precomp = None

        for md in monad_bundles:
            hoppe = check_hoppe_criterion(
                md, cyobj, h11_eff,
                pts, ray_indices, div_basis, n_toric,
                _precomp=_precomp)
            md['hoppe'] = hoppe

        results['monad'][(rk_B, rk_C)] = monad_bundles

        if verbose and monad_bundles:
            # Show summary
            n_pass = sum(1 for m in monad_bundles
                        if m['hoppe']['checks'].get('H0_V') == 'pass')
            n_likely = sum(1 for m in monad_bundles
                          if m['hoppe']['checks'].get('H0_V') == 'likely_pass')
            n_fail = sum(1 for m in monad_bundles
                        if m['hoppe']['checks'].get('H0_V') == 'fail')
            print(f"  Hoppe H⁰(V)=0 check: {n_pass} pass, "
                  f"{n_likely} likely, {n_fail} fail")

            # Show top candidates
            good = [m for m in monad_bundles
                    if m['hoppe']['checks'].get('H0_V') != 'fail']
            if good:
                print(f"  Top candidates (Hoppe not failed):")
                for i, md in enumerate(good[:5]):
                    B_str = ' ⊕ '.join(
                        f"O({list(map(int, d))})" for d in md['B_divisors'])
                    C_str = ' ⊕ '.join(
                        f"O({list(map(int, d))})" for d in md['C_divisors'])
                    print(f"    [{i+1}] χ={md['chi']:.0f}, "
                          f"B={B_str}, C={C_str}")
                    print(f"         H⁰(B)={md['hoppe']['h0_B']}, "
                          f"H⁰(C)={md['hoppe']['h0_C']}, "
                          f"status={md['hoppe']['checks'].get('H0_V', '?')}")

    return results


# ══════════════════════════════════════════════════════════════════
#  Verification / cross-checks
# ══════════════════════════════════════════════════════════════════

def verify_chi_additivity(cy_data, n_tests=20):
    """Cross-check: χ(L₁⊕L₂) = χ(L₁) + χ(L₂) for random line bundles.

    This is a basic sanity check that our direct sum χ computation
    is consistent with the single line bundle χ computation.
    """
    intnums = cy_data['intnums']
    c2 = cy_data['c2']
    h11_eff = cy_data['h11_eff']

    rng = np.random.default_rng(42)
    all_pass = True

    for t in range(n_tests):
        D1 = rng.integers(-3, 4, size=h11_eff)
        D2 = rng.integers(-3, 4, size=h11_eff)

        chi1 = compute_chi(D1, intnums, c2, h11_eff)
        chi2 = compute_chi(D2, intnums, c2, h11_eff)
        chi_sum = direct_sum_chi([D1, D2], intnums, c2, h11_eff)

        if abs(chi_sum - (chi1 + chi2)) > 1e-10:
            print(f"  FAIL test {t}: χ(L₁⊕L₂)={chi_sum} ≠ "
                  f"χ(L₁)+χ(L₂)={chi1}+{chi2}={chi1+chi2}")
            all_pass = False

    return all_pass


def verify_monad_chi(cy_data, n_tests=20):
    """Cross-check: χ(V) = χ(B) - χ(C) for random monads."""
    intnums = cy_data['intnums']
    c2 = cy_data['c2']
    h11_eff = cy_data['h11_eff']

    rng = np.random.default_rng(123)
    all_pass = True

    for t in range(n_tests):
        # Random B (rk 5) and C (rk 1)
        B_divs = [rng.integers(-2, 3, size=h11_eff) for _ in range(5)]
        C_divs = [rng.integers(-2, 3, size=h11_eff)]

        chi_B = sum(compute_chi(D, intnums, c2, h11_eff) for D in B_divs)
        chi_C = sum(compute_chi(D, intnums, c2, h11_eff) for D in C_divs)
        chi_V = monad_chi(B_divs, C_divs, intnums, c2, h11_eff)

        if abs(chi_V - (chi_B - chi_C)) > 1e-10:
            print(f"  FAIL test {t}: χ(V)={chi_V} ≠ "
                  f"χ(B)-χ(C)={chi_B}-{chi_C}={chi_B-chi_C}")
            all_pass = False

    return all_pass


# ══════════════════════════════════════════════════════════════════
#  CLI entry point
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser(
        description='Stage 5: Higher-rank vector bundle analysis')
    parser.add_argument('--h11', type=int, required=True,
                       help='h11 value of the CY manifold')
    parser.add_argument('--poly', type=int, required=True,
                       help='Polytope index (0-based)')
    parser.add_argument('--max-coeff', type=int, default=2,
                       help='Max absolute coefficient in divisor search (default: 2)')
    parser.add_argument('--max-nonzero', type=int, default=2,
                       help='Max nonzero entries per divisor (default: 2)')
    parser.add_argument('--target-chi', type=int, default=3,
                       help='Target |χ(V)| (default: 3)')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only run verification tests')
    args = parser.parse_args()

    h11 = args.h11
    h21 = h11 + 3  # χ = -6
    poly_idx = args.poly

    print(f"Stage 5: Rank-n bundle analysis")
    print(f"  Target: h11={h11}, poly={poly_idx}")
    print(f"  Search: max_coeff={args.max_coeff}, max_nonzero={args.max_nonzero}")
    print(f"  Target χ(V): ±{args.target_chi}")
    print()

    # Fetch polytope
    print("Fetching polytope...")
    polys = fetch_polytopes_cached(h11, h21, limit=poly_idx + 1)
    if poly_idx >= len(polys):
        print(f"ERROR: Only {len(polys)} polytopes for h11={h11}, requested index {poly_idx}")
        exit(1)

    polytope = polys[poly_idx]
    print(f"  Polytope: {polytope}")

    # Extract CY data
    print("Extracting CY data...")
    cy_data = extract_cy_data(polytope)
    if cy_data is None:
        print("ERROR: Could not extract CY data")
        exit(1)

    print(f"  h11={cy_data['h11']}, h11_eff={cy_data['h11_eff']}, "
          f"n_toric={cy_data['n_toric']}")
    print(f"  favorable={cy_data['favorable']}")

    # Verification
    print("\n═══ Verification ═══")
    t0 = time.time()

    print("  χ additivity test: ", end='', flush=True)
    if verify_chi_additivity(cy_data):
        print("PASS (20/20)")
    else:
        print("FAIL")

    print("  Monad χ test: ", end='', flush=True)
    if verify_monad_chi(cy_data):
        print("PASS (20/20)")
    else:
        print("FAIL")

    print(f"  Verification time: {time.time()-t0:.1f}s")

    if args.verify_only:
        print("\nDone (verify-only mode)")
        exit(0)

    # Full analysis
    t0 = time.time()
    results = analyze_rank_n_bundles(
        cy_data,
        target_chi=args.target_chi,
        max_coeff=args.max_coeff,
        max_nonzero=args.max_nonzero,
    )

    # Summary
    print(f"\n{'='*60}")
    print(f"  Stage 5 Summary")
    print(f"{'='*60}")

    for rank, bundles in results['direct_sum'].items():
        print(f"  SU({rank}) direct sums: {len(bundles)}")

    for (rk_B, rk_C), bundles in results['monad'].items():
        rk_V = rk_B - rk_C
        n_stable = sum(1 for b in bundles
                      if b.get('hoppe', {}).get('checks', {}).get('H0_V') != 'fail')
        print(f"  SU({rk_V}) monads (B={rk_B},C={rk_C}): "
              f"{len(bundles)} total, {n_stable} Hoppe-compatible")

    print(f"\n  Total time: {time.time()-t0:.1f}s")
