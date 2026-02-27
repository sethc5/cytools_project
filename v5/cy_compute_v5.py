#!/usr/bin/env python3
"""
cy_compute_v5.py — Physics computation layer for pipeline v5.

Imports and re-exports all v2 functions (lattice points, Koszul h⁰,
bundle search, fibration counting, Swiss cheese). Adds v3/v4/v5 routines:

  T05 (intersection algebra):
    - analyze_intersection_algebra()  →  Yukawa rank, c₂ positivity, volume form
  T2 (deep physics):
    - compute_lvs_score()            →  LVS compatibility from Kähler cone scan
    - compute_yukawa_texture()       →  Yukawa matrix for clean bundles
    - analyze_mori_cone()            →  Mori cone rays, del Pezzo contractions
  T3 (stability):
    - compute_tri_stability()        →  c₂ / κ hash stability across random tris
  Scoring:
    - compute_sm_score()             →  100-point SM composite score (v5 weights)

v5 scoring changes from v4.1 (h22-40 data, 19K polytopes):
  - fibration_sm removed (3→0): only 3 polytopes had SM gauge group;
    n_k3_fib anti-correlates (r=-0.22). 3 points permanently stranded.
  - rank_sweet_spot added (0→3): Yukawa rank 140-159 is the SM sweet spot
    for h11_eff in 18-22 range. Graded: 140-159→3, 130-139→2, 120-129→1.
  - mori_blowdown graded (binary→fraction): n_dp_contract/n_mori_rays ratio
    replaces binary check. ≥0.9→5, ≥0.7→4, ≥0.5→3, ≥0.3→2, else→1.
  Total: 100 points, 0 stranded.

All functions take CYTools objects or dicts — no raw SQL.
"""

import json
import sys
import os
import numpy as np

# ── Import all v2 functions ──────────────────────────────────────
# Add v2/ to path so we can import without package gymnastics
_v2_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'v2')
if _v2_dir not in sys.path:
    sys.path.insert(0, _v2_dir)

from cy_compute import (  # noqa: E402
    # Lattice point counting
    count_lattice_points,
    precompute_vertex_data,
    count_lattice_points_batch,
    # Koszul h⁰
    compute_h0_koszul,
    compute_h0_koszul_batch,
    compute_h0_parallel,
    # χ and intersection numbers
    compute_chi,
    compute_D3,
    build_intnum_tensor,
    compute_chi_batch,
    # Coordinate conversions
    basis_to_toric,
    basis_to_toric_batch,
    # Bundle search
    find_chi3_bundles,
    find_chi3_bundles_capped,
    # Fibrations
    count_fibrations,
    # CY data extraction
    extract_cy_data,
    # Swiss cheese
    check_swiss_cheese,
    # Utility
    poly_hash,
    # Polytope cache
    fetch_polytopes_cached,
    clear_poly_cache,
)


# ══════════════════════════════════════════════════════════════════
#  T05: Intersection Algebra Analysis
# ══════════════════════════════════════════════════════════════════

def analyze_intersection_algebra(cyobj, h11_eff, intnums_basis=None, c2_basis=None):
    """Analyze the intersection algebra for physics content.

    Cheap (~0.1s): uses only κ_{ijk} and c₂ already computed in T0.

    Args:
        cyobj: CYTools CY threefold object
        h11_eff: effective Picard rank
        intnums_basis: dict of intersection numbers (in basis), or None to compute
        c2_basis: c₂ vector (in basis), or None to compute

    Returns:
        dict with yukawa_rank, yukawa_density, c2_all_positive,
        c2_vector, kappa_signature, volume_form_type, n_kappa_entries
    """
    if intnums_basis is None:
        intnums_basis = dict(cyobj.intersection_numbers(in_basis=True))
    if c2_basis is None:
        c2_basis = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

    result = {}

    # ── Yukawa rank: count nonzero κ_{ijk} in basis ──
    # Total possible triples (with repetition, sorted indices)
    total_triples = 0
    nonzero_triples = 0
    for i in range(h11_eff):
        for j in range(i, h11_eff):
            for k in range(j, h11_eff):
                total_triples += 1
                key = (i, j, k)
                if key in intnums_basis and intnums_basis[key] != 0:
                    nonzero_triples += 1

    result['yukawa_rank'] = nonzero_triples
    result['yukawa_density'] = (nonzero_triples / total_triples
                                if total_triples > 0 else 0.0)
    result['n_kappa_entries'] = total_triples

    # ── c₂ positivity (DRS conjecture) ──
    c2_vec = c2_basis[:h11_eff]
    result['c2_all_positive'] = int(np.all(c2_vec >= 0))
    result['c2_vector'] = c2_vec.tolist()

    # ── Volume form structure via Hessian at Kähler cone tip ──
    kappa_sig, vol_type = _classify_volume_form(cyobj, h11_eff, intnums_basis)
    result['kappa_signature'] = kappa_sig
    result['volume_form_type'] = vol_type

    return result


