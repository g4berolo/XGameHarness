---
name: how-to-do
description: "XGameHarness 主推入口 — 说出你想做的事（哪怕很模糊），帮你澄清目标、检索匹配的 skill/agent、给出完整的建议流程并立刻推进第一步。任何时间任何情况都可调用：不知道下一步干嘛时无参数直接跑。触发词：怎么做/该用什么/帮我推进/下一步/不知道从哪开始/我想做…"
argument-hint: "[想做的事，可留空 = 帮我看看现在该干嘛]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Skill
---

# /how-to-do — 我想做 X，该怎么做？

比 `/handbook` 更进一步：handbook 是查表（X → 用哪个 skill），本 skill 是**导航**
（澄清目标 → 组织完整流程 → 陪你走第一步）。定位 = harness 的万能入口，用户在
任何阶段迷路都可以调它继续推进。

## 模式 A：带目标调用（`/how-to-do 我想做X`）

### 1. 理解与完善目标

先判断目标清晰度，不清晰就用 AskUserQuestion 补齐（最多问一轮、问最关键的 2-3 项）：

- **产出物**：用户要的是文档（GDD/ADR/计划）、代码、资产、还是决策？
- **范围与边界**：单个系统还是整个玩法域？新建还是改造现有？
- **当前基础**：相关前置工件存在吗？（就地 Glob/Read 验证，不猜——参照 R1）
  例：用户说"写战斗策划案"→ 先查 `design/gdd/game-concept.md`、`systems-index.md`
  是否存在，缺前置会改变建议流程
- 目标已足够清晰时**跳过提问直接进下一步**，不为问而问

### 2. 检索手册 + 组织建议流程

Read `${CLAUDE_PLUGIN_ROOT}/docs/HANDBOOK.md` § 1 定位匹配条目，然后**不止给单个
skill**，而是组织成建议流程(pipeline)：

- **前置**：缺什么先补什么（如无 game-concept → 先 `/brainstorm`）
- **主体**：核心步骤用哪个 skill / spawn 哪个 subagent（给可直接复制的 spawn 模板）
- **收尾**：质量关卡（`/design-review`、`/code-review`、`/gate-check`…）
- 每步一句话说明"为什么"，标注哪些步骤可跳过及跳过的代价

典型示例（用户说"我想写个新系统的策划案"）：

```
建议流程：
1. [前置] design/gdd/systems-index.md 里有这个系统吗？没有 → /map-systems 先登记
2. [主体] /design-system —— 8 段结构逐节引导写作
   数值公式细化可 spawn systems-designer subagent: <算例/曲线任务模板>
3. [收尾] /design-review —— 交给程序实现前必过
```

### 3. 立即推进

给出流程后**不要停在建议**：问用户"现在从第 N 步开始？"，确认后直接用 Skill tool
调起对应 skill（R5 —— 命中即调用，不徒手复刻）。

## 模式 B：无参数调用（"我现在该干嘛"）

1. 收集项目现状（存在才读，全部有守卫）：
   - `team/session-state/{identity}/active.md` 的"下一步"（注意 R1：这是 intent
     snapshot，引用前验证对应文件真实状态）
   - `plan/stage.md` / `plan/sprints/` 最新 sprint 的未完成项
   - `team/memo/{identity}/open/` 未处理 memo
2. 归纳 2-4 个候选方向（每个附：来源依据 + 对应 skill/agent + 预估量级），
   AskUserQuestion 让用户挑
3. 选定后转模式 A 第 2-3 步
4. 项目完全空白时 → 建议 `/project-init`（未接入）或 `/brainstorm`（零概念）起步

## 原则

- **回答要可执行**：每次输出必须以"下一个具体动作"结尾，不许停在泛泛清单
- 手册没覆盖的目标：如实说明，按对 harness 与项目的了解给流程，并提示可把该
  场景补进 HANDBOOK.md
- 不越权：涉及 spawn subagent 遵守 R4（提示模板由用户确认）；涉及提交推送遵守
  项目协作协议
