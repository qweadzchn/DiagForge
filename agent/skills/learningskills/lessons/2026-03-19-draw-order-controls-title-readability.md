# Draw Order Controls Title Readability

## Trigger

虚线容器和标题标签都画出来了，但标题被边框压住、切断，或者看起来像少字。

## Problem

标题内容本身没错，位置也差不多对，但导出预览后标题可读性明显变差。

## Root Cause

当系统还没有显式 z-order 能力时，图元创建顺序本身就是有效的“层级”。如果先画标题、后画容器，容器边框会盖到标题上。

## Reusable Fix

默认规则改成：

1. 先画容器
2. 再画标题
3. 再画容器内部节点
4. round review 必须检查标题是否被边框压住

## Where It Belongs

`drawskills`

## Example

Model / Backbone / CBS 这些标题如果先于虚线容器创建，导出后很容易出现边框压字；把容器移到前面画，标题可读性会立刻改善。
