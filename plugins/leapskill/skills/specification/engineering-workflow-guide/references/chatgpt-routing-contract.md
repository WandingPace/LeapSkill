# ChatGPT & Codex Skill 路由合同

这份文档规定 ChatGPT 和 Codex 消费、执行和切换 `matt-skills-curated` 插件包中 skills 时的权威运行时协议。

---

## 1. ChatGPT 消费协议

用户与 ChatGPT / Codex 交互时，遵循严格的 4 步执行生命周期：

```text
[ User Request ] ──► [ Step 1: Route & Select Primary Skill ]
                                  │
                                  ▼
                     [ Step 2: Ingest SKILL.md Core Invariants ]
                                  │
                                  ▼
                     [ Step 3: Execute Phase Procedures (TWI) ]
                                  │
                                  ▼
                     [ Step 4: Phase Handshake & Next Route ]
```

### Step 1: 路由并只选择一个主 skill

- **Action**：根据 `references/catalog.md` 和 `references/routing-matrix.md` 匹配用户意图。
- **Constraint**：为当前轮指定**一个**主 specialist skill。
- **Rule**：同一阶段不要同时调用多个 skill。

### Step 2: 读取 `SKILL.md` 和核心不变量

- **Action**：完整读取目标 skill 的 `SKILL.md`。
- **Constraint**：立刻内化 **Core Invariants** 和 **Anti-Rationalization Guardrails**。
- **Rule**：未确认前置条件和 public seam 之前，不要直接进入代码执行。

### Step 3: 执行分步流程（TWI）

- **Action**：遵循 Training Within Industry（TWI）步骤：**Action**、**Key Point**、**Why**。
- **Constraint**：在每个 seam 处遵守内联风险检查表（`- [ ]`）。
- **Rule**：交付干净、面向人的结果，不要倾倒内部思考碎片。

### Step 4: 阶段握手和下一跳

- **Action**：每个阶段以可检查的完成边界结束，并宣布生命周期中的下一阶段。
- **Example**：完成 `grill-with-docs` 后，宣布切换到 `to-spec`。

---

## 2. 标准多阶段生命周期

| 场景 | 标准多阶段管线 | 阶段切换触发 |
|---|---|---|
| **Greenfield Feature** | `grill-with-docs` ➔ `to-spec` ➔ `to-tickets` ➔ `implement` ➔ `code-review` | 用户批准规格和工单图 |
| **Bug / Regression** | `diagnosing-bugs` ➔ `tdd` ➔ `code-review` | 红灯失败已复现，最小 repro 已隔离 |
| **Wide Refactoring** | `improve-codebase-architecture` ➔ `setup-ts-deep-modules` ➔ `code-review` | 可视化架构报告已批准 |
| **AI / ML Initiative** | `ai-engineering` ➔ `ml-best-practices` ➔ `code-review` | 超过 naive baseline，95% CI 已验证 |
| **Massive Initiative** | `wayfinder` ➔ `to-spec` ➔ `to-tickets` ➔ `implement-spec` | 迷雾清除，frontier 工单已认领 |
| **Long-Form Essay** | `writing-fragments` ➔ `writing-shape` ➔ `writing-beats` | 原始材料已整理，候选开头已选定 |

---

## 3. ChatGPT 防 Hallucination 护栏

1. **没有幻影 skill**：绝不发明 `references/catalog.md` 里不存在的 skill 名称。
2. **不扩 scope**：严格实现已批准规格要求的内容。
3. **不盲目批准**：需求缺失或矛盾时停下，用 `grill-me` 或 `to-questionnaire` 澄清。
4. **零 secret 泄漏**：绝不回显私有 API key、token 或环境变量密码。
