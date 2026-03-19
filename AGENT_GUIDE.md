# AGENT_GUIDE

这个文件是本项目给 agent 的总入口。

目标不是让 agent “直接调几个接口”，而是让 agent 明确：

1. 什么时候该调用 `visioskills`
2. 什么时候该调用 `drawskills`
3. 什么时候必须进入 `learningskills`
4. 如何把一次画图任务走成闭环

## Core Mental Model

- `visioskills` 解决“怎么稳定操作 Visio”
- `drawskills` 解决“怎么把图画得清楚、整齐、像样”
- `learningskills` 解决“这次遇到的问题，下次别再从零踩一遍”

不要把三者混成一个大 prompt。

## Recommended Workflow

### 1. Preflight

先确认运行态，再开始画：

1. bridge 已启动
2. `GET /health` 正常
3. `POST /ping_visio` 正常
4. token、导出目录、保存路径都明确

如果 preflight 没过，不进入绘图。

### 2. Pick The Right Layer

遇到任务时按下面规则分流：

- 要新建/编辑/连线/保存/导出：先看 `visioskills/visio-operator/SKILL.md`
- 要复现论文图、排版研究图、控制布局和样式：看 `drawskills/visio-figure-builder/SKILL.md`
- 要总结“这次为什么画歪了、为什么文本爆掉了、为什么导出后发现难看”：看 `learningskills/visio-iteration-journal/SKILL.md`

## Closed-Loop Drawing Rule

任何稍复杂的图，都不要一次画到底。

建议流程：

1. 先出结构骨架
2. 对齐与分布
3. 再连主链路
4. 再做样式
5. 导出 PNG 预览
6. 发现问题后做一轮修正
7. 把可复用经验写进 `learningskills/lessons/`

## What Good Execution Looks Like

一次高质量执行通常会留下这些东西：

- 明确的操作顺序
- 可追溯的 `request_id`
- 保存后的 `.vsdx`
- 一张导出的 PNG 预览
- 一份简洁的变更说明
- 如有新经验，一条新的 generalized lesson

## What Not To Do

- 不要依赖“当前选中的对象”这种隐式上下文
- 不要在对齐前就把所有 connector 画满
- 不要一边发现问题一边只在脑子里记，最后什么都没沉淀
- 不要把一次性的临时修补直接写进 drawskill，当成通用规则

## File Map

- `visioskills/OPERATIONS.md`: 当前原子操作能力与缺口
- `docs/PROJECT_STRUCTURE.md`: 仓库结构总览
- `docs/architecture/`: 设计决策、链路方案、系统分层
- `demo/README.md`: 示例脚本说明

## Default Improvement Loop

当一次绘图任务完成后，优先问这 4 个问题：

1. 这次问题是操作层问题，还是构图层问题？
2. 这个修复是一次性的，还是可复用的？
3. 它应该沉淀到 `visioskills`、`drawskills` 还是 `learningskills`？
4. 下次 agent 如何更早发现它？
