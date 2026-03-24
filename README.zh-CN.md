# DrawForge

[English](README.md) | [简体中文](README.zh-CN.md)

DrawForge 是一个实验性框架，目标是基于 Microsoft Visio，构建一套由 agent 驱动的闭环流程，把参考图逐步转成可编辑的图表资产。

当前项目主要关注：

- 分析输入图
- 规划布局和绘制策略
- 把规划编译成 DrawDSL
- 通过 Visio bridge 执行
- 导出预览图、逐轮 review，并把经验沉淀下来

这个仓库的重点，不是一次性生成结果，而是把围绕这条闭环的工作流、合同和可复用技能建设起来。

## 从哪里开始

- 第一次接触项目： [GET_STARTED.md](GET_STARTED.md)
- 想跑一个绘图任务： [Setup/README.md](Setup/README.md)
- 想让新 agent 进入仓库工作： [AGENT_START_HERE.md](AGENT_START_HERE.md)
- agent 资产总入口： [agent/README.md](agent/README.md)
- 想开发系统本身： [DEVELOPMENT.md](DEVELOPMENT.md)
- 想看运行模式和写权限规则： [MODE_POLICY.md](MODE_POLICY.md)

## 这个仓库在做什么

DrawForge 不是要替代专业图表软件。
它更像是在尝试把这些软件纳入一套清晰的 agent 工作流：

`intent -> analysis -> plan -> drawdsl -> backend -> preview -> review -> lesson`

为了让这条流程可以持续改进，仓库把不同决策明确拆层，而不是把所有逻辑塞进一个 prompt 里。

## 仓库导览

- `Setup/`
  - job 配置、工作区初始化、执行脚本
- `agent/`
  - 面向 agent 的可复用资产和技能入口
- `agent/skills/plannerskills/`
  - 图形分析和任务编排
- `agent/skills/drawskills/`
  - 布局、排版、间距、DrawDSL、绘图规则
- `agent/skills/visioskills/`
  - Visio bridge、原子操作、执行指导
- `agent/skills/learningskills/`
  - 从绘图轮次中提炼的可复用经验
- `docs/`
  - 面向使用者、开发者、架构和调研的文档

如果你需要更详细的 agent 工作说明，请看 [AGENT_GUIDE.md](AGENT_GUIDE.md)。

## 这条闭环怎么工作

1. 分析输入图，识别主要区域和结构。
2. 规划本轮先画什么、重点改进什么。
3. 把绘图意图编译成 DrawDSL。
4. 通过软件后端执行。
5. 导出预览图，并与目标图对比。
6. 记录哪些地方成功了，哪些地方失败了，哪些经验应该沉淀为长期资产。

## 当前状态

已经能工作的部分：

- 基于 Windows FastAPI 的 Visio COM bridge
- 稳定的 session、save、close、export 流程
- 基于 DrawDSL 的节点和连线执行
- 文本框耦合和竖排文本支持
- 基于预览图的 review 流程
- 在 `agent/skills/learningskills/` 中沉淀可复用经验

还不够强的部分：

- 更丰富的连线路由控制
- 图级 readback
- 原生图片放置
- 更广的 benchmark 覆盖
- 更强的、超出 Visio 细节层的后端抽象

## 文档入口

- 项目文档总索引： [docs/README.md](docs/README.md)
- 架构与合同： [docs/architecture/README.md](docs/architecture/README.md)
- 面向使用者的操作文档： [docs/human/README.md](docs/human/README.md)
- 面向开发者的文档： [docs/dev/README.md](docs/dev/README.md)

## 许可证

DrawForge 使用 MIT License。
见 [LICENSE](LICENSE)。

## 后端方向

当前执行后端是 Microsoft Visio。
更高层的目标，是尽量保持规划、绘图意图、review 和 learning 这些层稳定，同时允许未来加入新的后端，比如并行的 `drawioskills/`。

## 项目方向

如果这个仓库长期有价值，真正会沉淀下来的，不会是某一次模型运行。
而会是不断增长的这组资产：

- contracts
- skills
- operations
- layout rules
- review rules
- lessons
- backend adapters

这也是项目希望持续做强的部分。
