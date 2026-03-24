# 02_SYSTEM_ARCHITECTURE_FULL_DESIGN

> 目标：给出 DrawForge 的完整可持续架构，确保“不是 demo，而是科研可用生产系统”。

---

## 1. 设计原则

1. **执行内核优先**：先保证稳定执行，再扩展智能策略。
2. **显式状态**：所有对象定位必须显式 id，拒绝隐式上下文。
3. **可恢复**：失败可定位、可重试、可回滚到检查点。
4. **可演进**：模型可替换，协议与经验资产不报废。
5. **可审计**：每次操作可追溯“谁在何时做了什么”。

---

## 2. 分层总览

### L0 用户意图层（Intent Layer）
- 输入：自然语言需求（后续可接图片/草图）
- 输出：任务目标约束（图类型、风格、结构要求）

### L1 规划层（Planner / drawskills）
- 作用：把目标拆成可执行图结构计划
- 资产：drawskills 模板（如 ResNet 块、论文图规范）
- 输出：DrawDSL（结构化图脚本）

### L2 编译与校验层（Compiler/Guard）
- 作用：对 LLM 产物做“编译器式”约束
- 步骤：
  1) 语法检查
  2) 类型检查
  3) 引用检查
  4) 规则检查（审美/规范）
  5) 风险检查
  6) 降级与重写
- 输出：ExecIR（可执行中间表示）

### L3 原子执行层（visioskills Runtime）
- 作用：将 ExecIR 转为稳定原子命令集
- 典型命令：create_shape / set_text / connect / align / style
- 要求：幂等 request_id + 显式对象定位

### L4 Bridge 服务层（Windows）
- 作用：承接 HTTP 请求并串行调用 Visio COM
- 核心：Session Manager + Command Queue(STA) + Error Mapper + Audit Logger

### L5 Visio COM 层
- 作用：最终落地到 .vsdx 的唯一写入口

---

## 3. 为什么需要“接 Visio 端口的东西”

需要，而且是必需组件：**Windows Bridge Service**。

原因：
- COM 在 Windows 会话中运行；WSL 不可直接调用。
- Bridge 将不稳定因素（COM 错误、线程问题）隔离在一层。
- Bridge 统一提供安全、日志、重试、恢复能力。

---

## 4. 为什么需要“类似编译器的检查层”

LLM 输出天然有不确定性。
如果不经过编译/校验直接执行，会出现：
- 引用不存在对象
- 参数单位混乱
- 违反页面约束
- 不符合科研绘图规范

编译层的作用是把“可能正确”变成“可执行且可验证正确”。

---

## 5. 结构化语言设计（可持续关键）

建议两级表示：

1. **DrawDSL（平台无关）**
   - 描述“画什么”
   - 包含 nodes/edges/layout/style/constraints

2. **ExecIR（平台相关）**
   - 描述“怎么画”
   - 直接映射 visioskills 原子操作序列

价值：
- 模型升级不影响底层执行契约。
- 后续可接其他绘图后端（理论可扩展）。
- 经验可沉淀为模板与规则，而非散落提示词。

---

## 6. visioskills 与 drawskills 角色边界

### visioskills（原子库）
- 关注执行正确性与稳定性
- 不承载复杂语义
- 例：`create_rectangle`, `set_text`, `connect_shapes`

### drawskills（复合库）
- 关注结构模板与审美规范
- 调用多个 visioskills 组合出高层图元
- 例：`draw_resnet_block`, `draw_two_stage_pipeline`

边界清晰是可维护性的核心。

---

## 7. 经验沉淀系统（你强调的“可持续”）

沉淀对象：
1. DrawDSL 模板成功率
2. 执行失败模式（错误码、上下文）
3. 修复策略（自动重试/重规划）
4. 质量评分（布局整齐度、规范匹配度）

机制：
- 所有执行记录结构化入库（至少 JSONL）
- 建立回归图集，每次升级自动回放
- 以数据驱动改进 drawskills 与校验规则

---

## 8. 安全与稳定策略（防 Visio 崩溃）

1. COM 串行执行（STA）
2. 写操作幂等 request_id
3. 严格错误分级
4. 超时+重试+熔断
5. 检查点保存与恢复
6. 最小网络暴露与鉴权

这不是“限制模型”，而是“保护系统可长期运行”。

---

## 9. 版本演进与不报废策略

- Tool 协议版本化：`tool@v1`, `tool@v2`
- 能力协商：Agent 启动先握手支持版本
- 兼容窗口：旧版保留一段周期
- 回归门禁：通过基准图集才允许上线

因此模型升级不会导致系统整体报废。

---

## 10. 开发路线图（先基础后扩展）

### Phase 1（当前）
- 打通 WSL -> Windows Bridge -> Visio COM
- 完成最小原子操作 + 日志 + 恢复

### Phase 2
- 建立 DrawDSL + 编译/校验层
- 实现首批 drawskills（结构化复用）

### Phase 3
- 经验库闭环（回归、评分、自动修复）
- 扩展科研场景复杂模板

---

## 11. 本次讨论结论记录

1. 该项目复杂度来自“长期可靠系统”，不是单次画图。
2. 必须先做 Windows Bridge，WSL 不直接碰 COM。
3. 必须有编译/校验层，不能让 LLM 输出裸奔直达执行层。
4. 必须定义结构化语言（DrawDSL/ExecIR）以承载经验沉淀。
5. 必须先做执行内核，再扩 drawskills，避免堆成技术垃圾。

---

## 12. 立即行动建议

- 先完成连接链路验证与稳定性验收（见文档 01）。
- 通过后再冻结 visioskills v1 协议。
- 未通过前，不进入复杂业务开发。
