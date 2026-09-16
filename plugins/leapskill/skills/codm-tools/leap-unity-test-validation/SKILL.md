---
name: leap-unity-test-validation
description: How-to for the shared G:/UnitySource/Tests/TestValidation harness (result.json, report.html, CDB). Covers workspace-aware Unity.exe selection, run/report flow, and per-scene routing. Do NOT use for engine build/compile diagnosis (use cgame-engine build-verify) or for locating engine call chains (use cgame-engine code-discovery); this skill runs the validation harness only.
---

# Unity Test Validation

This skill is the harness how-to. For TDD RED/GREEN and plan verification in `G:\UnitySource`, follow `superpowers:test-driven-development` **Workspace Test Selection** (Debug Editor, then this script). Do not add a second test entry here.

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
| `srpBatcher` / `hism` / `hismBatch` / `addLightShadow` | 见下方「Result Contract」「Adding Another Switch」公共契约（暂无专属文件，需要时按 two-cam-shadow.md 模板补） |

The current harness has one implemented switch example, `Graphics.enableSRPBatch`. Treat SRP as an example, not as the workflow boundary. Future switch tests should reuse the same phases, result contract, report, and CDB diagnostics.

## Required Sequence

Same two steps as TDD Workspace Test Selection. Missing the Debug build does not count. Do not use `perl build.pl test native`、`-runNativeTests`、`BuildWindowsEditor.Bee.bat`、`perl bee.pl EditorApp`、`WindowsStandaloneSupport`、`render-validation`。

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

Parameters:

- `-CreateScene <hism|hismBatch|srpBatcher>` generates a validation scene.
- `-TestScene Assets/<scene>.unity` loads an existing scene; it is mutually exclusive with `-CreateScene`.
- `-SrpBatch:$false|$true` requests the current example switch, `Graphics.enableSRPBatch`.
- `-Debugger Cdb` launches Unity under Windows CDB and captures native exceptions. Always include it for EditorPlay runs in this repository; each run follows a fresh Debug Editor build and must retain native-crash evidence even when the expected result is PASS.
- `-OutputDirectory` and `-ReportDirectory` override the default evidence/report locations.

Do not use `-Mode Player` unless the user explicitly asks. Default is EditorPlay after the Debug Editor build.

## Adding Another Switch

Follow the same contract when adding a new graphics/logic switch:

1. Give it explicit script parameters rather than overloading an existing switch's meaning.
2. Pass it through Unity command-line arguments to `TestValidationRunner`.
3. Apply it immediately before PlayMode and verify the actual value equals the requested value after entering PlayMode.
4. Store both requested and actual values in `result.json`.
5. Include both values in the HTML report.
6. Keep scene-specific assertions independent from switch state.
7. Always launch with `-Debugger Cdb`; do not create a separate debugger workflow.
8. Report a switch as validated only when both requested state and actual state match and the run reaches the completion sentinel.

Do not hard-code a new switch as the default. Keep `None` or the current safe baseline as the default until the new path is validated.

## 参数调整脚本约定

当测试需要调整引擎相关参数时，按作用范围分两种挂载方式，不要在 `TestValidationRunner` 里散落硬编码：

- **组件级参数**：只影响某个对象/组件的参数，新建一个 MonoBehaviour 测试脚本（如 `<ParamName>TestSetting.cs`），挂在对应的 GameObject/组件下，在 `Awake`/`Start` 里读取参数值（来自命令行传入的 runner 配置）并应用到目标组件。参数与被测对象随场景一起序列化，断言时按该对象校验。
- **全局通用参数**：影响整个场景/全局管线状态的参数，统一挂到场景的主相机（Main Camera）下。相机是场景必然存在的根性对象，全局参数脚本挂在相机下可保证任何生成的或加载的场景都有唯一、可预期的挂载点。

两种脚本都遵守同样的契约：参数值通过 `TestValidationRunner` 的命令行参数传入，脚本内不写死默认值以外的业务值；`result.json` 同时记录 requested 与 actual；脚本只在测试场景内存在，不要打进业务工程。

## Output Layout

Generated scenes write to（测试工程内的绝对路径）:

```text
G:\UnitySource\Tests\TestValidation\Report\TestValidation\Generated-<scene-kind>\<timestamp>\
```

Loaded scenes write to:

```text
G:\UnitySource\Tests\TestValidation\Report\TestValidation\Scene-<relative-name-without-extension>\<timestamp>\
```

Example: `-TestScene Assets/test.unity` writes under `Scene-test`.

Each run directory contains:

- `result.json`
- `screenshot.png` when rendering reaches capture
- `capture.rdc` (RenderDoc multi-frame capture, written at Unity exit; copied next to `report.html`, and linked from the report Evidence list)
- `editor.log`
- `unity.log` in Player mode
- `cdb.log` in CDB mode
- `report.html`

## Validation Flow

