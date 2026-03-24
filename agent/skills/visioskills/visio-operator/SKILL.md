---
name: visio-operator
description: Operate Microsoft Visio through the DrawForge bridge with stable atomic actions. Use when an agent needs to create sessions, add/edit/connect/style shapes, save documents, export PNG previews, or execute a prepared drawing spec without taking over planning decisions.
---

# Visio Operator

使用这个 skill 时，优先保证“稳定执行”，不是一次性画得多花哨。

## Mandatory Preflight

开始前先检查：

1. bridge 已启动
2. `GET /health` 正常
3. `POST /ping_visio` 正常
4. token、保存路径、导出目录明确

任一项失败时，先修运行态，不继续绘图。

## Input Contract

优先消费：

- `drawdsl.json`
- 或已经准备好的显式操作计划

如果 `drawdsl.json` 还不存在，说明上层交接还没完成，先不要在这里猜。

如果当前问题仍然是“这张图该怎么理解”，先退回 `plannerskills`，不要在这里猜。

## Default Execution Contract

- 所有写操作都带 `request_id`
- 所有对象都通过显式 ID 定位
- 每次大改后导出一次 PNG
- 复杂图先加形状，再对齐，再连线，再做样式
- 保存时优先传显式 `save_path`

## Boundary Rule

如果问题是“这个接口怎么调、这个 connector 为什么没 glue 上、应该什么时候 save/export”，留在 `visioskills`。

如果问题是“这一列怎么排更好看、这一组模块怎么布得更像论文图”，转到 `drawskills`。

如果问题是“输入图属于什么图、该先画主区域还是侧边细节、应该选哪些 drawskills”，转到 `plannerskills`。

如果问题是“这次踩的坑以后怎么避免”，转到 `learningskills`。
