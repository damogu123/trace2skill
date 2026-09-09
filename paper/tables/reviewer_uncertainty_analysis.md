# Reviewer-requested uncertainty and sensitivity analysis

These are task-level descriptive analyses. They do not estimate run-to-run
variation because each task/method configuration has one execution.

## Solve-rate uncertainty

| Method | Solved | Rate | Wilson 95% interval |
|---|---:|---:|---:|
| Auto SKILL.md | 5/6 | 0.833 | [0.436, 0.970] |
| Generic checklist | 5/6 | 0.833 | [0.436, 0.970] |
| Reflexion memory | 5/6 | 0.833 | [0.436, 0.970] |
| Length-matched Reflexion | 4/6 | 0.667 | [0.300, 0.903] |
| No memory | 4/6 | 0.667 | [0.300, 0.903] |

## Paired common-solved uncertainty

Negative deltas favor Auto SKILL.md. Intervals are exact-enumeration
task-resampling bootstrap percentile intervals over the common-solved tasks.

| Baseline | n | Cycle delta (95% interval) | Token delta (95% interval) |
|---|---:|---:|---:|
| Generic checklist | 4 | 0.00 [-0.75, 0.75] | -11,816 [-30266, 7078] |
| Reflexion memory | 4 | -1.00 [-2.00, 0.25] | -22,828 [-44394, -1262] |
| Length-matched Reflexion | 4 | -1.00 [-1.75, -0.25] | -27,258 [-41409, -13106] |
| No memory | 3 | -1.00 [-1.78, -0.22] | -25,573 [-47137, -2454] |

## Token sensitivity

| Method | Mean | Median | Leave-one-task-out mean range |
|---|---:|---:|---:|
| Auto SKILL.md | 56,867 | 52,645 | [47974, 62676] |
| Generic checklist | 71,694 | 55,994 | [59790, 78195] |
| Reflexion memory | 65,915 | 68,543 | [59916, 70802] |
| Length-matched Reflexion | 75,231 | 75,249 | [67633, 82841] |
| No memory | 92,031 | 85,286 | [78329, 101236] |

## Structural-control outlier check

Auto SKILL.md mean/median tokens: 111,978 / 86,436.
Format-shuffled mean/median tokens: 102,006 / 86,502.
After excluding black_193, means are 82,639 and 85,556, respectively. This confirms that the aggregate token ranking is outlier-sensitive.
