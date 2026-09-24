---
name: leap-rdc-debug-diff
description: "用于对比两份 RenderDoc .rdc 抓帧中同一 draw 的 VS/PS 常量缓冲区，区分 draw 专属差异与帧全局差异，并定位可能影响画面的变量。不替代完整抓帧分析、shader 调试或普通离线 .rdc 浏览。"
---

# RenderDoc 常量缓冲区差异对比

对比两个 `.rdc` 抓帧在同一 draw 上的 cbuffer（常量缓冲）数值差异，并区分「该 draw 专属差异」与「帧全局差异」。驱动 `renderdoc-mcp`（stdio MCP server），全部脚本只用 Python 标准库。

## 前置条件

- MCP server 二进制：`I:\GitHubProject\renderdoc\renderdoc-mcp-cpp\bin\renderdoc-mcp.exe`
  - 若 `bin\` 下版本旧或缺失，可用 `build\Release\` 下较新构建（需确认含 `renderdoc.dll`）。
- 该 server 走**单行 JSON over stdio**（非 Content-Length 帧），见 `scripts\rdc_mcp.py` 驱动实现。
- Python：任意 3.x（脚本只用 stdlib，无需 `renderdoc` 模块）。

> 注意：本 skill **不依赖** renderdoc-mcp 的 MCP 工具暴露在会话里；即使会话没有注册该 MCP server，也可以直接用脚本驱动 stdio 协议。

## 脚本清单

全部在 `<skill-dir>\scripts\`：

| 脚本 | 用途 |
|------|------|
| `rdc_mcp.py` | MCPClient 驱动（initialize → tools/call → shutdown），其它脚本依赖它 |
| `rdc_cbuffer_diff.py` | **主入口**：跨两个 capture、同一 EID 对，diff VS/PS 各 cbuffer 变量 |
| `rdc_samecap_diff.py` | 同一 capture 内两个 EID 的 cbuffer 对比（判断 per-draw vs per-frame）|
| `rdc_cb_vars.py` | 打印某 capture/EID/stage/cbuffer 的指定变量值 |
| `rdc_cb_usage.py` | 从 shader disasm 提取真正被读取的 cbuffer register（排除未用变量噪音）|
| `rdc_shader2.py` | 取某 EID 的 VS/PS shader disassembly（验证两张图是否同一 shader）|
| `rdc_shader_groups.py` | 统计某 capture 内按 shader 分组的 draw 分布 |
| `rdc_find_shader_draws.py` | 在两张 capture 里找出用某 shader 的所有 draw |
| `rdc_export_rt.py` | 导出某 EID 的 render target（需先 goto_event）|

## 工作流

1. **确认两个 EID 是同一个 draw**：
   - 用 `rdc_shader2.py` 分别取两个 EID 的 VS disasm，比对 shader hash（如 `d787b666-...`）与 `ResourceId`。
   - 用 `rdc_shader_groups.py` / `rdc_find_shader_draws.py` 确认两者在同 pass、同 shader、相邻 draw（索引数模式一致，如 `...111→450→180→204`）。

2. **跑主 diff（跨 capture）**：
   ```powershell
   python "<skill-dir>\scripts\rdc_cbuffer_diff.py" "A.rdc" <eidA> "B.rdc" <eidB> --stage vs,ps --json "out.json"
   ```
   输出每个 stage 每个 cbuffer 里**数值不同**的变量（默认容差 `--tol 1e-4`）。

3. **判断差异是 draw 专属还是 frame 全局**（关键步骤）：
   - **同 capture 内**：`rdc_samecap_diff.py A.rdc <eidA> <eidA-5>` 看 cbuffer1/2/3 是否仍 identical。若同 capture 内这些 cbuffer 恒定 → 跨 capture 的差异属于 frame-global。
   - **换 shader 验证**：用不同 shader 的 draw（如 `rdc_find_shader_draws.py` 找另一 shader）做同样的跨 capture diff。若连不同 shader 都共享同一组差异（如 viewproj 矩阵槽位）→ 一定是 frame-global（相机/全局状态），与目标 EID 无关。

4. **过滤"未使用变量"**（stripped shader 常见）：
   - `rdc_cb_usage.py A.rdc <eidA> ps` 输出 PS 真正读取的 `cbN[reg]`。
   - 若某个 diff 变量对应的 register 不在使用列表里（如 `cb0_v221` 对应 `cb0[221]` 但 PS 不读），则该差异**不影响画面**，别报成根因。

5. **结合渲染结果**：需要时可 `rdc_export_rt.py` 导出两个 EID 的 MainRT，视觉对比（帧全局光照/曝光差异往往一眼可见）。

## 典型结论模板

```
- 同一 draw：shader hash 一致 (d787b666-... / 72adb07e-...)，索引数/顺序一致。
- 帧全局差异（所有同 shader draw 都有，非目标 EID 独有）：
  VS cbuffer1 cb1_v0 / cb1_v4  → 光源/时间参数
  VS cbuffer2 cb2_v13-v20      → view/projection 矩阵（相机）
  PS cbuffer3 cb3_v8-v15 / v24 → 光照/曝光参数
  PS cbuffer0 cb0_v221         → 未使用寄存器（不影响画面）
- draw 专属差异：cbuffer0 的 cb0_v10（UV 偏移），per-mesh。
```

## 注意事项

- `get_cbuffer_contents` 的变量名是 stripped 的（`cbN_vN`），需靠 register 使用 + 数值语义反推含义。
- 变量值键名是 `floatValues` / `intValues` / `uintValues`（**不是** CLI 打印用的 `values`），读 JSON 时注意。
- `export_render_target` 需先 `goto_event`（MCP server 语义），`rdc_export_rt.py` 已处理。
- 两个 capture 的 totalEvents/draws 可能不同（E=636/C=599），**不能靠 EID 对齐**，要用 shader + 索引模式对齐。
- 若 `bin\renderdoc-mcp.exe` 的 `get_cbuffer_contents` 返回空变量名但值在 `floatValues` 里，属正常（见上面键名提醒）。
