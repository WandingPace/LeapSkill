---
name: leap-unity-test-validation
description: "用于运行共享的 G:/UnitySource/Tests/TestValidation 测试框架，执行 Editor PlayMode 验证、按场景路由，并产出 result.json、report.html 和 CDB 证据。不用于引擎编译问题诊断、代码调用链定位或 RenderValidation 的多 API 渲染矩阵。"
---

# Unity Test Validation（Editor PlayMode 测试框架）

本 skill 说明如何使用该测试框架。在 `G:\UnitySource` 中做 TDD RED/GREEN 或计划验证时，先遵循 `superpowers:test-driven-development` 的 **Workspace Test Selection**（先编 Debug Editor，再运行本脚本）。不要在这里增加第二套测试入口。

## 飞行前检查：先选定工作区的 Unity.exe

**不要先跑命令。先确认当前工作区，再决定用哪个 `Unity.exe`。** 测试工程只有一份（固定在 `G:\UnitySource\Tests\TestValidation`，跨工作区共享），但被测引擎二进制**必须来自当前工作区那次成功的 Debug build**。用别的工作区/旧 build 会编译失败或结果失真。完整解析步骤见 [references/workspace-resolution.md](references/workspace-resolution.md)。

固定路径（不随工作区变）：

| 项 | 全路径 |
|---|---|
| 测试工程根 | `G:\UnitySource\Tests\TestValidation` |
| Runner 脚本 | `G:\UnitySource\Tests\TestValidation\Scripts\run-test-validation.ps1` |
| 默认报告根目录 | `G:\UnitySource\Tests\TestValidation\Report\TestValidation` |

随工作区变（每次确认）：Debug Editor 构建脚本 `<工作区根>\BuildWindowsEditor.Bee.Debug.bat` 与产物 `<工作区根>\build\WindowsEditor\Unity.exe`。用 `-EditorPath` 显式传给 runner（runner 默认按脚本位置解析到 `G:\UnitySource`，非该工作区时必须覆盖）。所有命令用绝对路径调用（`& G:\UnitySource\...\run-test-validation.ps1`），避免 `.\` 依赖。

## 场景流程路由

每场景的专属流程/断言/参数/已知坑放在 `references/scenes/<scene>.md`，按 `-CreateScene` / `-TestScene` 名路由。本 SKILL.md 只放公共 harness。新增场景时建同名 `<scene>.md`，别把场景细节堆进本文件。

| 场景 (-CreateScene) | 流程文件 |
|---|---|
| `twoCamShadow` | [references/scenes/two-cam-shadow.md](references/scenes/two-cam-shadow.md) |
| `srpBatcher` / `hism` / `hismBatch` / `addLightShadow` | 见下方「结果契约」「新增其他开关」公共契约（暂无专属文件，需要时按 two-cam-shadow.md 模板补） |

当前框架只实现了一个开关示例：`Graphics.enableSRPBatch`。SRP 只是示例，不是流程边界。后续开关测试应复用相同的测试阶段、结果契约、报告和 CDB 诊断。

## 必需步骤

与 TDD Workspace Test Selection 一样，必须执行两步。缺少 Debug Editor 构建的验证无效。不要使用 `perl build.pl test native`、`-runNativeTests`、`BuildWindowsEditor.Bee.bat`、`perl bee.pl EditorApp`、`WindowsStandaloneSupport` 或 `render-validation`。

```powershell
# 1. 先编 Debug Editor（产物 G:\UnitySource\build\WindowsEditor\Unity.exe）
G:\UnitySource\BuildWindowsEditor.Bee.Debug.bat

# 2. 再跑 Editor PlayMode（绝对路径调用，任何工作目录都可用）。Debug Editor 构建后的每次验证默认都加 CDB：
& G:\UnitySource\Tests\TestValidation\Scripts\run-test-validation.ps1 `
  -Mode EditorPlay `
  -CreateScene srpBatcher `
  -Frames 120 `
  -SrpBatch:$false `
  -Debugger Cdb `
  -TimeoutSeconds 300
