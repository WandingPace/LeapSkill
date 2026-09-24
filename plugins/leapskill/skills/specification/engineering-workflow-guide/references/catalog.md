# 精选 Skill 目录

默认只使用一个主 skill。只有在进入不同阶段时，才增加另一个。

## 探索与规划

- `grill-with-docs`：计划或设计需要集中访谈，并且领域术语、架构决策要在解决的同时写入项目文档时使用。
- `grill-me`：计划、设计、需求或决策在执行前需要集中访谈，以暴露歧义、缺失约束、取舍或薄弱假设时使用。
- `grilling`： relentlessly 追问用户的计划、决策或想法。用户想压力测试自己的思路，或使用任何“grill”触发词时使用。
- `to-spec`：当前对话和仓库上下文已经足够，无需再次访谈即可合成可构建规格，包括实现和测试决策时使用。
- `to-tickets`：已批准的计划、规格或当前对话需要拆成有序 tracer-bullet 实施工单，并写入配置的 tracker 时使用。
- `wayfinder`：目标太大或太不确定，单个 agent 会话做不完，需要跨多个会话维护决策工单、阻塞项、断言和已解决上下文的共享地图时使用。
- `prototype`：构建一次性原型来回答设计问题。用户想验证状态模型或逻辑是否合理，或探索 UI 形态时使用。
- `research`：面向高信任一手来源调研问题，并把结果保存为仓库中的 Markdown。用户要求研究主题、收集文档或 API 事实、或把阅读工作交给后台 agent 时使用。
- `to-questionnaire`：决策、规格或实现问题依赖只有其他干系人才知道的事实，且需要把这些未知项整理成精确问卷时使用。
- `workflow-designer`：重复任务、运营流程、内容生产、review 循环、个人或团队工作流需要变成可实施规格（含触发、输入、动作、人工检查点、输出、失败处理、责任人）时使用。

## 实现与质量

- `implement`：具体规格、已批准计划或工单集已准备好实施，任务需要范围明确的代码修改和验证时使用。
- `implement-spec`：带任务图工单的规格要在多个子代理或隔离分支上并行实施，最终目标是在单一分支上产出完整 PR 时使用。
- `tdd`：以红绿循环测试先行实现功能或修 bug，或任务需要围绕 public 行为建立长期有效的 integration 风格测试时使用。
- `code-review`：从固定点（commit、branch、tag 或 merge-base）开始 review 变更，沿两个轴：Standards（代码是否遵循仓库文档化标准）和 Spec（代码是否符合原始 issue/规格）。并行子代理运行两类 review，并排报告。用户想 review 分支、PR、WIP，或说“review since X”时使用。
- `diagnosing-bugs`：疑难 bug 和性能回归的诊断循环。用户说“diagnose/debug this”，或报告异常、报错、失败、变慢时使用。
- `resolving-merge-conflicts`：需要处理进行中的 git merge/rebase 冲突时使用。
- `migrate-to-shoehorn`：TypeScript 测试依赖不安全的 `as` 或 `as unknown as` 断言构造 fixture，用户想把这些测试专用值迁移到 `@total-typescript/shoehorn` 并显式表达意图时使用。

## AI 与机器学习

- `ai-engineering`：设计、训练、微调、优化和部署生产 ML 模型与 LLM，要求严格 train-test 隔离、naive baseline、公平性审计和 100ms 内延迟预算。
- `ai-data-remediation`：自愈数据管线层，包含语义异常聚类、AST 校验的 lambda 转换和零损失数学对账。
- `ml-best-practices`：统计 ML 标准，包括探索性数据分析、缺失值策略、双模型基准、95% bootstrap 置信区间和叙事优先的 notebook 结构。

## 认知与自主编排

