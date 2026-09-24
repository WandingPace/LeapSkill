# 命令

所有命令都在 `G:\UnitySource` 下运行。

## 主入口

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 [options]
```

## 列出 Case

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 -Command list
```

校验 Case JSON，并打印 ID、平台、图形 API 和场景。

## 仅构建

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command build `
  -Case material-mesh-setpass `
  -Output artifacts\RenderValidation\manual-build
```

构建一个包含 `graphicsApis` 所配置图形 API 的 Player。

## 单 API 运行

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command run `
  -Case material-mesh-setpass `
  -Output artifacts\RenderValidation\single-api
```

使用 Case 的 `graphicsApi` 值。这是证据采集，不是标准基线测试。

## 多 API 加开关矩阵

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command matrix `
  -Case material-mesh-setpass `
  -Output artifacts\RenderValidation\api-switch-matrix `
  -SwitchType UnityEngine.Graphics `
  -SwitchMember enableRenderThreadEarlySync `
  -BeforeValue false `
  -AfterValue true
```

Runner 会对每个已配置 API 依次执行：

1. Editor/GameView Before 的 UnityStats 和截图。
2. Player/RenderDoc Before 抓帧。
3. Editor/GameView After 的 UnityStats 和截图。
4. Player/RenderDoc After 抓帧。
5. Before/After 截图差异和 HTML 报告。

输出目录为 `<output>/<case>/<api>/<before|after>/`，另加 `<output>/<case>/matrix-report.html`。

## 重新生成矩阵报告

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command matrix-report `
  -Case material-mesh-setpass `
  -Run artifacts\RenderValidation\api-switch-matrix\material-mesh-setpass
```

修改 `Tests\RenderValidation\Report\RenderValidationComparisonTemplate.html` 或 `Runner/MatrixReportWriter.cs` 后使用。该命令会重新处理 RenderDoc 统计，但不会重新构建或抓帧。

## 静态开关 A/B 报告

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command compare `
  -Case material-mesh-setpass `
  -Output artifacts\RenderValidation\switch-compare `
  -SwitchType UnityEngine.Graphics `
  -SwitchMember enableRenderThreadEarlySync `
  -BeforeValue false `
  -AfterValue true
```

生成包含一个可拖动 Before/After 视图的 `comparison-report.html`。

## 分析已有抓帧

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command analyze `
  -Case material-mesh-setpass `
  -Capture G:\path\capture.rdc `
  -Output G:\path\analysis
```

## 引擎支持产物构建

只有对应的支持产物缺失或过旧时才运行：

```powershell
.\BuildWindowsEditor.Bee.bat
perl .\bee.pl WindowsStandaloneSupport --platform=win64 --config=release --scriptingBackend=mono --useQTS=1 --developmentPlayer=1 --verbose
```