def _classify_volume_form(cyobj, h11_eff, intnums_basis):
    """Classify the volume form by Hessian eigenvalue structure.

    Evaluates H_ij = ∂²V/∂t^i∂t^j at the Kähler cone tip.
    V = (1/6) κ_{ijk} t^i t^j t^k
    H_ij = κ_{ijk} t^k

    Returns:
        (signature_string, type_string)
        signature_string: "(p, q)" where p = positive eigenvalues, q = negative
        type_string: "swiss_cheese" | "fibered" | "generic"
    """
    try:
        kc = cyobj.toric_kahler_cone()
        tip = np.array(kc.tip_of_stretched_cone(1.0), dtype=float)
    except Exception:
        return ("unknown", "generic")

    if tip is None or len(tip) < h11_eff:
        return ("unknown", "generic")

    # Build Hessian: H_{ab} = Σ_c κ_{abc} t_c
    # κ stored with sorted indices (i≤j≤k). For each stored triple,
    # contract each distinct index with tip and assign to remaining pair.
    # Mirrors the Yukawa texture approach to avoid degenerate overcounting.
    H = np.zeros((h11_eff, h11_eff), dtype=float)
    for (i, j, k), val in intnums_basis.items():
        ii, jj, kk = int(i), int(j), int(k)
        if ii >= h11_eff or jj >= h11_eff or kk >= h11_eff:
            continue
        # Contract first index with tip → H[jj, kk]
        H[jj, kk] += val * tip[ii]
        # Contract second index (if distinct from first) → H[ii, kk]
        if ii != jj:
            H[ii, kk] += val * tip[jj]
        # Contract third index (if distinct from both) → H[ii, jj]
        if ii != kk and jj != kk:
            H[ii, jj] += val * tip[kk]

    # Loop fills upper triangle for off-diagonal entries.
    # Copy upper→lower (H.T adds the transpose), then subtract diagonal
    # to avoid double-counting the diagonal which was already correct.
    H = H + H.T - np.diag(np.diag(H))

    eigenvalues = np.linalg.eigvalsh(H)
    n_pos = int(np.sum(eigenvalues > 1e-10))
    n_neg = int(np.sum(eigenvalues < -1e-10))
    n_zero = h11_eff - n_pos - n_neg

    sig = f"({n_pos},{n_neg},{n_zero})" if n_zero > 0 else f"({n_pos},{n_neg})"

    # Classify
    if n_pos == 1 and n_neg == h11_eff - 1:
        vol_type = "swiss_cheese"
    elif n_zero >= h11_eff // 2:
        vol_type = "fibered"
    else:
        vol_type = "generic"

    return (sig, vol_type)


# ══════════════════════════════════════════════════════════════════
#  T2: LVS Compatibility Score
# ══════════════════════════════════════════════════════════════════

