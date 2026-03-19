# png2vsdx

让 agent 像人一样使用 Microsoft Visio 画图的实验性执行系统。

当前仓库的重点不是“单次画一张图”，而是把这件事拆成可以持续演进的 4 层：

1. `visioskills`: 教 agent 稳定操作 Visio。
2. `drawskills`: 教 agent 用这些操作把图画得更好。
3. `learningskills`: 教 agent 把一次次画图中踩过的坑沉淀成经验。
4. `AGENT_GUIDE.md`: 教 agent 什么时候用哪一层，以及如何形成闭环。

## Why This Repo Exists

现有方案大多停在以下其中一类：

- 只能“生成图”，不能长期多轮编辑
- 只能“操作软件”，没有结构化绘图能力
- 能跑 demo，但没有回放、复盘、经验沉淀

`png2vsdx` 想做的是另一条路线：

- `WSL/Agent -> Windows Bridge -> Visio COM`
- 显式 `session_id / shape_id / request_id`
- 结构化 DrawDSL，而不是直接自然语言裸奔到 COM
- 导出 PNG 做闭环预览
- 逐步补上“看图评估 -> 复盘 -> 沉淀”的能力

## Current Status

已经落地：

- Windows 侧 FastAPI bridge
- 单线程 COM 执行队列（STA）
- 基础原子操作：创建会话、加图形、定位、样式、连线、保存、关闭、导出 PNG
- WSL 侧 Python HTTP 客户端
- DrawDSL schema v0.1
- 研究型绘图 skill 雏形
- 三轮 closed-loop 绘图 demo

还在补的关键能力：

- 当前画布的读回和检查能力
- DrawDSL -> ExecIR 的编译与校验层
- learningskills 经验沉淀机制
- 可回放的回归基准图集

## Start Here

- 想看总入口：`AGENT_GUIDE.md`
- 想按“放图 -> 改配置 -> 开始画”的方式跑任务：`Setup/README.md`
- 想看项目结构：`docs/PROJECT_STRUCTURE.md`
- 想部署 bridge：`docs/setup/WINDOWS_BRIDGE_DEPLOY.md`
- 想跑最小闭环：`docs/setup/SMOKE_TEST_FROM_WSL.md`
- 想看系统设计：`docs/architecture/`

## Repository Layout

```text
visioskills/     Atomic Visio operations, bridge server, operator skill
drawskills/      Drawing DSL, figure-building skill, layout/style references
learningskills/  Reusable lessons distilled from drawing iterations
Setup/           Per-job config, runtime checks, operator entrypoint
InputPNG/        Source figures to reproduce
OutputPreview/   Per-round preview exports
OutputVSDX/      Final VSDX outputs
demo/            Example scripts only; generated binaries are gitignored
docs/            Setup, research, architecture, project structure
```

## Quick Workflow

1. 在 Windows 启动 bridge。
2. 把参考图放进 `InputPNG/`，并按 `Setup/README.md` 准备 `Setup/draw-job.local.json`。
3. 用 `python Setup/run_draw_job.py --config Setup/draw-job.local.json` 做一次任务预检。
4. 让 agent 先读 `AGENT_GUIDE.md`，再根据任务进入 `visioskills`、`drawskills`、`learningskills`。
5. 每次大改后导出 PNG 做闭环检查，并把可复用经验沉淀到 `learningskills/lessons/`。

## Near-Term Roadmap

- 补读回能力：列 shape、读 geometry/style、页面边界
- 补编译层：DrawDSL -> ExecIR -> visioskills
- 建立学习闭环：问题归因、修复策略、经验模板
- 建立可展示的 benchmark gallery 和回归流程
