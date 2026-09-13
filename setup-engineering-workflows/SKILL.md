---
name: setup-engineering-workflows
description: "Configure repository issue-tracking, triage-label, domain-doc, and agent-instruction conventions. Use when initializing engineering workflows in a repo, configuring GitHub/GitLab issue labels, or establishing CONTEXT.md conventions — even if the user says \"setup our workflows\". Do NOT use for general project package installs."
---

# 设置工程工作流程

配置和标准化存储库问题跟踪、分类标签词汇、域建模架构 (`docs/agents/domain.md`) 和代理指令 (`AGENTS.md` / `CLAUDE.md`)。

---

## 核心不变量

1. **提示驱动的探索**：在提出更改建议之前检查现有的远程、目录和标签；不要盲目覆盖现有的跟踪器设置。
2. **单上下文与多上下文谨慎**：默认为单上下文（根目录下的`CONTEXT.md`）；仅在检测到 monorepo 信号（工作区、“packages/*”）时建议多上下文（“CONTEXT-MAP.md”）。
3. **保留代理指令文件**：如果`CLAUDE.md`或`AGENTS.md`存在，则就地编辑；如果两者都不存在，请在创建之前询问用户。切勿同时创建两者。
4. **条件分类配置**：如果存储库中存在“分类”技能，则仅配置分类标签文件（“docs/agents/triage-labels.md”）。
5. **持久工作区文档**：将所有配置的决策保留到 `docs/agents/issue-tracker.md`、`docs/agents/domain.md` 和 `docs/agents/triage-labels.md` 中。

---

## 架构和内容地图 (MOC)

```
[ Codebase Inspection (Remotes, Monorepos) ] ──► [ Interactive Setup Sections A/B/C ] ──► [ Update AGENTS.md / docs/agents/ ]
```

|组件|责任|种子模板|
|---|---|---|
| **问题跟踪器配置** | GitHub (`gh`)、GitLab (`glab`) 或本地 Markdown | `技能/setup-engineering-workflows/issue-tracker-github.md` |
| **分类词汇** |映射到存储库标签的 5 个规范角色 | `技能/设置工程工作流程/分类标签.md` |
| **域文档布局** |单上下文与多上下文约定 | `技能/setup-engineering-workflows/domain.md` |

---

## 分步程序 (TWI)

### 第 1 步：自主存储库探索
- **操作**：检查 `git remote -v`、根指令文件（`AGENTS.md`、`CLAUDE.md`）、`docs/adr/` 和工作区配置（`pnpm-workspace.yaml`、`packages/`）。
- **关键点**：确定存储库是否已有跟踪器或分类约定。
- **为什么**：避免重新询问用户 git 和配置文件中已经明显的事实。

### 步骤 2：配置问题跟踪器和分类标签
- **行动**：逐节提出建议：
- **A 部分（跟踪器）**：GitHub (`gh`)、GitLab (`glab`) 或本地 Markdown (`.scratch/`)。
- **B 部分（标签）**：规范角色（`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for human`、`wontfix`）。
- **C 部分（领域）**：单上下文与多上下文。
- **内嵌清单**：
  - [ ] Tracker 已确认并记录在“docs/agents/issue-tracker.md”中
  - [ ] 在“docs/agents/triage-labels.md”中映射的分类标签
  - [ ] 写入“docs/agents/domain.md”的域文档规则

### 步骤 3：将指令发送至 AGENTS.md / CLAUDE.md
- **操作**：添加或更新“AGENTS.md”（或“CLAUDE.md”）内的“## Agent Skills”块：
  ```markdown
## 代理技巧
  
### 问题跟踪器
[问题跟踪摘要]。请参阅“docs/agents/issue-tracker.md”。
  
### 域文档
[单一或多上下文]。请参阅“docs/agents/domain.md”。
  ```
- **为什么**：上下文指针确保新生成的子代理立即读取存储库约定。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“创建 AGENTS.md 和 CLAUDE.md 以实现最大覆盖范围。”* | **禁止。只维护一份规范代理文件。** |多个指令文件会导致配置漂移和规则冲突。 |
| *“在单包存储库上强制使用多上下文。”* | **默认为单上下文，除非 monorepo 存在。** |不必要的多上下文结构会产生过多的目录嵌套。 |
| *“无需询问即可覆盖现有的自定义问题标签。”* | **将现有存储库标签映射到规范角色。** |覆盖现有团队标签会破坏活动的项目板和工作流程。 |

