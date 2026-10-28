---
name: verify-and-stop
description: Prove existing work meets acceptance conditions without expanding scope. Use for validation-only tasks, completion checks, focused gate runs, and last-mile proof. 中文用户说"只验证别改""验收一下""证明做完了"时也使用。Do NOT use for 需要顺手修复或扩大范围的任务。
---

# Verify and stop

把验收条件翻译成最小充分证明集。

- 仓库状态未变时，复用仍然有效的结果。
- 先跑聚焦检查，再跑更宽的门禁。
- 精确区分 pass、fail、unavailable、blocked 四种状态。
- 不改产品代码，除非验证请求明确包含修复。
- 验收标准通过后，不加润色、清理或无关测试。

验收证明完成立即停。只报告命令、结果和未解决风险。