def compute_lvs_score(cyobj, h11_eff):
    """Compute LVS compatibility by scanning for small 4-cycles.

    Tests multiple points in the Kähler cone: the tip, extremal rays,
    and scaled versions. Finds the best τ_small / V^{2/3} ratio.

    Returns:
        dict with lvs_score, best_small_div, volume_hierarchy,
        has_swiss, n_swiss, best_swiss_tau, best_swiss_ratio
    """
    result = {
        'lvs_score': 1.0,       # default: bad (1.0 = no hierarchy)
        'best_small_div': -1,
        'volume_hierarchy': 1.0,
        'has_swiss': 0,
        'n_swiss': 0,
        'best_swiss_tau': 0.0,
        'best_swiss_ratio': 1.0,
    }

    try:
        kc = cyobj.toric_kahler_cone()
        tip = np.array(kc.tip_of_stretched_cone(1.0), dtype=float)
    except Exception:
        return result

    if tip is None or len(tip) < h11_eff:
        return result

    best_ratio = 1.0
    best_div = -1
    swiss_hits = []

    # Test two scale factors (ratios are scale-invariant for
    # the homogeneous part; 2 scales suffice to probe hierarchy)
    for scale in [10.0, 50.0]:
        t_scaled = tip * scale
        try:
            vol = cyobj.compute_cy_volume(t_scaled)
            dvols = cyobj.compute_divisor_volumes(t_scaled)
        except Exception:
            continue

        if vol <= 0:
            continue

        v_23 = vol ** (2.0 / 3.0)
        for i in range(min(len(dvols), h11_eff)):
            tau_i = float(dvols[i])
            if tau_i <= 0:
                continue
            ratio = tau_i / v_23
            if ratio < best_ratio:
                best_ratio = ratio
                best_div = i

            # Skip Swiss cheese probe if ratio already too large
            if ratio > 0.5:
                continue

            # Swiss cheese test: can we make this one small while rest are large?
            t_test = t_scaled.copy()
            t_test[i] = tip[i]  # keep one at tip scale, rest at scaled
            try:
                vol2 = cyobj.compute_cy_volume(t_test)
                dvols2 = cyobj.compute_divisor_volumes(t_test)
                if vol2 > 0:
                    tau_small = float(dvols2[i])
                    ratio2 = tau_small / vol2 ** (2.0 / 3.0)
                    if ratio2 < 0.1:
                        swiss_hits.append((i, tau_small, vol2, ratio2))
            except Exception:
                continue

    # Volume hierarchy: max/min divisor volume at best scale
    try:
        t_big = tip * 20.0
        dvols_big = cyobj.compute_divisor_volumes(t_big)
        dvols_pos = [v for v in dvols_big if v > 0]
        if dvols_pos:
            result['volume_hierarchy'] = max(dvols_pos) / min(dvols_pos)
    except Exception:
        pass

    result['lvs_score'] = best_ratio
    result['best_small_div'] = best_div

    if swiss_hits:
        swiss_hits.sort(key=lambda x: x[3])
        result['has_swiss'] = 1
        result['n_swiss'] = len(swiss_hits)
        result['best_swiss_tau'] = swiss_hits[0][1]
        result['best_swiss_ratio'] = swiss_hits[0][3]

    return result


# ══════════════════════════════════════════════════════════════════
#  T2: Yukawa Texture Analysis
# ══════════════════════════════════════════════════════════════════

def compute_yukawa_texture(D_basis, intnums_basis, h11_eff):
    """Compute the Yukawa coupling matrix for a line bundle.

    For a bundle V with divisor class D:
        Y_{abc} = κ_{ijk} D_a^i D_b^j D_c^k
    where a,b,c label the 3 generations (when h⁰ = 3).

    Since we don't have the explicit basis of H¹(V), we compute the
    "diagonal" Yukawa: Y = D_i D_j D_k κ_{ijk} projected onto the
    bundle's divisor components. This gives the overall Yukawa scale
    and structure, not the full 3×3 matrix.

    For a more meaningful analysis, we construct a proxy 3×3 matrix
    by evaluating the Yukawa trilinear form at 3 random directions
    in the divisor space near D.

    Args:
        D_basis: (h11_eff,) bundle divisor in basis
        intnums_basis: dict of κ_{ijk}
        h11_eff: effective Picard rank

    Returns:
        dict with yukawa_texture_rank, yukawa_hierarchy, yukawa_zeros
    """
    D = np.array(D_basis, dtype=float)

    # Build the trilinear form T contracted with D
    # Y_jk(D) = Σ_i κ_{ijk} D_i (a bilinear form on the remaining 2 indices)
    Y2 = np.zeros((h11_eff, h11_eff), dtype=float)
    for (i, j, k), val in intnums_basis.items():
        ii, jj, kk = int(i), int(j), int(k)
        if ii < h11_eff and jj < h11_eff and kk < h11_eff:
            # Weight by D components; symmetrize over the contraction index
            Y2[jj, kk] += val * D[ii]
            if ii != jj:
                Y2[ii, kk] += val * D[jj]
            if ii != kk and jj != kk:
                Y2[ii, jj] += val * D[kk]

    # Upper triangle was filled; copy to lower without halving.
    Y2 = Y2 + Y2.T - np.diag(np.diag(Y2))

    # Nonzero eigenvalues → Yukawa rank and hierarchy
    eigvals = np.abs(np.linalg.eigvalsh(Y2))
    eigvals_nz = eigvals[eigvals > 1e-12]

    result = {
        'yukawa_texture_rank': len(eigvals_nz),
        'yukawa_hierarchy': 0.0,
        'yukawa_zeros': int(np.sum(np.abs(Y2) < 1e-12)),
    }

    if len(eigvals_nz) >= 2:
        result['yukawa_hierarchy'] = float(eigvals_nz.max() / eigvals_nz.min())

    return result


