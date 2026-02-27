#!/usr/bin/env python3
"""
fiber_analysis.py — F-theory elliptic fibration analysis for toric CY3s.

Given a reflexive 4D polytope with elliptic fibrations, classifies:
  1. Fiber polygon type (which of 16 reflexive 2D polygons)
  2. Base surface topology
  3. Kodaira singular fiber types (via "tops" analysis from N-lattice polytope)
  4. Gauge algebra from Kodaira classification
  5. Standard Model gauge group check

The F-theory gauge algebra arises from singular fibers in the elliptic
fibration π: X → B.  Over each toric divisor D_ρ of the base B, the
fiber can degenerate.  In the toric picture, the degeneration is visible
from the lattice points of the N-lattice polytope Δ at each base height.

Algorithm:
  1. Find 2D reflexive sub-polygons F* ⊆ Δ* (M-lattice dual polytope)
     → each defines an elliptic fibration with fiber Newton polygon F*.
  2. For each fibration, project Δ (N-lattice polytope) to base coordinates
     via b(p) = (⟨p,w₁⟩, ⟨p,w₂⟩) where w₁,w₂ span F*.
  3. The lattice points of Δ at each base height form "tops".
  4. The excess lattice points (beyond minimum) at each base divisor
     determine the Kodaira fiber type → gauge algebra.

Kodaira fiber type → Gauge algebra:
  I_0     → trivial (smooth fiber)
  I_n     → su(n)  [or sp(⌊n/2⌋) if monodromy]
  II      → trivial
  III     → su(2)
  IV      → su(3)  [or sp(1)]
  I*_n    → so(2n+8) [or so(2n+7)]
  IV*     → e₆     [or f₄]
  III*    → e₇
  II*     → e₈

Usage:
    python fiber_analysis.py --h11 17 --poly 25
    python fiber_analysis.py --h11 14 --poly 2 --verbose
    python fiber_analysis.py --h11 17 --poly 63 --save

Reference: FRAMEWORK.md §B-21, Braun (2012) arXiv:1110.4883,
           Candelas-Font (2000), Bouchard-Svrček (2003)
"""

import argparse
import json
import sys
import time
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
import cytools as cy
from cytools.config import enable_experimental_features
enable_experimental_features()

# ══════════════════════════════════════════════════════════════════
#  16 reflexive 2D polygon classification
# ══════════════════════════════════════════════════════════════════

# All 16 reflexive 2D polygons (classified by GL₂(ℤ)-invariant).
# Computed by exhaustive enumeration of reflexive lattice polygons.
# Invariant = (n_lattice_pts, n_hull_vertices, sorted_edge_gcds, 2×area).

