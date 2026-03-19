# Export Before Polish

## Trigger

在 Visio 里看着差不多，但导出 PNG 后发现字体拥挤、间距不均、连接线交叉更明显。

## Problem

只在编辑态观察，很容易高估图的清晰度；真正交付时的问题通常在导出预览后才暴露。

## Root Cause

编辑态的缩放、选择框和页面上下文会掩盖真实视觉密度，agent 也容易过早结束。

## Reusable Fix

在完成骨架、连接线和样式后，先执行一次 `export_png`，再决定是否进入最终 polish。

## Where It Belongs

`drawskills`

## Example

复杂 pipeline 图在 Visio 编辑界面里看起来对齐正常，但 PNG 预览会更快暴露“同一行字重不一致”和“竖向间距漂移”。