# ══════════════════════════════════════════════════════════════════
#  T2: Mori Cone Analysis
# ══════════════════════════════════════════════════════════════════

def analyze_mori_cone(cyobj, h11_eff, intnums_basis=None, c2_basis=None):
    """Analyze Mori cone for del Pezzo contractions.

    A del Pezzo contraction exists when a Mori cone generator C
    satisfies: D · C < 0 for a del Pezzo divisor D (i.e., C shrinks
    the dP surface).

    Args:
        cyobj: CYTools CY object
        h11_eff: effective Picard rank
        intnums_basis: intersection numbers dict (optional)
        c2_basis: c₂ vector (optional)

    Returns:
        dict with n_mori_rays, n_dp_contract
    """
    result = {'n_mori_rays': 0, 'n_dp_contract': 0}

    try:
        mc = cyobj.toric_mori_cone()
        mori_rays = np.array(mc.rays())
        result['n_mori_rays'] = len(mori_rays)
    except Exception:
        return result

    if intnums_basis is None:
        intnums_basis = dict(cyobj.intersection_numbers(in_basis=True))
    if c2_basis is None:
        c2_basis = np.array(cyobj.second_chern_class(in_basis=True), dtype=float)

    # Identify del Pezzo divisors (D³ > 0, c₂·D > 0, D³ = 9-n for dP_n)
    dp_indices = []
    for a in range(h11_eff):
        D3 = intnums_basis.get((a, a, a), 0)
        c2D = c2_basis[a] if a < len(c2_basis) else 0
        if D3 > 0 and c2D > 0:
            dp_n = 9 - D3
            if 0 <= dp_n <= 8:
                dp_indices.append(a)

    if not dp_indices:
        return result

    # Check each Mori ray against each dP divisor
    # Compute D_a² · C_m = Σ_j κ_{a,a,j} C_m[j]  (self-intersection of D_a along C_m)
    # Negative value → C_m is a contractible curve on the dP surface D_a
    n_contract = 0
    for m_ray in mori_rays:
        for a in dp_indices:
            # Compute intersection D_a · C_m using the bilinear pairing
            # from the intersection form
            dot = 0.0
            for j in range(min(len(m_ray), h11_eff)):
                key = tuple(sorted([a, a, j]))
                dot += intnums_basis.get(key, 0) * float(m_ray[j])
            if dot < -1e-10:
                n_contract += 1
                break  # count each ray once

    result['n_dp_contract'] = n_contract
    return result


# ══════════════════════════════════════════════════════════════════
#  Divisor Classification (from v2 T1, extracted for reuse)
# ══════════════════════════════════════════════════════════════════

