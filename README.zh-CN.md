# DiagForge

[English](README.md) | [简体中文](README.zh-CN.md)

通过构建在专业图表软件之上的 Agentic Abstraction Layer，锻造可持续编辑的人类级图表资产。

DiagForge 不是一个一次性的“PNG 转 VSDX”脚本。
它是一个围绕图表工作的持久化 Agentic Abstraction Layer 仓库：

- 人类提供粗粒度视觉目标和意图
- 模型负责规划与推理
- 软件后端负责稳定执行
- 预览图和运行反馈驱动反思
- 重复修复会沉淀为可复用资产

目标是把死的像素图，复活成结构化、可编辑、可继续演化的图表资产。当前主要面向 Microsoft Visio，后续也可以扩展到其他图表软件后端。

## 核心思想

基础模型是推理引擎。
真正的长期价值在模型之外：

- planning contracts
- layout rules
- drawing DSLs
- software operation layers
- review loops
- reusable lessons

这部分才是我们希望随着时间不断增强、且不会因为底层模型更替而贬值的资产。

## 为什么叫 `DiagForge`

`Diag` 指向我们真正关心的对象：

- 图表逻辑
- 空间拓扑
- 布局意图
- 可编辑结构

`Forge` 指向核心工作闭环：

- 把人类模糊输入当作原材料
- 通过软件技能执行
- 读取环境反馈
- 反思哪里失败
- 修正下一轮结果
- 把重复修复沉淀为可复用资产

所以这个仓库不应该被理解为“导出一张静态图片”。
它是在一个闭环中锻造活的、可编辑的图表资产。

## 这个项目的不同之处

大多数图表自动化项目会停在下面某一个点：

- 只能生成一次图，不能按轮次持续改进
- 只能点软件，但不知道怎么把图画好
- 能跑 demo，但无法留下可复用的规划与复盘资产

DiagForge 想补齐中间这一层：

`intent -> plan -> drawdsl -> backend -> preview -> review -> lesson`

这条闭环本身就是产品。

## 闭环机制

DiagForge 把画图任务视为两个耦合过程：

1. 前向执行
   - 分析输入图
   - 规划结构与优先级
   - 把绘图意图编译成 DrawDSL
   - 通过软件后端执行

2. 反向反思
   - 检查预览图和运行反馈
   - 判断失败属于规划、布局还是执行问题
   - 更新规则、检查项和 lessons
   - 让下一轮有可度量的改进

这就是仓库“agentic abstraction layer”方向的核心。

## 分层架构

仓库分成五层。
每一层都应该回答一个核心问题。

- `Setup`
  - 当前在跑哪个 job？
  - 产物输出到哪里？
  - 最多允许多少轮？
- `plannerskills`
  - 这是什么类型的图？
  - 哪些区域重要？
  - 需要哪些能力？
- `drawskills`
  - 布局、文字、间距、容器和连线语义应该怎么处理？
  - 这些意图如何编码成 DrawDSL？
- `visioskills`
  - 如何稳定、可验证地操作 Microsoft Visio？
- `learningskills`
  - 这一轮提炼出了什么可复用经验？

如果你是一个刚进入仓库的 agent，请先读 [AGENT_GUIDE.md](AGENT_GUIDE.md)。

## 仓库结构

```text
Setup/          Job 配置、工作区初始化、执行脚本
plannerskills/  图表分析与任务编排规则
drawskills/     布局、排版、间距、DrawDSL、图形构建逻辑
visioskills/    Visio bridge、原子操作、执行指导
learningskills/ 从绘图轮次中提炼的可复用经验
InputPNG/       输入参考图
OutputPreview/  用于 review 的预览 PNG
OutputVSDX/     最终 VSDX 输出
docs/           合同、架构、配置、流程文档
```

## 标准产物链

对于一个绘图 job，默认产物链是：

1. `Setup/draw-job.local.json`
2. `Setup/jobs/<job>/analysis.json`
3. `Setup/jobs/<job>/plan.json`
4. `Setup/jobs/<job>/drawdsl.json`
5. `OutputPreview/<job>/round-*.png`
6. `OutputVSDX/<final>.vsdx`
7. `Setup/jobs/<job>/reviews/round-*.json`
8. `learningskills/lessons/*.md`

这条链是有意设计的。
不要把一切都折叠进一个 prompt 或一个脚本里。

## 后端方向

当前执行后端是 Microsoft Visio，所以今天的运行层是 `visioskills`。

更长期的方向是：

- 让 `plannerskills` 继续专注图形理解和任务编排
- 让 `drawskills` 继续专注后端无关的绘图意图
- 让 `learningskills` 继续专注可复用的失败模式和经验
- 通过后端专属技能层支持多个软件后端，例如：
  - `visioskills`
  - 未来的 `drawioskills`

这并不意味着“只要多加一个文件夹就什么都不用改”。
真正的目标是：高层认知闭环尽量稳定，而后端特定的执行与能力映射被清晰隔离。

## 当前能力

已经实现或可用的能力：

- 基于 Windows FastAPI 的 Visio COM bridge
- 稳定的 session、save、close、export 流程
- 节点和连接线样式 readback
- 画图前自动 page auto-fit
- 文本框耦合
- 透明 label shape
- connector glue-side control
- 通过 `DrawDSL -> executor -> bridge -> readback` 支持竖排文本
- 通用布局后处理，包括 minimum-gap reflow 和 container auto-fit
- 结构化 round review 和 reusable lessons

仍然较弱或缺失的部分：

- 更丰富的连线路由控制
- 图级 readback
- 原生图片放置
- 更广覆盖的 benchmark 图族
- 更强的、位于 Visio 细节之上的后端抽象

## 当前 benchmark 方向

仓库当前使用 `InputPNG/` 下的 benchmark 图来打磨系统。
这些图本身不是终点。
它们是对系统的压力测试：

- 混合布局
- 窄模块
- 文字、框尺寸、间距联动
- 容器尺寸控制
- 连线路由
- 基于预览图的迭代
- planner / draw / runtime 的故障归因

## 快速开始

1. 启动 Windows bridge。
2. 把源 PNG 放进 `InputPNG/`。
3. 复制 `Setup/draw-job.template.json` 为 `Setup/draw-job.local.json`。
4. 运行：

```powershell
python Setup\run_draw_job.py --config Setup\draw-job.local.json
```

然后继续看：

- [Setup/README.md](Setup/README.md)
- [AGENT_GUIDE.md](AGENT_GUIDE.md)
- [docs/ARTIFACT_CONTRACTS.md](docs/ARTIFACT_CONTRACTS.md)
- [docs/LAYER_CONTRACTS.md](docs/LAYER_CONTRACTS.md)
- [docs/PLAN_TO_OPERATION_LOOP.md](docs/PLAN_TO_OPERATION_LOOP.md)

## 项目方向

DiagForge 想成为构建在现有人类高质量软件之上的可复用 agentic software layer。

在当前阶段，这个“人类软件资产”是 Microsoft Visio。
后续也可能扩展到其他图表软件。

如果这套系统成立，那么长期价值不在于某一次模型运行。
长期价值在于不断增长的这组资产：

- contracts
- skills
- operations
- layout rules
- review rules
- lessons
- backend adapters

这部分才是我们想持续做强的东西。
