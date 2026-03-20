# Text Size Box Gap Coupling

## Trigger

图里把字号调大后，文字虽然更清楚了，但开始压边、挤到邻近框，或者让整行失衡。

## Problem

把字体、框尺寸和间距当成三个独立旋钮去调，最终会造成图面越来越乱。

## Root Cause

在可读性图里，字号、框尺寸、padding 和相邻间距本来就是联动约束，不是独立参数。

## Reusable Fix

默认规则改成：

1. 先定字体层级
2. 再按文字内容增长框尺寸
3. 再按框尺寸增长相邻间距
4. 最后才考虑是否需要缩字

## Where It Belongs

`drawskills`

## Example

主模块标题从 12 pt 提升到 15 pt 后，不仅框需要变高，整列垂直间距也要一起上调，否则会压到下方节点。
