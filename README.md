# Matt Skills Curated 中文版

这是 [Matt Skills Curated](https://github.com/) 插件技能集的中文维护版本，基于插件缓存中的 `matt-skills-curated/1.1.0` 技能内容生成。

## 内容

- 42 个技能目录
- 每个技能保留原始 `name`、目录名、脚本和配置结构
- `SKILL.md` 正文、参考文档和界面名称已翻译为中文
- frontmatter 的 `description` 保留英文，以降低技能触发边界的变化风险

## 翻译约定

- 保留代码块、命令、路径、API 名称和工具名
- 保留技能的 kebab-case 标识符
- 保留 YAML/Markdown 结构
- 对机器翻译导致的命令变化做了校验和修正

## 后续维护

如需继续完善翻译，建议按技能逐个提交，便于比较和回滚。可以使用下面的命令检查结构：

```bash
find . -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
rg '^description: "' --glob 'SKILL.md'
```
