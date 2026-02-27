#!/usr/bin/env python3
"""
cy_compute_v6.py — Physics computation layer for pipeline v6.

Imports ALL compute functions from v5 (which re-exports v2 functions).
Overrides ONLY the scoring: SM_SCORE_WEIGHTS and compute_sm_score().

v6 scoring changes from v5 (validated on 501K polytopes, 4,588 T2-scored):
  - tadpole_ok    5→0: dead (100% pass, topological constant χ/24=-0.25)
  - lvs_binary    5→0: near-dead (96.1% pass), merged into lvs_quality
  - lvs_quality  10→15: 7-tier grading (absorbed lvs_binary points)
  - mori_blowdown 5→2: near-dead (99.7% pass), keeps fraction grading
  - yukawa_hierarchy 27→30: THE key discriminator, extended top brackets
  - vol_hierarchy  5→7: independent signal, better graded
  - bundle_quality 0→3: NEW conjunction of depth + rate
  Total: 100 pts, 0 stranded.

All v5 compute functions are re-exported unchanged:
  analyze_intersection_algebra, compute_lvs_score, compute_yukawa_texture,
  analyze_mori_cone, classify_divisors, check_triangulation_stability,
  compute_tri_stability, check_instanton_divisor
"""

import sys
import os

# ── Fix the import path that v5 gets wrong ──
# v5 adds 'v2/' to sys.path, but the actual location is 'archive/v2/'.
# We add the correct path BEFORE importing v5, so v5's broken path
# attempt is harmless (the module is already found).
_v6_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_v6_dir)
_archive_v2_dir = os.path.join(_project_root, 'archive', 'v2')
if _archive_v2_dir not in sys.path:
    sys.path.insert(0, _archive_v2_dir)

# Now import v5's compute module (which imports from cy_compute in v2)
_v5_dir = os.path.join(_project_root, 'v5')
if _v5_dir not in sys.path:
    sys.path.insert(0, _v5_dir)

from cy_compute_v5 import (  # noqa: E402
    # v2 re-exports (core CYTools wrappers)
    count_lattice_points,
    precompute_vertex_data,
    count_lattice_points_batch,
    compute_h0_koszul,
    compute_h0_koszul_batch,
    compute_h0_parallel,
    compute_chi,
    compute_D3,
    build_intnum_tensor,
    compute_chi_batch,
    basis_to_toric,
    basis_to_toric_batch,
    find_chi3_bundles,
    find_chi3_bundles_capped,
    count_fibrations,
    extract_cy_data,
    check_swiss_cheese,
    poly_hash,
    fetch_polytopes_cached,
    clear_poly_cache,
    # v3/v4 compute functions
    analyze_intersection_algebra,
    compute_lvs_score,
    compute_yukawa_texture,
    analyze_mori_cone,
    classify_divisors,
    check_triangulation_stability,
    check_instanton_divisor,
    # v5 new
    compute_tri_stability,
)


# ══════════════════════════════════════════════════════════════════
#  SM Score (100-point composite) — v6
# ══════════════════════════════════════════════════════════════════

SM_SCORE_WEIGHTS = {
    # --- v6 weights (audit-validated on 501K polytopes, 4,588 T2-scored) ---
    #
    # Changes from v5:
    #   tadpole_ok     5→0: REMOVED — 100% pass (chi/24=-0.25 is a constant)
    #   lvs_binary     5→0: REMOVED — 96.1% pass, merged into lvs_quality
    #   lvs_quality   10→15: expanded 7-tier grading (absorbed lvs_binary pts)
    #   mori_blowdown  5→2: reduced — 99.7% pass, keeps fraction grading
    #   yukawa_hierarchy 27→30: upweighted — THE key discriminator (r=+0.31)
    #   vol_hierarchy   5→7: upweighted — independent signal
    #   bundle_quality  0→3: NEW — conjunction of depth + rate
    #
    'clean_bundles':    10,  # n_clean > 0, log₂ scaled (saturates ~50)
    'yukawa_rank':      15,  # Yukawa texture rank ≥ 3
    'yukawa_hierarchy': 30,  # eigenvalue spread — THE key discriminator
    'lvs_quality':      15,  # τ/V^{2/3} ratio grading (7 tiers, absorbed lvs_binary)
    'rank_sweet_spot':   3,  # Yukawa rank 140-159 sweet spot (from v5)
    'vol_hierarchy':     7,  # volume hierarchy (better graded)
    'mori_blowdown':     2,  # del Pezzo contraction fraction (reduced, keeps grading)
    'd3_diversity':      5,  # many distinct D³ values
    'clean_depth':       5,  # clean bundles found early in search
    'clean_rate':        5,  # n_clean / n_bundles_checked (structural quality)
    'bundle_quality':    3,  # NEW: conjunction of depth + rate
}

SM_SCORE_MAX = sum(SM_SCORE_WEIGHTS.values())  # 100


