# WSL 侧烟雾测试（连通 + 画图）

把 `HOST` 和 `TOKEN` 改成你的值：

```bash
HOST="http://<windows-host>:18761"
TOKEN="replace-with-token"

curl -s "$HOST/health"

curl -s -X POST "$HOST/ping_visio" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{}'

SESSION_JSON=$(curl -s -X POST "$HOST/session/create" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"request_id":"req-create-1","visible":true}')

echo "$SESSION_JSON"
SESSION_ID=$(echo "$SESSION_JSON" | sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p')

echo "SESSION_ID=$SESSION_ID"

BOX1=$(curl -s -X POST "$HOST/shape/add" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-add-1\",\"session_id\":\"$SESSION_ID\",\"shape_type\":\"Rectangle\",\"x\":2.5,\"y\":4.0,\"width\":2.2,\"height\":1.0,\"text\":\"Input\"}")

echo "$BOX1"
ID1=$(echo "$BOX1" | sed -n 's/.*"shape_id":\([0-9]*\).*/\1/p')

BOX2=$(curl -s -X POST "$HOST/shape/add" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-add-2\",\"session_id\":\"$SESSION_ID\",\"shape_type\":\"Rectangle\",\"x\":6.0,\"y\":4.0,\"width\":2.2,\"height\":1.0,\"text\":\"Output\"}")

echo "$BOX2"
ID2=$(echo "$BOX2" | sed -n 's/.*"shape_id":\([0-9]*\).*/\1/p')

# 调整位置/大小
curl -s -X POST "$HOST/shape/update_geometry" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-geom-1\",\"session_id\":\"$SESSION_ID\",\"shape_id\":$ID1,\"x\":2.7,\"y\":4.1,\"width\":2.3,\"height\":1.0}"

# 设置文本样式
curl -s -X POST "$HOST/shape/set_text_style" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-text-1\",\"session_id\":\"$SESSION_ID\",\"shape_id\":$ID1,\"font_name\":\"Calibri\",\"font_size_pt\":11,\"font_rgb\":[20,20,20]}"

# 设置线条/填充色
curl -s -X POST "$HOST/shape/set_colors" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-color-1\",\"session_id\":\"$SESSION_ID\",\"shape_id\":$ID1,\"line_rgb\":[31,31,31],\"fill_rgb\":[238,244,255],\"line_weight_pt\":1.0}"

# 连线
curl -s -X POST "$HOST/shape/connect" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-conn-1\",\"session_id\":\"$SESSION_ID\",\"from_shape_id\":$ID1,\"to_shape_id\":$ID2}"

# 保存
curl -s -X POST "$HOST/session/save" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-save-1\",\"session_id\":\"$SESSION_ID\"}"

# 导出当前页 PNG（闭环预览）
EXPORT_JSON=$(curl -s -X POST "$HOST/session/export_png" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"request_id\":\"req-export-1\",\"session_id\":\"$SESSION_ID\",\"file_name\":\"smoke_preview.png\"}")

echo "$EXPORT_JSON"
TICKET=$(echo "$EXPORT_JSON" | sed -n 's/.*"ticket":"\([^"]*\)".*/\1/p')

# 一次性下载（需带 token）
curl -s -L "$HOST/artifact/download/$TICKET" \
  -H "Authorization: Bearer $TOKEN" \
  -o ./smoke_preview.png
```

> `ticket` 是一次性短时效凭证（默认 5 分钟）。下载后会失效。
