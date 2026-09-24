---
name: teach
description: "Teach a technical concept interactively using the workspace as an active learning lab with durable learning records. Use when the user asks to understand a codebase concept, learn a language feature, explore design patterns, or practice coding skills — even if they say \"explain how this works to me\". 中文用户常在说“给我讲讲这段代码怎么工作”“教我这个设计模式”或“带我做几个练习”时请求此技能。 Do NOT use for silent autonomous code generation."
---

# 教学

将当前项目转变为交互式、有状态的学习实验室，生成结构化 HTML 课程、参考资料、主要来源参考书目和渐进式学习记录。

**输出位置**：每个学习主题使用独立目录 `Docs/Teach/<topic-slug>/`。先确定当前项目根目录（Git 仓库取仓库根，否则取当前工作区根），再将所有课程、参考表、术语表、资源和学习记录写入该主题目录。不要把教学产物散落到项目根目录、skill 安装目录或用户目录。

---

## 核心不变量

1. **基于任务的课程**：每节课、测验和练习都必须直接锚定“Docs/Teach/<topic-slug>/MISSION.md”（学习者明确的现实世界目标）。
2. **理想的难度和检索**：通过努力检索、间隔练习和交错练习，而不是瞬间流畅，以达到长期存储强度的目标。
3. **精美的 HTML 产物**：课程在“Docs/Teach/<topic-slug>/lessons/000X-<name>.html”中呈现为独立的出版级 HTML 文档，并通过共享资源 (“Docs/Teach/<topic-slug>/assets/style.css”) 设置样式。
4. **持久的学习记录**：在“Docs/Teach/<topic-slug>/learning-records/000X-<name>.md”中捕获关键见解、非明显突破和心智模式转变，以维护最近发展区 (ZPD)。
5. **基于主要来源**：切勿纯粹依赖模型记忆；引用并链接“Docs/Teach/<topic-slug>/RESOURCES.md”中经过验证的主要来源和内联课程注释。

---

## 架构和内容地图 (MOC)

```
[ Learner Request / Mission ] ──► [ Assess ZPD via Learning Records ] ──► [ Build HTML Lesson & Quizzes ] ──► [ Record Progress in Learning Records ]
```

|组件|责任|文件位置/模板|
|---|---|---|
| **任务锚** |核心动机和现实目标| `Docs/Teach/<topic-slug>/MISSION.md` ([MISSION-FORMAT.md](MISSION-FORMAT.md)) |
| **课程工件** |交互式 HTML 课程模块 | `Docs/Teach/<topic-slug>/lessons/000X-<slug>.html` |
| **参考表** |备忘单、语法摘要和术语表 | `Docs/Teach/<topic-slug>/reference/*.html` |
| **学习记录** |里程碑式的反思和概念性的突破| `Docs/Teach/<topic-slug>/learning-records/000X-<slug>.md` |
| **共享资产** |版式、样式和交互式测验小部件 | `Docs/Teach/<topic-slug>/assets/*` |
| **主要来源** |经过审查的文档和书籍参考文献| `Docs/Teach/<topic-slug>/RESOURCES.md`（[RESOURCES-FORMAT.md](RESOURCES-FORMAT.md)） |

---

## 分步程序 (TWI)

### 第 1 步：建立使命并评估最近发展区
- **操作**：确定项目根目录和 `Docs/Teach/<topic-slug>/` 主题目录，然后检查其中的 `MISSION.md` 和现有 `learning-records/`。如果未初始化，请询问用户以确定他们的动机和起始基线。
- **要点**：围绕用户需要“做什么”而不是抽象理论进行框架教学。
- **为什么**：如果立足于立即应用，学习会明显更快、更持久。

### 第 2 步：来源主要参考文献
- **行动**：识别并记录 `Docs/Teach/<topic-slug>/RESOURCES.md` 中最重要的主要源文档或权威文章。
- **要点**：确保声明和代码模式符合现代最佳实践。
- **为什么**：引用主要来源可以建立用户信任并培养研究习惯。

### 第 3 步：编写交互式 HTML 课程
- **操作**：在主题目录内生成链接到 `assets/style.css` 的 `lessons/000X-<slug>.html`，并把共享样式写入 `assets/style.css`。
- **要点**：包括交互式自检问题、代码片段和参考表的直接链接。
- **内嵌清单**：
  - [ ] 独立 HTML 在浏览器中清晰打开
  - [ ] 采用平衡字数/字符数格式化的测验答案
  - [ ] 包括后续讨论提示

### 第四步：记录学习记录的突破
- **行动**：用户与课程互动后，在 `Docs/Teach/<topic-slug>/learning-records/000X-<slug>.md` 中捕获掌握的关键概念和下一步练习的领域。
- **为什么**：在不同的会话中保持学习状态同步。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“将 2000 字的解释直接转储到聊天中。”* | **将学习内容打包到模块化 HTML 课程和参考文件中。** |聊天文字滚动消失；结构化文件提供了持久的个人图书馆。 |
| *“给出简单的多项选择题和明显的答案。”* | **实施平衡、高摩擦的检索练习。** |显而易见的答案会造成错误的流畅性，而无法建立长期记忆。 |
| *“在不检查主题目录中的 `MISSION.md` 的情况下进行教学。”* | **每节课的强制性任务调整。** |脱节的理论会导致学习者脱离并快速遗忘。 |
| *“把课程文件写到项目根目录，之后再整理。”* | **所有主题产物统一写入 `Docs/Teach/<topic-slug>/`。** |固定的主题目录让课程可检索、可重复访问，也不会污染项目源码树。 |