def classify_divisors(intnums_basis, c2_basis, h11_eff):
    """Classify basis divisors as del Pezzo, K3, or rigid.

    Returns:
        dict with n_dp, dp_types, n_k3_div, n_rigid
    """
    n_dp = 0
    dp_types = []
    n_k3_div = 0
    n_rigid = 0

    for a in range(h11_eff):
        D3 = intnums_basis.get((a, a, a), 0)
        c2D = c2_basis[a] if a < len(c2_basis) else 0

        if D3 > 0 and c2D > 0:
            dp_n = 9 - D3
            if 0 <= dp_n <= 8:
                n_dp += 1
                dp_types.append(dp_n)
            n_rigid += 1
        elif D3 == 0 and c2D > 0:
            n_k3_div += 1
        elif D3 < 0:
            n_rigid += 1

    return {
        'n_dp': n_dp,
        'dp_types': dp_types,
        'n_k3_div': n_k3_div,
        'n_rigid': n_rigid,
    }


# ══════════════════════════════════════════════════════════════════
#  SM Score (100-point composite) — v5
# ══════════════════════════════════════════════════════════════════

SM_SCORE_WEIGHTS = {
    # --- v5 weights (updated from h22-40 analysis, 19K polytopes) ---
    # v5 changes from v4.1:
    #   fibration_sm 3→0 (REMOVED): only 3 polytopes had SM gauge group;
    #     n_k3_fib anti-correlates (r=-0.22). 3 points permanently stranded.
    #   rank_sweet_spot 0→3 (NEW): Yukawa rank 140-159 is the SM sweet spot
    #     for h11_eff 18-22. Graded: 140-159→3, 130-139→2, 120-129→1.
    #   mori_blowdown: binary→graded by contraction fraction
    #     (n_dp_contract / n_mori_rays). Rewards higher dP coverage.
    'clean_bundles':    10,  # n_clean > 0, log₂ scaled (saturates ~50)
    'yukawa_rank':      15,  # Yukawa texture rank ≥ 3
    'yukawa_hierarchy': 27,  # eigenvalue spread — THE key discriminator
    'lvs_binary':        5,  # has Swiss cheese structure (yes/no)
    'lvs_quality':      10,  # τ/V^{2/3} ratio grading (smaller = better)
    'rank_sweet_spot':   3,  # Yukawa rank 140-159 sweet spot (replaces fibration_sm)
    'vol_hierarchy':     5,  # volume hierarchy > 1000
    'tadpole_ok':        5,  # |χ/24| ≤ 20
    'mori_blowdown':     5,  # del Pezzo contraction fraction (graded)
    'd3_diversity':      5,  # many distinct D³ values
    'clean_depth':       5,  # clean bundles found early in search
    'clean_rate':        5,  # n_clean / n_bundles_checked (structural quality)
}

SM_SCORE_MAX = sum(SM_SCORE_WEIGHTS.values())  # 100