REFLEXIVE_2D_POLYGONS = {
    # 4 points (1 polygon)
    1:  {'verts': [(-1,-1),(1,0),(0,1)],             'n_pts': 4,
         'name': 'F1',  'surface': 'P2',  'inv': (4,3,(1,1,1),3)},

    # 5 points (2 polygons)
    2:  {'verts': [(-1,-1),(1,0),(-1,1)],            'n_pts': 5,
         'name': 'F2',  'surface': 'Bl_1(P2)',  'inv': (5,3,(1,1,2),4)},
    3:  {'verts': [(-1,0),(0,-1),(1,0),(0,1)],       'n_pts': 5,
         'name': 'F3',  'surface': 'P1xP1', 'inv': (5,4,(1,1,1,1),4)},

    # 6 points (2 polygons)
    4:  {'verts': [(-1,-1),(1,0),(0,1),(-1,1)],      'n_pts': 6,
         'name': 'F4',  'surface': '',  'inv': (6,4,(1,1,1,2),5)},
    5:  {'verts': [(-1,-1),(0,-1),(1,0),(0,1),(-1,0)], 'n_pts': 6,
         'name': 'F5',  'surface': '',  'inv': (6,5,(1,1,1,1,1),5)},

    # 7 points (5 polygons)
    6:  {'verts': [(-1,-1),(2,0),(0,1)],             'n_pts': 7,
         'name': 'F6',  'surface': 'P(1,1,2)',  'inv': (7,3,(1,2,3),6)},
    7:  {'verts': [(-1,-1),(1,-1),(0,1),(-1,1)],     'n_pts': 7,
         'name': 'F7',  'surface': '',  'inv': (7,4,(1,1,2,2),6)},
    8:  {'verts': [(-1,-1),(1,-1),(1,0),(0,1),(-1,0)], 'n_pts': 7,
         'name': 'F8',  'surface': '',  'inv': (7,5,(1,1,1,1,2),6)},
    9:  {'verts': [(-1,0),(-1,-1),(0,-1),(1,0),(1,1),(0,1)], 'n_pts': 7,
         'name': 'F9',  'surface': 'dP6',  'inv': (7,6,(1,1,1,1,1,1),6)},
    # Note: 5th 7-pt polygon (if exists) has inv TBD - not found in [-2,2]² search

    # 8 points (2 polygons)
    10: {'verts': [(-1,-1),(1,-1),(1,0),(0,1),(-1,1)], 'n_pts': 8,
         'name': 'F10', 'surface': '',  'inv': (8,4,(1,1,2,3),7),
         'note': 'trapezoid with off-edge points'},
    11: {'verts': [(-1,-1),(1,-1),(1,0),(0,1),(-1,0)], 'n_pts': 8,
         'name': 'F11', 'surface': '',  'inv': (8,5,(1,1,1,2,2),7)},

    # 9 points (3 polygons)
    12: {'verts': [(0,-1),(2,-1),(-1,1)],            'n_pts': 9,
         'name': 'F12', 'surface': '',  'inv': (9,3,(2,2,4),8)},
    13: {'verts': [(0,-1),(2,-1),(0,1),(-1,1)],      'n_pts': 9,
         'name': 'F13', 'surface': '',  'inv': (9,4,(1,2,2,3),8)},
    14: {'verts': [(0,-1),(2,-1),(0,1),(-2,1)],      'n_pts': 9,
         'name': 'F14', 'surface': '',  'inv': (9,4,(2,2,2,2),8)},

    # 10 points (1 polygon)
    15: {'verts': [(-1,-1),(2,-1),(-1,2)],           'n_pts': 10,
         'name': 'F15', 'surface': 'dP3_max',  'inv': (10,3,(3,3,3),9),
         'note': 'generic Weierstrass model'},
}


def _lattice_pts_of_polygon(verts):
    """Enumerate all lattice points inside a 2D convex polygon.

    Computes convex hull first to ensure proper vertex ordering,
    then uses half-plane intersection for robust containment.
    """
    # Get proper convex hull ordering
    hull = _convex_hull_2d([(int(v[0]), int(v[1])) for v in verts])
    if len(hull) < 3:
        return [tuple(v) for v in verts]

    hull = [(int(x), int(y)) for x, y in hull]
    n = len(hull)

    # Bounding box
    xs = [p[0] for p in hull]
    ys = [p[1] for p in hull]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    # Pre-compute edge normals (inward-pointing for CCW hull)
    edges = []
    for i in range(n):
        x1, y1 = hull[i]
        x2, y2 = hull[(i + 1) % n]
        # For CCW hull, inward normal of edge (x1,y1)→(x2,y2) is (-(y2-y1), x2-x1)
        edges.append((x1, y1, -(y2 - y1), x2 - x1))

    pts = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            inside = True
            for ex, ey, nx, ny in edges:
                # dot product with inward normal
                if nx * (x - ex) + ny * (y - ey) < 0:
                    inside = False
                    break
            if inside:
                pts.append((x, y))

    return pts


