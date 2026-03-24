# LAYER_CONTRACTS

这个文件定义 DrawForge 各层的输入、输出、职责边界和禁止行为。

目标只有一个：让 agent 一进入仓库，就知道自己当前应该在哪一层做决定。

配套的产物定义见 `docs/architecture/ARTIFACT_CONTRACTS.md`。

## 总流程

标准执行顺序：

1. `Setup`
2. `plannerskills`
3. `drawskills`
4. `visioskills`
5. `learningskills`

不要跳层，也不要让下层替上层做决定。

## 每层只回答一个核心问题

- `Setup`: 这次任务怎么跑
- `plannerskills`: 这张图是什么、先画什么
- `drawskills`: 怎么排版和设样式更合理
- `visioskills`: 怎么稳定在 Visio 里执行
- `learningskills`: 这次经验以后怎么复用

## 后端扩展原则

当前默认后端是 Microsoft Visio，所以执行层目录是 `agent/skills/visioskills/`。

以后如果要支持其他工业图表软件，例如 Draw.io，原则上应该新增平行的后端执行层，例如 `drawioskills/`，而不是把上层重新写一遍。

理想边界是：
- `plannerskills` 尽量不感知具体绘图软件
- `drawskills` 尽量输出后端无关的布局、文本、容器、连线语义
- 后端层负责把这些意图映射到具体软件能力
- `learningskills` 优先沉淀跨后端可复用经验

也就是说，新增后端不应推翻上层认知流，而应替换或扩展“执行抓手”。

## 1. Setup

职责：

- 定义单次任务的运行配置
- 指定输入图、输出目录、轮次限制、保存策略
- 创建 job workspace 和标准产物路径

输入：

- `InputReference/<image>`
- `Setup/draw-job.local.json`

输出：

- `Setup/jobs/<job_name>/analysis.json`
- `Setup/jobs/<job_name>/plan.json`
- `Setup/jobs/<job_name>/drawdsl.json`
- `Setup/jobs/<job_name>/reviews/`
- `Setup/jobs/<job_name>/run-summary.json`

禁止：

- 不负责分析图结构
- 不负责决定怎么画
- 不直接调用 Visio COM

## 2. plannerskills

职责：

- 看输入图
- 拆出区域、模块、箭头、文字、风格
- 判断这是一类什么图
- 选择该用哪些 drawskills 和 visioskills 能力
- 产出“本次该怎么画”的计划

输入：

- 输入图片
- `analysis.json`
- 历史 lessons

输出：

- 更新后的 `analysis.json`
- `plan.json`

禁止：

- 不直接生成 Visio 调用序列
- 不直接写死具体 `shape_id`
- 不替代 drawskills 做具体排版

## 3. drawskills

职责：

- 把 planner 的计划变成可执行的绘图规格
- 决定字号、框尺寸、文字方向、最小间距、线条语义
- 把“图意图”编译成 DrawDSL

输入：

- `plan.json`
- layout/style references
- 相关 lessons

输出：

- `drawdsl.json`

禁止：

- 不直接承担跨轮 orchestration
- 不直接管理 bridge/runtime
- 不承担长期经验库维护

## 4. visioskills

职责：

- 把 DrawDSL 或更低层命令稳定落到 Visio
- 创建 session、加 shape、改 geometry、改 style、连线、保存、导出

输入：

- `drawdsl.json` 或显式操作计划

输出：

- `.vsdx`
- 预览 PNG
- request-level 执行结果

禁止：

- 不分析图是什么类型
- 不自己决定布局风格
- 不把一次性经验硬编码成通用规划逻辑

## 5. learningskills

职责：

- 复盘本轮结果
- 记录失败模式、根因和通用修复方式
- 决定经验应该反哺 planner、drawskills 还是 visioskills

输入：

- `reviews/round-*.json`
- 导出预览 PNG
- 执行结果和错误

输出：

- `agent/skills/learningskills/lessons/*.md`
- 对 planner/draw/visio 的回写建议

禁止：

- 不直接替代某一层完成工作
- 不保存一次任务的流水账当成长期知识

## 经验归属规则

遇到一个问题时，按下面规则决定归属：

- “怎么操作某个 Visio 功能” -> `visioskills`
- “框、字、方向、间距、线条样式怎样联动更合理” -> `drawskills`
- “输入图属于什么图、该先画哪一块、该用哪些能力” -> `plannerskills`
- “这次为什么失败、以后怎么避免” -> `learningskills`

## 当前最重要的通用约束

这些约束不是图专用技巧，而是默认绘图规则：

- 字体默认 `Times New Roman`
- 字号、框尺寸和间距必须联动
- 文字方向改变时，框和邻近间距必须重算
- 任何两个图元默认不能重叠
- 线条样式要有语义，而不是统一一种线

