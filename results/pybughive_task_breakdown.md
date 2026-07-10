# PyBugHive Task Breakdown

Date: 2026-05-27

Notation: `S c/tok` means solved with `c` diagnosis-edit-test cycles and `tok` total tokens. `F` means unsolved.

## Held-Out Task Metadata

| Task | Repo | Family | Failure summary |
| --- | --- | --- | --- |
| `pybughive_black_1493` | `black` | `test_failure_triage` | Black finds root incorrectly |
| `pybughive_black_185` | `black` | `test_failure_triage` | Trailing comma after from-import |
| `pybughive_black_389` | `black` | `test_failure_triage` | Importing `__future__` as renamed import |
| `pybughive_black_59` | `black` | `test_failure_triage` | Internal error on complex variable type |
| `pybughive_discord_py_7818` | `discord.py` | `test_failure_triage` | Nested groups with explicit class |
| `pybughive_scrapy_1265` | `scrapy` | `test_failure_triage` | Backward compatibility for relocated import |
| `pybughive_scrapy_2552` | `scrapy` | `test_failure_triage` | Invalid request URL without real scheme |

## Outcome Matrix

| Task | `auto_skill` | `format_shuffled_skill` | `generic_checklist` | `length_matched_reflexion` | `no_memory` | `raw_trajectory_retrieval` | `reflexion` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `black_1493` | S 1 / 24,520 | S 2 / 48,228 | S 1 / 27,688 | S 1 / 15,223 | S 2 / 71,879 | S 1 / 45,117 | S 2 / 32,977 |
| `black_185` | S 1 / 28,140 | S 2 / 31,551 | S 1 / 49,600 | S 2 / 64,508 | S 1 / 35,189 | S 1 / 53,669 | S 2 / 68,748 |
| `black_389` | S 3 / 62,598 | S 1 / 18,270 | S 1 / 18,387 | S 1 / 20,460 | S 2 / 63,250 | S 1 / 24,566 | S 1 / 27,022 |
| `black_59` | S 2 / 99,774 | F | S 2 / 174,980 | S 3 / 253,799 | S 2 / 58,131 | F | F |
| `discord_py_7818` | S 2 / 76,694 | S 3 / 73,050 | S 3 / 39,095 | S 2 / 53,442 | S 2 / 58,833 | S 1 / 50,945 | S 2 / 58,244 |
| `scrapy_1265` | S 2 / 41,000 | S 1 / 19,885 | S 1 / 26,317 | S 2 / 36,465 | S 1 / 33,318 | S 1 / 40,534 | S 1 / 39,757 |
| `scrapy_2552` | S 1 / 31,151 | S 1 / 20,881 | S 1 / 27,754 | S 1 / 20,131 | S 1 / 14,736 | S 1 / 65,335 | S 1 / 14,635 |

## Repository-Level Readout

| Repo | Tasks | Most useful signal |
| --- | ---: | --- |
| `black` | 4 | Differentiates methods best. `black_59` separates Auto-SKILL from `reflexion`, `raw_trajectory_retrieval`, and `format_shuffled_skill`, but also shows that `generic_checklist` and `no_memory` are strong. |
| `discord.py` | 1 | All methods solve, but process differs: `raw_trajectory_retrieval` records 1 cycle, while `generic_checklist` and `format_shuffled_skill` need 3 cycles. |
| `scrapy` | 2 | Mostly sanity-check tasks. All methods solve `scrapy_2552` in 1 cycle after rerun; `scrapy_1265` does not strongly favor Auto-SKILL. |

## Differentiating Cases

| Case | Observation | Interpretation |
| --- | --- | --- |
| `black_59` | Auto-SKILL solves; `reflexion`, `raw_trajectory_retrieval`, and `format_shuffled_skill` fail. | Best evidence that structured procedural memory helps transfer beyond unstructured memory and shuffled content. |
| `black_389` | Auto-SKILL solves but uses 3 cycles, while most baselines solve in 1. | Auto-SKILL can over-diagnose or apply a heavier procedure than the task requires. |
| `scrapy_2552` | All methods solve in 1 cycle. | Good harness sanity check, weak discriminative value. |
| `length_matched_reflexion` on `black_59` | Solves but records negative transfer and very high token use. | Supports the claim that length-matched reflective memory can carry inefficient or harmful procedural residue. |

## Immediate Use in Paper

Use this breakdown to support three modest claims:

1. Auto-SKILL transfers across repositories within a broad test-failure triage family.
2. Auto-SKILL is more reliable than `reflexion`, `raw_trajectory_retrieval`, and `format_shuffled_skill` on this MVP slice.
3. This MVP is not sufficient to claim superiority over `generic_checklist` or `no_memory`; the next benchmark slice must be harder.
