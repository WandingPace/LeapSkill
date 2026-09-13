---
name: code-review
description: "Review changed code against repository coding standards and original specification intent. Use when reviewing a branch, diff, PR, pull request, merge-base changes, or verifying code against documented standards — even if the user just says \"review this\". Do NOT use for authoring new code or diagnosing failing runtime bugs."
---

# 代码审查

对“HEAD”和固定点之间的差异进行两轴回顾：
1. **标准**：代码是否符合记录的存储库标准和干净的架构气味？
2. **规范**：代码是否忠实且完整地实现了原始问题/规范，而没有范围蔓延？

两个轴都作为独立的并行子代理执行，以防止上下文污染，并并排报告结果。

---

## 核心不变量

1. **严格的两轴分离**：将标准和规范结果分开；切勿将它们合并或交叉排列成混合乐谱。
2. **固定合并基础差异**：始终使用 `git rev-parse` 解析引用并查看 `git diff <fixed-point>...HEAD`。
3. **基于证据的引用**：每个发现都必须引用确切的文件、行范围和违反的标准/规范条款。
4. **工具不重复**：跳过自动预提交工具已经捕获的格式、语法或 lint 错误。
5. **无盲目批准**：如果缺少规范，请明确报告“未提供规范 - 仅根据标准进行验证”。

---

## 架构和内容地图 (MOC)

```
[ Pin Fixed Point ] ──► [ Identify Spec & Standards ] ──► [ Parallel Review Subagents ] ──► [ Side-by-Side Synthesis ]
                                                                 │
                                ┌────────────────────────────────┴────────────────────────────────┐
                                ▼                                                                 ▼
                     [ Standards Subagent ]                                              [ Spec Subagent ]
                     - Documented repo rules                                             - Missing requirements
                     - Fowler code smells                                                - Unasked scope creep
                     - Architectural boundaries                                          - Flawed implementations
```

|组件|责任|评测来源|
|---|---|---|
| **标准轴** |建筑气味、命名、凝聚力 | `CODING_STANDARDS.md`、`CONTRIBUTING.md`、气味基线 |
| **规格轴** |功能完整性、范围边界 |问题描述、`specs/*.md`、用户需求 |
| **聚合** |并列平衡报告|按轴分类的逐字调查结果 |

---

## 分步程序 (TWI)

### 第 1 步：固定固定点和差异
- **操作**：解析基本引用并确认非空差异（`git diff <base>...HEAD`）。
- **要点**：如果引用无效或工作树为空，则快速失败。
- **为什么**：根据不正确的基础进行审查会比较不相关的更改。

### 步骤 2：提取标准和规格来源
- **操作**：找到存储库指南（`CODING_STANDARDS.md`）和原始要求/问题。
- **关键点**：为标准代理配备 Fowler 气味基线（神秘名称、重复代码、功能嫉妒、原始痴迷、推测普遍性）。
- **内嵌清单**：
  - [ ] 差异碱基已确认
  - [ ] 确定的标准文档
  - [ ] 提取的规范/问题要求

### 第 3 步：调度并行子代理
- **操作**：同时生成标准子代理和规格子代理以及专用提示。
- **要点**：将每个子代理限制在其指定域（每个报告 < 400 字）。
- **为什么**：将标准和规范评估合并到一个通道中会导致光环偏差，其中干净的代码掩盖了缺失的功能。

### 步骤 4：汇总和综合报告
- **行动**：在“## Standards”和“## Spec”标题下展示调查结果以及可操作的补救建议。
- **关键点**：清楚地说明每个轴内最严重的问题。
- **为什么**：明确的优先级可以帮助作者首先解决关键的设计问题。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“代码看起来格式很漂亮，所以它一定是正确的。”* | **标准通过 $\neq$ 规格通过。** |优雅的代码可能完全无法实现所需的业务逻辑。 |
| *“它按照票证的要求进行操作，因此请忽略杂乱的架构。”* | **规格通过 $\neq$ 标准通过。** |绕过标准的快速黑客行为会产生严重的技术债务。 |
| *“将两条评论合并为一个综合分数。”* | **严格的两轴分离。** |混合分数会掩盖哪个维度需要修复。 |
| *“指出评论中的小缩进问题。”* | **跳过自动 linter 处理的问题。** |手动审查应侧重于语义、架构和意图。 |
