# v4 Pipeline Changelog

## v4.1 — 2026-02-26: Evidence-Based Tuning from h22-30 Analysis

Based on comprehensive analysis of 9,000 polytopes (1,134 T2-scored) across
h11=22–30. All changes driven by Pearson correlations and distributional
evidence. See PROCESS_LOG.md for full analysis.

### Threshold Changes

| Parameter | v4.0 | v4.1 | Rationale |
|-----------|------|------|-----------|
| EFF_MAX   | 20   | **22** | 46% of score-75+ polytopes sat at eff=20 ceiling. At h30, 535 polytopes blocked solely by eff>20. Raising to 22 doubled T0 pass rate at h26 (142→282). |

### Scoring Weight Changes (total remains 100)

| Component | v4.0 | v4.1 | Rationale |
|-----------|------|------|-----------|
| yukawa_hierarchy | 25 | **27** | Remains THE key discriminator. Pearson r=+0.31 with score. All elite polytopes (≥75) have yuk_h 11.6× population average. |
| dp_divisors | 5 | **0 (removed)** | n_dp ANTI-correlates with score (r=−0.19). Elite polytopes have n_dp=5.0 vs population 6.5. Rewarding more dP was actively wrong. |
| fibration_sm | 5 | **3** | n_k3_fib anti-correlates with score (r=−0.22). Keep SM/GUT gauge group reward but reduce weight. Fibration *count* doesn't help. |
| vol_hierarchy | — | **5 (new)** | Volume hierarchy >1000 averages 6.5 pts higher than <100. Previously unscored. Independent signal — not just LVS proxy. Graded: ≥1000→5, ≥100→3, ≥10→1. |

### Unchanged Components

- clean_bundles: 10 (log₂ scaled)
- yukawa_rank: 15
- lvs_binary: 5
- lvs_quality: 10
- tadpole_ok: 5
- mori_blowdown: 5
- d3_diversity: 5
- clean_depth: 5
- clean_rate: 5

### Impact

- Champion h30/P289 rescores from 82 → 92 (gains vol_hierarchy + yukawa boost)
- h26 T0 pass rate: 142 → 282 (2× candidates from EFF_MAX change alone)
- Expected: more high-eff polytopes at h26-40 now visible to the pipeline

### Scan: h26-40 with v4.1

Launched 2026-02-26 with 14 workers. Re-scans h26-30 with new thresholds
(adds eff=21-22 polytopes + rescores existing), then extends through h31-40.

---

## v4.0 — 2026-02-26: Initial Evidence-Based Scoring

Created from analysis of 6,578 v3 polytopes (h11=13–21). Major changes from v3:

### Removed (zero discrimination)
- `chi_match` (was 10 pts): χ=−6 for all candidates by construction
- `h0_diversity` (was 5 pts): anti-correlates with SM quality

### Promoted
- `yukawa_hierarchy` (10→25): THE key discriminator — every score-90
  polytope has hierarchy >1000×

### Split
- `lvs_compatible` (15 → lvs_binary 5 + lvs_quality 10): graded τ/V^{2/3}
  replaces binary swiss cheese check

### Added
- `clean_rate` (5 pts): n_clean/n_checked — structural SM-friendliness
- `clean_depth` (5 pts): first clean hit position in bundle search
- `d3_diversity` (5 pts): distinct D³ values among clean bundles

### T1 Efficiency Fix
- T1_BUNDLE_CAP=500 (was uncapped — caused indefinite hangs)
- T1_WALL_SEC=120 (hard per-polytope wall-time)
- Progress reporting every 20 polytopes

### Gap-Priority Scheduling
- Sorted by gap descending before T1 dispatch
- `pool.imap_unordered(chunksize=1)` for responsive load balancing

### --scan Range Fix
- `--h11 A B` where B>A now correctly scans range(A, B+1)
- Previously treated as list [A, B], skipping intermediate values