1. Build Debug Editor with `G:\UnitySource\BuildWindowsEditor.Bee.Debug.bat`. Then resolve `G:\UnitySource\build\WindowsEditor\Unity.exe` and the test project `G:\UnitySource\Tests\TestValidation`.
2. Generate or load the requested scene.
3. Apply requested test settings. The current example applies `Graphics.enableSRPBatch`.
4. In EditorPlay mode, start batch Unity without `-quit`, run `TestValidationRunner.RunEditor`, and enter PlayMode.
5. Run a state machine through `entering-play-mode` -> `waiting-for-scene` -> `running` -> `waiting-for-screenshot` -> `complete`.
6. After the requested frame count, show `UnityEditor.GameView`, invoke its private `RepaintImmediately()` method, read `UnityEditor.UnityStats`, then render to a temporary `RenderTexture` and capture the back buffer.
7. Write `result.json`, `screenshot.png`, and a completion sentinel to the Editor log.
8. The PowerShell script verifies result pass state, requested-vs-actual switch state, artifacts, and completion sentinel.
9. Write `report.html` for success and failure paths, including process crashes and timeouts.

## Result Contract

Reliable evidence:

- `passed`
- requested and actual values for every switch under test
- `validationMode`
- `requestedFrames` and `framesCompleted`
- `rendererCount`
- `foregroundPixelCount`
- `expectedColorPixelCount`
- screenshot and Editor log

Editor UnityStats fields:

- `drawCalls`
- `batches`
- `setPassCalls`
- `triangles`
- `vertices`
- `renderTextureChanges`
- `shadowCasters`
- `frameTime`
- `renderTime`

These counts are meaningful only when `renderStatsAvailable` is true. If core counters stay zero, report them as `N/A` rather than measured zero values.

The generated SRP Batcher example scene contains 24 shared-material cubes and 8 distinct-material spheres. Require at least 32 renderers and at least 2000 expected blue/warm pixels. Other generated scenes should define their own scene-specific contracts. Arbitrary loaded scenes use generic health checks only.

## HTML Report

`report.html` is the primary human-facing result. It contains:

- PASS/FAIL badge and process exit code
- scene, mode, requested/actual switch values
- **Comparison Evidence** section（对比验证输出契约，见下文）
- frame and renderer counts
- foreground and expected-color pixel counts
- UnityStats table
- screenshot preview
- links to raw evidence
- failure reason
- Editor/Player log tails
- CDB analysis and CDB log tail when CDB is enabled

Report the HTML path in the final response. A report is not a pass signal by itself; confirm `result.json`, sentinel, and artifacts for successful runs.

When the current engineering task tracks state in a `status.md` (for example under `Docs\superpowers\plans\...`), record the generated report/evidence directory there after completed validation runs. Use one clickable absolute-path Markdown link per run, preferably directly to `report.html` (or `cdb.log`/`result.json` when relevant), with a short result summary. Do not use backtick-only relative directories or bare Windows paths as the only representation. Keep failure diagnostics with their run directory.

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

## CDB Native Debugging

Always use `-Debugger Cdb` for EditorPlay in this repository, not only after a failure. A successful run still writes an empty-of-exception `cdb.log`, which is evidence that the native process exited without an AV, stack overflow, or divide-by-zero. If CDB is unavailable, stop and report that CDB is required; do not silently downgrade the run.

CDB mode:

1. Locates Windows Debuggers `cdb.exe`.
2. Starts Unity as the debuggee.
3. Loads line information and Unity symbols.
4. Enables automatic handlers for access violation, stack overflow, and divide-by-zero.
5. On exception, runs `!analyze -v`, switches to the exception context, dumps the current and all-thread stacks, and records Unity module information.
6. Writes `cdb.log`, exits the debuggee after evidence capture, and surfaces the exception plus symbolized Unity frames in `report.html`.

Do not infer a root cause solely from the outer process exit code. Read `cdb.log` and report the actual native exception and first meaningful Unity frames. Preserve the raw CDB log.

The SRP ON example produced a native stack overflow `0xC00000FD` at `Renderer::FlattenMaterialsAndCustomPropBuffers` calling `Renderer::EnsureMaterialCacheUpdated`; do not reuse this as a generic conclusion. Each new run and switch must derive its finding from that run's CDB evidence.

## Interpretation

- Debug Editor 未编过或 `BuildWindowsEditor.Bee.Debug.bat` 失败时，不要跑 PlayMode，也不要用旧的 `Unity.exe` 冒充本次验证。
- A baseline pass proves the harness can create/load the scene, enter PlayMode, run frames, render, and capture. It does not prove every switch works.
- A switch failure with CDB evidence should be diagnosed from the native exception and stack, not treated as a test harness defect.
- Missing completion sentinel, missing JSON/screenshot, or timeout means the run did not finish. Inspect Editor log, state file, and CDB log before changing engine code.
- `Temp/UnityLockfile` or "another Unity instance is running" means the project is open elsewhere. Stop the other Editor and remove the lockfile before retrying.
- Do not modify the harness merely because it correctly detects an engine defect.

## 报告自动打开（默认行为）

每次运行结束（无论 PASS/FAIL/超时，只要 `report.html` 已生成），PowerShell 脚本自动在默认浏览器打开 `report.html`，不需要额外参数或手动命令。Agent 的工作流相应约定：

1. 验证命令执行完后，报告已在浏览器弹出——最终回复里仍要给出 report.html 的可点击 Markdown 链接，但不重复调用 `Start-Process` 打开。
2. 若用户明确说"不要自动打开"，可传 `-NoOpenReport` 跳过。
3. 环境干扰（如 `Temp/UnityLockfile`）导致未生成报告时，脚本不会打开任何东西；按 Interpretation 清理后重跑。

Keep responses in Chinese by default. Preserve generated artifacts for diagnosis unless the user asks for cleanup, and never commit `Library/`, `Temp/`, `Report/`, `TestResults*/`, or generated scene output.
