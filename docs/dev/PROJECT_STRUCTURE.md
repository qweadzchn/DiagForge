# PROJECT_STRUCTURE

## 顶层目录

### `agent/skills/plannerskills/`

总控规划层。

包含：

- `visio-drawing-orchestrator/`: 教 agent 如何先分析图，再产出计划

职责边界：

- 负责输入图分析和任务拆解
- 负责决定调用哪些 drawskills / visioskills
- 不直接承担底层执行
- 不替代长期经验沉淀

入口文件：

- `agent/skills/plannerskills/README.md`
- `agent/skills/plannerskills/visio-drawing-orchestrator/SKILL.md`

### `agent/skills/drawskills/`

复合绘图层。

包含：

- `schemas/`: DrawDSL schema
- `examples/`: 最小结构化绘图示例
- `visio-figure-builder/`: 教 agent 如何把计划变成布局、样式和 DrawDSL

职责边界：

- 关注布局、样式、排版和图元间协同约束
- 调用多个 `visioskills`
- 不直接承载 runtime / bridge 逻辑
- 不承担总体任务规划

入口文件：

- `agent/skills/drawskills/README.md`
- `agent/skills/drawskills/visio-figure-builder/SKILL.md`

### `agent/skills/visioskills/`

Visio 原子执行层。

包含：

- `bridge_server/`: Windows 侧 bridge 服务与 Visio COM adapter
- `client/`: WSL / Python 侧 HTTP 客户端
- `OPERATIONS.md`: 当前支持的稳定操作、约束、缺口
- `visio-operator/`: 教 agent 如何调用这些原子操作

职责边界：

- 关注稳定执行
- 不负责高层绘图审美
- 不负责经验沉淀

入口文件：

- `agent/skills/visioskills/README.md`
- `agent/skills/visioskills/visio-operator/SKILL.md`
- `agent/skills/visioskills/OPERATIONS.md`

- Note:
- Current repo uses Visio as the first backend.
- If Draw.io is added later, prefer a parallel backend directory such as `drawioskills/`.
- Do not leak backend-specific details back into `agent/skills/plannerskills/` or `agent/skills/drawskills/`.

### `agent/skills/learningskills/`

经验沉淀层。

包含：

- `visio-iteration-journal/`: 教 agent 如何做复盘和沉淀
- `templates/`: 经验记录模板
- `lessons/`: 已沉淀的经验

职责边界：

- 记录 generalized lessons
- 归因“为什么出问题”
- 反哺 `plannerskills`、`drawskills` 和 `visioskills`

入口文件：

- `agent/skills/learningskills/README.md`
- `agent/skills/learningskills/visio-iteration-journal/SKILL.md`

### `Setup/`

单次绘图任务的操作入口。

包含：

- `draw-job.template.json`: 任务配置模板
- `job.schema.json`: 执行设置 schema
- `analysis.schema.json`: 输入图分析产物 schema
- `plan.schema.json`: 绘图计划产物 schema
- `round-review.schema.json`: 轮次复盘产物 schema
- `run_draw_job.py`: 任务预检脚本
- `jobs/`: 每个 job 的结构化工作区
- `README.md`: 人类操作流程

职责边界：

- 负责“这次怎么跑”
- 负责这次 job 的标准产物路径
- 不描述图结构本身
- 不替代 DrawDSL

入口文件：

- `Setup/README.md`
- `Setup/draw-job.template.json`
- `Setup/run_draw_job.py`

### `InputReference/`

用户放参考图的目录。

这是运行输入，不是 agent 的长期资产，所以保留在仓库外层。

### `OutputPreview/`

每轮导出 PNG 预览的目录。

它应该保留在仓库外层，而不是放进 `agent/`：

- 它是 run-specific 产物，不是 reusable skill asset
- 人类 review 和脚本都需要稳定、直接的输出路径
- 它和 `OutputEditable/`、`InputReference/` 一起组成任务运行面的外部接口

### `OutputEditable/`

最终可编辑结果的目录。

它同样属于交付产物层，应该和 `OutputPreview/` 并列保留在外层。

### `.runtime/`

内部运行时目录。

包含：

- `bridge_exports/`: bridge 生成的一次性 PNG 暂存文件

职责边界：

- 只服务 bridge/runtime
- 不作为人类 review 的正式输出目录
- 不进入 `agent/`
- 默认应被 git 忽略

### `docs/`

面向人类开发者的项目文档。

包含：

- `setup/`: 部署与 smoke test
- `research/`: 外部调研
- `architecture/`: 内部架构与关键决策
- `LAYER_CONTRACTS.md`: 各层输入输出与禁止行为
- 其他维护型文档

## 推荐阅读顺序

1. `README.md`
2. `Setup/README.md`
3. `docs/architecture/LAYER_CONTRACTS.md`
4. `docs/architecture/ARTIFACT_CONTRACTS.md`
5. `AGENT_GUIDE.md`
6. `docs/human/setup/WINDOWS_BRIDGE_DEPLOY.md`
7. `docs/human/setup/SMOKE_TEST_FROM_WSL.md`
8. `docs/architecture/`

