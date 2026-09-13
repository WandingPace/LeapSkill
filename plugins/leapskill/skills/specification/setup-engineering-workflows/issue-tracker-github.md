# Issue tracker: GitHub

这个仓库的 issue 和规格保存在 GitHub issues 中。所有操作使用 `gh` CLI。

## 约定

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行正文用 heredoc。
- **读取 issue**：`gh issue view <number> --comments`，可用 `jq` 过滤评论，并读取标签。
- **列出 issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，并按需加 `--label`、`--state` 过滤。
- **评论**：`gh issue comment <number> --body "..."`
- **加 / 去标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭**：`gh issue close <number> --comment "..."`

仓库从 `git remote -v` 推断；在 clone 里运行时，`gh` 会自动识别。

## Pull request 作为 triage 面

**PR 作为请求面：no。**（如果这个仓库把外部 PR 当作功能请求，设为 `yes`；`/triage` 会读取这个标记。）

设为 `yes` 时，PR 使用与 issue 相同的标签和状态，对应使用 `gh pr` 命令：

- **读取 PR**：`gh pr view <number> --comments`，diff 用 `gh pr diff <number>`。
- **列出待 triage 的外部 PR**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`，只保留 `authorAssociation` 为 `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR` 或 `NONE` 的项（丢弃 `OWNER`/`MEMBER`/`COLLABORATOR`）。
- **评论 / 标签 / 关闭**：`gh pr comment`、`gh pr edit --add-label`/`--remove-label`、`gh pr close`。

GitHub 的 issue 和 PR 共用编号空间，所以裸 `#42` 可能是任意一种：先 `gh pr view 42`，失败再 `gh issue view 42`。

## 当 skill 说“发布到 issue tracker”

创建 GitHub issue。

## 当 skill 说“读取相关工单”

运行 `gh issue view <number> --comments`。

## Wayfinding 操作

供 `/wayfinder` 使用。**map** 是一个单独 issue，**child** issue 是工单。

- **Map**：一个带 `wayfinder:map` 标签的 issue，正文包含 Notes / Decisions-so-far / Fog。`gh issue create --label wayfinder:map`。
- **Child ticket**：作为 GitHub sub-issue 链接到 map（通过 sub-issues endpoint 的 `gh api`）。未启用 sub-issues 时，把 child 加进 map 正文的 task list，并在 child 正文顶部写 `Part of #<map>`。标签：`wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）。被认领后，把 ticket assign 给执行者。
- **Blocking**：使用 GitHub **原生 issue dependencies**，这是权威且 UI 可见的表示。添加边：`gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`，其中 `<blocker-db-id>` 是 blocker 的数字 **database id**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`，不是 `#number` 也不是 `node_id`）。GitHub 会在 `issue_dependencies_summary.blocked_by` 中报告（只含 open blocker，作为实时门禁）。不可用时退回 child 正文顶部的 `Blocked by: #<n>, #<n>`。所有 blocker 关闭后，ticket 才解锁。
- **Frontier 查询**：列出 map 的 open children（`gh issue list --state open`，限定 map 的 sub-issues / task list），去掉有 open blocker（`issue_dependencies_summary.blocked_by > 0`，或 `Blocked by` 行里有 open issue）或有 assignee 的项；map 顺序中第一个可用者胜出。
- **Claim**：`gh issue edit <n> --add-assignee @me`，这是会话的第一个写操作。
- **Resolve**：`gh issue comment <n> --body "<answer>"`，然后 `gh issue close <n>`，最后把上下文指针（gist + 链接）追加到 map 的 Decisions-so-far。
