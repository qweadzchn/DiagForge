# Connect After Alignment

## Trigger

画到一半就开始连线，后面一旦挪动模块，connector 数量一多就难以维护。

## Problem

连接线过早介入，会把本来简单的布局调整放大成整图混乱。

## Root Cause

布局和连接是两个阶段的问题；先混在一起处理，会让视觉噪声和修改成本同时升高。

## Reusable Fix

默认顺序改成：先放 shape，再对齐/分布，再连主链路，最后补细连接和样式。

## Where It Belongs

`drawskills`

## Example

网络结构图的 backbone 和 neck 节点在还没统一 row spacing 时就连线，通常会导致 connector crossing 和局部拥挤。
