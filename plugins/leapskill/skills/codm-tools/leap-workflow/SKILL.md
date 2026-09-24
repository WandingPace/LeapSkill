---
name: leap-workflow
description: "用于用户明确调用 $leap-workflow，或要求用 Leap WorkFlow 分阶段处理非平凡功能、重构、迁移、审查、测试和调试任务的场景。不用于小型直接修改、普通代码问答或未获授权的后续阶段。"
---

# Leap WorkFlow

所有回复都要通俗、直接，不要赘述。所有落档都面向人阅读，因此内容必须清晰。

## 任务类型路由

### 调研任务

1. 先查询 `Docs/Research`。目录按树形结构组织，先查找相关模块和文件夹名称。

   越底层的 Markdown 文件记录越详细的流程，越上层的 Markdown 文件记录越宏观的流程。例如：

   ```text
   Shadow.md
     Shadow-DirectionalShadow.md
     Shadow-SpotShadow.md
     Shadow-SpotShadow-PerObjectShadow.md
   OC.md
     OC-SOC.md
     OC-MOC.md
     OC-SDOC.md
   ```

2. 根据文档记录的源码流程查找相关代码。
   - 找到：直接按记录的源码位置调整；如果与现状不一致，按规范更新文档结构。
   - 没找到：重新调研，并更新文档结构。

### 规划新方案或即时修改需求

1. 将需求和做法通过Skill /showme 展示改动点 落档到 `Docs/AIWork/xxx/xxx-Plan01.md`。`xxx` 为任务名称，`Plan01` 表示一期任务。
2. 规划实现期的日志。在关键位置使用 `CDL_LOG` 下日志，便于测试期判断问题属于逻辑问题还是渲染问题。
3. 落档需求时要用面向人的语言说明需求名称、需求描述、涉及的模块和数据结构，以及每个模块要修改的内容。代码流程要用树形结构写出。

### 审查任务

1. 阅读代码改动，判断是否符合当前方案（`Docs/AIWork/xxx/xxx-Plan0x.md`）的预期。
2. 将相关结论落档到 `Docs/AIWork/xxx/xxx-Review01.md`。

### 测试任务

1. 一般使用对应测试场景，例如 `TestValidation`。找不到时询问用户。
2. 使用 CDL 相关工具打开对应日志，判断日志是否符合预期。
3. 日志不符合预期时，按逻辑问题处理；日志符合预期但渲染不符合预期时，接入 RendererDoc 继续调查。

### 调试任务

1. 用户描述现象后，不要重新复现，直接根据现象调查逻辑。
2. 修复完成后，将简要记录落档到 `Docs/AIWork/xxx/xxx-Debug.md`。
3. 先使用日志定位问题属于逻辑问题还是渲染问题。
