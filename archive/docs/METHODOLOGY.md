# Methodology: AI-Assisted Calabi-Yau Manifold Analysis

## Overview

This project was developed through iterative collaboration between a human researcher and an LLM coding assistant (Claude), using CYTools 1.4.5 on a consumer laptop (Dell, Python 3.13). The workflow demonstrates how AI-assisted development can accelerate computational algebraic geometry research, while also documenting the specific pitfalls encountered.

## Development Timeline

| Phase | Duration | What happened |
|-------|----------|---------------|
| Setup | ~30 min | CYTools install, venv configuration, KS database download |
| Q1: Database query | ~1 hr | Filter KS database for χ=±6, identify 104 candidate polytopes |
| Q1b: Symmetry scan | ~2 hr | GL(ℤ,4) automorphism scan, find GL=12 polytope |
| Polytope deep dive | ~2 hr | Construct CY3, compute intersection numbers, Kähler cone |
| Tier 1 | ~1 hr | Divisor classification, tadpole, gauge group viability |
| Tier 2 | ~2 hr | HRR index implementation, line bundle scan, S₃ analysis |
| Tier 3 | ~3 hr | LVS/KKLT feasibility, Kähler cone optimization |
| Documentation | ~1 hr | README, GitHub setup, this document |

Total: approximately 12 hours of interactive sessions.

## API Discovery Challenges

### Problem: Wrong Method Names

CYTools 1.4.5 has method names that differ from what documentation or intuition suggests:

```python
# WRONG — raises AttributeError
kc = cy.kahler_cone()
mc = cy.mori_cone()

# CORRECT
kc = cy.toric_kahler_cone()
mc = cy.toric_mori_cone()
```

**How discovered:** The LLM initially generated `cy.kahler_cone()` based on standard mathematical terminology. The `AttributeError` was caught, and `dir(cy)` was used to discover the correct method names. This pattern repeated several times.

### Problem: Missing Line Bundle Cohomology

CYTools does not provide a built-in method for computing individual sheaf cohomology groups $h^i(X, \mathcal{O}(D))$. Most string phenomenology literature assumes this is available.

**Workaround:** Implemented the Hirzebruch-Riemann-Roch index theorem directly:

$$\chi(X, \mathcal{O}(D)) = \frac{1}{6}\kappa_{abc}\,n^a n^b n^c + \frac{1}{12}\,c_{2,a}\,n^a$$

where $\kappa_{abc}$ are the triple intersection numbers and $c_{2,a} = \int_X c_2 \wedge D_a$.

This gives the alternating sum $h^0 - h^1 + h^2 - h^3$, not individual cohomology dimensions. For CY3 with $c_1 = 0$, Serre duality gives $h^3 = h^0(\mathcal{O}(-D))$, so for "ample enough" line bundles, $\chi$ determines the generation count.

### Problem: Toric vs. Basis Index Confusion

CYTools stores intersection numbers using **toric divisor indices** (0 to $n_{\text{points}}-1$, e.g. 0–21 for our manifold), while the Kähler parameters use **basis indices** (0 to $h^{1,1}-1$, e.g. 0–16).

```python
# WRONG — IndexError or wrong values
kappa_000 = intnums[(0, 0, 0)]  # ← this IS toric index 0, which happens to work
kappa_basis = intnums[(17, 17, 17)]  # ← ERROR: index 17 is toric, not basis

# CORRECT — convert basis to toric first
div_basis = cy.divisor_basis()  # e.g., [0, 1, 2, 5, 6, 7, ...]
toric_idx = div_basis[a]        # basis index a → toric index
kappa_aaa = intnums.get((toric_idx, toric_idx, toric_idx), 0)
```

**How discovered:** After initial runs produced nonsensical intersection numbers, systematic printing of `cy.divisor_basis()` revealed the mapping. The LLM proposed both wrong and right approaches; the user's domain knowledge flagged the inconsistency.

## The HRR Workaround: Design Decisions

The `chi_line_bundle` function needed careful handling of symmetry factors:

```python
def chi_line_bundle(n_vec, intnums, c2_vals, n_toric):
    cubic = 0.0
    for (a, b, c), kval in intnums.items():
        # CYTools stores each triple (a,b,c) with a ≤ b ≤ c exactly once
        if a == b == c:
            cubic += kval * n[a]**3            # factor 1
        elif a == b:
            cubic += 3 * kval * n[a]**2 * n[c]  # factor 3 (symmetry)
        elif b == c:
            cubic += 3 * kval * n[a] * n[b]**2
        elif a == c:
            cubic += 3 * kval * n[a]**2 * n[b]
        else:
            cubic += 6 * kval * n[a] * n[b] * n[c]  # factor 6
    cubic /= 6.0
    linear = np.dot(c2_vals, n) / 12.0
    return cubic + linear
```

**Validation:** For $D = 0$ (trivial bundle), $\chi = 0$ as expected (since $\chi(\mathcal{O}_X) = 0$ on CY3 with strict SU(3) holonomy). For single divisors $D_a$, cross-checked against the manual formula $\chi = \kappa_{aaa}/6 + c_{2,a}/12$.

