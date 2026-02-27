# Contributing

Contributions welcome — especially scan runs, pipeline improvements, and negative results.

## What's Valuable

**Highest impact** (roughly ordered):

1. **Scan expansion** — Run `v4/pipeline_v4.py --scan` at h¹¹ values not yet covered. The landscape database (`v4/cy_landscape_v4.db`) currently holds 70,000 polytopes across h¹¹ = 13–40. High-h¹¹ ranges (h¹¹ ≥ 30) are sparsely sampled — more `--limit` depth there is valuable.

2. **Deep analysis** — Run `v4/pipeline_v4.py --deep --top N` on T2-scored candidates. The top champions (h28/P874, h28/P186 at SM score 87) need rank-n bundle construction and stability analysis.

3. **Stage 5 implementation** — Monad/extension bundle construction and stability checks. The `archive/analysis/rank_n_bundles.py` script has initial SU(4)/SU(5) scanners — extending with true stability analysis (beyond Hoppe) is the key gap.

4. **Picard-Fuchs / geometry** — The GL=12/D₆ polytope study ([GL12_GEOMETRY.md](GL12_GEOMETRY.md)) needs the PF PDE system in Mori coordinates. Also: quantum Yukawa corrections (Gromov-Witten invariants).

5. **F-theory** — Discriminant locus analysis on elliptic-fibered candidates (h17/poly25 has 15 elliptic fibrations).

6. **Bug fixes** — Especially cohomology alternatives to cohomCalg (which fails above 64 SR generators).

7. **Negative results** — If you prove something doesn't work, that's just as valuable. Add it to [CATALOGUE.md](CATALOGUE.md).

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

The current pipeline is `v4/pipeline_v4.py` with v5.2 scoring (100-point SM composite, 12 components). It uses a 4-tier architecture:

| Tier | Time | What it does |
|------|------|--------------|
| T0 | 0.1 s | Geometry + intersection algebra — kills ~85% |
| T1 | 0.5 s | Bundle screening — kills ~70% of T0 survivors |
| T2 | 3–30 s | Deep physics + SM scoring — top ~1K |
| T3 | 30 s+ | Full phenomenology + triangulation stability — top ~50 |

### Scan (T0 → T2)

```bash
# Scan h11=28, first 1000 polytopes, 4 workers
python v4/pipeline_v4.py --scan --h11 28 --limit 1000 -w 4

# Deep scan — first 50K polytopes at h11=28
python v4/pipeline_v4.py --scan --h11 28 --limit 50000 -w 4
```

### Deep analysis (T3)

```bash
# T3 on top 20 candidates by SM score
python v4/pipeline_v4.py --deep --top 20
```

### Rescore (after scoring formula changes)

```bash
python v4/pipeline_v4.py --rescore
```

All results are stored in `v4/cy_landscape_v4.db` (SQLite).

## PR Format

Include in your PR description:
- **What you ran**: which script, which parameters
- **Machine**: specs (cores, RAM) and runtime
- **h¹¹ range**: which Hodge numbers were covered
- **Polytope count**: how many scanned
- **Summary stats**: pass rates, any standout candidates

If you find a polytope with SM score ≥ 80, mention it explicitly — these are strong Standard Model candidates.

## How We Verify Contributions

The pipeline is deterministic — same polytope + same CYTools version = same numbers. Contributed results are spot-checked by re-running the pipeline on a random sample.

**Fingerprinting**: The database stores `cytools_version` and `poly_hash` (SHA-256 of sorted vertex matrix). This lets us detect version-dependent differences (e.g. CYTools 1.4.5 vs 2.x triangulation changes).

**What this catches**:
- CYTools version mismatches that silently change output
- Polytope indexing confusion (KS database ordering can vary)

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