def compute_sm_score(data):
    """Compute 100-point SM composite score from polytope data dict.

    Accepts a dict with the relevant fields (from DB row or live computation).
    Missing fields score 0.

    v6 changes from v5:
      - Removed tadpole_ok (5→0): 100% pass, zero discrimination
      - Removed lvs_binary (5→0): 96.1% pass, merged into lvs_quality
      - lvs_quality expanded (10→15): 7-tier grading with finer brackets
      - mori_blowdown reduced (5→2): 99.7% pass, keeps fraction grading
      - yukawa_hierarchy upweighted (27→30): extended top brackets
      - vol_hierarchy upweighted (5→7): better graded
      - bundle_quality NEW (3 pts): rewards BOTH depth AND rate

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
    _tex = data.get('yukawa_texture_rank')
    yuk_rank = _tex if _tex is not None else data.get('yukawa_rank', 0)
    if yuk_rank is not None and yuk_rank >= 3:
        score += w['yukawa_rank']
    elif yuk_rank is not None and yuk_rank >= 1:
        score += w['yukawa_rank'] * yuk_rank // 3

    # ── Yukawa hierarchy (30 pts — THE discriminator) ──
    # v6: extended top brackets. ≥50K → full 30, ≥10K → 27 (was ceiling).
    yuk_hier = data.get('yukawa_hierarchy', 0.0) or 0.0
    if yuk_hier >= 5e4:
        score += 30                              # 30 pts (exceptional)
    elif yuk_hier >= 1e4:
        score += 27                              # 27 pts (elite)
    elif yuk_hier >= 1e3:
        score += 22                              # 22 pts
    elif yuk_hier >= 500:
        score += 17                              # 17 pts
    elif yuk_hier >= 1e2:
        score += 12                              # 12 pts
    elif yuk_hier >= 10:
        score += 5                               # 5 pts

    # ── LVS quality (15 pts — τ/V^{2/3} ratio, 7-tier grading) ──
    # Absorbs old lvs_binary (has_swiss → now implicitly scored via ratio).
    # Data: top scorers avg lvs=0.005, bottom avg lvs=0.08
    lvs = data.get('lvs_score')
    if lvs is not None:
        if lvs < 0.001:
            score += 15                          # superb
        elif lvs < 0.002:
            score += 13                          # elite
        elif lvs < 0.005:
            score += 10                          # excellent
        elif lvs < 0.01:
            score += 8                           # good
        elif lvs < 0.03:
            score += 5                           # decent
        elif lvs < 0.05:
            score += 3                           # marginal

    # ── Rank sweet spot (3 pts — from v5, unchanged) ──
    yuk_total = data.get('yukawa_rank', 0) or 0
    if 140 <= yuk_total <= 159:
        score += w['rank_sweet_spot']            # 3 pts
    elif 130 <= yuk_total <= 139:
        score += 2                               # 2 pts
    elif 120 <= yuk_total <= 129:
        score += 1                               # 1 pt

    # ── Volume hierarchy (7 pts — better graded) ──
    vol_h = data.get('volume_hierarchy', 0) or 0
    if vol_h >= 10000:
        score += 7                               # 7 pts
    elif vol_h >= 1000:
        score += 5                               # 5 pts
    elif vol_h >= 100:
        score += 3                               # 3 pts
    elif vol_h >= 10:
        score += 1                               # 1 pt

    # ── Mori cone blowdown (2 pts — fraction grading, reduced weight) ──
    n_dp_c = data.get('n_dp_contract', 0) or 0
    n_mori = data.get('n_mori_rays', 0) or 0
    if n_dp_c >= 1 and n_mori > 0:
        frac = n_dp_c / n_mori
        if frac >= 0.7:
            score += 2                           # 2 pts
        elif frac >= 0.3:
            score += 1                           # 1 pt

    # ── D³ diversity (5 pts — unchanged from v5) ──
    d3_n = data.get('d3_n_distinct', 0) or 0
    if d3_n >= 10:
        score += w['d3_diversity']
    elif d3_n >= 5:
        score += w['d3_diversity'] * 2 // 3
    elif d3_n >= 2:
        score += w['d3_diversity'] // 3

    # ── Clean depth (5 pts — unchanged from v5) ──
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

    # ── Clean rate (5 pts — unchanged from v5) ──
    n_checked = data.get('n_bundles_checked', 0) or 0
    if n_clean > 0 and n_checked > 0:
        rate = n_clean / n_checked
        if rate >= 0.03:
            score += w['clean_rate']
        elif rate >= 0.02:
            score += w['clean_rate'] * 2 // 3
        elif rate >= 0.01:
            score += w['clean_rate'] // 3

    # ── Bundle quality (3 pts — NEW: conjunction of depth + rate) ──
    # Rewards polytopes strong on BOTH dimensions. Different from separate
    # clean_depth/clean_rate which reward each independently.
    if n_clean > 0 and n_checked > 0:
        rate = n_clean / n_checked
        if n_clean >= 20 and rate >= 0.03:
            score += 3                           # 3 pts
        elif n_clean >= 10 and rate >= 0.02:
            score += 2                           # 2 pts
        elif n_clean >= 5 and rate >= 0.01:
            score += 1                           # 1 pt

    return min(score, SM_SCORE_MAX)
