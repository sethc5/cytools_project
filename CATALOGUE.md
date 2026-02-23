# Catalogue of Results — χ = −6 CY Landscape

> **Purpose**: Record what's been checked, what passed, and what's ruled out.
> If a polytope or approach appears here, you don't need to redo the work.
>
> **Last updated**: 2026-02-24. Scan v2 complete (1,025 polytopes). T2 complete (157/157).

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

- **h¹¹ = 25–128**: 92 of 104 Hodge pairs are completely untouched. The KS database has millions of polytopes at high h¹¹.
- **Limit cap**: Even at h¹¹ = 15–17, we saw only the first 100 of thousands. The KS CGI returns polytopes in an unspecified order — we have no guarantee the first 100 are representative.
- **Favorable bias**: Scan v1 (pre-B-11 fix) missed all 705 non-favorable polytopes. Scan v2 fixed this, but our best candidates are all non-favorable. There may be non-favorable polytopes we haven't reached in the first 100.

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

## 3. Top 20 Candidates (Tier 2 — all 157 complete)

Ranked by clean h⁰=3 bundle count. All non-favorable. T2 score out of 55.

| Rank | Polytope | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell |
|------|----------|----|------------|-------|--------|-----|-----|
| 1 | **h14/poly2** | 41 | **268** | 828 | 13 | 3 | 1 |
| 2 | h17/poly96 | 39 | 227 | 930 | **65** | 2 | 1 |
| 3 | h17/poly9 | 35 | 181 | 876 | 15 | 1 | 0 |
| 4 | h17/poly8 | 45 | 159 | 558 | 13 | 3 | 3 |
| 5 | h15/poly23 | 45 | 119 | 524 | 20 | 4 | 6 |
| 6 | h17/poly21 | 45 | 118 | 532 | 13 | 4 | 6 |
| 7 | h19/poly7 | 41 | 114 | 374 | 6 | 3 | 1 |
| 8 | h16/poly22 | 45 | 111 | 440 | 10 | 4 | 6 |
| 9 | h16/poly51 | 41 | 109 | 486 | 12 | 3 | 1 |
| 10 | h15/poly36 | 41 | 107 | 310 | 11 | 3 | 1 |
| 11 | h15/poly61 | 45 | 103 | 338 | 4 | 3 | 3 |
| 12 | h17/poly58 | 45 | 102 | 520 | 6 | 3 | 3 |
| 13 | h16/poly43 | 41 | 98 | 544 | 13 | 3 | 1 |
| 14 | h15/poly25 | 45 | 95 | 418 | 13 | 3 | 3 |
| 15 | h17/poly32 | 45 | 95 | 438 | 13 | 3 | 3 |
| 16 | h16/poly52 | 41 | 94 | 388 | 4 | 3 | 1 |
| 17 | h16/poly3 | 45 | 86 | 458 | 15 | 4 | 4 |
| 18 | h13/poly0 | 35 | 86 | 380 | 10 | 1 | 0 |
| 19 | h15/poly14 | 39 | 76 | 588 | 44 | 2 | 1 |
| 20 | h16/poly73 | 45 | 74 | 382 | 12 | 3 | 3 |

Full merged CSV: [results/tier2_full_results.csv](results/tier2_full_results.csv)

### T2 Score Distribution (all 157)

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
- **h14/poly2 is the new clean-bundle leader** (268 clean) at the lowest h¹¹ (14) in the batch. Low h¹¹ = simpler moduli stabilization. Strong full-pipeline candidate.
- **h17/poly96 has max h⁰ = 65** — the highest of any polytope scanned. 227 clean bundles despite only T2=39.
- Every top candidate is non-favorable. These were invisible before Bug B-11 fix.
- 23 polytopes hit the T2 score cap of 45 — the scoring saturates. Clean bundle count is the better discriminator.
- h16/poly74 has **10 elliptic fibrations** (most of any candidate) — exceptional for F-theory.

---

## 4. Deep Pipeline Results

### h13/poly1 — Full Pipeline Score: 18/20

The strongest candidate found so far. Full write-up in [FINDINGS.md](FINDINGS.md).

- h¹¹=13, h²¹=16, χ=−6 (native 3-generation)
- **25 completely clean bundles**: h⁰=3, h¹=h²=h³=0
- 11,054 total χ=±3 bundles (5,527 each sign)
- 76 bundles with h⁰ ≥ 3, max h⁰ = 6
- 3 del Pezzo divisors (dP₄, dP₆, dP₄), 1 K3-like
- Swiss cheese: τ=10.0, V=308,352, ratio=0.0022
- **No nef bundles** (min Mori pairing = −19)
- Favorable: No. h¹¹_eff = 13.

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

1. **Full pipeline on h14/poly2** — New clean-bundle leader (268) at h¹¹=14. Lowest h¹¹ with this many bundles. Needs Stages 1–4 deep analysis + scorecard.

2. **Full pipeline on h17/poly8** — Top T2=45 scorer by clean count (159 clean, K3=3, ell=3). Best candidate among those with maximum T2 score.

3. **Expand scan at h¹¹ = 15–17** — Remove `limit=100` cap. We scanned 100/553 at h15, 100/5180 at h16, 100/38735 at h17.

4. **Stage 5: Higher-rank bundles** — Line bundles only give U(1) gauge group. Standard Model needs SU(3)×SU(2)×U(1). This requires rank 4 or 5 vector bundles (monads, extensions). Nobody has attempted this yet on our candidates.

5. **F-theory on h16/poly74** — 10 elliptic fibrations (most of any candidate). Prime target for discriminant locus classification.

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
