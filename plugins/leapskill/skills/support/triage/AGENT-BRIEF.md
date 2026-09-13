# 编写 Agent Brief

Agent brief 是 issue 或 PR 进入 `ready-for-agent` 状态时贴上的结构化评论。它是 AFK agent 工作的权威规格。原始正文和讨论只是背景；agent brief 才是合同。

它说明**agent 应该做什么**，这个定义在两类对象上都成立：issue 是从零构建变更；PR 是在现有 diff 上完成剩余工作、补齐缺口、处理 review 意见。原则相同，下面的 PR 示例展示了差异。

## 原则

### 耐久优于精确到位置

Issue 可能会在 `ready-for-agent` 里待几天甚至几周，代码库期间会变化。写 brief 时要保证文件被重命名、移动或重构后仍然有用。

- **要**描述接口、类型和行为契约
- **要**写出 agent 需要查找或修改的具体类型、函数签名、配置结构
- **不要**引用文件路径，它们会过期
- **不要**引用行号
- **不要**假设当前实现结构不会变

### 描述行为，不写实现步骤

描述系统**应该做什么**，不是**怎么实现**。agent 会重新探索代码库，并自己决定实现方式。

- **好：** “`SkillConfig` 类型应接受可选的 `schedule` 字段，类型为 `CronExpression`”
- **坏：** “打开 src/types/skill.ts，在第 42 行加一个 schedule 字段”
- **好：** “用户不带参数运行 `/triage` 时，应看到需要处理的 issue 摘要”
- **坏：** “在主 handler 函数里加一个 switch”

### 完整的验收标准

Agent 需要知道什么时候算完成。每个 agent brief 都必须有具体、可测试的验收标准。每条标准都应能独立验证。

- **好：** “运行 `gh issue list --label needs-triage` 能返回已完成初步分类的 issue”
- **坏：** “triage 应正常工作”

### 明确边界

写清楚哪些内容不在范围内。这样可以防止 agent 过度打磨，或自行处理相邻功能。

## 模板

```markdown
## Agent Brief

**Category:** bug / enhancement
**Summary:** 一句话说明需要做什么

**Current behavior:**
描述当前行为。bug 时，这是错误行为；
enhancement 时，这是新功能要基于的现状。

**Desired behavior:**
agent 完成后系统应该是什么行为。
具体说明边界情况和错误条件。

**Key interfaces:**
- `TypeName`: 需要改什么，为什么
- `functionName()` 返回类型: 现在返回什么，应该返回什么
- Config shape: 需要新增哪些配置项

**Acceptance criteria:**
- [ ] 具体、可测试的标准 1
- [ ] 具体、可测试的标准 2
- [ ] 具体、可测试的标准 3

**Out of scope:**
- 这个 issue 不应改动或处理的内容
- 看似相关但实际独立的相邻功能
```

## 示例

### 好的 agent brief（bug）

```markdown
## Agent Brief

**Category:** bug
**Summary:** Skill description 截断在单词中间，输出 broken

**Current behavior:**
当 skill description 超过 1024 字符时，系统固定在第 1024 个字符处截断，
不考虑单词边界，导致描述在单词中间结束（例如 "Use when the user wants to confi"）。

**Desired behavior:**
截断应发生在 1024 字符之前最后一个单词边界，并追加 "..." 表示被截断。

**Key interfaces:**
- `SkillMetadata` 类型的 `description` 字段：类型不变，
  但填充它的校验/处理逻辑需要尊重单词边界
- 任何读取 SKILL.md frontmatter 并提取 description 的函数

**Acceptance criteria:**
- [ ] 1024 字符以下的描述不变
- [ ] 1024 字符以上的描述在最后一个单词边界处截断
- [ ] 截断后的描述以 "..." 结尾
- [ ] 包含 "..." 的总长度不超过 1024 字符

**Out of scope:**
- 修改 1024 字符上限本身
- 支持多行 description
```

### 好的 agent brief（enhancement）

```markdown
## Agent Brief

**Category:** enhancement
**Summary:** 增加 `.out-of-scope/` 目录，记录被拒绝的功能请求

**Current behavior:**
功能请求被拒绝时，issue 会被打上 `wontfix` 标签并关闭、加评论。
决策和理由没有持久记录。之后出现类似请求时，维护者只能回忆
或搜索历史讨论。

**Desired behavior:**
被拒绝的功能请求应记录在 `.out-of-scope/<concept>.md` 中，
包含决策、理由，以及所有请求过该功能的 issue 链接。
triage 新 issue 时，应检查这些文件是否匹配。

**Key interfaces:**
- `.out-of-scope/` 中的 Markdown 格式：每个文件包含 `# Concept Name`
  标题、`**Decision:**`、`**Reason:**`，以及带 issue 链接的
  `**Prior requests:**` 列表
- triage 工作流应尽早读取所有 `.out-of-scope/*.md`，
  并按概念相似度匹配新 issue

**Acceptance criteria:**
- [ ] 以 wontfix 关闭功能时，会创建或更新 `.out-of-scope/` 文件
- [ ] 文件包含决策、理由和被关闭 issue 的链接
- [ ] 已存在匹配的 `.out-of-scope/` 文件时，新 issue 追加到
      "Prior requests"，不重复建文件
- [ ] triage 时会检查现有 `.out-of-scope/` 文件；新 issue 命中旧拒绝时
      显示出来

**Out of scope:**
- 自动匹配（由人确认是否匹配）
- 重新打开之前拒绝过的功能
- Bug report（只有 enhancement 的拒绝进入 `.out-of-scope/`）
```

### 好的 agent brief（PR）

PR 场景下，"Current behavior" 描述的是 diff 的当前状态，brief 要求 agent 完成或修复它，而不是从零构建。

```markdown
## Agent Brief

**Category:** enhancement
**Summary:** 完成贡献者已实现的 `triage list --json` 输出参数

**Current behavior:**
这个 PR 增加了 `--json` 参数，把 issue 列表序列化成 JSON。
正常路径可用，diff 也符合项目命令结构。还剩两个缺口：
错误输出仍是人类可读文本（不是 JSON），新参数没有测试覆盖。

**Desired behavior:**
带 `--json` 时，所有输出（包括错误）都是 stdout 上格式合法的 JSON，
命令 exit code 不变。不带参数时，现有可读输出不变。

**Key interfaces:**
`--json` 下，命令错误路径应输出 `{ "error": string }`，
而不是纯文本错误。

**Acceptance criteria:**
- [ ] `triage list --json` 在成功和失败时都输出合法 JSON
- [ ] exit code 与非 JSON 命令一致
- [ ] 有测试覆盖 `--json` 的成功输出和一个错误场景
- [ ] 默认（非 JSON）输出逐字节不变

**Out of scope:**
- 给其他命令增加 `--json`
- 修改 PR 已定义的成功 payload JSON 结构
```

### 坏的 agent brief

```markdown
## Agent Brief

**Summary:** 修复 triage bug

**What to do:**
triage 那个东西坏了。看主文件修一下。
150 行附近的函数有问题。

**Files to change:**
- src/triage/handler.ts (line 150)
- src/types.ts (line 42)
```

它的问题是：

- 没有分类
- 描述模糊（“triage 那个东西坏了”）
- 引用了会过期的文件路径和行号
- 没有验收标准
- 没有范围边界
- 没有描述当前行为和期望行为的差异
