# Catalogue of Results — χ = −6 CY Landscape

> **Purpose**: Record what's been checked, what passed, and what's ruled out.
> If a polytope or approach appears here, you don't need to redo the work.
>
> **Last updated**: 2026-02-23. h13–h16 fully scanned (~11,000 polytopes). h17 scan 42% (Codespace). h18 scan 98% (Hetzner). **12 full pipeline runs** (7× 26/26). GL=12/D₆ geometry study in progress.

---

## 1. Scan Coverage

### What We Scanned

| h¹¹ | KS count | Scanned | Hits (h⁰≥3) | Coverage |
|------|----------|---------|-------------|----------|
| 13 | 3 | 3 | 3 | 100% |
| 14 | 22 | 22 | 18 | 100% |
| 15 | 553 | 100 | 73 | 18% |
| 16 | 5,180 | 100 | 73 | 1.9% |
| 17 | 38,735 | 100 | 82 | 0.26% |
| 18 | ~200k+ | 100 | 73 | <0.05% |
| 19 | ~500k+ | 100 | 68 | <0.02% |
| 20 | ~1M+ | 100 | 59 | ~0% |
| 21 | large | 100 | 57 | ~0% |
| 22 | large | 100 | 56 | ~0% |
| 23 | large | 100 | 43 | ~0% |
| 24 | large | 100 | 29 | ~0% |
| **Total** | | **1,025** | **634** | |

**Key stat**: 634/1025 (62%) have at least one line bundle with h⁰ ≥ 3 among the first ~5,500 bundles probed.

### What We Haven't Scanned

- **h¹¹ = 19–128**: 90+ of 104 Hodge pairs have only 100 polytopes sampled. The KS database has millions at high h¹¹.
- **Favorable bias**: Scan v1 (pre-B-11 fix) missed all 705 non-favorable polytopes. Scan v2 fixed this, but our best candidates are all non-favorable.

---

## 2. Screening Funnel Results

```
1,025 polytopes (scan v2, h11=13..24, limit=100/h11)
  │
  ├─ 634 have h⁰ ≥ 3 line bundles ─────────── 62% pass
  │   │
  │   ├─ 337 pass Tier 1 ──────────────────── 33% of total
  │   │   (dP divisors + Swiss cheese + symmetry + max h⁰)
  │   │   │
  │   │   ├─ 157 pass Tier 1.5 ────────────── 15% of total  
  │   │   │   (fibrations + 300-bundle probe, ≥3 clean h⁰=3)
  │   │   │   │
  │   │   │   └─ 157 completed Tier 2 ────── ✅ ALL DONE
  │   │   │       23 scored T2=45 (max)
  │   │   │       66 scored T2≥41
  │   │   │
  │   │   └─ 180 filtered at T1.5
  │   │       (too few clean bundles or probe truncated badly)
  │   │
  │   └─ 297 filtered at T1
  │       (no dP divisors, no Swiss cheese, or max h⁰ too low)
  │
  └─ 391 have max h⁰ ≤ 2 ──────────────────── 38% fail
```

---

## 3. Top Candidates (Tier 2 — all 177 complete)

Ranked by clean h⁰=3 bundle count. All non-favorable. T2 score out of 55.

| Rank | Polytope | Score | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell | Notes |
|------|----------|-------|------------|-------|--------|-----|-----|-------|
| 1 | **★ h14/poly2** | **26/26** | **320** | 828 | 13 | 3 | 3 | Heterotic champion |
| 2 | **★ h16/poly11** | **26/26** | **298** | 840 | 13 | 3 | 3 | 5 dP divisors |
| 3 | **★ h17/poly96** | **25/26** | **252** | 930 | **65** | 2 | 1 | Highest max h⁰, 0 dP |
| 4 | **★ h17/poly63** | **26/26** | **218** | 922 | 40 | 5 | **10** | F-theory champion |
| 5 | **★ h17/poly9** | **23/26** | **192** | 876 | 15 | 1 | 0 | No ell/dP |
| 6 | **★ h18/poly34** | **26/26** | **184** | 730 | 16 | 4 | 6 | 5 dP |
| 7 | **★ h17/poly8** | **26/26** | **180** | 558 | 13 | 3 | 3 | Best LVS (τ=2208) |
| 8 | h17/poly90 | 45 | 148 | 542 | 16 | 3 | 3 |
| 9 | h15/poly23 | 45 | 119 | 524 | 20 | 4 | 6 |
| 10 | h17/poly21 | 45 | 118 | 532 | 13 | 4 | 6 |
| 11 | h19/poly7 | 41 | 114 | 374 | 6 | 3 | 1 |
| 12 | h16/poly22 | 45 | 111 | 440 | 10 | 4 | 6 |
| 13 | h16/poly51 | 41 | 109 | 486 | 12 | 3 | 1 |
| 14 | h15/poly36 | 41 | 107 | 310 | 11 | 3 | 1 |
| 15 | h15/poly61 | 45 | 103 | 338 | 4 | 3 | 3 |
| 16 | h17/poly58 | 45 | 102 | 520 | 6 | 3 | 3 |
| 17 | h16/poly43 | 41 | 98 | 544 | 13 | 3 | 1 |
| 18 | h15/poly25 | 45 | 95 | 418 | 13 | 3 | 3 |
| 19 | h17/poly32 | 45 | 95 | 438 | 13 | 3 | 3 |
| 20 | h16/poly52 | 41 | 94 | 388 | 4 | 3 | 1 |

