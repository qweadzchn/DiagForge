# visioskills 原子操作清单（v0.2）

原则：一个 API 只做一件可验证的小动作，优先保证执行稳定性、可组合性和可回放性。

## 当前稳定能力

### 会话类

- `POST /session/create`
  - 创建或打开会话文档
- `POST /session/save`
  - 保存会话文档，支持显式 `save_path`
- `POST /session/close`
  - 关闭会话

### 图形类

- `POST /shape/add`
  - 添加图形
  - 当前稳定支持：`Rectangle`、`Circle`、`Line`
- `POST /shape/select`
  - 选中图形
- `POST /shape/update_geometry`
  - 更新位置与尺寸
- `POST /shape/align`
  - 对齐多个图形
- `POST /shape/distribute`
  - 分布多个图形
- `POST /shape/connect`
  - 添加 connector 并 glue 到两个 shape

### 样式类

- `POST /shape/set_text_style`
  - 设置文本、字体、字号、文字颜色
- `POST /shape/set_text_block`
  - 调整文本块位置与尺寸
- `POST /shape/set_colors`
  - 设置线条颜色、填充颜色、线宽

### 预览与闭环

- `POST /session/export_png`
  - 导出当前页 PNG，供 agent 做闭环预览
- `GET /artifact/download/{ticket}`
  - 使用一次性 ticket 下载导出产物

## 操作约束

### 鉴权

- 使用 `Authorization: Bearer <token>`

### 幂等

- 所有写操作都必须带 `request_id`
- 重试时保持相同 `request_id`

### 定位

- 优先使用显式 `session_id / shape_id / page_name`
- 不依赖隐式 UI 状态

## visioskills 的职责边界

`visioskills` 只负责“怎么稳定做动作”，不负责：

- 高层图语义规划
- 审美判断
- 经验沉淀

这些分别属于 `drawskills` 和 `learningskills`。

## 当前关键缺口

为了让 agent 更像人一样使用 Visio，`visioskills` 还需要继续补这几类读回能力：

1. 页面读回
   - 列出 page、页面尺寸、当前页边界
2. 图形读回
   - 列出 shape、name、geometry、style、text
3. 关系读回
   - 谁连着谁、connector 属于哪一层
4. 高级编辑
   - duplicate、group、ungroup、delete、z-order、arrowhead、line routing

没有这些读回能力，agent 虽然“能画”，但还不够“能看自己画了什么”。

## 推荐使用顺序

1. `health`
2. `ping_visio`
3. `session/create`
4. 一批 `shape/add`
5. `shape/update_geometry` / `align` / `distribute`
6. `shape/connect`
7. `shape/set_text_style` / `set_text_block` / `set_colors`
8. `session/export_png`
9. `session/save`

## 维护原则

每增加一个操作，都要问这 3 个问题：

1. 它是不是足够原子？
2. 它能不能幂等、回放、定位问题？
3. 它应该属于 `visioskills`，还是其实属于 `drawskills`？
