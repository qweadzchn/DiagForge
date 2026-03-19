---
name: visio-iteration-journal
description: Distill reusable lessons from Visio drawing iterations in png2vsdx. Use when an agent encounters a drawing problem, layout failure, export surprise, bridge recovery issue, or any repeatable obstacle during Visio work and should convert that one-off fix into a generalized lesson stored under learningskills.
---

# Visio Iteration Journal

这个 skill 负责把“这次好不容易解决的问题”变成“下次 agent 可以直接用的经验”。

## When To Capture A Lesson

遇到下面这些情况就应该考虑沉淀：

- 导出 PNG 后才发现布局很乱
- 字体、文本块、尺寸反复调不对
- connector 画早了导致整图难以维护
- bridge / session / save / export 出现可复用的恢复经验
- 某个 drawskill 规则明显该补

## What A Good Lesson Contains

一条好 lesson 至少回答这 5 件事：

1. 问题是什么
2. 触发信号是什么
3. 根因是什么
4. 可复用修复方式是什么
5. 它应该反哺到哪一层

## Capture Workflow

1. 先写清现象，不要一上来就写结论
2. 抽离任务特有细节，保留可泛化信息
3. 用 `../templates/lesson-template.md` 记录
4. 存到 `../lessons/`
5. 如果经验需要变成规则：
   - 操作层经验 -> 更新 `visioskills`
   - 构图层经验 -> 更新 `drawskills`
   - 只是暂时观察 -> 先留在 `lessons/`

## Writing Rule

lesson 必须写成 generalized knowledge，不写成一次任务的流水账。

避免这种写法：

- “今天我在某张图里把第 7 个框往左挪了 0.2 in”

优先这种写法：

- “当同一行模块宽度差异较大时，先统一 anchor，再做 distribute，否则视觉中心会漂移”

## Files To Read

- `../templates/lesson-template.md`
- `../../AGENT_GUIDE.md`
- `../../drawskills/visio-figure-builder/references/layout-iteration-notes.md`
