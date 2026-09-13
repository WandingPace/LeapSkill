---
name: resolving-merge-conflicts
description: "Resolve in-progress git merge or rebase conflicts by intent traced to primary sources. Use when hit with merge conflicts, CONFLICT markers in files, rebase pauses, or when git prompts to resolve conflicted hunks — even if the user just says \"fix this merge\". 中文用户常在说“解决合并冲突”“处理 rebase 冲突”或“帮我修一下这些 CONFLICT 标记”时请求此技能。 Do NOT use for creating new branches or routine rebasing without conflicts."
---

# 解决合并冲突

通过识别两个分支的语义意图并使用自动化测试门验证集成完整性，系统地解决正在进行的 Git 合并和变基冲突。

---

## 核心不变量

1. **三向意图重构**：在更改冲突代码之前了解共同的合并基础祖先、传入更改（“THEIRS”）和目标分支更改（“OURS”）。
2. **永远不要盲目选择我们的或他们的**：单独检查每个冲突块；综合保留两个分支功能需求的解决方案。
3. **零孤立冲突标记**：验证所有“<<<<<<<”、“=======”和“>>>>>>>”标记在暂存之前已完全消除。
4. **非破坏性解决**：保留相邻的未更改的代码、注释和文档字符串；避免冲突块之外的意外行删除。
5. **强制解决后测试通过**：在结束合并（`git commit`）或变基（`git rebase --continue`）之前执行完整的构建、类型检查和测试套件。

---

## 架构和内容地图 (MOC)

```
[ Merge/Rebase Conflict Detected ] ──► [ Identify 3-Way Merge Base & Commits ] ──► [ Hunk-by-Hunk Semantic Synthesis ] ──► [ Build & Test Gate ]
```

|相|责任|验证命令 |
|---|---|---|
| **冲突发现** |识别所有未合并的文件 | `git status --porcelain | grep "^UU\|^AA\|^DU\|^UD"` |
| **验祖** |查看冲突文件的基本版本 | `git show :1:<file>` (基础), `:2:<file>` (我们的), `:3:<file>` (他们的) |
| **整合门** |运行编译器、linter 和单元测试 |项目构建/测试命令|

---

## 分步程序 (TWI)

### 第 1 步：识别冲突文件并合并上下文
- **操作**：运行 `git status` 枚举所有冲突文件并检查两个分支上的最新提交日志：
````bash
git log --oneline -n 5 HEAD
git log --oneline -n 5 MERGE_HEAD # 或 REBASE_HEAD
````
- **关键点**：确定每个分支试图提供哪些功能或错误修复。
- **为什么**：了解开发人员的意图可以防止避免做出语法有效但语义破碎的合并结果。

### 步骤 2：从语义上解决冲突块
- **操作**：打开每个冲突文件，分析“HEAD”（我们的）和传入的（他们的）之间的差异，并重写块以满足这两个要求。
- **要点**：如果两个分支都添加了新的导入、依赖项或路由，请将它们干净地组合起来，不要重复。
- **内嵌清单**：
  - [ ] 所有冲突标记（`<<<`、`===`、`>>>`）已删除
  - [ ] 重复导入和导出去重
  - [ ] 保留了两个分支的新功能

### 步骤 3：使用构建和测试套件进行验证
- **操作**：跨已解析的工作树运行存储库的类型检查器、linter 和测试套件。
- **关键点**：如果测试失败，请调查解决冲突是否破坏了微妙的运行时假设。
- **为什么**：许多合并冲突可以干净地编译，但会引入仅测试捕获的逻辑回归。

### 第 4 步：暂存并完成合并/变基
- **操作**：暂存已解析的文件（`git add <files>`）并完成操作：
- 对于合并：`git commit`（保留标准合并提交消息）。
- 对于变基：`git rebase --continue`。
- **要点**：检查`git status`以确保工作树是干净的。
- **为什么**：清晰的结论确保上游 CI 管道可以在无需人工干预的情况下构建合并分支。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“使用‘git checkout --ours’完全接受‘我们的’或‘他们的’，这样会更快。”* | **禁止语义冲突。** |一揽子检查会覆盖有效的工作并从一个分支恢复关键的错误修复。 |
| *“删除失败的测试以使合并提交通过。”* | **修复代码以使测试通过。** |删除测试会降低覆盖率并在生产中引入回归。 |
| *“假设代码没有问题，无需运行完整的测试套件。”* | **提交合并之前必须通过强制测试。** |手动解决冲突经常会引入语法错误和损坏的导入。 |
