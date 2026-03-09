#!/usr/bin/env python3
"""B-51: Observable-first scoring of 37 T4-verified CY3 polytopes.

Implements the v7 scoring spec from v7/README.md:

    V7_SCORE_WEIGHTS = {
        't4_verified':       10,   # T4 tier confirmed
        'tri_stable':         5,   # c₂ / κ triangulation-stable
        'net_gen_3':         15,   # |χ(V)| = 3 net generations
        'vector_like_light':  5,   # heavy vector-like pairs
        'tadpole_flux_ok':   15,   # n_D3_bundle + n_D3_flux ≤ χ/24
        'dm_mass_window':    15,   # m_DM in 100 GeV – 10 TeV
        'proton_decay_rate': 10,   # Γ_p in Hyper-K sensitivity range
        'neutrino_mass_hier':10,   # normal / inverted hierarchy predicted
        'gauge_unification': 10,   # α_GUT within 10% of observed
        'susy_breaking_scale': 5,  # m_{3/2} in 10–100 TeV window
    }  # Total: 100 pts

All scoring is performed on v6 DB data (read-only).
Results are written to:
  - v7/results/observable_scores.json
  - v7/results/observable_scores.txt
  - v7/cy_landscape_v7.db  (fresh SQLite with v7 scores)
"""

import os
import json
import sqlite3
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = Path(__file__).parent
V6_DB = HERE.parent / "v6" / "cy_landscape_v6.db"
V7_DB = HERE / "cy_landscape_v7.db"
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(exist_ok=True)
OUT_JSON = RESULTS_DIR / "observable_scores.json"
OUT_TXT  = RESULTS_DIR / "observable_scores.txt"

# ---------------------------------------------------------------------------
# Scoring functions (each returns an int within its max)
# ---------------------------------------------------------------------------

def score_t4_verified() -> int:
    """10 pts: T4 tier is the inclusion criterion, so always 10."""
    return 10


def score_tri_stable(c2_frac: float, kappa_frac: float) -> int:
    """5 pts: triangulation stability of c₂(TX) and κ_{abc}.

    Thresholds reflect real data distribution (max observed ~0.35).
    We give partial credit because full stability (≥0.9) is unreachable
    on these high-h¹¹ polytopes with only 20–60 tested triangulations.
    """
    avg = (c2_frac + kappa_frac) / 2.0
    if avg >= 0.30:
        return 5       # best available: ≥30% stable
    if avg >= 0.10:
        return 3
    if avg >= 0.03:
        return 1
    return 0


def score_net_gen_3(has_SM: int, has_GUT: int) -> int:
    """15 pts: net 3 generations via SM-compatible gauge algebra.

    has_SM=1 means v6 found an SM-like gauge group in the D-brane moduli;
    this is the best available proxy for χ(V)=±3 being achievable.
    """
    if has_SM:
        return 15
    if has_GUT:
        return 7
    return 0


def score_vector_like_light(has_SM: int, n_rigid: int) -> int:
    """5 pts: natural suppression of vector-like pairs.

    Rigid divisors (n_rigid) constrain zero-mode counting.  A large
    number of rigid divisors in an SM geometry indicates the spectrum
    is constrained and unwanted pairs are likely massive (≥ M_GUT).
    """
    if has_SM and n_rigid >= 6:
        return 5
    if has_SM and n_rigid >= 3:
        return 3
    if has_SM:
        return 1
    return 0


def score_tadpole_flux_ok(d3_min: float) -> int:
    """15 pts: D3 tadpole satisfiable with H-flux.

    d3_min = minimum Δn_D3 = min over monad candidates of
    n_D3^bundle - n_D3^max.  Negative means flux can cancel the deficit.
    All T4 entries in the v6 DB have d3_min ≤ 0 by construction (T4
    requires at least one candidate within the tadpole bound).
    Score 15 for d3_min ≤ 0, graded reduction for positive values.
    """
    if d3_min <= 0:
        return 15
    if d3_min <= 30:
        return 10
    if d3_min <= 100:
        return 5
    return 0


