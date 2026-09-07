---
managed-by: XGameHarness/game-studio-core
paths:
  - "design/gdd/**"
---

# Design Document Rules

## Scope of these rules

These rules govern **per-system design documents** — the output of `/design-system`
and `/reverse-document design`. Other documents that live under `design/gdd/`
(game-concept, game-pillars, systems-index, economy model, faction and character
sheets, art/sound bible) have their own templates and are NOT graded or checked
against the section lists below.

## Rigor first

- Every per-system design document MUST declare a rigor level in its header:
  `Rigor: Lite` or `Rigor: Full`
- **Lite is the default.** Escalate to Full only when the change hits one of these:
  touches more than 2 existing systems' interfaces; changes the core loop; involves
  the economy or monetization; affects save compatibility; involves network
  replication; or is a brand-new system that has never been designed before
  (being enumerated in `systems-index.md` does not make it designed)
- A Full document MUST state which trigger justified the escalation
- Grading exists so small changes still get written down. Do NOT apply the Full
  checklist to a Lite document — that is not a finding, it is the point

## Every document, both rigor levels

- MUST open with four sections, before any tier-specific content:
  - `## 读本` — **一份完整的、能从头读到尾的策划案**，不是导语、不是摘要。
    详见下面「读本怎么写」那一节。
  - `## 设计前提` — the plain-language premise the user confirmed before writing
    started, unedited. A one-line system description in `systems-index.md` is NOT
    an approved premise; approving an index approves the enumeration, not what
    those words expand into
  - `## 已定决策摘要` — upstream constraints with their source files, and for each,
    whether it is normative or an illustrative data example (downstream treats
    examples as hard dependencies unless told otherwise). A delegation brief dies
    with the task; the file is what the next reader has
  - `## 本篇用到的新词` — every term this document coins that the user has not used
    before, with meaning and why an existing word would not do. Write 无 if there
    are none; never leave it empty
- **A term the user has not met MUST NOT appear in a question put to them.**
  Restate decisions in vocabulary the user has already used, or introduce the term
  first. A well-formed Open Questions section makes a handoff look complete;
  format compliance is not comprehension
- A design document is a **behavior contract, not an implementation plan**.
  Test: if the implementation can change without changing player-observable
  behavior, it does not belong here
- MUST NOT contain: concrete class/function names, Blueprint node wiring, library or
  framework selection (those go in an ADR), per-item number tables (those go in data
  files), or step-by-step implementation plans (those go in the sprint plan)
- Acceptance criteria must be testable — a QA tester must be able to verify pass/fail
- No hand-waving: "the system should feel good" is not a valid specification.
  Feel and pacing are validated by playtest, not asserted in a design document
- MUST be written incrementally: create the skeleton first, then fill each section one
  at a time with user approval between sections. Write each approved section to the
  file immediately to persist decisions and manage context

## 读本怎么写

**读本是一份完整的策划案，不是导语，不是摘要。**

用户原话（2026-09-07，第二次说时把第一版否掉了）：

> 我希望读本不只是几句大白话，而且开发者通过客户端能看到的 GDD
> 是完整的可读的一份策划案。

判据只有一条：**一个不做这块的开发者只读读本，应该完全懂这个系统怎么运转。**
读完还得回去翻规则表才明白，就是没写够。

### 五段（Full 文档）

按这个顺序，各用一个三级标题分开：

1. **这是个什么系统** —— 它在整个游戏里占什么位置，拿掉它游戏会缺什么
2. **玩家在里面经历什么** —— 从玩家视角走一遍：他看到什么、做什么决定、
   赢了输了分别是什么感受
3. **它怎么运转** —— **把规则用白话讲完整**。这一段最长，
   而且**必须完整**：每条会影响玩家决策的规则都要讲到，只是不写成条目和公式
4. **为什么这么定** —— 关键取舍。定成另一个样子会怎样、为什么没那么定
5. **一个完整的例子** —— 从头到尾走一遍具体的一局 / 一次交互，带上具体情境

Lite 文档写前三段就够（它本来就是一次小改动，第 4 段并进第 3 段）。

### 三条硬规矩

**不许出现**：系统编号（`#20 §R7`）、类名 / 函数名、文件路径、
缩写代号（`PP-D5`、`FP gate`）、本篇之外没解释过的术语。

**不许写具体数值和公式。** 说「买通一个 AI 的价钱随着关卡推进变少」，
不说「叛价 = 合作余利 × 0.6」。

> 这一条是**防走散**用的，不是嫌数字难读。读本和下面的规则表讲的是同一个
> 系统 —— 同一个数在两处各写一遍，改了其中一处**不会有任何地方报错**，
> 而下游会照着过期的那份做下去。**数值只有规则表那一份**，
> 读本负责说清它是什么、往哪个方向变。

**不许省。** 「详见下文」「具体规则见 Detailed Rules」这类句子在读本里是
失败信号 —— 读本的读者正是那个不会往下翻的人。

### 它跟别的几节的关系

| 这一节 | 是什么 | 谁说的 |
|---|---|---|
| `## 读本` | **完整的策划案**，白话，不带数值 | 我们写给读者的 |
| `## 设计前提` | **出处** —— 用户当初确认的原话，一个字不许编辑 | 用户说的 |
| Detailed Rules / Formulas / … | **契约** —— 精确、可判定、带数值 | 给实现和 QA 的 |

读本和契约**不是两份文档，是同一件事的两层**。分界线是：
**读本说「发生什么、为什么」，契约说「精确到什么程度」。**

### 一份都还没有

这条规则 2026-09-07 才立，**现存文档一篇都没有读本**。它们要等下次修订、
或者专门跑一次 `/reverse-document` 才补得上。

客户端在没有这一节时**明说这一篇还没有读本**，不假装
（做不到的事不要长得像做得到）。

## Lite documents

- MUST contain: 意图 (why), 改动 (only what changes — 新增 / 修改 / 移除),
  非目标 (explicitly out of scope), 验收 (3-5 testable conditions)
- 非目标 MUST NOT be empty — it is the scope-creep brake
- 改动 describes the delta, not the whole system. Restating the entire system is the
  signal that this should have been Full
- **A brand-new system downgraded to Lite renames 改动 to 构成** and drops the
  新增/修改/移除 sub-headings — for a system that does not exist yet, two of the
  three are empty by construction. Trigger #6 exists to prevent this shape; when it
  is waived, swap the structure rather than letting each document improvise
- Keep it short. Past roughly 50 lines, restructure as Full

## Full documents

- MUST contain these 6 sections: Detailed Rules, Formulas, Edge Cases,
  Dependencies, Tuning Knobs, Acceptance Criteria
- **`Overview` 和 `Player Fantasy` 并进 `## 读本` 了**（2026-09-07）。
  读本的第 1 段和第 2 段说的正是这两件事 —— 留着的话同一个系统会被写两遍，
  而**两处说法走散时不会有任何地方报错**，正是这份规则刚在
  「不许写具体数值」那条里警告的东西。
  这六节是**契约**：精确、可判定、带数值
- Formulas must include variable definitions, expected value ranges, and example
  calculations — but the formula *shape* and safe ranges only; the concrete values
  live in data files
- Edge cases must explicitly state what happens, not just "handle gracefully"
- Dependencies must be bidirectional — if system A depends on B, B's doc must mention A
- Tuning knobs must specify safe ranges and what gameplay aspect they affect
- Balance values must link to their source formula or rationale
