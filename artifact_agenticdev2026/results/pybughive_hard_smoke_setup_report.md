# PyBugHive Hard-Smoke Setup Report

Date: 2026-05-28

Last updated: 2026-06-02

## What Was Created

- Hard-subset selector: `scripts/select_pybughive_hard_subset.py`
- WSL-capable verification: `scripts/verify_pybughive_tasks.py --runner wsl`
- Candidate ranking: `results/pybughive_hard_subset_candidates.csv`
- Hard-subset plan: `results/pybughive_hard_subset_plan.md`
- Generated task JSONs: `tasks/pybughive_hard/heldout/`
- Generated patches: `patches/pybughive_hard/`
- Generated metadata: `data/pybughive_hard/`
- Verification outputs:
  - `results/pybughive_hard_verify.json`
  - `results/pybughive_hard_verify.csv`
  - `results/pybughive_hard_verify.md`
- Smoke manifest: `manifests/pybughive_hard_smoke_codex.json`
- Prompt packs: `prompts/runs/pybughive_hard_smoke/`

## Verification Result

| Status | Count |
| --- | ---: |
| `pilot_ready` | 7 |
| `reference_test_failed` | 1 |

Ready tasks:

- `pybughive_black_132`
- `pybughive_black_133`
- `pybughive_black_154`
- `pybughive_black_183`
- `pybughive_black_193`
- `pybughive_black_232`
- `pybughive_black_234`

Excluded task:

- `pybughive_black_1632`: reference patch failed the verification test, so it should not enter agent evaluation.

## Smoke Manifest

`manifests/pybughive_hard_smoke_codex.json` contains 35 runs:

- 7 verified hard tasks
- 5 core methods:
  - `no_memory`
  - `generic_checklist`
  - `auto_skill`
  - `reflexion`
  - `length_matched_reflexion`

The manifest intentionally excludes `raw_trajectory_retrieval` and `format_shuffled_skill` for the first hard-smoke pass. Add them after the 5-method smoke run is stable.

## Recommended Execution Strategy

Run a tiny smoke first:

```powershell
python scripts\run_external_agent.py manifests\pybughive_hard_smoke_codex.json --run-ids pybughive_hard_smoke_pybughive_black_132_no_memory_seed1,pybughive_hard_smoke_pybughive_black_132_generic_checklist_seed1,pybughive_hard_smoke_pybughive_black_132_auto_skill_seed1 --agent-command "python scripts/run_codex_agent.py --prompt-path {prompt_path} --repo-dir {repo_dir} --artifacts-dir {artifacts_dir} --trace-path {trace_path} --model gpt-5.3-codex --approval-policy never --sandbox danger-full-access" --test-runner wsl --prepare --force --allow-missing-trace --agent-timeout 3600
```

If that succeeds, run the full 35-run hard smoke with the same command minus `--run-ids`.

## Harness Notes

Updates made on 2026-05-28:

- `scripts/run_codex_agent.py` now tells the agent to treat benchmark-prepared dirty worktrees as the starting state. This prevents false stops caused by test fixtures, docs, or generated package files already present in the prepared checkout.
- `scripts/run_codex_agent.py` now explicitly forbids web search, browser tools, online documentation, GitHub pages, and external network sources during benchmark runs.
- `scripts/run_codex_agent.py` now explicitly forbids recreating, resetting, recloning, repopulating, or copying over the prepared checkout. This was added after an invalid `pybughive_black_193` `generic_checklist` attempt tried to repair perceived contamination by running task-preparation/copy operations. That attempt was killed and is not counted; the accepted rerun used the hardened harness.
- One `reflexion` attempt for `pybughive_black_154` emitted an actual web-search query and was stopped before producing an accepted trajectory. The accepted rerun was produced after the no-web harness rule was added. Some accepted logs still contain blank `web search:` markers with no query text; treat these as CLI artifacts to monitor, not as evidence of external source use.

Update made on 2026-06-02:

