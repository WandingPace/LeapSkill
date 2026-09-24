---
name: leap-quickcmd-compose
description: "用于发现、编排并执行用户 PowerShell QuickCmd 中的 qc-* 命令，支持关闭 CODM、完整更新项目等有序工作流。不用于硬编码命令目录、绕过实时命令列表或执行与 QuickCmd 无关的 PowerShell 操作。"
---

# QuickCmd 编排

只能通过 `scripts/quickcmd-runner.ps1` 执行命令。不要在本 skill 中复制或硬编码 `QuickCmd.ps1` 的命令目录。

## 工作流

1. 每次执行请求的工作流前，先用 `-List -Json` 运行 runner。该操作会点源当前 `QuickCmd.ps1`，并返回实时命令目录。
2. 根据显示名称和 `qc-*` 函数名，把用户请求的每个动作映射到目录项。必须保持用户指定的顺序。
3. 如果动作只有一个明确匹配项，直接继续，不要询问。只有存在多个合理候选或完全没有匹配项时才询问。
4. 执行前，用一行简短文字告诉用户确切顺序，例如：`调用顺序：qc-closeCODM -> qc-updateProject`。
5. 使用一次 runner 调用和 `-Commands` 按顺序执行。不要使用 QuickCmd 的交互式 `c`/fzf 选择器。
6. 报告每条命令的成功或失败。首次失败即停止；除非用户明确要求尽力继续。

## 命令

列出当前命令目录：

```powershell
& "<skill-dir>\scripts\quickcmd-runner.ps1" -List -Json
```

执行有序工作流：

```powershell
& "<skill-dir>\scripts\quickcmd-runner.ps1" -Commands qc-closeCODM,qc-updateProject
```

只有用户明确要求失败后继续时，才使用 `-ContinueOnError`。

## 安全规则

- 用户直接要求关闭、打开、更新、构建、配置或转发时，视为授权执行对应的实时 QuickCmd 条目。
- 不要静默增加用户没有请求的动作。
- 绝不调用实时目录中不存在的 `qc-*` 函数。
- 保持执行可见：在对话中展示解析后的顺序，并允许 runner 打印命令头和原始输出。
- 如果加载源文件失败，停止并报告路径和错误；不要回退到过期目录。
