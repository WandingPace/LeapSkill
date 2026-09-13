---
name: triage
description: "Classify, verify, and prepare external bug reports and feature requests into agent-ready briefs. Use when processing incoming issues, validating bug reproductions, rejecting out-of-scope requests, or structuring contributor tickets — even if the user says \"triage these issues\". 中文用户常在说“分诊这些 issue”“验证这个 bug 报告”或“整理成给 agent 的简报”时请求此技能。 Do NOT use for internal tickets already produced by to-tickets."
---

# Issue 分诊

对传入问题和外部拉取请求进行分类，根据代码重现错误报告，拒绝对“.out-of-scope/”的超出范围的请求，并合成持久的、高上下文的代理简报。

---

## 核心不变量

1. **强制免责声明**：在分类过程中创建的每个评论或问题都必须以“> *这是由 AI 在分类过程中生成的。*”开头。
2. **类别和状态正交性**：每个分类问题必须恰好具有一个类别（“bug”、“增强”）和一个状态（“needs-triage”、“needs-info”、“ready-for-agent”、“ready-for-human”、“wontfix”）。
3. **简报之前的重现**：在升级为“ready-for-agent”之前，根据代码库测试和重现步骤验证错误声明。
4. **超出范围的知识库**：被拒绝的增强请求必须以明确的理由编入“.out-of-scope/<slug>.md”，以防止重复进行重新分类。
5. **冗余筛选**：在对功能请求进行分类之前，在代码库中搜索现有实现；如果已经实施，请以解释结束。

---

## 架构和内容地图 (MOC)

```
[ Incoming Issue / External PR ]
                │
                ▼
┌───────────────────────────────────────┐
│ 1. Redundancy & Out-of-Scope Check    │ ──► Search code & `.out-of-scope/*.md`
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│ 2. Reproduction & Verification Pass   │ ──► Verify bug or test PR diff locally
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│ 3. Socratic Grilling & State Decision │ ──► Settle terms, update `CONTEXT.md`
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│ 4. Outcome Publication                │ ──► Post Agent Brief or Out-of-Scope Record
└───────────────────────────────────────┘
```

|组件|责任|参考格式|
|---|---|---|
| **代理简介** | 无人值守代理的独立说明 | `AGENT-BRIEF.md` |
| **超出范围知识库** |被拒绝提案的持久存储| `OUT-OF-SCOPE.md` |
| **分类状态机** |规范角色和状态转换 | `docs/agents/triage-labels.md` |

---

## 分步程序 (TWI)

###第一步：查询需要注意的问题
- **操作**：查询跟踪器以查找未标记的问题、“needs-triage”问题和“needs-info”问题以及新的记者活动。
- **要点**：配置为请求表面时包括外部 PR。
- **为什么**：将维护者的注意力集中在需要分类干预的可操作项目上。

### 第 2 步：屏幕冗余和先前拒绝
- **操作**：搜索代码库中的现有功能并检查“.out-of-scope/*.md”是否有先前的拒绝。
- **关键点**：如果请求的行为已经存在，则关闭为直接指向实现的“wontfix”。
- **为什么**：防止重复的功能实现和浪费的工程周期。

### 第 3 步：重现声明并制定建议
- **操作**：尝试重现错误报告或检查外部 PR 差异以运行测试套件。
- **要点**：如果由于缺少细节而导致无法复现，请转到“needs-info”并提出具体问题。
- **内嵌清单**：
  - [ ] 尝试在本地环境中重现错误
  - [ ] 已识别的相关代码路径和潜在根本原因
  - [ ] 向维护者提交的类别和状态建议

### 第 4 步：应用状态并交付代理简介
- **操作**：应用维护者批准的状态：
- “ready-for-agent”：带有复制命令和建议接缝的后结构化代理简介。
- `needs-info`：发布标记记者的特定问题块。
- `wontfix`（增强）：在`.out-of-scope/`中记录并关闭问题。
- **为什么**：高保真代理简介使下游自主代理能够在无需人工干预的情况下实施修复。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“将错误提升为“ready-for-agent”而不重现它。”* | **复现通过后才能交给代理。** |未经验证的错误报告会让下游代理陷入徒劳无功的境地。 |
| *“在简短评论中拒绝某个功能而不对其进行记录。”* | **在“.out-of-scope/”中记录拒绝的增强功能。** |无记录的拒绝会导致重复地重新评估同一请求。 |
| *“向记者提出模糊的问题，例如‘请提供更多详细信息’。”* | **在“needs-info”中提出具体的、可操作的问题。** |模糊的问题会延迟解决并使外部贡献者感到沮丧。 |