```

通过条件：Debug Editor 退出码 0；`result.json` 的 `passed=true`；requested/actual 开关一致；完成 sentinel 存在；`report.html` 已生成。`report.html` 单独不能当 PASS。崩溃以 `cdb.log` 的异常码和 Unity 栈为准。

加载已有场景时，第二步把 `-CreateScene` 换成 `-TestScene`，第一步仍然要先编 Debug Editor：

```powershell
G:\UnitySource\BuildWindowsEditor.Bee.Debug.bat

& G:\UnitySource\Tests\TestValidation\Scripts\run-test-validation.ps1 `
  -Mode EditorPlay `
  -TestScene Assets/test.unity `
  -Frames 3 `
  -SrpBatch:$false `
  -Debugger Cdb
```

参数：

- `-CreateScene <hism|hismBatch|srpBatcher>`：生成验证场景。
- `-TestScene Assets/<scene>.unity`：加载已有场景；与 `-CreateScene` 互斥。
- `-SrpBatch:$false|$true`：请求当前示例开关 `Graphics.enableSRPBatch`。
- `-Debugger Cdb`：在 Windows CDB 下启动 Unity 并捕获原生异常。本仓库的所有 EditorPlay 运行都必须带上该参数；每次运行都要先做一次新的 Debug Editor 构建，即使预期结果是 PASS，也必须保留原生崩溃证据。
- `-OutputDirectory` 和 `-ReportDirectory`：覆盖默认的证据和报告目录。

除非用户明确要求，否则不要使用 `-Mode Player`。默认流程是在 Debug Editor 构建后运行 EditorPlay。

## 新增其他开关

新增图形或逻辑开关时，遵循相同契约：

1. 为新开关增加明确的脚本参数，不要复用并改变已有开关的含义。
2. 通过 Unity 命令行参数传给 `TestValidationRunner`。
3. 在进入 PlayMode 前立即应用开关，并在进入 PlayMode 后确认实际值等于请求值。
4. 在 `result.json` 中记录请求值和实际值。
5. 在 HTML 报告中同时展示两个值。
6. 场景专属断言不得依赖开关状态。
7. 始终使用 `-Debugger Cdb` 启动，不要再建立一套独立调试流程。
8. 只有请求状态与实际状态一致，并且运行到达完成 sentinel 时，才能把开关报告为已验证。

不要把新开关硬编码为默认值。在新路径通过验证前，默认值保持 `None` 或当前安全基线。

## 参数调整脚本约定

当测试需要调整引擎相关参数时，按作用范围分两种挂载方式，不要在 `TestValidationRunner` 里散落硬编码：

- **组件级参数**：只影响某个对象/组件的参数，新建一个 MonoBehaviour 测试脚本（如 `<ParamName>TestSetting.cs`），挂在对应的 GameObject/组件下，在 `Awake`/`Start` 里读取参数值（来自命令行传入的 runner 配置）并应用到目标组件。参数与被测对象随场景一起序列化，断言时按该对象校验。
- **全局通用参数**：影响整个场景/全局管线状态的参数，统一挂到场景的主相机（Main Camera）下。相机是场景必然存在的根性对象，全局参数脚本挂在相机下可保证任何生成的或加载的场景都有唯一、可预期的挂载点。

两种脚本都遵守同样的契约：参数值通过 `TestValidationRunner` 的命令行参数传入，脚本内不写死默认值以外的业务值；`result.json` 同时记录 requested 与 actual；脚本只在测试场景内存在，不要打进业务工程。

## 输出目录

生成场景的输出目录（测试工程内的绝对路径）：

```text
G:\UnitySource\Tests\TestValidation\Report\TestValidation\Generated-<scene-kind>\<timestamp>\
```

加载已有场景的输出目录：

```text
G:\UnitySource\Tests\TestValidation\Report\TestValidation\Scene-<relative-name-without-extension>\<timestamp>\
```

示例：`-TestScene Assets/test.unity` 会写入 `Scene-test` 下的目录。

每次运行的目录包含：

- `result.json`
- 渲染执行到截图阶段时的 `screenshot.png`
- `capture.rdc`（RenderDoc 多帧抓帧，在 Unity 退出时写入；会复制到 `report.html` 同级目录，并从报告的证据列表链接）
- `editor.log`
- Player 模式下的 `unity.log`
- CDB 模式下的 `cdb.log`
- `report.html`

## 验证流程

