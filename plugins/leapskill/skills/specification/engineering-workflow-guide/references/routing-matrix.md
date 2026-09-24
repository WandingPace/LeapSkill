# ChatGPT Skill 路由矩阵

这张矩阵把常见用户说法和工程意图映射到唯一主 skill、后续管线和排除条件。

---

| 用户意图 / 说法 | 主 Skill | 生命周期管线 | 不要使用的场景 |
|---|---|---|---|
| “探索想法”、“访谈我”、“挑刺我的计划” | `grill-me` | `grill-me` ➔ `to-spec` | 需求已经正式且清晰 |
| “把决策记录成 ADR”、“定义领域术语” | `grill-with-docs` | `grill-with-docs` ➔ `to-spec` | 正在写生产应用代码 |
| “写技术规格”、“把需求形式化” | `to-spec` | `to-spec` ➔ `to-tickets` | 规格已写好并批准 |
| “拆成工单”、“创建任务图”、“tracer bullets” | `to-tickets` | `to-tickets` ➔ `implement` | 需求模糊或未批准 |
| “问干系人问题”、“异步需求调研” | `to-questionnaire` | `to-questionnaire` ➔ `to-spec` | 信息已在仓库里 |
| “快速原型”、“UI spike”、“一次性探索” | `prototype` | `prototype` ➔ `grill-with-docs` | 构建永久生产功能 |
| “设计运营流程”、“写 SOP”、“review 循环” | `workflow-designer` | `workflow-designer` ➔ `to-spec` | 一次性手动脚本执行 |
| “调研第三方 API”、“查文档” | `research` | `research` ➔ `to-spec` | 阅读本地项目代码文件 |
| “定义实体模型”、“统一语言”、“CONTEXT.md” | `domain-modeling` | `domain-modeling` ➔ `codebase-design` | 普通数据库表迁移 |
| “设计深模块”、“模块接口 seam”、“Ousterhout” | `codebase-design` | `codebase-design` ➔ `implement` | 简单一行 helper 函数 |
| “审计代码库架构”、“Git churn 热点分析” | `improve-codebase-architecture` | `improve-codebase-architecture` ➔ `setup-ts-deep-modules` | 常规单文件 bug 修复 |
| “TypeScript 边界”、“dependency-cruiser 规则” | `setup-ts-deep-modules` | `setup-ts-deep-modules` ➔ `code-review` | 非 TypeScript 代码库 |
| “不安全测试断言”、“迁移到 shoehorn” | `migrate-to-shoehorn` | `migrate-to-shoehorn` ➔ `code-review` | 生产应用类型 |
| “实现已批准规格”、“写功能”、“做工单” | `implement` | `implement` ➔ `code-review` | 需求模糊或未批准 |
| “并行子代理”、“隔离 worktree”、“多 agent PR” | `implement-spec` | `implement-spec` ➔ `code-review` | 单人单文件修改 |
| “测试驱动开发”、“红绿重构”、“写测试” | `tdd` | `tdd` ➔ `code-review` | 一次性探索 spike |
| “诊断 bug”、“修失败测试”、“CI 不稳定”、“崩溃” | `diagnosing-bugs` | `diagnosing-bugs` ➔ `tdd` ➔ `code-review` | 明显的简单语法错误 |
| “review PR”、“review 分支 diff”、“检查标准” | `code-review` | `code-review` | 写新代码或诊断 bug |
| “merge conflict”、“rebase conflict”、“修冲突标记” | `resolving-merge-conflicts` | `resolving-merge-conflicts` ➔ `code-review` | 无冲突的常规安全 rebase |
| “禁止 force push”、“拦截危险 git”、“hard reset 护栏” | `git-safety-guardrails` | `git-safety-guardrails` | 安全的 git status 或 log |
| “配置 issue tracker”、“设置 triage 标签”、“初始化文档” | `setup-engineering-workflows` | `setup-engineering-workflows` | 普通 npm 包安装 |
| “配置 Husky”、“lint-staged”、“Prettier pre-commit” | `setup-pre-commit` | `setup-pre-commit` | 远程 CI/CD 流水线自动化 |
| “triage 新 issue”、“写 agent brief”、“out of scope” | `triage` | `triage` ➔ `implement` | 来自 to-tickets 的内部工单 |
| “梳理大项目”、“跨会话工作”、“战争迷雾” | `wayfinder` | `wayfinder` ➔ `to-spec` | 小型单会话功能 |
| “交互式 bash 向导”、“控制台凭证配置” | `wizard` | `wizard` | AI 能直接执行的任务 |
| “训练 ML 模型”、“LoRA 微调”、“vLLM serving” | `ai-engineering` | `ai-engineering` ➔ `ml-best-practices` | 标准 CRUD 后端 |
| “自愈数据管线”、“AST 校验数据修复” | `ai-data-remediation` | `ai-data-remediation` ➔ `code-review` | 常规数据库 schema 迁移 |
| “统计 ML”、“95% bootstrap CI”、“EDA”、“数据泄漏” | `ml-best-practices` | `ml-best-practices` ➔ `ai-engineering` | 基础表格格式化 |
| “内部认知工作区”、“三种 register”、“深度思考” | `j-space` | `j-space` ➔ `implement` | 简单单步查询 |
| “合成 /goal 提示词”、“通宵自主运行” | `goal` | `goal` ➔ `implement-spec` | 立即单轮执行 |
| “写新 skill”、“skill 评测”、“10 条规范原则” | `skill-conductor` | `skill-conductor` ➔ `writing-for-agents` | 一般应用编码 |
| “压缩会话”、“迁移上下文”、“保存交接” | `handoff` | `handoff` | 向 git 提交代码 |
| “会话回顾”、“审计 agent 错误” | `retro` | `retro` ➔ `writing-for-agents` | 任务实现进行中 |
| “show-me”、“画出来”、“可视化解释” | `show-me` | `show-me` | 用户只想要普通 prose 解释，或技能已被显式禁用 |
| “换个简单说法”、“用大白语解释”、“等等什么” | `wait-what` | `wait-what` | 初期规划或头脑风暴 |
| “教技术概念”、“交互式 HTML 实验室”、“ZPD” | `teach` | `teach` | 静默自动代码生成 |
| “写 agent 指令”、“AGENTS.md 规则”、“上下文指针” | `writing-for-agents` | `writing-for-agents` ➔ `skill-conductor` | 面向人的营销文案 |
| “头脑风暴文章笔记”、“收集原始片段”、“比喻” | `writing-fragments` | `writing-fragments` ➔ `writing-shape` | 最终稿格式化 |
| “把笔记整理成草稿”、“逐块组装文章” | `writing-shape` | `writing-shape` ➔ `writing-beats` | 生成初始原始片段 |
| “叙事 beat”、“逐 beat 推进写作” | `writing-beats` | `writing-beats` | 快速单句修改 |
| “搭建练习目录”、“工作坊教程脚手架” | `scaffold-exercises` | `scaffold-exercises` ➔ `code-review` | 应用功能脚手架 |
