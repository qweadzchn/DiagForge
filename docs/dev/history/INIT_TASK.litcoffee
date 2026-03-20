# 任务书：DiagForge 核心执行层架构调研与实施计划

## 角色设定
你是 `DiagForge` 项目的核心开发 Agent。你的目标是构建一个健壮、可扩展的基于 Visio 的多模态排版系统。请严格遵循“先调研、后汇报、再开发”的原则。

## 核心任务与环境约束
我们目前处于**阶段一**：构建 Agent 到 Visio 的操作链路（即“执行手”）。
- **执行环境约束**：你（Agent 本体）运行在 WSL (Linux) 环境中。
- **目标操作软件**：Microsoft Visio 运行在宿主机的 Windows 环境中。
- **版本控制**：全程需要使用 Git 并同步到 GitHub 远程仓库。


## 架构核心目录设计
系统需围绕以下核心目录展开，你需要在此基础上进行调研和设计：
1. `docs/dev/research/`（调研知识库）：存放所有高价值的技术调研结论。
2. `visioskills/`（原子操作库）：封装与 Visio 交互的最基础动作（如：画框、连线、改色）。这部分需要通过 MCP (Model Context Protocol) 暴露给你自己。
3. `drawskills/`（复合技能库）：存放拓扑记忆和审美规范（如：如何画一个 ResNet 块，IEEE 论文规范配色等），供你调用组合。

## 调研与分析目标 (Action Required)
在编写任何具体业务代码之前，你需要完成以下调研并向主管（User）提交一份《技术实施方案》。**极度重要：坚决不重复造轮子！你必须联网搜索现有的开源组件。**

1. **开源组件与轮子调研 (Open-Source Research)**：
   - 寻找 GitHub/PyPI 上现有的 Python 操控 Visio 的封装库（如针对 `win32com` 的现成 Wrapper）。
   - 调研官方或社区成熟的 MCP Server 模板（如基于 Python 的标准 MCP SDK实现）。
   - 寻找 WSL 与 Windows 宿主机进行 RPC/HTTP 通信的现成轻量级框架。
   - **产出**：在方案中列出你可以直接“拿来主义”的开源库清单及其 GitHub 链接。
2. **跨系统通信方案**：基于你找到的开源库，设计如何在 WSL 中安全调用 Windows 宿主机 Visio 的架构图。
3. **MCP 工具定义**：初步列出 `visioskills` 中需要实现的头 5 个基础操作 API 及其参数结构。
4. **技能库存储结构**：定义 `drawskills` 的配置文件格式（JSON/YAML），给出一个“画两个带箭头的方框”的结构化示例。
5. **Git 工作流**：说明你将如何处理代码的 commit 和同步。

## 阶段任务：调研与方案输出 (Action Required)

在编写任何业务代码前，你必须联网搜索开源组件并完成调研。**极其重要：坚决不重复造轮子！** 你在调研时，必须应用**“高价值过滤机制”**：只记录 Stars 高、近期有维护、且能切实解决跨系统/Visio操作痛点的方案。对于过时或无关的库，直接丢弃，不要污染知识库。

请按以下结构输出文档，并将调研结果固化：

### 1. 技术组件甄选与知识沉淀
在 `docs/dev/research/` 下创建并写入 `01_OpenSource_Components.md`，内容需包含：
- **Visio COM 操控封装库**：寻找 GitHub/PyPI 上比原生 `pywin32` 更好的 Visio 二次封装库（如果有）。对比它们的优缺点。
- **MCP Server SDK**：调研 Anthropic 官方或其他社区成熟的基于 Python 的 MCP Server 实现。
- **WSL-Windows 穿透方案**：重点调研 WSL2 如何获取宿主机 vEthernet IP，以及选择哪种 RPC/HTTP/SSE 机制来实现 WSL(Agent Client) 到 Windows(MCP Server) 的低延迟通信。

### 2. 接口与规范初步设计
向主管（User）提交一份《阶段一技术实施方案》，必须包含以下具体细节：
- **跨系统架构图描述**：明确指出哪部分代码跑在 Windows（如封装了 COM 的 MCP Server），哪部分跑在 WSL（如 OpenClaw Agent），以及它们通过什么协议（如 HTTP 端口 8000）通信。
- **原子 API 定义**：列出 `visioskills` 需要实现的首批 5 个核心 API。必须给出严格的输入参数类型定义（例如：`connect_shapes(source_id: str, target_id: str)`）。
- **复合技能结构**：定义 `drawskills` 的配置文件格式（强推 JSON Schema 或 YAML），并给出一个“绘制两个带箭头相连的矩形”的完整代码结构示例。

## 交付与纪律规范
1. 生成并保存 `docs/dev/research/01_OpenSource_Components.md`。
2. 输出《阶段一技术实施方案》供主管 Review。
3. **红线纪律**：在主管明确回复“方案通过，开始开发”之前，**绝不允许**编写任何 Visio 操控代码、MCP Server 代码，或胡乱创建上述定义之外的文件目录。
4. 等待主管的下一步指令。


<!-- ## 交付规范
1. 阅读本阶段任务后，生成一份详细的《技术实施方案》。
2. **在主管明确回复“方案通过，开始开发”之前，绝不要编写核心业务代码或创建复杂项目结构。**
3. 等待主管指令。 -->