1. 使用 `G:\UnitySource\BuildWindowsEditor.Bee.Debug.bat` 构建 Debug Editor，然后确认 `G:\UnitySource\build\WindowsEditor\Unity.exe` 和测试工程 `G:\UnitySource\Tests\TestValidation` 可用。
2. 生成或加载请求的场景。
3. 应用请求的测试设置。当前示例应用 `Graphics.enableSRPBatch`。
4. 在 EditorPlay 模式下，以批处理方式启动 Unity，但不传 `-quit`；运行 `TestValidationRunner.RunEditor` 并进入 PlayMode。
5. 状态依次经过 `entering-play-mode`、`waiting-for-scene`、`running`、`waiting-for-screenshot` 和 `complete`。
6. 达到请求帧数后，显示 `UnityEditor.GameView`，调用其私有方法 `RepaintImmediately()`，读取 `UnityEditor.UnityStats`，再渲染到临时 `RenderTexture` 并捕获后台缓冲区。
7. 写入 `result.json`、`screenshot.png`，并向 Editor 日志写入完成 sentinel。
8. PowerShell 脚本校验结果是否为通过、请求开关值与实际值是否一致、产物是否存在，以及完成 sentinel 是否存在。
9. 无论成功还是失败，包括进程崩溃和超时，都写入 `report.html`。

## 结果契约

可靠证据：

- `passed`
- 每个被测开关的请求值和实际值
- `validationMode`
- `requestedFrames` and `framesCompleted`
- `rendererCount`
- `foregroundPixelCount`
- `expectedColorPixelCount`
- 截图和 Editor 日志

Editor `UnityStats` 字段：

- `drawCalls`
- `batches`
- `setPassCalls`
- `triangles`
- `vertices`
- `renderTextureChanges`
- `shadowCasters`
- `frameTime`
- `renderTime`

仅当 `renderStatsAvailable` 为 true 时，这些统计值才有意义。如果核心计数器始终为 0，应报告为 `N/A`，不能把它当作实测零值。

生成的 SRP Batcher 示例场景包含 24 个共享材质立方体和 8 个独立材质球体。要求至少有 32 个 renderer，并且至少 2000 个预期蓝色或暖色像素。其他生成场景应定义自己的场景专属契约。任意加载的场景只使用通用健康检查。

## HTML 报告

`report.html` 是主要的人类可读结果，包含：

- PASS/FAIL 标记和进程退出码
- 场景、模式、开关请求值和实际值
- **Comparison Evidence** section（对比验证输出契约，见下文）
- 帧数和 renderer 数量
- 前景像素数和预期颜色像素数
- `UnityStats` 表格
- 截图预览
- 原始证据链接
- 失败原因
- Editor/Player 日志尾部
- 启用 CDB 时的 CDB 分析和 CDB 日志尾部

最终回复必须给出 HTML 路径。报告本身不是通过信号；成功运行还必须确认 `result.json`、sentinel 和产物。

如果当前工程任务使用 `status.md` 跟踪状态（例如位于 `Docs\superpowers\plans\...`），应在每次验证完成后把生成的报告和证据目录记录到该文件。每次运行使用一个可点击的绝对路径 Markdown 链接，优先直接链接 `report.html`（需要时链接 `cdb.log` 或 `result.json`），并附一行简短结果摘要。不要把反引号包裹的相对目录或裸 Windows 路径作为唯一表示。失败诊断应与对应运行目录放在一起。

## 对比验证输出契约

任何场景需要 A/B 对比验证（开关某投影体前后对比、好/坏帧对比、两个引擎静态开关对比等）时，统一走这个契约，报告会自动渲染，不需要每类测试改 report 模板：

1. `TestValidationRunner.cs` 在 `result.json` 的 `comparisons` 数组（`ComparisonEntry[]`）里为每条对比写一个条目：
   - `name`：对比项名称（如 `"WorldOccluder shadow -> 1P plate"`）
   - `metric`：被比较的指标（如 `"lit magenta pixels on plate"`）
   - `stateA` / `valueA`：A 态描述与数值；`stateB` / `valueB`：B 态
   - `screenshotA` / `screenshotB`：两态截图的绝对路径（可为空，为空则报告跳过该图）
   - `verdict`：`confirmed`（对比差异达标）/ `failed`（未达标）/ `info`（仅展示）
