# DrawCallRecord 数据格式

## JSON 结构

```json
{
  "exportTime": "...", "totalFrames": 1, "totalDrawCalls": N,
  "frames": [ { "frameIndex": int, "drawCallCount": N, "drawCalls": [ ... ] } ]
}
```

## Draw Call 关键字段

`eventType`（`Mesh` / `DynamicGeometry` / `ClearAll` / `GLDraw` / `ClearDepthStencil` …）、`eventName`（pass 路径）、`meshName`、`rendererName`、`shaderName`、`shaderKeywords`、`batchBreakCause`、`vertexCount`、`indexCount`、`triangleCount`、`instanceCount`、`meshSubset`、`shaderPassIndex`、四个属性表 `floatProperties` / `vectorProperties` / `matrixProperties` / `textureProperties`，外加 `colorRenderTargets` / `depthRenderTarget`。

## 默认忽略的属性 Key

子串匹配，不区分大小写：

- VP/V/P 矩阵：`unity_MatrixVP`、`unity_MatrixV`、`unity_MatrixP`、`unity_MatrixInvV`、`unity_MatrixInvP`、`unity_MatrixMVP`
- 投影/模型视图：`glstate_matrix_projection`、`glstate_matrix_modelview0`、`glstate_matrix_inv_trans_modelview0`、`glstate_matrix_transpose_modelview0`
- 相机参数：`_WorldSpaceCameraPos`、`unity_OrthoParams`、`unity_FrustumPlanes`、`CameraProjection`、`CameraWorldClipPlanes`、`Stereo*`
- 阴影 VP（视为相机相关）：`*WorldToShadow*`（含 `_AdditionalLightsWorldToShadow0`）
