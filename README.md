# Trace2Skill

[![仓库验证](https://github.com/damogu123/trace2skill/actions/workflows/validate.yml/badge.svg)](https://github.com/damogu123/trace2skill/actions/workflows/validate.yml)
[![项目主页](https://img.shields.io/badge/项目主页-Trace2Skill-1463ff)](https://damogu123.github.io/trace2skill/)
[![DOI](https://img.shields.io/badge/DOI-10.1145%2F3843282.3844421-0b7285)](https://doi.org/10.1145/3843282.3844421)

**面向语言智能体调试的低样本程序性技能迁移。**

Trace2Skill 是论文 **“Evaluating Low-Shot Procedural Skill Transfer in
Language-Agent Debugging”** 的复现仓库与评估工具。项目研究一个具体问题：
能否从少量成功调试轨迹中归纳出可检查、可复用的自然语言 `SKILL.md`，并将这份
程序性记忆迁移到未见的 PyBugHive 缺陷修复任务。

本仓库包含论文源码、清洗后的轨迹记录、冻结的记忆对象、实验清单、验证脚本、
汇总指标，以及面向 AgenticDev 2026 的精简复现 artifact。

## 项目入口

- [中文项目主页](https://damogu123.github.io/trace2skill/)
- [论文 DOI](https://doi.org/10.1145/3843282.3844421)
- [两页 camera-ready PDF](docs/static/pdfs/trace2skill-paper.pdf)
- [AgenticDev 复现 artifact](artifact_agenticdev2026/README.md)
- [数据选择说明](artifact_agenticdev2026/DATA_SELECTION.md)
- [复现步骤](artifact_agenticdev2026/REPRODUCE.md)
- [当前项目状态](SESSION_HANDOFF.md)

## 研究设计

1. 从 `K=3` 条脱敏调试轨迹中归纳 Auto `SKILL.md`。
2. 冻结该记忆对象，并部署到六个同缺陷家族的未见 PyBugHive `black` 任务。
3. 与通用检查清单、Reflexion、等长 Reflexion 和无记忆基线比较。
4. 同时记录成功率、诊断-编辑-测试循环、Token、失败补丁和负迁移。
5. 使用 `gpt-5.5` 补充运行 Auto `SKILL.md` 与格式打乱技能的结构对照。

## 主要结果

主要同模型实验使用六个任务，每个任务和方法仅执行一次。因此，这些结果是先导性
证据，不应解释为记忆方法的普遍排名。

| 方法 | 已解决 | 循环数/已解决任务 | Token/已解决任务 | 负迁移次数 |
|---|---:|---:|---:|---:|
| Auto `SKILL.md` | 5/6 | 2.00 | 56,866.8 | 1 |
| 通用检查清单 | 5/6 | 2.00 | 71,694.4 | 0 |
| Reflexion | 5/6 | 2.60 | 65,914.6 | 0 |
| 等长 Reflexion | 4/6 | 2.75 | 75,231.3 | 0 |
| 无记忆 | 4/6 | 3.00 | 92,030.8 | 0 |

Auto `SKILL.md` 与最佳基线取得相同成功率，其主要信号是相对反思基线更低的观测
过程成本。它与人类编写的通用检查清单在成功率和循环数上持平，现有样本不足以证明
稳定优势。`black_132` 中保留了一次明确的负迁移：首个记忆引导补丁使完整测试失败数
从 4 增至 6。

补充的同模型 `gpt-5.5` 结构对照中，Auto 和格式打乱技能均解决 6/6 个任务。Auto
记录的循环和失败补丁更少，但 Token 效率并不占优，因此不能据此声称标准
`SKILL.md` 结构是成功修复的必要条件。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `artifact_agenticdev2026/` | 精简、可审计的论文复现 artifact |
| `scripts/` | 任务导入、验证、智能体运行、轨迹记录和指标计算脚本 |
| `schemas/` | 任务、轨迹、运行清单和智能体 trace 的 JSON Schema |
| `tasks/` | 评估工具使用的任务定义 |
| `memory/` | 实验中冻结的记忆对象 |
| `manifests/` | 可运行的实验配置 |
| `prompts/` | 归纳提示和已保存的运行提示 |
| `trajectories/` | 用于分析的已验证轨迹 JSON |
| `results/` | 汇总指标、环境检查和实验报告 |
| `paper/` | 论文源码、参考文献、图表、审稿记录和构建说明 |
| `docs/` | 中文项目主页与工具文档 |

原始 `runs/`、临时 `workspaces/`、进程日志、外部基准源码和 LaTeX 中间文件不会
提交到 Git。论文结论所依赖的清洗后过程记录保存在 `trajectories/` 和
`artifact_agenticdev2026/trajectory_sets/`。

## 环境要求

- 仓库级验证脚本仅使用 Python 标准库，建议使用 Python 3.12 或更高版本。
- Windows 示例使用 `py` 启动器；Linux/macOS 可替换为 `python3`。
- 重新执行历史 PyBugHive 任务时，应使用任务中记录的固定依赖和兼容 Python 环境。
- 部分原始实验使用 WSL/Linux 环境；仅做数据验证和指标复算不需要 Docker 或 WSL。
- 调用真实语言模型可能产生费用，也可能因模型版本变化而无法逐位复现旧运行。

## 快速验证

在仓库根目录执行：

```powershell
py -m compileall -q scripts
py scripts/validate_task.py tasks
py scripts/validate_trajectory.py trajectories
py scripts/validate_run_manifest.py manifests
py scripts/validate_project_page.py docs
py scripts/validate_artifact_inventory.py artifact_agenticdev2026
```

验证论文使用的精简实验集合：

```powershell
py scripts/validate_task.py artifact_agenticdev2026/tasks
py scripts/validate_trajectory.py artifact_agenticdev2026/trajectory_sets/primary_first6
py scripts/validate_trajectory.py artifact_agenticdev2026/trajectory_sets/structural_control_gpt55
py scripts/validate_run_manifest.py artifact_agenticdev2026/manifests
```

GitHub Actions 会在每次 push 和 pull request 时自动执行上述核心检查，并确认论文图表
和不确定性分析可由仓库内数据重新生成。

## 复现汇总结果

复算主要六任务实验：

```powershell
py scripts/compute_metrics.py artifact_agenticdev2026/trajectory_sets/primary_first6 `
  --tasks artifact_agenticdev2026/task_sets/primary_first6 `
  --group-by method `
  --output-json results/recomputed_primary_first6_by_method.json `
  --output-csv results/recomputed_primary_first6_by_method.csv
```

复算 `gpt-5.5` 结构对照：

```powershell
py scripts/compute_metrics.py artifact_agenticdev2026/trajectory_sets/structural_control_gpt55 `
  --tasks artifact_agenticdev2026/task_sets/primary_first6 `
  --group-by method `
  --output-json results/recomputed_structural_control_gpt55_by_method.json `
  --output-csv results/recomputed_structural_control_gpt55_by_method.csv
```

重新生成论文图表和审稿后不确定性分析：

```powershell
py scripts/make_paper_results.py
py scripts/analyze_review_uncertainty.py
```

## 重新运行智能体实验

以下命令保留了原实验的调用形式。执行前请阅读
[`docs/codex_agent_runner.md`](docs/codex_agent_runner.md) 和
[`docs/real_agent_execution_checklist.md`](docs/real_agent_execution_checklist.md)，
确认 Codex CLI、模型权限、任务环境和费用预算均已配置：

```powershell
py scripts/run_external_agent.py manifests/pybughive_hard_smoke_codex.json `
  --agent-command "py scripts/run_codex_agent.py --prompt-path {prompt_path} --repo-dir {repo_dir} --artifacts-dir {artifacts_dir} --trace-path {trace_path} --model gpt-5.3-codex" `
  --require-agent-zero `
  --prepare `
  --skip-existing-trajectories
```

冻结文件位于 `memory/pybughive/test_failure_triage/`。如果修改记忆内容，必须使用新的
条件名称和运行清单重新执行实验，不能将新记忆与旧结果混用。

## 构建论文

两页 AgenticDev camera-ready 论文源码为 `paper/main_poster.tex`。安装 ACM LaTeX
模板、`latexmk`、Perl、Inkscape 和所需宏包后，在 `paper/` 目录执行：

```powershell
latexmk -g -pdf -interaction=nonstopmode -halt-on-error `
  -jobname=agenticdev2026_paper12_camera_ready main_poster.tex
```

完整构建说明见 [`paper/BUILD.md`](paper/BUILD.md)。提交系统使用的自包含源码包位于
`paper/submission/agenticdev_camera_ready_source.zip`。

## 已知边界

- 主要实验只有六个同缺陷家族任务，每种配置只有一次执行。
- 尚未完成多执行种子、多归纳种子、跨项目困难任务和第二位负迁移标注者。
- 原始模型服务和历史基准环境可能随时间变化；仓库保证的是记录、验证和指标复算，
  不是对付费智能体运行的永久逐位重放。
- reference patch 只用于核验任务可复现性和可解性，不会提供给未见任务修复智能体。

## 引用

GitHub 可通过 [`CITATION.cff`](CITATION.cff) 提供引用信息。BibTeX：

```bibtex
@inproceedings{sun2026trace2skill,
  author    = {Jiachen Sun},
  title     = {Evaluating Low-Shot Procedural Skill Transfer in
               Language-Agent Debugging},
  booktitle = {Proceedings of the 1st International Workshop on Agentic AI
               for Next-Generation Software Development},
  year      = {2026},
  publisher = {Association for Computing Machinery},
  doi       = {10.1145/3843282.3844421},
  url       = {https://doi.org/10.1145/3843282.3844421}
}
```

## 许可

camera-ready 论文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。
`docs/` 下的项目主页布局与代码采用 CC BY-SA 4.0，详见
[`docs/PROJECT_PAGE_LICENSE.md`](docs/PROJECT_PAGE_LICENSE.md)。当前尚未为整个仓库的
软件与数据选择统一许可证，因此其余内容默认保留所有权利。
