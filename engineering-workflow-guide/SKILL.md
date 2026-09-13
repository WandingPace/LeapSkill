---
name: engineering-workflow-guide
description: "Route engineering, AI/ML, cognitive, or productivity tasks to the narrowest effective specialist skill. Use when a task spans planning, implementation, debugging, review, architecture, research, setup, AI modeling, data remediation, or autonomous goals, when the user asks what to do next, or when unsure which workflow fits — even if they don't explicitly name a skill. Do NOT use when the specific specialist skill is already obvious and unambiguous."
---

# 工程工作流程指南

集中分析任务，对开发人员意图进行分类，并将工程工作流程路由到精选技能目录中范围最窄、杠杆率最高的专业技能。

---

## 核心不变量

1. **最窄有效技能**：选择完全涵盖任务的最具体技能；当存在专门的工具时，避免调用广泛的、仪式性的元技能。
2. **每阶段一项主要技能**：为本回合指定一项主要专长技能；仅跨不同的生命周期门链接辅助技能（例如规划$\rightarrow$实施$\rightarrow$审查）。
3. **没有未打包的幽灵技能**：每个路由技能都必须逐字存在于`references/catalog.md`中，并且具有已建立的`SKILL.md`。
4. **快速路径用户覆盖**：如果用户通过名称明确请求有效技能，请立即兑现，无需多余的路由审议。
5. **设置先决条件检查**：如果未配置存储库问题跟踪、分类标签或域文档，请在规划或分类之前运行“setup-engineering-workflows”。

---

## 架构和内容地图 (MOC)

```
[ Developer Intent / Request ]
                │
                ▼
┌────────────────────────────────────────────────────────┐
│ 1. Intent Classification & Catalog Lookup               │
│    (Match job against `references/catalog.md`)          │
└──────────────────────────┬─────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
[ Discovery & Plan ]   [ Code & Architecture ]   [ AI, ML & Automation ]
- `grill-with-docs`    - `implement`             - `ai-engineering`
- `to-spec`            - `code-review`           - `ai-data-remediation`
- `to-tickets`         - `diagnosing-bugs`       - `ml-best-practices`
- `wayfinder`          - `domain-modeling`       - `j-space`
- `prototype`          - `setup-ts-deep-modules` - `goal`
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Lifecycle Route Execution                           │
│    (State route briefly, invoke primary skill)         │
└────────────────────────────────────────────────────────┘
```

|路由器参考|责任|文件位置 |
|---|---|---|
| **技能目录** |所有 42 个打包技能的详尽索引 | [参考文献/catalog.md](参考文献/catalog.md) |
| **ChatGPT 路由合约** |运行时消耗和抗幻觉协议| [参考文献/chatgpt-routing-contract.md](参考文献/chatgpt-routing-contract.md) |
| **路由矩阵** | 100 多个意图模式、触发器和排除项 | [参考文献/路由矩阵.md](参考文献/路由矩阵.md) |
| **相界** | `/clear`、`/compact`、`/handoff` 和子代理的决策树 | [相边界.md](相边界.md) |

|生命周期场景 |规范路由管道 |
|---|---|
| **模糊绿地特征** | `grill-with-docs` $\rightarrow$ `to-spec` $\rightarrow$ `to-tickets` $\rightarrow$ `实现` |
| **硬错误或回归** | `诊断错误` $\rightarrow$ `tdd` |
| **拉取请求审查** | “代码审查”（两轴：标准和规范）|
| **深度模块重组** | `改进代码库架构` $\rightarrow$ `setup-ts-deep-modules` |
| **大型多会话地图** | `wayfinder` $\rightarrow$ `to-spec` $\rightarrow$ `to-tickets` |
| **深度多步骤推理** | `j-space`（认知寄存器和接缝审核）|
| **自主无人值守目标** | `目标`（7 部分即时合同）|
| **生产 ML / LLM 系统** | `人工智能工程` $\rightarrow$ `机器学习最佳实践` |
| **自我修复数据管道** | `ai-数据修复` |
| **长篇写作和散文** | `写作片段` $\rightarrow$ `写作形状` / `写作节拍` |

---

## 分步程序 (TWI)

### 第 1 步：提取请求并查阅目录
- **行动**：阅读 `references/catalog.md` 并对用户的潜在意图进行分类，而不仅仅是原始关键字。
- **要点**：检查存储库设置是否完成（`docs/agents/issue-tracker.md`）。
- **为什么**：准确的意图分类可确保代理在需求未定义时不会跳入代码。

### 第 2 步：制定最窄路线
- **行动**：选择单一主要专业技能并用 1-2 行陈述多阶段路线图。
- **内嵌清单**：
  - [ ] 在 `references/catalog.md` 中验证目标技能
  - [ ] 调用零重叠元技能
  - [ ] 不同的生命周期阶段清晰分离

### 步骤 3：执行初级阶段
- **动作**：调用选定的技能指令并直接执行。
- **为什么**：直接转换消除了对话开销。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“一次简单的改变即可调用 4 种技能。”* | **每个生命周期阶段强制执行 1 项主要技能。** |重叠的技能提示会产生相互冲突的指令并浪费上下文预算。 |
| *“发明一个不在目录中的新自定义工作流程名称。”* | **专门路由到“catalog.md”中的打包技能。** |路由到不存在的技能会导致执行失败。 |
| *“否决用户的显式技能调用。”* | **尊重用户要求的技能，除非存在严重冲突。** |尊重开发人员的意图和运营自主权。 |

