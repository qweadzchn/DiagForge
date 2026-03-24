---
name: visio-figure-builder
description: Build publication-style figures in Microsoft Visio through the DrawForge bridge after a planner has already analyzed the source figure and produced a plan. Use when the agent needs to translate a drawing plan into layout, typography, spacing, line-style semantics, and DrawDSL, especially for research figures.
---

# Visio Figure Builder

这个 skill 不是总控规划器。

它的职责是：在 planner 已经把图拆解过之后，把计划变成布局、样式和 DrawDSL。

## Preflight (mandatory)

1. Read `../../../../docs/architecture/LAYER_CONTRACTS.md`
2. Read `../../../../AGENT_GUIDE.md`
3. Read `../../../../docs/architecture/ARTIFACT_CONTRACTS.md`
4. If `../../../../Setup/draw-job.local.json` exists, treat its `execution` block as the source of truth for round limits, preview export, cleanup, and final-output behavior.

## Input Contract

优先消费：

- `../../../../Setup/jobs/<job_name>/analysis.json`
- `../../../../Setup/jobs/<job_name>/plan.json`
- relevant lessons

这个 skill 应该把“planner 已经想清楚的结构”变成 DrawDSL，而不是自己重新做总体任务规划。

## Output Contract

这个 skill 的核心产物是：

- `../../../../Setup/jobs/<job_name>/drawdsl.json`

这个文件应该表达“要画什么”，不应该携带 bridge 地址、token、session id 之类的运行态信息。

## Default style preset

- Font family: `Times New Roman`
- Main block title: `12-16 pt`
- Standard module label: `10-13 pt`
- Annotation / footnote row: `9.5-11 pt`
- Text color: `RGB(20,20,20)`
- Line color: `RGB(40,40,40)`
- Line weight: `0.9-1.3 pt`

## Coupled Rules (hard constraints)

这些规则默认生效，不是可有可无的建议：

1. 默认字体使用 `Times New Roman`
2. 字号变大时，框尺寸必须联动变大
3. 框尺寸变大后，邻近间距必须重算
4. 文字方向变化时，重新计算框宽高和最小间距
5. 节点之间默认不能互相压到
6. 线条样式必须表达语义差异

## Execution role

`drawskills` 在这条链路里主要负责：

1. Decide layout family and lanes from planner output
2. Choose typography hierarchy
3. Apply text-box coupling rules
4. Convert semantic edges into line-style semantics
5. Emit DrawDSL

## Failure policy

- 如果 planner 的分析还不够，先回到 `plannerskills`
- 如果 Visio 原子能力不够，回到 `visioskills`
- 如果本轮发现新规律，交给 `learningskills`

## Use references

- For layout tuning and iteration lessons, read:
  - `references/layout-iteration-notes.md`
- For paper-friendly defaults, read:
  - `references/research-figure-guidelines.md`
- For box-size / font-size / spacing coupling, read:
  - `references/text-layout-coupling.md`
- For connector and line-style semantics, read:
  - `references/line-style-semantics.md`