- `j-space`：操作内部认知工作区，用于多步链式推理、长程规划、校准置信度、三种 register（inner/ledger/outer）和 seam 不变量审计。
- `goal`：合成高杠杆的自主 `/goal` 提示词与合同，包含可观察的完成标准、已验证资源清单和无人值守执行的终局目标锚定。
- `skill-conductor`：agent skill 的全生命周期管理（草稿、测试、review、改进、打包），基于 10 条规范创作原则和 BinEval 五维评分。

## 设计与架构

- `domain-modeling`：构建并打磨项目领域模型。用户想确定领域术语或统一语言、记录架构决策，或其他 skill 需要维护领域模型时使用。
- `codebase-design`：设计深模块的共享词汇。用户想设计或改进模块接口、寻找深化机会、决定 seam 位置、提升可测试性或 AI 可导航性，或其他 skill 需要深模块词汇时使用。
- `improve-codebase-architecture`：代码库需要架构 review，寻找浅模块、弱 seam、低局部性或深化机会，并输出可视化报告和聚焦设计讨论时使用。
- `setup-ts-deep-modules`：TypeScript 仓库需要用 dependency-cruiser 强制 package 入口、隐藏实现目录、通过 public 接口测试和循环依赖检查，尤其是扁平 packages 目录或 monorepo 时使用。

## 仓库安全与初始化

- `setup-engineering-workflows`：仓库工作流需要在规划、triage、wayfinding 或工单工作前建立明确的 issue tracker、triage 标签、领域文档或 agent 指令约定时使用。
- `setup-pre-commit`：JavaScript/TypeScript 仓库需要用 Husky 和 lint-staged 建立可靠的 pre-commit 质量检查，同时保留仓库的 package manager、formatter、既有 hook 和测试/类型检查约定时使用。
- `git-safety-guardrails`：仓库需要对破坏性或不可逆 Git 操作加护栏，尤其 force push、hard reset、clean、破坏性 restore、删分支或改写历史时使用。
- `triage`：仓库 issue 或外部贡献请求需要分类、验证、补充信息跟进、拒绝处理，或生成持久 agent-ready 实现简报时使用。
- `wizard`：生成交互式 bash 向导，带人完成只有人能执行的步骤。用于基础设施开通、凭证或 CI secret 配置、陌生第三方控制台操作、一次性迁移或切换。不要用于 agent 自己能完成的步骤。

## 连续性与沟通

- `handoff`：当前工作、决策、证据、阻塞项和下一步行动需要压缩成持久交接文档，给其他 agent 或以后会话使用时使用。
- `retro`：对编码会话做回顾，找出 agent 环境、导航指针、自动化检查、编码标准、工具开销或 AGENTS.md 指令的可执行改进时使用。
- `show-me`：用户想更直观地理解当前主题，需要紧凑图表、代码形态草图、diff 或聚焦 HTML 产物时显式调用。此技能不参与自动路由。
- `wait-what`：上一轮解释或方案没有讲明白，需要重置假设、换角度重新讲，并明确指出卡住点时使用。
- `teach`：用户想通过当前工作区学习技术概念或技能，需要自适应讲解、示例、理解检查和持久学习记录时使用。
- `writing-for-agents`：创建或修改面向 agent 的 Skill、AGENTS.md、CLAUDE.md、被引用的 agent 文档、上下文指针、模板或其他可复用 agent 指导时使用。

## 写作与学习内容

- `writing-fragments`：用户想先收集强原始片段，不急于确定大纲或最终结构，从而发展文章、随笔、帖子、脚本或其他长文时使用。
- `writing-shape`：用户已有固定的笔记、片段、转写材料或研究材料，想在不改动原始材料的前提下，一块一块整理成连贯文章或长文草稿时使用。
- `writing-beats`：用户想要交互式长文写作流程，按小的叙事或论证 beat 推进，每一步给出几个有效下一步，同时保持读者所需上下文清晰时使用。
- `scaffold-exercises`：课程、工作坊、教程或培训仓库需要新增练习目录、问题/解答/讲解变体、starter 文件、编号或符合仓库规范的 lint-ready 脚手架时使用。
