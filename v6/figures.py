#!/usr/bin/env python3
"""
figures.py — Generate all 8 paper figures from v6 production database.

Figures:
  1. KS population bar chart by h¹¹ (chi=-6, log scale)
  2. Screening funnel diagram
  3. Score histogram (T3-verified entries, bins of 5)
  4. Score vs h¹¹ scatter (colored by has_SM)
  5. Max sm_score vs h¹¹ — boundary collapse plot (KEY RESULT)
  6. h¹¹ histogram of top-37
  7. Score vs n_clean scatter (≥70 tier, champion annotated)
  8. T4 stability fractions (c₂/κ distributions for top-37)

Usage:
    cd /workspaces/cytools_project/v6
    python3 figures.py [--db cy_landscape_v6.db] [--out-dir results/figures]

Output: PNG files in results/figures/, one per figure.
"""

import argparse
import os
import sqlite3
import sys

import matplotlib
matplotlib.use("Agg")  # headless — no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":    "DejaVu Serif",
    "font.size":      11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "figure.dpi":     150,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

CHAMPION = (26, 11670, 89)  # (h11, poly_idx, score)


# ══════════════════════════════════════════════════════════════════════════════
#  Data loaders
# ══════════════════════════════════════════════════════════════════════════════

def load_ks_population():
    """Return {h11: count} for all chi=-6 polytopes in the full KS DB."""
    # Hardcoded from KS database (6,122,441 total, chi=-6)
    # Source: http://hep.itp.tuwien.ac.at/~kreuzer/CY/ + local index
    data = {
        13: 4, 14: 33, 15: 425, 16: 2190, 17: 5292, 18: 22830, 19: 39920,
        20: 66752, 21: 97608, 22: 108888, 23: 225965, 24: 438438, 25: 424218,
        26: 411864, 27: 533376, 28: 545600, 29: 421632, 30: 411013,
        31: 320802, 32: 275244, 33: 232880, 34: 209560, 35: 174572, 36: 151416,
        37: 129224, 38: 110316, 39: 88352, 40: 76376,
        # tail (h41-119: approx, total ~327K)
        41: 60832, 42: 50816, 43: 42624, 44: 35152, 45: 28832, 50: 13216,
        55: 5824, 60: 2336, 70: 512, 80: 128, 90: 32, 100: 8, 119: 1,
    }
    return data


def get_db(db_path):
    return sqlite3.connect(db_path)


def load_h11_stats(con):
    """Per-h11 scanned count, scored count, max sm_score."""
    rows = con.execute("""
        SELECT h11,
               COUNT(*) as n_stored,
               SUM(CASE WHEN sm_score IS NOT NULL THEN 1 ELSE 0 END) as n_scored,
               MAX(sm_score) as max_score
        FROM polytopes
        WHERE h11 BETWEEN 13 AND 42
        GROUP BY h11 ORDER BY h11
    """).fetchall()
    return rows


def load_t3_scores(con):
    """All T3/T4 entries: h11, sm_score, has_SM, n_clean."""
    rows = con.execute("""
        SELECT h11, sm_score, has_SM, n_clean
        FROM polytopes
        WHERE sm_score >= 70 AND tier_reached IN ('T3','T4')
        ORDER BY sm_score DESC
    """).fetchall()
    return rows


def load_top37(con):
    """Top 37 (sm_score >= 80): h11, sm_score, tri_c2, tri_kappa."""
    rows = con.execute("""
        SELECT h11, poly_idx, sm_score, n_clean, has_SM, has_GUT,
               tri_c2_stable_frac, tri_kappa_stable_frac
        FROM polytopes WHERE sm_score >= 80
        ORDER BY sm_score DESC, n_clean DESC
    """).fetchall()
    return rows


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 1: KS population bar chart
# ══════════════════════════════════════════════════════════════════════════════

