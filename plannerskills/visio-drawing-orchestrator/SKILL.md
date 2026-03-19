---
name: visio-drawing-orchestrator
description: Analyze a source figure, classify the diagram family, decompose regions and elements, and produce a drawing plan before any detailed Visio drawing begins. Use when a job starts from an input image and the agent must decide what to draw first, which drawskills to invoke, which visioskills capabilities are needed, and how round-by-round critique should be structured.
---

# Visio Drawing Orchestrator

这个 skill 是总控层。

它负责先想清楚“这次要怎么画”，再把工作交给 `drawskills` 和 `visioskills`。

## Input Contract

开始时优先读取：

- `../../Setup/draw-job.local.json`
- `../../Setup/jobs/<job_name>/run-summary.json`
- 输入图片
- `../../docs/LAYER_CONTRACTS.md`
- `../../docs/ARTIFACT_CONTRACTS.md`
- 相关 lessons

## Output Contract

这个 skill 至少要产出两份东西：

1. `analysis.json`
2. `plan.json`

如果还没产出这两份结构化结果，不要直接进入复杂绘图。

## Responsibilities

1. 识别图类型
   - pipeline
   - network architecture
   - module-detail side panel
   - mixed-layout figure
2. 拆分区域
   - 主画布
   - 侧边模块说明
   - 标题/legend/IO 区
3. 抽取元素
   - box
   - text
   - arrow
   - image
   - annotation
4. 判断风格
   - 字体
   - 字号层级
   - 线条类型
   - 颜色语义
5. 形成绘图策略
   - 先画什么
   - 后画什么
   - 哪些 drawskills 负责布局
   - 哪些 visioskills 能力是必要的

## Planning Rule

planner 只做“策略和结构”的决定，不做这些事：

- 不直接硬编码所有坐标
- 不直接写 Visio 请求序列
- 不把本轮失败经验直接塞进长期规则

## Round Loop

每一轮后都要回答：

1. 本轮偏差是识别问题、布局问题，还是执行问题？
2. 下一轮应该改 planner、drawskills，还是 visioskills？
3. 是否需要新增一条 lesson？

## Read These Files As Needed

- `../../docs/LAYER_CONTRACTS.md`
- `../../Setup/analysis.schema.json`
- `../../Setup/plan.schema.json`
- `../../drawskills/visio-figure-builder/SKILL.md`
- `../../learningskills/visio-iteration-journal/SKILL.md`
- `references/planning-checklist.md`
