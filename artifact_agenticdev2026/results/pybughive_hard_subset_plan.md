# PyBugHive Hard-Subset Plan

## Goal

Select a harder held-out subset that can separate Auto-SKILL from `generic_checklist` and `no_memory`.
The current MVP is useful but too easy because both generic baselines solve 7/7 held-out tasks.

## Selection Heuristic

Candidates are ranked higher when metadata suggests harder debugging:

- multiple source files or larger reference patches;
- multiple or large test patches;
- broader full-test command is available;
- title suggests crash, internal error, parse failure, unstable formatting, import behavior, or nested edge cases;
- cross-file behavior regression or API/domain knowledge may be involved.

Candidates are penalized for heavy projects, heavy install steps, text-only issues, very tiny patches, and test commands requiring manual review.

## Candidate Counts

- Ranked candidates: 64
- Pilot-light candidates: 12
- Full-study-heavy candidates: 52
- Task JSONs written in this run: 8

## Recommended Pilot-Light Candidates

| Rank | Task ID | Project | Score | Source files | Changed lines | Test files | Test changed lines | Why hard |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `pybughive_black_132` | black | 216 | 3 | 70 | 4 | 89 | 3 source files; 70 source changed lines; 4 test files |
| 2 | `pybughive_black_193` | black | 191 | 2 | 57 | 4 | 185 | 2 source files; 57 source changed lines; 4 test files |
| 3 | `pybughive_black_133` | black | 181 | 2 | 81 | 2 | 18 | 2 source files; 81 source changed lines; 2 test files |
| 4 | `pybughive_black_232` | black | 169 | 2 | 86 | 1 | 14 | 2 source files; 86 source changed lines; has broader full-test command |
| 5 | `pybughive_black_1632` | black | 168 | 3 | 28 | 3 | 132 | 3 source files; 28 source changed lines; 3 test files |
| 6 | `pybughive_black_154` | black | 159 | 2 | 21 | 5 | 62 | 2 source files; 5 test files; 62 test changed lines |
| 7 | `pybughive_black_183` | black | 156 | 3 | 46 | 2 | 18 | 3 source files; 46 source changed lines; 2 test files |
| 8 | `pybughive_black_234` | black | 150 | 2 | 46 | 2 | 10 | 2 source files; 46 source changed lines; 2 test files |
| 9 | `pybughive_black_334` | black | 142 | 2 | 20 | 2 | 31 | 2 source files; 2 test files; 31 test changed lines |
| 10 | `pybughive_black_238` | black | 131 | 2 | 12 | 2 | 42 | 2 source files; 2 test files; 42 test changed lines |
| 11 | `pybughive_black_112` | black | 129 | 3 | 18 | 1 | 18 | 3 source files; has broader full-test command; cross-file reference patch |
| 12 | `pybughive_black_385` | black | 127 | 2 | 15 | 1 | 72 | 2 source files; 72 test changed lines; has broader full-test command |

## Full-Study Heavy Candidates

These may be useful later, but should not be first because environment setup is likely expensive.

| Rank | Task ID | Project | Score | Warnings | Title |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `pybughive_numpy_22714` | numpy | 186 | heavy_project | BUG: `numpy.median()` does not respect `keepdims=True` when the `out` argument is specified |
| 2 | `pybughive_salt_64430` | salt | 157 | heavy_project | [BUG] regression for user.present on handling groups with dupe GIDs |
| 3 | `pybughive_pandas_15055` | pandas | 153 | heavy_project | .str.replace does not accept a repl function |
| 4 | `pybughive_poetry_3112` | poetry | 132 | heavy_install_steps | poetry lock/export wrong with sys_platform (works fine on ver 1.0.10) |
| 5 | `pybughive_pandas_15420` | pandas | 120 | heavy_project | rank incorrectly orders ordered categories |
| 6 | `pybughive_pandas_15447` | pandas | 102 | heavy_project | Wrong result of pandas.sparse.series.SparseSeries.loc with indexer of length 1 |
| 7 | `pybughive_salt_62336` | salt | 99 | heavy_project | [BUG] no access to opts and sls vars in pyobjects renderer |
| 8 | `pybughive_pandas_14580` | pandas | 91 | heavy_project | BUG: iloc misbehavior with pd.Series: sometimes returns pd.Categorical instead |
| 9 | `pybughive_poetry_3098` | poetry | 86 | heavy_install_steps | Nested relative directory dependency failing to resolve. |
| 10 | `pybughive_pandas_14390` | pandas | 85 | heavy_project | BUG: Line delimited json is breaks if string includes `}` |
| 11 | `pybughive_pandas_14522` | pandas | 83 | heavy_project | Categorical.searchsorted() uses lexical order instead of the provided categorical order |
| 12 | `pybughive_pandas_15428` | pandas | 81 | heavy_project | BUG: pd.cut with bins=1 and input all 0s |

## Execution Protocol

1. Verify the written pilot-light task JSONs with `scripts/verify_pybughive_tasks.py` before running agent baselines.
2. Keep only tasks where initial failure reproduces and the reference patch passes.
3. First run only `no_memory`, `generic_checklist`, `auto_skill`, `reflexion`, and `length_matched_reflexion` on the verified hard subset.
4. Add `format_shuffled_skill` and `raw_trajectory_retrieval` after the first hard-subset smoke run is stable.

## Suggested First Commands

```powershell
python scripts\verify_pybughive_tasks.py tasks\pybughive_hard\heldout --workspace workspaces\verify_pybughive_hard --force --timeout 900 --output-json results\pybughive_hard_verify.json --output-csv results\pybughive_hard_verify.csv --output-md results\pybughive_hard_verify.md
```