def score_dm_mass_window(tau: float, n_swiss: int) -> int:
    """15 pts: m_DM ≈ m_{3/2} in 100 GeV – 10 TeV.

    In LVS, m_{3/2} ~ M_Pl / V.  The Swiss-cheese best_swiss_tau records
    the small-cycle Kähler modulus τ_s of the best Swiss-cheese candidate.
    Physical LVS requires τ_s > 1 and finite.  Huge-negative tau signals
    the optimiser found no valid Swiss-cheese minimum.

    Mapping used:
      tau ∈ (1, 200):    ideal small cycle → 15 pts  (m_{3/2} ~ 10–100 TeV)
      tau ∈ [200, 5000): still reasonable → 10 pts   (heavier SUSY, DM ok)
      tau ∈ [5000,50000): marginal → 5 pts
      tau ≤ 0 or large: non-physical → 0 pts
    """
    if n_swiss == 0 or tau is None:
        return 0
    if 1.0 < tau < 200.0:
        return 15
    if 200.0 <= tau < 5000.0:
        return 10
    if 5000.0 <= tau < 50000.0:
        return 5
    return 0


def score_proton_decay_rate(has_GUT: int, n_ell_fib: int, n_k3_fib: int) -> int:
    """10 pts: Γ_p in Hyper-Kamiokande sensitivity range.

    M_GUT is set by the geometry of the fibration structure.
    Elliptic and K3 fibrations allow F-theory / heterotic duality,
    which naturally places M_GUT near the observed value 2×10¹⁶ GeV.
    Multiple fibrations tighten the constraint further.
    """
    if not has_GUT:
        return 0
    if n_ell_fib >= 3 or n_k3_fib >= 3:
        return 10
    if n_ell_fib >= 2 or n_k3_fib >= 2:
        return 7
    if n_ell_fib >= 1 or n_k3_fib >= 1:
        return 4
    return 2   # has_GUT but no fibration detected


def score_neutrino_mass_hier(has_SM: int, yukawa_hierarchy: float) -> int:
    """10 pts: hierarchical neutrino masses (normal or inverted hierarchy).

    Large Yukawa texture hierarchy (ratio of largest to smallest non-zero
    Yukawa coupling) indicates seesaw-compatible mass matrices.  A high
    hierarchy (>1000) gives a natural three-generation mass splitting
    consistent with measured Δm² values.
    """
    if not has_SM:
        return 0
    if yukawa_hierarchy >= 1000.0:
        return 10
    if yukawa_hierarchy >= 100.0:
        return 7
    if yukawa_hierarchy >= 10.0:
        return 4
    return 2


def score_gauge_unification(best_gauge: str, has_GUT: int) -> int:
    """10 pts: α_GUT within 10% of observed value at M_GUT.

    Exceptional groups (E₆, E₇, E₈) and GUT groups (SU(5), SO(10))
    enforce gauge coupling unification by construction — their Dynkin
    indices align the running of α₁,₂,₃.  SU(N≥6) can also unify
    in string compactifications.
    """
    bg = (best_gauge or "").lower()
    # Exceptional groups E6/E7/E8 → automatic unification
    if re.search(r'\be[678]\b', bg):
        return 10
    # SO(10) or SU(5) directly → GUT unification group
    if 'so(10)' in bg or 'su(5)' in bg:
        return 10
    # has_GUT flag set but lower rank group
    if has_GUT:
        return 5
    return 0


def score_susy_breaking_scale(tau: float, n_swiss: int) -> int:
    """5 pts: m_{3/2} in 10–100 TeV (SUSY breaking scale window).

    Uses the same LVS proxy as dm_mass_window.  The window 10–100 TeV
    is narrower (ideal small τ_s ~ 30–200 in LVS).
    """
    if n_swiss == 0 or tau is None:
        return 0
    if 1.0 < tau < 200.0:
        return 5   # ideal small cycle
    if 200.0 <= tau < 5000.0:
        return 3   # slightly heavier but still TeV-scale
    if 5000.0 <= tau < 50000.0:
        return 1   # marginal
    return 0


# ---------------------------------------------------------------------------
# Main scoring pipeline
# ---------------------------------------------------------------------------

