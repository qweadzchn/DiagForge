---
name: visio-operator
description: Operate Microsoft Visio through the png2vsdx bridge with stable atomic actions. Use when an agent needs to create sessions, add/edit/connect/style shapes, save documents, export PNG previews, run smoke tests, or compile higher-level drawing plans into explicit visioskills calls.
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

## Default Execution Contract

- 所有写操作都带 `request_id`
- 所有对象都通过显式 ID 定位
- 每次大改后导出一次 PNG
- 复杂图先加形状，再对齐，再连线，再做样式
- 保存时优先传显式 `save_path`

## Good Usage Pattern

1. 创建 session
2. 批量放置基础 shapes
3. 调整 geometry
4. 对齐与分布
5. 设置文本和颜色
6. 添加 connector
7. 导出 PNG 预览
8. 保存文档

## Failure Handling

- 4xx: 先检查 payload 和 session 状态
- 5xx: 按同一 `request_id` 重试一次
- 如果还是失败：返回失败步骤、关键参数、当前上下文

## Read These Files As Needed

- `../OPERATIONS.md`
- `../client/http_client.py`
- `../bridge_server/app.py`
- `../../AGENT_GUIDE.md`

## Boundary Rule

如果问题是“这个接口怎么调、这个 connector 为什么没 glue 上、应该什么时候 save/export”，留在 `visioskills`。

如果问题是“这一列怎么排更好看、这一组模块怎么布得更像论文图”，转到 `drawskills`。

如果问题是“这次踩的坑以后怎么避免”，转到 `learningskills`。
