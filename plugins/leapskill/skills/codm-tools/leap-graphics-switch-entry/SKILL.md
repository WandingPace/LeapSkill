---
name: leap-graphics-switch-entry
description: "为 CODM 的引擎 Graphics.* 静态开关补全三个控制入口：Editor 右键菜单、GM Terminal 命令、FeatureSwitchWindow。用于新增或补挂 Graphics 开关入口；不用于普通业务逻辑开关、非 Graphics 类型的运行时配置或引擎 C++ 侧改动。"
---

# Graphics 开关三入口

CODM 的引擎 `Graphics.*` 静态开关不序列化、进程级生效。给它们挂控制入口时，三处先例文件各有一种模式，按现有先例风格插入即可。

## 入口位置与插入模式

三处都要加，且加的片段必须跟同文件里最近的同类开关保持一致的写法。

### 1. Editor 右键菜单

文件：`I:\CODMCHN\Assets\Scripts\Effects\Editor\ProgramMenuEditor.cs`

在 `OnSetupMenu(GenericMenu menu)` 里找对应分组（`LightProbe` / `Scene` / `Shadow` / `OC` / `Render` 等），插入：

```csharp
menu.AddItem(new GUIContent($"Render/Graphics.<propName> 开关: {GetOnStr(Graphics.<propName>)}"), false,
    (s) => { Graphics.<propName> = !Graphics.<propName>; }, "");
```

### 2. GM Terminal 命令

文件：`I:\CODMCHN\Assets\Scripts\GM\TerminalCommands_Graph.cs`

在已有的 `RegisterCommand` 静态方法区追加：

```csharp
[RegisterCommand(Help = "<CommandName> [0|1], no argument toggles")]
static void <CommandName>(CommandArg[] args)
{
    Graphics.<propName> = args.Length > 0
        ? args[0].Int != 0
        : !Graphics.<propName>;
    Terminal.Log("<propName> = {0}", Graphics.<propName>);
}
```

命令命名取 PascalCase 加 `Toggle` 后缀（如 `VAExplicitBufferUploadToggle`、`SubmitSplitBeforeBackbufferToggle`）。

### 3. FeatureSwitchWindow

文件：`I:\CODMCHN\Assets\Editor\Tools\FeatureSwitch\FeatureSwitchWindow.cs`

在对应 tab 的 `Draw*()` 方法里追加：

```csharp
ToggleGraphics("<propName>", "<tooltip>");
```

`ToggleGraphics` 已封装反射读写和缺 binding 降级提示，直接调用即可，不要直接写 `Graphics.<propName>`。

## 前置检查

- 确认引擎 C++ 侧 binding 存在：`rg -n "<propName>" "G:\UnitySource" --type cpp`。没有 binding 时开关在运行时不生效，FeatureSwitchWindow 会显示"无 binding"。
- 确认启动逻辑是否已有默认值设置（如 `LoadingFlowDevicePatchController`），如有，入口只是运行时覆盖，不改启动默认值。
- 项目编码规则禁止反射，但 `FeatureSwitchWindow` 的 `ToggleGraphics` 是已存在的封装，属于先例复用，不算新增反射。

## 验收

改完三个文件后走 `compile-verify` 确认 Editor + Runtime 程序集都能过。
