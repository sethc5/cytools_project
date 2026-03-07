#!/usr/bin/env python3
"""
gen_figures.py — Generate all paper figures from the local v6 DB.

Run from the paper/ directory:
    python gen_figures.py

Produces figures/ subdirectory with 8 PNG/PDF files.
"""

import os
import sys
import sqlite3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import LogLocator, LogFormatter

# ── paths ──────────────────────────────────────────────────────────────────
here    = os.path.dirname(os.path.abspath(__file__))
root    = os.path.dirname(here)
db_path = os.path.join(root, 'v6', 'cy_landscape_v6.db')
outdir  = os.path.join(here, 'figures')
os.makedirs(outdir, exist_ok=True)

print(f"Database: {db_path}")
con = sqlite3.connect(db_path)
cur = con.cursor()

# ── style ───────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'legend.fontsize': 10,
    'figure.dpi': 150,
})

BLUE   = '#2166ac'
RED    = '#d73027'
GREEN  = '#1a9850'
ORANGE = '#f46d43'
GRAY   = '#888888'

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — KS landscape coverage by h11 (bar chart, log scale)
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 1: KS coverage by h11 ...")
rows = cur.execute("""
    SELECT h11, COUNT(*) as total,
           SUM(CASE WHEN sm_score IS NOT NULL THEN 1 ELSE 0 END) as scored
    FROM polytopes
    GROUP BY h11
    ORDER BY h11
""").fetchall()

h11s   = [r[0] for r in rows]
totals = [r[1] for r in rows]
scored = [r[2] for r in rows]

fig, ax = plt.subplots(figsize=(9, 4))
x = np.arange(len(h11s))
ax.bar(x, totals, color=BLUE, alpha=0.6, label='Scanned')
ax.bar(x, scored, color=ORANGE, alpha=0.9, label='T2-scored')
ax.set_yscale('log')
ax.set_xticks(x)
ax.set_xticklabels([str(h) for h in h11s], fontsize=8)
ax.set_xlabel(r'$h^{1,1}$')
ax.set_ylabel('Count (log scale)')
ax.set_title(r'KS Landscape Coverage by $h^{1,1}$ ($\chi = -6$)')
ax.legend()
ax.grid(True, axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'fig1_coverage_h11.pdf'))
fig.savefig(os.path.join(outdir, 'fig1_coverage_h11.png'))
plt.close()
print("  saved fig1")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Screening funnel diagram
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 2: Screening funnel ...")
t0 = cur.execute("SELECT COUNT(*) FROM polytopes").fetchone()[0]
t1 = cur.execute("SELECT COUNT(*) FROM polytopes WHERE favorable=1").fetchone()[0]
t2 = cur.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score IS NOT NULL").fetchone()[0]
t3_70 = cur.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score >= 70").fetchone()[0]
t3_80 = cur.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score >= 80").fetchone()[0]
t4    = cur.execute("SELECT COUNT(*) FROM polytopes WHERE sm_score >= 89").fetchone()[0]

stages = ['T0: All\nscanned', 'T1: Favorable\ntriangulation', 'T2: Scored',
          'T3: Score≥70', 'T3+: Score≥80', 'T4: Score≥89']
counts = [t0, t1, t2, t3_70, t3_80, t4]

fig, ax = plt.subplots(figsize=(8, 5))
colors = [BLUE, BLUE, ORANGE, ORANGE, RED, RED]
bars = ax.barh(range(len(stages)), counts, color=colors, alpha=0.75)
for i, (bar, cnt) in enumerate(zip(bars, counts)):
    ax.text(cnt * 1.02, i, f'{cnt:,}', va='center', fontsize=9)
ax.set_xscale('log')
ax.set_yticks(range(len(stages)))
ax.set_yticklabels(stages)
ax.set_xlabel('Count (log scale)')
ax.set_title('Pipeline Screening Funnel')
ax.invert_yaxis()
ax.grid(True, axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'fig2_funnel.pdf'))
fig.savefig(os.path.join(outdir, 'fig2_funnel.png'))
plt.close()
print(f"  saved fig2  (funnel: {t0:,} → {t4})")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Score histogram (T2 entries, bins of 5)
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 3: Score histogram ...")
scores_all = [r[0] for r in cur.execute(
    "SELECT sm_score FROM polytopes WHERE sm_score IS NOT NULL"
).fetchall()]

