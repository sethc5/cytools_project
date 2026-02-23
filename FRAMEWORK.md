# FRAMEWORK.md — Theoretical Pipeline: String Compactification → 3-Generation Model

> **Purpose**: Top-down map from the physics goal to every computational step.
> Each node has a status. This is the master navigation document.

---

## 0. The Physics Goal

**Build a realistic 3-generation model from string theory.**

Concretely: find a Calabi-Yau 3-fold $X$ and a vector bundle $V \to X$ such that the low-energy 4D effective theory contains:

| Requirement | Mathematical translation | Status |
|---|---|---|
| 3 chiral families (quarks + leptons) | $\|h^1(X, V) - h^1(X, V^*)\| = 3$ | **Partially addressed** |
| Correct gauge group ($SU(3) \times SU(2) \times U(1)$) | Bundle structure group → GUT breaking | Not started |
| 1 Higgs doublet pair | $h^1(X, \wedge^2 V) = 1$ (for $SU(5)$ GUT) | Not started |
| Moduli stabilization (hierarchy problem) | Swiss cheese / LVS / KKLT mechanism | **Addressed** |
| Positive vacuum energy or de Sitter uplift | Anti-D3 branes or F-term | Not started |

### Connection to the Higgs boson

The Higgs field enters at two levels:

1. **Higgs existence**: In heterotic $E_8 \times E_8$ compactifications, embedding a rank-$n$ bundle $V$ into $E_8$ breaks it to a commutant GUT group $G$. Matter fields arise from $H^1(X, V)$ (generations) and $H^1(X, \wedge^2 V)$ (Higgs doublets in $SU(5)$ models). Getting exactly 1 Higgs pair requires computing a *different* cohomology group than the one giving 3 generations.

2. **Higgs mass hierarchy**: Why is $m_H \approx 125$ GeV $\ll M_{\text{Planck}}$? In LVS (Large Volume Scenario), the CY volume $\mathcal{V}$ sets the SUSY-breaking scale: $m_{\text{soft}} \sim M_P / \mathcal{V}$. A Swiss cheese structure with small 4-cycle volume $\tau \sim 4$ and large overall volume $\mathcal{V} \sim 10^4$ gives $m_{\text{soft}} \sim 10^{-4} M_P \sim$ TeV, precisely the electroweak scale.

---

## 1. The Computational Pipeline

### Stage 1: Calabi-Yau Geometry ✅ DONE

> *Input*: Kreuzer-Skarke database of reflexive polytopes  
> *Output*: CY 3-folds with $\chi = -6$ (giving $|\chi|/2 = 3$ generations in standard embedding)

| Step | Description | Tool/Method | Status |
|------|-------------|-------------|--------|
| 1.1 | Enumerate $\chi = -6$ polytopes | `fetch_polytopes(h11, h21=h11+3)` | ✅ 7500+ polytopes found |
| 1.2 | Triangulate and compute CY data | CYTools triangulate/get_cy | ✅ Routine |
| 1.3 | Choose best candidates | Pipeline scorecard | ✅ Polytope 40, h13-P0/P1/P2 identified |

**Key insight**: $\chi = -6$ exists at every $h^{1,1} \geq 13$. The smallest cases (h11=13, 3 polytopes) are the cleanest.

### Stage 2: Divisor Analysis ✅ DONE

> *Input*: CY 3-fold $X$  
> *Output*: Classification of divisors, volume hierarchy

| Step | Description | Tool/Method | Status |
|------|-------------|-------------|--------|
| 2.1 | Divisor basis identification | `cyobj.divisor_basis()` | ✅ |
| 2.2 | Intersection numbers | `intersection_numbers(in_basis=True)` | ✅ |
| 2.3 | Second Chern class | `second_chern_class(in_basis=True)` | ✅ (has size bug at high h11) |
| 2.4 | Divisor classification (dP, K3, etc.) | $D^3$, $c_2 \cdot D$, $\chi(\mathcal{O}_D)$ | ✅ Polytope 40: 11 rigid dP |
| 2.5 | Swiss cheese structure | Volume hierarchy $\tau_{\text{small}} / \mathcal{V}^{2/3} \ll 1$ | ✅ Poly40: τ=4.0, h13-P1: τ=4.5 |

### Stage 3: Line Bundle Cohomology ✅ DONE

> *Input*: CY 3-fold $X$, line bundle $\mathcal{O}(D)$  
> *Output*: $h^0(X, \mathcal{O}(D))$ for all $\chi = 3$ bundles