def compute_sm_score(data):
    """Compute 100-point SM composite score from polytope data dict.

    Accepts a dict with the relevant fields (from DB row or live computation).
    Missing fields score 0.

    v5 changes from v4.1:
      - fibration_sm removed: only 3 polytopes in 19K had SM gauge group.
        3 pts permanently stranded → removed entirely.
      - rank_sweet_spot added (3 pts): Yukawa rank in 140-159 range is
        the sweet spot for h11_eff=18-22 polytopes. Graded tiers.
      - mori_blowdown graded: fraction of Mori rays with dP contractions
        replaces binary yes/no. Better discrimination.

    Args:
        data: dict with keys matching polytope columns

    Returns:
        int score in [0, 100]
    """
    import math
    score = 0
    w = SM_SCORE_WEIGHTS

    # ── Clean bundles (log₂ scaled, 10 pts max) ──
    n_clean = data.get('n_clean', 0) or 0
    if n_clean > 0:
        # 1 clean → 3pts, 8 → 6pts, 32 → 8pts, 50+ → 10pts
        score += min(w['clean_bundles'],
                     int(2 + 2.0 * math.log2(max(1, n_clean))))

    # ── Yukawa texture rank (15 pts) ──
    # Use yukawa_texture_rank (T2 eigenvalue count) if available;
    # fall back to yukawa_rank (T05 κ triple count) only if texture_rank
    # was never computed (None), NOT when it's 0 (= no clean bundles).
    _tex = data.get('yukawa_texture_rank')
    yuk_rank = _tex if _tex is not None else data.get('yukawa_rank', 0)
    if yuk_rank is not None and yuk_rank >= 3:
        score += w['yukawa_rank']
    elif yuk_rank is not None and yuk_rank >= 1:
        score += w['yukawa_rank'] * yuk_rank // 3

    # ── Yukawa hierarchy (27 pts — THE discriminator) ──
    # Data: score-90 all have hier > 1000. score-86 avg ~200.
    # Graded: <10 → 0, 10-99 → 5, 100-499 → 10, 500-999 → 15,
    #         1000-9999 → 20, 10000+ → 27
    yuk_hier = data.get('yukawa_hierarchy', 0.0) or 0.0
    if yuk_hier >= 1e4:
        score += w['yukawa_hierarchy']          # 27 pts
    elif yuk_hier >= 1e3:
        score += 20                              # 20 pts
    elif yuk_hier >= 500:
        score += 15                              # 15 pts
    elif yuk_hier >= 1e2:
        score += 10                              # 10 pts
    elif yuk_hier >= 10:
        score += 5                               # 5 pts

    # ── LVS binary (5 pts — has swiss cheese at all) ──
    if data.get('has_swiss'):
        score += w['lvs_binary']

    # ── LVS quality (10 pts — τ/V^{2/3} ratio grading) ──
    # Data: top scorers avg lvs=0.005, bottom avg lvs=0.08
    lvs = data.get('lvs_score')
    if lvs is not None:
        if lvs < 0.002:           # elite
            score += w['lvs_quality']
        elif lvs < 0.005:         # excellent
            score += 8
        elif lvs < 0.01:          # good
            score += 6
        elif lvs < 0.03:          # decent
            score += 4
        elif lvs < 0.05:          # marginal
            score += 2

    # ── Rank sweet spot (3 pts — replaces fibration_sm) ──
    # Yukawa rank 140-159 is the SM sweet spot for h11_eff=18-22.
    # Below 120: too sparse. Above 160: too dense (less texture).
    yuk_total = data.get('yukawa_rank', 0) or 0
    if 140 <= yuk_total <= 159:
        score += w['rank_sweet_spot']       # 3 pts
    elif 130 <= yuk_total <= 139:
        score += 2                           # 2 pts
    elif 120 <= yuk_total <= 129:
        score += 1                           # 1 pt

    # ── Volume hierarchy (5 pts — big/small divisor volume ratio) ──
    vol_h = data.get('volume_hierarchy', 0) or 0
    if vol_h >= 1000:
        score += w['vol_hierarchy']
    elif vol_h >= 100:
        score += w['vol_hierarchy'] * 2 // 3
    elif vol_h >= 10:
        score += w['vol_hierarchy'] // 3

    # ── Tadpole bound (5 pts) ──
    chi24 = data.get('chi_over_24')
    if chi24 is not None and abs(chi24) <= 20:
        score += w['tadpole_ok']

    # ── Mori cone blowdown (5 pts — graded by contraction fraction) ──
    # v5: fraction of Mori rays with dP contractions, not binary yes/no.
    n_dp_c = data.get('n_dp_contract', 0) or 0
    n_mori = data.get('n_mori_rays', 0) or 0
    if n_dp_c >= 1 and n_mori > 0:
        frac = n_dp_c / n_mori
        if frac >= 0.9:
            score += 5                       # 5 pts
        elif frac >= 0.7:
            score += 4                       # 4 pts
        elif frac >= 0.5:
            score += 3                       # 3 pts
        elif frac >= 0.3:
            score += 2                       # 2 pts
        else:
            score += 1                       # 1 pt (any contraction)

    # ── D³ diversity (5 pts) ──
    d3_n = data.get('d3_n_distinct', 0) or 0
    if d3_n >= 10:
        score += w['d3_diversity']
    elif d3_n >= 5:
        score += w['d3_diversity'] * 2 // 3
    elif d3_n >= 2:
        score += w['d3_diversity'] // 3

    # ── Clean depth (5 pts — clean bundles found early) ──
    first_clean = data.get('first_clean_at', -1)
    n_chi3 = data.get('n_chi3', 0) or 0
    if first_clean is not None and first_clean >= 0 and n_chi3 > 0:
        frac = first_clean / max(1, n_chi3)
        if frac < 0.05:
            score += w['clean_depth']
        elif frac < 0.2:
            score += w['clean_depth'] * 2 // 3
        elif frac < 0.5:
            score += w['clean_depth'] // 3

    # ── Clean rate (5 pts — structural SM-friendliness) ──
    n_checked = data.get('n_bundles_checked', 0) or 0
    if n_clean > 0 and n_checked > 0:
        rate = n_clean / n_checked
        if rate >= 0.03:       # top: 3%+ clean
            score += w['clean_rate']
        elif rate >= 0.02:     # good: 2-3%
            score += w['clean_rate'] * 2 // 3
        elif rate >= 0.01:     # decent: 1-2%
            score += w['clean_rate'] // 3

    return min(score, SM_SCORE_MAX)


