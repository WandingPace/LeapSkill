---
name: caveman-commit
description: >
  Write a Conventional Commits message compressed to intent only. Use for
  "write a commit", "commit message", /commit or /caveman-commit.
  中文用户说"写个提交信息""生成 commit"时也使用。Do NOT use for 执行 git commit 或暂存文件。
---

写极简而精确的提交信息。Conventional Commits 格式。无废话。写"为什么"优先于"做了什么"。

## 规则

**主题行：**
- `<type>(<scope>): <动词开头摘要>` — `<scope>` 可选
- 类型：`feat`、`fix`、`refactor`、`perf`、`docs`、`test`、`chore`、`build`、`ci`、`style`、`revert`
- 动词开头："新增"、"修复"、"移除"——不用"新增了"、"已修复"
- 尽量 ≤50 字符，硬上限 72
- 结尾不加句号
- 冒号后中英文遵循项目惯例

**正文（仅在需要时）：**
- 主题行已自明时完全省略
- 仅这些情况加正文：不显而易见的*为什么*、破坏性变更、迁移说明、关联 issue
- 72 字符折行
- 列表用 `-` 不用 `*`
- issue/PR 引用放末尾：`Closes #42`、`Refs #17`

**绝不写入：**
- "本提交做了 X"、"我"、"我们"、"现在"、"目前"——diff 自己会说做了什么
- "应某人要求……"——用 Co-authored-by trailer
- "Generated with Claude Code" 或任何 AI 署名——除非用户自己的规则要求 `Assisted-by`/AI 署名 trailer，那就作为 trailer 添加
- Emoji（除非项目惯例要求）
- scope 已表达时复述文件名

## 示例

diff：新增用户资料 endpoint，正文解释为什么
- ❌ "feat: 新增一个从数据库获取用户资料信息的接口"
- ✅
  ```
  feat(api): 新增 GET /users/:id/profile

  移动端首屏只需要资料数据而非完整 user 载荷，
  以降低冷启动页面的 LTE 流量。

  Closes #128
  ```

diff：破坏性 API 变更
- ✅
  ```
  feat(api)!: 将 /v1/orders 更名为 /v1/checkout

  BREAKING CHANGE: 使用 /v1/orders 的客户端须在 2026-06-01 前
  迁移到 /v1/checkout。此后旧路由返回 410。
  ```

## 自动澄清

以下情况必须写正文：破坏性变更、安全修复、数据迁移、回滚先前提交。绝不把这些压缩成只有主题行——未来的调试者需要上下文。

## 边界

只生成提交信息。不执行 `git commit`，不暂存文件，不 amend。输出为可直接粘贴的代码块。"stop caveman-commit"或"正常模式"：恢复详细提交风格。