## Kähler Cone Optimization

### The Problem

At the tip of the stretched Kähler cone, all divisor volumes are large ($\tau > 50$). The LVS and KKLT moduli stabilization mechanisms require at least one rigid del Pezzo divisor with small volume ($\tau \sim 1$–10) for non-perturbative effects.

### The Solution

Used scipy's Nelder-Mead optimizer to search the Kähler cone interior for points where specific rigid divisors have small volumes:

1. **Random scan** (5000 points): Sample random perturbations of the tip, project back into the cone if outside, compute divisor volumes.
2. **Targeted optimization**: For each of the 14 rigid dP divisors, minimize $\tau_a$ subject to:
   - Point stays inside the Kähler cone: $M \cdot t \geq 0$ (81 wall conditions)
   - CY volume stays large: $\text{Vol}(X) > 50$
   - All Kähler parameters positive: $t^a > 0$

### Key Finding

D₂₁ (a dP₀ from the S₃ triplet {D₁₇, D₂₀, D₂₁}) can be shrunk smoothly to $\tau \to 0$ while maintaining $\text{Vol} > 17{,}000$, staying inside the Kähler cone boundary. The interpolation from the cone interior to the boundary gives:

| λ | τ(D₂₁) | Vol(CY) | W_np |
|---|---------|---------|------|
| 0.0 | → 0 | 16,984 | ~ 1 |
| 0.1 | 1.52 | 17,048 | 7×10⁻⁵ |
| 0.2 | 3.92 | 17,248 | 5×10⁻¹¹ |
| 0.3 | 6.89 | 17,563 | 6×10⁻¹⁹ |
| 0.5 | 24.50 | 18,135 | ~ 0 |

The $\lambda = 0.2$ point ($\tau \approx 4$, $W_{\rm np} \sim 10^{-11}$) is in the ideal regime for KKLT stabilization.

## Iterative Debugging Patterns

### Pattern 1: "Try → Error → dir() → Fix"

Roughly 40% of API calls to CYTools followed this pattern:
1. LLM generates a plausible method call
2. Python raises `AttributeError` or `TypeError`
3. Run `dir(obj)` or `help(obj.method)` to find the correct API
4. Fix and re-run

This is analogous to reading documentation, but faster in an interactive session.

### Pattern 2: "Compute → Cross-check → Debug index confusion"

Another ~30% of debugging involved index mapping errors:
1. Compute a quantity using one index convention
2. Cross-check against known values (e.g., $\sum \kappa_{abc} = \chi$)
3. Discover the cross-check fails
4. Realize toric vs. basis index mismatch
5. Add explicit index mapping

### Pattern 3: "Physics intuition → Code → Surprise → Investigate"

The most productive pattern:
1. User suggests a physical quantity to compute
2. LLM writes the code
3. Result is unexpected (e.g., all rigid divisors have large $\tau$)
4. Both analyze whether this is a real constraint or an artifact
5. Leads to new investigation (Kähler cone optimization)

## What the LLM Did Well

- **Rapid prototyping**: Turning mathematical formulas into Python code in seconds
- **Error recovery**: Quickly adapting when API calls fail
- **Systematic scanning**: Writing nested loops over parameter spaces
- **Cross-checking**: Implementing consistency checks (e.g., $\sum \kappa = \chi$)
- **Documentation**: Generating formatted output, markdown tables, plot labels

## What Required Human Judgment

- **Physical interpretation**: Is $\alpha_{\rm GUT}^{-1} = 24$ meaningful or coincidental?
- **Rigor assessment**: Which results are theorems vs. order-of-magnitude estimates?
- **Strategy**: Deciding to pursue Kähler cone optimization instead of giving up
- **Scope management**: Knowing when "19/20" is good enough vs. which FAILs matter
- **Honest framing**: The LLM initially presented results more confidently than warranted; the user pushed for honest assessment of what's rigorous vs. hand-wavy

## Reproducibility

All computations are deterministic given:
- CYTools 1.4.5
- The polytope vertex matrix (14 vertices in ℤ⁴, stored in `scan_manifold.py`)
- NumPy's default triangulation (which CYTools uses internally)

The one non-deterministic element is the Kähler cone random scan (seed=42 for reproducibility) and the Nelder-Mead optimization (which depends on starting points but converges to the same basin).

## Lessons for AI-Assisted Mathematical Research

1. **Domain expertise is irreplaceable.** The LLM can compute $\kappa_{abc}$, but deciding *which* $\kappa_{abc}$ matters requires physics knowledge.

2. **API documentation matters more than mathematical knowledge.** 80% of debugging was API issues, not math errors.

3. **Interactive verification beats batch computation.** Running one cell at a time, checking output, and adjusting is far more productive than writing a complete script and running it once.

4. **The LLM's confidence doesn't correlate with correctness.** Both the A₄ misidentification (later corrected to D₁₂) and the initial Tier 3 scoring required human skepticism.

5. **Code is the proof.** The notebook is a reproducible record of exactly what was computed. Every number has a cell that generated it.
