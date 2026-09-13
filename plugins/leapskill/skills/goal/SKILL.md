---
name: goal
description: "Design and synthesize high-leverage autonomous goal prompts and contracts for unattended execution. Use when crafting a /goal prompt, planning an overnight autonomous coding run, converting rambling specifications into a self-contained agentic mission, or setting up multi-agent autonomous loops — even if they don't explicitly say \"goal prompt\". Do NOT use when the user asks for immediate single-turn execution in the current conversation without an autonomous goal contract."
---

# 自主目标和合约合成

将用户意图、模糊要求或杂乱的规范转化为特殊的、独立的“/目标”提示，为无人值守、自主多轮执行做好准备。

## 核心原则

> **自主目标提示指定目的地、质量栏和验证循环 - 绝不是微管理的分步脚本。**

---

## 核心不变量

1. **可观察的完成条件**：每个可交付成果必须拥有自主会话可以验证自身的具体完成状态（例如，测试套件通过、CLI 在装置上运行、构建输出存在）。
2. **前期授权和创作自由**：授予明确的权限以做出设计决策、选择内部工作流程并解决歧义，而无需打扰用户。
3. **已验证的资源清单**：仅列出已针对实时环境进行验证的 2-4 个工具或路径。与明确的发现授权相结合。
4. **强制多遍验证**：强制要求至少 3 次与目标介质匹配的不同迭代遍。
5. **最终目标线**：以一个包含可交付成果和自主指令的近期锚定句子结尾（“...是你的/目标。完全自主地工作，在完成之前不要向我询问任何事情。”）。

---

## 七部分目标提示剖析

```
┌──────────────────────────────────────────────────────────┐
│ 1. Core Desire & High-Stakes Context                     │
│ 2. Uncompromising Quality Bar & Principles               │
│ 3. Verified Resource Inventory & Discovery Mandate       │
│ 4. Explicit Decision Authority & Creative Freedom        │
│ 5. Medium-Matched Multi-Pass Verification Loop           │
│ 6. Concrete Delivery Destination                         │
│ 7. Terminal Goal Line & Autonomy Directive               │
└──────────────────────────────────────────────────────────┘
```

---

## 分步程序 (TWI)

### 第 1 步：提取意图并填补空白
- **行动**：提取可交付成果、范围、实际风险、提到的工具、质量标准和目标目的地。
- **要点**：针对较小的差距综合合理的默认值。如果歧义很严重，请提前解决。
- **为什么**：多轮来回击败了自治委托的速度优势。

### 第 2 步：验证资源并构建解剖结构
- **行动**：在命名路径和工具之前验证它们，然后将 7 个组件编织成自然流畅的散文（150-350 字）。
- **关键点**：明确说明结果和约束，同时明确授予代理自由来浏览内部实施步骤。
- **内嵌清单**：
  - [ ] 字数在 150–350 字以内
  - [ ] 根据实时存储库验证命名资源
  - [ ] 明确授予创作自由和决策权
  - [ ] 定义了特定于介质的验证通道（3 次迭代）
  - [ ] 明确的目标（链接、目录路径、文件工件）
  - [ ] 以最终目标线和自治指令结束

### 第 3 步：机械验证和交付
- **操作**：根据七个不变量验证起草的提示并在干净的代码块中输出。
- **要点**：提供准备复制粘贴的提示，零混乱。
- **为什么**：干净的交付可以防止执行过程中的格式和语法错误。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“我列出了分步说明，这样代理就不会迷路。”* | **指定目标，而不是微观管理步骤。** |微观管理会阻止代理适应不可预见的障碍。 |
| *“我凭记忆命名了几个工具，但没有检查它们是否存在。”* | **命名前验证所有资源。** |未经验证的资源会导致代理在搜索虚拟路径时浪费时间。 |
| *“该任务是主观的，因此不需要验证通过。”* | **每个交付成果都需要验证标准。** |未经验证的任务会导致过早完成和未发现的缺陷。 |
| *“我在球门线后添加了注释和解释。”* | **终点线必须是最后一句话。** |新近度偏差确保最终指令锚定模型的主要目标。 |
