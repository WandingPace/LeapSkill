---
name: leap-render-validation
description: "用于运行或复现 UnitySource RenderValidation 确定性渲染验证，涵盖多图形 API、静态 Graphics 开关 A/B、RenderDoc 抓帧、UnityStats、截图和 HTML 报告，也可检查或重建矩阵/对比报告。不用于 Unity Editor PlayMode 的 TestValidation 场景验证或普通 Unity 功能测试。"
---

# RenderValidation

操作 `G:\UnitySource\Tests\RenderValidation` 中已有的系统，不要从零重建整条流程。

## 工作流

1. 先阅读 `G:\UnitySource\Docs\RenderValidation.md`。
2. 确认 `build\WindowsEditor\Unity.exe` 和 `build\WindowsStandaloneSupport\Variations\win64_development_mono\WindowsPlayer.exe` 存在。
3. 选择范围最小的命令：
   - `list`：校验 manifest。
   - `run`：采集单个 API 的证据。
   - `compare`：生成静态开关 A/B 报告。
   - `matrix`：覆盖所有已配置 API 和一个静态开关。
   - `matrix-report`：基于已有证据重新生成矩阵报告。
4. 具体命令见 [references/commands.md](references/commands.md)；修改 Case JSON 前先阅读 [references/configuration.md](references/configuration.md)。
5. 执行后检查 `result.xml`、`assertions.json`、`unity-stats.json`、`capture.rdc`、截图和 HTML 报告。进程、API 和开关结果要分别报告。

## 必须遵守的结果解读

- `UnityEditor.UnityStats` 提供 `setPassCalls`、`drawCalls`、`batches`、`triangles`、`vertices` 和耗时。不要新增 `Graphics.renderValidation*` 或其他引擎统计 API。
- RenderDoc 抓帧独立验证 Player 的 GPU 执行，并提供 RenderDoc draw 数量。当前 vendor CLI 可能隐藏成功的 `info/events/draws` 文本，因此要使用断言退出码和 `.rdc` 证据。
- `matrix` 只比较同一次运行内的证据，不使用标准基线。
- 如果某个开关导致 Player 无法达到 `stable` 或 `complete`，应把它报告为行为问题；保留 Editor/UnityStats 证据，并把 Player/RenderDoc 变体标为失败。
- 只有报告不算通过信号。必须确认每个变体的 `result.xml` 和抓帧，才能判定流程成功。

## 当前已验证默认项

使用 `UnityEngine.Graphics.enableRenderThreadEarlySync` 的 `false | true` 对开关流程做冒烟测试。

不要因为开关能够应用就认为它已经验证。必须拿到成功的 Player 协议事件和抓帧；否则应把缺失协议或抓帧阶段报告为该开关的观察结果。
