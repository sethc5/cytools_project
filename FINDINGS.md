# What We Found and Why It Matters

## The Question

Can the geometry of a tiny, curled-up extra dimension explain why our universe has exactly three generations of matter, why the strong and weak forces have the strengths they do, and why protons don't decay?

String theory says yes — if you can find the right shape. That shape is a **Calabi-Yau manifold**, a 6-dimensional space so small it's invisible, but whose topology determines the particle physics we observe. There are hundreds of millions of candidate shapes in the Kreuzer-Skarke database. Almost none of them give three generations of matter.

## What We Did

We searched the database for Calabi-Yau manifolds with Euler characteristic χ = −6 — the topological condition for exactly **three generations** of quarks and leptons. Out of ~500,000 known shapes, only 104 satisfy this at the simplest level.

We then ran a 20-check verification pipeline on the most symmetric candidate (a polytope with 14 vertices, GL symmetry order 12, and Hodge numbers h¹¹ = 17, h²¹ = 20):

| Tier | What It Tests | Score |
|------|--------------|-------|
| **1. Geometry** | Rigid divisors, Kähler cone, gauge group embedding | **7/7** |
| **2. Particle physics** | Line bundle spectrum, 3-generation bundles, Yukawa texture | **5/6** |
| **3. Stability** | Moduli stabilization (LVS/KKLT), proton lifetime, vacuum structure | **7/7** |

**Total: 19/20.** This manifold passes every check we can compute on a laptop.

## The Key Results

- **14 rigid del Pezzo divisors** — surfaces inside the manifold where gauge fields can live. You need at least one; this manifold has fourteen.

- **178 line bundles with |χ| = 3** — each a distinct way to get exactly three generations of matter from the geometry. Most manifolds have zero or one.

- **D₁₂ discrete symmetry** — the manifold has a dihedral-12 symmetry group. Quotienting by its S₃ subgroup reduces to h¹¹ = 5, h²¹ = 7, giving a simpler effective geometry that still produces three generations.

- **α⁻¹_GUT = 24 from pure topology** — the ratio of two intersection numbers gives the inverse gauge coupling at unification. Running this down through the MSSM renormalization group gives α⁻¹_em ≈ 135.0 at the electron mass, within 1.5% of the measured 137.036.

- **Instanton-viable blow-up cycle** — one del Pezzo divisor (D₂₁) can be smoothly shrunk to the non-perturbative regime (τ ~ 4) while keeping the overall volume large (Vol > 17,000), enabling KKLT moduli stabilization with W_np ~ 10⁻¹¹.

## Why It Matters

**For string phenomenology:** Most "string vacuum" papers start with a manifold chosen for convenience and then check a few properties. We did the opposite — started from the physical constraint (χ = −6) and ran every check we could compute. The fact that one manifold passes 19/20 is not proof of anything, but it's a concrete, reproducible data point that the field can build on.

**For the methodology:** This entire analysis was done by a non-expert using an LLM and CYTools on a consumer laptop in ~12 hours. The traditional version of this work would require a PhD student, a computing cluster, and months. If the tools and the approach are sound, it means the barrier to entry for computational string phenomenology just dropped by an order of magnitude.

**What it does NOT prove:** This is not evidence that string theory describes our universe. The 19/20 scorecard mixes exact algebraic geometry theorems with order-of-magnitude estimates. The gauge coupling "prediction" has ~1.5% error and depends on assumptions about the GUT group. The proton decay estimate spans 10 orders of magnitude of uncertainty. An honest summary: *the geometry is consistent with known physics at every level we can check, but "consistent with" is far weaker than "predicts."*

## Reproduce It

```bash
git clone https://github.com/sethc5/cytools_project.git
pip install cytools numpy scipy
python scan_manifold.py          # runs all 3 tiers on the GL=12 polytope
python batch_scan.py --chi -6    # scans the KS database for more candidates
```

The full analysis notebook (`cy_manifold_query.ipynb`) contains every computation, with outputs, in 90 cells.
