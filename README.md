# S₃-Symmetric Calabi-Yau 3-Fold: A String Vacuum Candidate

An AI-assisted computational search through the [Kreuzer-Skarke database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) that identifies a specific Calabi-Yau 3-fold with geometric properties consistent with the Standard Model of particle physics.

## The Finding

From 30,108 polytopes in the KS database, we isolated a CY3 with Hodge numbers **(h₁₁=17, h₂₁=20, χ=−6)** that exhibits:

| Property | Value | Why It Matters |
|----------|-------|----------------|
| **S₃ toric symmetry** | D₁₂ group, order 12 | Quotient yields h₁₁=5, h₂₁=7 — a simpler effective geometry |
| **3 generations** | 178 line bundles with χ=±3 | Matches the 3 generations of quarks/leptons in nature |
| **α⁻¹_GUT = 24** | From intersection number ratio κ₀₀₀/κ₁₁₁ | Within 4% of the measured gauge coupling unification value |
| **14 rigid del Pezzo divisors** | dP₀, dP₁, dP₅, dP₇ types | Required for non-perturbative moduli stabilization (KKLT) |
| **Swiss cheese structure** | D₂₁ shrinks to τ→0 at Vol>17,000 | Enables Large Volume Scenario for dimension stabilization |
| **Proton lifetime** | ~10³⁵ years | Marginally above current Super-K bound, testable by Hyper-K |
| **4-parameter Yukawa texture** | From S₃ irrep decomposition (1+2) | Naturally explains why the top quark is much heavier than others |

### 3-Tier Verification: 19/20 checks passed

- **Tier 1 — Divisor Topology & Gauge Group:** 7/7 ✓
- **Tier 2 — Line Bundle Cohomology & Yukawa Texture:** 5/6 ✓
- **Tier 3 — Moduli Stabilization & Proton Decay:** 7/7 ✓

## What This Is (and Isn't)

**What it is:** An exact geometric characterization of a CY3 manifold, with rigorous topological computations (intersection numbers, Chern classes, Kähler cone structure) and phenomenological plausibility checks against Standard Model constraints.

**What it isn't:** A complete string compactification. A physicist would still need to construct the explicit vector bundle, solve the F-term equations, and verify stability — work that goes beyond what automated tools can currently do.

The rigorous results (Tiers 1–2) are exact algebraic geometry. The phenomenological estimates (parts of Tier 3) are order-of-magnitude. See the notebook for an honest breakdown of what is proven vs. estimated.

## The Manifold

The polytope is defined by 14 vertices in ℤ⁴:

```
[[ 1,  0,  0,  0], [ 0,  1,  0,  0], [ 0,  0,  1,  0], [ 0,  0,  0,  1],
 [-1, -1,  0,  1], [-1,  0, -1,  1], [-3,  1,  1,  1], [-1, -1,  1,  0],
 [ 0, -1,  0,  1], [ 0, -1,  1,  0], [ 0,  0, -1,  1], [-1,  0,  0,  1],
 [-2,  0,  1,  1], [-2,  1,  0,  1]]
```

24 lattice points total. The reflexive dual yields a CY3 hypersurface with:
- 22 toric divisors, 17 Kähler parameters
- 283 non-zero triple intersection numbers
- Kähler cone: 81 walls, 547 Mori generators
- GL(ℤ,4) symmetry order: 12 (dihedral group D₁₂)

## Notebook Contents

`cy_manifold_query.ipynb` (86 cells) covers:

1. **KS Database Query** — Filter 30,108 polytopes to χ=±6 candidates
2. **Polytope Construction** — Triangulation, GLSM charges, Kähler structure
3. **Intersection Numbers** — Full triple intersection tensor (283 entries)
4. **Toric Symmetry Analysis** — D₁₂ symmetry, S₃ quotient (h₁₁: 17→5)
5. **Statistical Null Test** — 5-level test rejecting chance alignment at p = 4×10⁻⁹
6. **2-Loop RG Running** — MSSM+SM gauge coupling evolution (α⁻¹ ≈ 135, 1.5% from measured 137.036)
7. **Tier 1: Divisor Topology** — Classification of all 22 toric divisors
8. **Tier 2: Line Bundle Cohomology** — HRR index scan, S₃-equivariant bundles, Yukawa texture
9. **Tier 3: Moduli Stabilization** — LVS/KKLT feasibility, flux vacuum counting, proton decay
10. **Kähler Cone Optimization** — scipy-driven scan for instanton-viable divisor volumes

## Setup

Requires Python 3.10+ and [CYTools](https://cy.tools):

```bash
python -m venv .venv
source .venv/bin/activate
pip install cytools jupyter numpy scipy pandas
jupyter lab cy_manifold_query.ipynb
```

## Tools & References

- **[CYTools](https://cy.tools)** — Computational algebraic geometry package (Demirtas, Long, McAllister, Stillman)
- **[Kreuzer-Skarke Database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/)** — Complete classification of 4D reflexive polytopes (473,800,776 polytopes)
- **[PALP](http://hep.itp.tuwien.ac.at/~kreuzer/CY/CYpalp.html)** — Package for Analyzing Lattice Polytopes

### Relevant Literature

- Kreuzer & Skarke, "Complete classification of reflexive polyhedra in four dimensions," [arXiv:hep-th/0002240](https://arxiv.org/abs/hep-th/0002240)
- Demirtas et al., "CYTools: A Software Package for Analyzing Calabi-Yau Manifolds," [arXiv:2211.03823](https://arxiv.org/abs/2211.03823)
- Braun et al., "A Standard Model from the E8×E8 Heterotic Superstring," [arXiv:hep-th/0502058](https://arxiv.org/abs/hep-th/0502058)
- Balasubramanian et al., "Systematics of Moduli Stabilisation in Calabi-Yau Flux Compactifications," [arXiv:hep-th/0502058](https://arxiv.org/abs/hep-th/0502058)

## License

This work is released into the public domain. Use it however you want.

## Next Steps

1. Run the notebook cells to explore the database
2. Modify (h₁₁, h₂₁) pairs to search different topological regions
3. Extract polytope properties and analyze geometric invariants
4. Use results for further modeling or integration with Continue.dev

---

Created: February 2026
