# demo

这个目录现在只保留“如何演示系统”的脚本。

## 保留内容

- `draw_vortexnet_arch.py`
- `draw_vortexnet_closed_loop_3rounds.py`

## 不纳入版本库的内容

- 运行脚本后生成的 `.vsdx`
- 导出的 PNG
- 调试临时文件

这些产物现在已经由仓库根目录的 `.gitignore` 忽略。

如果后面需要展示效果，建议单独维护一份精选的 `showcase/` 或在 README 中引用导出图，而不是把每次运行产物都提交到仓库。
