# PROJECT_STRUCTURE

## 顶层目录

### `visioskills/`

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

### `drawskills/`

复合绘图层。

包含：

- `schemas/`: DrawDSL schema
- `examples/`: 最小结构化绘图示例
- `visio-figure-builder/`: 教 agent 如何把高层图意图编排成 Visio 图

职责边界：

- 关注结构规划、布局、样式、排版
- 调用多个 `visioskills`
- 不直接承载运行时 bridge 逻辑

### `learningskills/`

经验沉淀层。

包含：

- `visio-iteration-journal/`: 教 agent 如何做复盘和沉淀
- `templates/`: 经验记录模板
- `lessons/`: 已沉淀的经验

职责边界：

- 记录 generalized lessons
- 归因“为什么出问题”
- 反哺 `visioskills` 和 `drawskills`

### `Setup/`

单次绘图任务的操作入口。

包含：

- `draw-job.template.json`: 任务配置模板
- `job.schema.json`: 执行设置 schema
- `run_draw_job.py`: 任务预检脚本
- `README.md`: 人类操作流程

职责边界：

- 负责“这次怎么跑”
- 不描述图结构本身
- 不替代 DrawDSL

### `InputPNG/`

用户放参考图的目录。

### `OutputPreview/`

每轮导出 PNG 预览的目录。

### `OutputVSDX/`

最终 VSDX 结果的目录。

### `demo/`

示例脚本目录。

只放：

- 可复现的脚本
- 演示用途的小体量说明

不放：

- 临时导出物
- 自动生成的 `.vsdx`
- 调试残留截图

### `docs/`

面向人类开发者的项目文档。

包含：

- `setup/`: 部署与 smoke test
- `research/`: 外部调研
- `architecture/`: 内部架构与关键决策
- 其他维护型文档

## 推荐阅读顺序

1. `README.md`
2. `Setup/README.md`
3. `AGENT_GUIDE.md`
4. `docs/setup/WINDOWS_BRIDGE_DEPLOY.md`
5. `docs/setup/SMOKE_TEST_FROM_WSL.md`
6. `docs/architecture/`
