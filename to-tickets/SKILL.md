---
name: to-tickets
description: "Decompose an approved specification or plan into ordered, dependency-linked tracer-bullet implementation tickets. Use when turning a spec or architectural plan into actionable tracker issues with clear acceptance criteria — even if the user says \"break this into tickets\". Do NOT use for initial requirements gathering."
---

# 前往门票

将批准的规范、计划或设计文档分解为垂直切片、按依赖性排序的跟踪项目符号实施票，并具有明确的验收标准。

---

## 核心不变量

1. **严格的垂直跟踪器切片**：每个标准票必须垂直切割所有必要的层（架构、域逻辑、API、UI、测试），而不是单个层的水平切片。
2. **显式依赖 DAG**：每个票据必须显式声明其阻塞先决条件（“阻塞者：”）以形成明确的有向无环图。
3. **单一上下文窗口大小调整**：每张票证的大小必须调整为在单个代理上下文窗口内完成，而不会耗尽令牌或工具限制。
4. **广泛重构的扩展契约**：具有广泛爆炸半径的广泛架构重构必须遵循扩展契约模式，而不是被迫进入脆弱的单步垂直切片。
5. **无父级突变**：在创作和发布子票证时，切勿关闭、解决或损坏父级跟踪器问题。

---

## 架构和内容地图 (MOC)

```
[ Approved Spec / Plan ] ──► [ DAG Dependency Decomposition ] ──► [ User Granularity Review ] ──► [ Atomic Tracker Publication ]
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼                                                         ▼
    [ Vertical Tracer Bullets ]                               [ Expand-Contract Migrations ]
    - Narrow cross-layer path                                 - Expand (add new form beside old)
    - Independently verifiable                                - Migrate in localized batches
    - Fit in 1 context window                                 - Contract (delete old form)
```

|组件|责任|输出目标|
|---|---|---|
| **当地票务店** |原子 Markdown 票证文件 | `.scratch/<feature-slug>/issues/NN-<slug>.md` |
| **追踪器问题** |使用阻止元数据进行远程问题创建 | GitHub、Linear、GitLab 问题 |
| **预分解门** |在进行简单的改变之前先让改变变得容易|专用拦截票 #01 |

---

## 分步程序 (TWI)

### 第 1 步：上下文摄取和预分解识别
- **行动**：获取批准的规范并检查目标代码库区域以确定必要的预分解。
- **要点**：如果现有代码使目标更改变得困难，请创建专用的准备重构票作为第一个阻止者。
- **为什么**：“让更改变得简单，然后进行简单的更改”可以防止架构清理与功能添加交织在一起。

### 第 2 步：垂直追踪子弹切片并制定 DAG
- **操作**：将功能分解为垂直跟踪器切片和链接依赖项：
- 对于标准功能：垂直切片切入架构、API、UI 和测试。
- 对于广泛的重构：按扩展 $\rightarrow$ 批量迁移 $\rightarrow$ 合同的顺序进行。
- **要点**：为每张票证分配一个明确的“阻止者”列表。没有阻塞的票证可以立即执行。
- **内嵌清单**：
  - [ ] 每个垂直切片都提供独立可验证的行为
  - [ ] 通过扩展契约进行广泛的重构
  - [ ] 票证严格适合单个新上下文窗口
  - [ ] 验收标准是二元的且可测试的

### 第 3 步：呈现细分和测验用户以供批准
- **操作**：向用户展示建议的票证、标题、阻止程序和可交付成果。
- **要点**：提示用户验证粒度、依赖性和顺序。
- **为什么**：快速人工验证可确保票据大小与团队速度相匹配并避免执行障碍。

### 第 4 步：发布到 Tracker
- **操作**：按拓扑顺序（首先阻止者）将批准的票证发布到配置的问题跟踪器或“.scratch/<feature-slug>/issues/NN-<slug>.md”。
- **要点**：将“准备好代理”分类标签应用于所有未阻止的工单。
- **为什么**：拓扑创建确保下游工单可以清晰地引用实时上游工单 ID。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“我将创建水平票据：1 个用于数据库，1 个用于后端，1 个用于 UI。”* | **禁止。强制执行垂直示踪切片。** |水平层无法进行端到端验证，导致系统在提交时被破坏。 |
| *“这张票很大，但一个代理人可以管理它。”* | **分割票证超过 1 个上下文窗口。** |过大的票据会导致上下文耗尽、需求丢失和幻觉。 |
| *“将准备性重构与新功能逻辑相结合。”* | **将预分解分离到一个不同的票证中。** |将重构与功能交付混合在一起会掩盖代码审查中的回归。 |
| *“跳过编写验收标准，因为规范中有它们。”* | **每张票的强制性原子验收清单。** |实施者代理需要独立的验证标准，而无需重新阅读规范。 |

