---
name: leap-drawcall-diff
description: "用于对比两份 CODM DrawCallRecord JSON，定位 mesh、pass、shader、属性和渲染目标变化，默认忽略相机、VP 和阴影矩阵噪音。不用于 RenderDoc 抓帧分析、实时性能分析或单份 DrawCallRecord 的独立解读。"
---

# DrawCall 差异对比

DrawCallRecord JSON 由引擎 API `Graphics.StartDrawCallRecording(1)` 开始录制产生（`1` 表示录制 1 帧），录制结束后文件自动写入 `%USERPROFILE%\AppData\LocalLow\Tencent\Call-of-Duty\DrawCallRecords\DrawCallRecord_*.json`。

对比两个 `DrawCallRecord_*.json`，聚焦 **mesh 渲染差异**，默认忽略相机相关矩阵（VP/投影/阴影 WorldToShadow）噪音。脚本只用标准库，不引入依赖。

## 工作流

1. 确认两份文件路径（用户通常只给文件名，去 `DrawCallRecords\` 目录解析）。
2. 先运行 `--summary` 查看总量与 `eventType` 分布，再运行完整 diff。
3. 按输出分层解读：**pass 数量变化**（定位问题 pass）→ **移除/新增 mesh** → **变化 mesh 的属性差异**。`batchBreakCause` 变化常是 draw call 数量变化的根因，优先看。
4. 只对比 `eventType` 为 `Mesh` / `DynamicGeometry` 的记录；`ClearAll` / `GLDraw` / `ClearDepthStencil` 不参与。多 frame 时平铺聚合。
5. 需要对比相机/阴影矩阵时加 `--include-camera` / `--include-shadow`；需要全量机读结果时用 `--json`。

mesh 渲染身份键 = `(eventName, meshName, shaderName, meshSubset, shaderPassIndex)`。同一 mesh 拆成多个 draw 会各自成组对比。

属性对比基于序列化文本，浮点打印格式差异（`1.000000` vs `1.0`）可能误报，判断时留意数值是否实际相等。

## 命令

脚本入口：`<skill-dir>\scripts\drawcall_diff.py`。

```powershell
# 摘要
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --summary

# 完整 diff
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>"

# 范围过滤（子串匹配）
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --pass "OpaqueGeometry"
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --mesh "CXB_Screen_06"

# 机器可读 JSON
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --json
```

显示控制：`--top 50`（报告最多 mesh 条目数）、`--detail 20`（每个 mesh 最多属性变化条数）。

## 忽略规则

默认忽略相机/VP/阴影矩阵属性（完整 key 列表见 [references/data-format.md](references/data-format.md)）。`--include-camera` 放开相机/VP，`--include-shadow` 放开阴影矩阵（不随 `--include-camera` 自动放开）。
