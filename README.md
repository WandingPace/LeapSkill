# LeapSkill

LeapSkill 是我的个人 Codex 技能库：一套从想法、规格、实现、验证到沉淀的完整研发工作流技能。它基于 `matt-skills-curated/1.1.0` 的中文翻译起步，接下来会逐步改造成我自己的方法、术语和工程习惯。

原版仓库：<https://github.com/mattpocock/skills>（Matt Pocock 的公开技能库；本仓库的翻译基准是 `matt-skills-curated/1.1.0` 版本的 curated 子集，上游当前最新版已重构过 skill 内容和目录结构，逐文件对照时需留意版本差异）

## 当前内容

- 1 个插件：`leapskill`（同时提供 Codex 与 Cursor marketplace 清单）
- 55 个技能目录，按流程分组位于 `plugins/leapskill/skills/{requirements,specification,architecture,implementation,verification,support,learning,codm-tools}/`
- 覆盖需求澄清、规格拆解、架构设计、实现测试、调试评审、教学交接、长文写作和 CODM 工具流（含 Shader 关键字审计与 SVN diff 复核）
- 正文与界面文案已中文化
- 保留技能的 kebab-case 名称、脚本和配置结构

## 安装到 Cursor

仓库已包含 Cursor marketplace 清单，可被 Cursor Team Marketplace 索引：

- Marketplace：`.cursor-plugin/marketplace.json`
- 插件清单：`plugins/leapskill/.cursor-plugin/plugin.json`

技能按分类嵌套在 `skills/{category}/{skill}/` 下。Cursor 插件索引默认只扫 `skills/` 一层，因此 `plugin.json` 里显式列出了每个技能目录。

### Team Marketplace（推荐）

1. 打开 [Cursor Dashboard → Plugins](https://cursor.com/dashboard?tab=plugins)
2. Add Marketplace → Import from Repo
3. 填入 `https://github.com/WandingPace/LeapSkill`
4. 在 Customize 中安装 `leapskill`

本地私有 Git 仓库也可以作为 Team Marketplace 导入，只要仓库根目录有 `.cursor-plugin/marketplace.json`。

### 本地调试

Cursor 只从 `~/.cursor/plugins/local/<plugin>` 发现本地插件；指向仓库外的符号链接会被跳过。把插件目录拷进去后 Reload Window：

```powershell
$dst = Join-Path $env:USERPROFILE ".cursor\plugins\local\leapskill"
New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item "I:\TencentGit\LeapSkill\plugins\leapskill" $dst -Recurse
```

然后 `Developer: Reload Window`，打开 Customize，确认 `LeapSkill` 及其技能已加载。聊天里可用 `/show-me`、`/skill-conductor`、`/tdd`、`/research` 显式调用。

## 安装到 Codex

仓库已包含 Codex marketplace 清单，可以作为插件安装：

```bash
codex plugin marketplace add /path/to/LeapSkill
codex plugin add leapskill@leapskill
```

安装后开启新对话即可使用。可以显式调用，例如 `$show-me`、`$skill-conductor`、`$tdd`、`$research`；也可能根据任务描述被 Codex 自动选中。`show-me` 仅支持显式调用，用于把当前主题解释为紧凑图表、代码形态草图、diff 或聚焦的 HTML 产物。

## 翻译与改造约定

- 保留代码块、命令、路径、API 名称和工具名
- 保留技能的 kebab-case 标识符
- 保留 YAML/Markdown 结构
- 修改一个技能时只提交该技能相关文件
- 新增技能必须包含清晰的正面触发与 `Do NOT use for...` 负面边界

## 维护检查

如需继续完善翻译，建议按技能逐个提交，便于比较和回滚。可以使用下面的命令检查结构：

```bash
find plugins/leapskill/skills -type f -name SKILL.md | wc -l
rg '^description: "' plugins/leapskill/skills --glob 'SKILL.md'
```

本地开发路径：`/Users/liuweiping/MyProject/LeapSkill`

