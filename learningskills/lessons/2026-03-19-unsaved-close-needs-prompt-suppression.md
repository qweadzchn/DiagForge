# Unsaved Close Needs Prompt Suppression

## Trigger

预览已经成功导出，但 `session/close` 很慢、超时，随后 `ping_visio` 也开始卡住或报错。

## Problem

任务主体已经画完，但 bridge 的 COM worker 会在收尾阶段被拖死，导致下一轮无法稳定开始。

## Root Cause

未保存的 scratch 文档在 `save=False` 时直接 `doc.Close()`，Visio 仍可能等待交互式保存确认，从而阻塞 COM worker。

## Reusable Fix

关闭未保存文档时：

1. 先把 `doc.Saved` 设为 `True`
2. 再执行 `doc.Close()`
3. 如果 bridge 已经进入坏状态，重启 bridge 和 `VISIO.EXE`

## Where It Belongs

`visioskills`

## Example

第 2 轮导出 `round-02.png` 已经成功，但 close 阶段持续超时；在 adapter 里对 `save=False` 增加 `doc.Saved = True` 后，第 3 轮可以正常保存并关闭。