# ══════════════════════════════════════════════════════════════════
#  T3: Triangulation Stability (v4 — property-level)
# ══════════════════════════════════════════════════════════════════

def check_triangulation_stability(polytope, n_samples=50, key_checks=None):
    """Check if properties are stable across random triangulations.

    Args:
        polytope: CYTools Polytope object
        n_samples: number of random triangulations to test
        key_checks: list of properties to check stability of
                   default: ['has_clean', 'has_swiss', 'has_fib']

    Returns:
        dict with n_triangulations, props_stable (1 if ≥80% stable)
    """
    if key_checks is None:
        key_checks = ['has_clean', 'has_swiss', 'has_fib']

    result = {'n_triangulations': 0, 'props_stable': 0}

    try:
        tris = polytope.random_triangulations_fast(N=n_samples)
    except Exception:
        try:
            tris = [polytope.triangulate()]
        except Exception:
            return result

    # Fibrations depend on polytope only (triangulation-independent).
    # Check once before the loop to avoid redundant dual-polytope computation.
    has_fib = False
    if 'has_fib' in key_checks:
        try:
            n_k3, n_ell = count_fibrations(polytope)
            has_fib = (n_k3 > 0 or n_ell > 0)
        except Exception:
            pass

    n_tested = 0
    props = {k: 0 for k in key_checks}

    for tri in tris:
        try:
            cy = tri.get_cy()
            h11_eff = len(cy.divisor_basis())
            intnums = dict(cy.intersection_numbers(in_basis=True))
            c2 = np.array(cy.second_chern_class(in_basis=True), dtype=float)

            pts = np.array(polytope.points(), dtype=int)
            n_toric = pts.shape[0]
            ray_indices = list(range(1, n_toric))
            div_basis = [int(x) for x in cy.divisor_basis()]

            # Quick checks (not full bundle census — too slow)
            if 'has_clean' in key_checks:
                bundles = find_chi3_bundles_capped(intnums, c2, h11_eff,
                                                   max_coeff=2, max_nonzero=2,
                                                   cap=20)
                if bundles:
                    _precomp = precompute_vertex_data(pts, ray_indices)
                    for D_basis, chi_val in bundles[:10]:
                        # Handle both chi signs (same logic as T1/T2)
                        if chi_val > 0:
                            D_check = basis_to_toric(D_basis, div_basis, n_toric)
                            D_dual = basis_to_toric(-D_basis, div_basis, n_toric)
                        else:
                            D_check = basis_to_toric(-D_basis, div_basis, n_toric)
                            D_dual = basis_to_toric(D_basis, div_basis, n_toric)
                        h0 = compute_h0_koszul(pts, ray_indices, D_check,
                                               _precomp=_precomp)
                        if h0 == 3:
                            h3 = compute_h0_koszul(pts, ray_indices, D_dual,
                                                   _precomp=_precomp)
                            if h3 == 0:
                                props['has_clean'] += 1
                                break

            if 'has_swiss' in key_checks:
                swiss = check_swiss_cheese(cy, h11_eff)
                if swiss:
                    props['has_swiss'] += 1

            if 'has_fib' in key_checks and has_fib:
                props['has_fib'] += 1

            n_tested += 1
        except Exception:
            continue

    result['n_triangulations'] = n_tested
    if n_tested > 0:
        # Stable if ≥80% of triangulations share the property
        stability_pct = min(props.get(k, 0) / n_tested for k in key_checks)
        result['props_stable'] = 1 if stability_pct >= 0.8 else 0

    return result


