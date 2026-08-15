---
managed-by: XGameHarness/unreal-pack
paths:
  - "client/Source/**/AI/**"
---

# AI Code Rules

适用于本项目 NPC / Enemy AI 代码（默认 `client/Source/**/AI/**`，按项目结构调整
frontmatter 的 `paths:`）。

> **当前 path 占位** — `client/Source/client/AI/` 子目录尚未建立。首次 AI 代码 land 时本规则自动激活；若实际目录命名不同，按需 patch 本文件 `paths:`。

- AI tick 预算: 单 actor < 0.2ms，总 AI < 2ms / frame — `stat ai` / Unreal Insights 验证
- 所有 AI 参数 data-driven（Behavior Tree blackboard keys / `UAIPerceptionComponent` 配置 / 计时器 / 权重） — 全部走 `UPrimaryDataAsset` 或 DataTable
- AI 必须可视化 debug — 实现 `DrawDebug*` / `Visual Logger` hook for 当前状态、感知锥、决策路径、目标
- AI 行为必须 telegraph — 玩家有时间读懂并反应（动画 wind-up / VFX 预兆 / 音效铺垫）
- 优先用 **Behavior Tree** 或 **State Tree** — 禁止写长 if/else 决策链
- 群组 AI 支持队形 / 包夹 / 角色分配 — 全部从 DataAsset 配置
- 所有 AI 状态机必须 log 转换（`UE_LOG(LogAI, Verbose, TEXT("..."))`） — 便于 replay / postmortem debug
- 即使单人游戏，所有 AI 输入仍按 server-authoritative 习惯校验（防 cheat engine 注入）
