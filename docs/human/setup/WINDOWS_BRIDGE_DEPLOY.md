# Windows 侧部署说明（先打通链路）

目标：让 WSL 中的 Agent 可以稳定调用 Windows 上的 Visio COM。

## 1) 你需要在 Windows 做的事

### 1. 安装依赖
- Microsoft Visio（Standard/Professional）
- Python 3.11+（建议 3.12）

### 2. 拷贝项目代码到 Windows（或直接 git clone）
建议路径：
`<repo-root>`（例如 `D:\work\DiagForge`）

### 3. 创建 venv 并安装 bridge 依赖
在 PowerShell：

```powershell
cd <repo-root>\agent\skills\visioskills\bridge_server
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. 设置鉴权 token（示例）
```powershell
$env:VISIO_BRIDGE_TOKEN="replace-with-a-long-random-token"
```

### 5.（可选）设置导出目录（用于闭环截图）
```powershell
$env:VISIO_BRIDGE_EXPORT_DIR="<repo-root>\.runtime\bridge_exports"
```

这里的目录是 bridge 的内部暂存目录，不是最终交付目录。
最终给人看的预览图会进入 `OutputPreview/`，最终 `.vsdx` 会进入 `OutputVSDX/`。

### 6. 启动 Bridge
```powershell
uvicorn app:app --host 0.0.0.0 --port 18761
```

> 如果你只想本机访问，可以把 host 改成 `127.0.0.1`。

## 2) 在 WSL 侧验证（我来做）

我会按顺序验证：
1. `GET /health`
2. `POST /ping_visio`
3. `POST /session/create`
4. `POST /shape/add`（先画框）
5. `POST /shape/update_geometry`（定位 + 调整大小）
6. `POST /shape/connect`（连线）
7. `POST /shape/set_text_style` + `/shape/set_colors`（字体与颜色）

## 3) 防火墙建议
如果 WSL 访问失败，先临时放行 18761 入站（Private Profile）。
后续收敛为：
- 固定源地址（WSL 子网）
- 仅允许内网/本机

## 4) 常见报错

### `Missing Bearer token`
请求没带 `Authorization: Bearer <token>`。

### `COM initialization failed`
通常是 pywin32 或 Visio 环境异常，重新安装 pywin32 并确认 Visio 能手动打开。

### `No open Visio document bound to session`
session 失效，重新 `session/create`。

## 5) 当前已支持的基础能力
- 选图形：`/shape/select`
- 定位位置与尺寸：`/shape/update_geometry`
- 连线：`/shape/connect`
- 文本与字体颜色：`/shape/set_text_style`
- 线条/填充颜色与线宽：`/shape/set_colors`
- 导出当前页 PNG：`/session/export_png`
- 受限一次性下载：`/artifact/download/{ticket}`

---

当你在 Windows 启动好 bridge 后，直接把以下信息发我：
1. Windows 主机地址（WSL 可达）
2. 端口（默认 18761）
3. token（可临时测试 token）

我就立刻从 WSL 侧连通并跑完整操作链路测试。
