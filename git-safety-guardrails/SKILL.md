---
name: git-safety-guardrails
description: "Safeguard repositories against destructive, irreversible, or history-rewriting Git operations. Use when running force pushes, hard resets, branch deletions, cleans, destructive restores, or history re-writes — even if the user says \"clean up git history\". Do NOT use for routine safe git status, fetch, diff, or branch queries."
---

# Git 安全护栏

安装和维护确定性的预执行护栏，在自治代理执行危险、破坏性或历史重写的 Git 命令之前拦截和阻止这些命令。

---

## 核心不变量

1. **确定性拦截**：在执行前自动阻止破坏性的 Git 命令（`git push --force`、`git reset --hard`、`git clean -f/-fd`、`git branch -D`、`git checkout .`、`git restore .`）。
2. **显式权限门**：截获的命令返回显式非零退出代码，通知代理它缺乏执行破坏性操作的权限。
3. **范围澄清**：始终询问用户是将护栏本地应用到项目（`.claude/settings.json`）还是全局应用（`~/.claude/settings.json`）。
4. **设置合并安全**：将护栏挂钩无缝合并到现有的“PreToolUse”配置中，而不会覆盖其他工具或设置。
5. **强制拦截测试**：在完成设置之前验证安全挂钩是否在模拟禁止命令上正确触发。

---

## 架构和内容地图 (MOC)

```
[ Agent Tool Call (Bash/Git) ] ──► [ PreToolUse Hook: `block-dangerous-git.sh` ]
                                                  │
                        ┌─────────────────────────┴─────────────────────────┐
                        ▼                                                   ▼
            [ Safe Git Operation ]                              [ Destructive Command ]
            - `git status`, `git diff`                          - `git push --force`, `reset --hard`
            - ALLOWED to execute                                - BLOCKED (Exit Code 2)
```

|组件|责任|地点 |
|---|---|---|
| **分类器挂钩脚本** |检查并阻止禁止的 git 模式 | `scripts/block-dangerous-git.sh` |
| **Python 命令解析器** |解析复杂的 shell 命令链 | `scripts/classify_git_command.py` |
| **设置集成** |代理环境中的钩子注册 | `.claude/settings.json` 或 `~/.claude/settings.json` |

---

## 分步程序 (TWI)

### 步骤一：确认护栏范围
- **操作**：询问用户是否仅为此项目或全局配置护栏。
- **要点**：除非用户指定全局，否则默认为项目级别 `.claude/settings.json`。
- **为什么**：范围内的安装可以避免外部个人存储库中出现意外的副作用。

### 第 2 步：复制 Hook 脚本并使其可执行
- **操作**：将 `scripts/block-dangerous-git.sh` 复制到 `.claude/hooks/block-dangerous-git.sh` 并运行 `chmod +x`。
- **要点**：复制前确保父目录存在。
- **内嵌清单**：
  - [ ] 目标目录已创建
  - [ ] 复制脚本并设置可执行权限（`chmod +x`）
  - [ ] 如果需要，Python 分类器脚本位于同一位置

### 步骤 3：在设置配置中注册 Hook
- **操作**：将 PreToolUse 挂钩条目添加到 `.claude/settings.json`，合并到现有数组（如果存在）中。
- **要点**：使用 `"$CLAUDE_PROJECT_DIR"/.claude/hooks/block-dangerous-git.sh` 路径扩展。
- **为什么**：相对路径扩展确保了跨不同工作目录上下文的钩子函数。

### 步骤 4：验证护栏拦截（测试门）
- **操作**：使用模拟的阻止命令测试挂钩：
````bash
echo '{"tool_input":{"command":"git push origin main --force"}}' | .claude/hooks/block-dangerous-git.sh
````
- **关键点**：验证命令是否以代码 2 退出并输出描述性阻止消息。
- **为什么**：证明钩子拦截危险命令可以保证未经验证的代理不会意外擦除 Git 历史记录。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“如果工作树有未提交的错误，则允许`git reset --hard`。”* | **阻止所有硬重置；需要显式存储或恢复。** |硬重置永久删除未提交的代码和工作树上下文。 |
| *“允许强制推送功能分支。”* | **默认阻止所有强制推送。** |强制推送可以覆盖队友的提交并破坏分支历史记录。 |
| *“跳过使用模拟输入验证挂钩脚本。”* | **强制模拟测试通过。** |挂钩脚本中的语法错误会导致它们无法打开，从而使存储库不受保护。 |