Full merged CSV: [results/tier2_full_results.csv](results/tier2_full_results.csv)

### T2 Score Distribution (all 177)

| T2 Score | Count |
|----------|-------|
| 45 (max) | 23 |
| 44 | 17 |
| 43 | 6 |
| 42 | 4 |
| 41 | 16 |
| 40 | 11 |
| 39 | 10 |
| 38 | 14 |
| ≤37 | 56 |

**Observations**:
- **★ h14/poly2 (Heterotic Champion)**: Full pipeline score 26/26, **320 clean bundles** (up from 268 in T2), 3 Swiss cheese directions, lowest h¹¹ (14) = simplest moduli stabilization.
- **★ h17/poly63 (F-Theory Champion)**: Full pipeline score 26/26, **218 clean bundles** (up from 198 in T2), **10 elliptic fibrations** (up from 6 in T2), 6 dP divisors, richest fibration structure.
- **h17/poly96 has max h⁰ = 65** — the highest of any polytope scanned. 227 clean bundles despite only T2=39.
- Every top candidate is non-favorable. These were invisible before Bug B-11 fix.
- 23 polytopes hit the T2 score cap of 45 — the scoring saturates. Full pipeline 26-point scorecard is the better discriminator.
- **Full pipeline finds more**: T2→pipeline upgrades: h14/poly2 clean 268→320, h17/poly63 clean 198→218, elliptic 6→10. The more thorough methodology in Stages 1-4 catches bundles/fibrations missed by the faster T2 screen.
- h16/poly74 has **10 elliptic fibrations** (most of any candidate) — exceptional for F-theory.

---

## 4. Deep Pipeline Results (12 complete)

### ★ h14/poly2 — Heterotic Champion (Score: 26/26)

- h¹¹=14, h²¹=17, χ=−6 (native 3-gen)
- **320 completely clean bundles** (most of any candidate)
- 828 with h⁰ ≥ 3, max h⁰ = 13
- 3 dP divisors, 3 Swiss cheese directions (τ=58.5)
- 3 K3 + 3 elliptic fibrations

### ★ h17/poly25 — F-Theory + Triple-Threat Champion (Score: 26/26)

- h¹¹=17, h²¹=20, χ=−6
- **170 clean bundles**, 490 with h⁰ ≥ 3, max h⁰ = 8
- **15 elliptic fibrations** (all-time record) + 6 K3 + Swiss cheese τ=56
- Only candidate excelling at heterotic + F-theory + LVS simultaneously

### ★ h15/poly61 — LVS Champion (Score: 25/26)

- h¹¹=15, h²¹=18, χ=−6
- **110 clean bundles**, 338 with h⁰ ≥ 3, max h⁰ = 4
- **Swiss cheese τ = 14,300** (6.5× runner-up)
- 3 K3 + 3 elliptic fibrations. 0 dP (−1 point)

### ★ h17/poly63 — Former F-Theory Champion (Score: 26/26)

- 218 clean bundles, max h⁰=40, 6 dP, 5 K3 + 10 elliptic
- 1 nef bundle (extremely rare)

### ★ h16/poly11 (26/26, 298 clean), h18/poly34 (26/26, 184 clean), h17/poly8 (26/26, 180 clean, τ=2208)

### All 12 pipeline runs: see [FINDINGS.md](FINDINGS.md)

### h13/poly1 — Benchmark (Score: 18/20, legacy scoring)

The original benchmark candidate. Full write-up in [FINDINGS.md](FINDINGS.md).

- h¹¹=13, h²¹=16, χ=−6
- **25 completely clean bundles**
- 3 dP divisors, Swiss cheese τ=10.0

### Polytope 40 (h15/poly40) — Pipeline Score: 10/20

Extensively studied but definitively limited. Write-up in [FINDINGS.md](FINDINGS.md).

