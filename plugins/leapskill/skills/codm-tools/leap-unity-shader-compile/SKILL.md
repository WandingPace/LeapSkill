---
name: leap-unity-shader-compile
description: "用当前 Unity 5.6 UnityShaderCompiler.exe 编 vulkan/gles3/d3d11 变体，按 shader 名、pass # 和 keywords 输出反汇编与 ALU/TEX/采样数。用于编译 shader、看变体指标、对比 cginc 修改对 SPIR-V/采样的影响。不用于 RenderDoc 抓帧、实时 GPU 性能或关键字审计。"
---

# Unity Shader 离线编译

直接对话当前 Editor 那套 `UnityShaderCompiler.exe`，按 shader 名/路径 + `pass #` + keywords 编 vulkan / gles3 / d3d11。stdout 打指标，反汇编落盘到 `%TEMP%\usc_compile`。只用 Python 标准库。

## 何时用

- 用户给 FrameDebugger 变体文本：`CODStandard Dynamic, pass #0` + 一行 keywords
- 要看编出来的 Vulkan SPIR-V / GLES / DX11
- 要比两份 cginc 对采样次数 / ALU 的影响
- 不要用 VulkanSDK glslang，也不要开 Editor Inspector 的 Compile and show code

## 默认路径

- 工程：`CODM_ROOT`，缺省 `I:\CODMCHN`
- 编译器：`G:\CODM_CHN\Engine\Unity564p4_Win64_Bin_QTS\WinUnity\Data\Tools64\UnityShaderCompiler.exe`
- Data：同目录 `...\WinUnity\Data`
- shader 名只扫 `I:\CODMCHN\Assets\Shaders`
- `--shader` 也接受完整 `.shader` 路径：绝对路径、工程相对路径、`Assets/...`

## 命令

```powershell
$skill = "C:\Users\leapliu\.agents\skills\leap-unity-shader-compile"
$py = "python"
$script = "$skill\scripts\compile_shader.py"

# smoke
& $py $script --smoke

# 列 pass
& $py $script --shader "CODStandard Dynamic" --list

# 编一个变体（默认 vulkan+gles3+d3d11）
& $py $script --shader "CODStandard Dynamic" --pass 0 --keywords "DIRECTIONAL ENABLE_CUSTOM_SHADOWMAP SHADOWS_NOSS SHADOWS_SCREEN _DYNAMIC_OPAQUE"

# FrameDebugger 两行
& $py $script --variant @"
CODStandard Dynamic, pass #0
DIRECTIONAL ENABLE_CUSTOM_SHADOWMAP SHADOWS_NOSS SHADOWS_SCREEN _DYNAMIC_OPAQUE
"@

# 只编 vulkan
& $py $script --shader "CODStandard Dynamic" --pass 0 --keywords "DIRECTIONAL" --platform vulkan

# 完整 .shader 路径（绝对路径 / 工程相对路径 / Assets/... 都可以）
& $py $script --shader "I:\CODMCHN\Assets\Shaders\CODM\Standard\CFStandard_Dynamic.shader" --pass 0 --keywords "DIRECTIONAL ENABLE_CUSTOM_SHADOWMAP SHADOWS_NOSS SHADOWS_SCREEN _DYNAMIC_OPAQUE"
& $py $script --shader "Assets\Shaders\CODM\Standard\CFStandard_Dynamic.shader" --list

# 编完不自动打开输出
& $py $script --shader "CODStandard Dynamic" --pass 0 --keywords "DIRECTIONAL" --platform vulkan --no-open

# 对比两份 cginc
& $py $script --shader "CODStandard Terrain TexArray And VT" --pass 0 --keywords "DIRECTIONAL SHADOWS_SCREEN" --platform vulkan --diff A.cginc B.cginc
```

## 输出

- stdout：ALU / TEX / flow / tempRegister / sample_count / texbind / cbuffer，并打 `out=<dir>`
- 默认目录：`%TEMP%\usc_compile\<shader>\passN\<kw-hash>\`
  - 实例：`C:\Users\leapliu\AppData\Local\Temp\usc_compile\CODStandard_Dynamic\pass0\ebde587fa0`
  - `metrics.json`
  - `vulkan.spv` `vulkan.disasm`
  - `gles3.glsl` `gles3.disasm`
  - `d3d11.vs.bin` `d3d11.fs.bin` 及对应 `.disasm`
- `--diff` 输出：`%TEMP%\usc_compile\diff\A` 和 `...\B`
- 编译成功后自动打开输出目录（Explorer）和 `metrics.json` / `vulkan.disasm` / `gles3.disasm` / `d3d11.*.disasm`
- `--list` / `--smoke` 不打开；`--no-open` 关掉自动打开
- `stats:` 原样保留：DX11 最准，GLES/Vulkan 可能为 0；采样次数改从反汇编计

## 协议坑（不要改）

- magic `201508070`，长度是 UTF-8 字节数
- `initializeCompiler` 固定读 20 平台 × 2 行
- Vulkan=`18` GLES3=`9` D3D11=`4`；Vulkan/GLES3 必须 `programType=VS` 且 `programMask=VS|FS`
- include 顺序：shader 目录 → `CODM_ROOT` → `Assets/Shaders/Includes` → `Assets/Shaders` → engine `CGIncludes` 最后
- preprocess 不注入 `SHADERLOD_*`，compile 前按 SubShader LOD 补；LightMode 补 `UNITY_PASS_*`
- 改 cginc 对比只能 swap live 文件，不要靠 extra include 目录覆盖；`--diff` 必须还原并 hash 校验
- FrameDebugger 的 `pass #` 是当前 LOD SubShader 内的 Pass 序号，默认第一个 SubShader；`--lod` 选其它 LOD
