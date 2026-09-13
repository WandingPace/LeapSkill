# LeapSkill

LeapSkill 是我的个人 Codex 技能库：一套从想法、规格、实现、验证到沉淀的完整研发工作流技能。它基于 `matt-skills-curated/1.1.0` 的中文翻译起步，接下来会逐步改造成我自己的方法、术语和工程习惯。

## 当前内容

- 42 个技能目录
- 42 个 Codex 可发现的 `SKILL.md`
- 覆盖需求澄清、规格拆解、架构设计、实现测试、调试评审、教学交接和长文写作
- 正文与界面文案已中文化
- 保留技能的 kebab-case 名称、脚本和配置结构

## 安装到 Codex

Codex 会读取 `~/.agents/skills` 下的本地技能。推荐用符号链接安装，方便仓库更新后立即生效：

```bash
git clone https://github.com/WandingPace/LeapSkill.git
mkdir -p ~/.agents/skills

for dir in /path/to/LeapSkill/*/; do
  ln -s "$dir" ~/.agents/skills/"$(basename "$dir")"
done
```

安装后开启新对话即可使用。可以显式调用，例如 `$skill-conductor`、`$tdd`、`$research`；也可能根据任务描述被 Codex 自动选中。

## 翻译与改造约定

- 保留代码块、命令、路径、API 名称和工具名
- 保留技能的 kebab-case 标识符
- 保留 YAML/Markdown 结构
- 修改一个技能时只提交该技能相关文件
- 新增技能必须包含清晰的正面触发与 `Do NOT use for...` 负面边界

## 维护检查

如需继续完善翻译，建议按技能逐个提交，便于比较和回滚。可以使用下面的命令检查结构：

```bash
find . -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
rg '^description: "' --glob 'SKILL.md'
```

本地开发路径：`/Users/liuweiping/MyProject/LeapSkill`