- h¹¹=15, h²¹=18, χ=−6
- **Max h⁰ = 2** (rigorously proven via 7-script audit)
- 116 three-divisor χ=3 bundles, 2 single-divisor
- 11 del Pezzo divisors (dP₁ through dP₇)
- Swiss cheese: τ=4.0, V=17,506
- Z₂ symmetry
- **No line bundle has h⁰ = 3. Do not re-investigate this polytope for line bundle h⁰.**

---

## 5. Ruled Out — Don't Re-Check These

### 5a. Specific Polytopes

| Polytope | What Was Tried | Why It Fails | Evidence |
|----------|---------------|--------------|----------|
| h15/poly40 | Line bundle h⁰=3 search | Max h⁰ = 2, rigorously proven | Koszul + lattice points, 7-script dragon slayer series |
| Ample Champion (h11=2, h21=29) | Z₃×Z₃ quotient to χ=−6 | Pure g₁, g₂ have fixed curves → singular quotient | Numerical optimizer found \|P\|² ≈ 10⁻⁸⁸ on fixed locus |
| Ample Champion | Diagonal Z₃ quotient | Gives χ=−18 (9 generations), not −6 | Hodge number calculation |

### 5b. General Negative Results

| Claim | Scope | Proof |
|-------|-------|-------|
| **No nef h⁰=3 bundles exist** | All 1,025 scanned polytopes | Min Mori pairing < 0 for every χ=3 bundle found. Kodaira vanishing never applies. |
| **K3 + elliptic fibrations are universal** | All 157 T1.5 survivors | Every χ=−6 polytope at h¹¹≥13 has both K3 and elliptic fibrations. This is not a discriminator. |
| **Non-favorable polytopes dominate** | 705/1025 = 69% | Most χ=−6 polytopes are non-favorable. The strongest candidates are ALL non-favorable. |
| **cohomCalg is blocked** at high h¹¹ | h¹¹ ≥ 15 typically | SR ideal exceeds 64 generators → hard failure. Must use Koszul or other methods. |
| **h⁰ distribution peaks at 1–3** | 1,025 polytopes | Distribution: h⁰_max = 1 (316), 2 (76), 3 (249), 4 (117), 5 (42), 6+ (225) |

### 5c. CYTools Bugs That Caused False Results

These bugs wasted significant time. If you're using CYTools 1.4.5, be aware:

| Bug | Description | Impact | Workaround |
|-----|-------------|--------|------------|
| B-11 | `second_chern_class(in_basis=True)` returns wrong-size vector for non-favorable polytopes | 705/1025 polytopes invisible in scan v1 | Use `h11_eff = len(div_basis)` as working dimension |
| #2 | Intersection numbers have toric vs basis coordinate confusion | Wrong D³, wrong χ computation | Always use `in_basis=True` |
| #3 | Mori cone: 15-dim divisor vs 20-dim Mori generators | Index mismatch in nef check | Explicit index mapping to basis |
| #5 | cohomCalg hard limit of 64 SR generators | Cannot compute cohomology on complex polytopes | Use Koszul pipeline instead |
| #7 | `glsm_linear_relations()` includes non-character translations | Misleading for linear equivalence | Check dimensions manually |

---

## 6. What Needs Doing Next

Ordered by expected impact:

1. **Complete h17 + h18 scans** — h17 running on Codespace (42%), h18 on Hetzner (98% — nearly done). Results will add thousands of new candidates to the T1→T2 funnel.

2. **Stage 5: Higher-rank bundles** — `rank_n_bundles.py` exists but needs stability analysis beyond Hoppe. Find a truly stable rank-4/5 bundle with net chirality = 3.

3. **Picard-Fuchs in Mori coordinates** — The GL=12/D₆ polytope has a closed-form period formula and 26 D₆-invariant Yukawa couplings. Next: derive the PF PDE system in the 6 Mori coordinates for exact period integrals.

4. **F-theory discriminant locus** — h17/poly25 has **15 elliptic fibrations** (record). Classify singular fibers (Kodaira types) to determine gauge algebras.

5. **Run full pipeline on remaining T2 candidates** — 27 T2 candidates still lack full pipeline analysis.

6. **Expand to h¹¹ ≥ 19** — Use `scan_fast.py` (2.4× speedup) on the Hetzner server after h18 completes.

---

## 7. How to Contribute to This Catalogue

Run any tier of the pipeline and PR your results:

```bash
# Scan more polytopes (increase limit or add new h11 values)
python scan_chi6_h0.py  # edit limit= in script

# Screen results through the pipeline
python tier1_screen.py
python tier15_screen.py --csv results/tier1_screen_results.csv
python tier2_screen.py --csv15 results/tier15_screen_results.csv --start 0 --end 20
```

Output CSVs go in `results/`. Include your scan parameters in the PR description.
