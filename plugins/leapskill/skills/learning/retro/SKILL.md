---
name: retro
description: "Conduct a retrospective on a coding session to systematically improve agent environment, navigation pointers, automated checks, coding standards, tool economy, or AGENTS.md instructions. Use when reflecting on completed work, auditing agent mistakes, or optimizing repository rules — even if the user says \"run a retro\"; 中文用户常会要求“做个复盘”“总结这次会话”“审计代理错误”或“优化仓库规则”。Do NOT use during active mid-task implementation."
---

# 复盘

对过去的代理编码会话进行系统的、基于证据的回顾，以改进存储库导航指针、自动化 lint/类型检查、审阅者标准和代理指令的易用性与可维护性。

---

## 核心不变量

1. **上下文压力分离**：将实施代理（高上下文压力；需要最少的引导和导航指针）与审核代理（低上下文压力；执行深度编码标准）区分开来。
2. **将规则推向金字塔**：只要有可能，将指令转换为自动编译器/linter 检查 $\rightarrow$ 审阅者规则 $\rightarrow$ 文档 $\rightarrow$ 仅作为最后的手段 `AGENTS.md`。
3. **无效指令修剪**：主动审核并消除`AGENTS.md`和`CLAUDE.md`中的非操作或冗余指令。
4. **工具经济分析**：识别并简化token 消耗过高的 MCP 工具调用或大文件负载读取。
5. **按严重程度排名的建议**：提出可操作的改进候选方案，严格按照对代理可靠性和token 效率的影响排序。

---

## 架构和内容地图 (MOC)

```
[ Session Logs & Past Mistakes ]
                │
                ▼
┌───────────────────────────────────────┐
│ 1. 6-Category Retrospective Audit     │
│    (Nav, Checks, Standards, Steering, │
│     Tooling, Info Access)             │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│ 2. Rule Hierarchy Placement           │ ──► Auto-Check > Reviewer Rule > Doc Pointer > AGENTS.md
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│ 3. Severity-Ranked Action Items       │ ──► Concrete diffs to configs, linters, or standards
└───────────────────────────────────────┘
```

|审核类别|评测重点|整治行动|
|---|---|---|
| **导航** |搜索文件所花费的时间 |在 `docs/` 中添加简洁的导航指针 |
| **自动检查** |可预防的语法/类型/路径错误 |添加 linter 规则、Husky 钩子、TypeScript 严格性 |
| **编码标准** |错过架构指南 |将规则添加到“CODING_STANDARDS.md”（在审核期间阅读）|
| **指令卫生** |笨重的 `AGENTS.md` / `CLAUDE.md` |修剪无效指令、精简说明文字、把规则下放到子文档 |
| **工具经济** |昂贵/冗余的工具调用|缓存结果、范围搜索、优化 grep 模式 |
| **信息访问** |缺少日志或凭据 |提供只读日志或环境变量 |

---

## 分步程序 (TWI)

### 第 1 步：提取会话日志和主要来源
- **操作**：读取指定会话（或当前会话）的记录日志并识别摩擦点、错误转弯和重复失败。
- **要点**：所有批评都基于可观察的事件，而不是一般建议。
- **为什么**：复盘必须基于实际执行中观察到的开发者和智能体摩擦。

### 第 2 步：针对 6 个改进类别进行审核
- **操作**：评估理想情况下应该在哪里捕获故障（例如自动检查与审阅者与提示指针）。
- **内嵌清单**：
  - [ ] 这个错误可以被 linter 或编译器标志捕获吗？
  - [ ] 这是否属于审核代理的“CODING_STANDARDS.md”？
  - [ ] `AGENTS.md` 文件是否精简（$<100$ 行）并且不含无效指令？

### 步骤 3：提出按严重程度排序的行动项目
- **操作**：使用具体文件差异和命令行指令格式化建议。
- **要点**：清楚地解释每个提议的规则变更的权衡。
- **为什么**：具体的提案允许维护者通过一次确认来接受改进。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“针对遇到的每个错误，向 AGENTS.md 添加 50 行指令。”* | **将规则下放到自动检查或审查文档。** |重载“AGENTS.md”每次都会使上下文窗口膨胀并降低推理能力。 |
| *“在实施者提示上施加严格的编码标准规则。”* | **将编码标准放入“CODING_STANDARDS.md”中以供审核。** |实现者需要上下文空间来进行推理、调试和文件探索。 |
| *“保留无操作指令，因为它们听起来不错。”* | **修剪所有不能明显引导模型行为的指令。** |无效指令会消耗 token，并削弱对关键不变量的关注。 |
