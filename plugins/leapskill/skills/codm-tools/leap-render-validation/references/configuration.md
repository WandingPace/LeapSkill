# 配置

## Case 文件

Case 位于：

```text
G:\UnitySource\Tests\RenderValidation\Cases
```

默认 Case：

```text
material-mesh-setpass
```

核心 API 字段：

```json
{
  "graphicsApi": "d3d11",
  "graphicsApis": ["d3d11", "vulkan", "gles"]
}
```

- `graphicsApi`：`run` 使用的默认 API。
- `graphicsApis`：`matrix` 使用的有序列表。
- `gles` 映射为 `OpenGLES3` 和 `-force-gles`。

不要添加基线路径或标准图像门禁。矩阵结果只比较同一次运行产生的变体。

## 场景要求

生成场景由 `RenderValidationBuild.cs` 产生。自定义场景必须满足：

- 位于 `Tests/RenderValidation/Project/Assets` 下；
- 由 Case JSON 中的项目相对路径引用；
- 包含零个或一个 `IRenderValidationScene`；生成场景可以使用运行时回退；
- 在 `EnterStableState` 中进入确定性状态；
- 抓帧期间避免随机、异步或依赖时间的变化。

## 开关参数

`matrix` 和 `compare` 通过反射接受 public 或 non-public 的静态属性或字段：

- `SwitchType`：完整 C# 类型名，例如 `UnityEngine.Graphics`。
- `SwitchMember`：属性或字段名。
- `BeforeValue` / `AfterValue`：`bool`、`int`、`float`、`string` 或枚举文本。

流程验证时优先选择不会改变渲染循环形态的开关。已验证的冒烟开关为：

```text
UnityEngine.Graphics.enableRenderThreadEarlySync=false|true
```

## 输出契约

每个变体目录应包含：

```text
capture.rdc
actual.png
editor-screenshot.png
unity-stats.json
assertions.json
result.xml
player.log
capture.log
```

`matrix-report.html` 必须为每个 API 提供一个独立滑块，并按以下格式展示数据：

```text
Before | After
```

HTML 报告不能包含未解析的 `{{TOKEN}}` 占位符。
