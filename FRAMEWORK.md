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

### Stage 6: Moduli Stabilization 🔶 IN PROGRESS

> *Fix the ~100 moduli to get definite 4D physics*

| Step | Description | Status |
|------|-------------|--------|
| 6.1 | Kähler moduli: Swiss cheese / LVS | ✅ Multiple candidates viable (best: h15/poly61 τ=14,300) |
| 6.2 | Complex structure moduli: flux superpotential | 🔶 Picard-Fuchs periods computed for GL=12/D₆ polytope (closed-form formula, 501 terms) |
| 6.3 | Vacuum energy / cosmological constant | ❌ |

### Stage 7: Phenomenological Checks 🔶 IN PROGRESS

| Step | Description | Status |
|------|-------------|--------|
| 7.1 | Yukawa couplings: $\int_X \Omega \wedge A \wedge A \wedge A$ | 🔶 D₆-invariant classical Yukawas computed (26 non-zero entries) for GL=12 polytope. Quantum corrections (GW invariants) not yet. |
| 7.2 | Proton decay rate (dimension-6 operators) | ❌ |
| 7.3 | Gauge coupling unification | ❌ |
| 7.4 | Neutrino masses | ❌ |

---

## 2. Current Position in the Pipeline

```
Stage 1 ──── Stage 2 ──── Stage 3 ──── Stage 4 ──── Stage 5 ──── Stage 6 ──── Stage 7
  CY           Divs         Line         Net          Vec          Moduli       Pheno
  Geom         Anal         Bundles      Chiral       Bundles      Stabil       Checks
  ✅            ✅            ✅            🔶            🔶            🔶            🔶
```

**We are working across Stages 5–7 in parallel.** Line bundle analysis (Stages 1–4) is complete for 12 candidates. Active fronts:
- (A) Stage 5: `rank_n_bundles.py` built — SU(4)/SU(5) scanners with direct sum + monad construction. First results on h14/poly2.
- (B) Stage 6.2: Picard-Fuchs periods for the GL=12/D₆ polytope (closed-form formula, 501 exact coefficients, GKZ orbit compression to 6 invariant moduli).
- (C) Stage 7.1: D₆-invariant classical Yukawa couplings (26 non-zero entries, two-sector structure). See [GL12_GEOMETRY.md](GL12_GEOMETRY.md).

---

## 3. Candidate Comparison

| | h14/poly2 | h17/poly25 | h15/poly61 | h17/poly63 |
|---|---|---|---|---|
| **Stage 1**: $\chi = -6$ | ✅ | ✅ | ✅ | ✅ |
| **Stage 2**: Rigid divisors | **13/13** | 13/17 | 10/15 | **13/13** |
| **Stage 2**: Swiss cheese | **YES** ($\tau=58.5$) | YES ($\tau=56$) | **YES** ($\tau=14,300$) | YES ($\tau=84$) |
| **Stage 3**: Clean $h^0=3$ | **320** | 170 | 110 | 218 |
| **Stage 3**: Max $h^0$ | 13 | 8 | 4 | **40** |
| **Stage 4**: All clean verified | ✅ | ✅ | ✅ | ✅ |
| **Stage 5**: Rank-4/5 bundles | 🔶 initial | ❌ | ❌ | ❌ |
| **Fibrations**: K3 / Ell | 3/3 | **6/15** | 3/3 | 5/10 |
| **Score** | **26/26** | **26/26** | 25/26 | **26/26** |
| **Best for…** | Heterotic | F-theory + triple-threat | LVS | Fibrations |

### GL=12 / D₆ Polytope (h¹¹=17, h²¹=20)

The polytope with the largest lattice automorphism group (|GL(Δ)| = 12, D₆) among all χ = −6 polytopes. Selected for deep theoretical study:

- **D₆ symmetry reduces moduli**: h¹¹_inv = 5, h²¹_inv = 6
- **26 D₆-invariant Yukawa couplings** organized into two sectors with one cross-coupling
- **Closed-form period formula**: CT[P^k] as a double factorial sum
- **GKZ system**: 6 orbit-compressed Mori coordinates define the invariant moduli space
- **Next step**: Picard-Fuchs PDE system in Mori coordinates

Full reference: [GL12_GEOMETRY.md](GL12_GEOMETRY.md). Analysis code: [picard_fuchs.py](picard_fuchs.py).

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
| Full pipeline on top candidates | **Easy** | All Stage 1-4 tools proven | ✅ DONE (12 runs) |
| Rank-4/5 bundles (Stage 5.1-5.2) | Medium-Hard | ✅ `rank_n_bundles.py` built | **Active** |
| Picard-Fuchs in Mori coordinates | Hard | `picard_fuchs.py` + sympy | **Active** |
| Individual $h^1, h^2$ (Stage 4.3) | Medium | Čech cohomology or exact sequences | Next |
| $\wedge^2 V$ Higgs count (Stage 5.5) | Hard | Requires Stage 5.1 first | After 5.1 |
| Flux superpotential (Stage 6.2) | Hard | Period integrals — closed-form available | Active |
| Yukawa couplings (Stage 7.1) | Very hard | Classical done, quantum (GW) needed | Active |
| F-theory discriminant locus | Hard | CYTools fiber analysis + Kodaira | Next |

---

## 6. Open Questions

1. **Can we find a truly stable rank-4/5 bundle with net chirality = 3?** `rank_n_bundles.py` finds candidates (100+ SU(4) direct sums, 3 Hoppe-stable monads on h14/poly2). But direct sums are polystable at best. Need genuinely indecomposable stable bundles.

2. **What gauge algebras arise from the 15 elliptic fibrations on h17/poly25?** Kodaira fiber classification would determine the non-abelian gauge content in F-theory.

3. **Can the Picard-Fuchs system in Mori coordinates be solved?** The GL=12/D₆ polytope has 6 invariant complex structure moduli. The PF system in the naive 1-parameter model has degree ∼72 (= Vol(Δ*)). In proper Mori coordinates z₁…z₆, it should factor into tractable coupled PDEs.

4. **Does the D₆-invariant Yukawa sector structure (A/B/cross) constrain fermion mass textures?** The 26 non-zero couplings organize into two sectors with one cross-coupling κ(O1,O2,O3) = 18. This may constrain CKM-like mixing.

5. **Does h15/poly61's extreme τ = 14,300 translate to viable moduli stabilization in a concrete flux model?**  Can the absence of dP divisors be compensated by other instanton sources?
