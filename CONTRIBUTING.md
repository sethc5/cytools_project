# Contributing

Contributions welcome — especially scan runs, pipeline improvements, and negative results.

## What's Valuable

**Highest impact** (roughly ordered):

1. **Scan expansion** — Run `scan_chi6_h0.py` with higher limits at h¹¹ = 15–17. Or add h¹¹ values we haven't touched (h¹¹ = 25+). The first 100 polytopes per h¹¹ is just scratching the surface.

2. **Pipeline results** — Screen your scan output through T1 → T1.5 → T2 and PR the CSVs.

3. **Stage 5 implementation** — Monad/extension bundle construction and stability checks. This is the critical gap: line bundles only give U(1), but SM needs non-abelian gauge groups.

4. **F-theory** — Discriminant locus analysis on elliptic-fibered candidates.

5. **Bug fixes** — Especially cohomology alternatives to cohomCalg (which fails above 64 SR generators).

6. **Negative results** — If you prove something doesn't work, that's just as valuable. Add it to [CATALOGUE.md](CATALOGUE.md).

## Setup

### Local (tested on Ubuntu/Fedora, Python 3.12–3.13)

```bash
git clone https://github.com/sethc5/cytools_project.git
cd cytools_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

CYTools 1.4.5 needs some native dependencies (`pplpy`, `python-flint`). If `pip install cytools` fails, check [CYTools install docs](https://cy.tools/docs/getting-started/).

### Codespace

The repo has a `.devcontainer/devcontainer.json`. Just open in GitHub Codespaces — CYTools and all dependencies are pre-configured.

## Running the Pipeline

### 1. Scan

```bash
# Edit limit= in scan_chi6_h0.py to control how many polytopes per h11
python scan_chi6_h0.py
# Output: results/scan_chi6_h0_v2.log
```

### 2. Tier 1 (fast, ~1s/polytope)

```bash
python tier1_screen.py
# Output: results/tier1_screen_results.csv
```

### 3. Tier 1.5 (intermediate, ~5s/polytope)

```bash
python tier15_screen.py --csv results/tier1_screen_results.csv
# Output: results/tier15_screen_results.csv
```

### 4. Tier 2 (deep, ~3min/polytope)

```bash
# Single range:
python tier2_screen.py --csv15 results/tier15_screen_results.csv --start 0 --end 20

# Parallel batch (4 pipes):
./run_t2_batch.sh
# Output: results/tier2_screen_results.csv
```

## PR Format

Include in your PR description:
- **What you ran**: which script, which parameters
- **Machine**: specs (cores, RAM) and runtime
- **h¹¹ range**: which Hodge numbers were covered
- **Polytope count**: how many scanned
- **Summary stats**: pass rates, any standout candidates

Put output CSVs in `results/`. If you find a polytope with T2 score ≥ 40 or max h⁰ ≥ 10, mention it explicitly — these are the ones worth a full pipeline run.

## Code Style

- No strict linter enforced. Keep it readable.
- Use the CYTools API conventions documented in [MATH_SPEC.md](MATH_SPEC.md).
- Always use `in_basis=True` for intersection numbers and c₂. See [MATH_SPEC.md](MATH_SPEC.md) bugs section.
- Test on at least one known polytope (h13/poly1 is the standard benchmark).

## Documenting Negative Results

If you prove something doesn't work:

1. Add it to the "Ruled Out" section of [CATALOGUE.md](CATALOGUE.md)
2. Include: polytope ID, what you tried, why it fails, evidence (script name or brief calculation)
3. This prevents others from repeating dead-end work

## Questions

Open an issue. Or just PR and we'll discuss in review.
