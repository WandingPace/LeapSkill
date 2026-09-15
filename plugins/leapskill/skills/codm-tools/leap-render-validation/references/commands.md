# Commands

All commands run from `G:\UnitySource`.

## Main entry

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 [options]
```

## List cases

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 -Command list
```

Validates Case JSON and prints ID, platform, graphics API, and scene.

## Build only

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command build `
  -Case material-mesh-setpass `
  -Output artifacts\RenderValidation\manual-build
```

Builds one Player containing the graphics APIs configured by `graphicsApis`.

## Single-API run

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command run `
  -Case material-mesh-setpass `
  -Output artifacts\RenderValidation\single-api
```

Uses the Case `graphicsApi` value. This is evidence capture, not a canonical-baseline test.

## Multi-API + switch matrix

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

For every configured API, the Runner executes:

1. Editor/GameView Before UnityStats and screenshot.
2. Player/RenderDoc Before capture.
3. Editor/GameView After UnityStats and screenshot.
4. Player/RenderDoc After capture.
5. Before/After screenshot diff and HTML report.

The output is `<output>/<case>/<api>/<before|after>/` plus `<output>/<case>/matrix-report.html`.

## Regenerate matrix report

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command matrix-report `
  -Case material-mesh-setpass `
  -Run artifacts\RenderValidation\api-switch-matrix\material-mesh-setpass
```

Use after changing `Tests\RenderValidation\Report\RenderValidationComparisonTemplate.html` or `Runner/MatrixReportWriter.cs`; this replays RenderDoc statistics but does not rebuild or recapture.

## Static switch A/B report

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

Generates `comparison-report.html` with one draggable Before/After view.

## Analyze an existing capture

```powershell
Tests\RenderValidation\Scripts\run-render-validation.ps1 `
  -Command analyze `
  -Case material-mesh-setpass `
  -Capture G:\path\capture.rdc `
  -Output G:\path\analysis
```

## Engine support builds

Only run these when the corresponding support output is missing or stale:

```powershell
.\BuildWindowsEditor.Bee.bat
perl .\bee.pl WindowsStandaloneSupport --platform=win64 --config=release --scriptingBackend=mono --useQTS=1 --developmentPlayer=1 --verbose
```
