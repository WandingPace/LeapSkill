# Configuration

## Case files

Cases live in:

```text
G:\UnitySource\Tests\RenderValidation\Cases
```

Default case:

```text
material-mesh-setpass
```

Core API fields:

```json
{
  "graphicsApi": "d3d11",
  "graphicsApis": ["d3d11", "vulkan", "gles"]
}
```

- `graphicsApi`: default API for `run`.
- `graphicsApis`: ordered list for `matrix`.
- `gles` maps to `OpenGLES3` and `-force-gles`.

Do not add baseline paths or canonical image gates. Matrix results compare variants produced by the same run.

## Scene requirements

Generated scenes are produced by `RenderValidationBuild.cs`. A custom scene must:

- live under `Tests/RenderValidation/Project/Assets`;
- be referenced by a Case JSON project-relative path;
- have zero or one `IRenderValidationScene`; generated scenes can use the runtime fallback;
- become deterministic in `EnterStableState`;
- avoid random, asynchronous, or time-dependent changes during capture.

## Switch parameters

`matrix` and `compare` accept a public or non-public static property/field through reflection:

- `SwitchType`: full C# type name, for example `UnityEngine.Graphics`.
- `SwitchMember`: property or field name.
- `BeforeValue` / `AfterValue`: `bool`, `int`, `float`, `string`, or enum text.

Prefer switches that do not alter rendering loop shape when the goal is workflow validation. The validated smoke switch is:

```text
UnityEngine.Graphics.enableRenderThreadEarlySync=false|true
```

## Output contract

Each variant directory should contain:

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

`matrix-report.html` must contain one independent slider per API and data formatted as:

```text
Before | After
```

The HTML report must not contain unresolved `{{TOKEN}}` placeholders.
