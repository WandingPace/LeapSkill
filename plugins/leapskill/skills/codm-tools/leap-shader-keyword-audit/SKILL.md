---
name: leap-shader-keyword-audit
description: "用于审计 CODM Shader 关键字：找出 Shader pragma 未声明、Unity 内置和引擎也未定义、但材质或 SVC 仍在使用的关键字，预览或删除资源侧引用，并审计删除后的 SVN diff 是否只改 keyword 字段。不用于普通 Shader 编译错误、RenderDoc 渲染诊断或材质视觉问题排查。"
---

# Shader 关键字审计

用于处理 `keyword.txt` 与项目资源的对账：区分 Shader pragma、Unity built-in、引擎正式 keyword、材质 `.mat` 和 `.shadervariants` 来源，避免把编译期 `#define`、普通 `#if` 引用或运行时全局开关误判为变体关键字。

## 工作流

1. 先只读审计，不直接删除。
2. 默认输入为：
   - 关键字表：`<CODM_ROOT>\Assets\Shaders\CODM\Standard\keyword.txt`
   - 扫描根：`<CODM_ROOT>\Assets`
   - 引擎根：`G:\UnitySourceCODM`
3. 先生成 CSV 报告并检查 `resource-only` / `Unmatched`。报告中的项表示：Shader pragma 未声明、Unity 内置白名单未覆盖、引擎 built-in 与引擎 Shader pragma 也未定义，但材质或 SVC 仍在使用。
4. 需要删除时，必须先取得用户明确的执行授权，再同时传 `--delete --yes`。只传 `--delete` 只打印警告，不写文件。
5. 删除后再次运行只读审计，确认 `Unmatched` 归零；再运行 `audit_svn_diff.py` 检查 SVN diff，确认变更只落在 keyword 字段。
6. 报告修改文件时按“文件、来源、删除的关键字、数量”输出；不要只说总数量。

## 命令

脚本入口：

```powershell
$skill = "<skill-dir>"
$codm = $env:CODM_ROOT
if (-not $codm) { $codm = "I:\CODMCHN" }

# 只读审计
python "$skill\scripts\shader_keyword_audit.py" `
  --keyword-file "$codm\Assets\Shaders\CODM\Standard\keyword.txt" `
  --scan-root "$codm\Assets" `
  --csv "$codm\.codex-tmp\shader_keyword_audit.csv"

# 只删除明确授权后的 Unmatched 项，并生成逐文件报告
python "$skill\scripts\shader_keyword_audit.py" `
  --keyword-file "$codm\Assets\Shaders\CODM\Standard\keyword.txt" `
  --scan-root "$codm\Assets" `
  --delete --yes `
  --delete-report "$codm\.codex-tmp\shader_keyword_deleted_files.csv"
```

删除后 SVN diff 审计：

```powershell
python "$skill\scripts\audit_svn_diff.py" `
  --report "$codm\.codex-tmp\shader_keyword_deleted_files.csv" `
  --output-dir "$codm\.codex-tmp\shader_keyword_svn_audit"
```

`audit_svn_diff.py` 会检查报告内每个文件：

- `svn status` 必须是普通 `M`；
- 不允许属性变更、冲突、缺失或未版本化；
- diff 中新增/删除行只允许来自 `m_ShaderKeywords`、`m_ValidKeywords` 或 `keywords`；
- 发现其他字段变化时返回非零退出码并列出文件与行。

SVN 远端基线不可用、凭据失败或大批量 diff 很慢时，不要用状态检查冒充逐行 diff 结论；明确报告缺口。

## 判定规则

- Shader 侧只认 `#pragma multi_compile*` / `#pragma shader_feature*`；`#define` 和普通 `#if` 不算正式声明。
- `keyword.txt` 不是打包链路入口；打包实际看材质、SVC、Unity built-in 与引擎 keyword。
- `_DITHER_LOD` 属于引擎 built-in；不要把它列为未定义。
- 删除只改材质和 SVC 中的关键字引用，不修改 Shader 源码。
- 对 `ATMOSPHERICS_LOW`、`HTOD_SCATTERING`、`_USE_DYNAMIC_LIGHT` 等编译期宏/运行时关键字，先按审计脚本和引擎结果判断，不要凭名称推断。

## 输出要求

- 报告必须列出每个被改文件；
- 同时给出总数：文件数、关键字条目数、唯一关键字数；
- 删除后给出二次审计结果；
- 如果发现非 keyword 字段变化，单独列出文件、字段行，并说明这不是本 skill 删除器产生的预期变更。
