---
current_stage: Concept
---

# 开发阶段 SoT（Single Source of Truth）

> 项目侧文件，路径固定为 `plan/stage.md`。由 `/project-init` 从本模板实例化，
> 之后是**项目自己的文件** —— harness 不会覆盖它。
>
> 读它的有：`/gate-check`（门禁判定 + 通过后写回）、`/project-stage-detect`、
> `/start`（状态看板）、`/how-to-do`（下一步建议）、`project-stage-report` 模板。
>
> **当前阶段写在 frontmatter 的 `current_stage`**，不再有独立的 `plan/stage.txt`
> —— 两个文件必然漂移，合成一处。

## 怎么用这张表

harness 只规定 sub-phase 的**种类**（"最薄的端到端可玩路径"这种跨项目都成立的东西），
不规定它在你项目里**具体指什么**。后者填进「本项目含义」列。

举例：`PP-E2 Walking Skeleton` 在一个 roguelike 里可能是「大厅→楼层→战斗→结算闭环」，
在一个农场模拟里可能是「种下→生长→收获→售出闭环」—— 种类相同，内容完全不同。

- **Tier**：`Critical` / `Should` / `Optional`。`/gate-check` 的 PASS 条件是
  **当前阶段所有 Critical 行都 ✅ Done**，Should / Optional 只影响 CONCERNS 措辞。
- **Status**：`⏳ Not Started` / `🔄 In Progress` / `✅ Done` / `➖ N/A`。
  用不上的行标 `➖ N/A` 并在含义列写一句为什么，**不要删行** —— 删了以后看不出是
  "做完了"还是"从没考虑过"。
- 项目可以**增行**（本项目特有的必过项）。增的行照样参与 Critical 判定。
- 阶段词表本身（7 个 stage）不建议改 —— 改了 `/project-stage-detect` 的阶段映射会对不上。

## 阶段词表（7 stage / 6 道门 + 1 道发布后）

```
Concept → Pre-Production → First Playable → Vertical Slice → Alpha → Beta → Release
```

## 阶段矩阵

| ID | Sub-phase | Tier | Status | 本项目含义 |
|---|---|---|---|---|
| **Concept** | | | | |
| C-D1 | 游戏概念文档成文并通过评审 | Critical | ⏳ | |
| C-D2 | 设计支柱(pillars)确定 | Critical | ⏳ | |
| C-P1 | 目标平台 / 受众 / 规模量级 | Should | ⏳ | |
| **Pre-Production** | | | | |
| PP-E1 | 引擎与技术栈选定 + 首个 ADR | Critical | ⏳ | |
| PP-E2 | Walking Skeleton — 最薄的端到端可玩路径跑通 | Critical | ⏳ | |
| PP-A1 | 视觉风格方向锁定 | Critical | ⏳ | |
| PP-A2 | 美术管线 POC — 单个资产走通全流程 | Should | ⏳ | |
| PP-D1 | MVP 范围内的系统 GDD 全部通过评审 | Critical | ⏳ | |
| PP-D2 | 系统清单(systems-index)成文 | Should | ⏳ | |
| PP-P1 | 第一份 sprint plan 落地 | Critical | ⏳ | |
| **First Playable** | | | | |
| FP-E1 | 核心循环端到端可玩，无阻断性缺陷 | Critical | ⏳ | |
| FP-D1 | 首轮数值调优 | Critical | ⏳ | |
| FP-A1 | 第一波正式美术替换占位 | Should | ⏳ | |
| FP-P1 | 首次内部试玩 + 反馈归类 | Critical | ⏳ | |
| **Vertical Slice** | | | | |
| VS-E1 | 切片范围内功能完整（真实实现，非文档） | Critical | ⏳ | |
| VS-D1 | 切片范围内内容完整 | Critical | ⏳ | |
| VS-A1 | 切片达到可对外展示的美术质量 | Critical | ⏳ | |
| VS-A2 | 音效首轮真实接入 | Should | ⏳ | |
| VS-P1 | 外部试玩，验证 pillar 是否成立 | Critical | ⏳ | |
| **Alpha** | | | | |
| A-E1 | 功能完整 — 全部 MVP 系统真实实现 | Critical | ⏳ | |
| A-D1 | 内容完整 — 全部计划内容进入游戏 | Critical | ⏳ | |
| A-A1 | 资产全部就位（允许占位件） | Critical | ⏳ | |
| A-E2 | 测试套件通过 + 性能基线测得 | Critical | ⏳ | |
| A-P1 | 多轮试玩 + 迭代 | Critical | ⏳ | |
| **Beta** | | | | |
| B-E1 | 性能达标（对照 technical-preferences 的预算） | Critical | ⏳ | |
| B-D1 | 数值终调 | Critical | ⏳ | |
| B-A1 | 美术 / 特效 / 音乐 打磨完成 | Critical | ⏳ | |
| B-Q1 | 功能与内容锁定 + 0 个严重缺陷 | Critical | ⏳ | |
| B-L1 | 本地化 — 文本外化 + 翻译 + 语言质检 | Should | ⏳ | |
| **Release** | | | | |
| R-Q1 | QA 全量签核 | Critical | ⏳ | |
| R-L1 | 法务与合规（用户协议 / 隐私政策 / 分级） | Critical | ⏳ | |
| R-S1 | 商店页素材（描述 / 截图 / 预告片） | Critical | ⏳ | |
| R-S2 | 终版构建 + 渠道分发包 | Critical | ⏳ | |

## History

每次 `/gate-check` 判定 PASS 并推进阶段时追加一行。

| Date | Gate | 变更 | 备注 |
|---|---|---|---|
| [日期] | — | 从 harness 模板初始化，current_stage = Concept | `/project-init` |
