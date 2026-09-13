---
name: grill-with-docs
description: "Interview the user to stress-test a design while simultaneously recording domain terms and architectural decisions in project documentation. Use when planning features in a codebase and wanting domain terms captured in CONTEXT.md and ADRs — even if the user says \"grill this feature\". Do NOT use when no codebase context or documentation trail is needed."
---

# 与文档一起烧烤

进行结构化苏格拉底式设计访谈，同时提取领域术语并将其提交到“CONTEXT.md”中，并将难以逆转的架构决策提交到架构决策记录（“docs/adr/*.md”）中。

---

## 核心不变量

1. **同步文档蒸馏**：随着决策的确定，将普遍存在的领域语言提取并记录到“CONTEXT.md”中，并将架构选择实时记录到 ADR 中。
2. **批量前沿问题**：以结构化批次形式呈现独立的前沿问题，并具有明确的默认值，而不是一次性查询。
3. **自主事实侦察**：在提出设计问题之前，自主研究现有的代码库架构、类型和模式。
4. **轻量级 ADR 触发器**：当设计选择造成重大技术债务或难以逆转时（例如数据库选择、同步策略），请立即编写专用 ADR。
5. **零推测性散文**：仅记录面试期间已积极解决的决定；保持草稿笔记的清晰划分。

---

## 架构和内容地图 (MOC)

```
[ User Feature Idea ] ──► [ Codebase Recon & ADR Review ] ──► [ Socratic Grilling Rounds ]
                                                                       │
                                      ┌────────────────────────────────┴────────────────────────────────┐
                                      ▼                                                                 ▼
                            [ Update CONTEXT.md ]                                              [ Author ADR Docs ]
                            - Ubiquitous language                                              - Context & Decision
                            - Entity definitions                                               - Consequences & Tradeoffs
```

|神器|目的|参考格式|
|---|---|---|
| **领域词典** |捕获普遍存在的语言和实体关系 | `技能/领域建模/CONTEXT-FORMAT.md` |
| **建筑实录** |记录不可逆的架构选择 | `技能/域建模/ADR-FORMAT.md` |
| **烧烤协议** |推动结构化前沿问题轮次| `技能/烧烤/SKILL.md` |

---

## 分步程序 (TWI)

### 第 1 步：发现现有文档基线
- **操作**：检查存储库中现有的“CONTEXT.md”、“GLOSSARY.md”和“docs/adr/”记录。
- **关键点**：采用现有的项目约定进行领域建模和决策记录。
- **为什么**：保持架构一致性可以防止重复的术语和分散的记录。

### 步骤 2：进行苏格拉底式拷问
- **行动**：确定未解决的要求并制定带有建议默认值的编号问题轮次。
- **关键点**：询问边界、不变量、实体生命周期和故障恢复。
- **内嵌清单**：
  - [ ] 根据现有域词典审查术语
  - [ ] 问题的格式和明确的建议
  - [ ] 强调架构权衡

### 步骤 3：提取和更新域术语表
- **行动**：随着术语和实体的澄清，使用标准格式更新或创建“CONTEXT.md”。
- **要点**：确保术语严格定义且范围明确。
- **为什么**：共享的通用语言可以防止工程师和代理之间的不一致。

### 步骤 4：编写架构决策记录 (ADR)
- **操作**：对于重要的架构选择，请在“docs/adr/NNNN-<slug>.md”中编写新的编号 ADR。
- **关键点**：包括背景、决策、状态和后果（积极和消极）。
- **为什么**：ADR 保留机构记忆并防止重复过去的辩论。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“整个采访结束后我会写文档。”* | **在决策确定时记录条款和 ADR。** |事后文档通常会忽略微妙的细微差别、权衡和理由。 |
| *“此架构选择很小，不需要 ADR。”* | **如果难以逆转，请撰写 ADR。** |看似次要的选择往往会导致重大的技术债务。 |
| *“我会要求用户解释现有的域模型。”* | **自主阅读现有文档和架构。** |在吸引用户之前，代理必须从存储库工件构建初始上下文。 |

