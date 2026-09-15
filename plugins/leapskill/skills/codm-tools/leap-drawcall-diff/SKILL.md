---
name: leap-drawcall-diff
description: Compare two CODM DrawCallRecord JSON captures (under %USERPROFILE%\AppData\LocalLow\Tencent\Call-of-Duty\DrawCallRecords\DrawCallRecord_*.json) and report mesh rendering differences. Ignores camera/VP-projection related matrix properties by default. Use when the user wants to diff two DrawCallRecord exports to find which meshes, passes, shaders, properties, or render targets changed between frames/builds.
---

# DrawCall Diff

对比两个 `DrawCallRecord_*.json`，聚焦 **mesh 渲染差异**，默认忽略相机相关矩阵（VP/投影/阴影 WorldToShadow）噪音。脚本只用标准库，不引入依赖。

## 数据结构（确认过）

每个 JSON 形如：

```json
{
  "exportTime": "...", "totalFrames": 1, "totalDrawCalls": N,
  "frames": [ { "frameIndex": int, "drawCallCount": N, "drawCalls": [ ... ] } ]
}
```

每个 draw call 关键字段：`eventType`（`Mesh` / `DynamicGeometry` / `ClearAll` / `GLDraw` / `ClearDepthStencil` …）、`eventName`（pass 路径）、`meshName`、`rendererName`、`shaderName`、`shaderKeywords`、`batchBreakCause`、`vertexCount`、`indexCount`、`triangleCount`、`instanceCount`、`meshSubset`、`shaderPassIndex`，以及四个属性表 `floatProperties` / `vectorProperties` / `matrixProperties` / `textureProperties`，外加 `colorRenderTargets` / `depthRenderTarget`。

## Workflow

1. 确认两份文件路径（用户通常只给文件名，去 `C:\Users\<user>\AppData\LocalLow\Tencent\Call-of-Duty\DrawCallRecords\` 下解析，或问用户）。
2. 先跑 `--summary` 看两份文件的 draw call / mesh 事件 / 三角形总量与 eventType 分布。
3. 再跑完整 diff，按输出分层解读：pass 数量变化 → 移除/新增 mesh → 变化 mesh 的标量与属性差异。
4. 默认已忽略相机相关属性（见下），若需要对比相机/阴影矩阵再显式加 `--include-camera` / `--include-shadow`。
5. 需要全量可机读结果时用 `--json`。

## 命令

脚本入口：`<skill-dir>\scripts\drawcall_diff.py`。

摘要：

```powershell
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --summary
```

完整 diff：

```powershell
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>"
```

范围过滤（只对比某个 pass 或某个 mesh，均子串匹配）：

```powershell
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --pass "OpaqueGeometry"
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --mesh "CXB_Screen_06"
```

机器可读 JSON（管道给后续分析）：

```powershell
python "<skill-dir>\scripts\drawcall_diff.py" "<A.json>" "<B.json>" --json
```

显示控制：`--top 50`（报告最多 mesh 条目数）、`--detail 20`（每个 mesh 最多属性变化条数）。

## 忽略规则（默认）

下列属性 key（子串匹配，不区分大小写）默认不参与对比：

- VP/V/P 矩阵：`unity_MatrixVP`、`unity_MatrixV`、`unity_MatrixP`、`unity_MatrixInvV`、`unity_MatrixInvP`、`unity_MatrixMVP`
- 投影/模型视图：`glstate_matrix_projection`、`glstate_matrix_modelview0`、`glstate_matrix_inv_trans_modelview0`、`glstate_matrix_transpose_modelview0`
- 相机参数：`_WorldSpaceCameraPos`、`unity_OrthoParams`、`unity_FrustumPlanes`、`CameraProjection`、`CameraWorldClipPlanes`、`Stereo*`
- 阴影 VP（默认也忽略，视为相机相关）：`*WorldToShadow*`（含 `_AdditionalLightsWorldToShadow0`）

放开控制：

- `--include-camera`：也对比相机/VP 相关属性。
- `--include-shadow`：也对比阴影 `WorldToShadow` 矩阵（不加此参数时即使 `--include-camera` 也仍忽略阴影矩阵）。

## 输出解读

- `按 pass 的 draw call 数量变化`：某 pass 下 mesh 事件总数的增减，先看这里定位到哪个 pass 出问题。
- `被移除的 mesh`：B 中完全消失的 `(pass, mesh, shader, subset, passIndex)` 组合，按三角形量降序。
- `新增的 mesh`：B 中全新出现的组合，同样按三角形量降序。
- `变化的 mesh`：两边都有的组合，报告 `draws` / `tris` 数量变化、`renderer` 变化、标量字段变化（shaderKeywords / batchBreakCause / vertex/index/triangle/instance 等），以及属性表变化（float/vector/matrix/texture 与 render target 签名）。

mesh 渲染身份键 = `(eventName, meshName, shaderName, meshSubset, shaderPassIndex)`。同一 mesh 被拆成多个 draw（不同 subset/pass）会各自成组对比。

## 注意事项

- 只对比 `eventType` 为 `Mesh` / `DynamicGeometry` 的记录；`ClearAll` / `GLDraw` / `ClearDepthStencil` 不参与。
- 多个 frame 时会把所有 frame 的 draw call 平铺后按身份键聚合；如需限定帧，先用 `--summary` 确认 frameIndex 再另行处理。
- `batchBreakCause` 变化（如 `DynamicBatchingDisabled` ↔ `DifferentShaderCasterHashes`）常是 draw call 数量变化的根因，优先看。
- 属性对比用的是序列化后的规范文本，浮点打印格式差异（如 `1.000000` vs `1.0`）可能造成误报，判断时留意数值实际是否相等。
