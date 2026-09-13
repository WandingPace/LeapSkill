---
name: improve-codebase-architecture
description: "Survey codebases for shallow modules, weak seams, and deepening opportunities, producing a visual report. Use when conducting architectural reviews, identifying design debt, finding deepening opportunities, or preparing codebase refactors — even if the user says \"analyze our architecture\"; 中文用户常会要求“分析代码库架构”“梳理模块边界”或“找出设计债务”并生成重构建议报告。Do NOT use for basic syntax linting or formatting."
---

# 改进代码库架构

调查代码库中的浅层模块、抽象漏洞和薄弱接缝，在操作系统临时目录中生成交互式可视化 HTML 报告，其中包含架构重构之前/之后的模型。

---

## 核心不变量

1. **YAGNI 范围优先**：优先考虑最近提交历史记录（`git log --oneline`）中的热点，其中架构摩擦正在积极减慢开发速度。
2. **严格的设计词汇**：使用规范术语（**模块**、**接口**、**深度**、**接缝**、**适配器**、**杠杆**、**局部性**）和来自`CONTEXT.md`的领域词汇来构建所有发现。
3. **外部临时报告**：使用 Tailwind CDN 和 Mermaid 图将可视化报告写入操作系统临时目录 (`<tmpdir>/architecture-review-<timestamp>.html`)；切勿在存储库中乱扔评论 HTML。
4. **前/后视觉模型**：每个深化候选者都必须具有清晰的前/后结构图，说明界面简化和实现深度。
5. **无推测接口提议**：提出候选问题领域和深化方向；在用户选择候选者之前，不要提出具体的代码接口。

---

## 架构和内容地图 (MOC)

```
[ Hotspot & Git Log Analysis ] ──► [ Deepening Candidate Survey ] ──► [ Generate HTML Report in /tmp ] ──► [ Grilling on Chosen Candidate ]
```

|组件|责任|参考|
|---|---|---|
| **热点扫描仪** |识别经常更改、高摩擦的文件 | Git 日志和子代理探索 |
| **HTML 可视化报告** |并排渲染 Mermaid 和 Tailwind 卡 ​​| `HTML-REPORT.md` |
| **候选方案深化** |对选定候选方案的苏格拉底式审查| `skills/grilling/SKILL.md` + `skills/codebase-design/SKILL.md` |

---

## 分步程序 (TWI)

### 第 1 步：扫描最近的代码库热点
- **操作**：检查“git log --oneline -n 100”和“CONTEXT.md”以识别高流失率模块和域边界。
- **要点**：专注于理解一个概念需要在多个碎片文件之间跳转的模块。
- **为什么**：与活动热点相比，深化稳定、未受影响的遗留文件的投资回报率较低。

### 第 2 步：调查深化机会
- **操作**：使用删除测试评估候选模块并定位浅层传递。
- **关键点**：检查提取的纯函数是否缺乏局部性和泄漏调用者的状态。
- **内嵌清单**：
  - [ ] 从 git churn 识别的热点文件
  - [ ] 制定了 2-4 个不同的深化候选方案
  - [ ] 按推荐强度分类的候选者（“强”、“值得探索”、“推测”）

### 步骤 3：生成独立的可视化 HTML 报告
- **操作**：使用 Tailwind 和 Mermaid CDN 脚本编写 `<tmpdir>/architecture-review-<timestamp>.html`。
- **要点**：包括问题描述、杠杆/局部性优势以及Mermaid图之前/之后的并排。
- **为什么**：视觉架构图比文字墙更有效地传达结构改进。

### 第 4 步：打开报告并促进候选方案选择
- **操作**：通过 `open <path>` (macOS) / `xdg-open` (Linux) / `start` (Windows) 启动 HTML 报告，并询问用户要探索哪个候选。
- **要点**：选择后，进入拷问循环以解决模块边界并更新“CONTEXT.md”/ADR。
- **为什么**：协作候选方案选择可确保团队在投资重构之前获得支持。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“将 HTML 审核报告直接写入存储库根目录。”* | **将报告专门写入操作系统临时目录。** |评审工件永远不应该污染项目 Git 历史记录。 |
| *“立即在报告中起草完整的替换代码文件。”* | **首先呈现架构方向和图表。** |在就架构接缝达成一致之前过早编码会导致浪费精力。 |
| *“在没有有力证据的情况下重新启动已解决的 ADR 决定。”* | **尊重现有的 ADR，除非出现严重摩擦。** |对既定决定不断重新提起诉讼会阻碍进展。 |