- The original `gpt-5.3-codex` model became unavailable for this ChatGPT-account Codex CLI session while running `pybughive_black_234`. The accepted `pybughive_black_234` runs used a temporary `gpt-5.5` manifest, `manifests/pybughive_hard_smoke_codex_gpt55.json`, and regenerated/updated only the `black_234` run prompts. Therefore, the first-six aggregate below remains the strict same-model hard-smoke result, while the first-seven aggregate is model-mixed exploratory evidence.

## Tiny Smoke Result: `pybughive_black_132`

Completed on 2026-05-27 with five methods:

| Method | Solved | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `no_memory` | 1/1 | 3.0 | 133137.0 | 0.0 |
| `generic_checklist` | 1/1 | 3.0 | 119311.0 | 0.0 |
| `auto_skill` | 0/1 |  |  | 1.0 |
| `reflexion` | 1/1 | 2.0 | 46367.0 | 0.0 |
| `length_matched_reflexion` | 0/1 |  |  | 0.0 |

Artifacts:

- Trajectories: `trajectories/pybughive_hard_smoke/`
- Metrics CSV: `results/pybughive_hard_black132_smoke_metrics.csv`
- Metrics JSON: `results/pybughive_hard_black132_smoke_metrics.json`

Interpretation:

- The hard task is useful: even successful baselines needed 3 diagnosis-edit-test cycles, unlike the easier held-out MVP tasks.
- `auto_skill` failed on this task and produced a negative-transfer signal. It focused on preserving/removing magic trailing commas in bracket handling rather than repairing the `delimiter_split` star/doublestar condition that solved the task for the other methods.
- `reflexion` solved the task in 2 cycles and 46367 tokens, making it the strongest successful method on this first hard smoke.
- `length_matched_reflexion` was rerun after the earlier usage-limit interruption. It completed normally but did not solve the task: 2 cycles, 50869 tokens, 2 failed patches, no negative-transfer flag.
- This is not yet evidence against procedural skills overall, but it is strong evidence that the current induced skill is too generic for this `black` failure family. Next, run at least one additional hard `black` task with the same 5 methods to see whether this pattern repeats.

## Tiny Smoke Result: `pybughive_black_133`

Completed on 2026-05-27 with five methods:

| Method | Solved | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `no_memory` | 0/1 |  |  | 0.0 |
| `generic_checklist` | 1/1 | 1.0 | 45692.0 | 0.0 |
| `auto_skill` | 1/1 | 1.0 | 33629.0 | 0.0 |
| `reflexion` | 1/1 | 3.0 | 89908.0 | 0.0 |
| `length_matched_reflexion` | 1/1 | 1.0 | 52402.0 | 0.0 |

Artifacts:

- Trajectories: `trajectories/pybughive_hard_smoke/`
- Metrics CSV: `results/pybughive_hard_black133_smoke_metrics.csv`
- Combined first-two-task CSV: `results/pybughive_hard_black132_133_smoke_metrics.csv`
- Metrics JSON: `results/pybughive_hard_black132_133_smoke_metrics.json`

Interpretation:

- `auto_skill` solved this task in 1 cycle and 33629 tokens. This is the clearest hard-smoke example so far where the induced procedural memory helps with a within-family `black` formatting failure.
- `generic_checklist` was rerun on 2026-05-28 after adding a harness note that benchmark-prepared dirty worktrees should be treated as the starting state. The rerun solved the task in 1 cycle and 45692 tokens.
- `length_matched_reflexion` also solved in 1 cycle, but used more tokens than `auto_skill`. This is a useful control result because it shows the extra text budget alone is not obviously better than the procedural format.
- `reflexion` solved the task but needed 3 cycles and 89908 tokens.
- `no_memory` found a narrow fix direction but failed the full suite because the patch introduced formatting/idempotence failures.
- After the `generic_checklist` rerun, all successful methods converged on the same local invariant: commas inside `syms.varargslist` should not trigger delimiter-based splitting.

## Tiny Smoke Result: `pybughive_black_154`

Completed on 2026-05-28 with five methods:

| Method | Solved | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `no_memory` | 1/1 | 3.0 | 64415.0 | 0.0 |
| `generic_checklist` | 1/1 | 3.0 | 55994.0 | 0.0 |
| `auto_skill` | 1/1 | 3.0 | 69586.0 | 0.0 |
| `reflexion` | 1/1 | 4.0 | 71249.0 | 0.0 |
| `length_matched_reflexion` | 1/1 | 4.0 | 77025.0 | 0.0 |