2. 引擎行为约束：同一帧内多次 `camera.Render()` 复用首帧 shadowmap，且运行时改 `cullingMask` 不影响已渲染帧——A/B 两态必须跨帧采集（改状态 → 等 ≥2 个正常帧 → 再渲染读数）。
3. PowerShell 报告把每条对比渲染为 Comparison Evidence 区块：数值表格一行（含 Delta B-A 与 verdict badge），A/B 截图（存在时）渲染为**滑窗对比组件**（同一视点两图叠放、拖动洋红分割线左右透视；截图自动复制到运行目录 `cmp-*.png` 保证相对链接可随目录移动）。
4. 对比差异的达标阈值由各场景自己的断言定义（如阴影探针 ≥100 像素）；`verdict=failed` 必须同时让场景断言失败，不能只改报告展示。
5. 滑窗对比的 A/B 两图必须同视点同分辨率才有透视意义；截图与数值必须来自同一次渲染（不要分开存图与读数，手动 `Render()` 可见性滞后一帧，分开采集会错位）。

## CDB 原生调试

本仓库的 EditorPlay 始终使用 `-Debugger Cdb`，不能只在失败后启用。成功运行也会写出不含异常的 `cdb.log`，用于证明原生进程未发生访问违规、栈溢出或除零。如果 CDB 不可用，应停止并报告 CDB 是必需条件，不能静默降低运行标准。

CDB 模式会执行：

1. 定位 Windows Debuggers 的 `cdb.exe`。
2. 将 Unity 作为被调试进程启动。
3. 加载行号信息和 Unity 符号。
4. 为访问违规、栈溢出和除零启用自动处理器。
5. 发生异常时运行 `!analyze -v`，切换到异常上下文，转储当前线程和所有线程栈，并记录 Unity 模块信息。
6. 写出 `cdb.log`，在采集证据后退出被调试进程，并在 `report.html` 中展示异常和已符号化的 Unity 调用栈。

不要只根据外层进程退出码推断根因。必须读取 `cdb.log`，报告实际原生异常和第一批有效的 Unity 栈帧，并保留原始 CDB 日志。

SRP ON 示例曾在 `Renderer::FlattenMaterialsAndCustomPropBuffers` 调用 `Renderer::EnsureMaterialCacheUpdated` 时产生原生栈溢出 `0xC00000FD`。不要把该结论复用为通用结论。每次新运行和每个新开关都必须根据本次运行的 CDB 证据得出结论。

## 结果解读

- Debug Editor 未编过或 `BuildWindowsEditor.Bee.Debug.bat` 失败时，不要跑 PlayMode，也不要用旧的 `Unity.exe` 冒充本次验证。
- 基线通过只证明测试框架能够创建或加载场景、进入 PlayMode、运行帧、渲染并截图，不证明每个开关都正常。
- 有 CDB 证据的开关失败，应从原生异常和调用栈诊断，不能当作测试框架缺陷。
- 缺少完成 sentinel、缺少 JSON、缺少截图或超时，说明本次运行没有完成。修改引擎代码前先检查 Editor 日志、状态文件和 CDB 日志。
- 出现 `Temp/UnityLockfile` 或“another Unity instance is running”说明工程正在别处打开。停止另一个 Editor 并移除锁文件后再重试。
- 测试框架正确检测到引擎缺陷时，不要为了绕过缺陷而修改框架。

## 报告自动打开（默认行为）

每次运行结束（无论 PASS/FAIL/超时，只要 `report.html` 已生成），PowerShell 脚本自动在默认浏览器打开 `report.html`，不需要额外参数或手动命令。Agent 的工作流相应约定：

1. 验证命令执行完后，报告已在浏览器弹出——最终回复里仍要给出 report.html 的可点击 Markdown 链接，但不重复调用 `Start-Process` 打开。
2. 若用户明确说"不要自动打开"，可传 `-NoOpenReport` 跳过。
3. 环境干扰（如 `Temp/UnityLockfile`）导致未生成报告时，脚本不会打开任何东西；按「结果解读」清理后重跑。

回复默认使用中文。除非用户要求清理，否则保留生成的诊断产物；永远不要提交 `Library/`、`Temp/`、`Report/`、`TestResults*/` 或生成的场景输出。
