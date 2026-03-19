# Setup Workspace

这个目录是“单次画图任务”的入口。

目标是把一次绘图任务标准化成：

1. 把参考图放进 `InputPNG/`
2. 改一个本地配置文件
3. 让 agent 或脚本按配置执行闭环绘图
4. 预览结果放到 `OutputPreview/`
5. 最终 `.vsdx` 放到 `OutputVSDX/`

## 推荐目录约定

- `../InputPNG/`
  - 输入参考图
- `../OutputPreview/`
  - 每轮 PNG 预览
- `../OutputVSDX/`
  - 最终 `.vsdx`

## 你平时怎么用

1. 把要临摹的 PNG 放进 `InputPNG/`
2. 复制 `draw-job.template.json` 为 `draw-job.local.json`
3. 在 `draw-job.local.json` 里改：
   - `job_name`
   - `task.input_png`
   - `task.final_vsdx_name`
   - `execution.max_rounds`
4. 在启动 bridge 的同一个 shell 里设置：
   - `VISIO_BRIDGE_TOKEN`
   - 如有需要，`VISIO_BRIDGE_BASE`
5. 运行：

```powershell
python Setup\run_draw_job.py --config Setup\draw-job.local.json
```

这个预检会在以下情况直接失败退出：

- 输入 PNG 不存在
- bridge 的 `health` 不通
- `ping_visio` 因 token 或 Visio 运行态失败

6. 然后告诉 agent：
   - “按 `Setup/draw-job.local.json` 画”
   - 或者直接把输入图片发到聊天里

## 默认执行策略

- 不保存中间 `.vsdx`
- 每轮导出 PNG 预览
- 每轮结束后清理 session
- 每轮总结可复用经验
- 达到满意结果或轮次上限后结束
- 默认保留最终 `.vsdx`

## 为什么不把这些设置写进 DrawDSL

因为这些是“任务执行设置”，不是“图结构描述”。

- DrawDSL 负责“画什么”
- `Setup/job.schema.json` 负责“这次怎么跑”

这样边界更清楚，后面更容易维护。
