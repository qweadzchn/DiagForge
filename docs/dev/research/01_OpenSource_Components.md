# 01_OpenSource_Components

更新时间：2026-03-16 (UTC)

## 调研范围与过滤标准

本次围绕 4 个主题做了有目的检索：
1. Visio COM 自动化（Windows 执行层）
2. MCP Python Server 生态（工具暴露层）
3. LLM + 图DSL（规划/中间表示层）
4. 可持续经验沉淀（状态/日志/回归层）

过滤原则（高价值过滤机制）：
- 优先 GitHub Star 较高、近期有维护、与本项目直接相关的项目
- 低 Star 但“方向唯一”的项目只作为样例参考，不作为核心依赖
- 营销站点/泛文章/不可复现方案直接降权

---

## 一、可直接借鉴的核心组件（推荐清单）

| 组件 | 领域 | Stars* | 最近活跃* | 可借鉴点 | 结论 |
|---|---:|---:|---|---|---|
| https://github.com/modelcontextprotocol/python-sdk | MCP Python SDK | 22k+ | 2026-03 | FastMCP、Tool/Resource、SSE/HTTP/stdio 传输 | **必须采用**（协议层基座） |
| https://github.com/modelcontextprotocol/servers | MCP 服务器集合 | 81k+ | 2026-03 | server 组织方式、工具 schema 规范、参考实现 | **必须参考**（工程模板库） |
| https://github.com/GongRzhe/Office-Visio-MCP-Server | Visio MCP 专项 | 46 | 2025-05 | Visio COM + MCP 的最小可运行链路 | **强参考**（起步快） |
| https://github.com/saveenr/VisioAutomation | .NET Visio 自动化 | 107 | 2025-12 | Visio 对象模型封装思路、稳定 API 组织 | **强参考**（设计灵感） |
| https://github.com/mhammond/pywin32 | Windows COM 基础 | 3k+ | 持续维护 | Python 调 COM 的事实标准 | **必须采用**（底层依赖） |
| https://github.com/mermaid-js/mermaid | 图DSL生态 | 86k+ | 2026-03 | 图结构文本化、可读可版本化 | **参考**（DSL设计借鉴） |
| https://github.com/terrastruct/d2 | 图DSL生态 | 23k+ | 2025-10 | 声明式图表示、布局表达能力 | **参考**（DSL能力边界） |
| https://github.com/mingrammer/diagrams | Diagram-as-code | 42k+ | 2026-02 | Python 声明式图构造模式 | **参考**（API风格） |

\* Stars / 最近活跃来自 GitHub API 查询（本次调研时点）。

---

## 二、Visio COM 自动化：现状与结论

### 2.1 现实结论
- **不存在“超成熟、高星、全功能”的 Python Visio 封装大一统库**。
- 可行路径仍是：**pywin32 + 自建稳定封装层**。
- 已有开源（如 Office-Visio-MCP-Server、visiopy）可作为“起步样例”，但距离科研生产级仍有工程缺口。

### 2.2 能复用什么
1. `pywin32`：COM 调用底层（必须）。
2. `Office-Visio-MCP-Server`：可复用其工具定义与基础操作流程。
3. `VisioAutomation(.NET)`：借鉴对象模型封装与 API 分层设计（即便语言不同）。

### 2.3 不能照搬什么
- 仅基于 `file_path` 的无会话操作（不利于多轮编辑）
- 无幂等 request_id 的写操作（重试会污染图）
- 无执行队列的 COM 直连调用（稳定性风险高）

---

## 三、MCP Server 生态：现状与结论

### 3.1 推荐基座
- 直接采用 `modelcontextprotocol/python-sdk`（FastMCP）构建 `visioskills` MCP Server。
- 参考 `modelcontextprotocol/servers` 的目录、schema 与测试组织方式。

### 3.2 关键收益
- 协议层与 LLM 解耦：后续换模型不推翻工具层。
- 传输可切换（stdio/SSE/HTTP），便于先本地再跨机。
- 工具 schema 可版本化，支持平滑升级。

