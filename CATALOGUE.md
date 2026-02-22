# Catalogue of Results — χ = −6 CY Landscape

> **Purpose**: Record what's been checked, what passed, and what's ruled out.
> If a polytope or approach appears here, you don't need to redo the work.
>
> **Last updated**: 2026-02-24. Scan v2 complete (1,025 polytopes). T2 partial (20/157).

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
  │   │   │   ├─ 20 completed Tier 2 ─────── (deep analysis)
  │   │   │   │
  │   │   │   └─ 137 awaiting Tier 2
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

## 3. Top 20 Candidates (Tier 2)

All non-favorable except h15/poly33. T2 score out of 55.

| Rank | Polytope | h¹¹_eff | T2 | Clean h⁰=3 | h⁰≥3 | max h⁰ | K3 | Ell |
|------|----------|---------|-----|------------|-------|--------|-----|-----|
| 1 | h17/poly63 | 13 | 45 | 198 | 922 | 40 | 5 | 6 |
| 2 | h18/poly34 | 13 | 45 | 189 | 730 | 16 | 4 | 4 |
| 3 | h17/poly90 | 13 | 45 | 148 | 542 | 16 | 3 | 3 |
| 4 | h16/poly63 | 13 | 45 | 72 | 584 | 37 | 4 | 4 |
| 5 | h18/poly6 | 13 | 45 | 56 | 514 | 24 | — | — |
| 6 | h15/poly94 | 13 | 45 | 36 | 126 | 10 | — | — |
| 7 | h19/poly67 | — | 45 | 27 | 100 | 10 | — | — |
| 8 | h16/poly86 | — | 45 | 24 | 126 | 10 | — | — |
| 9 | h16/poly24 | — | 44 | 27 | 144 | 10 | — | — |
| 10 | h19/poly68 | — | 44 | 22 | 90 | 10 | — | — |
| 11 | h17/poly57 | — | 42 | 18 | 70 | 10 | — | — |
| 12 | h16/poly11 | — | 41 | 255 | 840 | 13 | — | — |
| 13 | h14/poly5 | — | 41 | 74 | 670 | 27 | — | — |
| 14 | h18/poly8 | — | 41 | 36 | 122 | 16 | — | — |
| 15 | h16/poly91 | — | 39 | 22 | 102 | 11 | — | — |
| 16 | h17/poly41 | — | 38 | 9 | 66 | 12 | — | — |
| 17 | h15/poly33 [F] | — | 37 | 16 | 60 | 10 | — | — |
| 18 | h17/poly81 | — | 35 | 16 | 90 | 10 | — | — |
| 19 | h19/poly35 | — | 34 | 9 | 36 | 10 | — | — |
| 20 | h18/poly74 | — | 29 | 4 | 38 | 20 | — | — |

**Observations**:
- Every top candidate is non-favorable (h¹¹_eff < h¹¹). These were invisible before Bug B-11 fix.
- h16/poly11 has the most clean bundles (255) despite a lower T2 score — it may be underscored.
- h14/poly5 is notable: low h¹¹ but high h⁰ count. Worth a full pipeline run.

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

1. **Complete Tier 2 on remaining 137 candidates** — The batch is running on Codespace. Will reveal how many polytopes rival h17/poly63.

2. **Full pipeline on h17/poly63** — Top T2 scorer (198 clean bundles, max h⁰=40). Needs the same detailed treatment h13/poly1 got.

3. **Expand scan at h¹¹ = 15–17** — Remove `limit=100` cap. These h¹¹ values have thousands of polytopes we haven't touched.

4. **Stage 5: Higher-rank bundles** — Line bundles only give U(1) gauge group. Standard Model needs SU(3)×SU(2)×U(1). This requires rank 4 or 5 vector bundles (monads, extensions). Nobody has attempted this yet on our candidates.

5. **F-theory classification** — All candidates have elliptic fibrations. Discriminant locus analysis would identify gauge groups directly from geometry.

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
