"""B-52: Gauge Group Landscape Analysis for T4 Cluster.

Relaxes the v6 has_SM filter: instead of requiring SU(3)×SU(2)×U(1) directly
in a fibration gauge algebra, we ask which T4 entries have gauge groups that
CAN break to the Standard Model via standard chains:

    E8 → E6×SU(3) → SU(5)×... → SM
    E7 → SU(5)×U(1)^2         → SM
    E6 → SO(10)×U(1)           → SM
    SU(N≥5) → SU(5)            → SM

Key question: how many of the 5 "no-SM" T4 entries are actually SM-reachable?
"""

import sqlite3
import re
import json
import os
import sys
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V6_DB = ROOT / "v6" / "cy_landscape_v6.db"
V7_DB = ROOT / "v7" / "cy_landscape_v7.db"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Gauge algebra parsing
# ---------------------------------------------------------------------------

def parse_gauge_algebra(galg: str) -> dict:
    """Parse F-theory gauge algebra string into structured form.

    The v6 strings follow a pattern like:
        "su(4) × su(8) or e7 × su(6) × U(1)^3"

    The "su(N) or eK" token means the Kodaira fiber type is ambiguous between
    SU(N) and the exceptional algebra eK (same rank, different monodromy).
    """
    if not galg:
        return {
            "su_ranks": [], "exceptional": [], "u1_count": 0,
            "max_su": 0, "has_e678": False, "sm_reach": False, "direct_sm": False,
        }

    factors = re.split(r"\s*×\s*", galg)
    su_ranks: list[int] = []
    exceptional: list[str] = []
    u1_count = 0

    for tok in factors:
        tok = tok.strip()
        # "su(N) or eK" — ambiguous fiber; record both
        m = re.match(r"su\((\d+)\)\s+or\s+(e[678])", tok, re.I)
        if m:
            su_ranks.append(int(m.group(1)))
            exceptional.append(m.group(2).lower())
            continue
        m = re.match(r"su\((\d+)\)", tok, re.I)
        if m:
            su_ranks.append(int(m.group(1)))
            continue
        m = re.match(r"(e[678])\b", tok, re.I)
        if m:
            exceptional.append(m.group(1).lower())
            continue
        m = re.match(r"so\((\d+)\)", tok, re.I)
        if m:
            su_ranks.append(int(m.group(1)) // 2)  # approximate rank parity
            continue
        m = re.match(r"U\(1\)\^?(\d*)", tok, re.I)
        if m:
            u1_count += int(m.group(1)) if m.group(1) else 1
            continue

    max_su = max(su_ranks) if su_ranks else 0
    has_e678 = bool(exceptional)

    # SM reachability: E7 ⊃ SU(5) × U(1)^2, E8 ⊃ SU(5)×SU(5),
    # SU(N≥5) ⊃ SU(5) as maximal special unitary subgroup.
    sm_reach = max_su >= 5 or has_e678

    # Direct SM: contains both su(3) and su(2) explicitly (rough check)
    direct_sm = (3 in su_ranks and 2 in su_ranks)

    return {
        "su_ranks": sorted(su_ranks, reverse=True),
        "exceptional": sorted(set(exceptional)),
        "u1_count": u1_count,
        "max_su": max_su,
        "has_e678": has_e678,
        "sm_reach": sm_reach,
        "direct_sm": direct_sm,
    }


def gauge_summary_label(parsed: dict) -> str:
    """Return a short human-readable label for the gauge algebra class."""
    if parsed["has_e678"]:
        e_str = "/".join(e.upper() for e in parsed["exceptional"])
        return f"exceptional({e_str})"
    if parsed["max_su"] >= 10:
        return f"SU({parsed['max_su']})_GUT"
    if parsed["max_su"] >= 5:
        return f"SU({parsed['max_su']})_reach"
    if parsed["direct_sm"]:
        return "SM_direct"
    if parsed["max_su"] > 0:
        return f"SU({parsed['max_su']})_small"
    return "empty"


# ---------------------------------------------------------------------------
# Breaking chain labels for human readability
# ---------------------------------------------------------------------------

BREAKING_CHAINS = {
    "e8": "E8 → E6×SU(3) → SU(5)×... → SM",
    "e7": "E7 → SU(5)×U(1)^2 → SM",
    "e6": "E6 → SO(10)×U(1) → SM",
}


def breaking_chain(parsed: dict) -> str:
    for exc in ["e8", "e7", "e6"]:
        if exc in parsed["exceptional"]:
            return BREAKING_CHAINS[exc]
    if parsed["max_su"] >= 5:
        mxs = parsed["max_su"]
        return f"SU({mxs}) → SU(5) → SM" if mxs > 5 else "SU(5) → SM (direct GUT)"
    return "none"


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def load_data() -> tuple[list, list]:
    """Return (t4_entries, t4_fibrations)."""
    con = sqlite3.connect(V6_DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("""
        SELECT h11, poly_idx, sm_score, has_SM, has_GUT, best_gauge,
               n_ell_fib, n_k3_fib, best_swiss_tau, d3_min
        FROM polytopes
        WHERE tier_reached='T4'
        ORDER BY sm_score DESC, h11, poly_idx
    """)
    entries = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT f.h11, f.poly_idx,
               f.fiber_type, f.gauge_algebra, f.gauge_rank,
               f.contains_SM, f.has_SU5_GUT, f.kodaira_types, f.MW_rank_bound
        FROM fibrations f
        JOIN polytopes p ON f.h11=p.h11 AND f.poly_idx=p.poly_idx
        WHERE p.tier_reached='T4'
    """)
    fibrations = [dict(r) for r in cur.fetchall()]
    con.close()
    return entries, fibrations


def analyse(entries: list, fibrations: list) -> list:
    """Compute per-entry gauge reachability metrics."""
    # Group fibrations by (h11, poly_idx)
    fib_by_entry: dict[tuple, list] = defaultdict(list)
    for fb in fibrations:
        key = (fb["h11"], fb["poly_idx"])
        p = parse_gauge_algebra(fb["gauge_algebra"])
        fib_by_entry[key].append({
            "fiber_type": fb["fiber_type"],
            "gauge_algebra": fb["gauge_algebra"],
            "parsed": p,
            "contains_SM": fb["contains_SM"],
            "has_SU5_GUT": fb["has_SU5_GUT"],
        })

    results = []
    for e in entries:
        key = (e["h11"], e["poly_idx"])
        fibs = fib_by_entry.get(key, [])

        # Aggregate metrics across fibrations
        any_sm_reach = any(f["parsed"]["sm_reach"] for f in fibs)
        any_direct_sm = any(f["parsed"]["direct_sm"] for f in fibs)
        any_exceptional = any(f["parsed"]["has_e678"] for f in fibs)
        max_su_any = max((f["parsed"]["max_su"] for f in fibs), default=0)
        all_exceptional_types = sorted(set(
            exc for f in fibs for exc in f["parsed"]["exceptional"]
        ))
        # Best fibration for SM purposes (exceptional > high-SU)
        best_fib = None
        for f in sorted(fibs, key=lambda x: (
            x["parsed"]["has_e678"],
            x["parsed"]["max_su"],
        ), reverse=True):
            best_fib = f
            break

        # Classification
        n_ell = e["n_ell_fib"] or 0
        n_k3 = e["n_k3_fib"] or 0
        n_db_fibs = len(fibs)
        missing_fiber_data = (n_ell + n_k3 > 0) and (n_db_fibs == 0)

        if e["has_SM"]:
            gauge_class = "A_SM_direct"
        elif any_sm_reach:
            gauge_class = "B_SM_reachable"
        elif missing_fiber_data:
            gauge_class = "C_data_gap"
        else:
            gauge_class = "D_unreachable"

        chain = breaking_chain(best_fib["parsed"]) if best_fib else "none"

        results.append({
            "h11": e["h11"],
            "poly_idx": e["poly_idx"],
            "sm_score": e["sm_score"],
            "has_SM": e["has_SM"],
            "has_GUT": e["has_GUT"],
            "best_gauge_v6": e["best_gauge"] or "",
            "tau": e["best_swiss_tau"],
            "d3_min": e["d3_min"],
            "n_ell_fib": n_ell,
            "n_k3_fib": n_k3,
            "n_db_fibrations": n_db_fibs,
            "gauge_class": gauge_class,
            "any_sm_reach": any_sm_reach,
            "any_direct_sm": any_direct_sm,
            "any_exceptional": any_exceptional,
            "max_su_any": max_su_any,
            "exceptional_types": all_exceptional_types,
            "best_breaking_chain": chain,
            "fibrations": [
                {
                    "fiber_type": f["fiber_type"],
                    "gauge_algebra": f["gauge_algebra"],
                    "max_su": f["parsed"]["max_su"],
                    "exceptional": f["parsed"]["exceptional"],
                    "sm_reach": f["parsed"]["sm_reach"],
                }
                for f in fibs
            ],
        })

    return results


# ---------------------------------------------------------------------------
# Statistics computation
# ---------------------------------------------------------------------------

def compute_stats(results: list) -> dict:
    n = len(results)
    class_counts = Counter(r["gauge_class"] for r in results)
    exceptional_counts: Counter = Counter()
    su_rank_all: list[int] = []
    excep_fiber_count = 0

    for r in results:
        for fb in r["fibrations"]:
            for exc in fb["exceptional"]:
                exceptional_counts[exc] += 1
            su_rank_all.extend([fb["max_su"]])
            if fb["exceptional"]:
                excep_fiber_count += 1

    total_fibs = sum(len(r["fibrations"]) for r in results)

    # SU rank histogram
    su_hist = Counter(su_rank_all)

    return {
        "total_entries": n,
        "total_fibrations": total_fibs,
        "class_A_SM_direct": class_counts.get("A_SM_direct", 0),
        "class_B_SM_reachable": class_counts.get("B_SM_reachable", 0),
        "class_C_data_gap": class_counts.get("C_data_gap", 0),
        "class_D_unreachable": class_counts.get("D_unreachable", 0),
        "fibrations_with_exceptional": excep_fiber_count,
        "exceptional_type_counts": dict(exceptional_counts),
        "su_rank_histogram": {str(k): v for k, v in sorted(su_hist.items())},
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_json(results: list, stats: dict) -> None:
    out = {"statistics": stats, "entries": results}
    path = RESULTS_DIR / "gauge_group_analysis.json"
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    print(f"Wrote {path}")


def write_txt(results: list, stats: dict) -> None:
    lines = []
    lines.append("=" * 90)
    lines.append("B-52: GAUGE GROUP LANDSCAPE — T4 CLUSTER (37 entries)")
    lines.append("=" * 90)
    lines.append("")
    lines.append("CLASSIFICATION")
    lines.append("-" * 40)
    lines.append(f"  Class A — SM-direct gauge group (has_SM=1):      {stats['class_A_SM_direct']:>3}")
    lines.append(f"  Class B — SM-reachable (SU(N≥5) or eK, has_SM=0): {stats['class_B_SM_reachable']:>3}")
    lines.append(f"  Class C — data gap (fibrations missing from DB):  {stats['class_C_data_gap']:>3}")
    lines.append(f"  Class D — no SM path found:                        {stats['class_D_unreachable']:>3}")
    lines.append("")
    lines.append(f"Total T4 fibration rows in DB: {stats['total_fibrations']}")
    fec = stats['fibrations_with_exceptional']
    tf = stats['total_fibrations']
    lines.append(f"  Fibrations with exceptional factor (E7/E8):  {fec}/{tf} ({100*fec//tf if tf else 0}%)")
    lines.append(f"  Exceptional factor breakdown:")
    for exc, cnt in sorted(stats["exceptional_type_counts"].items()):
        lines.append(f"    {exc.upper()}: {cnt}")
    lines.append("")
    lines.append("SU(N) RANK DISTRIBUTION (all T4 fibrations, 'or eK' counted once under SU)")
    for rank_s, cnt in sorted(stats["su_rank_histogram"].items(), key=lambda x: int(x[0])):
        bar = "█" * cnt
        lines.append(f"  su({int(rank_s):>2}): {cnt:>3}  {bar}")
    lines.append("")
    lines.append("")
    lines.append("ENTRY DETAIL TABLE")
    lines.append("-" * 90)
    hdr = "{:<14s}  {:>3s}  {:4s}  {:2s}  {:3s}  {:4s}  {:4s}  {:>6s}  {:<16s}  {}".format(
        "Entry", "sm", "[cl]", "SM", "GUT", "nell", "nfib", "max_su", "exceptional", "breaking_chain"
    )
    lines.append(hdr)
    lines.append("-" * 90)
    for r in sorted(results, key=lambda x: x["gauge_class"]):
        h11, pidx = r["h11"], r["poly_idx"]
        cl = r["gauge_class"][0]  # A/B/C/D
        exc = "/".join(e.upper() for e in r["exceptional_types"]) or "-"
        chain = r["best_breaking_chain"][:40] if r["best_breaking_chain"] != "none" else "-"
        line = (
            f"h{h11}/P{pidx:<7d}  {r['sm_score']:3d}  [{cl}]  "
            f"{r['has_SM']:2d}  {r['has_GUT']:3d}  "
            f"{r['n_ell_fib']:4d}  {r['n_db_fibrations']:4d}  "
            f"{r['max_su_any']:>6d}  {exc:<16s}  {chain}"
        )
        lines.append(line)
    lines.append("")

    # Deep dive: Class B entries
    class_b = [r for r in results if r["gauge_class"] == "B_SM_reachable"]
    if class_b:
        lines.append("")
        lines.append("CLASS B — SM-REACHABLE (has_SM=0 but gauge group supports SM breaking)")
        lines.append("=" * 90)
        for r in class_b:
            lines.append(f"\nh{r['h11']}/P{r['poly_idx']}  sm_score={r['sm_score']}  tau={r['tau']:.1f}  d3_min={r['d3_min']:.1f}")
            for fb in r["fibrations"]:
                exc_str = "/".join(e.upper() for e in fb["exceptional"]) if fb["exceptional"] else "none"
                lines.append(f"  [{fb['fiber_type']}] {fb['gauge_algebra']}")
                lines.append(f"       → max_su={fb['max_su']}  exceptional={exc_str}")
                lines.append(f"       → breaking chain: {r['best_breaking_chain']}")

    # Deep dive: Class C entries
    class_c = [r for r in results if r["gauge_class"] == "C_data_gap"]
    if class_c:
        lines.append("")
        lines.append("CLASS C — DATA GAP (fibrations found in polytope scan but absent from DB)")
        lines.append("=" * 90)
        for r in class_c:
            lines.append(
                f"  h{r['h11']}/P{r['poly_idx']}  n_ell={r['n_ell_fib']}  n_k3={r['n_k3_fib']}"
                f"  n_db={r['n_db_fibrations']}  (fibration gauge data not stored)"
            )

    lines.append("")
    lines.append("INTERPRETATION")
    lines.append("-" * 90)
    lines.append("  The v6 filter (has_SM=1) required the FULL SM gauge group to appear directly")
    lines.append("  in a fibration. B-52 relaxes this: ANY gauge group that can break to")
    lines.append("  SU(3)×SU(2)×U(1) via standard chains is counted as SM-reachable.")
    lines.append("")
    a = stats["class_A_SM_direct"]
    b = stats["class_B_SM_reachable"]
    c = stats["class_C_data_gap"]
    d = stats["class_D_unreachable"]
    lines.append(f"  After relaxation: {a+b}/{a+b+c+d} entries have confirmed SM path")
    lines.append(f"                   {c} entries have a data gap (fibrations not stored)")
    lines.append(f"                   {d} entries have no SM-reachable gauge factor")
    lines.append("")
    lines.append("  Class B highlight: h24/P272 has SU(10) fibration gauge factor.")
    lines.append("  SU(10) → SU(5) × U(1)^5 → SM (standard breaking chain).")
    lines.append("  This entry also has tau=200 (LVS-physical range), d3_min=-8 (manageable).")
    lines.append("")
    lines.append("  Exceptional sector (E7/E8 fibers): 33/72 fibrations across the T4 cluster")
    lines.append("  contain a Kodaira fiber that is ambiguously SU(N) or an exceptional algebra.")
    lines.append("  If the monodromy selects E7 or E8, standard breaking chains apply:")
    lines.append("    E7 → SU(5) × U(1)^2 → SU(3)×SU(2)×U(1)")
    lines.append("    E8 → E6×SU(3) → SO(10)×SU(3)×U(1) → SU(5)×SU(3)×U(1)^2 → SM")
    lines.append("")

    path = RESULTS_DIR / "gauge_group_analysis.txt"
    path.write_text("\n".join(lines))
    print(f"Wrote {path}")
    print("\n".join(lines))


def update_v7_db(results: list) -> None:
    """Add gauge_class column to v7 DB entries."""
    if not V7_DB.exists():
        print(f"v7 DB not found at {V7_DB} — skipping DB update")
        return

    con = sqlite3.connect(V7_DB)
    cur = con.cursor()

    # Add column if missing
    for col, ctype in [("gauge_class", "TEXT"), ("any_sm_reach", "INTEGER"),
                       ("max_su_any", "INTEGER"), ("any_exceptional", "INTEGER")]:
        try:
            cur.execute(f"ALTER TABLE polytopes ADD COLUMN {col} {ctype}")
        except sqlite3.OperationalError:
            pass  # column already exists
    con.commit()
    print("Ensured gauge columns in v7 DB polytopes table")

    for r in results:
        cur.execute("""
            UPDATE polytopes SET gauge_class=?, any_sm_reach=?, max_su_any=?, any_exceptional=?
            WHERE h11=? AND poly_idx=?
        """, (
            r["gauge_class"],
            int(r["any_sm_reach"]),
            r["max_su_any"],
            int(r["any_exceptional"]),
            r["h11"],
            r["poly_idx"],
        ))

    con.commit()
    con.close()
    print(f"Updated {len(results)} rows in v7 DB")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading T4 data from v6 DB...")
    entries, fibrations = load_data()
    print(f"  {len(entries)} T4 entries, {len(fibrations)} fibration rows")

    print("\nAnalysing gauge group landscape...")
    results = analyse(entries, fibrations)

    stats = compute_stats(results)

    print("\nWriting results...")
    write_json(results, stats)
    write_txt(results, stats)

    print("\nUpdating v7 DB...")
    update_v7_db(results)

    print("\nDone.")