Artifacts:

- Trajectories: `trajectories/pybughive_hard_smoke/`
- Metrics CSV: `results/pybughive_hard_black154_only_smoke_metrics.csv`
- First-three-task by-task CSV: `results/pybughive_hard_first3_by_task_metrics.csv`
- First-three-task by-method CSV: `results/pybughive_hard_first3_by_method_metrics.csv`

Interpretation:

- All five methods solved this task, so `pybughive_black_154` does not separate methods by solve rate.
- `generic_checklist` was the most token-efficient on this task: 3 cycles and 55994 tokens.
- `auto_skill` solved the task but did not outperform the generic checklist or no-memory baseline on efficiency: 3 cycles and 69586 tokens.
- The dominant failure pattern was boundary handling for standalone comments before `def`/`class`/decorator lines, plus preserving spacing after section-divider comments. Most methods had to repair an over-broad first patch.
- This is useful boundary evidence: the current induced skill transfers to some `black` formatting cases (`black_133`) but is not uniformly better across adjacent formatter subfamilies.

## Tiny Smoke Result: `pybughive_black_183`

Completed on 2026-05-28 with five methods:

| Method | Solved | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `no_memory` | 1/1 | 3.0 | 104517.0 | 0.0 |
| `generic_checklist` | 1/1 | 1.0 | 88978.0 | 0.0 |
| `auto_skill` | 1/1 | 2.0 | 52645.0 | 0.0 |
| `reflexion` | 1/1 | 1.0 | 53506.0 | 0.0 |
| `length_matched_reflexion` | 1/1 | 3.0 | 98025.0 | 0.0 |

Artifacts:

- Trajectories: `trajectories/pybughive_hard_smoke/`
- Metrics CSV: `results/pybughive_hard_black183_only_smoke_metrics.csv`
- Metrics JSON: `results/pybughive_hard_black183_only_smoke_metrics.json`
- First-four-task by-task CSV: `results/pybughive_hard_first4_by_task_metrics.csv`
- First-four-task by-method CSV: `results/pybughive_hard_first4_by_method_metrics.csv`

Interpretation:

- All five methods solved this task, so the separation is in process efficiency rather than solve rate.
- `auto_skill` solved in 2 cycles and 52645 tokens, far below `no_memory` and `length_matched_reflexion`, and close to `reflexion` in token cost.
- `generic_checklist` and `reflexion` both solved in 1 cycle, so this task should not be claimed as unconditional evidence that SKILL.md dominates every memory baseline.
- `length_matched_reflexion` is informative as a prompt-control baseline: it first changed the assert trigger set too broadly, failed the expression tests, and only later converged on iterative redundant-parentheses normalization. This supports the value of structured procedural guidance over length-matched unstructured memory.
- The shared root cause was idempotence in `normalize_invisible_parens`: redundant nested assert parentheses were only removed one layer per formatting pass.

## Tiny Smoke Result: `pybughive_black_193`

Completed on 2026-05-28 with five methods:

| Method | Solved | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `no_memory` | 0/1 |  |  | 0.0 |
| `generic_checklist` | 0/1 |  |  | 0.0 |
| `auto_skill` | 1/1 | 3.0 | 92439.0 | 0.0 |
| `reflexion` | 0/1 |  |  | 0.0 |
| `length_matched_reflexion` | 0/1 |  |  | 0.0 |

Artifacts:

- Trajectories: `trajectories/pybughive_hard_smoke/`
- Metrics CSV: `results/pybughive_hard_black193_only_smoke_metrics.csv`
- Metrics JSON: `results/pybughive_hard_black193_only_smoke_metrics.json`
- First-five-task by-task CSV: `results/pybughive_hard_first5_by_task_metrics.csv`
- First-five-task by-method CSV: `results/pybughive_hard_first5_by_method_metrics.csv`

Interpretation:

- This is the strongest hard-smoke win for `auto_skill` so far: it was the only method to solve `pybughive_black_193`, using 3 cycles and 92439 tokens.
- `no_memory` produced a narrow Python 2 compatibility-style change but failed the full suite, so it did not repair the intended formatting regression.
- `generic_checklist` failed after broad formatting/encoding-sensitive edits. The invalid earlier attempt that tried to recreate/copy the checkout was killed and excluded; the accepted rerun still failed under the hardened harness.
- `reflexion` and `length_matched_reflexion` both pursued a starred-unpacking/`UNPACKING_PARENTS` diagnosis and failed to repair the broader expression formatting behavior. This is a useful contrast case: unstructured memory pointed to a nearby prior pattern but did not transfer to the correct procedural invariant.
- `auto_skill` generalized better on this task by following the induced debugging procedure around trigger conditions, expression/test-like nodes, narrow verification, and full-suite validation. This should be used as a qualitative case study, not as a standalone superiority claim.

## Tiny Smoke Result: `pybughive_black_232`

Completed on 2026-05-28 with five methods:

| Method | Solved | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `no_memory` | 1/1 | 3.0 | 66054.0 | 0.0 |
| `generic_checklist` | 1/1 | 2.0 | 48497.0 | 0.0 |
| `auto_skill` | 1/1 | 1.0 | 36035.0 | 0.0 |
| `reflexion` | 1/1 | 3.0 | 68543.0 | 0.0 |
| `length_matched_reflexion` | 1/1 | 3.0 | 73473.0 | 0.0 |

Artifacts:

- Trajectories: `trajectories/pybughive_hard_smoke/`
- Metrics CSV: `results/pybughive_hard_black232_only_smoke_metrics.csv`
- Metrics JSON: `results/pybughive_hard_black232_only_smoke_metrics.json`
- First-six-task by-task CSV: `results/pybughive_hard_first6_by_task_metrics.csv`
- First-six-task by-method CSV: `results/pybughive_hard_first6_by_method_metrics.csv`

Interpretation:

- All five methods solved `pybughive_black_232`, so this task separates methods by process efficiency rather than solve rate.
- `auto_skill` was the clear efficiency winner: 1 cycle and 36035 tokens. It immediately framed the issue as over-broad optional-parens insertion for a `for ... in ...` statement whose iterable starts with a multiline string.
- `generic_checklist` also solved efficiently, but needed 2 cycles and 48497 tokens after first fixing iterable wrapping and then loop-target wrapping.
- `no_memory`, `reflexion`, and `length_matched_reflexion` each needed 3 cycles. Their common failure mode was an over-broad first edit that either changed global `for_stmt` behavior or introduced Black self-format/idempotence regressions.
- This is a strong process-efficiency case for procedural memory: the SKILL.md procedure appears to help the agent compress the failure into the right invariant before broad edits accumulate.

## Tiny Smoke Result: `pybughive_black_234`

Completed on 2026-06-02 with five methods. These runs used `gpt-5.5` because `gpt-5.3-codex` was no longer accepted by the local Codex CLI account.

| Method | Solved | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: |
| `no_memory` | 1/1 | 1.0 | 98948.0 | 0.0 |
| `generic_checklist` | 1/1 | 1.0 | 53835.0 | 0.0 |
| `auto_skill` | 1/1 | 2.0 | 73324.0 | 0.0 |
| `reflexion` | 1/1 | 1.0 | 52222.0 | 0.0 |
| `length_matched_reflexion` | 1/1 | 1.0 | 51356.0 | 0.0 |

Artifacts:

- Trajectories: `trajectories/pybughive_hard_smoke/`
- Metrics CSV: `results/pybughive_hard_black234_only_smoke_metrics.csv`
- Metrics JSON: `results/pybughive_hard_black234_only_smoke_metrics.json`
- Model-mixed first-seven by-task CSV: `results/pybughive_hard_first7_by_task_metrics.csv`
- Model-mixed first-seven by-method CSV: `results/pybughive_hard_first7_by_method_metrics.csv`

Interpretation:

