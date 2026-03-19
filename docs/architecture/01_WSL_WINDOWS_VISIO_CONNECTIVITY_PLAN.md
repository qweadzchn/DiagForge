# 01_WSL_WINDOWS_VISIO_CONNECTIVITY_PLAN

> 目标：先打通并验证 **WSL Agent -> Windows Bridge -> Visio COM** 最小链路。

## 1. 底层机制（必须先理解）

- Visio COM 只能由 Windows 用户会话中的进程稳定持有。
- WSL(Linux) 不能原生直接操作 COM 对象。
- 因此必须引入 Windows 侧 Bridge 进程，WSL 通过 HTTP/TCP 调用。

结论：
`WSL Agent -> HTTP -> Windows Bridge Service -> Visio COM -> .vsdx`

## 2. 最小可测能力（M0）

Bridge 先只提供 4 个 API：

1. `GET /health`
   - 返回服务健康状态与版本。
2. `POST /ping_visio`
   - 验证 COM 初始化、Visio 进程可达性。
3. `POST /open_or_create_doc`
   - 打开/创建测试文档，返回 `document_id`。
4. `POST /add_rectangle`
   - 在指定页添加矩形，返回 `shape_id`。

## 3. 连接验证步骤（建议顺序）

### Step A: Windows 侧准备

1. 确认 Visio 可手动打开。
2. 安装依赖：Python、pywin32、FastAPI、uvicorn。
3. 启动 Bridge 服务（本地端口，如 18761）。

### Step B: Windows 本地自检

- `GET /health` 应返回 `ok`。
- `POST /ping_visio` 应返回 Visio 版本或可访问标记。

### Step C: WSL 连通验证

1. 在 WSL 用 `curl` 调 `health`。
2. 再调 `ping_visio`。
3. 若通过，执行 `open_or_create_doc -> add_rectangle`。

## 4. 常见失败与定位

1. **服务未启动/端口未监听**
   - 现象：连接拒绝。
   - 处理：检查服务进程与端口监听。

2. **防火墙拦截**
   - 现象：超时。
   - 处理：放行指定端口或改为仅本机可达策略。

3. **WSL 到 Windows 地址错误**
   - 现象：DNS/路由失败。
   - 处理：使用稳定主机地址配置并固化到环境变量。

4. **COM 初始化失败**
   - 现象：`ping_visio` 返回 COM 异常。
   - 处理：检查 Visio 安装、权限、位数兼容、用户会话状态。

5. **线程模型错误（高危）**
   - 现象：间歇性异常/卡死。
   - 处理：确保所有 COM 调用走单线程串行队列。

## 5. 安全与防崩最低要求

- 仅暴露最小 API 面。
- 必须鉴权（Bearer Token）。
- 写操作必须 `request_id`（幂等）。
- 超时控制 + 有限重试。
- 连续失败触发保护模式。
- 关键步骤前自动 checkpoint。

## 6. 验收标准（通过才进入下一阶段）

1. 连续 100 次 `ping_visio` 无崩溃。
2. 连续 100 次 `add_rectangle` 成功率 >= 99%。
3. 任意 1 次失败后服务可继续处理后续请求。
4. 每次请求都有完整日志（含 request_id 与错误码）。

## 7. 通过后的下一步

- 固化 `visioskills v1` 最小原子操作协议。
- 增加编译/校验层（DrawDSL -> ExecIR -> visioskills）。
- 再进入 drawskills 复合技能。
