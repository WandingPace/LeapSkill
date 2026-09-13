---
name: research
description: "Investigate a technical question against high-trust primary sources and capture findings as a cited Markdown note. Use when gathering API facts, reading documentation, verifying library capabilities, or delegating reading legwork — even if the user says \"look into this library\". Do NOT use for writing production feature code."
---

＃ 研究

根据权威的主要来源调查技术问题、库功能和架构事实，在引用的 Markdown 研究笔记中捕获可验证的发现。

---

## 核心不变量

1. **独家主要来源**：以官方文档、源代码、正式规范或第一方发行说明中的​​所有发现为依据；永远不要依赖未经验证的博客文章或二次摘要。
2. **强制归属和行级引用**：每个技术声明、API 签名或版本约束都必须直接链接到其主要源 URI 或存储库文件路径。
3. **后台代理执行**：在隔离的后台子代理中运行密集读取、抓取和存储库审核，以保留主代理的工作上下文。
4. **结构化决策 Markdown 输出**：将研究综合到匹配项目约定的永久 Markdown 文件中（例如 `docs/research/<slug>.md` 或 `.scratch/research/<slug>.md`）。
5. **事实与观点的分离**：将经过验证的架构事实与主观工程建议明确分开。

---

## 架构和内容地图 (MOC)

```
[ Technical Question / Library Query ] ──► [ Spawn Research Subagent ] ──► [ Primary Source Retrieval ] ──► [ Cited Synthesis Report ]
```

|组件|责任|输出目标|
|---|---|---|
| **主要来源审核员** |阅读官方文档、Github 存储库、规格 |网络搜索和 URL 内容工具 |
| **研究笔记** |带有引文和引文的结构化调查结果 | `docs/research/<主题>.md` |
| **验证门** |根据运行时/版本验证 API 签名 |直接测试片段|

---

## 分步程序 (TWI)

### 第 1 步：制定研究假设和边界
- **行动**：定义核心技术问题、必要的库版本和兼容性要求。
- **关键点**：区分硬技术限制（例如速率限制、内存占用）和人体工程学权衡。
- **为什么**：无限制的研究会导致过度的代币消费，而没有回答核心决策问题。

### 步骤2：查询权威的主要来源
- **操作**：使用搜索和 Web 工具获取主要文档、GitHub 存储库、RFC 和 API 参考。
- **要点**：验证项目的 `package.json`、`pyproject.toml` 或 `Cargo.toml` 的确切版本兼容性。
- **内嵌清单**：
  - [ ] 来源第一方/权威
  - [ ] 版本与项目环境匹配
  - [ ] 捕获准确的 API 签名和故障模式

### 步骤 3：作者引用的研究笔记
- **操作**：将综合写入 `docs/research/<slug>.md` （或项目标准路径）：
- **摘要**：高层裁决和建议方向。
- **主要发现**：带有直接降价链接的具体技术事实。
- **代码示例**：最小的、经过验证的使用示例。
- **权衡和陷阱**：边缘情况、性能瓶颈和限制。
- **为什么**：永久研究笔记保留机构背景并防止跨工程周期重复研究。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“我记得这个库是如何根据训练数据工作的，因此无需查找当前文档。”* | **所有图书馆事实的强制主要来源查找。** |训练记忆会产生已弃用的 API 签名的幻觉，并错过最近的重大更改。 |
| *“从第三方教程或论坛帖子中总结。”* | **将声明追溯到权威的主要来源。** |第三方教程经常传播反模式和过时的解决方法。 |
| *“将完整的研究文本内联到聊天中，无需编写文件。”* | **始终将发现提交到持久的研究报告中。** |聊天中的发现在上下文重置后消失； Markdown 文件提供持久性文档。 |