# ══════════════════════════════════════════════════════════════════
#  T3: Triangulation Stability — c₂ / κ hash (v5 NEW)
# ══════════════════════════════════════════════════════════════════

def compute_tri_stability(polytope, n_samples=20):
    """Test c₂ vector and κ hash stability across random triangulations.

    Compares each random triangulation against the default placing
    triangulation to check if the c₂ vector and the set of nonzero
    κ_{ijk} entries are invariant.

    This is a lightweight, quantitative stability check:
      - c₂ stable → moduli-stabilization inputs are triangulation-independent
      - κ hash stable → Yukawa texture is triangulation-independent

    Args:
        polytope: CYTools Polytope object
        n_samples: number of random triangulations to test (default 20)

    Returns:
        dict with:
          tri_n_tested: int — number of random triangulations tested
          tri_c2_stable_frac: float — fraction with same c₂ as default
          tri_kappa_stable_frac: float — fraction with same κ nonzero pattern
    """
    result = {
        'tri_n_tested': 0,
        'tri_c2_stable_frac': 0.0,
        'tri_kappa_stable_frac': 0.0,
    }

    # ── Reference: default placing triangulation ──
    try:
        tri_ref = polytope.triangulate()
        cy_ref = tri_ref.get_cy()
        h11_eff_ref = len(cy_ref.divisor_basis())
        c2_ref = tuple(np.array(cy_ref.second_chern_class(in_basis=True),
                                dtype=float).round(8).tolist())
        intnums_ref = dict(cy_ref.intersection_numbers(in_basis=True))
        kappa_hash_ref = frozenset(k for k, v in intnums_ref.items() if v != 0)
    except Exception:
        return result

    # ── Sample random triangulations ──
    try:
        tris = polytope.random_triangulations_fast(N=n_samples)
    except Exception:
        return result

    n_tested = 0
    n_c2_match = 0
    n_kappa_match = 0

    for tri in tris:
        try:
            cy = tri.get_cy()
            h11_eff = len(cy.divisor_basis())

            # Skip if effective rank changed (different basis)
            if h11_eff != h11_eff_ref:
                n_tested += 1
                continue

            # c₂ comparison
            c2_vec = tuple(np.array(cy.second_chern_class(in_basis=True),
                                    dtype=float).round(8).tolist())
            if c2_vec == c2_ref:
                n_c2_match += 1

            # κ nonzero pattern comparison
            intnums = dict(cy.intersection_numbers(in_basis=True))
            kappa_hash = frozenset(k for k, v in intnums.items() if v != 0)
            if kappa_hash == kappa_hash_ref:
                n_kappa_match += 1

            n_tested += 1
        except Exception:
            continue

    result['tri_n_tested'] = n_tested
    if n_tested > 0:
        result['tri_c2_stable_frac'] = round(n_c2_match / n_tested, 4)
        result['tri_kappa_stable_frac'] = round(n_kappa_match / n_tested, 4)

    return result


# ══════════════════════════════════════════════════════════════════
#  T3: Instanton Divisor Check
# ══════════════════════════════════════════════════════════════════

def check_instanton_divisor(intnums_basis, c2_basis, h11_eff):
    """Check for rigid del Pezzo divisors suitable for E3 instantons.

    For LVS moduli stabilization, need a divisor D with:
      - D³ = 9 - n for some 0 ≤ n ≤ 8 (del Pezzo dP_n)
      - c₂·D = 3 + n
      - The divisor is rigid: h^{1,0} = h^{2,0} = 0

    For toric divisors, rigidity follows from the dP structure.

    Returns:
        1 if suitable instanton divisor exists, 0 otherwise
    """
    for a in range(h11_eff):
        D3 = intnums_basis.get((a, a, a), 0)
        c2D = c2_basis[a] if a < len(c2_basis) else 0

        if D3 > 0 and c2D > 0:
            dp_n = 9 - D3
            expected_c2D = 3 + dp_n
            # Allow some tolerance because c₂ in toric basis may differ
            if 0 <= dp_n <= 8 and abs(c2D - expected_c2D) < 2:
                return 1
    return 0
