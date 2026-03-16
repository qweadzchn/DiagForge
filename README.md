# png2vsdx

阶段一目标：打通 `WSL Agent -> Windows Bridge -> Visio COM` 链路，并先实现基础可用操作能力。

## 当前已落地内容

- `visioskills/bridge_server/`
  - FastAPI Bridge（Windows 运行）
  - 单线程 COM 执行队列（STA）
  - 基础接口：创建会话、加图形、选中、定位/调大小、连线、字体/颜色、保存、关闭
  - Bearer Token 鉴权（可选）
  - request_id 幂等缓存（基础版）

- `visioskills/client/`
  - WSL 侧 Python HTTP 客户端

- `drawskills/schemas/`
  - DrawDSL JSON Schema（v0.1）

- `drawskills/examples/`
  - `two_boxes_arrow.yaml` 示例（两个方框 + 箭头）

- `docs/setup/`
  - Windows 部署说明
  - WSL 烟雾测试脚本

## 目录

```text
visioskills/
  bridge_server/
  client/

drawskills/
  schemas/
  examples/

docs/
  research/
  setup/
```

## 下一步（需要 Windows 环境）

1. 在 Windows 启动 bridge（见 `docs/setup/WINDOWS_BRIDGE_DEPLOY.md`）
2. 从 WSL 跑连通 + 画图烟雾测试（见 `docs/setup/SMOKE_TEST_FROM_WSL.md`）
3. 根据实测日志修正：错误码、重试策略、会话恢复
