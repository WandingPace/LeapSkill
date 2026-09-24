# RESOURCES.md 格式

`RESOURCES.md` 固定放在当前项目的 `Docs/Teach/<topic-slug>/RESOURCES.md`，是这个主题的可信资源清单。讲解所需的知识应从这里取，不靠模型自己猜。经验判断来自这里列出的社区。

## 结构

```md
# {主题} Resources

## Knowledge

- [Book: _The Science and Practice of Strength Training_ by Zatsiorsky & Kraemer](https://example.com)
  训练计划和适应机制的基础教材。用于：周期化、恢复、强度区间相关问题。
- [Article: "How Much Should I Train?" by Greg Nuckols (Stronger By Science)](https://example.com)
  关于容量指标的循证综述。用于：确定每个肌群的每周组数目标。

## Wisdom (Communities)

- [r/weightroom](https://reddit.com/r/weightroom)
  高信噪比 subreddit，管理员会清理伪科学。用于：训练计划评审、平台期排查。
- Local: Tuesday strength class at {gym name}
  用于：训练动作的实时教练反馈。
```

## 规则

- **只收高信任来源。** 优先一手资料、公认专家、同行评审研究和审核严格的社区。营销包装成教育的资源不要。
- **每个条目都要加注释。** 裸链接三个月后就没用了。加一行：它覆盖什么，什么时候用它。
- **按 Knowledge / Wisdom 分组。** 对应 [SKILL.md](./SKILL.md) 里的理念。一个资源只出现在一组里也没问题。
- **显式暴露缺口。** 如果 mission 需要的某个领域没有好资源，写一个 `## Gaps` 章节列出缺什么，驱动后续搜索。
- **果断删除。** 被证明错误、内容浅、偏离 mission 的资源要移除，不要留着。五个锋利的来源好过三十个平庸的。
- **记录社区偏好。** 如果用户明确不想加入社区，写在这里，后续课程不要反复建议。
