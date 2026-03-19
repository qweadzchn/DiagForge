# DiagForge 开发文档（阶段一）

更新时间：2026-03-16 UTC

---

## 0. 结论先行：这个项目能不能做、能不能做成可用系统？

**可以开发，且具备做成“科研可用系统”的可行性。**
但前提是坚持当前已形成的工程路线：
1. 先做稳定执行内核（不是 demo 脚本）
2. 严格分层（drawskills ≠ visioskills）
3. 以会话、幂等、错误恢复、回归基准作为上线门槛

如果跳过这些，项目会退化成“偶尔能跑一次”的半自动脚本，不满足你的目标。

---

## 1) 目前已知信息（含文档挂载路径）

### 1.1 任务与硬约束（官方任务书）
- `INIT_TASK.md`
  - 约束：Agent 在 WSL，Visio 在 Windows
  - 目标：先调研后开发
  - 需定义：跨系统方案、visioskills API、drawskills 格式、Git 工作流
- `INIT_TASK.litcoffee`
  - 新增要求：必须优先做开源组件调研（禁止重复造轮子）
  - 新增目录：`docs/research/`
  - 新增交付：`docs/research/01_OpenSource_Components.md`

### 1.2 已有调研文档
- `docs/research/01_OpenSource_Components.md`
  - 已筛选 MCP SDK、Visio 相关样例、WSL 网络文档、图 DSL 生态
  - 结论：`pywin32 + Windows Bridge + MCP Python SDK` 是当前最现实主线
- `docs/architecture/00_DECISIONS_TO_CONFIRM.md`
  - 已给出需拍板决策清单（协议、鉴权、幂等、熔断、MVP 范围）
- `docs/architecture/01_WSL_WINDOWS_VISIO_CONNECTIVITY_PLAN.md`
  - 给出最小链路验证路线与验收指标（100 次稳定性验证等）
- `docs/architecture/02_SYSTEM_ARCHITECTURE_FULL_DESIGN.md`
  - 给出分层架构（Intent/Planner/Compiler/Runtime/Bridge/COM）

### 1.3 仓库与协作状态
- 已有远程：`git@github.com:qweadzchn/DiagForge.git`
- SSH 认证已打通（可访问 private 仓库）
- 当前本地仍处于“调研资料阶段”，尚未进入业务实现

---

## 2) 你已确认过的事项（来自会话）

> 注：以下是会话级确认，不等同于“技术规格冻结”。

1. 继续推进 `DiagForge` 调研，且是**深度调研**，不是泛搜。
2. 项目目标是**真实可用科研系统**，明确不是 demo。
3. GitHub 使用 private 仓库即可，不需要改 public。
4. 远程地址采用 SSH（`git@github.com:qweadzchn/DiagForge.git`）。
5. 允许按任务书先输出方案/文档，再等你确认后进入开发。

---

## 3) 仍需你拍板 / 仍需补充调研的关键点

### 3.1 需要你拍板（高优先级）
对应文档：`docs/architecture/00_DECISIONS_TO_CONFIRM.md`

A. Bridge 与协议
- [ ] Windows 常驻 Bridge 是否作为唯一主链路（建议：是）
- [ ] v1 通信协议定为 HTTP/JSON（建议：是）
- [ ] 默认端口（建议：18761）
- [ ] 鉴权方式（建议：Bearer Token）

B. 执行稳定性约束
- [ ] COM 严格单线程串行队列（STA）
- [ ] 所有写操作必须携带 `request_id` 幂等
- [ ] 连续错误触发保护模式（熔断/只读）

C. MVP 范围
- [ ] 仅支持单页 + 基础图元 + 连接线 + 基础对齐样式 + 日志恢复
- [ ] 暂缓高级功能（多页协同、复杂自动美化、图像理解）

### 3.2 还需继续调研（技术与工程细节）
1. Visio COM 异常分类与恢复策略细化（可执行错误码体系）
2. WSL2 网络模式（NAT vs mirrored）在你机器上的实测策略
3. MCP transport 选型细化（WSL↔Windows 用 HTTP；MCP 内部 stdio/SSE 的取舍）
4. `drawskills` Schema 的版本演进策略（兼容旧模板）
5. 回归图集与质量评分规则（“科研可用”的客观门槛）

---

## 4) 分部分开发计划（在“方案通过，开始开发”后执行）

### Phase 0：规格冻结（1-2 天）
**输出**：
- `docs/specs/` 下协议与错误码草案（仅文档）
- 决策清单勾选版（冻结 v1）

**通过条件**：
- 关键决策全部确认（至少 A/B/C 三组核心项）

---

### Phase 1：跨系统执行内核（M0-M1）
**目标**：打通并稳定 `WSL -> Windows Bridge -> Visio COM`

**子任务**：
1. Windows Bridge 骨架（健康检查 + 鉴权 + 日志 + 队列）
2. 最小 4 个接口验证（health/ping/open/create/add rectangle）
3. COM 串行化执行与超时控制
4. 稳定性压测（连续请求）

**验收**：
- 连续 100 次关键请求成功率 >= 99%
- 异常后服务可恢复
- 日志可追踪到 request_id

---

### Phase 2：visioskills v1（原子技能）
**目标**：定义并实现首批 5 个稳定原子 API

建议首批：
1. `open_or_create_document`
2. `add_rectangle`
3. `set_shape_text`
4. `connect_shapes`
5. `save_document`

**验收**：
- 参数与返回结构稳定
- 错误码覆盖关键失败场景
- 同一请求重试不产生重复副作用

---

### Phase 3：drawskills v1（复合技能）
**目标**：建立结构化技能配置与执行链路

**子任务**：
1. 定义 YAML/JSON Schema
2. 实现示例 skill：两个方框 + 箭头
3. 运行时 symbol table（逻辑 ID 映射 native shape id）

**验收**：
- skill 可重复执行并得到一致布局
- 支持参数化（文本、位置、颜色）

---

### Phase 4：经验沉淀与回归（科研可用关键）
**目标**：让系统“越用越稳”

**子任务**：
1. 结构化日志（skill_id/error_code/latency）
2. 基准图集回放（two-box/resnet/pipeline）
3. 失败模式归因与修复策略迭代

**验收**：
- 每次版本升级都有回归报告
- 关键技能成功率持续提升

---

## 5) 风险评估（现实版）

### 高风险
1. COM 线程与生命周期处理不当导致 Visio 卡死
2. 并发请求打穿串行约束造成状态错乱
3. 缺少幂等导致“重试=重复绘图污染”

### 中风险
1. WSL 到 Windows 网络地址策略不稳
2. `drawskills` Schema 过早复杂化导致维护困难

### 低风险
1. Git 流程与协作规范（已有成熟实践可复用）

---

## 6) 推荐下一步（现在就可执行）

1. 你先对 `docs/architecture/00_DECISIONS_TO_CONFIRM.md` 逐项勾选（或我给你出一版“建议默认值”供你一次性确认）。
2. 我按你确认结果，补一份 `docs/specs/` 的**v1 接口与错误码文档**（仍不写业务代码）。
3. 你回复“方案通过，开始开发”后，再进入 Phase 1 实现。

---

## 7) 当前判断

- **是否可开发：可以。**
- **是否有希望做成科研可用：有，但必须走“稳定执行内核 + 结构化技能 + 回归沉淀”路线。**
- **当前最缺的不是写代码速度，而是规格冻结与验收门槛。**
