# PyBugHive Import Report

## Summary

- Source issues: 149
- Metadata-eligible issues: 130
- Selected first-batch tasks: 10
- Reproducibility status: metadata-screened; environment execution still needs PyBugHive-compatible Python/pipenv setup.

## Selected Tasks

| Split | Task ID | Project | Issue | Source Files | Test Files | Warnings |
| --- | --- | --- | ---: | ---: | ---: | --- |
| train | `pybughive_black_297` | black | 297 | 1 | 2 | none |
| train | `pybughive_cookiecutter_1513` | cookiecutter | 1513 | 1 | 3 | none |
| train | `pybughive_discord_py_7676` | discord.py | 7676 | 1 | 1 | none |
| heldout | `pybughive_scrapy_2552` | scrapy | 2552 | 1 | 1 | none |
| heldout | `pybughive_black_185` | black | 185 | 1 | 1 | none |
| heldout | `pybughive_discord_py_7818` | discord.py | 7818 | 1 | 1 | none |
| heldout | `pybughive_scrapy_1265` | scrapy | 1265 | 2 | 2 | none |
| heldout | `pybughive_black_59` | black | 59 | 1 | 1 | none |
| heldout | `pybughive_black_1493` | black | 1493 | 1 | 1 | none |
| heldout | `pybughive_black_389` | black | 389 | 1 | 2 | none |

## Notes

- Each task includes a PyBugHive test patch under `patches/pybughive/` because PyBugHive exposes many bugs by copying tests from the fixing commit onto the buggy parent commit.
- `scripts/prepare_task.py` now applies `benchmark.test_patch_path` before installing and reproducing the initial failure.
- The generated `ground_truth.patch_path` contains only the reference source-code patch, separate from the test patch.
