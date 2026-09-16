# 工作区与 Unity.exe 解析（飞行前检查）

TestValidation 的**测试工程只有一份**（固定在 `G:\UnitySource\Tests\TestValidation`），但被测的**引擎 `Unity.exe` 必须来自"当前工作区"那一次成功 Debug build**。这两件事别混在一起——选错引擎是本 skill 最常见的踩坑来源。

## 为什么必须先确认工作区

同一台机器上同时存在多个 Unity 源码 checkout（`G:\UnitySource`、`G:\UnitySourceCODM`、`I:\CODMCHN` 等），各自有独立的 `build\WindowsEditor\Unity.exe`，版本与定制不同。

- 引擎改动（新绑定 / 新开关）只在**做改动那个工作区**里编出来的 `Unity.exe` 才存在。
- 测试工程里的脚本（如 `PerObjectShadowTestSetting.cs`）会调用这些新绑定；用旧/别的工作区的 `Unity.exe` 跑，会 `Scripts have compiler errors`（如 `error CS0117: Graphics does not contain usePerObjectBoundShadow`），batchmode abort，最终超时且没有 result.json。
- 症状迷惑性强：表现为"超时"，但根因是引擎二进制与测试脚本不匹配。先看 `editor.log` 有没有 `error CS` / `Compilation failed`。

## 解析步骤（每次跑测试前都走一遍）

1. 确认当前工作区根：用 `cgame-engine:project-inspect` 或直接看会话 `cwd`/任务指定的 checkout（例如 `G:\UnitySourceCODM`）。不要假设是 `G:\UnitySource`。
2. 定位该工作区的 Debug Editor 产物：`<当前工作区根>\build\WindowsEditor\Unity.exe`。
   - 不存在或日期早于本次引擎改动时，先用该工作区的 `BuildWindowsEditor.Bee.Debug.bat` 编一次。
3. 显式传给 runner（runner 默认按脚本位置解析到 `G:\UnitySource`，必须用 `-EditorPath` 覆盖）：

```powershell
& G:\UnitySource\Tests\TestValidation\Scripts\run-test-validation.ps1 `
  -EditorPath "G:\UnitySourceCODM\build\WindowsEditor\Unity.exe" `
  -Mode EditorPlay -CreateScene twoCamShadow -Frames 120 -Debugger Cdb -TimeoutSeconds 600
```

4. 核对：脚本第一行会打印 `[TestValidation] Editor: <path>`。确认这个 path 属于当前工作区再继续；不对就停。

## 不变量（invariants）

- 测试工程路径 `G:\UnitySource\Tests\TestValidation` 固定，不随工作区变。
- `Unity.exe` 路径随工作区变，禁止写死、禁止用别的 checkout 的产物冒充。
- `Temp\UnityLockfile` 残留（无对应运行中的本工程 Unity 进程）会阻塞启动，先删再跑。注意别误删别的 checkout 正在用的工程锁。
