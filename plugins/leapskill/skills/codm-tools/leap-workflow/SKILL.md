---
name: leap-workflow
description: Use when the user explicitly invokes $leap-workflow or asks for the Leap WorkFlow staged workflow for a non-trivial feature, refactor, migration, or bug fix.
---

# Leap WorkFlow

所有回复使用傻子都能懂的语言，不要赘述
一切落档都是为了给人看，所以落档内容要清晰明了

判断任务类型：
  调研任务时： 
    1. 先查询Docs/Research ，目录采用树形结构 先找相关模块 文件夹名称
    eg: 越底层的md文件记录的流程越详细，越上层的md文件记录的流程越宏观
      Shadow.md
        Shadow-DirectionalShadow.md
        Shadow-SpotShadow.md
        Shadow-SpotShadow-PerObjectShadow.md
      OC.md
        OC-SOC.md
        OC-MOC.md
        OC-SDOC.md

    2. 根据文档记录的源码流程查找相关代码
      找到：直接根据记录的源码位置调整，如果不一致需要根据规范更新文档结构.   
      没找到：需要重新调研，并更新文档结构
  讨论规划Plan时：
    如果需要落档 落档到Docs/AIWork/xxx/xxx-Plan.md  (xxx为任务名称)
    规划实现期Log, 使用CDL_LOG 在关键位置下Log. 用于测试期判断是逻辑问题还是渲染问题
    落档需求：用给人看的语言描述，需求名称，需求描述，改动涉及几个模块。每个模块改哪些东西。把代码流程树形结构写出来。
  Review任务时:
    1. 将相关review结论落档到相关Docs/AIWork/xxx/xxx-Review.md
  
  测试任务时：
    一般是由对应的测试场景 eg: TestValidation, 没有找到的话询问用户
    使用CDL相关工具打开对应的Log 测试Log是否符合预期，如果不符合预期则为逻辑问题, 如果符合预期 渲染不符合预期 则使用RendererDoc接入

  Debug任务时：
    当我说了现象，不用再去复现 直接根据现象调查逻辑




     
   
   
