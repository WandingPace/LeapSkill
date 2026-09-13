# HTML 报告格式

架构 review 渲染成一个自包含 HTML 文件，放在系统临时目录。Tailwind 和 Mermaid 都来自 CDN。Mermaid 负责图结构依赖；手写 div 和 inline SVG 负责更编辑化的视觉（mass diagram、cross-section）。两者混用：不要所有图都靠 Mermaid，否则很快会变得模板化。

## 脚手架

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{{repo name}} 架构 review</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* Tailwind 不方便覆盖的小自定义层：
         虚线 seam、手绘感箭头等 */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

仓库名、日期，以及一个紧凑图例：实线框 = module，虚线 = seam，红色箭头 = leakage，粗黑框 = deep module。不要介绍段落，直接进入候选对象。

## 候选卡片

图承担主要表达。文字稀疏、朴素，并直接使用 `/codebase-design` skill 的术语，不做额外解释。

每个候选对象是一个 `<article>`：

- **标题**：短，直接命名深化动作（例如“合并 Order intake 管线”）。
- **Badge 行**：推荐强度（`Strong` = emerald，`Worth exploring` = amber，`Speculative` = slate），加上依赖分类标签（`in-process`、`local-substitutable`、`ports & adapters`、`mock`）。
- **文件**：等宽字体列表，`font-mono text-sm`。
- **Before / After 图**：核心内容。两列并排。见下方图形模式。
- **问题**：一句话。哪里痛。
- **方案**：一句话。改变什么。
- **收益**：bullet，每条不超过 6 个词。例如“测试只打一个 interface”、“Pricing 不再泄漏”、“删除 4 个浅 wrapper”。
- **ADR 提示**（如适用）：琥珀色框里一行。

不要解释性长段落。如果图需要一段话才能理解，就重画图。

## 图形模式

按候选对象选择合适模式，并混用。不要每张图都长一样，多样性本身就是目的。

### Mermaid graph（依赖 / 调用流的主力）

当重点是“X 调 Y，Y 调 Z，看看这团乱”时，用 Mermaid `flowchart` 或 `graph`。包在 Tailwind 卡片里，避免显得突兀。用 `classDef` 把泄漏边标红，把 deep module 标黑。时序图适合表达“before：6 次往返；after：1 次”。

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### 手写 boxes-and-arrows（当 Mermaid 布局不听话）

module 用带边框和标签的 `<div>`，箭头用绝对定位在 relative 容器上的 inline SVG `<line>` 或 `<path>`。当你想让 after 图呈现“一个粗边框 deep module，内部灰化”的效果时用这种；Mermaid 画不出正确的视觉重量。

### Cross-section（适合分层浅）

堆叠水平条带（`h-12 border-l-4`）展示一次调用穿过的层。Before：6 个薄层，每层几乎不做事。After：1 个厚条带，写明合并后的职责。

### Mass diagram（适合“接口和实现一样宽”）

每个 module 画两个矩形：一个代表 interface 表面积，一个代表 implementation。Before：interface 矩形几乎和 implementation 一样高（浅）。After：interface 矩形变矮，implementation 矩形变高（深）。

### Call-graph collapse

Before：嵌套盒子组成的函数调用树。After：同一棵树折叠成一个盒子，现在内部的调用在盒子里淡化显示。

## 风格指导

- 偏编辑设计，不做企业 dashboard。留白要足。标题可用 serif（`font-serif` 与 stone/slate 搭配不错）。
- 颜色克制：一个主色（emerald 或 indigo），红色只给 leakage，amber 只给警告。
- 图高约 320px，让 before/after 能并排舒适展示，不需要滚动。
- 图内 module 标签用 `text-xs uppercase tracking-wider`，看起来像示意图而不是 UI。
- 脚本只有 Tailwind CDN 和 Mermaid ESM import。报告其余部分静态：无应用代码，除 Mermaid 自身渲染外无交互。

## 首选推荐章节

一张更大的卡片。候选名、一句为什么、锚链接到它的卡片。仅此而已。

## 语气

朴素、简洁，但架构名词和动词直接来自 `/codebase-design` skill。简洁不是漂移术语的理由。

**必须使用：** module、interface、implementation、depth、deep、shallow、seam、adapter、leverage、locality。

**不要替换：** component、service、unit（代替 module）；API、signature（代替 interface）；boundary（代替 seam）；layer、wrapper（当你想说的是 module）。

**符合风格的表述：**

- “Order intake module 是浅的：interface 几乎和 implementation 一样宽。”
- “Pricing 跨 seam 泄漏。”
- “深化：一个 interface，一个测试位置。”
- “两个 adapter 证明这个 seam：生产 HTTP，测试内存。”

**收益 bullet** 要用术语表词汇命名收益：*“locality：bug 集中在一个 module”*、*“leverage：一个 interface，N 个调用点”*、*“interface 收窄，implementation 吸收 wrapper”*。不要写 *“更容易维护”* 或 *“代码更干净”*，这些词不在术语表里，配不上位置。

不 hedge，不铺垫，不写“值得注意的是”。如果一句话能变 bullet，就变 bullet；如果 bullet 能删，就删。如果一个词不在 `/codebase-design` 术语表里，先找表里的词，再考虑发明新词。
