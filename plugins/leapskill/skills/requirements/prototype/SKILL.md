---
name: prototype
description: "Build a throwaway prototype to answer a specific design, state model, or UI exploration question. Use when evaluating whether an interface feels right, exploring UI concepts, or testing logic before committing to a full spec — even if the user says \"mock this up\"; 中文用户常会要求“做个原型”“先 mock 一个界面”或“快速验证方案”。Do NOT use for production implementation."
---

# 原型

构建一次性探索性代码，旨在快速回答单个承载架构、状态机或 UI 问题，而无需产生生产开销。

---

## 核心不变量

1. **构造一次性**：原型必须明确标记为一次性，生产持久性或抽象开销为零。
2. **分支隔离**：将逻辑/状态机原型 (`LOGIC.md`) 与可视化 UI 变体探索 (`UI.md`) 分开。
3. **单命令启动**：UI 原型使用​​一个命令运行（`pnpm dev`、`bun run ...`）；逻辑原型是单个可双击的 HTML/JS 文件。
4. **透明状态暴露**：每个操作或转换都必须直观地暴露完整的底层状态负载。
5. **Decisions-Only Mainline Merge**：仅将经过验证的决策/类型合并到主线中；将原型代码提交到单独的临时分支。

---

## 架构和内容地图 (MOC)

```
[ Load-Bearing Design Question ] ──► [ Select Exploration Branch ] ──► [ Minimal Runnable Prototype ] ──► [ Extract Settled Decision ]
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
             [ Logic / State Prototype ]                         [ UI Variant Explorer ]
             - Single HTML/JS file                               - Multi-variant route
             - Free-play + guided tabs                           - Bottom floating bar
             - Full state visualizer                             - URL parameter toggle
```

|分支|问题已解答 |工件格式 |
|---|---|---|
| **逻辑/状态** | “这个状态机或业务规则感觉正确吗？” | `LOGIC.md` |
| **用户界面变化** | “这种视觉交互应该是什么样子？” | `UI.md` |

---

## 分步程序 (TWI)

### 第 1 步：确定问题和探索分支
- **行动**：确定核心不确定性是逻辑/状态的还是视觉/经验的。
- **要点**：检查组件是否具有复杂的过渡状态（选择逻辑）或样式/布局决策（选择 UI）。
- **为什么**：选择错误的格式会浪费时间为逻辑边缘情况构建 UI 或为静态布局构建状态机。

### 步骤 2：实现最小可运行原型
- **操作**：创建具有零数据库持久性和最少抽象的原型：
- 逻辑：带有状态按钮、转换日志和引导演练场景的独立 HTML。
- UI：专用的草稿路线，通过查询参数切换 2-4 个完全不同的变体。
- **内嵌清单**：
  - [ ] 在文件名和注释中标记为一次性
  - [ ] 通过单个标准命令或浏览器单击启动
  - [ ] 显示每次交互的实时内部状态

### 步骤 3：交互式评估和决策提取
- **操作**：引导用户完成原型以评估边缘情况并记录结论。
- **关键点**：将经过验证的数据形状、状态机缩减器或组件布局提取到问题跟踪器或规范中。
- **为什么**：捕获精炼的发现可以防止一次性原型代码意外地演变成生产意大利面条。

### 第 4 步：存档原型并清理主程序
- **操作**：将原型提交到临时分支（`prototype/<name>`），将其链接到工单中，并保持 `main` 干净。
- **关键点**：永远不要将未检查的原型黑客直接合并到主分支中。
- **为什么**：严格的分离使主要代码库保持原始状态，同时保留历史设计背景。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“让我们直接在主生产文件中构建这个原型。”* | **禁止。将原型保留在隔离的暂存路径中。** |将原型内联到生产代码中会产生意外的依赖性和技术债务。 |
| *“向原型添加完整的单元测试和错误处理。”* | **跳过一次性原型中的生产强化。** |强化探索性代码会减慢学习周期并产生情感依恋。 |
| *“将整个原型合并到 main 中，因为它可以工作。”* | **仅摘录决定；存档原型分支。** |原型缺乏生产安全、验证、错误边界和文档。 |
