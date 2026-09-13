---
name: implement-spec
description: "Execute a full specification across task tickets using isolated subagent branches into a unified PR. Use when a specification with associated task-graph tickets is ready to implement across multiple subagents or isolated worktrees, and the goal is a complete pull request on a single branch — even if the user says \"build the whole spec\". 用于用户要求按完整规格和任务图拆分给子代理或工作树并行实施，并最终合并成一个 PR 时。Do NOT use for single isolated bug fixes or exploratory coding without tickets."
---

# 按规格实施

跨隔离的子代理分支协调已批准的规范及其 DAG 任务图的并行实施，最终形成一个统一的、经过code-review的拉取请求。

---

## 核心不变量

1. **DAG 可执行边界并发**：实施者子代理专门处理未阻塞的前沿工单；对应工单合并完成后，新解锁的工单会立即可以开始。
2. **严格的工作树隔离**：每个实施者子代理都在自己专用的、隔离的 Git 工作树和分支中执行，以防止文件冲突。
3. **仅上下文指针**：严格通过上下文指针（规范路径、工单 ID、ADR）与子代理进行通信；避免倾倒巨大的文字墙。
4. **专用合并验证**：将已完成的工作树分支合并到主 PR 分支由具有完整测试套件验证的合并子代理处理。
5. **统一code-review质量门**：在将其标记为可供人工审查之前，在统一的 PR 分支中运行“code-review”，并在最后一次修复所有发现的问题。

---

## 架构和内容地图 (MOC)

```
[ Approved Spec & DAG Tickets ] ──► [ Create PR Branch ] ──► [ Parallel Worktree Subagents ]
                                                                       │
                                      ┌────────────────────────────────┴────────────────────────────────┐
                                      ▼                                                                 ▼
                            [ Ticket #01 Worktree ]                                           [ Ticket #02 Worktree ]
                            - Isolated branch                                                 - Isolated branch
                            - Red/Green TDD cycle                                             - Red/Green TDD cycle
                                      │                                                                 │
                                      └────────────────────────────────┬────────────────────────────────┘
                                                                       ▼
                                                       [ Merge & Verify on PR Branch ]
                                                                       │
                                                                       ▼
                                                       [ Code Review & Worktree Cleanup ]
```

|角色 |责任|执行模式|
|---|---|---|
| **勘探代理** |预读外部文档和共享架构 |后台子代理（`research`）|
| **实施者代理** |在隔离的工作树内执行单票 |并行子代理（`implement`）|
| **合并代理** |将功能分支合并到 PR 分支并验证测试 |串行集成流程|
| **审查门** |在最终 PR 分支上运行两轴code-review | `code-review/SKILL.md` |

---

## 分步程序 (TWI)

### 第 1 步：提取任务图并初始化 PR 分支
- **行动**：阅读技术规格和相关工单，计算初始可执行边界。
- **要点**：创建专用 PR 分支 (`feat/<spec-slug>`) 并草拟链接所有目标工单的拉取请求。
- **为什么**：预先链接工单可确保自动状态跟踪和可追溯性。

### 步骤 2：调度并行实施者子代理
- **操作**：对当前可执行边界上的每张工单，在隔离的工作树（`.worktrees/<ticket-slug>`）中生成一个实施者子代理。
- **关键点**：将上下文指针传递给规范和工单，而无需重复指令。
- **内嵌清单**：
  - [ ] 与主存储库工作区隔离的工作树
  - [ ] 实施者遵循严格的 TDD 红绿循环
  - [ ] 每个实施者都处理一个分配的工单

### 第 3 步：合并已完成的工单和 Advance Frontier
- **操作**：当实现者完成时，将其分支合并到 PR 分支，运行测试套件，并删除工作树。
- **关键点**：重新计算任务图边界以立即启动新的解锁工单。
- **为什么**：持续合并可以使集成差异较小并尽早发现冲突。

### 步骤 4：运行两轴code-review和清理
- **操作**：合并所有工单后，在“feat/<spec-slug>”上运行“code-review”。
- **要点**：在将 PR 标记为可供人工审核之前，修复所有标准和规范结果。
- **为什么**：全面的合并前审查可保证生产级架构和完整的规范合规性。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“在同一共享工作树中运行所有实施者。”* | **每个子代理强制隔离 git 工作树。** |共享工作区会导致文件锁争用、覆盖和 git 索引损坏。 |
| *“由于所有单元测试都已通过，因此跳过code-review。”* | **最后 PR 分支上的强制两轴code-review。** |通过测试不会发现架构坏味道、福勒反模式或遗漏的规范条款。 |
| *“在其依赖项合并之前实施阻止的工单。”* | **严格遵守 DAG 可执行边界。** |过早地实施阻塞工单会导致大规模的合并冲突和返工。 |
