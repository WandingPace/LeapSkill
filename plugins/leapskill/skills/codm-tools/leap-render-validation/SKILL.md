---
name: leap-render-validation
description: Run the UnitySource RenderValidation system for deterministic Unity rendering tests, including D3D11/Vulkan/GLES API matrices, static Graphics switch A/B comparison, RenderDoc capture, UnityStats collection, screenshots, and HTML reports. Use when Codex should build or reuse the RenderValidation test Player, validate rendering changes, compare an engine static switch before/after, inspect or regenerate matrix/comparison reports, or troubleshoot RenderValidation runs in G:/UnitySource.
---

# RenderValidation

Operate the existing system in `G:\UnitySource\Tests\RenderValidation`; do not rebuild the pipeline from scratch.

## Workflow

1. Read `G:\UnitySource\Docs\RenderValidation.md` first.
2. Confirm `build\WindowsEditor\Unity.exe` and `build\WindowsStandaloneSupport\Variations\win64_development_mono\WindowsPlayer.exe` exist.
3. Choose the narrowest command:
   - `list` for manifest validation.
   - `run` for one API evidence capture.
   - `compare` for a static switch A/B report.
   - `matrix` for every configured API and one static switch.
   - `matrix-report` to regenerate a matrix report from existing evidence.
4. Use [references/commands.md](references/commands.md) for exact commands and [references/configuration.md](references/configuration.md) before editing Case JSON.
5. After execution, inspect `result.xml`, `assertions.json`, `unity-stats.json`, `capture.rdc`, screenshots, and the HTML report. Report process/API/switch results separately.

## Required Interpretation

- `UnityEditor.UnityStats` supplies `setPassCalls`, `drawCalls`, `batches`, `triangles`, `vertices`, and timing. Do not add `Graphics.renderValidation*` or another engine statistics API.
- RenderDoc captures independently validate Player GPU execution and provide RenderDoc draw counts. Current vendor CLI may suppress successful `info/events/draws` text, so use assert exit codes and `.rdc` evidence.
- `matrix` compares evidence within the same run and does not use canonical baselines.
- If a switch prevents the Player from reaching `stable` or `complete`, report that as a behavioral finding; preserve Editor/UnityStats evidence and mark the Player/RenderDoc variant failed.
- A report alone is not a pass signal. Confirm per-variant `result.xml` and captures before calling the workflow successful.

## Current Validated Default

Use `UnityEngine.Graphics.enableRenderThreadEarlySync` with `false | true` to smoke-test the switch workflow.

Do not treat a switch as validated merely because it can be applied. Require successful Player protocol events and captures, or report the missing protocol/capture stage as the observed behavior for that switch.
