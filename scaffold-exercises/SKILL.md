---
name: scaffold-exercises
description: "Scaffold course, workshop, or tutorial exercises following repository conventions. Use when creating exercise folders, problem/solution/explainer variants, numbered lesson files, or workshop boilerplate — even if the user says \"add a new exercise\". Do NOT use for routine application feature scaffolding."
---

# 脚手架练习

支架标准化教育练习目录、问题/解决方案/解释器变体子文件夹以及严格通过存储库 linter 规则的样板 TypeScript 模块。

---

## 核心不变量

1. **严格的破折号数字层次结构**：
- 节文件夹：`exercises/XX-section-name/`（2 位零填充数字）。
- 练习文件夹：`exercises/XX-section-name/XX.YY-exercise-name/`（section.exercise 格式）。
2. **强制变体子文件夹**：每个练习必须至少包含“问题/”、“解决方案/”或“解释器/”之一（存根默认为“解释器/”）。
3. **非空自述文件标准**：每个变体文件夹必须包含一个非空的“readme.md”，其中包含干净的“# Title”、描述和零损坏的链接。
4. **Git 感知移动**：在重新编号或重组现有练习以保留提交历史记录时，始终使用“git mv”而不是原始文件系统重命名。
5. **强制 CLI Lint Gate**：在结束脚手架步骤之前执行并验证“pnpm ai-hero-cli 内部 lint”。

---

## 架构和内容地图 (MOC)

```
[ Curriculum Plan / Outline ] ──► [ Generate Numbered Directories ] ──► [ Scaffold Variant Subfolders ] ──► [ Lint & Commit Gate ]
```

|变体文件夹 |学生目的|所需文件 |
|---|---|---|
| `问题/` |带有“// TODO:”标记的活跃学生工作区 | `readme.md`、`main.ts` |
| `解决方案/` |完整的参考实现 | `readme.md`、`main.ts` |
| `解释器/` |无代码任务的概念深入探讨 | `自述文件.md` |

---

## 分步程序 (TWI)

### 第 1 步：解析课程计划和计算层次结构
- **操作**：从提供的大纲中提取章节名称、练习标题和所需的变体类型。
- **要点**：制定正确的 2 位数字前缀（`01`、`02`、`01.01`、`01.02`）。
- **为什么**：一致的编号可确保练习在 CLI 和 UI 中按正确的时间顺序显示。

### 步骤 2：脚手架目录树和变体文件
- **操作**：创建文件夹 (`mkdir -p`) 并使用标题和描述填充 `readme.md` 存根。
- **要点**：如果涉及到代码执行，则生成一个非空的`main.ts`。
- **内嵌清单**：
  - [ ] 严格执行短划线大小写目录命名
  - [ ] 在每个变体子文件夹中创建非空“readme.md”
  - [ ] 未引入禁止的“.gitkeep”或“speaker-notes.md”文件

### 步骤 3：运行内部 Linter 并修复问题
- **操作**：执行`pnpm ai-hero-cli inside lint`来验证练习结构。
- **要点**：迭代任何报告的损坏链接或丢失文件，直到 linter 完全通过。
- **为什么**：预提交 linting 可以防止破坏课程构建和自动化跑步者安全带。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“重新编号练习时使用原始`mv`。”* | **所有重命名和移动都必须使用“git mv”。** |原始的举动打破了 Git 的指责，并使 PR 评论中的差异变得不可读。 |
| *“在练习文件夹中创建空的`.gitkeep`文件。”* | **禁止。填充有意义的“readme.md”存根。** | Linter 规则禁止练习包中包含“.gitkeep”文件。 |
| *“跳过在存根上运行 `pnpm ai-hero-cli 内部 lint`。”* | **强制性绿色短绒验证。** |缺少标题标题或无效的子文件夹名称会破坏下游测试运行程序。 |

