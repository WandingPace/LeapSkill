# Issue tracker: Local Markdown

这个仓库的 issue 和规格保存在 `.scratch/` 下的 Markdown 文件中。

## 约定

- 一个 feature 一个目录：`.scratch/<feature-slug>/`
- 规格文件：`.scratch/<feature-slug>/spec.md`
- 实施工单一文件一票：`.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 开始编号；不要合并成单个 tickets 文件
- Triage 状态记录在每个 issue 文件顶部附近的 `Status:` 行（角色字符串见 `triage-labels.md`）
- 评论和对话历史追加到文件底部 `## Comments` 标题下

## 当 skill 说“发布到 issue tracker”

在 `.scratch/<feature-slug>/` 下创建新文件（需要时创建目录）。

## 当 skill 说“读取相关工单”

读取被引用路径的文件。用户通常会直接给路径或 issue 编号。

## Wayfinding 操作

供 `/wayfinder` 使用。**map** 是一个文件，每个 **child** 文件是一张工单。

- **Map**：`.scratch/<effort>/map.md`（正文包含 Notes / Decisions-so-far / Fog）。
- **Child ticket**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 编号，正文写问题。`Type:` 行记录工单类型（`research`/`prototype`/`grilling`/`task`）；`Status:` 行记录 `claimed`/`resolved`。
- **Blocking**：顶部附近的 `Blocked by: NN, NN` 行。列出的每个文件都是 `resolved` 后，ticket 才解锁。
- **Frontier**：扫描 `.scratch/<effort>/issues/`，找 open、unblocked 且未 claimed 的文件；编号最小者胜出。
- **Claim**：任何工作开始前，先设置 `Status: claimed` 并保存。
- **Resolve**：在 `## Answer` 标题下追加答案，设置 `Status: resolved`，然后把上下文指针（gist + 链接）追加到 `map.md` 的 Decisions-so-far。