def figure1_ks_population(out_dir):
    ks = load_ks_population()
    h11s = sorted(k for k in ks if k <= 60)
    counts = [ks[h] for h in h11s]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(h11s, counts, width=0.8, color="#3A7DBF", alpha=0.85, linewidth=0)
    ax.set_yscale("log")
    ax.set_xlabel(r"$h^{11}$")
    ax.set_ylabel("Number of polytopes")
    ax.set_title(r"KS database: $\chi = -6$ polytopes by $h^{11}$")
    ax.axvspan(13, 28.5, alpha=0.08, color="green", label="Productive region (h¹¹ ≤ 28)")
    ax.axvline(28.5, color="green", lw=1.2, ls="--", alpha=0.7)
    ax.legend()
    ax.set_xlim(11, 62)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig1_ks_population.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 2: Screening funnel
# ══════════════════════════════════════════════════════════════════════════════

def figure2_funnel(out_dir):
    stages = [
        ("KS χ=−6 polytopes",     6_122_441),
        ("Scanned (h13–h40)",      3_113_640),
        ("T2-scored",                 54_931),
        ("T3-verified (≥70)",            965),
        ("T4-verified (≥80)",             37),
        ("Global optimum",                 1),
    ]
    labels = [s[0] for s in stages]
    values = [s[1] for s in stages]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = plt.cm.Blues_r(np.linspace(0.2, 0.7, len(stages)))
    bar_heights = [max(np.log10(v), 0) for v in values]
    y_pos = range(len(stages))

    bars = ax.barh(list(y_pos), bar_heights, color=colors, height=0.6, linewidth=0.5, edgecolor="white")
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("log₁₀(count)")
    ax.set_title("Screening funnel — chi=−6 KS landscape (v6 pipeline)")
    ax.invert_yaxis()

    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f"{val:,}", va="center", fontsize=9)

    fig.tight_layout()
    path = os.path.join(out_dir, "fig2_funnel.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 3: Score histogram
# ══════════════════════════════════════════════════════════════════════════════

def figure3_score_histogram(con, out_dir):
    rows = load_t3_scores(con)
    scores = [r[1] for r in rows if r[1] is not None]

    fig, ax = plt.subplots(figsize=(8, 4))
    bins = range(min(scores), max(scores) + 6, 5)
    n, _, patches = ax.hist(scores, bins=bins, color="#3A7DBF", alpha=0.85,
                            edgecolor="white", linewidth=0.5)
    # Highlight ≥80 tier
    for patch, left in zip(patches, bins):
        if left >= 80:
            patch.set_facecolor("#D62728")
            patch.set_alpha(0.9)

    ax.set_xlabel("sm_score (100-point composite)")
    ax.set_ylabel("Count (T3-verified entries)")
    ax.set_title(f"Score distribution — {len(scores)} T3-verified polytopes")
    ax.axvline(80, color="#D62728", lw=1.5, ls="--", label="≥80 tier (37 entries, red)")
    ax.axvline(89, color="black", lw=1.5, ls=":", label="Champion h26/P11670 (89)")
    ax.legend()
    fig.tight_layout()
    path = os.path.join(out_dir, "fig3_score_histogram.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 4: Score vs h¹¹ scatter
# ══════════════════════════════════════════════════════════════════════════════

def figure4_score_vs_h11(con, out_dir):
    rows = load_t3_scores(con)
    h11s   = np.array([r[0] for r in rows])
    scores = np.array([r[1] for r in rows])
    has_sm = np.array([r[2] for r in rows])

    fig, ax = plt.subplots(figsize=(9, 5))
    # Jitter x slightly for readability
    jitter = np.random.default_rng(42).uniform(-0.25, 0.25, len(h11s))

    ax.scatter(h11s[has_sm == 0] + jitter[has_sm == 0], scores[has_sm == 0],
               alpha=0.4, s=15, color="#777", label="No SM gauge content", zorder=2)
    ax.scatter(h11s[has_sm == 1] + jitter[has_sm == 1], scores[has_sm == 1],
               alpha=0.6, s=20, color="#3A7DBF", label="SM gauge content", zorder=3)

    # Champion star
    ax.scatter([26], [89], marker="*", s=250, color="#D62728", zorder=5,
               label="Champion h26/P11670 (89)")

    ax.axhline(80, color="#D62728", lw=1.2, ls="--", alpha=0.6, label="Score=80 threshold")
    ax.set_xlabel(r"$h^{11}$")
    ax.set_ylabel("sm_score")
    ax.set_title("Score vs h¹¹ — all 965 T3-verified entries")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig4_score_vs_h11.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 5: Max score vs h¹¹ — boundary collapse (KEY RESULT)
# ══════════════════════════════════════════════════════════════════════════════

def figure5_boundary_collapse(con, out_dir):
    stats = load_h11_stats(con)

    h11s   = [r[0] for r in stats]
    max_sm = [r[3] if r[3] is not None else 0 for r in stats]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(h11s, max_sm, "o-", color="#3A7DBF", lw=2, ms=6, label="Max sm_score")
    ax.fill_between(h11s, max_sm, alpha=0.15, color="#3A7DBF")

    # Mark productive boundary
    ax.axvline(28.5, color="#D62728", lw=1.5, ls="--",
               label="Productive boundary (h¹¹=28)")
    ax.axhline(80, color="gray", lw=1, ls=":", alpha=0.7, label="Score=80 threshold")

    # Annotate collapse
    ax.annotate("§29: 5.45M polytopes\nscanned → 0 entries ≥70",
                xy=(30.5, 25), xytext=(34, 55),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
                fontsize=9, color="#D62728")

    # Champion marker
    ax.scatter([26], [89], marker="*", s=200, color="#D62728", zorder=5,
               label="Champion h26/P11670")

    ax.set_xlabel(r"$h^{11}$")
    ax.set_ylabel("Max sm_score in h¹¹ slice")
    ax.set_title("Landscape boundary: score ceiling collapses past h¹¹=28")
    ax.set_xlim(12, max(h11s) + 1)
    ax.set_ylim(-2, 95)
    ax.legend(fontsize=9)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig5_boundary_collapse.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 6: h¹¹ histogram of top-37
# ══════════════════════════════════════════════════════════════════════════════

def figure6_top37_h11(con, out_dir):
    rows = load_top37(con)
    h11s = [r[0] for r in rows]

    unique_h11 = sorted(set(h11s))
    counts_sm = []
    counts_nosm = []
    for h in unique_h11:
        sm  = sum(1 for r in rows if r[0] == h and r[4] == 1)
        nsm = sum(1 for r in rows if r[0] == h and r[4] == 0)
        counts_sm.append(sm)
        counts_nosm.append(nsm)

    x = np.arange(len(unique_h11))
    w = 0.5
    fig, ax = plt.subplots(figsize=(8, 4))
    b1 = ax.bar(x, counts_sm, width=w, color="#3A7DBF", alpha=0.9, label="SM gauge content")
    b2 = ax.bar(x, counts_nosm, width=w, bottom=counts_sm, color="#AAC4E0", alpha=0.8,
                label="No SM gauge content")

    ax.set_xticks(x)
    ax.set_xticklabels([f"h{h}" for h in unique_h11])
    ax.set_ylabel("Count")
    ax.set_title("Top-37 (score ≥ 80, T4-verified): distribution by h¹¹")
    ax.legend()
    for xi, sm, nsm in zip(x, counts_sm, counts_nosm):
        tot = sm + nsm
        if tot > 0:
            ax.text(xi, tot + 0.1, str(tot), ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig6_top37_h11.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 7: Score vs n_clean scatter
# ══════════════════════════════════════════════════════════════════════════════

def figure7_score_vs_nclean(con, out_dir):
    rows = load_t3_scores(con)
    scores  = np.array([r[1] for r in rows if r[1] is not None and r[3] is not None])
    ncleans = np.array([r[3] for r in rows if r[1] is not None and r[3] is not None])
    has_sm  = np.array([r[2] for r in rows if r[1] is not None and r[3] is not None])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(ncleans[has_sm == 0], scores[has_sm == 0],
               alpha=0.3, s=14, color="#999", label="No SM")
    ax.scatter(ncleans[has_sm == 1], scores[has_sm == 1],
               alpha=0.5, s=18, color="#3A7DBF", label="SM")
    # Top37 highlighted
    rows37 = load_top37(con)
    s37 = [r[2] for r in rows37]
    n37 = [r[3] for r in rows37]
    ax.scatter(n37, s37, alpha=0.9, s=40, color="#D62728", zorder=4, label="Top-37 (score ≥80)")

    # Champion
    ax.scatter([22], [89], marker="*", s=280, color="black", zorder=5,
               label="Champion h26/P11670")
    # n_clean record (h22/P682, score=85, n_clean=84)
    ax.annotate("h22/P682\nn_clean=84", xy=(84, 85), xytext=(65, 80),
                arrowprops=dict(arrowstyle="->", lw=1), fontsize=8)

    ax.set_xlabel("n_clean (clean U(1) bundles with h⁰=3, h¹=h²=h³=0)")
    ax.set_ylabel("sm_score")
    ax.set_title("Score vs clean-bundle count — 965 T3-verified entries")
    ax.legend(fontsize=9)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig7_score_vs_nclean.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Figure 8: T4 triangulation stability distributions
# ══════════════════════════════════════════════════════════════════════════════

def figure8_t4_stability(con, out_dir):
    rows = load_top37(con)
    c2_fracs    = [r[6] for r in rows if r[6] is not None]
    kappa_fracs = [r[7] for r in rows if r[7] is not None]
    scores      = [r[2] for r in rows if r[6] is not None]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    for ax, fracs, label, color in [
        (axes[0], c2_fracs,    "c₂ stable fraction (T4, 200 tri)", "#3A7DBF"),
        (axes[1], kappa_fracs, "κ stable fraction (T4, 200 tri)",  "#2CA02C"),
    ]:
        ax.hist(fracs, bins=20, range=(0, 1), color=color, alpha=0.8,
                edgecolor="white", linewidth=0.5)
        ax.set_xlabel(label)
        ax.set_ylabel("Count")
        ax.axvline(np.mean(fracs), color="black", lw=1.5, ls="--",
                   label=f"Mean={np.mean(fracs):.3f}")
        ax.legend(fontsize=9)

    fig.suptitle("T4 triangulation stability — top-37 (200 FRST samples each)", y=1.01)
    fig.tight_layout()
    path = os.path.join(out_dir, "fig8_t4_stability.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

    # Also: score vs c2_stable scatter
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.scatter(c2_fracs, scores, s=50, alpha=0.8, color="#3A7DBF")
    ax2.scatter([0.0333], [89], marker="*", s=250, color="#D62728", zorder=5,
                label="Champion h26/P11670")
    ax2.set_xlabel("c₂ stable fraction (T4)")
    ax2.set_ylabel("sm_score")
    ax2.set_title("Score vs triangulation stability (top-37)")
    ax2.legend(fontsize=9)
    fig2.tight_layout()
    path2 = os.path.join(out_dir, "fig8b_score_vs_stability.png")
    fig2.savefig(path2, bbox_inches="tight")
    plt.close(fig2)
    print(f"  Saved: {path2}")


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="Generate paper figures from v6 DB")
    ap.add_argument("--db",      default=os.path.join(SCRIPT_DIR, "cy_landscape_v6.db"))
    ap.add_argument("--out-dir", default=os.path.join(SCRIPT_DIR, "results", "figures"))
    ap.add_argument("--fig", type=int, nargs="*", help="Only generate these figure numbers")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    con = get_db(args.db)

    figs = args.fig or [1, 2, 3, 4, 5, 6, 7, 8]
    print(f"Generating {len(figs)} figure(s) → {args.out_dir}/")
    print()

    if 1 in figs:
        print("Figure 1: KS population...")
        figure1_ks_population(args.out_dir)
    if 2 in figs:
        print("Figure 2: Funnel...")
        figure2_funnel(args.out_dir)
    if 3 in figs:
        print("Figure 3: Score histogram...")
        figure3_score_histogram(con, args.out_dir)
    if 4 in figs:
        print("Figure 4: Score vs h¹¹...")
        figure4_score_vs_h11(con, args.out_dir)
    if 5 in figs:
        print("Figure 5: Boundary collapse...")
        figure5_boundary_collapse(con, args.out_dir)
    if 6 in figs:
        print("Figure 6: Top-37 h¹¹ histogram...")
        figure6_top37_h11(con, args.out_dir)
    if 7 in figs:
        print("Figure 7: Score vs n_clean...")
        figure7_score_vs_nclean(con, args.out_dir)
    if 8 in figs:
        print("Figure 8: T4 stability...")
        figure8_t4_stability(con, args.out_dir)

    print()
    print(f"All figures saved to: {args.out_dir}/")
    con.close()


if __name__ == "__main__":
    main()