- All five methods solved `pybughive_black_234`, so this task does not separate methods by solve rate.
- The root cause was localized in `LineGenerator.visit_import_from`: Black's custom import-from parenthesis handling inserted optional parentheses for long `from ... import *` statements, producing invalid code, and could also run across `# fmt: off` import regions.
- `auto_skill` solved the task but needed 2 cycles and more tokens than the reflection/checklist variants on this specific run. It still used fewer tokens than `no_memory`.
- Because this task used `gpt-5.5`, use it primarily as a completion check and qualitative example unless the earlier six tasks are rerun under the same model.

## First Six Hard Tasks

Aggregate over `pybughive_black_132`, `pybughive_black_133`, `pybughive_black_154`, `pybughive_black_183`, `pybughive_black_193`, and `pybughive_black_232`:

| Method | Solved | Solve rate | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: | ---: |
| `auto_skill` | 5/6 | 0.8333 | 2.0000 | 56866.8000 | 0.1667 |
| `generic_checklist` | 5/6 | 0.8333 | 2.0000 | 71694.4000 | 0.0000 |
| `reflexion` | 5/6 | 0.8333 | 2.6000 | 65914.6000 | 0.0000 |
| `length_matched_reflexion` | 4/6 | 0.6667 | 2.7500 | 75231.2500 | 0.0000 |
| `no_memory` | 4/6 | 0.6667 | 3.0000 | 92030.7500 | 0.0000 |

Interpretation:

- `auto_skill`, `generic_checklist`, and `reflexion` are tied on solve rate at 5/6, so the current claim should not be broad solve-rate dominance.
- `auto_skill` has the lowest token cost among solved tasks and a lower cycle count than `reflexion`; it also clearly outperforms `length_matched_reflexion` and `no_memory` on both solve rate and efficiency.
- `black_193` is a useful qualitative separator: only `auto_skill` solved it, while both reflection baselines followed a nearby but insufficient prior pattern.
- `black_232` adds a clean efficiency separator: all methods solved, but `auto_skill` required only 1 cycle while both reflection baselines required 3.
- `auto_skill` still has one failure and one negative-transfer signal on `black_132`, so the paper should present procedural memory as subfamily-sensitive transfer rather than universally beneficial memory.
- This first-six table is currently the cleanest same-model hard-smoke evidence. Keep it as the primary aggregate until all seven tasks are rerun under a single model.

## First Seven Hard Tasks (Model-Mixed Exploratory)

Aggregate over all seven verified hard tasks. The first six tasks used the earlier `gpt-5.3-codex` setup; `pybughive_black_234` used `gpt-5.5`.

| Method | Solved | Solve rate | Cycles per solved task | Tokens per solved task | Negative transfer |
| --- | ---: | ---: | ---: | ---: | ---: |
| `auto_skill` | 6/7 | 0.8571 | 2.0000 | 59609.6667 | 0.1429 |
| `generic_checklist` | 6/7 | 0.8571 | 1.8333 | 68717.8333 | 0.0000 |
| `reflexion` | 6/7 | 0.8571 | 2.3333 | 63632.5000 | 0.0000 |
| `length_matched_reflexion` | 5/7 | 0.7143 | 2.4000 | 70456.2000 | 0.0000 |
| `no_memory` | 5/7 | 0.7143 | 2.6000 | 93414.2000 | 0.0000 |

Interpretation:

- The exploratory first-seven table preserves the first-six pattern: `auto_skill`, `generic_checklist`, and `reflexion` are tied on solve rate, while `auto_skill` remains the most token-efficient successful method overall.
- `generic_checklist` has the lowest average cycle count after adding `black_234`, so the strongest current claim should emphasize procedural-memory token efficiency and qualitative transfer cases, not universal cycle dominance.
- `auto_skill` continues to beat `length_matched_reflexion` and `no_memory` on solve rate and efficiency, which is useful for the paper's core comparison against unstructured memory and no-memory baselines.
- This table should be labeled exploratory in any draft until the model mismatch is removed.

## Scientific Rationale

The hard subset is currently a formatting-heavy `black` slice. This is acceptable for a controlled hard smoke because prior MVP results showed the `black` family produced the strongest method separation, especially `black_59`. It is not yet a general benchmark slice; cross-repository hard tasks should be added after the black hard-smoke behavior is understood.