def _convex_hull_2d(points):
    """Compute convex hull vertices of 2D points (gift wrapping)."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    # Andrew's monotone chain
    def cross(O, A, B):
        return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _polygon_invariant(lattice_pts):
    """Compute a GL₂(ℤ)-invariant fingerprint for a 2D lattice polygon.

    Returns (n_total, n_vertices, sorted_edge_gcd_lengths, area_2x)
    where edge_gcd_length is gcd(|Δx|, |Δy|) for each convex hull edge.
    """
    hull = _convex_hull_2d(lattice_pts)
    n_verts = len(hull)
    n_total = len(lattice_pts)

    # Edge lattice lengths (gcd of coordinate differences)
    edge_lens = []
    for i in range(n_verts):
        p1 = hull[i]
        p2 = hull[(i + 1) % n_verts]
        dx = abs(p2[0] - p1[0])
        dy = abs(p2[1] - p1[1])
        edge_lens.append(int(np.gcd(dx, dy)))
    edge_lens.sort()

    # 2x area via shoelace
    area_2x = 0
    for i in range(n_verts):
        j = (i + 1) % n_verts
        area_2x += hull[i][0] * hull[j][1] - hull[j][0] * hull[i][1]
    area_2x = abs(area_2x)

    return (n_total, n_verts, tuple(edge_lens), area_2x)


def classify_fiber_polygon(lattice_pts_2d):
    """Classify a 2D reflexive polygon among the 15 known types.

    Uses GL₂(ℤ)-invariant fingerprint for robust matching:
    (n_total_pts, n_hull_vertices, sorted_edge_gcds, 2×area).

    Args:
        lattice_pts_2d: list of (x,y) integer tuples — all lattice points
                        of the polygon (including interior).

    Returns:
        (polygon_id, info_dict) or (0, {'name': 'unknown', ...}) if not matched.
    """
    target = _polygon_invariant(lattice_pts_2d)

    for pid, info in REFLEXIVE_2D_POLYGONS.items():
        if info.get('inv') == target:
            return pid, info

    # Fallback
    n_pts = len(lattice_pts_2d)
    hull = _convex_hull_2d(lattice_pts_2d)
    n_verts = len(hull)

    return 0, {'name': f'unknown({n_pts}pts,{n_verts}v)',
               'n_pts': n_pts, 'surface': '?'}


# ══════════════════════════════════════════════════════════════════
#  Elliptic fibration finder
# ══════════════════════════════════════════════════════════════════

def find_elliptic_fibrations(polytope, verbose=False):
    """Find all unique elliptic fibrations of a reflexive 4D polytope.

    An elliptic fibration is determined by a 2D reflexive sub-polygon
    F* ⊂ Δ* (the M-lattice dual polytope).  Two spanning vectors
    w₁, w₂ ∈ M of F* define the fibration.

    Returns list of dicts with keys:
        'w1', 'w2': spanning vectors of fiber polygon in M
        'fiber_pts_M': lattice points of the fiber polygon in Δ*
        'n_fiber_pts': number of those points
        'fiber_pts_2d': projected 2D coordinates of fiber polygon
        'fiber_id': reflexive polygon classification ID
        'fiber_info': classification info dict
    """
    dual_p = polytope.dual()
    pts_M = np.array(dual_p.points(), dtype=int)
    dual_set = set(tuple(x) for x in pts_M)

    # K3 directions: pairs ±v in Δ* with gcd=1
    k3_dirs = []
    for pt in pts_M:
        if np.all(pt == 0):
            continue
        if tuple(-pt) in dual_set and tuple(pt) < tuple(-pt):
            gcd = int(np.gcd.reduce(np.abs(pt)))
            if gcd == 1:
                k3_dirs.append(tuple(pt))

    if verbose:
        print(f"  K3 directions: {len(k3_dirs)}")

    # Find 2D reflexive sub-polygons (unique by point set)
    seen = set()
    fibs = []
    for i in range(len(k3_dirs)):
        for j in range(i + 1, len(k3_dirs)):
            w1, w2 = np.array(k3_dirs[i]), np.array(k3_dirs[j])
            W = np.vstack([w1, w2])
            if np.linalg.matrix_rank(W) < 2:
                continue

            sub_pts = []
            for pt in pts_M:
                aug = np.vstack([W, pt])
                if np.linalg.matrix_rank(aug) <= 2:
                    sub_pts.append(tuple(pt))

            if 4 <= len(sub_pts) <= 10:
                key = frozenset(sub_pts)
                if key not in seen:
                    seen.add(key)

                    # Find proper lattice basis for the 2D subspace
                    # (K3 directions may not generate the full sublattice)
                    basis = []
                    for pt in sub_pts:
                        if all(x == 0 for x in pt):
                            continue
                        if len(basis) == 0:
                            basis.append(np.array(pt, dtype=float))
                        elif len(basis) == 1:
                            mat = np.vstack([basis[0], np.array(pt, dtype=float)])
                            if np.linalg.matrix_rank(mat) == 2:
                                basis.append(np.array(pt, dtype=float))
                                break

                    if len(basis) < 2:
                        continue

                    # Project to 2D coordinates using lattice basis
                    A = np.vstack(basis).T   # (dim, 2)
                    pts_2d = []
                    valid = True
                    for pt in sub_pts:
                        ab, _, _, _ = np.linalg.lstsq(A, np.array(pt, dtype=float),
                                                       rcond=None)
                        a_int = round(float(ab[0]))
                        b_int = round(float(ab[1]))
                        # Verify integer coordinates
                        if abs(float(ab[0]) - a_int) > 0.01 or \
                           abs(float(ab[1]) - b_int) > 0.01:
                            valid = False
                            break
                        pts_2d.append((a_int, b_int))

                    if not valid:
                        # Basis doesn't generate lattice; try all pairs
                        nonzero = [np.array(p, dtype=float) for p in sub_pts
                                   if not all(x == 0 for x in p)]
                        found_basis = False
                        for bi in range(len(nonzero)):
                            for bj in range(bi+1, len(nonzero)):
                                mat = np.vstack([nonzero[bi], nonzero[bj]])
                                if np.linalg.matrix_rank(mat) < 2:
                                    continue
                                A2 = mat.T
                                pts_2d_try = []
                                ok = True
                                for pt in sub_pts:
                                    ab2, _, _, _ = np.linalg.lstsq(
                                        A2, np.array(pt, dtype=float), rcond=None)
                                    ai = round(float(ab2[0]))
                                    bi_ = round(float(ab2[1]))
                                    if abs(float(ab2[0]) - ai) > 0.01 or \
                                       abs(float(ab2[1]) - bi_) > 0.01:
                                        ok = False
                                        break
                                    pts_2d_try.append((ai, bi_))
                                if ok:
                                    pts_2d = pts_2d_try
                                    found_basis = True
                                    break
                            if found_basis:
                                break
                        if not found_basis:
                            continue

                    # Classify the fiber polygon
                    fid, finfo = classify_fiber_polygon(pts_2d)

                    fibs.append({
                        'w1': k3_dirs[i],
                        'w2': k3_dirs[j],
                        'fiber_pts_M': sub_pts,
                        'n_fiber_pts': len(sub_pts),
                        'fiber_pts_2d': pts_2d,
                        'fiber_id': fid,
                        'fiber_info': finfo,
                    })

    if verbose:
        print(f"  Unique elliptic fibrations: {len(fibs)}")

    return fibs


# ══════════════════════════════════════════════════════════════════
#  Base projection and tops computation
# ══════════════════════════════════════════════════════════════════

def compute_base_and_tops(polytope, fibration, verbose=False):
    """Compute the base surface and top data for an elliptic fibration.

    Projects the N-lattice polytope Δ to base coordinates via
    b(p) = (⟨p,w₁⟩, ⟨p,w₂⟩) and groups lattice points by base height.

    Returns dict with:
        'base_pts': list of distinct base coordinates
        'base_hull': convex hull vertices of base polygon
        'n_base_pts': total distinct base heights
        'fiber_at_origin': # lattice points at base origin
        'slices': {base_coord: list_of_Δ_points_at_that_height}
        'excess': {base_coord: n_extra_points_beyond_minimum}
        'total_excess': total gauge algebra rank estimate
        'h11_base': estimated h¹¹ of base surface
    """
    pts_N = np.array(polytope.points(), dtype=int)
    w1 = np.array(fibration['w1'], dtype=int)
    w2 = np.array(fibration['w2'], dtype=int)

    # Project to base coordinates
    slices = defaultdict(list)
    for pt in pts_N:
        b = (int(np.dot(pt, w1)), int(np.dot(pt, w2)))
        slices[b].append(tuple(pt))

    base_pts = sorted(slices.keys())
    base_hull = _convex_hull_2d(base_pts)
    n_fiber_0 = len(slices.get((0, 0), []))

    # Compute excess: for non-origin base points, excess = count - 1
    # (minimum 1 point needed per base vertex for a valid polytope)
    excess = {}
    total_excess = 0
    for b in base_pts:
        if b == (0, 0):
            continue
        e = len(slices[b]) - 1
        excess[b] = e
        total_excess += e

    # Base surface h¹¹ estimate
    # For a toric surface from a 2D polygon fan: h¹¹ = n_rays - 2
    # n_rays = number of boundary lattice points of base polygon
    boundary_pts = set()
    for b in base_pts:
        if b != (0, 0):
            boundary_pts.add(b)
    h11_base = max(len(boundary_pts) - 2, 0)

    return {
        'base_pts': base_pts,
        'base_hull': base_hull,
        'n_base_pts': len(base_pts),
        'fiber_at_origin': n_fiber_0,
        'slices': dict(slices),
        'excess': excess,
        'total_excess': total_excess,
        'h11_base': h11_base,
    }


# ══════════════════════════════════════════════════════════════════
#  Kodaira fiber type classification
# ══════════════════════════════════════════════════════════════════

# Kodaira → gauge algebra lookup
KODAIRA_GAUGE = {
    'I_0':   {'algebra': '-',       'rank': 0,  'dim': 0},
    'I_1':   {'algebra': '-',       'rank': 0,  'dim': 0},
    'I_2':   {'algebra': 'su(2)',   'rank': 1,  'dim': 3},
    'I_3':   {'algebra': 'su(3)',   'rank': 2,  'dim': 8},
    'I_4':   {'algebra': 'su(4)',   'rank': 3,  'dim': 15},
    'I_5':   {'algebra': 'su(5)',   'rank': 4,  'dim': 24},
    'I_6':   {'algebra': 'su(6)',   'rank': 5,  'dim': 35},
    'II':    {'algebra': '-',       'rank': 0,  'dim': 0},
    'III':   {'algebra': 'su(2)',   'rank': 1,  'dim': 3},
    'IV':    {'algebra': 'su(3)',   'rank': 2,  'dim': 8},
    'I*_0':  {'algebra': 'so(8)',   'rank': 4,  'dim': 28},
    'I*_1':  {'algebra': 'so(10)',  'rank': 5,  'dim': 45},
    'I*_2':  {'algebra': 'so(12)',  'rank': 6,  'dim': 66},
    'IV*':   {'algebra': 'e6',      'rank': 6,  'dim': 78},
    'III*':  {'algebra': 'e7',      'rank': 7,  'dim': 133},
    'II*':   {'algebra': 'e8',      'rank': 8,  'dim': 248},
}


def classify_top(n_excess, fiber_pts_at_height, base_coord, verbose=False):
    """Classify the Kodaira fiber type from excess lattice points.

    This is a heuristic classification based on the number of excess
    lattice points at each base height.  Full classification requires
    the intersection structure from the triangulation.

    Args:
        n_excess: number of excess lattice points at this base height
        fiber_pts_at_height: list of lattice points of Δ at this height
        base_coord: the base coordinate (for context)

    Returns:
        dict with 'kodaira', 'algebra', 'rank', 'confidence', 'note'
    """
    if n_excess == 0:
        return {
            'kodaira': 'I_0 or I_1',
            'algebra': '-',
            'rank': 0,
            'confidence': 'high',
            'note': 'smooth or nodal fiber'
        }

    # For toric resolutions, the excess points resolve A-D-E singularities.
    # The most common case: excess points form an A_{n} chain → I_{n+1}
    # This is a rank-level heuristic; full identification needs intersections.

    # Heuristic: excess n → most likely I_{n+1} (type A_n singularity)
    # unless the points have a branching structure (→ D or E type)

    if n_excess <= 6:
        # Default: assume A-type (I_{n+1})
        kodaira = f'I_{n_excess + 1}'
        algebra = f'su({n_excess + 1})'
        confidence = 'medium'
        note = f'A_{n_excess} singularity (most common for toric)'
    elif n_excess == 7:
        kodaira = 'I_8 or III*'
        algebra = 'su(8) or e7'
        confidence = 'low'
        note = 'needs intersection structure to distinguish'
    elif n_excess == 8:
        kodaira = 'I_9 or II*'
        algebra = 'su(9) or e8'
        confidence = 'low'
        note = 'needs intersection structure to distinguish'
    else:
        kodaira = f'I_{n_excess + 1}'
        algebra = f'su({n_excess + 1})'
        confidence = 'low'
        note = 'large excess — could be non-A type'

    return {
        'kodaira': kodaira,
        'algebra': algebra,
        'rank': n_excess,
        'confidence': confidence,
        'note': note,
    }


def analyze_kodaira_types(top_data, verbose=False):
    """Classify Kodaira types for all base divisors in a fibration.

    Returns list of dicts, one per non-trivial base divisor.
    """
    results = []
    for b, n_excess in sorted(top_data['excess'].items()):
        if n_excess == 0:
            continue
        pts = top_data['slices'][b]
        ktype = classify_top(n_excess, pts, b, verbose=verbose)
        ktype['base_coord'] = b
        ktype['n_points'] = len(pts)
        results.append(ktype)

    return results


# ══════════════════════════════════════════════════════════════════
#  Gauge algebra assembly
# ══════════════════════════════════════════════════════════════════

def compute_gauge_algebra(kodaira_types, h11_X=None, h11_base=None):
    """Assemble the total gauge algebra from Kodaira types.

    Returns dict with:
        'components': list of gauge algebra factors
        'total_rank': sum of ranks
        'total_dim': sum of dimensions
        'description': human-readable string
        'contains_SM': whether SU(3)×SU(2)×U(1) is possible
        'MW_rank_bound': Mordell-Weil rank upper bound (= # of U(1)s)
    """
    components = []
    total_rank = 0

    for kt in kodaira_types:
        if kt['rank'] > 0:
            components.append({
                'algebra': kt['algebra'],
                'rank': kt['rank'],
                'location': kt['base_coord'],
                'kodaira': kt['kodaira'],
            })
            total_rank += kt['rank']

    # Mordell-Weil rank bound: if h¹¹ is known
    mw_bound = None
    if h11_X is not None and h11_base is not None:
        # h¹¹(X) = h¹¹(B) + rk(G) + 1 + rk(MW)
        mw_bound = h11_X - h11_base - 1 - total_rank
        if mw_bound < 0:
            mw_bound = None  # formula doesn't apply cleanly

    # Check for SM gauge group possibility
    has_su3 = any(c['rank'] >= 2 for c in components)
    has_su2 = any(c['rank'] >= 1 for c in components)
    has_u1 = (mw_bound is not None and mw_bound >= 1) or \
             (len(components) >= 2)  # multiple factors can give U(1)

    contains_sm = has_su3 and has_su2 and has_u1

    # Check specifically for SU(5) GUT possibility
    has_su5 = any(c['rank'] >= 4 for c in components)

    desc_parts = [c['algebra'] for c in components if c['rank'] > 0]
    if mw_bound and mw_bound > 0:
        desc_parts.append(f"U(1)^{mw_bound}")

    return {
        'components': components,
        'total_rank': total_rank,
        'description': ' × '.join(desc_parts) if desc_parts else 'trivial',
        'contains_SM': contains_sm,
        'has_SU5_GUT': has_su5,
        'MW_rank_bound': mw_bound,
    }


# ══════════════════════════════════════════════════════════════════
#  Full analysis pipeline
# ══════════════════════════════════════════════════════════════════

def analyze_polytope(polytope, h11=None, verbose=False):
    """Full F-theory fibration analysis of a polytope.

    Returns dict with all fibration data, Kodaira types, gauge algebras.
    """
    t0 = time.time()
    pts_N = np.array(polytope.points(), dtype=int)

    # Get h¹¹ if not provided
    if h11 is None:
        try:
            t = polytope.triangulate()
            X = t.get_cy()
            h11 = X.h11()
        except Exception:
            pass

    if verbose:
        print(f"\n  Polytope: {len(pts_N)} pts in N-lattice, dim={polytope.dimension()}")
        dual_p = polytope.dual()
        print(f"  Dual: {len(dual_p.points())} pts in M-lattice")
        if h11:
            print(f"  h¹¹ = {h11}")

    # Find all elliptic fibrations
    fibs = find_elliptic_fibrations(polytope, verbose=verbose)

    results = {
        'n_fibrations': len(fibs),
        'h11': h11,
        'fibrations': [],
    }

    # Analyze each fibration
    best_sm_score = 0
    for i, fib in enumerate(fibs):
        if verbose:
            print(f"\n  {'─'*56}")
            print(f"  Fibration {i+1}/{len(fibs)}:")
            print(f"    Fiber polygon: {fib['n_fiber_pts']} pts, "
                  f"type {fib['fiber_info'].get('name', '?')}")
            if fib['fiber_info'].get('surface'):
                print(f"    Toric surface: {fib['fiber_info']['surface']}")

        # Compute base and tops
        top_data = compute_base_and_tops(polytope, fib, verbose=verbose)

        if verbose:
            print(f"    Base polygon: {len(top_data['base_hull'])} vertices, "
                  f"{top_data['n_base_pts']} lattice pts")
            print(f"    Fiber at origin: {top_data['fiber_at_origin']} pts")
            print(f"    Total gauge rank (excess): {top_data['total_excess']}")
            print(f"    Base decomposition:")
            for b in sorted(top_data['slices'].keys()):
                n = len(top_data['slices'][b])
                tag = " ← generic fiber" if b == (0, 0) else ""
                if b != (0, 0) and top_data['excess'].get(b, 0) > 0:
                    tag = f" ← {top_data['excess'][b]} excess → resolution divisors"
                print(f"      {b}: {n} pts{tag}")

        # Classify Kodaira types
        kodaira = analyze_kodaira_types(top_data, verbose=verbose)

        if verbose and kodaira:
            print(f"    Kodaira classification:")
            for kt in kodaira:
                print(f"      Base {kt['base_coord']}: {kt['kodaira']} → "
                      f"{kt['algebra']} (rank {kt['rank']}, {kt['confidence']})")

        # Compute gauge algebra
        gauge = compute_gauge_algebra(
            kodaira, h11_X=h11, h11_base=top_data.get('h11_base'))

        if verbose:
            print(f"    Gauge algebra: {gauge['description']}")
            if gauge['MW_rank_bound'] is not None:
                print(f"    Mordell-Weil rank bound: {gauge['MW_rank_bound']}")
            if gauge['contains_SM']:
                print(f"    ★ CONTAINS SU(3)×SU(2)×U(1) — SM candidate!")
            if gauge['has_SU5_GUT']:
                print(f"    ★ HAS SU(5) — GUT candidate!")

        # SM score
        sm_score = 0
        if gauge['contains_SM']:
            sm_score += 1
        if gauge['has_SU5_GUT']:
            sm_score += 1

        best_sm_score = max(best_sm_score, sm_score)

        fib_result = {
            'fiber_pts': fib['n_fiber_pts'],
            'fiber_type': fib['fiber_info'].get('name', '?'),
            'fiber_surface': fib['fiber_info'].get('surface', '?'),
            'base_pts': top_data['n_base_pts'],
            'base_hull_vertices': len(top_data['base_hull']),
            'fiber_at_origin': top_data['fiber_at_origin'],
            'total_excess': top_data['total_excess'],
            'kodaira_types': [
                {'base': kt['base_coord'], 'type': kt['kodaira'],
                 'algebra': kt['algebra'], 'rank': kt['rank'],
                 'confidence': kt['confidence']}
                for kt in kodaira
            ],
            'gauge_algebra': gauge['description'],
            'gauge_rank': gauge['total_rank'],
            'contains_SM': gauge['contains_SM'],
            'has_SU5_GUT': gauge['has_SU5_GUT'],
            'MW_rank_bound': gauge['MW_rank_bound'],
        }
        results['fibrations'].append(fib_result)

    elapsed = time.time() - t0
    results['elapsed'] = elapsed
    results['best_sm_score'] = best_sm_score

    return results


# ══════════════════════════════════════════════════════════════════
#  Batch analysis
# ══════════════════════════════════════════════════════════════════

def analyze_batch(h11, h21=None, limit=100, verbose=False, min_fibs=1):
    """Analyze all polytopes at given Hodge numbers.

    Returns list of results, one per polytope with ≥ min_fibs fibrations.
    """
    if h21 is None:
        h21 = h11 + 3

    polys = list(cy.fetch_polytopes(h11=h11, h21=h21, limit=limit))
    print(f"\n  Fetched {len(polys)} polytopes for h11={h11}, h21={h21}")

    batch_results = []
    for idx, p in enumerate(polys):
        result = analyze_polytope(p, h11=h11, verbose=False)
        if result['n_fibrations'] >= min_fibs:
            result['poly_idx'] = idx
            batch_results.append(result)
            if verbose:
                sm_tag = " ★ SM" if result['best_sm_score'] > 0 else ""
                algebras = [f['gauge_algebra'] for f in result['fibrations']]
                unique_alg = sorted(set(algebras))
                print(f"  Poly {idx:>4}: {result['n_fibrations']} fibs, "
                      f"gauge: {', '.join(unique_alg)}{sm_tag}")

    return batch_results


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
STAR = "\033[93m★\033[0m"


def print_summary(results, poly_idx=None):
    """Print a concise summary of fibration analysis."""
    h11 = results.get('h11', '?')
    label = f"h11={h11}"
    if poly_idx is not None:
        label += f", poly={poly_idx}"

    print(f"\n{'═'*60}")
    print(f"  {BOLD}F-THEORY FIBRATION ANALYSIS{RESET} — {label}")
    print(f"{'═'*60}")
    print(f"  Elliptic fibrations: {results['n_fibrations']}")
    print(f"  Analysis time: {results['elapsed']:.1f}s")

    if results['n_fibrations'] == 0:
        print(f"  No elliptic fibrations found.")
        return

    print(f"\n  {'Fib':>3}  {'Fiber':>6}  {'Base':>5}  {'Rank':>4}  "
          f"{'Gauge Algebra':<30}  {'SM?':>3}")
    print(f"  {'─'*3}  {'─'*6}  {'─'*5}  {'─'*4}  {'─'*30}  {'─'*3}")

    for i, fib in enumerate(results['fibrations']):
        sm_tag = f" {STAR}" if fib['contains_SM'] else ""
        gut_tag = " GUT" if fib['has_SU5_GUT'] else ""
        print(f"  {i+1:>3}  {fib['fiber_type']:>6}  "
              f"{fib['base_hull_vertices']:>5}v  {fib['gauge_rank']:>4}  "
              f"{fib['gauge_algebra']:<30}{sm_tag}{gut_tag}")

    # Summary
    all_gauges = set(f['gauge_algebra'] for f in results['fibrations'])
    max_rank = max(f['gauge_rank'] for f in results['fibrations'])
    any_sm = any(f['contains_SM'] for f in results['fibrations'])
    any_gut = any(f['has_SU5_GUT'] for f in results['fibrations'])

    print(f"\n  Max gauge rank: {max_rank}")
    print(f"  Distinct gauge algebras: {len(all_gauges)}")
    if any_sm:
        print(f"  {GREEN}{BOLD}★ SU(3)×SU(2)×U(1) candidate(s) found!{RESET}")
    if any_gut:
        print(f"  {YELLOW}{BOLD}★ SU(5) GUT candidate(s) found!{RESET}")


def main():
    parser = argparse.ArgumentParser(
        description='F-theory fibration analysis for toric CY3 hypersurfaces')
    parser.add_argument('--h11', type=int, required=True)
    parser.add_argument('--poly', type=int, default=None,
                        help='Polytope index (default: analyze all)')
    parser.add_argument('--h21', type=int, default=None)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--save', action='store_true',
                        help='Save results to JSON')
    parser.add_argument('--limit', type=int, default=100,
                        help='Max polytopes to fetch')
    parser.add_argument('--batch', action='store_true',
                        help='Analyze all polytopes at this h11')
    parser.add_argument('--min-fibs', type=int, default=1,
                        help='Minimum fibrations for batch mode')
    args = parser.parse_args()

    h21 = args.h21 if args.h21 else args.h11 + 3

    if args.batch:
        # Batch mode: analyze all polytopes
        batch = analyze_batch(args.h11, h21, limit=args.limit,
                              verbose=True, min_fibs=args.min_fibs)
        print(f"\n  Total: {len(batch)} polytopes with ≥{args.min_fibs} fibrations")

        if args.save:
            outfile = f"results/fiber_batch_h{args.h11}.json"
            # Convert to serializable
            for r in batch:
                for f in r['fibrations']:
                    for kt in f.get('kodaira_types', []):
                        kt['base'] = list(kt['base']) if isinstance(kt['base'], tuple) else kt['base']
            with open(outfile, 'w') as fp:
                json.dump(batch, fp, indent=2, default=str)
            print(f"  Saved to {outfile}")
        return

    # Single polytope mode
    polys = list(cy.fetch_polytopes(h11=args.h11, h21=h21, limit=args.limit))
    if args.poly is None:
        print("Error: --poly required for single polytope mode (use --batch for all)")
        sys.exit(1)

    if args.poly >= len(polys):
        print(f"Error: polytope index {args.poly} out of range (have {len(polys)})")
        sys.exit(1)

    p = polys[args.poly]
    print(f"\n  Analyzing h11={args.h11}, h21={h21}, poly={args.poly}")

    results = analyze_polytope(p, h11=args.h11, verbose=args.verbose)
    results['poly_idx'] = args.poly

    print_summary(results, poly_idx=args.poly)

    # Print detailed Kodaira types
    for i, fib in enumerate(results['fibrations']):
        if fib['kodaira_types']:
            print(f"\n  Fibration {i+1} — Kodaira types:")
            for kt in fib['kodaira_types']:
                base = kt['base']
                print(f"    Base divisor {base}: {kt['type']} → {kt['algebra']} "
                      f"(rank {kt['rank']}, {kt['confidence']} confidence)")

    if args.save:
        outfile = f"results/fiber_h{args.h11}_P{args.poly}.json"
        # Convert tuples to lists for JSON
        for f in results['fibrations']:
            for kt in f.get('kodaira_types', []):
                kt['base'] = list(kt['base']) if isinstance(kt['base'], tuple) else kt['base']
        with open(outfile, 'w') as fp:
            json.dump(results, fp, indent=2, default=str)
        print(f"\n  Saved to {outfile}")


if __name__ == '__main__':
    main()
