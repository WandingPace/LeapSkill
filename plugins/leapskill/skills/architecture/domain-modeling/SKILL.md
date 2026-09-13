---
name: domain-modeling
description: "Build and sharpen a project's domain model, ubiquitous language, and architectural decision records. Use when establishing codebase terminology, challenging fuzzy concepts, writing ADRs, or updating CONTEXT.md — even if the user says \"define our terms\". 用于用户要求统一定义领域术语、澄清模糊业务概念、写 ADR 或更新 CONTEXT.md 时。Do NOT use for general code refactoring without domain shifts."
---

# 领域建模

积极建立、强化和实施通用领域语言 (CONTEXT.md) 和架构决策记录 (docs/adr/*.md)，以防止代理和工程团队之间出现语义漂移。

---

## 核心不变量

1. **主动执行语义纪律**：主动挑战超载、模棱两可或口语化的术语，并实时将其与规范定义保持一致。
2. **立即内联术语表更新**：在领域术语具体化时将其捕获到“CONTEXT.md”中；切勿在会话结束时对术语表进行批量编辑。
3. **CONTEXT.md 必须完全不包含实现细节**：`CONTEXT.md`必须包含零实现细节、框架或数据库选择——它是一个纯领域字典。
4. **选择性 ADR 阈值**：仅当决策满足所有 3 个标准时才撰写 ADR：(1) 难以逆转，(2) 没有背景就令人惊讶，(3) 真正权衡的结果。
5. **代码库-术语表对齐**：与实时代码库实体交叉引用术语并立即标记差异。

---

## 架构和内容地图 (MOC)

```
[ Domain Discussions / User Prompts ] ──► [ Semantic Challenge & Disambiguation ] ──► [ Inline CONTEXT.md Update ]
                                                                 │
                                ┌────────────────────────────────┴────────────────────────────────┐
                                ▼                                                                 ▼
                     [ Domain Dictionary ]                                              [ Architectural Records ]
                     - Single-context: `CONTEXT.md`                                     - `docs/adr/NNNN-<slug>.md`
                     - Multi-context: `CONTEXT-MAP.md`                                  - Context, Decision, Consequences
```

|产物|责任|格式参考|
|---|---|---|
| **领域术语** |规范术语、实体边界、不变量 | `CONTEXT-FORMAT.md` |
| **架构决策记录** |不可逆转的架构选择和权衡| `ADR-FORMAT.md` |
| **上下文地图** |跨模块化存储库的有界上下文 | `CONTEXT-MAP.md` |

---

## 分步程序 (TWI)

### 第 1 步：检测上下文架构和词汇表基线
- **操作**：检查根 `CONTEXT-MAP.md` 是否存在（多上下文）或单个 `CONTEXT.md` / `docs/adr/`。
- **要点**：在第一个解析的术语上延迟创建术语表文件。
- **为什么**：多上下文系统需要按有界上下文划分域术语以防止冲突。

### 第 2 步：挑战模糊和超载的语言
- **行动**：拦截模糊名词（例如“帐户”、“项目”、“流程”）并提出不同的规范域实体。
- **关键点**：具有具体边缘情况场景的压力测试边界（例如，“部分取消期间会发生什么？”）。
- **为什么**：不明确的名词会导致数据库实体臃肿和业务逻辑错综复杂。

### 步骤 3：验证与现有代码库的一致性
- **操作**：在代码库中搜索实体名称并检查现有架构是否与用户的描述一致。
- **要点**：立即突出显示差异：“代码取消了整个订单，但您描述了部分取消。哪个是正确的？”
- **内嵌清单**：
  - [ ] 根据实时数据库/代码实体验证术语
  - [ ] 使用标准格式将定义添加到“CONTEXT.md”
  - [ ] 术语表中省略了实施细节

### 步骤 4：编写架构决策记录 (ADR)
- **操作**：对于满足 3 分阈值的决策，请创建 `docs/adr/NNNN-<slug>.md`。
- **关键点**：文档背景、决策、状态和后果。
- **为什么**：透明的 ADR 可以防止重复辩论并记录技术债务权衡。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“我将把数据库表模式添加到 CONTEXT.md 中。”* | **禁止。 CONTEXT.md 仅包含纯域术语。** |将域术语表与数据库模式耦合使其在迁移时过时。 |
| *“让我们为每个小选择（例如库助手）编写一个 ADR。”* | **强制执行 3 点 ADR 阈值。** |低价值的 ADR 会使文档变得混乱，并掩盖真正关键的架构选择。 |
| *“用户互换使用了‘用户’和‘客户’；我将忽略它。”* | **立即挑战并消除超载术语的歧义。** |合并不同的域概念会产生严重的授权和建模错误。 |