fig, ax = plt.subplots(figsize=(8, 4))
bins = np.arange(0, 100, 5)
counts_hist, edges, patches = ax.hist(scores_all, bins=bins, color=BLUE, alpha=0.8, edgecolor='white')
ax.axvline(70, color=ORANGE, linestyle='--', label='Score = 70')
ax.axvline(80, color=RED, linestyle='--', label='Score = 80')
ax.set_xlabel('SM score')
ax.set_ylabel('Count')
ax.set_title('Score Distribution of T2-Scored Polytopes')
ax.legend()
ax.grid(True, axis='y', alpha=0.3)
max_score = max(scores_all)
ax.annotate(f'Champion: {max_score}', xy=(max_score, 1), xytext=(max_score-25, 15),
            arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'fig3_score_hist.pdf'))
fig.savefig(os.path.join(outdir, 'fig3_score_hist.png'))
plt.close()
print(f"  saved fig3  (max score: {max_score})")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — Score vs h11 scatter (colored by has_SM flag)
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 4: Score vs h11 scatter ...")
rows4 = cur.execute("""
    SELECT h11, sm_score
    FROM polytopes
    WHERE sm_score IS NOT NULL
    ORDER BY RANDOM()
    LIMIT 5000
""").fetchall()

h11_arr  = np.array([r[0] for r in rows4])
score_arr = np.array([r[1] for r in rows4])

fig, ax = plt.subplots(figsize=(8, 5))
sc = ax.scatter(h11_arr, score_arr, c=score_arr, cmap='coolwarm',
                s=6, alpha=0.5, vmin=0, vmax=100)
ax.axhline(70, color=ORANGE, linestyle='--', lw=1, label='Score = 70')
ax.axhline(80, color=RED, linestyle='--', lw=1, label='Score = 80')
plt.colorbar(sc, ax=ax, label='SM score')
ax.set_xlabel(r'$h^{1,1}$')
ax.set_ylabel('SM score')
ax.set_title(r'SM Score vs $h^{1,1}$ (T2-scored sample)')
ax.legend()
ax.grid(True, alpha=0.2)
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'fig4_score_vs_h11.pdf'))
fig.savefig(os.path.join(outdir, 'fig4_score_vs_h11.png'))
plt.close()
print("  saved fig4")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 5 — Max score per h11 (boundary collapse)
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 5: Max score per h11 ...")
rows5 = cur.execute("""
    SELECT h11, MAX(sm_score) as maxscore, COUNT(*)
    FROM polytopes
    WHERE sm_score IS NOT NULL
    GROUP BY h11
    ORDER BY h11
""").fetchall()

h11_5  = [r[0] for r in rows5]
max_5  = [r[1] for r in rows5]
cnt_5  = [r[2] for r in rows5]

fig, ax = plt.subplots(figsize=(9, 4))
sc = ax.scatter(h11_5, max_5, c=np.log10([max(c,1) for c in cnt_5]),
                cmap='viridis', s=60, zorder=3)
ax.plot(h11_5, max_5, color=GRAY, alpha=0.4, lw=1)
ax.axhline(80, color=RED, linestyle='--', lw=1, label='Score = 80')
plt.colorbar(sc, ax=ax, label=r'$\log_{10}$(count)')
ax.set_xlabel(r'$h^{1,1}$')
ax.set_ylabel('Max SM score')
ax.set_title(r'Maximum SM Score per $h^{1,1}$ — Landscape Boundary')
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'fig5_max_score_boundary.pdf'))
fig.savefig(os.path.join(outdir, 'fig5_max_score_boundary.png'))
plt.close()
print("  saved fig5")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 6 — h11 histogram of T4 (top-37) polytopes
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 6: h11 histogram of T4 ...")
rows6 = cur.execute("""
    SELECT h11 FROM polytopes WHERE sm_score >= 80
""").fetchall()
h11_top = [r[0] for r in rows6]