| Step | Description | Tool/Method | Status |
|------|-------------|-------------|--------|
| 3.1 | Find all $\chi = 3$ line bundles | HRR: $\chi = D^3/6 + c_2 \cdot D / 12$ | ✅ 119 on Poly40, ~1000+ on h13 polytopes |
| 3.2 | Compute $h^0$ via Koszul sequence | Lattice point counting + shift | ✅ Verified on quintic |
| 3.3 | Nefness / Kodaira vanishing check | Mori cone pairing | ✅ No nef bundles found (any polytope) |
| 3.4 | Serre duality cross-check | $h^3(D) = h^0(-D)$ | ✅ |
| 3.5 | Landscape scan for $h^0 \geq 3$ | scan_chi6_h0.py | ✅ 136/320 polytopes have $h^0 \geq 3$ |

**Key result**: Polytope 40 has max $h^0 = 2$ (unusual). h13-P0 has 12 bundles with exact $h^0 = \chi = 3$.

### Stage 4: Net Chirality from Line Bundles 🔶 PARTIALLY DONE

> *For a line bundle $L$ on $X$*: net chirality $= h^1(X, L) - h^2(X, L)$

| Step | Description | Status |
|------|-------------|--------|
| 4.1 | Compute $h^0, h^3$ (done via Koszul + Serre) | ✅ |
| 4.2 | Deduce $h^1 - h^2 = h^0 - h^3 - \chi$ | ✅ For $h^0 = 3, h^3 = 0, \chi = 3$: $h^1 - h^2 = 0$ |
| 4.3 | Determine individual $h^1, h^2$ | ❌ Need independent computation (e.g., cohomCalg, Čech, or spectral sequence) |

**Issue**: For the exact $h^0 = \chi = 3$ bundles, we get $h^1 = h^2$ but don't know if both are 0. If $h^1 = h^2 = 0$, the bundle has "no higher cohomology" — the cleanest case. If $h^1 = h^2 = k > 0$, there are $k$ vector-like pairs that may or may not decouple.

### Stage 5: Vector Bundle Construction 🔶 IN PROGRESS

> *Moving beyond line bundles to get realistic gauge groups*

| Step | Description | Status |
|------|-------------|--------|
| 5.1 | Direct sum construction: $V = \oplus L_i$ | ✅ `rank_n_bundles.py` — SU(4) and SU(5) scanners, meet-in-the-middle |
| 5.2 | Monad construction: $0 \to V \to B \to C \to 0$ | ✅ `rank_n_bundles.py` — pair+triple decomposition, (5,1) and (6,2) |
| 5.3 | Stability check (Hoppe criterion) | ✅ H⁰(V)=0 check via Koszul; ∧²V check ❌ |
| 5.4 | Chiral spectrum: $\chi(V)$ for rank-$n$ $V$ | ✅ Verified: additivity + monad exact sequence |
| 5.5 | Higgs doublets: $\chi(\wedge^2 V)$ | ✅ For direct sums; ❌ for monads |
| 5.6 | Extension bundles | ❌ |
| 5.7 | Individual $h^i(V)$ computation | ❌ |

**First results (h14/poly2):**
- 100+ SU(4) direct sums with $|\chi| = 3$
- 100+ SU(5) direct sums with $|\chi| = 3$ and $|\chi(\wedge^2 V)| = 3$
- 100+ SU(4) monads, 3 pass Hoppe stability check
- All direct sums are decomposable (polystable at best, never truly stable)
- Monad candidates with $H^0(B) \leq H^0(C)$ may admit stable deformations

### Stage 6: Moduli Stabilization ✅ PARTIALLY DONE

> *Fix the ~100 moduli to get definite 4D physics*

| Step | Description | Status |
|------|-------------|--------|
| 6.1 | Kähler moduli: Swiss cheese / LVS | ✅ Polytope 40 viable, h13-P1 viable |
| 6.2 | Complex structure moduli: flux superpotential | ❌ |
| 6.3 | Vacuum energy / cosmological constant | ❌ |

### Stage 7: Phenomenological Checks ❌ NOT STARTED

| Step | Description | Status |
|------|-------------|--------|
| 7.1 | Yukawa couplings: $\int_X \Omega \wedge A \wedge A \wedge A$ | ❌ |
| 7.2 | Proton decay rate (dimension-6 operators) | ❌ |
| 7.3 | Gauge coupling unification | ❌ |
| 7.4 | Neutrino masses | ❌ |

---

## 2. Current Position in the Pipeline

```
Stage 1 ──── Stage 2 ──── Stage 3 ──── Stage 4 ──── Stage 5 ──── Stage 6 ──── Stage 7
  CY           Divs         Line         Net          Vec          Moduli       Pheno
  Geom         Anal         Bundles      Chiral       Bundles      Stabil       Checks
  ✅            ✅            ✅            🔶            🔶            🔶            ❌
```

