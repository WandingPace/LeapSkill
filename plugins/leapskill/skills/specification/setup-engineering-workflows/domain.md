# 领域文档

工程 skill 探索代码库时，应按以下方式消费这个仓库的领域文档。

## 探索前先读这些

- 仓库根目录的 **`CONTEXT.md`**
- 如果存在根目录 **`CONTEXT-MAP.md`**，它会指向每个上下文的 `CONTEXT.md`；读取与当前主题相关的那些
- **`docs/adr/`**：读取会影响你即将工作区域的 ADR。多上下文仓库还要检查 `src/<context>/docs/adr/` 里的上下文级决策

这些文件不存在时，**静默继续**。不要提示缺失，也不要一开始就建议创建。`/domain-modeling` skill（可通过 `/grill-with-docs` 和 `/improve-codebase-architecture` 到达）会在术语或决策真正被确定时按需创建它们。

## 文件结构

单上下文仓库（多数仓库）：

```text
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文仓库（根目录存在 `CONTEXT-MAP.md`）：

```text
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← 上下文专属决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用术语表词汇

当你的输出需要命名领域概念（issue 标题、重构提案、假设、测试名）时，使用 `CONTEXT.md` 里的定义。不要漂移到术语表明确要求避免的同义词。

如果你需要的概念还不在术语表里，这是一个信号：要么你在发明项目不用的语言（重新考虑），要么存在真实缺口（记录给 `/domain-modeling`）。

## 标记 ADR 冲突

如果你的输出和现有 ADR 矛盾，显式说出来，不要悄悄覆盖：

> _与 ADR-0007（event-sourced orders）冲突，但值得重新讨论，因为…_
