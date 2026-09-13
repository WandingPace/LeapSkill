# Issue tracker: GitLab

这个仓库的 issue 和规格保存在 GitLab issues 中。所有操作使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI。

## 约定

- **创建 issue**：`glab issue create --title "..." --description "..."`。多行描述用 heredoc。传 `--description -` 会打开编辑器。
- **读取 issue**：`glab issue view <number> --comments`。机器可读输出用 `-F json`。
- **列出 issue**：`glab issue list -F json`，按需加 `--label` 过滤。
- **评论**：`glab issue note <number> --message "..."`。GitLab 把评论叫作 note。
- **加 / 去标签**：`glab issue update <number> --label "..."` / `--unlabel "..."`。多标签可用逗号分隔或重复传参。
- **关闭**：`glab issue close <number>`。`glab issue close` 不支持关闭评论，所以先用 `glab issue note <number> --message "..."` 说明，再关闭。
- **Merge request**：GitLab 把 PR 叫作 merge request。使用 `glab mr create`、`glab mr view`、`glab mr note` 等；形态与 `gh pr ...` 相同，把 `pr` 换成 `mr`，`comment`/`--body` 换成 `note`/`--message`。

仓库从 `git remote -v` 推断；在 clone 里运行时，`glab` 会自动识别。

## Merge request 作为 triage 面

**MR 作为请求面：no。**（如果这个仓库把外部 merge request 当作功能请求，设为 `yes`；`/triage` 会读取这个标记。）

设为 `yes` 时，MR 使用与 issue 相同的标签和状态，对应使用 `glab mr` 命令：

- **读取 MR**：`glab mr view <number> --comments`，diff 用 `glab mr diff <number>`。
- **列出待 triage 的外部 MR**：`glab mr list -F json`，只保留作者不是 project member/owner 的 MR（贡献者的 MR，而不是维护者自己的进行中工作）。
- **评论 / 标签 / 关闭**：`glab mr note`、`glab mr update --label`/`--unlabel`、`glab mr close`。

与 GitHub 不同，GitLab 的 issue 和 MR 编号是分开的；只要知道维护者指的是哪个面，`#42` 就没有歧义。

## 当 skill 说“发布到 issue tracker”

创建 GitLab issue。

## 当 skill 说“读取相关工单”

运行 `glab issue view <number> --comments`。

## Wayfinding 操作

供 `/wayfinder` 使用。**map** 是一个单独 issue，**child** issue 是工单。

- **Map**：一个带 `wayfinder:map` 标签的 issue，正文包含 Notes / Decisions-so-far / Fog。`glab issue create --label wayfinder:map`。（在支持原生 epic 的 GitLab 版本里，也可以用 epic 存 map；带标签的 issue 在所有版本都可用。）
- **Child ticket**：一个 issue，描述顶部写 `Part of #<map>`，并带标签 `wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）。被认领后，把 ticket assign 给执行者。
- **Blocking**：使用 GitLab **原生 blocking link**，这是权威且 UI 可见的表示。通过 `/blocked_by #<n>` quick action 添加，作为 note 发布（`glab issue note <child> --message "/blocked_by #<blocker>"`）。原生 blocking link 是 Premium/Ultimate 功能；免费版或不可用时，退回描述顶部的 `Blocked by: #<n>, #<n>`。所有 blocker 关闭后，ticket 才解锁。
- **Frontier 查询**：`glab issue list -F json` 限定 map 的 children，去掉有 open blocker 的项：原生 `blocked_by` 链接指向 open issue（`glab api projects/:id/issues/:iid/links`）、`Blocked by` 行里有 open issue，或有 assignee；map 顺序中第一个可用者胜出。
- **Claim**：`glab issue update <n> --assignee @me`，这是会话的第一个写操作。
- **Resolve**：`glab issue note <n> --message "<answer>"`，然后 `glab issue close <n>`，最后把上下文指针（gist + 链接）追加到 map 的 Decisions-so-far。
