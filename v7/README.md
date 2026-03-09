# v7 — Beyond the Standard Model Archetype

**Era**: Post-B-48 (March 2026–)  
**Central question**: *"Does a correct description of reality look like the Standard Model, or are we discarding better candidates because they don't fit our template?"*

---

## Motivation

v6 established a universal D3-tadpole obstruction for perturbative SU(4) and
SU(5) monad bundles on all five priority χ=−6 entries (0/104,145 slope-feasible
candidates pass tadpole across B-45–B-48). Two interpretations are possible:

1. **Obstruction interpretation**: the KS χ=−6 cluster genuinely cannot support
   heterotic SM vacua via perturbative monads — correct answer is "not here."
2. **Filter bias interpretation**: the pipeline is tuned to confirm the SM we
   already know. A compactification that extends or supersedes the SM fails our
   filters by construction, even if it better describes reality.

v7 pursues both tracks simultaneously:

- **Track A** (obstruction):  non-perturbative completions — flux tadpole
  cancellation, extension bundles, spectral covers, gaugino condensation
- **Track B** (discovery):  observable-first scoring — rank candidates by
  physical predictions (dark matter mass, proton decay rate, neutrino masses)
  rather than group-theoretic SM-matching

---

## What Changes from v6

| Dimension | v6 | v7 |
|-----------|----|----|
| **Tadpole** | D3 must be satisfied by bundle alone | Allow H-flux contribution: $n_{D3}^{\rm bundle} + n_{D3}^{\rm flux} \leq \chi(X)/24$ |
| **Gauge group** | Must be SU(4) or SU(5) GUT → SM | Any stable bundle; ask what gauge group it breaks to |
| **Bundle class** | Perturbative monads only | Extension bundles, spectral covers, non-perturbative |
| **Generation count** | Exactly χ(V)=±3, no vector-like pairs | Net=3 required; vector-like pairs allowed and counted |
| **Scoring basis** | Group-theoretic SM-matching | Physical observables: DM mass window, proton decay Γ, neutrino Δm² |
| **Research question** | "Can we confirm the SM?" | "What does this geometry predict?" |

---

## Architecture

### Track A — Non-perturbative completion

Continue on the five priority T4 entries from v6. Relax perturbativity.

| Stage | Method | New capability |
|-------|--------|----------------|
| A1 | H-flux tadpole cancellation | Flux quanta $(H_{abc})$ contribute negative $n_{D3}$; scan flux lattice |
| A2 | Extension bundles | $0 \to L_1 \to V \to L_2 \to 0$ (rank-2 building blocks → SU(n) via tensor) |
| A3 | Spectral covers | Camara–Font–Ibáñez construction on elliptic fibrations |
| A4 | Instanton corrections | Check whether worldsheet instantons lift the obstruction |

### Track B — Observable scoring

Rescore all v6 DB entries (and new scans) on physical output rather than
group-theoretic criteria.

| Observable | Formula | Why it matters |
|------------|---------|----------------|
| Dark matter mass | $m_{\rm DM} \sim m_{3/2} \sim e^{-2\pi/g_s} M_{\rm Pl}$ | Testable at detectors |
| Proton decay | $\Gamma_p \propto (M_{\rm GUT})^{-4}$, $M_{\rm GUT}$ from gauge coupling unification | Testable at Hyper-K |
| Neutrino masses | $m_\nu \sim v^2/M_R$, $M_R$ from $B-L$ breaking scale | Constraints from oscillation experiments |
| Cosmological constant | $\Lambda \sim V_{\rm AdS} + \delta V_{\rm SUSY}$ | Anthropic or geometric selection |

### Scoring (v7 — observable-first, 100 pts)

```python
V7_SCORE_WEIGHTS = {
    # Geometry (carry forward from v6 T4 verification)
    't4_verified':          10,   # triangulation + T4 tier confirmed
    'tri_stable':            5,   # c₂ and κ stable across triangulations

    # Generation structure (relaxed)
    'net_gen_3':            15,   # |χ(V)| = 3 net generations (required)
    'vector_like_light':     5,   # vector-like pairs with mass > M_GUT (safe)

    # Tadpole (with flux)
    'tadpole_flux_ok':      15,   # n_D3_bundle + n_D3_flux ≤ χ/24

    # Observable predictions
    'dm_mass_window':       15,   # m_DM in 100 GeV – 10 TeV window
    'proton_decay_rate':    10,   # Γ_p in Hyper-K sensitivity range
    'neutrino_mass_hier':   10,   # normal or inverted hierarchy predicted
    'gauge_unification':    10,   # α_GUT within 10% of observed at M_GUT
    'susy_breaking_scale':   5,   # m_3/2 in 10 TeV – 100 TeV window
}
# Total: 100 pts
```

---

## Database

- **File**: `v7/cy_landscape_v7.db`
- **Schema**: extends v6 with new columns for flux quanta, non-pert bundle type,
  observable predictions
- **Source**: v6 DB is read-only reference; v7 DB starts from the 5 priority
  T4-verified entries and expands

---

## Priority Entries (inherited from v6)

| Entry | h¹¹_eff | Score | Why priority |
|-------|---------|-------|-------------|
| h22/P682  | 19 | 85 | Highest non-champion score, SM charge structure |
| h23/P36   | 19 | 82 | Strong Yukawa hierarchy |
| h21/P9085 | 19 | 80 | T4-verified, triangulation stable |
| h25/P860  | 20 | 78 | Largest Kähler cone flexibility |
| h26/P11670| 28 | 76 | Original monad test case |

---

## Immediate Next Steps

See `BACKLOG.md` (top-level) v7 section for task list.

**B-49** (first v7 task): H-flux tadpole scan on h22/P682 — compute flux
lattice, find quanta that cancel the $\Delta n_{D3} \approx 90$ excess found
in B-47a/B-48, check remaining consistency constraints.