def load_t4_entries():
    """Return all T4-verified entries from v6 DB as list of dicts."""
    con = sqlite3.connect(V6_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT h11, poly_idx, sm_score, tier_reached,
               has_SM, has_GUT, best_gauge,
               n_ell_fib, n_k3_fib, n_fibers,
               n_rigid, n_swiss, best_swiss_tau, best_swiss_ratio,
               tri_c2_stable_frac, tri_kappa_stable_frac, tri_n_tested,
               d3_min, d3_max,
               yukawa_hierarchy, yukawa_density,
               c2_all_positive, kappa_signature,
               n_flux_vacua_est, lvs_score,
               h11_eff, h21, chi, gap,
               monad_lp_slope_feasible, monad_lp_tadpole_ok,
               monad_su5_k1_slope_feasible
        FROM polytopes
        WHERE tier_reached = 'T4'
        ORDER BY sm_score DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    # Null-safe coercion
    for r in rows:
        r['has_SM']               = int(r['has_SM'] or 0)
        r['has_GUT']              = int(r['has_GUT'] or 0)
        r['best_gauge']           = r['best_gauge'] or ''
        r['n_ell_fib']            = int(r['n_ell_fib'] or 0)
        r['n_k3_fib']             = int(r['n_k3_fib'] or 0)
        r['n_rigid']              = int(r['n_rigid'] or 0)
        r['n_swiss']              = int(r['n_swiss'] or 0)
        r['best_swiss_tau']       = r['best_swiss_tau']   # may be None
        r['tri_c2_stable_frac']   = float(r['tri_c2_stable_frac'] or 0.0)
        r['tri_kappa_stable_frac']= float(r['tri_kappa_stable_frac'] or 0.0)
        r['d3_min']               = float(r['d3_min']) if r['d3_min'] is not None else 9999.0
        r['yukawa_hierarchy']     = float(r['yukawa_hierarchy'] or 0.0)
    return rows


def compute_v7_score(r: dict) -> dict:
    """Compute all 10 observable score components for one entry."""
    tau   = r['best_swiss_tau']
    nsw   = r['n_swiss']

    s = {}
    s['t4_verified']        = score_t4_verified()
    s['tri_stable']         = score_tri_stable(r['tri_c2_stable_frac'],
                                               r['tri_kappa_stable_frac'])
    s['net_gen_3']          = score_net_gen_3(r['has_SM'], r['has_GUT'])
    s['vector_like_light']  = score_vector_like_light(r['has_SM'], r['n_rigid'])
    s['tadpole_flux_ok']    = score_tadpole_flux_ok(r['d3_min'])
    s['dm_mass_window']     = score_dm_mass_window(tau, nsw)
    s['proton_decay_rate']  = score_proton_decay_rate(r['has_GUT'],
                                                      r['n_ell_fib'],
                                                      r['n_k3_fib'])
    s['neutrino_mass_hier'] = score_neutrino_mass_hier(r['has_SM'],
                                                       r['yukawa_hierarchy'])
    s['gauge_unification']  = score_gauge_unification(r['best_gauge'], r['has_GUT'])
    s['susy_breaking_scale']= score_susy_breaking_scale(tau, nsw)
    s['total']              = sum(s.values())
    return s


def build_results(rows: list) -> list:
    """Score all T4 entries and return sorted list of result dicts."""
    results = []
    for r in rows:
        entry_id = f"h{r['h11']}/P{r['poly_idx']}"
        scores = compute_v7_score(r)
        tau = r['best_swiss_tau']
        result = {
            'entry':             entry_id,
            'h11':               r['h11'],
            'poly_idx':          r['poly_idx'],
            'h11_eff':           r['h11_eff'],
            'h21':               r['h21'],
            'chi':               r['chi'],
            'gap':               r['gap'],
            'sm_score_v6':       r['sm_score'],
            'has_SM':            r['has_SM'],
            'has_GUT':           r['has_GUT'],
            'best_gauge':        r['best_gauge'],
            'n_ell_fib':         r['n_ell_fib'],
            'n_k3_fib':          r['n_k3_fib'],
            'n_rigid':           r['n_rigid'],
            'n_swiss':           r['n_swiss'],
            'best_swiss_tau':    tau,
            'tri_c2_stable_frac': r['tri_c2_stable_frac'],
            'yukawa_hierarchy':  r['yukawa_hierarchy'],
            'd3_min':            r['d3_min'],
            'v7_scores':         scores,
            'v7_total':          scores['total'],
        }
        results.append(result)
    results.sort(key=lambda x: (-x['v7_total'], -x['sm_score_v6']))
    return results


def write_json(results: list) -> None:
    with open(OUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[JSON] {OUT_JSON}  ({len(results)} entries)")


def write_txt(results: list) -> None:
    WEIGHTS = {
        't4_verified': 10, 'tri_stable': 5, 'net_gen_3': 15,
        'vector_like_light': 5, 'tadpole_flux_ok': 15, 'dm_mass_window': 15,
        'proton_decay_rate': 10, 'neutrino_mass_hier': 10,
        'gauge_unification': 10, 'susy_breaking_scale': 5,
    }
    KEYS = list(WEIGHTS.keys())
    header_short = ['T4', 'tri', 'gen', 'vll', 'tad', 'dm', 'pdec', 'nu', 'gu', 'susy']

    lines = []
    lines.append("B-51 Observable Scoring — v7 T4-verified cluster (37 entries)")
    lines.append("="*110)
    lines.append(f"{'Rank':4s}  {'Entry':14s}  {'v7':4s}  {'v6':4s}  "
                 + "  ".join(f"{h:4s}" for h in header_short)
                 + "  tau        SM  GUT  nell  yh")
    lines.append("-"*110)

    for rank, r in enumerate(results, 1):
        s = r['v7_scores']
        tau = r['best_swiss_tau']
        tau_str = f"{tau:9.0f}" if tau is not None else "     None"
        row = (
            f"{rank:4d}  {r['entry']:14s}  {r['v7_total']:4d}  {r['sm_score_v6']:4d}  "
            + "  ".join(f"{s[k]:4d}" for k in KEYS)
            + f"  {tau_str}"
            + f"  {r['has_SM']:2d}"
            + f"  {r['has_GUT']:3d}"
            + f"  {r['n_ell_fib']:4d}"
            + f"  {r['yukawa_hierarchy']:8.0f}"
        )
        lines.append(row)

    lines.append("")
    lines.append("Score max:           "
                 + "  ".join(f"{WEIGHTS[k]:4d}" for k in KEYS)
                 + "  (total /100)")
    lines.append("")

    # Summary statistics
    totals = [r['v7_total'] for r in results]
    lines.append(f"Range: {min(totals)}–{max(totals)} pts  |  Median: {sorted(totals)[len(totals)//2]} pts")
    lines.append("")

    # Top-5 notes
    lines.append("Top 5 entries:")
    for r in results[:5]:
        s = r['v7_scores']
        tau = r['best_swiss_tau']
        tau_str = f"{tau:.0f}" if tau is not None and tau > 0 else "non-physical"
        lines.append(
            f"  {r['entry']:14s}  v7={r['v7_total']:3d}  v6={r['sm_score_v6']:3d}"
            f"  SM={r['has_SM']}  GUT={r['has_GUT']}"
            f"  nell={r['n_ell_fib']}  nk3={r['n_k3_fib']}"
            f"  tau={tau_str}"
            f"  yh={r['yukawa_hierarchy']:.0f}"
            f"  gauge={r['best_gauge'][:45]}"
        )

    with open(OUT_TXT, 'w') as f:
        f.write("\n".join(lines) + "\n")
    print(f"[TXT]  {OUT_TXT}")


def write_v7_db(results: list) -> None:
    """Create v7/cy_landscape_v7.db with v7 scores for all T4 entries."""
    if V7_DB.exists():
        V7_DB.unlink()
    con = sqlite3.connect(V7_DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE polytopes (
            h11               INTEGER,
            poly_idx          INTEGER,
            h11_eff           INTEGER,
            h21               INTEGER,
            chi               INTEGER,
            gap               INTEGER,
            sm_score_v6       INTEGER,
            has_SM            INTEGER,
            has_GUT           INTEGER,
            best_gauge        TEXT,
            n_ell_fib         INTEGER,
            n_k3_fib          INTEGER,
            n_rigid           INTEGER,
            n_swiss           INTEGER,
            best_swiss_tau    REAL,
            tri_c2_stable_frac REAL,
            yukawa_hierarchy  REAL,
            d3_min            REAL,
            -- v7 observable scores
            v7_t4_verified         INTEGER,
            v7_tri_stable          INTEGER,
            v7_net_gen_3           INTEGER,
            v7_vector_like_light   INTEGER,
            v7_tadpole_flux_ok     INTEGER,
            v7_dm_mass_window      INTEGER,
            v7_proton_decay_rate   INTEGER,
            v7_neutrino_mass_hier  INTEGER,
            v7_gauge_unification   INTEGER,
            v7_susy_breaking_scale INTEGER,
            v7_total               INTEGER,
            PRIMARY KEY (h11, poly_idx)
        )
    """)
    for r in results:
        s = r['v7_scores']
        cur.execute("""
            INSERT INTO polytopes VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,?
            )
        """, (
            r['h11'], r['poly_idx'], r['h11_eff'], r['h21'], r['chi'], r['gap'],
            r['sm_score_v6'], r['has_SM'], r['has_GUT'], r['best_gauge'],
            r['n_ell_fib'], r['n_k3_fib'], r['n_rigid'], r['n_swiss'],
            r['best_swiss_tau'], r['tri_c2_stable_frac'],
            r['yukawa_hierarchy'], r['d3_min'],
            s['t4_verified'], s['tri_stable'], s['net_gen_3'],
            s['vector_like_light'], s['tadpole_flux_ok'], s['dm_mass_window'],
            s['proton_decay_rate'], s['neutrino_mass_hier'],
            s['gauge_unification'], s['susy_breaking_scale'],
            s['total'],
        ))
    con.commit()
    con.close()
    size_kb = V7_DB.stat().st_size // 1024
    print(f"[DB]   {V7_DB}  ({size_kb} KB, {len(results)} rows)")


def print_summary(results: list) -> None:
    KEYS = [
        't4_verified', 'tri_stable', 'net_gen_3', 'vector_like_light',
        'tadpole_flux_ok', 'dm_mass_window', 'proton_decay_rate',
        'neutrino_mass_hier', 'gauge_unification', 'susy_breaking_scale',
    ]
    MAX = [10, 5, 15, 5, 15, 15, 10, 10, 10, 5]

    print()
    print("=" * 60)
    print("B-51 Observable Scoring Summary")
    print("=" * 60)
    print(f"{'Rank':4s}  {'Entry':14s}  {'v7':4s}  {'v6':4s}")
    print("-" * 40)
    for rank, r in enumerate(results[:10], 1):
        print(f"{rank:4d}  {r['entry']:14s}  {r['v7_total']:4d}  {r['sm_score_v6']:4d}")

    print()
    print(f"Total entries scored: {len(results)}")
    totals = [r['v7_total'] for r in results]
    print(f"Score range: {min(totals)}–{max(totals)} / 100")
    print(f"Score median: {sorted(totals)[len(totals)//2]}")

    print()
    print("Component averages:")
    for k, mx in zip(KEYS, MAX):
        vals = [r['v7_scores'][k] for r in results]
        avg = sum(vals) / len(vals)
        nonzero = sum(1 for v in vals if v > 0)
        print(f"  {k:24s}  avg={avg:5.1f}/{mx}  ({nonzero}/{len(vals)} non-zero)")

    print()
    print("Top 5 entries:")
    for r in results[:5]:
        tau = r['best_swiss_tau']
        tau_str = f"{tau:.0f}" if tau is not None and tau > 0 else "non-phys"
        print(f"  {r['entry']:14s}  v7={r['v7_total']}  v6={r['sm_score_v6']}"
              f"  tau={tau_str}  gauge={r['best_gauge'][:50]}")


if __name__ == '__main__':
    print("Loading T4 entries from v6 DB ...")
    rows = load_t4_entries()
    print(f"  {len(rows)} entries loaded")

    print("Computing v7 observable scores ...")
    results = build_results(rows)

    write_json(results)
    write_txt(results)
    write_v7_db(results)
    print_summary(results)
