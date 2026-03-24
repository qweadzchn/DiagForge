---
name: visio-iteration-journal
description: Distill reusable lessons from Visio drawing iterations in DrawForge. Use when an agent encounters a drawing problem, layout failure, export surprise, bridge recovery issue, or any repeatable obstacle during Visio work and should convert that one-off fix into a generalized lesson stored under learningskills.
---

# Visio Iteration Journal

这个 skill 负责把“这次好不容易解决的问题”变成“下次 agent 可以直接用的经验”。

## Input Contract

优先读取：

- `../../../../docs/architecture/LAYER_CONTRACTS.md`
- `../../../../docs/architecture/ARTIFACT_CONTRACTS.md`
- `../templates/lesson-template.md`
- `../../../../Setup/jobs/<job_name>/reviews/round-*.json`
- 导出预览 PNG

## Output Contract

这个 skill 有两个层次的产物：

- `../../../../Setup/jobs/<job_name>/reviews/round-*.json`
- `../lessons/*.md`

如果只是本轮观察，还没抽象成通用规律，就先留在 `round-review.json`，不要直接写进 lesson。

## When To Capture A Lesson

遇到下面这些情况就应该考虑沉淀：

- 导出 PNG 后才发现布局很乱
- 字体、文本块、尺寸反复调不对
- connector 画早了导致整图难以维护
- bridge / session / save / export 出现可复用的恢复经验
- planner 的图分类或区域拆解明显误判
- 某个 drawskill 规则明显该补

## Capture Workflow

1. 先写清现象，不要一上来就写结论
2. 抽离任务特有细节，保留可泛化信息
3. 用 `../templates/lesson-template.md` 记录
4. 存到 `../lessons/`
5. 如果经验需要变成规则：
   - 规划层经验 -> 更新 `plannerskills`
   - 操作层经验 -> 更新 `visioskills`
   - 构图层经验 -> 更新 `drawskills`
   - 只是暂时观察 -> 先留在 `reviews/`

## Writing Rule

lesson 必须写成 generalized knowledge，不写成一次任务的流水账。

## Files To Read

- `../templates/lesson-template.md`
- `../../../../AGENT_GUIDE.md`
- `../../../../docs/architecture/LAYER_CONTRACTS.md`
- `../../drawskills/visio-figure-builder/references/layout-iteration-notes.md`

