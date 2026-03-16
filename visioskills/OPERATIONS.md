# visioskills 原子操作清单（v0.1）

> 原则：一个 API 只做一件可验证的小动作，便于组合、测试、回归与维护。

## 会话类

- `POST /session/create`
  - 创建/打开会话文档
- `POST /session/save`
  - 保存会话文档（支持 save_path）
- `POST /session/close`
  - 关闭会话

## 图形类

- `POST /shape/add`
  - 添加图形（Rectangle/Circle/Line，其他类型当前回退为 Rectangle）
- `POST /shape/select`
  - 选中图形
- `POST /shape/update_geometry`
  - 改坐标与尺寸（PinX/PinY/Width/Height）
- `POST /shape/connect`
  - 连线（支持常见 2D 形状，已加 1D fallback）

## 样式类

- `POST /shape/set_text_style`
  - 设置文本、字体、字号、文字颜色
- `POST /shape/set_text_block`
  - 设置文本块位置/尺寸（TxtPinX/TxtPinY/TxtWidth/TxtHeight）
- `POST /shape/set_colors`
  - 设置线条颜色、填充颜色、线宽

## 鉴权与幂等

- 鉴权：`Authorization: Bearer <token>`
- 幂等：写操作需要 `request_id`

## 设计建议（你提的方案）

是的，**“每个成功验证的能力都沉淀成原子操作”** 是正确的。
建议保持：

1. `visioskills/` 放原子 API（执行稳定性优先）
2. `drawskills/` 放组合技能模板（语义与审美）
3. `visioskills/OPERATIONS.md` 维护操作清单与状态（已测/待测/已弃用）

这样非常利于长期维护与版本演进。