fig, ax = plt.subplots(figsize=(7, 4))
from collections import Counter
h11_counts = Counter(h11_top)
h11_vals = sorted(h11_counts.keys())
h11_freqs = [h11_counts[h] for h in h11_vals]
ax.bar([str(h) for h in h11_vals], h11_freqs, color=RED, alpha=0.8)
ax.set_xlabel(r'$h^{1,1}$')
ax.set_ylabel('Count')
ax.set_title(r'$h^{1,1}$ Distribution of T4 Cluster (SM score $\geq 80$)')
for i, (v, f) in enumerate(zip(h11_vals, h11_freqs)):
    ax.text(i, f+0.1, str(f), ha='center', fontsize=9)
ax.grid(True, axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(outdir, 'fig6_h11_top37.pdf'))
fig.savefig(os.path.join(outdir, 'fig6_h11_top37.png'))
plt.close()
print(f"  saved fig6  (T4 has {len(h11_top)} entries)")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 7 — Score vs n_clean scatter
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 7: Score vs n_clean ...")
has_nclean = cur.execute("""
    SELECT name FROM pragma_table_info('polytopes') WHERE name='n_clean'
""").fetchone()

if has_nclean:
    rows7 = cur.execute("""
        SELECT sm_score, n_clean, poly_idx
        FROM polytopes
        WHERE sm_score >= 70 AND n_clean IS NOT NULL
        ORDER BY sm_score DESC
    """).fetchall()

    if rows7:
        sc7 = [r[0] for r in rows7]
        nc7 = [r[1] for r in rows7]
        pid7 = [r[2] for r in rows7]

        # champion
        champ_idx = sc7.index(max(sc7))

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(nc7, sc7, c=BLUE, s=20, alpha=0.6)
        ax.scatter(nc7[champ_idx], sc7[champ_idx], c=RED, s=100, zorder=5,
                   label=f'Champion (score={sc7[champ_idx]}, n_clean={nc7[champ_idx]})')
        ax.axhline(80, color=ORANGE, linestyle='--', lw=1, label='Score = 80')
        ax.set_xlabel('n_clean (# clean triangulations)')
        ax.set_ylabel('SM score')
        ax.set_title('SM Score vs n_clean (T3 tier, score ≥ 70)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, 'fig7_score_vs_nclean.pdf'))
        fig.savefig(os.path.join(outdir, 'fig7_score_vs_nclean.png'))
        plt.close()
        print(f"  saved fig7  ({len(rows7)} points)")
    else:
        print("  fig7: no n_clean data for score>=70")
else:
    print("  fig7: no n_clean column in polytopes table")

# ═══════════════════════════════════════════════════════════════════════════
# Figure 8 — Fibrations by h11 (bar chart)
# ═══════════════════════════════════════════════════════════════════════════
print("Fig 8: Fibrations by h11 ...")
try:
    rows8 = cur.execute("""
        SELECT p.h11, COUNT(f.id) as nfib
        FROM polytopes p
        JOIN fibrations f ON f.h11 = p.h11 AND f.poly_idx = p.poly_idx
        GROUP BY p.h11
        ORDER BY p.h11
    """).fetchall()

    if rows8:
        h11_f = [r[0] for r in rows8]
        nfib  = [r[1] for r in rows8]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar([str(h) for h in h11_f], nfib, color=GREEN, alpha=0.8)
        ax.set_xlabel(r'$h^{1,1}$')
        ax.set_ylabel('Number of fibrations found')
        ax.set_title(r'K3 Fibrations by $h^{1,1}$')
        ax.grid(True, axis='y', alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, 'fig8_fibrations_h11.pdf'))
        fig.savefig(os.path.join(outdir, 'fig8_fibrations_h11.png'))
        plt.close()
        print(f"  saved fig8  ({sum(nfib)} total fibrations)")
    else:
        print("  fig8: no fibration data")
except Exception as e:
    print(f"  fig8: error — {e}")

con.close()

print("\nAll figures written to:", outdir)
print("Files:", sorted(os.listdir(outdir)))
