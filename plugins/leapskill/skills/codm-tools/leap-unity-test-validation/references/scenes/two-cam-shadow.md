# 场景流程：twoCamShadow（验证 perObjectShadow）

本场景**唯一的验证目标是 perObjectShadow**：大 spot 低分辨率下物体阴影边缘糊/锯齿，开 per-object bound shadow 后阴影收紧到物体包围盒、边缘变锐。公共 harness（编译/run/result/CDB/report/对比契约）见 `SKILL.md` 主体。

## 被测对象与断言

- 生成器：`Assets\Editor\TwoCamShadowSceneCreator.cs`；产物 `Assets/Generated/TwoCamShadowValidation.unity`（runner 幂等，已存在则直接打开，改 creator 后传 `-ForceRecreate`）。
- 被测开关：`Graphics.usePerObjectBoundShadow`（全局）+ `Light.perObjectBoundShadowMode`（挂在 `SpotLight_Shadow1024` 上的 `PerObjectShadowTestSetting`）。
- 观测点：1P 相机黑底下 `OnePHandPlate`（magenta）上的阴影边缘**过渡带像素数**。OFF 糊=过渡带宽，ON 锐=过渡带窄。
- 断言：A/B 对比 ON 比 OFF 过渡带缩小 ≥30% 且 ≥20px，`verdict=confirmed` 才 PASS（见 SKILL.md「对比验证输出契约」）。

## 唯一参数

- `-PerObjectShadow on|off`：per-object 请求态，记入 result 的 `perObjectShadowRequested/Actual`。默认 `off`。这是本场景**唯一**的测试开关。

## 运行命令

```powershell
& G:\UnitySource\Tests\TestValidation\Scripts\run-test-validation.ps1 `
  -EditorPath "<当前工作区>\build\WindowsEditor\Unity.exe" `
  -Mode EditorPlay -TestScene Assets/Generated/TwoCamShadowValidation.unity `
  -Frames 140 -PerObjectShadow on -SrpBatch:$false -NoRenderDoc -Debugger Cdb -TimeoutSeconds 600
```

（`-EditorPath` 取值见 `../workspace-resolution.md`。）

## 探针状态机

进 PlayMode 跑满 `Frames` 后，`AdvanceOnePShadowProbes` 分步执行（每步间隔 `probeWaitFrames=2`，让引擎重建 shadowmap）：

1. step 0/1：灯光隔离 + 大 spot 低分辨率基线，量 `bigSpotTransitionPixels`。
2. step 2/3：per-object **OFF** 基线，产出 `probe_perobject_off.png` + `perObjectOffTransitionPixels`；再切 ON。
3. step 4：per-object **ON**，产出 `probe_perobject_on.png` + `perObjectOnTransitionPixels`；恢复请求态。
4. 完成后 `CaptureTwoCamScreenshots` 拍 `_world.png` / `_1p.png` 双机截图 + 合成图。

## 环境前置条件（不是测试参数）

这两个开关**与本用例无关，不要当成 perObjectShadow 的对比项去调**。它们只是 runner 的默认背景行为，恰好在当前引擎版本下会阻塞/崩溃，所以跑本场景时固定设为下列值以保证进程能活到探针跑完：


- **RenderDoc 截帧**：runner 默认在装了 RenderDoc 时于跑满帧数后 `TriggerMultiFrameCapture(3)`，抓到的是 **per-object ON 态**（`-PerObjectShadow on` 已应用）的正常渲染帧，`.rdc` 进程退出时落盘到报告同级 `capture.rdc` 并链接进 report.html。per-object 证据（探针像素+双机截图）本身不依赖 RenderDoc——要抓帧就省略 `-NoRenderDoc`（当前版本实测可正常 flush），不想要就固定 `-NoRenderDoc`。要 ON/OFF 对比帧需分别用 `-PerObjectShadow on/off` 各跑一次。

> 注意：这两个是"让进程别提前死掉"的环境约束，**不要**把它们写进 comparisons，也不要把 SRP on/off 当成 per-object 的 A/B。per-object 的 A/B 只有 OFF vs ON 一组。