**We are at the Stage 3→4 transition.** The line bundle analysis is complete. The next physics step is either:
- (A) Push to Stage 5 (vector bundles — high ceiling, hard)
- (B) Complete Stage 4 by computing individual $h^1, h^2$ (fills the gap)
- (C) Deep-dive Stage 6 on the best candidate (moduli stabilization realism)

---

## 3. Candidate Comparison

| | Polytope 40 (h11=15) | h13-P0 | h13-P1 | h13-P2 |
|---|---|---|---|---|
| **Stage 1**: $\chi = -6$ | ✅ | ✅ | ✅ | ✅ |
| **Stage 2**: Rigid divisors | 11/15 | **13/13** | **13/13** | **13/13** |
| **Stage 2**: Swiss cheese | **YES** ($\tau=4.0$) | NO | **YES** ($\tau=10.0$) | NO |
| **Stage 3**: $h^0 = 3$ exists | ❌ (max 2) | **YES** (12 bundles) | **YES** (25 bundles) | **YES** (17 bundles) |
| **Stage 3**: Nef $h^0=3$ bundle | ❌ | ❌ | ❌ | ❌ |
| **Stage 4**: Clean $h^0=3$ ($h^{1,2,3}=0$) | ❌ | ❌ untested | **YES (all 25)** | ❌ untested |
| **Stage 4-7**: Anything else | ❌ | ❌ | ❌ | ❌ |
| **Score** | 10/20 | — | **18/20** | — |

**Best overall candidate**: **h13-P1** — Swiss cheese + 25 completely clean h⁰=3 bundles.

---

## 4. Key References

| Ref | Authors | Relevance | Used |
|-----|---------|-----------|------|
| Kreuzer-Skarke (2000) | Kreuzer, Skarke | Complete list of 4D reflexive polytopes | ✅ Data source |
| Braun et al. (2006) | Braun, He, Ovrut, Pantev | Heterotic Standard Model from CY + vector bundle | Stage 5 template |
| Anderson et al. (2012) | Anderson, Gray, Lukas, Palti | Systematic line bundle cohomology on CY3 | ✅ Stage 3 methods |
| Balasubramanian et al. (2005) | Balasubramanian, Berglund, Conlon, Quevedo | Large Volume Scenario (LVS) | ✅ Stage 6 (Swiss cheese) |
| Donaldson (1985) / Uhlenbeck-Yau (1986) | — | Hermitian Yang-Mills ⟺ stability | Stage 5 theory |
| Blumenhagen et al. (2006) | Blumenhagen, Moster, Reinbacher, Weigand | Massless spectra via cohomCalg | ✅ Stage 3 (cohomCalg) |
| Cicoli et al. (2008) | Cicoli, Conlon, Quevedo | Swiss cheese moduli stabilization | ✅ Stage 6 details |

---

## 5. Difficulty / Tractability Map

Ranked by "what can we compute now with existing tools":

| Task | Difficulty | Tools available | Priority |
|------|-----------|----------------|----------|
| Full pipeline on h13-P1 | **Easy** | All Stage 1-3 tools proven | **NOW** |
| Individual $h^1, h^2$ (Stage 4.3) | Medium | Čech cohomology or exact sequences | Next |
| Rank-4/5 bundles (Stage 5.1-5.2) | Medium-Hard | ✅ `rank_n_bundles.py` built | **DONE** |
| $\wedge^2 V$ Higgs count (Stage 5.5) | Hard | Requires Stage 5.1 first | After 5.1 |
| Flux superpotential (Stage 6.2) | Hard | Period integrals, Picard-Fuchs | Later |
| Yukawa couplings (Stage 7.1) | Very hard | $\Omega$ integration on CY3 | Later |

---

## 6. Open Questions

1. **Why does Polytope 40 have max $h^0 = 2$?** It has more toric coordinates (20 vs 18), more SR generators (97 vs 79-87), and Z₂ symmetry. Is there a structural reason why higher h11 polytopes have *lower* max $h^0$?

2. **Are the $h^0 = 3$ bundles on h13-P0 cohomology-vanishing?** If $h^1 = h^2 = 0$, these are the cleanest possible 3-generation line bundles. We haven't verified this.

3. **Does h13-P1's Swiss cheese structure persist under $\alpha'$ corrections?** The LVS mechanism requires control over perturbative corrections. This depends on $\chi(X) = -6$ (small) and the Euler characteristic of the "small" divisor.

4. **Can we build a rank-4 or rank-5 bundle on any of these CYs?** This is the Standard Model question. Line bundles give $U(1)$; we need non-abelian gauge groups.
