# Text Orientation Requires Layout Reflow

## Trigger

某些窄高模块为了容纳文字改成竖排或旋转标签后，原本的宽高和间距假设不再成立。

## Problem

如果只改文字朝向，不重算框和邻近距离，就容易出现视觉碰撞或阅读困难。

## Root Cause

文字方向决定了有效占用空间，也影响读者的扫描路径。

## Reusable Fix

一旦文字方向变化：

1. 重算框宽高
2. 重算同 row / 同 column 的最小间距
3. 重新检查相邻 connector 是否压字

## Where It Belongs

`drawskills`

## Example

狭长模块用竖排文字替代横排后，框宽可减小，但高度和上下间距通常需要放大。
