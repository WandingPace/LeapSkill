# Out-of-Scope 知识库

仓库里的 `.out-of-scope/` 目录用于持久记录被拒绝的功能请求。它有两个作用：

1. **组织记忆**：记录功能为什么被拒绝，避免 issue 关闭后理由丢失
2. **去重**：新 issue 命中过去的拒绝时，skill 可以提示已有决策，避免重复争论

## 目录结构

```text
.out-of-scope/
├── dark-mode.md
├── plugin-system.md
└── graphql-api.md
```

一个文件对应一个**概念**，不是对应一个 issue。多个 issue 请求同一件事时，归到同一个文件里。

## 文件格式

文件应写得轻松易读，更像一份短设计文档，而不是数据库记录。用段落、代码和示例把理由讲清楚，让第一次读到的人也能明白。

```markdown
# Dark Mode

这个项目不支持 dark mode，也不支持面向用户的主题系统。

## Why this is out of scope

渲染管线假设只有一套颜色配置，定义在 `ThemeConfig` 中。
支持多主题需要：

- 一个包裹整个组件树的主题 context provider
- 每个组件都能按主题解析样式
- 一层持久化用户主题偏好的存储

这是一次明显的架构改动，也不符合这个项目专注于内容创作的方向。
主题化应该由嵌入或再分发输出内容的下游消费方处理。

```ts
// 当前 ThemeConfig 接口并不为运行时切换设计：
interface ThemeConfig {
  colors: ColorPalette; // 单一配色，构建时解析
  fonts: FontStack;
}
```

## Prior requests

- #42: "Add dark mode support"
- #87: "Night theme for accessibility"
- #134: "Dark theme option"
```

### 文件命名

概念名用短且有描述性的 kebab-case：`dark-mode.md`、`plugin-system.md`、`graphql-api.md`。名字要足够可辨识，让浏览目录的人不打开文件就知道被拒绝的是什么。

### 写拒绝理由

理由必须有实质内容，不是“我们不想做”，而是为什么不做。好的理由通常引用：

- 项目范围或理念（“这个项目专注于 X；主题化是下游问题”）
- 技术约束（“支持它需要 Y，这和我们的 Z 架构冲突”）
- 战略决策（“我们选择 A 而不是 B，因为...”）

理由要经得起时间。不要引用临时状况（“我们现在太忙”），那不是真正的拒绝，只是延期。

## 什么时候检查 `.out-of-scope/`

triage 的第 1 步（收集上下文）时，读取 `.out-of-scope/` 里的所有文件。评估新 issue 时：

- 检查请求是否命中已有的 out-of-scope 概念
- 匹配按概念相似度，不按关键词："night theme" 能匹配 `dark-mode.md`
- 命中时提示维护者：“它类似 `.out-of-scope/dark-mode.md`。之前拒绝的理由是 [reason]。你现在仍然这么认为吗？”

维护者可以：

- **确认**：新 issue 加进现有文件的 "Prior requests"，然后关闭
- **重新考虑**：删除或更新 out-of-scope 文件，issue 走正常 triage
- **不同意匹配**：两个 issue 相关但不同，走正常 triage

## 什么时候写入 `.out-of-scope/`

只有 **enhancement**（不是 bug）被作为 `wontfix` **拒绝**时才写。enhancement PR 同样适用：被拒绝的 PR 也要记录，避免同样请求以后以新代码的形式回来。

如果关闭原因是 `wontfix` 但功能**其实已经实现**，不要写进来。那是已构建的功能，不是被拒绝的功能；记录它会污染去重检查。关闭评论应指向功能所在位置。

流程：

1. 维护者判断功能请求超出范围
2. 检查是否已有匹配的 `.out-of-scope/` 文件
3. 有：把新 issue 追加到 "Prior requests"
4. 没有：用概念名新建文件，写决策、理由和第一条历史请求
5. 在 issue 上评论，说明决策并指向 `.out-of-scope/` 文件
6. 用 `wontfix` 标签关闭 issue

## 更新或删除 out-of-scope 文件

维护者对之前拒绝的概念改变主意时：

- 删除 `.out-of-scope/` 文件
- skill 不需要重新打开旧 issue，它们是历史记录
- 触发这次重新考虑的新 issue 走正常 triage