---

## 四、WSL ↔ Windows 通信：现状与结论

官方建议与社区实践一致：
- WSL2 默认 NAT；可考虑 mirrored networking（视环境）。
- 跨边界访问需明确主机地址策略与防火墙策略。

**本项目建议固定方案（v1）：**
1. Windows 侧常驻 Bridge（FastAPI）。
2. 仅监听本机/受控网段端口（如 18761）。
3. WSL 侧通过 HTTP 调用，强制 Bearer Token。
4. COM 调用统一串行队列（STA）执行。

参考：
- https://learn.microsoft.com/en-us/windows/wsl/networking
- https://learn.microsoft.com/en-us/windows/wsl/wsl-config

---

## 五、LLM + 图DSL：可借鉴但不能照抄

### 5.1 可借鉴方向
- Mermaid / D2 证明了“图结构文本化”在版本管理、审查、复用上的价值。
- `drawskills` 应采用类似 DSL 的结构化表示，而不是直接自然语言驱动执行层。

### 5.2 不能直接拿来替代的原因
- Mermaid/D2 是渲染 DSL，不是 Visio COM 执行协议。
- 我们需要双层中间表示：
  - **DrawDSL**（画什么，平台无关）
  - **ExecIR**（怎么画，面向 visioskills）

---

## 六、科研绘图 Agent 与“经验沉淀”架构

公开项目中：
- “科研智能体直接长期稳定操控 Visio”的完整开源体系几乎没有。
- 现有多为：图DSL生成、UI工具辅助、或单次自动化脚本。

因此本项目的差异化价值在于：
1. 执行层稳定内核（会话/幂等/错误分级/恢复）
2. 结构化技能层（drawskills 模板）
3. 经验闭环（日志 -> 回归 -> 技能迭代）

建议经验闭环最小实现：
- 每次执行记录：`request_id, skill_id, params_hash, result, error_code, latency`
- 建立基准任务集：`two-box-arrow`, `resnet-block`, `pipeline-3stage`
- 每次升级自动回放，未达阈值不得上线

---

## 七、现阶段“可借鉴项目 + 不可取坑点 + 应采用设计”

### 7.1 可借鉴项目（按优先级）
1. modelcontextprotocol/python-sdk
2. modelcontextprotocol/servers
3. Office-Visio-MCP-Server
4. VisioAutomation (.NET)
5. mermaid / d2 / diagrams（DSL思路）

### 7.2 不可取坑点
- 让 LLM 输出直接打 COM（无编译校验层）
- 执行依赖“当前选中对象”等隐式上下文
- 无幂等、无审计、无恢复机制
- 把 DSL 当执行协议（缺少 ExecIR 层）

### 7.3 我们应采用的设计
- **Windows Bridge + WSL Client** 的跨系统主链路
- `visioskills`（原子工具）与 `drawskills`（复合模板）强分层
- `DrawDSL -> Compiler/Guard -> ExecIR -> visioskills` 执行流水线
- 版本化工具协议 + 回归基准 + 事件日志沉淀

---

## 八、调研中的现实问题（透明记录）

- OpenClaw `web_search` 在当前环境缺少 `PERPLEXITY_API_KEY`，不可用。
- 已改用 Tavily skill (`skills/tavily-search-1.0.0`) + 官方文档抓取 + GitHub API 验证完成本轮调研。

---

## 附：关键链接

- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP Servers: https://github.com/modelcontextprotocol/servers
- Office Visio MCP Server: https://github.com/GongRzhe/Office-Visio-MCP-Server
- VisioAutomation (.NET): https://github.com/saveenr/VisioAutomation
- pywin32: https://github.com/mhammond/pywin32
- Mermaid: https://github.com/mermaid-js/mermaid
- D2: https://github.com/terrastruct/d2
- Diagrams (Python): https://github.com/mingrammer/diagrams
- WSL networking: https://learn.microsoft.com/en-us/windows/wsl/networking
- WSL config: https://learn.microsoft.com/en-us/windows/wsl/wsl-config
